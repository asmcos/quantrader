#!/usr/bin/env python3
"""
MACD 买卖：金叉满仓买入，死叉全部卖出。

信号和成交都用当天收盘价。不算手续费，一次只持有这一只股票。
前 slow+signal 根（默认 35 根）的交叉丢掉，避免 EMA 起点还没稳定就交易。

用法:
    python3 trade.py
    python3 trade.py sh600000
    python3 trade.py sz002129 12 26 9
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "03-均线和MACD"))

from macd import FAST, SIGNAL, SLOW, crosses, macd
from ma import load_close


def simulate(df, fast=FAST, slow=SLOW, signal=SIGNAL):
    """从第 slow+signal 根之后开始认交叉。返回交易表和期末权益（期初资金记为 1）。"""
    _, _, dif, dea, bar = macd(df["close"], fast, slow, signal)
    golden, death = crosses(dif, dea)
    warm = slow + signal
    golden = golden.copy()
    death = death.copy()
    golden.iloc[:warm] = False
    death.iloc[:warm] = False

    cash = 1.0
    shares = 0.0
    entry_day = None
    entry_px = None
    trades = []

    for day, row_g, row_d, close in zip(df.index, golden, death, df["close"]):
        if row_g and shares == 0:
            shares = cash / close
            cash = 0.0
            entry_day = day
            entry_px = close
        elif row_d and shares > 0:
            cash = shares * close
            shares = 0.0
            ret = close / entry_px - 1
            trades.append({
                "buy": entry_day,
                "sell": day,
                "buy_px": entry_px,
                "sell_px": close,
                "days": (day - entry_day).days,
                "ret": ret,
                "open": False,
            })
            entry_day = None

    if shares > 0:
        last_day = df.index[-1]
        last_px = df["close"].iloc[-1]
        trades.append({
            "buy": entry_day,
            "sell": last_day,
            "buy_px": entry_px,
            "sell_px": last_px,
            "days": (last_day - entry_day).days,
            "ret": last_px / entry_px - 1,
            "open": True,
        })
        equity = shares * last_px
    else:
        equity = cash

    hold_ret = df["close"].iloc[-1] / df["close"].iloc[warm] - 1
    return trades, equity - 1, hold_ret, golden, death


def save_plot(df, golden, death, png_path, title):
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "AR PL UKai CN", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df.index, df["close"], color="#333333", linewidth=1, label="收盘")
    buys = df.index[golden]
    sells = df.index[death]
    ax.scatter(buys, df.loc[buys, "close"], marker="^", color="#d62728", s=40, label="买入", zorder=3)
    ax.scatter(sells, df.loc[sells, "close"], marker="v", color="#2ca02c", s=40, label="卖出", zorder=3)
    ax.set_title(title)
    ax.set_ylabel("价格")
    ax.legend(frameon=False, loc="upper left")
    fig.savefig(png_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    fast = int(sys.argv[2]) if len(sys.argv) > 2 else FAST
    slow = int(sys.argv[3]) if len(sys.argv) > 3 else SLOW
    signal = int(sys.argv[4]) if len(sys.argv) > 4 else SIGNAL

    df = load_close(code)
    trades, strat_ret, hold_ret, golden, death = simulate(df, fast, slow, signal)

    name = df.attrs.get("name") or ""
    symbol = df.attrs.get("code") or code
    print(f"{symbol} {name}  MACD({fast},{slow},{signal})")
    print("规则：金叉按收盘满仓买入，死叉按收盘全部卖出。空仓期间资金不变。\n")
    print(f"{'买入':<12}{'卖出':<12}{'买价':>8}{'卖价':>8}{'天数':>6}{'收益':>8}")
    closed = 0
    for t in trades:
        mark = "  未卖" if t["open"] else ""
        print(
            f"{t['buy']:%Y-%m-%d}  {t['sell']:%Y-%m-%d}  "
            f"{t['buy_px']:8.2f}{t['sell_px']:8.2f}{t['days']:6d}{t['ret']:8.2%}{mark}"
        )
        if not t["open"]:
            closed += 1
    print(f"\n完成 {closed} 笔，期末仍持仓 {int(any(t['open'] for t in trades))} 笔")
    print(f"策略收益（复利，期初=1）: {strat_ret:8.2%}")
    print(f"一直持有（从第 {slow + signal} 根收盘买到最后）: {hold_ret:8.2%}")

    png = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{code}_trades.png")
    save_plot(df, golden, death, png, f"{name} {symbol}  金叉买入 / 死叉卖出")
    print(f"\n已保存: {png}")
    print("\n用法: python3 trade.py sh600000")
