#!/usr/bin/env python3
"""
当日分时 — 通达信协议 eltdx。

依赖: pip3 install eltdx
"""
import sys

try:
    from eltdx import TdxClient
except ImportError:
    print("请先安装: pip3 install eltdx")
    sys.exit(1)


def get_minute(code):
    """
    :param code: 如 sz000001
    :return: dict(code, date, prev_close, open, points=[...])
    """
    code = code.replace(".", "").lower()
    with TdxClient(timeout=10) as client:
        series = client.get_minute(code)
    points = []
    for p in series.points:
        points.append({
            "time": p.time_label,
            "price": p.price,
            "avg_price": p.avg_price,
            "volume": p.volume,
        })
    return {
        "code": code,
        "date": str(series.trading_date) if series.trading_date else "",
        "prev_close": series.prev_close,
        "open": series.open_price,
        "points": points,
    }


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz000001"
    data = get_minute(code)
    print(f"代码: {data['code']}  日期: {data['date']}")
    print(f"昨收: {data['prev_close']}  开盘: {data['open']}")
    print(f"分时点数: {len(data['points'])}")
    print("前 3 条:")
    for p in data["points"][:3]:
        print(f"  {p['time']} price:{p['price']} vol:{p['volume']}")
    print("\n用法: python3 minute_eltdx.py sh600000")
