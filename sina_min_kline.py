#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

""" 从 sina 获取分钟k数据 """
import pandas as pd
import click
from datetime import datetime
import os
import json
import argparse
import requests
import re
# 判断是否 是显示，还是重新下载数据计算
# 数据每天只需要下载一次

parser = argparse.ArgumentParser()
parser.add_argument("--offset", help="开始执行的位置",default='0')
parser.add_argument("--listlen", help="每次获取的股票数",default=200)
parser.add_argument("--resave", help="每次获取的股票数",default='0')
args = parser.parse_args()

offset = args.offset
resave = args.resave
listlen = int(args.listlen)

float2 = lambda a:float('%.2f' % a)

today = datetime.now().strftime('%Y-%m-%d')

code_list = []
csv_data = []
industrydict = {}

def create_clickable_code(code):
    code = code.replace(".","")
    url_template= '''<a href="http://quote.eastmoney.com/{code}.html" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template
def create_color_rise1(rise):
    url_template= '''<font color="#ef4136">{rise}</font></a>'''.format(rise=rise)
    return url_template

def get_data_fromjs(text):
	datas = []
	text_list = re.findall("var hq_str_(.+?);",text,re.S|re.M)
	for i in text_list:
		code,data = i.split("=")
		data = data.strip('"').split(",")
		rise = 0
		if float(data[2]) != 0:
			rise = (float(data[3]) - float(data[2])) * 100 / float(data[2]) 
			rise = float2(rise)
		datas.append([code,data[0],data[2],data[3],rise,industrydict[code]])

	df = pd.DataFrame(datas,columns=['code','name','昨日收盘','当前价','涨跌','行业'])
	df = df.sort_values(by="涨跌",ascending=False)
	df['code'] = df['code'].apply(create_clickable_code)
	df['涨跌'] = df['涨跌'].apply(create_color_rise1)
	print(df.iloc[:].reset_index(drop=True).to_html(escape=False))

def get_min_kdata(code,end=0):
	global code_list
	global csv_data 
	
	code_list.append(code)
	if len(code_list) >= listlen:
		codes = ",".join(code_list)	
		resp = requests.get('https://hq.sinajs.cn/?list=%s'%codes)
		csv_data.append(resp.text)
		code_list = []

def get_min_kdata_tail( ):
	global code_list
	global csv_data 
	if len(code_list) > 0:
		codes = ",".join(code_list)	
		resp = requests.get('https://hq.sinajs.cn/?list=%s'%codes)
		csv_data.append(resp.text)
		code_list = []

#获取股票的名字和代码号
def getstockinfo(stock):
    #2019-12-09,sz.002094,青岛金王,化工,申万一级行业
    # 时间，股票代码，名称，类别
    d,code,name,industry,skip2 = stock.split(',')
    code=code.replace(".","")

    industrydict[code]=industry
    return code,name,industry




# 判断是否已经下载了股票分类代码

if not os.path.exists('./datas/stock_industry_check.csv'):
    print('正在下载股票库列表....')
    os.system('python3 bs_get_industry_check.py')

stocklist = open('./datas/stock_industry_check.csv').readlines()
stocklist = stocklist[1+int(offset):] #删除第一行

for stock in stocklist:
    code ,name,industry = getstockinfo(stock)

if __name__ == "__main__":
     
     if not os.path.exists('./datas/stock_min_kdata.csv') or resave == '1':
     

        for stock in stocklist:
           code ,name,industry = getstockinfo(stock)
           print('正在获取',name,'代码',code)
           get_min_kdata(code)
        get_min_kdata_tail( )
        f = open('./datas/stock_min_kdata.csv','w')
        f.write('\n'.join(csv_data)) 
        f.close()       
     get_data_fromjs(open("./datas/stock_min_kdata.csv").read())
