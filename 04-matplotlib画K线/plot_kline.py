#!/usr/bin/env python3
"""
日 K、成交量、均线、MACD 画在一张图里。

均线和 MACD 用 03 的算法，在全部日 K 上算完，再只画最近一段。

用法:
    python3 plot_kline.py
    python3 plot_kline.py sh600000
    python3 plot_kline.py sz002129 120
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "01-股票的数据获取"))
sys.path.insert(0, os.path.join(ROOT, "03-均线和MACD"))

import day_k_qq
import pandas as pd
from ma import sma
from macd import macd

# 红涨绿跌
UP = "#d62728"
DOWN = "#2ca02c"
MA_COLORS = {5: "#e67e22", 10: "#2980b9", 20: "#8e44ad"}
MA_PERIODS = (5, 10, 20)


def load_dayk(code):
    raw = day_k_qq.get_dayk(code)
    if not raw:
        raise RuntimeError(f"获取失败: {code}")
    d = raw["data"]
    df = pd.DataFrame(d["dayks"])
    df["day"] = pd.to_datetime(df["day"])
    df = df.set_index("day").sort_index()
    for col in ("open", "close", "high", "low", "volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.attrs["code"] = d.get("code", code)
    df.attrs["name"] = d.get("name", "")
    return df


def add_indicators(df):
    out = df.copy()
    for n in MA_PERIODS:
        out[f"ma{n}"] = sma(out["close"], n)
    _, _, dif, dea, bar = macd(out["close"])
    out["dif"] = dif
    out["dea"] = dea
    out["macd"] = bar
    return out


def _setup_font():
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "AR PL UKai CN", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def plot(df, png_path):
    _setup_font()
    view = df.dropna(subset=["open", "close", "high", "low"]).copy()
    n = len(view)
    xs = list(range(n))
    up = view["close"] >= view["open"]

    fig, (ax_k, ax_v, ax_m) = plt.subplots(
        3, 1, sharex=True, figsize=(12, 8),
        gridspec_kw={"height_ratios": [3, 1, 1.3]},
    )
    fig.subplots_adjust(hspace=0.05)

    for i, row in enumerate(view.itertuples()):
        color = UP if row.close >= row.open else DOWN
        ax_k.vlines(i, row.low, row.high, color=color, linewidth=0.8)
        bottom = min(row.open, row.close)
        height = abs(row.close - row.open)
        if height == 0:
            height = max(row.close * 0.001, 0.01)
            bottom -= height / 2
        ax_k.add_patch(Rectangle((i - 0.3, bottom), 0.6, height, facecolor=color, edgecolor=color))
        ax_v.bar(i, row.volume, width=0.6, color=color)

    for period in MA_PERIODS:
        ax_k.plot(xs, view[f"ma{period}"], color=MA_COLORS[period], linewidth=1, label=f"MA{period}")

    bar_colors = [UP if v >= 0 else DOWN for v in view["macd"]]
    ax_m.bar(xs, view["macd"], width=0.6, color=bar_colors)
    ax_m.plot(xs, view["dif"], color="#2980b9", linewidth=1, label="DIF")
    ax_m.plot(xs, view["dea"], color="#e67e22", linewidth=1, label="DEA")
    ax_m.axhline(0, color="#888888", linewidth=0.6)

    step = max(n // 8, 1)
    ax_m.set_xticks(xs[::step])
    ax_m.set_xticklabels([d.strftime("%m-%d") for d in view.index[::step]], rotation=0)
    ax_k.set_xlim(-1, n)
    name = view.attrs.get("name") or ""
    code = view.attrs.get("code") or ""
    ax_k.set_title(f"{name} {code}  日K / 成交量 / MACD(12,26,9)")
    ax_k.legend(loc="upper left", frameon=False, ncol=3)
    ax_m.legend(loc="upper left", frameon=False, ncol=2)
    ax_k.set_ylabel("价格")
    ax_v.set_ylabel("成交量")
    ax_m.set_ylabel("MACD")

    fig.savefig(png_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    bars = int(sys.argv[2]) if len(sys.argv) > 2 else 120

    df = add_indicators(load_dayk(code))
    view = df.tail(bars)
    view.attrs = df.attrs

    out_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(out_dir, f"{code}_kline.png")
    plot(view, png_path)
    print(f"{df.attrs.get('code')} {df.attrs.get('name')}  画出最近 {len(view)} 根")
    print(f"已保存: {png_path}")
    print("\n用法: python3 plot_kline.py sh600000 80")
