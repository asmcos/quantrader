"""
hk_qq 修复版 — 不修改原 hk_qq.py，在此文件中提供修正后的接口。

主要修复见 2_说明_hk_qq.md
"""
import re
import json
import random
import requests

# 复用原文件中未出问题的工具函数
from hk_qq import (
    remake_code,
    remake_codelist,
    remake_result,
    search,
    qqlist,
    _qq_market_meta,
    get_dayk as _get_dayk_orig,
)

_DEFAULT_TIMEOUT = (5, 30)


def get_minute_data(code):
    """
    获取股票分时线数据（支持 A股、港股）

    修复原 hk_qq.get_minute_data 中 high/low 字段取错 qt 数组下标的问题：
      - 原代码 high=info_list[9]  实为当前价
      - 原代码 low=info_list[33]   实为当日最高价
      - 正确应为 high=info_list[33], low=info_list[34]
    """
    code = remake_code(code)

    url = "https://web.ifzq.gtimg.cn/appstock/app/minute/query"
    params = {
        "_var": f"min_data_{code}",
        "code": code,
        "r": random.random(),
    }

    try:
        resp = requests.get(url, params=params, timeout=_DEFAULT_TIMEOUT)
        resp.encoding = "utf-8"

        match = re.search(r"min_data_\w+\s*=\s*({.*?})\s*$", resp.text, re.DOTALL)
        if not match:
            return None

        data = json.loads(match.group(1))
        if data.get("code") != 0 or not data.get("data"):
            return None

        stock_data = data["data"].get(code)
        if not stock_data:
            return None

        qt_data = stock_data.get("qt", {})
        info_list = qt_data.get(code, [])

        minute_raw = stock_data.get("data", {}).get("data", [])
        date_str = stock_data.get("data", {}).get("date", "")

        prev_close = float(info_list[4]) if len(info_list) > 4 else 0
        day_open = float(info_list[5]) if len(info_list) > 5 else prev_close

        minute_list = []
        last_open = prev_close or day_open
        lastvolume = 0

        for item in minute_raw:
            parts = item.split(" ")
            if len(parts) < 4:
                continue

            time = parts[0]
            price = float(parts[1])
            volume = float(parts[2]) - lastvolume
            amount = float(parts[3])

            minute_list.append({
                "time": time,
                "open": last_open,
                "close": price,
                "high": price,
                "low": price,
                "volume": volume,
                "amount": amount,
            })
            last_open = price
            lastvolume = float(parts[2])

        return {
            "code": code,
            "name": info_list[1] if len(info_list) > 1 else "",
            "date": date_str,
            "current_price": float(info_list[3]) if len(info_list) > 3 else 0,
            "prev_close": prev_close,
            "open": day_open,
            "volume": float(info_list[6]) if len(info_list) > 6 else 0,
            # 修复：33=当日最高, 34=当日最低（原代码误用 9 和 33）
            "high": float(info_list[33]) if len(info_list) > 33 and info_list[33] else 0,
            "low": float(info_list[34]) if len(info_list) > 34 and info_list[34] else 0,
            "trends": minute_list,
        }

    except Exception as e:
        print(f"获取分时线数据失败: {e}")
        return None


def get_dayk(code):
    """
    获取日K线，修复首根 K 线涨跌幅未使用昨收价 (prePrice) 的问题。
  原代码首根 K 用 (收盘-开盘)/开盘，与行情软件显示的涨跌幅不一致。
    """
    code = remake_code(code)
    url = (
        "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get"
        "?_var=kline_dayqfq&param=%s,day,,,320,qfq&r=%s" % (code, random.random())
    )
    try:
        resp = requests.get(url, timeout=_DEFAULT_TIMEOUT)
        resp.encoding = "utf-8"
        match = re.search(r"kline_dayqfq\s*=\s*({.*})\s*$", resp.text, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group(1))
        if data.get("code") != 0 or not data.get("data"):
            return None
        stock_data = data["data"].get(code)
        if not stock_data:
            return None
        raw_bars = stock_data.get("qfqday") or stock_data.get("day")
        if not raw_bars:
            return None
        qt_data = stock_data.get("qt", {})
        info_list = qt_data.get(code, [])
        market, stock_code, decimal = _qq_market_meta(code)
        pre_price = float(stock_data.get("prec") or 0)
        dayks = []
        prev_close = pre_price or None
        for item in raw_bars:
            if len(item) < 6:
                continue
            open_p = float(item[1])
            close_p = float(item[2])
            if prev_close:
                rise = (close_p - prev_close) / prev_close * 100
            elif open_p:
                rise = (close_p - open_p) / open_p * 100
            else:
                rise = 0
            vol = float(item[5]) if item[5] else 0
            dayks.append({
                "day": item[0],
                "open": item[1],
                "close": item[2],
                "high": item[3],
                "low": item[4],
                "volume": str(int(vol)) if vol == int(vol) else str(vol),
                "rise": f"{rise:.2f}",
            })
            prev_close = close_p
        return {
            "rc": 0,
            "rt": 0,
            "data": {
                "code": stock_code,
                "market": market,
                "name": info_list[1] if len(info_list) > 1 else "",
                "decimal": decimal,
                "prePrice": pre_price,
                "dayks": dayks,
            },
        }
    except Exception as e:
        print(f"获取日K数据失败: {e}")
        return None


if __name__ == "__main__":
    print("=== 2_hk_qq 修复版测试 ===\n")

    for label, code in [("A股", "sz300199"), ("港股", "hk00700"), ("沪市", "sh600000")]:
        orig = __import__("hk_qq").get_minute_data(code)
        fixed = get_minute_data(code)
        if orig and fixed:
            ok = fixed["high"] >= fixed["low"]
            print(f"[{label} {code}] high={fixed['high']} low={fixed['low']} "
                  f"(原: high={orig['high']} low={orig['low']}) {'✓' if ok else '✗'}")

    print("\n--- 日K首根涨跌幅 ---")
    orig_d = __import__("hk_qq").get_dayk("sz002129")
    fixed_d = get_dayk("sz002129")
    if orig_d and fixed_d:
        o = orig_d["data"]["dayks"][0]
        f = fixed_d["data"]["dayks"][0]
        print(f"原: {o['day']} rise={o['rise']}%")
        print(f"新: {f['day']} rise={f['rise']}% (使用昨收 {fixed_d['data']['prePrice']})")
