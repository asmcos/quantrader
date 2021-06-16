#谐波理论之N字战法 harmonic

from common.framework import *
import pandas as pd
from  fibonacci import *

filename = './datas/stock_harmonic_n.html'

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

period = 6 
# 最大最小的列表

Nlist = []
#d,code,name,skip1,skip2
Nstocklist = []
def mn(datas,code,name):

    if len(datas) < 10:
        return []
    closes = datas['close']
    dates = datas['date']
    distance = 0
    prev_close = -1
     
    mnlist = []
    for i in range(period,len(dates)-period):
        m = talib.MAX(closes[i-period:i+period],len(closes[i-period:i+period]))
        n = talib.MIN(closes[i-period:i+period],len(closes[i-period:i+period])) #d 是最近时间，所以D不能往后太多
        m1 = m.values[-1]
        n1 = n.values[-1]
        if float(m1) == float(closes[i]):
            print("max",dates[i],closes[i],i-distance)
            mnlist.append([1,dates.values[i],float(closes.values[i]),i])
            distance = i
            prev_close = closes[i]
        if float(n1) == float(closes[i]):
            print("min",dates[i],closes[i],i-distance)
            mnlist.append([0,dates.values[i],float(closes.values[i]),i])
            distance = i
            prev_close = closes[i]

    return mnlist

# a > b
def scope(a,b):
    return (a-b) / a  * 100


Nlist=[]

#搜索 X,A,B
def N(mnlist,code,name):

    X = None
    A = None
    B = None
    status = 0 #反转状态 X->A->B
    distance = 0 #周期 > 10天？
    for i in mnlist:
        if i[0] == 0 and status == 0:
            X = i
            status = 1
            distance = i[3]
        if i[0] == 1 and status == 1 and i[3] - distance > 10 and scope(i[2],X[2]) > 10:
            status = 2
            A = i
            distance = i[3]
        if i[0] == 0 and status == 2 and i[3] - distance > 10 and scope(A[2],i[2]) > 10:
            status = 0
            distance = 0
            B = i
            b1 = downN(A[2],X[2],0.786) #b
            b2 = downN(A[2],X[2],0.618) #b 
            if approx(B[2],b1):
                print("N 0.786",(X[2],X[1]),(A[2],A[1]),(B[2],B[1]),b1)
                Nlist.append([code,name,B[1]])
            if approx(B[2],b2):
                print("N 0.618",(X[2],X[1]),(A[2],A[1]),(B[2],B[1]),b2)
                Nlist.append([code,name,B[1]])
 
# 搜索最大最小值,统计日K
def waterfall(code,name,datas):

    try:
        df = datas
        turn = df.turn[df.index[-1]]
        volume = df.volume[df.index[-1]]
        close = df.close[df.index[-1]]
        hqltsz = volume / turn / 1000000
        if hqltsz*close < 300:
            return 
    except:
        return

    mnlist = mn(datas,code,name)
    N(mnlist,code,name)

def create_clickable_code(code):
    code = code.replace(".","")
    url_template= '''<a href="http://quote.eastmoney.com/{code}.html" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template

def save():

    df = pd.DataFrame(Nlist,columns=['code','name','date'])
    df['code'] = df['code'].apply(create_clickable_code)
    content ='<meta charset="utf-8">\n谐波理论之N字形态\n'
    content += df.to_html(escape=False,float_format='%.2f')

    print("save file",filename)
    save_file(filename,content)
 

if __name__ == "__main__":
    init_stock_list()
    loop_all(waterfall)
    save()
