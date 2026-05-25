import requests
import re
import json
import random

def remake_code(code):
    code = code.lower()
    code = code.replace(".","")
    return code

def remake_codelist(codelist):
    if isinstance(codelist,str):
        codelist = codelist.split(",")

    return [remake_code(c) for c in codelist]

def remake_result(data):
    pattern = r'v_s_([a-z]{2}\d+)="\d+~([^~]+)~\d+~([\d.]+)~[-\d.]+~([-\d.]+)~'

    matches = re.findall(pattern, data)

    results = []
    for match in matches:
        code = match[0]
        name = match[1]
        price = match[2]
        rise  = match[3]
        results.append([code,name,price,rise])
    return results

def search(keyword):
    url = "https://proxy.finance.qq.com/cgi/cgi-bin/smartbox/search?stockFlag=1&fundFlag=1&app=official_website&c=1&query=" + keyword
    resp = requests.get(url)
    results=[]
    data = resp.json()['stock'][:10]
    for d in data:
        results.append({"name":d['name'],"code":d['code']})
    return results

def qqlist(codelist):
    codelist = remake_codelist(codelist)
    url = "https://qt.gtimg.cn/?q=s_" + ",s_".join(codelist)
    
    resp = requests.get(url)
    result = remake_result(resp.text)
    return result

# https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_dayqfq&param=sz002129,day,,,320,qfq&r=0.48251696632573515
#
#
def _qq_market_meta(code):
    if code.startswith('sh'):
        return 1, code[2:], 2
    if code.startswith('sz'):
        return 0, code[2:], 2
    if code.startswith('hk'):
        return 116, code[2:], 3
    return 0, code, 2

def get_dayk(code):
    """
    获取股票日K线数据（支持 A股、港股，A股为前复权 qfqday）

    :param code: 股票代码，格式如 sh600000, sz000001, hk00700
    :return: 与 hk_eastmoney.get_dayk 兼容的字典，data.dayks 为日K列表
    """
    code = remake_code(code)
    url = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?_var=kline_dayqfq&param=%s,day,,,320,qfq&r=%s" % (code, random.random())
    try:
        resp = requests.get(url)
        resp.encoding = 'utf-8'
        match = re.search(r'kline_dayqfq\s*=\s*({.*})\s*$', resp.text, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group(1))
        if data.get('code') != 0 or not data.get('data'):
            return None
        stock_data = data['data'].get(code)
        if not stock_data:
            return None
        raw_bars = stock_data.get('qfqday') or stock_data.get('day')
        if not raw_bars:
            return None
        qt_data = stock_data.get('qt', {})
        info_list = qt_data.get(code, [])
        market, stock_code, decimal = _qq_market_meta(code)
        pre_price = stock_data.get('prec') or 0
        dayks = []
        prev_close = None
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
                "name": info_list[1] if len(info_list) > 1 else '',
                "decimal": decimal,
                "prePrice": pre_price,
                "dayks": dayks,
            },
        }
    except Exception as e:
        print(f"获取日K数据失败: {e}")
        return None

def get_minute_data(code):
    """
    获取股票分时线数据（支持 A股、港股）
    
    :param code: 股票代码，格式如 sh600000, sz000001, hk00700
    :return: 完整的分时数据字典
    """
    code = remake_code(code)
    
    url = f"https://web.ifzq.gtimg.cn/appstock/app/minute/query"
    params = {
        "_var": f"min_data_{code}",
        "code": code,
        "r": random.random()
    }
    
    try:
        resp = requests.get(url, params=params)
        resp.encoding = 'utf-8'
        
        match = re.search(r'min_data_\w+\s*=\s*({.*?})\s*$', resp.text, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            
            if data.get('code') == 0 and data.get('data'):
                stock_data = data['data'].get(code)
                if stock_data:
                    # 解析基本信息 from qt array
                    qt_data = stock_data.get('qt', {})
                    info_list = qt_data.get(code, [])
                    
                    # 解析分时数据
                    minute_raw = stock_data.get('data', {}).get('data', [])
                    date_str = stock_data.get('data', {}).get('date', '')
                    
                    minute_list = []
                    open = 0;
                    lastvolume = 0 ;
                    for item in minute_raw:
                        parts = item.split(' ')
                       
                        if len(parts) >= 4:
                            time = parts[0]
                            price = float(parts[1])
                            volume = float(parts[2]) - lastvolume;
                            amount = float(parts[3])
                            
                            minute_list.append({
                                'time': time,
                                'open': open,
                                'close': price,
                                'high': price,
                                'low': price,
                                'volume': volume,
                                'amount': amount
                            })
                            open = price
                            lastvolume = float(parts[2]) ;
                    
                    # 构建返回结果
                    result = {
                        'code': code,
                        'name': info_list[1] if len(info_list) > 1 else '',
                        'date': date_str,
                        'current_price': float(info_list[3]) if len(info_list) > 3 else 0,
                        'prev_close': float(info_list[4]) if len(info_list) > 4 else 0,
                        'open': float(info_list[5]) if len(info_list) > 5 else 0,
                        'volume': float(info_list[6]) if len(info_list) > 6 else 0,
                        'high': float(info_list[9]) if len(info_list) > 9 else 0,
                        'low': float(info_list[33]) if len(info_list) > 33 else 0,
                        'trends': minute_list
                    }
                    
                    return result
        
        return None
    except Exception as e:
        print(f"获取分时线数据失败: {e}")
        return None

if __name__ == "__main__":
    print("=== 测试 A股分时 ===")
    data = get_minute_data("sz300199")
    if data:
        print(f"代码: {data['code']}")
        print(f"名字: {data['name']}")
        print(f"日期: {data['date']}")
        print(f"当前价: {data['current_price']}")
        print(f"昨收: {data['prev_close']}")
        print(f"开盘: {data['open']}")
        print(f"最高: {data['high']}")
        print(f"最低: {data['low']}")
        print(f"成交量: {data['volume']}")
        print(f"分时数据条数: {len(data['trends'])}")
        print("前3条分时:")
        for item in data['trends'][:3]:
            print(f"  时间: {item['time']}, open: {item['open']}, close: {item['close']}, high: {item['high']}, low: {item['low']}, volume: {item['volume']}")
    
    print("\n=== 测试港股分时 ===")
    data = get_minute_data("hk00700")
    if data:
        print(f"代码: {data['code']}")
        print(f"名字: {data['name']}")
        print(f"日期: {data['date']}")
        print(f"当前价: {data['current_price']}")
        print(f"昨收: {data['prev_close']}")
        print(f"开盘: {data['open']}")
        print(f"最高: {data['high']}")
        print(f"最低: {data['low']}")
        print(f"成交量: {data['volume']}")
        print(f"分时数据条数: {len(data['trends'])}")
        print("最后3条分时:")
        for item in data['trends'][-3:]:
            print(f"  时间: {item['time']}, open: {item['open']}, close: {item['close']}, high: {item['high']}, low: {item['low']}, volume: {item['volume']}")

    print("\n=== 测试深市日K ===")
    data = get_dayk("sz.002129")
    if data:
        d = data['data']
        print(f"代码: {d['code']}, 名字: {d['name']}, 昨收: {d['prePrice']}")
        print(f"日K条数: {len(d['dayks'])}")
        print("最早3根:")
        for bar in d['dayks'][:3]:
            print(f"  {bar['day']} O:{bar['open']} C:{bar['close']} rise:{bar['rise']}%")
        print("最近3根:")
        for bar in d['dayks'][-3:]:
            print(f"  {bar['day']} O:{bar['open']} C:{bar['close']} rise:{bar['rise']}%")

    print("\n=== 测试沪市日K ===")
    data = get_dayk("sh600000")
    if data:
        d = data['data']
        last = d['dayks'][-1]
        print(f"代码: {d['code']}, 名字: {d['name']}, 日K条数: {len(d['dayks'])}")
        print(f"最新: {last['day']} 收:{last['close']} 涨跌幅:{last['rise']}%")

    print("\n=== 测试港股日K ===")
    data = get_dayk("hk00700")
    if data:
        d = data['data']
        print(f"代码: {d['code']}, 名字: {d['name']}, 昨收: {d['prePrice']}")
        print(f"日K条数: {len(d['dayks'])}")
        print("最近3根:")
        for bar in d['dayks'][-3:]:
            print(f"  {bar['day']} O:{bar['open']} C:{bar['close']} rise:{bar['rise']}%")
