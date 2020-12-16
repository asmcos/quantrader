#
# exec script
# 计算股票昨日涨跌 前50，和100日之前的涨跌对比
# tushare 接口
import os
import sys
import signal
import threading,time
import queue
import pandas as pd
from datetime import datetime
import tushare as ts
import config
import argparse

# 判断是否 是显示，还是重新下载数据计算
# 数据每天只需要下载一次

parser = argparse.ArgumentParser()
parser.add_argument("--display", help="显示本地数据",default='0')
args = parser.parse_args()

display = args.display

####################
#1. 获取股票数据
####################
tspro = ts.pro_api(config.tspro['passwd'])
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
	df = pd.DataFrame(all_up_down_list, columns = ['昨日收盘','前日收盘','百日收盘','昨日涨跌','百日涨跌','名称','代码'])
	df.to_csv("./datas/stock_up_down_{0}.csv".format(endday),float_format='%.2f',index_label="序号")


#仅仅显示
def display_save_data():
	df= pd.read_csv("./datas/stock_up_down_{0}.csv".format(endday))

	df = df.sort_values(by="昨日涨跌",ascending=False)
	print(df.iloc[0:50])

	df = df.sort_values(by="百日涨跌",ascending=False)
	print(df.iloc[0:50])


def upordown(code,name):
	#df = ts.get_hist_data(code,start='2020-05-01')
	df = tspro.daily(ts_code=code, start_date='20200501')
	if len(df) < 2:
		return 
	lastday = df.index[0]
	lastday2 = df.index[1]
	closeld = float(df.close[lastday])
	closeld2 = float(df.close[lastday2])

	closeld100 = 0.0
	delta100 = 0.0
	if len(df) > 99:
		closeld100 = float(df.close[df.index[99]]) 
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

		
#获取股票的名字和代码号
def getstockinfo(stock):
	#2019-12-09,sz.002094,青岛金王,化工,申万一级行业
	# 时间，股票代码，名称，类别
	d,code,name,skip1,skip2 = stock.split(',')

	shsz = code.split('.')[0]
	code = code.split('.')[1]
	if shsz == 'sh':
		shsz = '.SH'
	if shsz == 'sz':
		shsz = '.SZ'
	return code+shsz,name

#获取所有的股票并下载数据
def get_data_thread(n):
	for stock in stocklist:
		code ,name = getstockinfo(stock)
		print('正在获取',name,'代码',code)
		q.put((code,name))
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
        code,name = q.get()
        print('正在分析',name,'代码',code)
        upordown(code,name)

    make_save_data()	

