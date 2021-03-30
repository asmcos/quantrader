#
# exec script
# 计算股票昨日涨跌 前200，和100日之前的涨跌对比


import os
import sys
import signal
import threading,time
import queue
import pandas as pd
import numpy as np
from datetime import datetime
import json
import argparse
import requests
import talib
# 判断是否 是显示，还是重新下载数据计算
# 数据每天只需要下载一次

parser = argparse.ArgumentParser()
parser.add_argument("--endday", help="日期",default='0')
args = parser.parse_args()

endday = args.endday

requests.adapters.DEFAULT_RETRIES = 5
####################
#1. 获取股票数据
####################

today = datetime.now()
if endday== '0':
	endday = str(today.year) + str(today.month) + str(today.day)
	
# print 打印color 表
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


# 处理异常，在出现异常的时候存盘
def handler(signum, frame):
	print("是不是想让我退出啊")
	sys.exit()


server="http://zhanluejia.net.cn"


def save_db_server(df):

    df = df.set_index('date')
    df = df.to_json(orient='table')
    jsondatas = json.loads(df)['data']

    requests.post(server+"/stock/updatedayMa",json=jsondatas,timeout=1000)


def get_day_ma(code,name):
    json = requests.get(server+"/stock/getdayMa",
        	params={"code":code,"end":endday,"limit":150},timeout=1000).json()

    print(json[0])

def get_day_data(code,name):
    try:
        json = requests.get("http://zhanluejia.net.cn/stock/getdayK",
        	params={"code":code,"end":endday,"limit":150},timeout=1000).json()
    except:
        time.sleep(2)
        json = requests.get("http://zhanluejia.net.cn/stock/getdayK",
        	params={"code":code,"end":endday,"limit":150},timeout=1000).json()
		
    df = pd.io.json.json_normalize(json)
	
    if len(df) < 2:
       return df
    df = df.drop(columns=['_id','codedate'])
    df = df.sort_values(by="date",ascending=True)


    return df

		
#获取股票的名字和代码号
def getstockinfo(stock):
	#2019-12-09,sz.002094,青岛金王,化工,申万一级行业
	# 时间，股票代码，名称，类别
	d,code,name,industry,skip2,hqltsz = stock.split(',')
	return code,name,industry



def ma(df):
    #通过tushare获取股票信息
    #提取收盘价
    closed=df['close'].values
    #获取均线的数据，通过timeperiod参数来分别获取 5,10,20 日均线的数据。
    ma5=talib.SMA(closed,timeperiod=5)
    ma10=talib.SMA(closed,timeperiod=10)
    ma20=talib.SMA(closed,timeperiod=20)
    ma30=talib.SMA(closed,timeperiod=30)
    ma60=talib.SMA(closed,timeperiod=60)

    ma5[np.isnan(ma5)] = 0
    ma10[np.isnan(ma10)] = 0
    ma20[np.isnan(ma20)] = 0
    ma30[np.isnan(ma30)] = 0
    ma60[np.isnan(ma60)] = 0

    df['ma5'] = ma5
    df['ma10'] = ma10
    df['ma20'] = ma20
    df['ma30'] = ma30
    df['ma60'] = ma60
    save_db_server(df) 

def get_data():
    for stock in stocklist:
        code ,name,industry = getstockinfo(stock)
        print('正在获取',name,'代码',code)
        df = get_day_data(code,name)
        if len(df) > 10:
            ma(df)
        else:
            continue
        #get_day_ma(code,name)

#
# 程序开始，监听信号
#
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGHUP, handler)
signal.signal(signal.SIGTERM, handler)
q = queue.Queue()

# 判断是否已经下载了股票分类代码

if not os.path.exists('./datas/stock_industry_check.csv'):
	print('正在下载股票库列表....')
	os.system('python3 bs_get_industry_check.py')

stocklist = open('./datas/stock_industry_check.csv').readlines()
stocklist = stocklist[1:] #删除第一行

# 判断是仅仅显示，还是需要下载数据计算
if True:

    get_data()

