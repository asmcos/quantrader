import pandas as pd
import numpy as np
import talib as talib
import tushare as ts
from matplotlib import rc
rc('mathtext', default='regular')
import sys

code = "600519"
if len(sys.argv) > 1:
	code = sys.argv[1]

dw = ts.get_k_data(code)
close = dw.close.values
dw['macd'], dw['macdsignal'], dw['macdhist'] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

#dw[['close','macd','macdsignal','macdhist']].plot()
for i in range(0,len(dw['open'])):
	print(i,dw['date'][i],dw['open'][i],dw['macd'][i],dw['macdsignal'][i],dw['macdhist'][i])
