#!/usr/bin/env python3
"""
把分时数据装进 pandas：01 的 minute_qq 原始 dict -> DataFrame。

用法:
    python3 minute_to_df.py hk00700
    python3 minute_to_df.py sz002129 --csv
"""
import os
import sys
from importlib import import_module

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pandas as pd


def _load_minute():
    sys.path.insert(0, os.path.join(ROOT, "01-股票的数据获取"))
    return import_module("minute_qq")


def _trade_day(data):
    """01 的 date 形如 20260923，转成 2026-09-23。"""
    day = str(data.get("date") or "")
    if len(day) == 8 and day.isdigit():
        return f"{day[:4]}-{day[4:6]}-{day[6:]}"
    return ""


def to_df(data):
    """分时 dict -> DataFrame。time 用当日日期，amount 保留接口里的累计成交额。"""
    df = pd.DataFrame(data["trends"])
    clock = df["time"].astype(str).str.replace(r"^(\d{2})(\d{2})$", r"\1:\2", regex=True)
    day = _trade_day(data)
    if day:
        df["time"] = pd.to_datetime(day + " " + clock, format="%Y-%m-%d %H:%M", errors="coerce")
    else:
        df["time"] = pd.to_datetime(clock, format="%H:%M", errors="coerce")
    df = df.set_index("time").sort_index()
    return df


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    code = args[0] if args else "hk00700"
    save = "--csv" in sys.argv

    data = _load_minute().get_minute(code)
    if not data:
        print(f"获取失败: {code}")
        sys.exit(1)

    df = to_df(data)
    print(f"代码: {code}  开盘: {data['open']}  最高: {data['high']}  最低: {data['low']}")
    print(f"分时行数: {len(df)}\n")
    print(df.head(3))
    print("...")
    print(df.tail(3))

    print(f"\n当日累计成交量: {df['volume'].sum():.0f}")
    print(f"最高价出现时间: {df['close'].idxmax().strftime('%H:%M')}")
    print(f"最低价出现时间: {df['close'].idxmin().strftime('%H:%M')}")

    if save:
        name = f"minute_{code}.csv"
        df.to_csv(name, encoding="utf-8-sig")
        print(f"\n已保存: {name}")
