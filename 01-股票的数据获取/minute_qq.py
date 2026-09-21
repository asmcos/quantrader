#!/usr/bin/env python3
"""
获取股票当日分时线（腾讯接口）。

使用仓库根目录修复版 2_hk_qq.get_minute_data
（已修正 high/low 字段；旧 hk_qq.py 有 high < low 的问题）。
"""
import os
import sys
from importlib import import_module

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

qq = import_module("2_hk_qq")


def get_minute(code):
    """返回分时字典，失败返回 None。"""
    return qq.get_minute_data(code)


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz300199"
    data = get_minute(code)
    if not data:
        print(f"获取失败: {code}")
        sys.exit(1)

    print(f"代码: {data['code']}  名称: {data['name']}  日期: {data['date']}")
    print(
        f"现价: {data['current_price']}  昨收: {data['prev_close']}  "
        f"开盘: {data['open']}"
    )
    print(f"最高: {data['high']}  最低: {data['low']}  成交量: {data['volume']}")
    print(f"分时条数: {len(data['trends'])}")

    ok = data["high"] >= data["low"]
    print(f"high/low 检查: {'通过' if ok else '异常'}\n")

    print("前 3 条:")
    for item in data["trends"][:3]:
        print(
            f"  {item['time']} open:{item['open']} close:{item['close']} "
            f"vol:{item['volume']}"
        )
    print("末 3 条:")
    for item in data["trends"][-3:]:
        print(
            f"  {item['time']} open:{item['open']} close:{item['close']} "
            f"vol:{item['volume']}"
        )

    print("\n用法: python3 minute_qq.py hk00700")
