"""从 SQLite 生成本次 suite 的 Tier-B 对比报告(Markdown)。

用法:.venv/bin/python scripts/battle_report.py [suite_id] > BATTLE.md
不传 suite_id 时取最近一次。
"""
from __future__ import annotations

import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

from arena import providers

DB = Path(__file__).resolve().parents[1] / "runs" / "arena.db"

ARMS = "xharness", "claude-code", "codex", "pi"

VERSIONS = {
    "xharness": "x-harness-rs@74f378c(gitee 镜像源码构建,2026-10-02 main)",
    "claude-code": "Claude Code 2.1.212(Anthropic 兼容端点)",
    "codex": "codex-cli 0.142.0(Responses API 直连)",
    "pi": "pi 0.74.2(@earendil-works/pi-coding-agent)",
}


def main() -> None:
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    suite = sys.argv[1] if len(sys.argv) > 1 else db.execute(
        "select suite from runs order by ts desc limit 1"
    ).fetchone()[0]
    rows = db.execute(
        "select * from runs where suite = ? order by adapter, task_id, repeat",
        (suite,),
    ).fetchall()
    if not rows:
        sys.exit(f"suite {suite} 无记录")

    by_arm: dict[str, dict[str, list[sqlite3.Row]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_arm[r["adapter"]][r["task_id"]].append(r)

    lines = []
    lines.append(f"# Tier-B 四 harness 对比报告(suite {suite})")
    lines.append("")
    lines.append("## 实验设置")
    lines.append("")
    lines.append("- **模型全程唯一**:`deepseek-chat` @ api.deepseek.com(DeepSeek,四臂同一 key)")
    lines.append("- **任务 12 道**:coding 4 / algo 3 / math 3 / data 1 / ops 1,隐藏判定,工作区每题从零初始化")
    lines.append("- **每题 ×2 次重复**;上下文窗口:xharness 显式 1,000,000,其余为各自默认")
    lines.append("- 判定全部由**外部隐藏测试/脚本**完成,不采信 harness 自评")
    lines.append("")
    lines.append("| 臂 | 版本 |")
    lines.append("|---|---|")
    for arm in ARMS:
        lines.append(f"| {arm} | {VERSIONS[arm]} |")
    lines.append("")

    lines.append("## 主榜(外部验证)")
    lines.append("")
    lines.append("| 臂 | 题(≥1次过) | 2/2稳定 | 严格通过率 | 总分 |")
    lines.append("|---|---|---|---|---|")
    for arm in ARMS:
        if arm not in by_arm:
            continue
        solved = sum(
            1
            for runs in by_arm[arm].values()
            if any(r["status"] == "pass" for r in runs)
        )
        stable = sum(
            1
            for runs in by_arm[arm].values()
            if all(r["status"] == "pass" for r in runs) and runs
        )
        n = len(by_arm[arm])
        pts = sum(r["points"] for r in rows if r["adapter"] == arm)
        lines.append(
            f"| {arm} | {solved}/{n} | {stable}/{n} | {solved / n:.0%} | {pts:.1f} |"
        )
    lines.append("")

    lines.append("## 效率(token 只记录,不横向排名;成本为统一牌价估算)")
    lines.append("")
    lines.append("| 臂 | 输入(新) | 缓存读 | 输出 | 估算成本¥ | ¥/解出题 | 平均耗时s |")
    lines.append("|---|---|---|---|---|---|---|")
    for arm in ARMS:
        if arm not in by_arm:
            continue
        rs = [r for r in rows if r["adapter"] == arm]
        inp = sum(r["input_tokens"] or 0 for r in rs)
        cach = sum(r["cache_tokens"] or 0 for r in rs)
        outp = sum(r["output_tokens"] or 0 for r in rs)
        reas = sum(r["reasoning_tokens"] or 0 for r in rs)
        cost = sum(
            providers.estimate_cost_cny(type("U", (), {
                "input_tokens": r["input_tokens"] or 0,
                "cache_tokens": r["cache_tokens"] or 0,
                "output_tokens": r["output_tokens"] or 0,
                "reasoning_tokens": r["reasoning_tokens"] or 0,
            })) for r in rs
        )
        solved = sum(
            1
            for runs in by_arm[arm].values()
            if any(r["status"] == "pass" for r in runs)
        )
        sec = sum(r["seconds"] or 0 for r in rs) / len(rs)
        lines.append(
            f"| {arm} | {inp:,} | {cach:,} | {outp:,} | {cost:.2f} | "
            f"{cost / solved:.2f} | {sec:.1f} |"
        )
    lines.append("")

    lines.append("## 分题矩阵(每格:2 次中通过次数)")
    lines.append("")
    task_ids = sorted({r["task_id"] for r in rows})
    header = "| 题 | " + " | ".join(a for a in ARMS if a in by_arm) + " |"
    lines.append(header)
    lines.append("|---" * (1 + len([a for a in ARMS if a in by_arm])) + "|")
    for t in task_ids:
        cells = []
        for arm in ARMS:
            if arm not in by_arm:
                continue
            runs = by_arm[arm].get(t, [])
            p = sum(1 for r in runs if r["status"] == "pass")
            cells.append(f"{p}/{len(runs)}" if runs else "-")
        lines.append(f"| {t} | " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("## 效率分(用的多,分数低;失败题烧的钱也计入)")
    lines.append("")
    lines.append("效率分 = 解出题数 × (全场最低总成本 ÷ 本臂总成本)。最省臂不打折,花 3 倍钱只拿 1/3 折。")
    lines.append("")
    arm_cost = {}
    arm_solved = {}
    for arm in ARMS:
        if arm not in by_arm:
            continue
        rs = [r for r in rows if r["adapter"] == arm]
        arm_cost[arm] = sum(
            providers.estimate_cost_cny(type("U", (), {
                "input_tokens": r["input_tokens"] or 0,
                "cache_tokens": r["cache_tokens"] or 0,
                "output_tokens": r["output_tokens"] or 0,
                "reasoning_tokens": r["reasoning_tokens"] or 0,
            })) for r in rs
        )
        arm_solved[arm] = sum(
            1
            for runs in by_arm[arm].values()
            if any(r["status"] == "pass" for r in runs)
        )
    min_cost = min(arm_cost.values()) if arm_cost else 1
    lines.append("| 臂 | 解出 | 总成本¥ | 次数 | 单次成本¥ | 成本折扣 | **效率分** | 每题最省赢家数 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    task_ids2 = sorted({r["task_id"] for r in rows})
    arm_runs = {
        a: len([r for r in rows if r["adapter"] == a]) for a in arm_cost
    }
    avg_cost = {
        a: (arm_cost[a] / arm_runs[a] if arm_runs.get(a) else 0) for a in arm_cost
    }
    min_avg = min(avg_cost.values()) if avg_cost else 1
    for arm in ARMS:
        if arm not in by_arm:
            continue
        cheapest = 0
        for t in task_ids2:
            cand = []
            for a in ARMS:
                if a not in by_arm:
                    continue
                runs = by_arm[a].get(t, [])
                if any(r["status"] == "pass" for r in runs):
                    c = sum(
                        providers.estimate_cost_cny(type("U", (), {
                            "input_tokens": r["input_tokens"] or 0,
                            "cache_tokens": r["cache_tokens"] or 0,
                            "output_tokens": r["output_tokens"] or 0,
                            "reasoning_tokens": r["reasoning_tokens"] or 0,
                        })) for r in runs
                    )
                    cand.append((c, a))
            if cand and min(cand)[1] == arm:
                cheapest += 1
        disc = (min_avg / avg_cost[arm]) if avg_cost.get(arm) else 0
        lines.append(
            f"| {arm} | {arm_solved[arm]} | {arm_cost[arm]:.2f} | {arm_runs[arm]} | "
            f"{avg_cost[arm]:.3f} | ×{disc:.2f} | "
            f"**{arm_solved[arm] * disc:.1f}** | {cheapest} |"
        )
    lines.append("")

    lines.append("## 注意事项(照 xharness-bench 的 Tier-B 纪律)")
    lines.append("")
    lines.append("- 各臂 system prompt 与工具面不同,是**实验处理的一部分**,不是干扰项;")
    lines.append("- token 记账口径各家不同(缓存/推理是否计入、何处累计),只记录不横比;")
    lines.append("- 12 题样本下,**差距 < 8 个百分点即在分辨率之内**,不作强结论;")
    lines.append("- 运行未做臂间交错调度,DeepSeek 服务端负载随时间的波动未完全消除。")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
