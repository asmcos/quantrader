#!/usr/bin/env python3
"""
RSI：这段时间里，上涨幅度占全部涨跌幅度的比例。

通达信默认画三条：6、12、24。西方教材常用 14，算法同一种，只是周期不同。

用法:
    python3 rsi.py
    python3 rsi.py sh600000
    python3 rsi.py sz002129 6 12 24
"""
import sys

from bars import load_bars, sma_cn

# 通达信默认
PERIODS = (6, 12, 24)


def rsi(close, n):
    """
    LC = 昨天收盘
    涨幅 = max(收盘 - LC, 0)
    振幅 = |收盘 - LC|
    RSI = SMA(涨幅, n, 1) / SMA(振幅, n, 1) * 100
    """
    change = close.diff()
    up = change.clip(lower=0)
    span = change.abs()
    up_avg = sma_cn(up, n, 1)
    span_avg = sma_cn(span, n, 1)
    return (up_avg / span_avg * 100).where(span_avg > 0)


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    periods = tuple(int(x) for x in sys.argv[2:]) or PERIODS

    df = load_bars(code)
    for n in periods:
        df[f"rsi{n}"] = rsi(df["close"], n)

    cols = [f"rsi{n}" for n in periods]
    print(f"{df.attrs['code']} {df.attrs['name']}")
    print(f"RSI 周期 {periods}，范围 0～100\n")
    print(df[cols].tail(8).round(2))
    print("\n用法: python3 rsi.py sh600000")
    print("      python3 rsi.py sz002129 14")
