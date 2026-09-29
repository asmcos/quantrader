#!/usr/bin/env python3
"""
KDJ：收盘价在最近 N 天最高、最低之间的位置，再做两次平滑。

通达信默认 N=9, M1=3, M2=3。

用法:
    python3 kdj.py
    python3 kdj.py sh600000
    python3 kdj.py sz002129 9 3 3
"""
import sys

from bars import load_bars, sma_cn

N, M1, M2 = 9, 3, 3


def kdj(df, n=N, m1=M1, m2=M2):
    """
    RSV = (收盘 - N日最低) / (N日最高 - N日最低) * 100
    K   = SMA(RSV, M1, 1)
    D   = SMA(K, M2, 1)
    J   = 3*K - 2*D
    """
    low_n = df["low"].rolling(n, min_periods=n).min()
    high_n = df["high"].rolling(n, min_periods=n).max()
    span = high_n - low_n
    rsv = ((df["close"] - low_n) / span * 100).where(span > 0)
    k = sma_cn(rsv, m1, 1)
    d = sma_cn(k, m2, 1)
    j = 3 * k - 2 * d
    return k, d, j


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else N
    m1 = int(sys.argv[3]) if len(sys.argv) > 3 else M1
    m2 = int(sys.argv[4]) if len(sys.argv) > 4 else M2

    df = load_bars(code)
    df["k"], df["d"], df["j"] = kdj(df, n, m1, m2)
    print(f"{df.attrs['code']} {df.attrs['name']}")
    print(f"参数 N={n} M1={m1} M2={m2}")
    print("K、D 多在 0～100；J = 3K-2D，可以超出这个范围\n")
    print(df[["k", "d", "j"]].tail(8).round(2))
    print("\n用法: python3 kdj.py sh600000")
    print("      python3 kdj.py sz002129 9 3 3")
