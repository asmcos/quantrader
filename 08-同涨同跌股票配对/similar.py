#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08 — 同涨同跌的股票配对。

数据来自 Klang 的本地缓存 ~/.klang/day/<code>day.json（由 Klang 的
tools/eltdx_updater.py 更新），不联网、不装额外行情库。

两种用法：
    python3 similar.py                          # 扫股票池，挑最像的一对并画图
    python3 similar.py --codes sh.600519 sz.000858 sh.601398
"""
import argparse
import csv
import itertools
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
KLANG = Path.home() / ".klang"

# 本地股票列表的 tdxbk/tdxgn 是空的，先放一张可编辑的小股票池演示。
# 想研究哪一类，就把同类股票写进 universe.csv 的同一个 group。
BUILTIN_UNIVERSE = {
    "白酒": ["sh.600519", "sz.000858", "sh.600809", "sz.000568"],
    "银行": ["sh.601398", "sh.601939", "sh.601288", "sh.600036"],
    "电池": ["sz.300750", "sz.300014", "sz.002074", "sh.688567"],
    "半导体": ["sh.688981", "sh.688347", "sh.603986", "sz.002049"],
}


def norm_code(code):
    c = str(code).strip().lower()
    if "." not in c and c[:2] in ("sh", "sz", "bj") and len(c) > 2:
        c = c[:2] + "." + c[2:]
    return c


def load_series(code, days):
    path = KLANG / "day" / (norm_code(code) + "day.json")
    if not path.exists():
        raise FileNotFoundError(f"没有本地日K: {path}")
    obj = json.loads(path.read_text(encoding="utf-8"))
    # Klang 日K 倒序存放，开盘前还有一条 volume=0 的占位，先排正序再剔掉。
    bars = [b for b in obj[2] if float(b.get("volume") or 0) > 0]
    bars.sort(key=lambda b: b["date"])
    if len(bars) < days + 5:
        raise ValueError(f"{code} 有效日K只有 {len(bars)} 根")
    s = pd.Series({b["date"]: float(b["close"]) for b in bars}, dtype=float)
    return s.tail(days), (obj[1] or code)


def load_universe(path):
    if not Path(path).exists():
        return {k: list(v) for k, v in BUILTIN_UNIVERSE.items()}, {}
    groups, names = {}, {}
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            code = norm_code(row.get("code", ""))
            if not code:
                continue
            group = (row.get("group") or "默认").strip()
            groups.setdefault(group, []).append(code)
            if row.get("name"):
                names[code] = row["name"].strip()
    return groups, names


def pair_metrics(sa, sb, roll_window=40):
    df = pd.concat([sa.rename("a"), sb.rename("b")], axis=1).dropna()
    ret = df.pct_change().dropna()
    x, y = ret["a"], ret["b"]
    # 过滤掉两边都不动的平盘日，否则“同向率”会被噪声抬高。
    mask = (x.abs() > 0.001) & (y.abs() > 0.001)
    hit = float((np.sign(x[mask]) == np.sign(y[mask])).mean()) if mask.any() else 0.0
    corr = float(x.corr(y))
    spear = float(x.corr(y, method="spearman"))
    beta = float(np.polyfit(y.values, x.values, 1)[0]) if len(x) > 2 else float("nan")
    roll = x.rolling(roll_window, min_periods=20).corr(y).dropna()
    stable = float((roll > 0.6).mean()) if len(roll) else 0.0
    # 谁先动：a 今天和 b 昨天、a 昨天和 b 今天的相关谁更高。
    lead = float(x.corr(y.shift(1)))
    lag = float(x.shift(1).corr(y))
    na = np.log(df["a"] / df["a"].iloc[0])
    nb = np.log(df["b"] / df["b"].iloc[0])
    curve_gap = float(np.mean(np.abs(na - nb)))
    return {
        "corr": corr,
        "spearman": spear,
        "hit": hit,
        "beta": beta,
        "stable": stable,
        "lead": lead,
        "lag": lag,
        "curve_gap": curve_gap,
        "ret_a": float(df["a"].iloc[-1] / df["a"].iloc[0] - 1),
        "ret_b": float(df["b"].iloc[-1] / df["b"].iloc[0] - 1),
        "days": len(ret),
        "score": 0.45 * max(corr, 0) + 0.35 * hit + 0.20 * stable,
    }


def scan(groups, series, names, min_corr, min_hit):
    rows = []
    for group, codes in groups.items():
        codes = [c for c in codes if c in series]
        for a, b in itertools.combinations(codes, 2):
            m = pair_metrics(series[a], series[b])
            if m["corr"] < min_corr or m["hit"] < min_hit:
                continue
            rows.append({
                "group": group,
                "code_a": a, "name_a": names.get(a, ""),
                "code_b": b, "name_b": names.get(b, ""),
                **{k: round(v, 4) for k, v in m.items()},
            })
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)


def plot(series, pairs, names, path):
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "AR PL UKai CN", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))

    ax = axes[0, 0]
    for code, s in series.items():  # series 这里只放被选中的 2-3 只
        curve = s / s.iloc[0] * 100
        ax.plot(curve.index, curve.values, linewidth=1.4, label=f"{names.get(code, code)} {code}")
    ax.set_title("归一化价格（起点=100）")
    ax.legend(fontsize=8, frameon=False)
    ax.tick_params(axis="x", labelrotation=30, labelsize=8)

    if pairs:
        a, b = pairs[0]["code_a"], pairs[0]["code_b"]
        df = pd.concat([series[a].rename("a"), series[b].rename("b")], axis=1).dropna()
        ret = df.pct_change().dropna()

        ax = axes[0, 1]
        ax.scatter(ret["b"] * 100, ret["a"] * 100, s=8, alpha=0.45, color="#4a6fa5")
        slope = np.polyfit(ret["b"], ret["a"], 1)
        xs = np.linspace(ret["b"].min(), ret["b"].max(), 50)
        ax.plot(xs, np.polyval(slope, xs) * 100, color="#c0392b", linewidth=1.2)
        ax.set_xlabel(f"{names.get(b, b)} 日收益 %")
        ax.set_ylabel(f"{names.get(a, a)} 日收益 %")
        ax.set_title("日收益散点与拟合线")

        ax = axes[1, 0]
        roll = ret["a"].rolling(40, min_periods=20).corr(ret["b"])
        ax.plot(roll.index, roll.values, color="#2980b9", linewidth=1.2)
        ax.axhline(0.6, color="#999999", linestyle="--", linewidth=0.8)
        ax.set_ylim(-1, 1)
        ax.set_title("40 日滚动相关")
        ax.tick_params(axis="x", labelrotation=30, labelsize=8)

        ax = axes[1, 1]
        labels = [f"{names.get(p['code_a'], p['code_a'])}\n/ {names.get(p['code_b'], p['code_b'])}" for p in pairs[:4]]
        vals = np.array([[p["corr"], p["hit"], p["stable"]] for p in pairs[:4]])
        xpos = np.arange(len(labels))
        w = 0.25
        for i, (color, key) in enumerate([("#c0392b", "相关系数"), ("#2980b9", "同向率"), ("#27ae60", "稳定度")]):
            ax.bar(xpos + (i - 1) * w, vals[:, i], w, label=key, color=color)
        ax.set_xticks(xpos)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylim(0, 1.15)
        ax.legend(frameon=False, fontsize=7, loc="upper left", ncol=3)
        ax.set_title("候选对三项指标")
    else:
        axes[1, 1].axis("off")
        axes[0, 1].axis("off")
        axes[1, 0].axis("off")

    fig.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def write_report(path, window, pairs_df, names):
    lines = [
        "# 08 — 同涨同跌股票配对报告",
        "",
        f"数据：Klang 本地日K，窗口 {window[0]} 至 {window[1]}，共 {window[2]} 只股票参与。",
        "",
        "| A | B | 组 | 相关 | 同向率 | 稳定度 | beta | 谁先动 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, r in pairs_df.iterrows():
        lead = "A先动" if r["lead"] > r["lag"] + 0.05 else ("B先动" if r["lag"] > r["lead"] + 0.05 else "同步")
        lines.append(
            f"| {names.get(r['code_a'], r['code_a'])} {r['code_a']} | "
            f"{names.get(r['code_b'], r['code_b'])} {r['code_b']} | {r['group']} | "
            f"{r['corr']:.2f} | {r['hit']:.0%} | {r['stable']:.0%} | "
            f"{r['beta']:.2f} | {lead} |"
        )
    lines += [
        "",
        "相关：日收益的 Pearson 系数。同向率：两边都动了的日子里方向一致的比例。",
        "稳定度：40 日滚动相关大于 0.6 的比例。beta：B 每涨 1%，A 平均涨多少。",
        "",
        "这只是把走势放在一起看，不代表基本面同类，也不代表以后还这样。",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="用 Klang 数据找同涨同跌的股票")
    ap.add_argument("--codes", nargs="+", help="直接比较 2-3 只指定股票")
    ap.add_argument("--universe", default=str(HERE / "universe.csv"), help="股票池 CSV：code,group,name")
    ap.add_argument("--days", type=int, default=120, help="回看交易日数，默认 120")
    ap.add_argument("--min-corr", type=float, default=0.70)
    ap.add_argument("--min-hit", type=float, default=0.65)
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    groups, names = load_universe(args.universe)
    if args.codes:
        codes = [norm_code(c) for c in args.codes]
        groups = {"手工指定": codes}

    series, meta = {}, {}
    for code in dict.fromkeys(c for cs in groups.values() for c in cs):
        try:
            series[code], meta[code] = load_series(code, args.days)
        except Exception as exc:
            print(f"跳过 {code}: {exc}")
    for code, name in meta.items():
        names.setdefault(code, name)
    if len(series) < 2:
        raise SystemExit("有效股票不足 2 只")

    result = scan(groups, series, names, args.min_corr, args.min_hit)
    if result.empty:
        print(f"没有达到 相关>={args.min_corr} 且 同向率>={args.min_hit} 的候选对，展示前两只做对照")
        rows = []
        for a, b in itertools.combinations(list(series)[:2], 2):
            rows.append({
                "group": "手工指定", "code_a": a, "name_a": names.get(a, ""),
                "code_b": b, "name_b": names.get(b, ""),
                **{k: round(v, 4) for k, v in pair_metrics(series[a], series[b]).items()},
            })
        result = pd.DataFrame(rows)
    result.to_csv(HERE / "pairs.csv", index=False, encoding="utf-8-sig")

    top = result.head(args.top).to_dict("records")
    show = top[:3] if args.codes else top[:1]
    if args.codes:
        shown_codes = codes
    elif show:
        shown_codes = [show[0]["code_a"], show[0]["code_b"]]
    else:
        shown_codes = list(series)[:2]
    window = (min(s.index[0] for s in series.values()),
              max(s.index[-1] for s in series.values()), len(series))
    plot({c: series[c] for c in shown_codes if c in series}, show, names, HERE / "compare.png")
    write_report(HERE / "report.md", window, result.head(args.top), names)

    print(f"窗口 {window[0]} ~ {window[1]}，有效股票 {len(series)} 只")
    print(f"候选对 {len(result)} 组，前 {min(args.top, len(result))} 组：\n")
    cols = ["group", "code_a", "name_a", "code_b", "name_b", "corr", "hit", "stable", "beta", "score"]
    print(result.reindex(columns=cols).to_string(index=False))
    print(f"\n已保存: {HERE / 'pairs.csv'}")
    print(f"已保存: {HERE / 'compare.png'}")
    print(f"已保存: {HERE / 'report.md'}")


if __name__ == "__main__":
    main()
