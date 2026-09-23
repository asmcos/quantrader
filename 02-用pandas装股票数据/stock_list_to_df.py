#!/usr/bin/env python3
"""
示例 3：股票列表 -> DataFrame，并做筛选。

01 的 stock_list.get_stock_list() 返回 (list[dict], total)，
dict 形如 {"code": "sz000001", "name": "平安银行"}。

用法:
    python3 stock_list_to_df.py           # 预览第一页
    python3 stock_list_to_df.py --all     # 全部
    python3 stock_list_to_df.py --all --filter 银行
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


def _load_stock_list():
    sys.path.insert(0, os.path.join(ROOT, "01-股票的数据获取"))
    return import_module("stock_list")


def to_df(stocks):
    """股票列表 dict -> DataFrame，加交易所/板块列。"""
    df = pd.DataFrame(stocks)
    df["market"] = df["code"].str[:2].map({"sh": "沪", "sz": "深", "hk": "港"})
    df["num"] = df["code"].str[2:]
    return df


if __name__ == "__main__":
    show_all = "--all" in sys.argv
    kw = None
    if "--filter" in sys.argv:
        i = sys.argv.index("--filter")
        if i + 1 < len(sys.argv):
            kw = sys.argv[i + 1]

    mod = _load_stock_list()
    if show_all:
        stocks, total = mod.get_stock_list()
    else:
        stocks, total = mod.get_stock_list(page_size=20, max_pages=1)

    df = to_df(stocks)
    print(f"DataFrame 形状={df.shape}  全市场约 {total} 只")
    print(df.head(5))

    if kw:
        hit = df[df["name"].str.contains(kw, na=False)]
        print(f"\n名称含 {kw!r} 的有 {len(hit)} 只:")
        print(hit[["code", "name"]].head(20))

    print("\n沪市数量:", (df["market"] == "沪").sum())
    print("深市数量:", (df["market"] == "深").sum())

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "stock_list.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"已保存: {csv_path}")
