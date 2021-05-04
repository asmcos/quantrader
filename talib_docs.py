#
# python3 talib demo使用用例
#
# talib 是非常有价值的股票计算分析工具
# 有很多写好的公式可以直接使用
# 本例子源代码在github上
# https://github.com/asmcos/quantrader

import talib
from common.framework import *

# 1. 获取股票的K线，代码和日期输入正确就行
#    例如：sz.000100 TCL
#    大家可以用常见的 python库就可以，baostock，tushare
#    例子中是我自己的网站的数据
#df = get_day_data("TCL",'sz.000100','2021-04-18','')

df = get_day_data("隆基",'sh.601012','2021-04-18','')
#########
"""
5 2021-04-23
   close       code        date   high    low  name   open    turn    volume
0  89.61  sh.601012  2021-04-19  90.16  84.77  隆基股份  85.90  1.9453  75210468
1  92.40  sh.601012  2021-04-20  94.50  88.86  隆基股份  89.60  2.1712  83943905
2  92.44  sh.601012  2021-04-21  95.57  90.66  隆基股份  94.00  2.2525  87086859
3  90.61  sh.601012  2021-04-22  93.88  88.38  隆基股份  93.51  1.5086  58328043
4  91.99  sh.601012  2021-04-23  93.30  90.70  隆基股份  90.70  1.1907  46036028
"""
#########
print(df)

closes = df['close']

# 2. max value 
#  max,min 使用方法类似
# 所以我写了一个例子
max1 = talib.MAX(closes,len(closes))
"""
0      NaN
1      NaN
2      NaN
3      NaN
4    92.44
含义就是 第5天的收盘价最高（从0开始计数的）
"""
print(max1)

# 3. SMA
# N日平均值
# MA  国际上SMA=MA
# 国内SMA有自己的算法不一样

sma = talib.SMA(closes.values,3)
print("3日平均:\n",sma)
#ma = talib.MA(closes.values,3)
# 结果sma = ma 不再重复执行


# 4. EMA
# 指数移动平均线
ema3 = talib.EMA(closes,3)
print("ema3:\n",ema3)

# 双均
# talib.DEMA(closes, timeperiod = 30)
# 考夫曼
# talib.KAMA(closes, timeperiod = 30)
# 三重指数移动平均线
# talib.TEMA(closes, timeperiod=30)

# 阶段中点价格
# 
#midpoint = talib.MIDPOINT(closes,3)

# 移动加权平均
# talib.WMA(closes, timeperiod = 30)

# 5.布林线BBANDS
# 参数说明：talib.BBANDS(close, timeperiod, matype)
# close:收盘价；timeperiod:周期；matype:平均方法(bolling线的middle线 = MA，用于设定哪种类型的MA)
# MA_Type: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3 (Default=SMA)
upper, middle, lower = talib.BBANDS(closes,5,matype = talib.MA_Type.EMA)
print("布林线: ",upper,middle,lower)

# 6 .macd
# 注意这个日线周期要长，大家可以调整获取k线数据的周期 例如：2021-01-01
# 另外：macd是相对的值，周期不一样，结果也不一样
# 例子，我使用了常见的参数12,26,9
#             diff, dea,       macd=df1['macd']*2
# talib name: macd, macdsignal,macdhist
df1 = get_day_data("隆基",'sh.601012','2020-02-18','')
df1['diff'], df1['dea'], df1['macd'] = talib.MACD(df1['close'], fastperiod=12, slowperiod=26, signalperiod=9)
print("MACD 数据必须大于26天:\n",df1)

print("################\n# 波动量指标\n################")

# 7. ATR：真实波动幅度均值
#
atr = talib.ATR(df1['high'], df1['low'], df1['close'], timeperiod=14)
print("ATR\n",atr)

# 8. AD 量价指标
ad = talib.AD(df1['high'],df1['low'],df1['close'],df1['volume'])
print("AD\n",ad)

# 9. OBV：能量潮
obv = talib.OBV(df1['close'],df1['volume'])
print("OBV\n",obv)



 
