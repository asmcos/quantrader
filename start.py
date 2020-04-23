#
# exec script
import os
import sys
import signal
import threading,time
import queue

code = '600600'

def handler(signum, frame):
	print("是不是想让我退出啊")
	sys.exit()


def macd(code,name):

    os.system('rm -f ./datas/ts_' + code+'.csv')
    y1 = os.system('python3 ts_to_csv.py --code '+code+' --start 2019-10-01')
    y2 = os.system('python3 btrmacd.py --datafile ./datas/ts_'+code+'.csv' + ' --code ' + code
	+' --name ' + name + ' --savedb 1')



def mrk(code,name):
	y1 = os.system('python3 btrmrk.py --datafile ./datas/ts_'+code+'.csv' + ' --code ' + code
	+' --name ' + name + ' --savedb 1')
	if y1 == 2: #ctrl+c
	    print(y1)
	    sys.exit()

def get_code_cvs(code):
	os.system('rm -f ./datas/ts_' + code+'.csv')
	y1 = os.system('python3 ts_to_csv.py --code '+code+' --start 2019-10-01')
	if y1 == 2 : #ctrl+c
	    print(y1)
	    sys.exit()
		

def getstockinfo(stock):
	#2019-12-09,sz.002094,青岛金王,化工,申万一级行业
	# 时间，股票代码，名称，类别
	d,code,name,skip1,skip2 = stock.split(',')
	code = code.split('.')[1]
	return code,name

def get_data_thread(n):
	for stock in stocklist:
		code ,name = getstockinfo(stock)
		print('正在获取',name,'代码',code)
		get_code_cvs(code)
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
	mrk(code,name)
