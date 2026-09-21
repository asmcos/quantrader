#!/usr/bin/env python3
"""
股票列表（代码 + 名称）— 通达信协议 eltdx。

依赖: pip3 install eltdx
"""
import sys

try:
    from eltdx import TdxClient
except ImportError:
    print("请先安装: pip3 install eltdx")
    sys.exit(1)


def get_stock_list(limit=None):
    """返回 [{"code": "sz000001", "name": "平安银行"}, ...]"""
    results = []
    with TdxClient(timeout=10) as client:
        for exchange in (0, 1):  # 0=深, 1=沪
            for item in client.get_codes_all(exchange):
                if getattr(item, "category", "") != "a_share":
                    continue
                results.append({
                    "code": f"{item.exchange}{item.code}",
                    "symbol": item.code,
                    "name": item.name,
                })
                if limit and len(results) >= limit:
                    return results
    return results


if __name__ == "__main__":
    show_all = "--all" in sys.argv
    stocks = get_stock_list(limit=None if show_all else 20)
    print(f"{'代码':<12}{'名称'}")
    print("-" * 28)
    for s in stocks:
        print(f"{s['code']:<12}{s['name']}")
    if not show_all:
        print("\n用法: python3 stock_list_eltdx.py --all")
