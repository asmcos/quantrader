#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

""" 从baostock获取daily数据到datas目录下的csv文件当中，文件名如：bs_sh.000001.csv """
""" python3 bs_to_csv.py --code sh.600600 """
import baostock as bs
import pandas as pd
import click
from datetime import datetime
import os
import json
import argparse
import requests
import time
import tdxhy

# 判断是否 是显示，还是重新下载数据计算
# 数据每天只需要下载一次

parser = argparse.ArgumentParser()
parser.add_argument("--offset", help="开始执行的位置",default='0')
args = parser.parse_args()

offset = args.offset



today = datetime.now().strftime('%Y-%m-%d')

lg = bs.login()
""" 函数参数装饰器 
@click.command()
@click.option("--name", default="浦发银行", help="baostock股票/指数代码，如浦发银行")
@click.option("--code", default="sh.600000", help="baostock股票/指数代码，如sh.600000")
@click.option("--start", default="2010-01-01", help="开始日期, 格式如：2010-01-01")
@click.option("--end", default=today, help="结束日期, 格式如：2010-01-01")
@click.option("--adj", default="3", help="复权类型(只针对股票)：3: 未复权 2:前复权 1:后复权 , 默认1")
"""
def get_data(name,code, start, end, adj):

    rs = bs.query_history_k_data_plus(code, 'date,open,high,low,close,volume,turn', start_date=start, end_date=end,
                                      frequency='d', adjustflag=adj)
    
	#print('query_history_k_data_plus respond error_code:' + rs.error_code)
    #print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
    # 打印结果集
    columns = ['date', 'open', 'high', 'low', 'close', 'volume','turn']
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())


def get_data_post_server(name,code,start,end,adj):
    rs = bs.query_history_k_data_plus(code, 'date,open,high,low,close,volume,code,turn', start_date=start,
                                      frequency='d' )
    datas = rs.get_data()
    if len(datas) < 2:
        return
    print(len(datas),datas.date[datas.index[-1]])
	#datas['name'] = name
    #datas = datas.set_index('date')
    datas = datas.to_json(orient='table')
    jsondatas = json.loads(datas)['data']
    for d in jsondatas:
        d['name'] = name
        del d['index']
    #print(jsondatas)
    #resp = requests.post("http://127.0.0.1:1337/dayks/updates",json=jsondatas)
    #print(resp.content)
    try:
        requests.post("http://klang.zhanluejia.net.cn/dayks/updates",json=jsondatas,timeout=2000)
    except:
        time.sleep(2)
        requests.post("http://klang.zhanluejia.net.cn/dayks/updates",json=jsondatas,timeout=2000)
        
#获取股票的名字和代码号
def getstockinfo(stock):
    #2019-12-09,sz.002094,青岛金王,化工,申万一级行业
    # 时间，股票代码，名称，类别
    d,code,name,skip1,skip2,tdxbk,tdxgn= stock.split(',')
    return code,name,tdxbk,tdxgn




# 判断是否已经下载了股票分类代码
filename_sl = os.path.expanduser("~/.klang_stock_list.csv")

if not os.path.exists(filename_sl):
    print('正在下载股票库列表....')
    os.system('python3 bs_get_industry_check.py')

stocklist = open(filename_sl).readlines()
stocklist = stocklist[1+int(offset):] #删除第一行


if __name__ == "__main__":
     for stock in stocklist:
        code ,name,tdxbk,tdxgn = getstockinfo(stock)
        print('正在获取',name,'代码',code)
        get_data_post_server(name,code,"2021-06-01",today,"3")
