from .common import *
import baostock as bs
import talib

# print 打印color 表
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKRED = '\033[31m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


stocklist=[]

bs.login()

def create_clickable_code(code):
    code = code.replace(".","")
    url_template= '''<a href="http://quote.eastmoney.com/{code}.html" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template
def create_clickable_name(name):
    url_template= '''<a href="http://so.eastmoney.com/News/s?keyword={name}" target="_blank"><font color="blue">{name}</font></a>'''.format(name=name)
    return url_template

def create_color_rise1(rise):
    url_template= '''<font color="#ef4136">{rise}</font></a>'''.format(rise=rise)
    return url_template

def create_color_hqltgz(hqltsz):
    if hqltsz > 80.0:
        url_template= '''<font color="#ef4136">{hqltsz}</font></a>'''.format(hqltsz=hqltsz)
    else:
        url_template = '''{hqltsz}'''.format(hqltsz=hqltsz)
    return url_template

def save_df_tohtml(filename,df):
        df['代码'] = df['code'].apply(create_clickable_code)
        df['名称'] = df['name'].apply(create_clickable_name)
        df['流通股值'] = df['流通股值'].apply(create_color_hqltgz)
        del df['code']
        del df['name']
        content = df.to_html(escape=False)
        save_file(filename,content)

def get_mnlist(datas,period=3):
    mnlist = []
    closes = datas['close']
    dates = datas['date']

    for i in range(period,len(dates)-period):
        m = talib.MAX(closes[i-period:i+period],len(closes[i-period:i+period]))
        n = talib.MIN(closes[i-period:i+period],len(closes[i-period:i+period])) #d 是最近时间，所以D不能往后太多
        m1 = m.values[-1]
        n1 = n.values[-1]
        if float(m1) == float(closes[i]):
            #print("max",dates[i],closes[i])
            mnlist.append([1,datas.values[i],float(closes.values[i])])
        if float(n1) == float(closes[i]):
            #print("min",dates[i],closes[i],i,closes[i-period:i+5])
            mnlist.append([0,datas.values[i],float(closes.values[i])])


    # 追加D发现最近的D 
    for i in range(len(dates)-period,len(dates)-1):
      try:
        n = talib.MIN(closes[i-period:i+2],len(closes[i-period:i+2])) #d 是最近时间，所以D不能往后太多
        n1 = n.values[-1]
        if float(n1) == float(closes[i]):
            #print("min",dates[i],closes[i])
            mnlist.append([0,datas.values[i],float(closes.values[i])])
      except:
            pass
    return mnlist


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

