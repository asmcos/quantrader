#Dragon phoenix 龙凤呈祥

from common.framework import *
import pandas as pd


filename = './datas/stock_dragon.html'

#金叉
def CrossUp(a,b):
    if a[-1] >= b[-1] and a[-2]<b[-2]:
        return True
    return False
#死叉    
def CrossDown(a,b):
        
    if a[-1] <= b[-1] and a[-2] > b[-2]:
        return True

    return False


"""
RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
K:SMA(RSV,M1,1);
D:SMA(K,M2,1);
"""

period = 5 
#大瀑布列表
wflist = []
def mn(datas,code,name):

    if len(datas) < 10:
        return []
    mnlist = []
    closes = datas['close']
    dates = datas['date']
    distance = 0
    prev_close = -1
    for i in range(period,len(dates)-period):
        m = talib.MAX(closes[i-period:i+period],len(closes[i-period:i+period]))
        n = talib.MIN(closes[i-period:i+period],len(closes[i-period:i+period])) #d 是最近时间，所以D不能往后太多
        m1 = m.values[-1]
        n1 = n.values[-1]
        if float(m1) == float(closes[i]):
            print("max",dates[i],closes[i],i-distance)
            mnlist.append([1,datas.values[i],float(closes.values[i]),i])
            distance = i
            prev_close = closes[i]
        if float(n1) == float(closes[i]):
            print("min",dates[i],closes[i],i-distance)
            if (i - distance) > 20 and closes[i] < prev_close: 
                print(OKBLUE,"bigwaterfall",code,name,dates[i],i-distance,ENDC)
                wflist.append([code,name,dates[i]])
            mnlist.append([0,datas.values[i],float(closes.values[i]),i])
            distance = i
            prev_close = closes[i]

 
    return mnlist

def search_wf(code):
    for i in wflist:
        if i[0] == code:
            return True
    return False
    
# 搜索瀑布,统计日K
def waterfall(code,name,datas):
    mn(datas,code,name)

dragonlist=[]
#搜索 macd金叉，kd 金叉，统计60分钟线
def dp(code,name,datas):
    print(code,name)
    

    df1 = datas #股票数据
    # 数据太少 macd 计算不准确 
    if len(datas) < 50:
        return

   # macd = macd * 2
    # 21,89,13
    df1['diff'], df1['dea'], df1['macd'] = talib.MACD(df1['close'], fastperiod=21, slowperiod=89, signalperiod=13)


    # 55,13,8
    df1['K'],df1['D'] = KD(df1['high'], df1['low'], df1['close'], fastk=55, slowk=13, slowd=8)

    distance = 0
    for i in range(10,len(datas)):
        ma = CrossUp(df1['diff'].values[:i],df1['dea'].values[:i])
        kd = CrossUp(df1['K'].values[:i],df1['D'].values[:i])
        if ma or kd:
            if ma and kd : distance = 0
            if distance < 10:
                print(OKGREEN,ma,kd,datas['time'].iloc[i],distance,ENDC)
                if search_wf(code) and df1['K'].values[i] <= 60:
                    print(OKGREEN,"dragon",name,code,datas['time'].iloc[i],ENDC)
                    dragonlist.append([code,name,datas['time'].iloc[i]])
            distance = 0

        distance += 1

def create_clickable_code(code):
    code = code.replace(".","")
    url_template= '''<a href="http://quote.eastmoney.com/{code}.html" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template

def save():

    df = pd.DataFrame(dragonlist,columns=['code','name','date'])
    df['code'] = df['code'].apply(create_clickable_code)
    content ='<meta charset="utf-8">\n龙凤呈祥\n'
    content += df.to_html(escape=False,float_format='%.2f')

    print("save file",filename)
    save_file(filename,content)
 

if __name__ == "__main__":
    init_stock_list()
    loop_all(waterfall)
    loop_60all(dp)
    save()
