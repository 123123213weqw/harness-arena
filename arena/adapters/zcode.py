"""ZCode headless 适配(第五臂,原生模型 GLM)。

ZCode CLI 打包在桌面 app 内(glm/zcode.cjs),已部署到 V100 ~/zcode-cli/:
  - 运行时:~/node22/bin/node ~/zcode-cli/zcode.cjs(Node ≥ 22)
  - builtin provider 表:~/zcode-cli/provider/(从 app Resources/config/provider 拷贝)
  - arena provider 配置:~/zcode-cli/arena-config/providers.json
    (zai-api + api-key + defaultModelSelection GLM-5.3-Flash,schema 见下)
  - 隔离:ZCODE_PERSONAL_PROVIDER_CONFIG_FILE 指向 arena 配置,
    ZCODE_STORAGE_DIR 指向工作区内,不碰用户实盘配置

provider config schema(逆向自 0.17.0,strict 校验,字段名必须精确):
  config.providerConfigRules.providerRules[] = {providerId, templateId?, providerName?,
    config: {access:{type:"api-key",apiKey}, api?:{type:"openai-chat-completions"|
    "openai-responses"|"anthropic-messages", baseUrl}, builtinModelIds?, modelOrder?}}
  config.defaultModelSelection = {providerId, modelId}   ← 必须在 config 内部,顶层无效

记账:跑完后读 ZCODE_STORAGE_DIR 下最新的 cli/rollout/model-io-*.jsonl,
逐条累加 usage{inputTokens,outputTokens,cacheReadTokens}(与 xharness 同口径)。
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from ..schema import Task
from .base import AgentRun, Usage

NODE_BIN = os.environ.get("ZCODE_NODE_BIN", str(Path.home() / "node22" / "bin" / "node"))
ZCODE_CJS = os.environ.get("ZCODE_CJS", str(Path.home() / "zcode-cli" / "zcode.cjs"))
PROVIDER_FILE = os.environ.get(
    "ZCODE_PROVIDER_FILE", str(Path.home() / "zcode-cli" / "arena-config" / "providers.json")
)
MODEL = os.environ.get("ARENA_ZCODE_MODEL", "GLM-5.3-Flash")


def _num(d: dict, *names: str) -> int:
    for n in names:
        v = d.get(n)
        if isinstance(v, (int, float)):
            return int(v)
    return 0


class ZcodeAdapter:
    name = "zcode"
    model = MODEL

    def run(self, task: Task, workdir: Path) -> AgentRun:
        usage = Usage()
        storage = (workdir / ".arena" / "zcode-storage").resolve()
        storage.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        env = {
            **os.environ,
            "ZCODE_PERSONAL_PROVIDER_CONFIG_FILE": PROVIDER_FILE,
            "ZCODE_STORAGE_DIR": str(storage),
        }
        try:
            r = subprocess.run(
                [
                    NODE_BIN, ZCODE_CJS,
                    "-p", task.prompt,
                    "--mode", "yolo",
                    "--no-color",
                ],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=task.timeout_minutes * 60 + 60,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return AgentRun(ok=False, usage=usage, error="zcode 超时")
        usage.seconds = time.time() - t0
        out_path = workdir / ".arena" / "zcode.out"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(r.stdout, encoding="utf-8")

        # 记账:rollout 里所有 model-io 记录的 usage 求和
        rollouts = sorted(storage.glob("cli/rollout/model-io-*.jsonl"))
        if rollouts:
            transcript = rollouts[-1]
            for line in transcript.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                # 记录结构:response.usage 为准(顶层 usage 为旧格式回退)
                u = (rec.get("response") or {}).get("usage") or rec.get("usage")
                if isinstance(u, dict) and (
                    _num(u, "inputTokens") or _num(u, "outputTokens")
                ):
                    usage.calls += 1
                    usage.input_tokens += _num(u, "inputTokens")
                    usage.output_tokens += _num(u, "outputTokens")
                    usage.cache_tokens += _num(u, "cacheReadTokens")
                    usage.reasoning_tokens += _num(u, "reasoningTokens")
        return AgentRun(
            ok=r.returncode == 0,
            usage=usage,
            transcript=rollouts[-1] if rollouts else out_path,
            error=(r.stderr.strip()[-400:] or None) if r.returncode != 0 else None,
        )
