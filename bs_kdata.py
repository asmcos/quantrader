#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

""" 从baostock获取daily数据到datas目录下的csv文件当中，文件名如：bs_sh.000001.csv """
""" python3 bs_to_csv.py --code sh.600600 """
import baostock as bs
import pandas as pd
from datetime import datetime
import os
import requests
import talib
# 判断是否 是显示，还是重新下载数据计算
# 数据每天只需要下载一次
from common.common import *
from fibonacci import search_pattern

today = datetime.now().strftime('%Y-%m-%d')

lg = bs.login()

period = 8 

def get_data(name,code,start,end,adj):
    mnlist = []
    rs = bs.query_history_k_data_plus(code, 'date,open,high,low,close,volume,code,turn', start_date=start,
                                      frequency='d' )
    datas = rs.get_data()
    if len(datas) < 2:
        return
    print(len(datas),datas.date[datas.index[-1]])
    closes = datas['close']
    dates = datas['date']

    for i in range(period,len(dates)-period):
        m = talib.MAX(closes[i+1-period:i-1+period],2*period-2)
        n = talib.MIN(closes[i+1-period:i-1+period],2*period-2)
        m1 = m.values[-1]
        n1 = n.values[-1]
        if float(m1) == float(closes[i]):
            #print("max",dates[i],closes[i])
            mnlist.append([1,datas.values[i],float(closes.values[i])])
        if float(n1) == float(closes[i]):
            #print("min",dates[i],closes[i])
            mnlist.append([0,datas.values[i],float(closes.values[i])])

    search_pattern(name,code,mnlist)


def getstockinfo(stock):
    #2019-12-09,sz.002094,青岛金王,化工,申万一级行业
    # 时间，股票代码，名称，类别
    d,code,name,skip1,skip2,HQLTSZ= stock.split(',')
    return code,name




# 判断是否已经下载了股票分类代码

if not os.path.exists('./datas/stock_industry_check.csv'):
    print('正在下载股票库列表....')
    os.system('python3 bs_get_industry_check.py')

stocklist = open('./datas/stock_industry_check.csv').readlines()
stocklist = stocklist[1+int(offset):] #删除第一行


if __name__ == "__main__":
     for stock in stocklist:
        code ,name = getstockinfo(stock)
        print('正在获取',name,'代码',code)
        get_data(name,code,"2020-03-20",today,"3")
