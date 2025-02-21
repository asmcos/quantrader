import requests
import re
import json
import time

t = str(time.time())


def timeline(code):
    #code = "116.01822"
    #code = "0.300059"
    url = "https://push2his.eastmoney.com/api/qt/stock/trends2/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58&ut=fa5fd1943c7b386f172d6893dbfba10b&iscr=0&ndays=1&secid=%s&_=%s26" % (code,t)

    resp = requests.get(url)
    print(resp.text)


def dayline(code):
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=20200101&end=20500101&ut=fa5fd1943c7b386f172d6893dbfba10b&rtntype=6&secid=%s&klt=101&fqt=1" %(code)

    resp = requests.get(url)
    print(resp.text)

def curlist(codelist):
    #http://qt.gtimg.cn/r=0.8409869808238q=s_sz000559,s_sz000913,s_sz002048,s_sz002085,s_sz002126,s_sz002284,s_sz002434,s_sz002472,s_sz002488
    # 多只股票的代码，以 A 股为例
    # 构造请求 URL
    #https://push2.eastmoney.com/api/qt/ulist.np/get?fields=f2,f3,f4,f6,f104,f105,f106,f12,f13,f10,f9,f8,f14&secids=1.000001,1.600010,116.00354,1.688047
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    # 定义请求参数
    params = {
    # 这里选择了一些常用字段，可根据需求调整
    "fields": "f12,f13,f14,f2,f3",
    # 示例股票代码，1 代表 A 股，0 代表创业板等，可添加更多
    "secids": ",".join(["1.600519","0.300059","116.00354"])
    }

    response = requests.get(url, params=params)
    print(response.text)


#timeline("0.300059")
#dayline("0.300059")
curlist([])

