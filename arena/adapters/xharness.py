"""xharness adapter:在本机驱动 x-harness-rs 的 xharness-host(headless)。

协议来自 xharness-bench 仓库实测沉淀(他们用直接实验验证过,非读文档):

  启动:xharness-host --bind 127.0.0.1:0 --workspace <ws> --state-dir <st>
        --static-dir <web> --ready-file <f> --shutdown-file <f>
        --provider deepseek --model <m> --base-url <url> --context-window <N>
        env:XHARNESS_DESKTOP_TOKEN(随机)、XHARNESS_API_KEY(模型 key)
        ready-file 内容为 "host:port"
  RPC:POST http://127.0.0.1:<port>/api/<method>
       body {"type":"client-request","rpcId":..,"method":..,"payload":{..}}
       header x-xharness-desktop-token
       resp {"result":{"ok":true,"value":..}}
  序列:workspace.list(等活)→ settings.describe → settings.mutate
       (permission.defaultPreset=danger-full-access,bench 无人审批)
       → session.create → session.prompt(mode=queue)
       → 轮询 session.history 直到 turn/end
  记账:assistant/message.usage 的 inputTokens(不含缓存读)/outputTokens/
       cacheReadTokens/reasoningTokens;tool/call 计数;
       session.history 默认只回最后 50 条,必须按 hasMore+beforeSeq 翻页。

--context-window 给 1,000,000:xharness-bench 的教训——upstream 实际按 1M 跑,
把这一臂锁 131072 等于送别臂八倍余量,测出来的是预算不是 harness。
"""
from __future__ import annotations

import json
import os
import secrets
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from .. import providers
from ..schema import Task
from .base import AgentRun, Usage

HOST_BIN = os.environ.get(
    "XHARNESS_HOST_BIN",
    str(Path.home() / "x-harness-rs" / "target" / "release" / "xharness-host"),
)
WEB_DIST = os.environ.get(
    "XHARNESS_WEB_DIST", str(Path.home() / "x-harness-rs" / "ui" / "dist")
)
CONTEXT_WINDOW = int(os.environ.get("XHARNESS_CONTEXT_WINDOW", "1000000"))


class _Rpc:
    def __init__(self, port: int, token: str):
        self.origin = f"http://127.0.0.1:{port}"
        self.token = token
        self.seq = 0

    def call(self, method: str, payload: dict | None = None, timeout: float = 120.0):
        self.seq += 1
        body = json.dumps(
            {
                "type": "client-request",
                "rpcId": f"arena-{self.seq}",
                "method": method,
                "payload": payload or {},
            },
            ensure_ascii=False,
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{self.origin}/api/{method}",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-xharness-desktop-token": self.token,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            parsed = json.loads(r.read())
        result = parsed.get("result")
        if not isinstance(result, dict) or result.get("ok") is not True:
            raise RuntimeError(f"RPC {method} failed: {json.dumps(parsed)[:400]}")
        return result.get("value")


def _norm(history: dict) -> list[dict]:
    events = []
    for entry in history.get("events") or []:
        event = entry.get("event", entry) if isinstance(entry, dict) else None
        if isinstance(event, dict) and isinstance(event.get("type"), str):
            events.append(event)
    return events


def _fetch_all(rpc: _Rpc, session_id: str) -> dict:
    """完整历史:默认页只有 50 条,必须翻页,否则 token 统计只算了尾巴。"""
    events: list[dict] = []
    before_seq = None
    for _ in range(200):
        payload: dict = {"sessionId": session_id, "maxMessages": 500}
        if before_seq is not None:
            payload["beforeSeq"] = before_seq
        page = rpc.call("session.history", payload)
        if not isinstance(page, dict):
            break
        batch = [e for e in (page.get("events") or []) if isinstance(e, dict)]
        events = batch + events
        if not page.get("hasMore"):
            break
        seqs = [e.get("seq") for e in batch if isinstance(e.get("seq"), int)]
        if not seqs:
            break
        before_seq = min(seqs)
    return {"events": events}


def _num(usage: dict, *names: str) -> int:
    for n in names:
        v = usage.get(n)
        if isinstance(v, (int, float)):
            return int(v)
    return 0


def _summarize(events: list[dict]) -> Usage:
    u = Usage()
    for ev in events:
        kind = ev.get("type")
        data = ev.get("data") or {}
        if not isinstance(data, dict):
            continue
        if kind in ("assistant/message", "message/assistant"):
            usage = data.get("usage")
            if isinstance(usage, dict):
                step_in = _num(usage, "inputTokens", "input_tokens") + _num(
                    usage, "cacheReadTokens", "cache_read_tokens"
                )
                if step_in or _num(usage, "outputTokens", "output_tokens"):
                    u.calls += 1
                u.input_tokens += _num(usage, "inputTokens", "input_tokens")
                u.output_tokens += _num(usage, "outputTokens", "output_tokens")
                u.cache_tokens += _num(usage, "cacheReadTokens", "cache_read_tokens")
                u.reasoning_tokens += _num(
                    usage, "reasoningTokens", "reasoning_tokens"
                )
        elif kind == "tool/call":
            u.calls = u.calls  # 工具调用不计入 provider 调用;见 transcript
    return u


class XHarnessAdapter:
    name = "xharness"
    model = providers.DEEPSEEK_MODEL

    def run(self, task: Task, workdir: Path) -> AgentRun:
        usage = Usage()
        if not Path(HOST_BIN).is_file():
            return AgentRun(
                ok=False, usage=usage, error=f"未找到 xharness-host: {HOST_BIN}"
            )
        st = workdir / ".arena" / "xharness-state"
        st.mkdir(parents=True, exist_ok=True)
        ready = st / "ready.address"
        shutdown = st / "shutdown.request"
        for f in (ready, shutdown):
            f.unlink(missing_ok=True)
        token = secrets.token_hex(24)
        log_path = st / "host.log"

        args = [
            HOST_BIN,
            "--bind", "127.0.0.1:0",
            "--workspace", str(workdir),
            "--state-dir", str(st),
            "--static-dir", WEB_DIST,
            "--ready-file", str(ready),
            "--shutdown-file", str(shutdown),
            "--provider", "deepseek",
            "--model", providers.DEEPSEEK_MODEL,
            "--base-url", providers.DEEPSEEK_BASE,
            "--context-window", str(CONTEXT_WINDOW),
        ]
        # 思考全开时默认输出上限(12288)会被推理烧光导致 max-tokens 截断,可放宽
        max_out = os.environ.get("XHARNESS_MAX_OUTPUT")
        if max_out:
            args += ["--max-output-tokens", max_out]
        env = {
            **os.environ,
            "XHARNESS_DESKTOP_TOKEN": token,
            "XHARNESS_API_KEY": providers.DEEPSEEK_KEY or "",
        }
        proc: subprocess.Popen | None = None
        err: str | None = None
        transcript = workdir / ".arena" / "transcript.json"
        try:
            with log_path.open("w") as logf:
                proc = subprocess.Popen(
                    args,
                    env=env,
                    stdout=logf,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                )
            port = None
            deadline = time.time() + 90
            while time.time() < deadline:
                if ready.is_file():
                    text = ready.read_text().strip()
                    p = text.partition(":")[2]
                    if p.isdigit():
                        port = int(p)
                        break
                if proc.poll() is not None:
                    raise RuntimeError(
                        "host 提前退出:"
                        + log_path.read_text(errors="replace")[-500:]
                    )
                time.sleep(0.4)
            if port is None:
                raise RuntimeError("ready-file 90s 未出现:"
                                   + log_path.read_text(errors="replace")[-300:])

            rpc = _Rpc(port, token)
            t2 = time.time() + 60
            while True:
                try:
                    rpc.call("workspace.list", {}, timeout=20)
                    break
                except (urllib.error.URLError, RuntimeError, OSError):
                    if time.time() > t2:
                        raise
                    time.sleep(0.5)

            desc = rpc.call("settings.describe", {})
            perm = next(
                (
                    n
                    for n in desc.get("namespaces", [])
                    if isinstance(n, dict) and n.get("ns") == "permission"
                ),
                None,
            )
            if perm is None:
                raise RuntimeError("settings.describe 无 permission 命名空间")
            rpc.call(
                "settings.mutate",
                {
                    "ns": "permission",
                    "ops": [
                        {
                            "op": "set",
                            "path": ["defaultPreset"],
                            "value": "danger-full-access",
                        }
                    ],
                    "expectedRevision": perm.get("revision"),
                },
            )

            sid = "arena-task"
            rpc.call("session.create", {"sessionId": sid, "cwd": str(workdir)})
            rpc.call(
                "session.prompt",
                {
                    "sessionId": sid,
                    "mode": "queue",
                    "content": [{"type": "text", "text": task.prompt}],
                },
            )

            turn_deadline = time.time() + task.timeout_minutes * 60
            events: list[dict] = []
            while time.time() < turn_deadline:
                events = _norm(rpc.call("session.history", {"sessionId": sid}))
                if any(e.get("type") == "turn/end" for e in events):
                    break
                if proc.poll() is not None:
                    break
                time.sleep(2.0)
            full = _norm(_fetch_all(rpc, sid))
            transcript.parent.mkdir(parents=True, exist_ok=True)
            transcript.write_text(
                json.dumps(full, ensure_ascii=False, indent=1), encoding="utf-8"
            )
            usage = _summarize(full)
        except Exception as e:
            err = f"xharness error: {e!r}"
        finally:
            if proc is not None and proc.poll() is None:
                try:
                    shutdown.touch()
                    proc.wait(timeout=10)
                except Exception:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
        return AgentRun(ok=err is None, usage=usage, transcript=transcript, error=err)
