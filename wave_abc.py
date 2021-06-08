#
# python3 talib demo使用用例
#
# talib 是非常有价值的股票计算分析工具
# 有很多写好的公式可以直接使用
# 本例子源代码在github上
# https://github.com/asmcos/quantrader
#  python3 wave_abc.py --start="2020-02-18"
import talib
from common.framework import *
import numpy as np

#金叉
def CrossUp(a,b):
    if a[-1] >= b[-1] and a[-2] < b[-2]:
        return True
    return False

resultlist = []
def wave_abc(code,name,datas):

    print(code,name) 

    df1 = datas #股票数据
    # 数据太少 macd 计算不准确 
    if len(datas) < 50:
        return

    df1['diff'], df1['dea'], df1['macd'] = talib.MACD(df1['close'], fastperiod=12, slowperiod=26, signalperiod=9)

    #计算 0 轴附近,40个周期内的macd最大值 * 0.2
    macd0_approx = talib.MAX(np.abs(df1['macd'].values),30)*0.2
    #计算 MACD 高点附近
    macd1_approx = talib.MAX(np.abs(df1['macd'].values),30)*0.7

    status = 0
    for i in range(1,len(df1)-1):
        dk = df1.iloc[i-1:i+1] #交叉后一个交易周期
        if CrossUp(dk['diff'].values,dk['dea'].values):
            if abs(df1['diff'].iloc[i])  < abs(macd0_approx[i]*2) and status == 4:
                print(OKBLUE,"0Cross轴金叉",code,name,df1.date.iloc[i],abs(df1['diff'].iloc[i]),ENDC)
                resultlist.append([code,name,df1.date.iloc[i]])
            else:
                status = 1
        #死叉
        if CrossUp(dk['dea'].values,dk['diff'].values):
            if abs(df1['diff'].iloc[i])  > abs(macd1_approx[i]*2) :
                print("高位死叉",df1.date.iloc[i],abs(df1['diff'].iloc[i]))
                status = 4
            else:
                status = 1

def display():
    for i in resultlist:
        print(i)

if __name__ == "__main__":
    init_stock_list()
    loop_all(wave_abc) 
    display()
