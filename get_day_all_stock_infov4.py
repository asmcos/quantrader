#
# exec script
# 计算股票昨日涨跌 前200，和100日之前的涨跌对比


import os
import sys
import signal
import threading,time
import queue
import pandas as pd
from datetime import datetime
import baostock as bs
import json
import argparse
import requests
# 判断是否 是显示，还是重新下载数据计算
# 数据每天只需要下载一次

parser = argparse.ArgumentParser()
parser.add_argument("--display", help="显示本地数据",default='0')
parser.add_argument("--ishtml", help="生成html格式",default='1')
parser.add_argument("--save_db", help="存储到远程数据库",default='0')
parser.add_argument("--file", help="存文件",default='0')
parser.add_argument("--endday", help="日期",default='0')
args = parser.parse_args()

display = args.display
ishtml = args.ishtml
filename = args.file
save_db = args.save_db
endday = args.endday

requests.adapters.DEFAULT_RETRIES = 5
####################
#1. 获取股票数据
####################
#hostname = "http://klang.org.cn"
hostname = "http://klang.zhanluejia.net.cn"
lg = bs.login()
today = datetime.now()
if endday== '0':
	endday = str(today.year) + str(today.month) + str(today.day)

if filename == '0':
    filename = './datas/stock_'+endday+'.html'
	
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
	df = pd.DataFrame(all_up_down_list, columns = ['名称','date','代码','当日收盘','前日收盘','21日收盘','百日收盘','当日涨跌','21日涨跌','百日涨跌','流通股值','行业'])
	df.to_csv("./datas/stock_up_down_{0}.csv".format(endday),float_format='%.2f',index_label="序号")


def create_clickable_code(code):
    code = code.replace(".","")
    url_template= '''<a href="https://gu.qq.com/{code}" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template
def create_clickable_name(name):
    url_template= '''<a href="http://so.eastmoney.com/News/s?keyword={name}" target="_blank"><font color="blue">{name}</font></a>'''.format(name=name)
    return url_template

def create_color_rise1(rise):
    url_template= '''<font color="#ef4136">{rise}</font></a>'''.format(rise=rise)
    return url_template

def create_color_hqltgz(hqltsz):
    if hqltsz >= 300.0:
        url_template= '''<font color="#ef4136">{hqltsz}</font></a>'''.format(hqltsz=hqltsz)
    else:
        url_template = '''{hqltsz}'''.format(hqltsz=hqltsz)
    return url_template
"""
    name: String,
    code: String,
    date: String,
    industry: String,
    close: Number,
    close1: Number,
    close21: Number,
    close100: Number,
    rise1: Number,
    rise21: Number,
    rise100: Number,
"""

#仅仅显示
def display_save_data():
    df= pd.read_csv("./datas/stock_up_down_{0}.csv".format(endday))
	
    del df['序号']
    #df = df.set_index('date')
    print("当日涨幅榜单:")
    df = df.sort_values(by="当日涨跌",ascending=False).reset_index()
    del df['index']
    if ishtml == "1":
        df['代码'] = df['代码'].apply(create_clickable_code)
        #df['名称'] = df['名称'].apply(create_clickable_name)
        df['当日涨跌'] = df['当日涨跌'].apply(create_color_rise1)
        df['流通股值'] = df['流通股值'].apply(create_color_hqltgz)
        #print(df.iloc[0:200]
        #    .reset_index(drop=True)
        #    .style.set_table_attributes('border="1" class="table"').render())
        from common.common import save_file
        content = "当日涨幅榜单:\n"
        content += df.iloc[0:200].to_html(escape=False)
        content += "当日涨幅榜，之前超跌榜\n"
        print("当日涨幅榜，之前超跌榜")
        
        df = df.iloc[0:200].sort_values(by="百日涨跌",ascending=True)
        print(df.to_html(escape=False))
        print("save to file:",filename)
        save_file(filename,content + df.to_html(escape=False))
    else:
        print(df.iloc[0:200])
    print("注：当日涨跌是date日期和他前一个交易日比较,百日涨跌是date日期和100天的股价比较")

def get_day_data(code,name):

    #json = requests.get("http://127.0.0.1:1337/dayks",
    #    	params={"code":code,"end":endday,"limit":150},timeout=1000).json()
    try:
        json = requests.get(hostname+"/dayks",
        	params={"code":code,"end":endday,"limit":150},timeout=1000).json()
    except:
        time.sleep(2)
        json = requests.get(hostname+"/dayks",
        	params={"code":code,"end":endday,"limit":150},timeout=1000).json()
	
    df = pd.io.json.json_normalize(json)
	
    if len(df) < 2:
       return df
    df = df.drop(columns=['_id','codedate'])
    df = df.sort_values(by="date",ascending=True)


    return df

def upordown(code,date,name,industry,lastday,lastday1,lastday21,lastday100,hqltsz):
	lastday = float(lastday)
	lastday1 = float(lastday1)
	lastday21 = float(lastday21)
	lastday100 = float(lastday100)
	delta1 = (lastday-lastday1)/lastday1 * 100.0

	delta21 = 0
	delta100 = 0
	if lastday21 > 0:
		delta21 = (lastday-lastday21)/lastday21 * 100.0
	if lastday100 > 0:
		delta100 = (lastday-lastday100)/lastday100 * 100.0
	code = code.replace(".","")
	
	print(OKBLUE)
	print("%.2f %.2f %.2f %.2f %.2f %.2f %.2f %s %s" %(lastday,lastday1,
		lastday21,
		lastday100,
		delta1,
		delta21,
		delta100,
		name,code)
		) 
	print(ENDC)

	all_up_down_list.append([
        name,date,code,
		lastday,lastday1,
		lastday21,
		lastday100,
		delta1,
		delta21,
		delta100,
		hqltsz*lastday,
        industry
	])	

		
#获取股票的名字和代码号
def getstockinfo(stock):
	#2019-12-09,sz.002094,青岛金王,化工,申万一级行业
	# 时间，股票代码，名称，类别
	d,code,name,industry,skip2= stock.split(',')
	return code,name,industry

#获取所有的股票并下载数据
def handler_data_thread(n):
    while True:
        code,date,name,industry,lastday,lastday1,lastday21,lastday100,hqltsz = q.get()
        print('正在分析',name,'代码',code,hqltsz)
        upordown(code,date,name,industry,lastday,lastday1,lastday21,lastday100,hqltsz)
        q.task_done() #每次做完任务就通知 join，jion收到最后一条通知就主程序退出

def get_data():
	for stock in stocklist:
		code ,name,industry = getstockinfo(stock)
		print('正在获取',name,'代码',code)
		df = get_day_data(code,name)
		#print(df)
		if len(df) > 2:
			try:
			    date = df.date[df.index[-1]]
			    turn = df.turn[df.index[-1]] 
			    volume = df.volume[df.index[-1]]
			    hqltsz = volume / turn / 1000000 
			    lastday  = df.close[df.index[-1]]
			    lastday1 = df.close[df.index[-2]]
			except:
			    continue
		else:
			continue
		lastday21 = 0
		if len(df) > 21:
			lastday21 = df.close[df.index[-21]] 
		lastday100 = 0
		if len(df) > 99:
			lastday100 = df.close[df.index[-100]] 
		q.put((code,date,name,industry,lastday,lastday1,lastday21,lastday100,hqltsz))

#
# 程序开始，监听信号
#
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGHUP, handler)
signal.signal(signal.SIGTERM, handler)
q = queue.Queue()

# 判断是否已经下载了股票分类代码
filename_sl = os.path.expanduser("~/.klang_stock_list.csv")

if not os.path.exists(filename_sl):
	print('正在下载股票库列表....')
	os.system('python3 bs_get_industry_check.py')

stocklist = open(filename_sl).readlines()
stocklist = stocklist[1:] #删除第一行

# 判断是仅仅显示，还是需要下载数据计算
if display == '1':
    display_save_data()
else:
    t = threading.Thread(target=handler_data_thread,args=(1,))
    t.start()

    get_data()

    q.join() #等待任务完成
    make_save_data()	
    display_save_data()
    os._exit(os.EX_OK)    
