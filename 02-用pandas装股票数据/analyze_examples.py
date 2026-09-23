#!/usr/bin/env python3
"""
pandas 分析技巧合集：基于 01 抓取的日K/分时数据。

每个函数都是一个可独立阅读的小例子，main 里按顺序跑。
用法: python3 analyze_examples.py
"""
import os
import sys
from importlib import import_module

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "01-股票的数据获取"))

import pandas as pd

import day_k_qq
import minute_qq
import stock_list

CODES = ["sz002129", "sh600000", "hk00700"]


def to_df(code):
    raw = day_k_qq.get_dayk(code)
    if not raw:
        return None
    d = raw["data"]
    df = pd.DataFrame(d["dayks"])
    df["day"] = pd.to_datetime(df["day"])
    df = df.set_index("day").sort_index()
    for c in ["open", "close", "high", "low", "volume", "rise"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df.attrs["code"] = d.get("code", code)
    df.attrs["name"] = d.get("name", "")
    return df


def ex1_rolling(df):
    """rolling 均线 + 乖离率。"""
    out = df.copy()
    for n in (5, 10, 20, 60):
        out[f"ma{n}"] = out["close"].rolling(n).mean()
    out["bias20"] = (out["close"] - out["ma20"]) / out["ma20"] * 100
    print(out[["close", "ma5", "ma20", "bias20"]].tail(5))


def ex2_returns(df):
    """收益率、波动率、最大回撤。"""
    r = df["close"].pct_change().dropna()
    cum = (1 + r).cumprod()
    dd = (cum / cum.cummax() - 1).min()
    print(f"日均收益 {r.mean():.4%}  日波动 {r.std():.4%}  年化波动 {r.std()*252**0.5:.2%}")
    print(f"最大回撤 {dd:.2%}")
    print("月收益(%):")
    print((df["close"].resample("ME").last().pct_change() * 100).dropna().tail(6))


def ex3_multi(codes):
    """多股票合并成一张宽表，比较相关性与累计涨幅。"""
    frames = {}
    for c in codes:
        d = to_df(c)
        if d is not None:
            frames[c] = d["close"]
    if len(frames) < 2:
        print("可用数据不足")
        return
    wide = pd.DataFrame(frames).sort_index()
    print(wide.tail(3))
    print("\n相关性:")
    print(wide.pct_change(fill_method=None).corr().round(3))
    print("\n区间累计涨幅(%):")
    # 三只股票交易日不完全重合，用各自第一根/最后一根有效收盘，避免 iloc[0] 落在空值上
    first = wide.apply(lambda s: s.dropna().iloc[0])
    last = wide.apply(lambda s: s.dropna().iloc[-1])
    print(((last / first - 1) * 100).round(2))


def ex4_groupby():
    """按星期几分组统计涨跌。"""
    d = to_df("sh600000")
    d = d.assign(dow=d.index.dayofweek)
    g = d.groupby("dow")["rise"].agg(["count", "mean", "std"])
    g.index = ["周一", "周二", "周三", "周四", "周五"][: len(g)]
    print(g.round(3))


def ex5_minute():
    """分时重采样成 30 分钟。"""
    from minute_to_df import to_df as minute_to_df

    data = minute_qq.get_minute("hk00700")
    if not data:
        print("分时获取失败")
        return
    df = minute_to_df(data)
    res = df.resample("30min").agg({"open": "first", "close": "last", "volume": "sum"})
    print(res.dropna())


def ex6_screen():
    """股票列表 -> DataFrame -> 按名称筛选。"""
    stocks, total = stock_list.get_stock_list(page_size=100, max_pages=1)
    df = pd.DataFrame(stocks)
    print(f"共 {len(df)} 条（全市场约 {total}）")
    # 第一页按代码从大到小，多是科创板，筛「银行」会是空表
    hit = df[df["name"].str.contains("科技", na=False)]
    print(hit.head(10))
    print("（名称含「银行」的股票不在这一页，要全市场再筛请用 stock_list_to_df.py --all --filter 银行）")


if __name__ == "__main__":
    base = to_df("sz002129")
    print("=== 1 rolling 均线 ===")
    ex1_rolling(base)
    print("\n=== 2 收益/波动/回撤 ===")
    ex2_returns(base)
    print("\n=== 3 多股票合并 ===")
    ex3_multi(CODES)
    print("\n=== 4 groupby 星期几 ===")
    ex4_groupby()
    print("\n=== 5 分时重采样 ===")
    ex5_minute()
    print("\n=== 6 股票列表筛选 ===")
    ex6_screen()
