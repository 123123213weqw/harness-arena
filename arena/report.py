"""CLI 报表:总榜(adapter 维度)+ 分域透视。rich 可用则用 rich,否则纯文本。"""
from __future__ import annotations

from collections import defaultdict

from .runner import RunResult


def _aggregate(results: list[RunResult]):
    agg: dict[str, dict] = defaultdict(lambda: {
        "n": 0, "pass": 0, "fail": 0, "error": 0, "pending": 0,
        "in_tok": 0, "cache_tok": 0, "out_tok": 0, "sec": 0.0,
        "points": 0.0, "solved": 0,
    })
    dom: dict[tuple[str, str], list[str]] = defaultdict(list)
    domains: list[str] = []
    for r in results:
        a = agg[r.adapter]
        a["n"] += 1
        a["in_tok"] += r.usage.input_tokens
        a["cache_tok"] += r.usage.cache_tokens
        a["out_tok"] += r.usage.output_tokens
        a["sec"] += r.usage.seconds
        a["points"] += r.points
        if r.status == "pass":
            a["pass"] += 1
        elif r.status == "fail":
            a["fail"] += 1
        elif r.status == "error":
            a["error"] += 1
        else:
            a["pending"] += 1
        key = (r.adapter, r.task.domain)
        dom[key].append(r.status)
        if r.task.domain not in domains:
            domains.append(r.task.domain)
    return agg, dom, domains


def print_report(results: list[RunResult]) -> None:
    agg, dom, domains = _aggregate(results)
    from . import providers

    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()
        t1 = Table(title="总榜(本次运行;token 只记录不横比,成本为估算)", show_lines=False)
        for col in ("adapter", "n", "pass", "rate", "in_tok", "cache_tok",
                    "out_tok", "avg_sec", "¥/解", "pts"):
            t1.add_column(col, justify="right" if col != "adapter" else "left")
        for name, a in sorted(agg.items()):
            cost = sum(
                providers.estimate_cost_cny(r.usage)
                for r in results if r.adapter == name
            )
            per_solve = f"{cost / a['pass']:.2f}" if a["pass"] else "-"
            t1.add_row(
                name, str(a["n"]), str(a["pass"]),
                f"{a['pass'] / a['n']:.0%}" if a["n"] else "-",
                str(a["in_tok"]), str(a["cache_tok"]), str(a["out_tok"]),
                f"{a['sec'] / a['n']:.1f}", per_solve, f"{a['points']:.1f}",
            )
        console.print(t1)

        if domains:
            t2 = Table(title="分域 pass/total")
            t2.add_column("adapter")
            for d in domains:
                t2.add_column(d, justify="center")
            for name in sorted(agg):
                row = [name]
                for d in domains:
                    sts = dom.get((name, d), [])
                    p = sum(1 for s in sts if s == "pass")
                    row.append(f"{p}/{len(sts)}" if sts else "-")
                t2.add_row(*row)
            console.print(t2)
    except ImportError:
        print("\n== 总榜 ==")
        for name, a in sorted(agg.items()):
            rate = f"{a['pass'] / a['n']:.0%}" if a["n"] else "-"
            print(f"{name:<14} n={a['n']} pass={a['pass']} rate={rate} "
                  f"in={a['in_tok']} cache={a['cache_tok']} out={a['out_tok']} "
                  f"pts={a['points']:.1f}")
        print("\n== 分域 ==")
        for (name, d), sts in sorted(dom.items()):
            p = sum(1 for s in sts if s == "pass")
            print(f"{name:<14} {d:<10} {p}/{len(sts)}")
