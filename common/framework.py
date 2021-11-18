from .common import *
import baostock as bs
import talib
import numpy as np

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


def SMA(data,period,period2):
    y1 = 0
    result = []
    for d in data:
        if str(d) == 'nan':
            result.append(np.nan)
            continue
        y1=( period2 * d + (period-period2)*y1 )/period
        result.append(y1) 
    return result

def KD(high,low,close,fastk,slowk,slowd):
    """
    RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
    K:SMA(RSV,M1,1);
    D:SMA(K,M2,1);
    """
    lo = talib.MIN(low,timeperiod=fastk)
    hi = talib.MAX(high,timeperiod=fastk)

    close = close.astype('float64')

    rsv = (close-lo)/(hi-lo) * 100
    k = SMA(rsv,slowk,1)
    d = SMA(k,slowd,1)
    return k,d

#
# pandas 转化html是可以定制化渲染，增加可以点击，颜色等
#
"""
def create_clickable_code(code):
    code = code.replace(".","")
    url_template= '''<a href="http://quote.eastmoney.com/{code}.html" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template
"""
def create_clickable_code(code):
    code = code.replace(".","")
    url_template= '''<a href="https://gu.qq.com/{code}" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    url_template += ''' (|) <a href="http://klang.org.cn/kline.html?code={code}" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
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
######################################


#pandas 格式变成html格式
def save_df_tohtml(filename,df):
        df['代码'] = df['code'].apply(create_clickable_code)
        df['名称'] = df['name'].apply(create_clickable_name)
        df['流通股值'] = df['流通股值'].apply(create_color_hqltgz)
        del df['code']
        del df['name']
        content = df.to_html(escape=False)
        save_file(filename,content)



#简单的计算某个周期内的最大值和最小值
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
            mnlist.append([1,datas.values[i],float(closes.values[i]),datas.iloc[i]])
        if float(n1) == float(closes[i]):
            #print("min",dates[i],closes[i],i,closes[i-period:i+5])
            mnlist.append([0,datas.values[i],float(closes.values[i]),datas.iloc[i]])


    # 追加D发现最近的D 
    for i in range(len(dates)-period,len(dates)-1):
      try:
        n = talib.MIN(closes[i-period:i+2],len(closes[i-period:i+2])) #d 是最近时间，所以D不能往后太多
        n1 = n.values[-1]
        if float(n1) == float(closes[i]):
            #print("min",dates[i],closes[i])
            mnlist.append([0,datas.values[i],float(closes.values[i]),datas.iloc[i]])
      except:
            pass
    return mnlist

#从zhanluejia获取日K
def get_day_data(name,code,start,end):
    
    
    try:
        json = requests.get("http://klang.zhanluejia.net.cn/dayks",
            params={"code":code,"start":start,"limit":0},timeout=1000).json()
    except:
        time.sleep(2)
        json = requests.get("http://klang.zhanluejia.net.cn/dayks",
            params={"code":code,"start":start,"limit":0},timeout=1000).json()

    df = pd.io.json.json_normalize(json)

    if len(df) < 2:
       return df
    df = df.drop(columns=['_id','codedate'])
    df = df.sort_values(by="date",ascending=True).reset_index()
    del df['index']
    
    print(len(df),df.date.iloc[-1])
    return df


#从bs获取日K数据
def get_data(name,code,start,end):
    rs = bs.query_history_k_data_plus(code, 'date,open,high,low,close,volume,code,turn', start_date=start,
                                      frequency='d' )
    datas = rs.get_data()
    if len(datas) < 2:
        return [] 
    print(len(datas),datas.date[datas.index[-1]])
    return datas

#从bs获取60min K数据
def get_60_data(name,code,start,end):
    rs = bs.query_history_k_data_plus(code, 'date,time,open,high,low,close,volume,code', start_date=start,
                                      frequency='60' )
    datas = rs.get_data()
    if len(datas) < 2:
        return [] 
    print(len(datas),datas.date[datas.index[-1]])
    return datas
# 从文件中一行数据 格式化分析出信息
def getstockinfo(stock):
    #2019-12-09,sz.002094,青岛金王,化工,申万一级行业
    # 时间，股票代码，名称，类别
    d,code,name,skip1,skip2,tdxbk,tdxgn= stock.split(',')
    return code,name,tdxbk,tdxgn

#循环调用A股所有的股票
def loop_all(callback,stlist=stocklist):
     bs.login()
     for stock in stocklist:
        code ,name ,tdxbk,tdxgn= getstockinfo(stock)
        print('正在获取',name,'代码',code)
        datas = get_day_data(name,code,start,today)
        callback(code,name,datas)


def loop_60all(callback,stlist=stocklist):
     bs.login()
     for stock in stlist:
        code ,name,tdxbk,tdxgn = getstockinfo(stock)
        print('正在获取',name,'代码',code)
        datas = get_60_data(name,code,start,today)
        callback(code,name,datas)



hostname="http://klang.org.cn"
hostname="http://klang.zhanluejia.net.cn"

#
#stock list
#
cm_dict  = {}
def init_chouma( ):

    json = requests.get(hostname+"/industries").json()
    #df = pd.json_normalize(json)
    #df = df.drop(columns=['_id','updatedAt','id','createdAt'])
    # 结果集输出到csv文件
    #df.to_csv(stname, index=False,columns=['updateDate','code','code_name','industry','industryClassification','tdxbk','tdxgn','chouma'])
    for i in json:
        cm_dict[i['code']] = i.get('chouma','50')

def get_chouma(code):
    return cm_dict.get(code,"50")
    

filename_sl = os.path.expanduser("~/.klang_stock_list.csv")
#从csv文件列表中获取A股所有的股票信息
def init_stock_list():
    global stocklist

    if not os.path.exists(filename_sl):
        print('正在下载股票库列表....')
        os.system('python3 bs_get_industry_check.py')

    stocklist = open(filename_sl).readlines()
    stocklist = stocklist[1+int(offset):] #删除第一行
    init_chouma()

    return stocklist



