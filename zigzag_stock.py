import pandas as pd
from zigzag_lib import peak_valley_pivots, max_drawdown, compute_segment_returns, pivots_to_modes
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import math
#设置字体 ，显示股票中文名称
matplotlib.rcParams["font.sans-serif"] = ['AR PL UKai CN']

## Klang
from Klang import Kl,Klang,APPROX 
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

# 杯和柄模式
def pattern_cup_handle():
    if len(pv_index) < 6:
        return 0 
    close = loaded_data['close'].values
    ret = 0
    for i in range(0,len(pv_index)-6):
        x1 = pv_index[i]
        a = pv_index[i+1]
        b = pv_index[i+2]
        c = pv_index[i+3]
        d = pv_index[i+4]
        e = pv_index[i+5]
        # a,c 杯沿差不多高，杯底b，比杯柄低，回调不能超过杯底部1/3
        ab = close[a] - close[b]
        cb = close[c] - close[b]
        cd = close[c] - close[d]
        if pivots[x1] == -1 and abs(ab-cb)/cb < 0.15 and \
            close[b] < close[d] and \
            cb / 3 > cd: 
            ax.text(a+1,close[a],"<-A")
            ax.text(c+1,close[c],"<-C")
            ax.annotate('', xy=(c, close[c]),xytext=(b, close[b]),\
                arrowprops=dict(color='blue', arrowstyle='-',connectionstyle="arc3,rad=0.4"))
            ax.annotate('', xy=(b, close[b]),xytext=(a, close[a]),\
                arrowprops=dict(color='blue', arrowstyle='-',connectionstyle="arc3,rad=0.4"))
            ret = 1

    return ret

# W 底部
def pattern_w_bottom():
    if len(pv_index) < 5:
        return 0 
    ret = 0
    close = loaded_data['close'].values
    for i in range(0,len(pv_index)-5):
        a = pv_index[i]
        b = pv_index[i+1]
        c = pv_index[i+2]
        d = pv_index[i+3]
        e = pv_index[i+4]
        ab = close[a] - close[b]
        ad = close[a] - close[d]

        # b,d 为双底，a，e为顶
        if pivots[a] == 1 and APPROX(ab,ad,0.05) and \
            ab / close[b] > 0.2 :
            ax.text(b+1,close[b],"<-B")
            ax.text(d+1,close[d],"<-D")
            ret = 1
    return ret

# 三次底部
def pattern_triple_bottom():
    if len(pv_index) < 6:
        return 0 
    ret = 0
    close = loaded_data['close'].values
    for i in range(0,len(pv_index)-6):
        a = pv_index[i]
        b = pv_index[i+1]
        c = pv_index[i+2]
        d = pv_index[i+3]
        e = pv_index[i+4]
        f = pv_index[i+5]
        ab = close[a] - close[b]
        ad = close[a] - close[d]
        af = close[a] - close[f]

        # b,d,f 为三底，a，e为顶
        if pivots[a] == 1 and APPROX(ab,ad,0.05) and \
            APPROX(ab,af,0.05) and ab / close[b] > 0.2 :
            ax.text(b+1,close[b],"<-B")
            ax.text(d+1,close[d],"<-D")
            ax.text(f+1,close[d],"<-F")
            ret = 1
    return ret
 
pivots = calc_data(loaded_data['close'].values)
pv_index = create_index(pivots)

if pattern_triple_bottom() == 1:
    plt.title( codename + "-" + Kl.cur_name + ' Prices - ZigZag trendline')
    plt.grid(True, linestyle='dashed')
    plt.savefig("images/" + codename + "_" + str(len(loaded_data['close'].values))+ "_zigzag.png",dpi=100,bbox_inches='tight')
    
if display :
    plt.show()

