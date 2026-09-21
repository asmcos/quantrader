#!/usr/bin/env python3
"""
获取 A 股股票列表（代码 + 名称）。

旧仓库里类似能力见：bs_get_industry_check.py、common/framework.py 的股票列表。
本文件不依赖 baostock，只要 requests 即可运行。
"""
import os
import sys
import time
import requests

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

# f13: 0=深市, 1=沪市
_MARKET_PREFIX = {0: "sz", 1: "sh"}


def _fetch_page(page, page_size, retries=5):
    hosts = (
        "https://push2.eastmoney.com/api/qt/clist/get",
        "https://82.push2.eastmoney.com/api/qt/clist/get",
    )
    params = {
        "pn": page,
        "pz": page_size,
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fid": "f12",
        # 深市主板/创业板 + 沪市主板/科创板
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f13,f14",
    }
    last_err = None
    for attempt in range(retries):
        url = hosts[attempt % len(hosts)]
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=(5, 20))
            resp.raise_for_status()
            return resp.json().get("data") or {}
        except Exception as e:
            last_err = e
            time.sleep(0.8 * (attempt + 1))
    raise last_err


def _parse_rows(data):
    rows = data.get("diff") or []
    # 东方财富有时返回 dict 而不是 list
    if isinstance(rows, dict):
        rows = list(rows.values())

    results = []
    for row in rows:
        symbol = str(row.get("f12", ""))
        market = _MARKET_PREFIX.get(row.get("f13"), "sz")
        name = row.get("f14", "")
        results.append({
            "code": f"{market}{symbol}",
            "symbol": symbol,
            "name": name,
        })
    return results


def get_stock_list(page_size=100, max_pages=None):
    """
    分页拉取沪深 A 股列表。

    :param page_size: 每页条数
    :param max_pages: 最多拉取页数；None 表示拉全量
    :return: [{"code": "sh600000", "name": "浦发银行", "symbol": "600000"}, ...]
    """
    results = []
    page = 1
    total = None

    while True:
        data = _fetch_page(page, page_size)
        if total is None:
            total = int(data.get("total") or 0)
        batch = _parse_rows(data)
        if not batch:
            break
        results.extend(batch)

        if max_pages is not None and page >= max_pages:
            break
        if total and page * page_size >= total:
            break
        page += 1
        time.sleep(0.2)

    return results, total if total is not None else len(results)


if __name__ == "__main__":
    show_all = "--all" in sys.argv

    if show_all:
        stocks, total = get_stock_list()
    else:
        stocks, total = get_stock_list(page_size=20, max_pages=1)

    print(f"本页/已取 {len(stocks)} 只，全市场约 {total} 只\n")
    print(f"{'代码':<12}{'名称'}")
    print("-" * 28)
    for s in stocks:
        print(f"{s['code']:<12}{s['name']}")

    if not show_all:
        print(f"\n... 还有约 {max(total - len(stocks), 0)} 只")
        print("用法: python3 stock_list.py          # 预览第一页")
        print("      python3 stock_list.py --all   # 打印全部")
