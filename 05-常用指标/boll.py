#!/usr/bin/env python3
"""
布林带：中轨是收盘价的简单均线，上下轨是中轨加减若干倍标准差。

通达信默认周期 20，宽度 2 倍标准差。

用法:
    python3 boll.py
    python3 boll.py sh600000
    python3 boll.py sz002129 20 2
"""
import sys

from bars import load_bars

N = 20
K = 2


def boll(close, n=N, k=K):
    """
    MID = MA(收盘, n)
    UPPER = MID + k * STD(收盘, n)
    LOWER = MID - k * STD(收盘, n)

    标准差按这 n 天整体计算（除以 n），与通达信 STD 一致。
    """
    mid = close.rolling(n, min_periods=n).mean()
    std = close.rolling(n, min_periods=n).std(ddof=0)
    return mid, mid + k * std, mid - k * std


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else N
    k = float(sys.argv[3]) if len(sys.argv) > 3 else K

    df = load_bars(code)
    df["mid"], df["upper"], df["lower"] = boll(df["close"], n, k)
    df["width"] = (df["upper"] - df["lower"]) / df["mid"] * 100
    print(f"{df.attrs['code']} {df.attrs['name']}")
    print(f"参数 周期={n}  倍数={k}")
    print("width 是上下轨距离占中轨的百分比\n")
    print(df[["close", "lower", "mid", "upper", "width"]].tail(8).round(3))
    print("\n用法: python3 boll.py sh600000")
    print("      python3 boll.py sz002129 20 2")
