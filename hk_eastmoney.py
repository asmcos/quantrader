import requests
import re
import json
import time

t = str(time.time())

def maket(mc):
    return {"1":"sh","0":"sz","116":"hk","128":"hk"}.get(str(mc))

def divisor1(mc):
    return {"1":100,"0":100,"116":1000,"128":1000}.get(str(mc))

def divisor(f1):
    return {2:100,3:1000}.get(f1,100)

def replace_market_code(code):
    code = code.lower()
    code = code.replace("sh", "1.").replace("sz", "0.").replace("hk", "116.").replace("..",".")
    return code

def replace_market_result(result):
    div = divisor(result['f1'])
    code  = maket(result['f13']) + result['f12']
    name  = result['f14'] 

    price = f"{result['f2'] / div:.2f}"
    rise = f"{result['f3'] / div:.2f}"

    return [code,name,price,rise]

def remake_code(codes):

    # 处理所有代码
    result = [replace_market_code(code) for code in codes]
    return result

def remake_result(codes):


    # 处理所有代码
    result = [replace_market_result(code) for code in codes]
    return result




def get_timeline(code):
    #code = "116.01822"
    #code = "0.300059"
    code = replace_market_code(code)
    url = "https://push2his.eastmoney.com/api/qt/stock/trends2/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58&ut=fa5fd1943c7b386f172d6893dbfba10b&iscr=0&ndays=1&secid=%s&_=%s26" % (code,t)

    resp = requests.get(url)
    return resp.text


def get_dayk(code):
    code = replace_market_code(code)

    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=20240101&end=20500101&ut=fa5fd1943c7b386f172d6893dbfba10b&rtntype=6&secid=%s&klt=101&fqt=1" %(code)

    try:
        resp = requests.get(url,timeout=(5, 30))
    except requests.exceptions.Timeout:
        return get_dayk(code)

    data_json = resp.json()
    dayks = []
    for i in data_json["data"]['klines']:
        d = i.split(",")
        dayks.append({"day":d[0],"open":d[1],"close":d[2],"high":d[3],
                    "low":d[4],"volume":d[5],"rise":d[8]})
    data_json["data"]["dayks"] = dayks
    del data_json['data']['klines']
    return data_json

def get_stock_price_bylist(codelist):
    #http://qt.gtimg.cn/r=0.8409869808238q=s_sz000559,s_sz000913,s_sz002048,s_sz002085,s_sz002126,s_sz002284,s_sz002434,s_sz002472,s_sz002488
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
   
    codelist = remake_code(codelist)
    params = {
     # 这里选择了一些常用字段，可根据需求调整
     "fields": "f12,f13,f14,f2,f3,f1",
     "secids": ",".join(codelist)
    }

    response = requests.get(url, params=params)
    try :
        ret = response.json()['data']['diff']
    except:
        ret = []

    return remake_result(ret)

def get_stock_code_market(page=1,market=1):
    # market 1 上证券
    # 0 深圳 m:0+t:6,m:0+t:80
    # 128 港股通票 m:128+t:3,m:128+t:4
    # 116 普通港股票 m:116+t:3,m:116+t:4
    if market == 1:
        fs = "m:1+t:2,m:1+t:23"
    if market == 0:
        fs = "m:0+t:6,m:0+t:80"
    if market == 128:
        fs = "m:128+t:3,m:128+t:4"
    if market == 116:
        fs = "m:116+t:3,m:116+t:4"

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "np": 1,
        "fltt": 1,
        "invt": 2,
        "fs": fs,
        "fields": "f12,f13,f14,f1,f2,f4,f3,f152,f5,f6,f7,f15,f18,f16,f17,f10,f8,f9,f23",
        "fid": "f12",
        "pn": page,  # 第1页
        "pz": 100,  # 每页100条
        "po": 0,
        "dect": 1,
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "wbp2u": "|0|0|0|web"
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)

#get_timeline("0.300059")
#get_dayk("0.300059")
#get_stock_price_bylist(["1.600519","0.300059","116.00354"])
#get_stock_code_market(page=1,market=0)
