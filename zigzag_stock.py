import pandas as pd
from zigzag_lib import peak_valley_pivots, max_drawdown, compute_segment_returns, pivots_to_modes
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import math
#设置字体 ，显示股票中文名称
matplotlib.rcParams["font.sans-serif"] = ['AR PL UKai CN']

## Klang
from Klang import Kl,Klang 
Klang.Klang_init()
## 

#
# load stock data by code
#
import sys

codename = "sh.600010" 

if len(sys.argv)>1:
    codename = sys.argv[1]
display = 1 
if len(sys.argv)>2:
    display = int(sys.argv[2])

offset = 100
if len(sys.argv)>3:
    offset = int(sys.argv[3])

Kl.code(codename)
print(codename,Kl.cur_name)
loaded_data = Kl.day_df.iloc[offset:] 


# Instantiate axes.
(fig, ax) = plt.subplots( figsize=(21, 7) )

def plot_pivots(X, pivots):
    plt.xlim(0, len(X))
    plt.ylim(X.min()*0.99, X.max()*1.01)
    ax.plot(np.arange(len(X)), X, 'k:', alpha=0.5)
    ax.plot(np.arange(len(X))[pivots != 0], X[pivots != 0], 'k-')
    plt.scatter(np.arange(len(X))[pivots == 1], X[pivots == 1], color='r')
    plt.scatter(np.arange(len(X))[pivots == -1], X[pivots == -1], color='g')


def create_index(pivots):
    index_list = []
    for i in range(0,len(pivots)):
        if pivots[i] != 0:
            index_list.append(i)
    return index_list

def calc_data(data_x):
    pivots = peak_valley_pivots(data_x, 0.02, -0.02)
    plot_pivots(data_x,pivots)    
    return pivots

# 尾部为上升趋势
def pattern_tail_rise():
    if pivots[pv_index[-1]] == 1 and pivots[pv_index[-2]] == -1:
        return 1
    return 0

def pattern_cup_handle():

    if len(pv_index) < 6:
        return 
    close = loaded_data['close'].values
    for i in range(0,len(pv_index)-6):
        x1 = pv_index[i]
        a = pv_index[i+1]
        b = pv_index[i+2]
        c = pv_index[i+3]
        d = pv_index[i+4]
        e = pv_index[i+5]
        # a,c 杯沿差不多高，杯底b，比杯柄低，回调不能超过15%
        if math.isclose(close[a],close[c],abs_tol = 0.1) and \
            close[b] < close[d] and \
            (close[c] - close[d] ) / close[d] < 0.15: 
            return 1

    return 0


pivots = calc_data(loaded_data['close'].values)
pv_index = create_index(pivots)
plt.title( codename + "-" + Kl.cur_name + ' Prices - ZigZag trendline')
plt.grid(True, linestyle='dashed')

if pattern_cup_handle():
    plt.savefig("images/" + codename + "_" + str(len(loaded_data['close'].values))+ "_zigzag.png",dpi=100,bbox_inches='tight')
    
if display :
    plt.show()

