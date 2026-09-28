#!/usr/bin/env python3
"""
MACD：用快慢两条 EMA 的差看趋势快慢，再用一条慢线平滑这个差。

默认参数 12, 26, 9。柱状图按国内行情软件：(DIF - DEA) * 2。

用法:
    python3 macd.py
    python3 macd.py sh600000
    python3 macd.py sz002129 12 26 9
"""
import sys

from ma import ema, load_close

# Gerald Appel 的日线经验参数，不是数学定理
FAST = 12
SLOW = 26
SIGNAL = 9


def macd(close, fast=FAST, slow=SLOW, signal=SIGNAL):
    """
    DIF  = EMA(收盘, fast) - EMA(收盘, slow)
    DEA  = EMA(DIF, signal)
    MACD = (DIF - DEA) * 2     # 国内软件的柱；TA-Lib 的 hist 不乘 2
    """
    if fast >= slow:
        raise ValueError("fast 必须小于 slow，否则快线不比慢线快")

    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)
    dif = ema_fast - ema_slow
    dea = ema(dif, signal)
    bar = (dif - dea) * 2
    return ema_fast, ema_slow, dif, dea, bar


def crosses(dif, dea):
    """DIF 上穿 DEA 为金叉，下穿为死叉。"""
    golden = (dif.shift(1) <= dea.shift(1)) & (dif > dea)
    death = (dif.shift(1) >= dea.shift(1)) & (dif < dea)
    return golden.fillna(False), death.fillna(False)


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    fast = int(sys.argv[2]) if len(sys.argv) > 2 else FAST
    slow = int(sys.argv[3]) if len(sys.argv) > 3 else SLOW
    signal = int(sys.argv[4]) if len(sys.argv) > 4 else SIGNAL

    df = load_close(code)
    ema_fast, ema_slow, dif, dea, bar = macd(df["close"], fast, slow, signal)
    df[f"ema{fast}"] = ema_fast
    df[f"ema{slow}"] = ema_slow
    df["dif"] = dif
    df["dea"] = dea
    df["macd"] = bar

    golden, death = crosses(df["dif"], df["dea"])
    print(f"{df.attrs['code']} {df.attrs['name']}")
    print(f"参数 fast={fast} slow={slow} signal={signal}")
    print(f"α_fast={2/(fast+1):.4f}  α_slow={2/(slow+1):.4f}  α_signal={2/(signal+1):.4f}")
    print("柱 macd = (dif - dea) * 2\n")
    print(df[[f"ema{fast}", f"ema{slow}", "dif", "dea", "macd"]].tail(8).round(4))

    print("\n最近金叉:")
    print(df.index[golden][-3:].strftime("%Y-%m-%d").tolist() or "（这段数据里没有）")
    print("最近死叉:")
    print(df.index[death][-3:].strftime("%Y-%m-%d").tolist() or "（这段数据里没有）")
    print("\n用法: python3 macd.py sh600000")
    print("      python3 macd.py sz002129 6 13 5")
