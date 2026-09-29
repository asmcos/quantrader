#!/usr/bin/env python3
"""
用 mplfinance（import 时习惯写成 mpf）画日 K、成交量、均线和 MACD。

蜡烛和成交量交给 mplfinance。均线、MACD 仍用 03 的算法，
在全部日 K 上算完再截取，不用 mplfinance 自带的 mav（那会只在截取后的窗口里重算）。

用法:
    python3 plot_kline_mpf.py
    python3 plot_kline_mpf.py sh600000
    python3 plot_kline_mpf.py sz002129 120
"""
import os
import sys

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "03-均线和MACD"))

import mplfinance as mpf

from plot_kline import add_indicators, load_dayk

UP = "#d62728"
DOWN = "#2ca02c"


def to_mpf_frame(df):
    """mplfinance 要求列名为 Open/High/Low/Close/Volume。"""
    out = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
    })
    return out


def plot(df, png_path, title):
    style = mpf.make_mpf_style(
        marketcolors=mpf.make_marketcolors(
            up=UP,
            down=DOWN,
            edge="inherit",
            wick="inherit",
            volume="in",
        ),
        rc={
            "font.sans-serif": ["Noto Sans CJK SC", "AR PL UKai CN", "DejaVu Sans"],
            "axes.unicode_minus": False,
        },
    )
    bar_colors = [UP if v >= 0 else DOWN for v in df["macd"]]
    addplots = [
        mpf.make_addplot(df["ma5"], color="#e67e22"),
        mpf.make_addplot(df["ma10"], color="#2980b9"),
        mpf.make_addplot(df["ma20"], color="#8e44ad"),
        mpf.make_addplot(df["dif"], panel=2, color="#2980b9", ylabel="MACD"),
        mpf.make_addplot(df["dea"], panel=2, color="#e67e22"),
        mpf.make_addplot(df["macd"], type="bar", panel=2, color=bar_colors),
    ]
    mpf.plot(
        to_mpf_frame(df),
        type="candle",
        volume=True,
        addplot=addplots,
        style=style,
        title=title,
        figsize=(12, 8),
        datetime_format="%m-%d",
        tight_layout=True,
        savefig=dict(fname=png_path, dpi=120, bbox_inches="tight"),
    )


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    bars = int(sys.argv[2]) if len(sys.argv) > 2 else 120

    df = add_indicators(load_dayk(code))
    view = df.tail(bars)
    name = df.attrs.get("name") or ""
    symbol = df.attrs.get("code") or code

    out_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(out_dir, f"{code}_kline_mpf.png")
    plot(view, png_path, f"{name} {symbol}  mplfinance  日K / 成交量 / MACD(12,26,9)")
    print(f"{symbol} {name}  画出最近 {len(view)} 根")
    print(f"已保存: {png_path}")
    print("\n用法: python3 plot_kline_mpf.py sh600000 80")
