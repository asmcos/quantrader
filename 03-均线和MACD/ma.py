#!/usr/bin/env python3
"""
均线：简单移动平均 SMA，指数移动平均 EMA。

用法:
    python3 ma.py
    python3 ma.py sh600000
"""
import os
import sys

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "01-股票的数据获取"))

import day_k_qq
import pandas as pd

# 日线常用周期：5/10 看短线，20 近一个月，60 近一个季度
MA_PERIODS = (5, 10, 20, 60)


def load_close(code):
    raw = day_k_qq.get_dayk(code)
    if not raw:
        raise RuntimeError(f"获取失败: {code}")
    d = raw["data"]
    df = pd.DataFrame(d["dayks"])
    df["day"] = pd.to_datetime(df["day"])
    df = df.set_index("day").sort_index()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df.attrs["code"] = d.get("code", code)
    df.attrs["name"] = d.get("name", "")
    return df


def sma(series, n):
    """简单移动平均：最近 n 根收盘价的算术平均，每根权重相同。"""
    return series.rolling(n, min_periods=n).mean()


def ema(series, n):
    """
    指数移动平均，递推公式（通达信 / 同花顺同一写法）:

        α = 2 / (n + 1)
        EMA_今天 = α * 收盘_今天 + (1 - α) * EMA_昨天
        第一天没有昨天时，EMA = 当天收盘

    n 越小，α 越大，越贴近最新价格。
    """
    alpha = 2.0 / (n + 1)
    return series.ewm(alpha=alpha, adjust=False).mean()


def add_mas(df, periods=MA_PERIODS):
    out = df.copy()
    for n in periods:
        out[f"sma{n}"] = sma(out["close"], n)
        out[f"ema{n}"] = ema(out["close"], n)
    return out


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    df = add_mas(load_close(code))
    cols = ["close"] + [f"sma{n}" for n in MA_PERIODS] + [f"ema{n}" for n in MA_PERIODS]
    print(f"{df.attrs['code']} {df.attrs['name']}")
    print("SMA 要满 n 天才有值；EMA 从第一天就有值，但前 n 天还不稳定。\n")
    print(df[cols].tail(8).round(3))
    print("\n用法: python3 ma.py sh600000")
