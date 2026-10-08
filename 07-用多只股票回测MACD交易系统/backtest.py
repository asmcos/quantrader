#!/usr/bin/env python3
"""
用多只股票回测 06 的 MACD 买卖。

规则不变：金叉按收盘满仓买入，死叉按收盘全部卖出。
股票从全市场列表里按代码均匀抽取，不只用第一页（那一页几乎都是科创板）。

用法:
    python3 backtest.py
    python3 backtest.py 10
"""
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "01-股票的数据获取"))
sys.path.insert(0, os.path.join(ROOT, "03-均线和MACD"))
sys.path.insert(0, os.path.join(ROOT, "06-用MACD指标做简单交易系统"))

import stock_list
from ma import load_close
from trade import simulate

PAGE = 100


def sample_stocks(n):
    """按代码排序后的位置均匀取 n 只。同一页只请求一次。"""
    first = stock_list._fetch_page(1, 1)
    total = int(first.get("total") or 0)
    if total <= 0:
        raise RuntimeError("股票列表为空")
    n = min(n, total)
    indexes = [int(i * total / n) for i in range(n)]
    pages = {}
    picked = []
    for idx in indexes:
        page = idx // PAGE + 1
        if page not in pages:
            pages[page] = stock_list._parse_rows(stock_list._fetch_page(page, PAGE))
            time.sleep(0.15)
        offset = idx % PAGE
        rows = pages[page]
        if offset < len(rows):
            picked.append(rows[offset])
    return picked, total


def run_one(code):
    df = load_close(code)
    trades, strat_ret, hold_ret, _, _ = simulate(df)
    closed = sum(1 for t in trades if not t["open"])
    return {
        "code": df.attrs.get("code") or code,
        "name": df.attrs.get("name") or "",
        "trades": closed,
        "strat": strat_ret,
        "hold": hold_ret,
        "better": strat_ret > hold_ret,
    }


def save_plot(df, png_path):
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "AR PL UKai CN", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(12, 5))
    x = range(len(df))
    width = 0.38
    ax.bar([i - width / 2 for i in x], df["strat"] * 100, width, label="MACD 买卖", color="#2980b9")
    ax.bar([i + width / 2 for i in x], df["hold"] * 100, width, label="一直持有", color="#e67e22")
    ax.axhline(0, color="#888888", linewidth=0.6)
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["code"].tolist(), rotation=45, ha="right")
    ax.set_ylabel("收益 %")
    ax.set_title("同一套 MACD(12,26,9) 在多只股票上的回测")
    ax.legend(frameon=False)
    fig.savefig(png_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    stocks, total = sample_stocks(n)
    print(f"全市场约 {total} 只，均匀抽取 {len(stocks)} 只")
    print("规则与 06 相同：金叉买入，死叉卖出，参数 12,26,9\n")

    rows = []
    for s in stocks:
        code = s["code"]
        try:
            row = run_one(code)
            rows.append(row)
            print(f"{row['code']:<10}{row['name']:<8}  完成{row['trades']:2d}笔  "
                  f"策略{row['strat']:8.2%}  持有{row['hold']:8.2%}")
        except Exception as e:
            print(f"{code}  跳过: {e}")
        time.sleep(0.15)

    if not rows:
        sys.exit("没有成功的回测")

    df = pd.DataFrame(rows)
    better = int(df["better"].sum())
    print(f"\n成功 {len(df)} 只，策略收益高于一直持有的有 {better} 只")
    print(f"策略收益平均 {df['strat'].mean():.2%}，中位数 {df['strat'].median():.2%}")
    print(f"一直持有平均 {df['hold'].mean():.2%}，中位数 {df['hold'].median():.2%}")

    out = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(out, "backtest.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    png_path = os.path.join(out, "backtest.png")
    save_plot(df, png_path)
    print(f"\n已保存: {csv_path}")
    print(f"已保存: {png_path}")
    print("\n用法: python3 backtest.py 10")
