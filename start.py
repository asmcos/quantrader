#
# exec script
import os
import sys
code = '600600'

if len(sys.argv) > 1:
	code = sys.argv[1]

def macd(code):
	os.system('rm -f ./datas/ts_' + code+'.csv')
	os.system('python3 ts_to_csv.py --code '+code+' --start 2019-10-01')
	os.system('python3 btrmacd.py --datafile ./datas/ts_'+code+'.csv')


#python3 btrstoch.py --datafile ./datas/ts_$code.csv
#python3 btrrsi.py --datafile ./datas/ts_$code.csv

if not os.path.exists('./datas/stock_industry.csv'):
	print('正在下载股票库列表....')
	os.system('python3 ts_get_industry.py')

def getstockinfo(stock):
	#2019-12-09,sz.002094,青岛金王,化工,申万一级行业
	# 时间，股票代码，名称，类别
	d,code,name,skip1,skip2 = stock.split(',')
	code = code.split('.')[1]
	return code,name
stocklist = open('./datas/stock_industry.csv').readlines()
stocklist = stocklist[1:] #删除第一行
for stock in stocklist:
	code ,name = getstockinfo(stock)
	print('正在分析',name,'代码',code)
	macd(code)
