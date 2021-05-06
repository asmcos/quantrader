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
def CrossUp(a,b,state):
    if a > b :
        if state == 0:
            return True,1
        return False,1     
    else:
        return False,0
#死叉    
def CrossDown(a,b,state):
    if (a < b):
        if state == 1:
            return True,0
        return False,0
    else:
        return False,1


def wave_abc(code,name,datas):
    state = 2

    df1 = datas #股票数据
    # 数据太少 macd 计算不准确 
    if len(datas) < 50:
        return

    df1['diff'], df1['dea'], df1['macd'] = talib.MACD(df1['close'], fastperiod=12, slowperiod=26, signalperiod=9)

    #计算 0 轴附近,40个周期内的macd最大值 * 0.2
    macd0_approx = talib.MAX(np.abs(df1['macd'].values),30)*0.2
    #计算 MACD 高点附近
    macd1_approx = talib.MAX(np.abs(df1['macd'].values),30)*0.7

    for i in range(1,len(df1)):
        dk = df1.iloc[i] #交叉后一个交易周期
        dk1 = df1.iloc[i-1]#交叉交易日

        dif = float("%.2f"% dk1['diff'])
        dea = float("%.2f"% dk1['dea'])
        macd = float("%.2f"% dk1['macd']) * 2

        up,state1 = CrossUp(dk['diff'],dk['dea'],state)
        down,state = CrossDown(dk['diff'],dk['dea'],state)
        if up:
            if 0 < dif and dif < macd1_approx[i] : #0轴上方附近
                print("金叉:",name,code,dk1['date'],dif,dea,macd)
                
            if 0 > dif and -dif < macd1_approx[i] : #0轴下方附近 
                print("金叉:",name,code,dk1['date'],dif,dea,macd)

        if down:
            if 0 < dif and dif > macd1_approx[i] : #0轴高点附近
                print("死叉:",name,code,dk1['date'],dif,dea,macd)

if __name__ == "__main__":
    init_stock_list()
    loop_all(wave_abc) 
