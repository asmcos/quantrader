#!/usr/bin/env python3
"""
日 K 线 — 经典 pytdx（通达信行情站）。

依赖: pip3 install pytdx
说明: 行情 IP 经常失效，脚本会尝试多个主机；仍失败请用 day_k_eltdx.py 或 day_k_qq.py。
根目录旧代码 tdxhy.py / tdx.py 也是基于 pytdx。
"""
import sys

try:
    from pytdx.hq import TdxHq_API
except ImportError:
    print("请先安装: pip3 install pytdx")
    sys.exit(1)

# 常见公开行情站（不保证长期可用）
HOSTS = [
    ("116.205.183.150", 7709),
    ("116.205.171.132", 7709),
    ("111.230.186.52", 7709),
    ("119.147.212.81", 7709),
]


def _market_code(code):
    code = code.replace(".", "").lower()
    if code.startswith("sh"):
        return 1, code[2:]
    if code.startswith("sz"):
        return 0, code[2:]
    # 纯数字：6 开头沪市
    if code.startswith("6"):
        return 1, code
    return 0, code


def get_dayk(code, count=30):
    market, symbol = _market_code(code)
    api = TdxHq_API()
    last_err = None
    for host, port in HOSTS:
        try:
            if not api.connect(host, port, time_out=3):
                continue
            # category 9 = 日K
            bars = api.get_security_bars(9, market, symbol, 0, count)
            api.disconnect()
            if not bars:
                last_err = RuntimeError(f"{host} 返回空")
                continue
            rows = []
            for b in bars:
                rows.append({
                    "day": str(b.get("datetime", ""))[:10],
                    "open": b.get("open"),
                    "close": b.get("close"),
                    "high": b.get("high"),
                    "low": b.get("low"),
                    "volume": b.get("vol"),
                })
            return rows
        except Exception as e:
            last_err = e
            try:
                api.disconnect()
            except Exception:
                pass
    raise RuntimeError(f"pytdx 连接失败: {last_err}")


if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "000001"
    try:
        rows = get_dayk(code, count=5)
    except Exception as e:
        print(e)
        print("建议改用: python3 day_k_eltdx.py sz000001")
        sys.exit(1)
    print(f"{code} 日K（pytdx）共 {len(rows)} 根\n")
    for r in rows:
        print(f"  {r['day']} O:{r['open']} C:{r['close']} H:{r['high']} L:{r['low']}")
    print("\n用法: python3 day_k_pytdx.py sz000001")
