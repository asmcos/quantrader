#!/usr/bin/env python3
"""
日 K 线 — 通达信协议 eltdx（前复权）。

依赖: pip3 install eltdx
"""
import sys

try:
    from eltdx import TdxClient
except ImportError:
    print("请先安装: pip3 install eltdx")
    sys.exit(1)


def get_dayk(code, count=30, adjust="qfq"):
    """
    :param code: 如 sz000001 / sh600000
    :return: [{"day","open","close","high","low","volume"}, ...]
    """
    code = code.replace(".", "").lower()
    with TdxClient(timeout=10) as client:
        series = client.get_kline("day", code, count=count, adjust=adjust)
    rows = []
    for bar in series.bars:
        day = bar.time.strftime("%Y-%m-%d") if bar.time else ""
        rows.append({
            "day": day,
            "open": bar.open,
            "close": bar.close,
            "high": bar.high,
            "low": bar.low,
            "volume": bar.volume_lots,
        })
    return rows


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "sz000001"
    rows = get_dayk(code, count=5)
    print(f"{code} 日K（eltdx 前复权）共 {len(rows)} 根\n")
    for r in rows:
        print(f"  {r['day']} O:{r['open']} C:{r['close']} H:{r['high']} L:{r['low']}")
    print("\n用法: python3 day_k_eltdx.py sh600000")
