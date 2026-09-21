#!/usr/bin/env python3
"""
获取股票日 K 线（腾讯接口，前复权）。

优先使用仓库根目录的修复版 2_hk_qq.get_dayk；
对应旧文件：hk_qq.py
"""
import os
import sys
from importlib import import_module

for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

# 保证能 import 仓库根目录模块
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

qq = import_module("2_hk_qq")


def get_dayk(code):
    """返回与 hk_eastmoney / 2_hk_qq 兼容的日K字典，失败返回 None。"""
    return qq.get_dayk(code)


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz002129"
    data = get_dayk(code)
    if not data:
        print(f"获取失败: {code}")
        sys.exit(1)

    d = data["data"]
    dayks = d["dayks"]
    print(f"代码: {d['code']}  名称: {d['name']}  昨收: {d['prePrice']}")
    print(f"日K条数: {len(dayks)}\n")
    print("最早 3 根:")
    for bar in dayks[:3]:
        print(f"  {bar['day']} O:{bar['open']} C:{bar['close']} rise:{bar['rise']}%")
    print("最近 3 根:")
    for bar in dayks[-3:]:
        print(f"  {bar['day']} O:{bar['open']} C:{bar['close']} rise:{bar['rise']}%")

    print("\n用法: python3 day_k_qq.py sh600000")
