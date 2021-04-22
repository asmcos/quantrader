from .common import *
import baostock as bs

# print 打印color 表
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


stocklist=[]

bs.login()

def get_data(name,code,start,end):
    mnlist = []
    rs = bs.query_history_k_data_plus(code, 'date,open,high,low,close,volume,code,turn', start_date=start,
                                      frequency='d' )
    datas = rs.get_data()
    if len(datas) < 2:
        return [] 
    print(len(datas),datas.date[datas.index[-1]])
    closes = datas['close']
    dates = datas['date']
    return datas

def getstockinfo(stock):
    #2019-12-09,sz.002094,青岛金王,化工,申万一级行业
    # 时间，股票代码，名称，类别
    d,code,name,skip1,skip2,HQLTSZ= stock.split(',')
    return code,name


def loop_all(callback):
     for stock in stocklist:
        code ,name = getstockinfo(stock)
        print('正在获取',name,'代码',code)
        datas = get_data(name,code,start,today)
        callback(code,name,datas)

def init_stock_list():
    global stocklist

    if not os.path.exists('./datas/stock_industry_check.csv'):
        print('正在下载股票库列表....')
        os.system('python3 bs_get_industry_check.py')

    stocklist = open('./datas/stock_industry_check.csv').readlines()
    stocklist = stocklist[1+int(offset):] #删除第一行
    return stocklist

