#
# exec script
# 计算股票昨日涨跌 前50，和100日之前的涨跌对比


import os
import sys
import signal
import threading,time
import queue
import pandas as pd
from datetime import datetime
import baostock as bs

import argparse

# 判断是否 是显示，还是重新下载数据计算
# 数据每天只需要下载一次

parser = argparse.ArgumentParser()
parser.add_argument("--display", help="显示本地数据",default='0')
parser.add_argument("--ishtml", help="生成html格式",default='0')
args = parser.parse_args()

display = args.display
ishtml = args.ishtml

####################
#1. 获取股票数据
####################

lg = bs.login()
today = datetime.now()
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

#所有的股票表计算后的数据表
all_up_down_list=[]

# 处理异常，在出现异常的时候存盘
def handler(signum, frame):
	print("是不是想让我退出啊")
	make_save_data()	
	sys.exit()

#存盘并且打印
def make_save_data():
	df = pd.DataFrame(all_up_down_list, columns = ['昨日收盘','前日收盘','百日收盘','昨日涨跌','百日涨跌','名称','代码','行业'])
	df.to_csv("./datas/stock_up_down_{0}.csv".format(endday),float_format='%.2f',index_label="序号")


def create_clickable_code(code):
    code = code.replace(".","")
    url_template= '''<a href="http://quote.eastmoney.com/{code}.html" target="_blank">{code}</a>'''.format(code=code)
    return url_template

#仅仅显示
def display_save_data():
	df= pd.read_csv("./datas/stock_up_down_{0}.csv".format(endday))
	if ishtml == "1":
		df['代码'] = df['代码'].apply(create_clickable_code)
	df = df.sort_values(by="昨日涨跌",ascending=False)
	if ishtml == "1":
		print(df.iloc[0:50].to_html(escape=False))
	else:
		print(df.iloc[0:50])

	df = df.sort_values(by="百日涨跌",ascending=False)
	if ishtml == "1":
		print(df.iloc[0:50].to_html(escape=False))
	else:
		print(df.iloc[0:50])

def get_day_data(code,name):
	kdata = bs.query_history_k_data_plus(code, 'date,open,high,low,close,volume', start_date='2020-05-01',
                                     frequency='d')
	df = kdata.get_data()
	return df 

def upordown(code,name,industry,lastday,lastday1,lastday100):
	lastday = float(lastday)
	lastday1 = float(lastday1)
	lastday100 = float(lastday100)
	delta1 = (lastday-lastday1)/lastday1 * 100.0

	delta100 = 0
	if lastday100 > 0:
		delta100 = (lastday-lastday100)/lastday100 * 100.0
	code = code.replace(".","")
	
	print(OKBLUE)
	print("%.2f %.2f %.2f %.2f %.2f %s %s" %(lastday,lastday1,
		lastday100,
		delta1,
		delta100,
		name,code)
		) 
	print(ENDC)

	all_up_down_list.append([
		lastday,lastday1,
		lastday100,
		delta1,
		delta100,
        name,code,industry
	])	

		
#获取股票的名字和代码号
def getstockinfo(stock):
	#2019-12-09,sz.002094,青岛金王,化工,申万一级行业
	# 时间，股票代码，名称，类别
	d,code,name,industry,skip2 = stock.split(',')
	return code,name,industry

#获取所有的股票并下载数据
def get_data_thread(n):
	for stock in stocklist:
		code ,name,industry = getstockinfo(stock)
		print('正在获取',name,'代码',code)
		df = get_day_data(code,name)
		if len(df) > 2:
			lastday  = df.close[df.index[-1]]
			lastday1 = df.close[df.index[-2]]
		lastday100 = 0
		if len(df) > 99:
			lastday100 = df.close[df.index[-100]] 
			q.put((code,name,industry,lastday,lastday1,lastday100))
	q.task_done()


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
if display == '1':
    display_save_data()
else :
    threading.Thread(target=get_data_thread,args=(1,)).start()
    while True:
        code,name,industry,lastday,lastday1,lastday100 = q.get()
        print('正在分析',name,'代码',code)
        upordown(code,name,industry,lastday,lastday1,lastday100)

    make_save_data()	

