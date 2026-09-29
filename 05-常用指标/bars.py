#!/usr/bin/env python3
"""日 K 的开高低收，供本课各指标使用。"""
import os
import sys

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "01-股票的数据获取"))

import day_k_qq
import pandas as pd


def sma_cn(series, n, m=1):
    """
    通达信 SMA(X, N, M)，不是简单移动平均。

        Y = (M * X + (N - M) * Y_昨天) / N

    M=1 时，今天权重是 1/N，昨天的平滑值占 (N-1)/N。
    RSI、KDJ 用的都是这一种。
    """
    return series.ewm(alpha=m / n, adjust=False).mean()


def load_bars(code):
    raw = day_k_qq.get_dayk(code)
    if not raw:
        raise RuntimeError(f"获取失败: {code}")
    d = raw["data"]
    df = pd.DataFrame(d["dayks"])
    df["day"] = pd.to_datetime(df["day"])
    df = df.set_index("day").sort_index()
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.attrs["code"] = d.get("code", code)
    df.attrs["name"] = d.get("name", "")
    return df
