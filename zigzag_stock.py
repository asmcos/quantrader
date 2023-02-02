import pandas as pd
from zigzag_lib import peak_valley_pivots, max_drawdown, compute_segment_returns, pivots_to_modes
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

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
    plt.scatter(np.arange(len(X))[pivots == 1], X[pivots == 1], color='g')
    plt.scatter(np.arange(len(X))[pivots == -1], X[pivots == -1], color='r')


plt.title( codename + "-" + Kl.cur_name + ' Prices - ZigZag trendline')
plt.grid(True, linestyle='dashed')

def calc_data(data_x):
    pivots = peak_valley_pivots(data_x, 0.02, -0.02)
    plot_pivots(data_x,pivots)
    plt.savefig("images/" + codename + "_" + str(len(data_x))+ "_zigzag.png",dpi=100,bbox_inches='tight')

calc_data(loaded_data['close'].values)

if display :
    plt.show()

