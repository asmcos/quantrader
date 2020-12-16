#
# exec script
import os
import sys
import signal
import threading,time
import queue
import pandas as pd
from datetime import datetime
import baostock as bs

####################
#1. 获取股票数据
####################

lg = bs.login()
today = datetime.now()
endday = str(today.year) + str(today.month) + str(today.day)

code = 'sh.600600'

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

all_up_down_list=[]

def handler(signum, frame):
	print("是不是想让我退出啊")
	make_save_data()	
	sys.exit()

def make_save_data():
	df = pd.DataFrame(all_up_down_list, columns = ['昨日收盘','前日收盘','百日收盘','昨日涨跌','百日涨跌','名称','代码'])
	df.to_csv("./datas/stock_up_down_{0}.csv".format(endday),float_format='%.2f',index_label="序号")

	df = df.sort_values(by="昨日涨跌",ascending=False)
	print(df.iloc[0:50])

	df = df.sort_values(by="百日涨跌",ascending=False)
	print(df.iloc[0:50])

def upordown(code,name):
	kdata = bs.query_history_k_data_plus(code, 'date,open,high,low,close,volume', start_date='2020-05-01',
                                     frequency='d')
	df = kdata.get_data()
	if len(df) < 2:
		return 
	lastday = df.index[-1]
	lastday2 = df.index[-2]
	closeld = float(df.close[lastday])
	closeld2 = float(df.close[lastday2])

	closeld100 = 0.0
	delta100 = 0.0
	if len(df) > 99:
		closeld100 = float(df.close[df.index[-100]]) 
		delta100 = float((closeld-closeld100) / closeld100 ) * 100.0	
	print(OKBLUE)
	print("%.2f %.2f %.2f %.2f %.2f %s %s" %(closeld,closeld2,
		closeld100,
		(closeld-closeld2)/closeld2 * 100.0,
		delta100,
		name,code)
		) 
	print(ENDC)
	all_up_down_list.append([
		closeld,closeld2,
		closeld100,
        (closeld-closeld2)/closeld2  * 100.0,
		delta100,
        name,code
	])	

#获取最新数据
def get_code_cvs(code):
	os.system('rm -f ./datas/bs_' + code+'.csv')
	y1 = os.system('python3 bs_to_csv.py --code '+code+' --start 2020-10-01')
	if y1 == 2 : #ctrl+c
		print(y1)
		handler("1","get_code_cvs")
	    #sys.exit()
		
#获取股票的名字和代码号
def getstockinfo(stock):
	#2019-12-09,sz.002094,青岛金王,化工,申万一级行业
	# 时间，股票代码，名称，类别
	d,code,name,skip1,skip2 = stock.split(',')
	#code = code.split('.')[1] bs not need the line
	return code,name

#获取所有的股票并下载数据
def get_data_thread(n):
	for stock in stocklist:
		code ,name = getstockinfo(stock)
		print('正在获取',name,'代码',code)
		#get_code_cvs(code)
		q.put((code,name))
	q.task_done()

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGHUP, handler)
signal.signal(signal.SIGTERM, handler)
q = queue.Queue()

if len(sys.argv) > 1:
	code = sys.argv[1]

if not os.path.exists('./datas/stock_industry_check.csv'):
	print('正在下载股票库列表....')
	os.system('python3 bs_get_industry_check.py')

stocklist = open('./datas/stock_industry_check.csv').readlines()
stocklist = stocklist[1:] #删除第一行


threading.Thread(target=get_data_thread,args=(1,)).start()


while True:
	code,name = q.get()
	print('正在分析',name,'代码',code)
	upordown(code,name)

make_save_data()	

