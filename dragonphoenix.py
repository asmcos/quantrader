#Dragon phoenix 龙凤呈祥

from common.framework import *

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

def dp(code,name,datas):
    print(code,name)
    #print(datas)

    df1 = datas #股票数据
    # 数据太少 macd 计算不准确 
    if len(datas) < 50:
        return

   # macd = macd * 2
    # 21,88,13
    df1['diff'], df1['dea'], df1['macd'] = talib.MACD(df1['close'], fastperiod=21, slowperiod=88, signalperiod=13)

    #print(df1['diff'],df1['dea'],df1['macd'])
    #print("macd",CrossUp(df1['dea'].values,df1['diff'].values))


    # 55,13,8
    df1['K'],df1['D'] = KD(df1['high'], df1['low'], df1['close'], fastk=55, slowk=13, slowd=8)
    #print("kd",CrossUp(df1['K'].values,df1['D'].values))


    for i in range(10,len(datas)):
        ma = CrossUp(df1['diff'].values[:i],df1['dea'].values[:i])
        kd = CrossUp(df1['K'].values[:i],df1['D'].values[:i])
        if ma and kd:
            print(ma,kd,datas['time'].iloc[i])

if __name__ == "__main__":
    init_stock_list()
    loop_60all(dp)
