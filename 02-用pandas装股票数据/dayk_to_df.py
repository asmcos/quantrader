#!/usr/bin/env python3
"""
示例 1：把 01 的日K数据装进 pandas DataFrame。

01 的 day_k_qq.get_dayk(code) 返回:
  {"data": {"code", "name", "prePrice",
            "dayks": [{"day","open","close","high","low","volume","rise",...}, ...]}}

本示例做三件事:
  1. dict -> DataFrame
  2. 类型转换 / 索引 / 排序
  3. 落地 csv + parquet
"""
import os
import sys

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pandas as pd

sys.path.insert(0, os.path.join(ROOT, "01-股票的数据获取"))
import day_k_qq


def to_dataframe(code="sz002129"):
    raw = day_k_qq.get_dayk(code)
    if not raw:
        raise RuntimeError(f"获取失败: {code}")

    d = raw["data"]
    df = pd.DataFrame(d["dayks"])

    df["day"] = pd.to_datetime(df["day"])
    df = df.set_index("day").sort_index()

    num_cols = ["open", "close", "high", "low", "volume", "rise"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df.attrs["code"] = d.get("code", code)
    df.attrs["name"] = d.get("name", "")
    return df


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    df = to_dataframe(code)

    print(f"{df.attrs['code']} {df.attrs['name']}  形状={df.shape}")
    print(df.head(3))
    print("...")
    print(df.tail(3))
    print("\ndtypes:")
    print(df.dtypes)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, f"{code}_dayk.csv")
    df.to_csv(csv_path)
    print(f"\n已保存: {csv_path}")

    try:
        pq_path = os.path.join(out_dir, f"{code}_dayk.parquet")
        df.to_parquet(pq_path)
        print(f"已保存: {pq_path}")
    except Exception as e:
        print(f"parquet 跳过（需 pyarrow）: {e}")

    print("\n用法: python3 dayk_to_df.py sh600000")
