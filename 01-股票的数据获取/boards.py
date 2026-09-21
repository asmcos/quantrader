#!/usr/bin/env python3
"""
获取 A 股行业板块涨跌榜（东方财富公开接口）。

旧仓库里类似能力见：bs_get_industry_check.py、tdxhy.py
本文件不依赖 baostock / 通达信，只要 requests 即可运行。
"""
import os
import requests

# 部分环境的系统代理会导致行情请求失败
for _k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    ),
    "Referer": "https://quote.eastmoney.com/",
}


def get_industry_boards(top_n=20):
    """
    返回行业板块列表，按涨跌幅降序。

    每项: {code, name, price, rise, up_count, down_count}
    """
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": top_n,
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": "f3",
        "fs": "m:90+t:2",  # 行业板块
        "fields": "f12,f14,f2,f3,f104,f105",
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=(5, 20))
    resp.raise_for_status()
    data = resp.json().get("data") or {}
    rows = data.get("diff") or []

    results = []
    for row in rows:
        results.append({
            "code": row.get("f12", ""),
            "name": row.get("f14", ""),
            "price": row.get("f2", 0),
            "rise": row.get("f3", 0),
            "up_count": row.get("f104", 0),
            "down_count": row.get("f105", 0),
        })
    return results


if __name__ == "__main__":
    boards = get_industry_boards(15)
    print(f"行业板块 Top {len(boards)}（按涨跌幅）\n")
    print(f"{'代码':<10}{'名称':<16}{'最新':>10}{'涨跌%':>8}{'上涨':>6}{'下跌':>6}")
    print("-" * 60)
    for b in boards:
        print(
            f"{b['code']:<10}{b['name']:<16}"
            f"{b['price']:>10}{b['rise']:>8}{b['up_count']:>6}{b['down_count']:>6}"
        )
