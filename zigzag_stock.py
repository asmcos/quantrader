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

Kl.code(codename)
print(codename,Kl.cur_name)
loaded_data = Kl.day_df 

#datetime types
loaded_data['datetime'] = pd.to_datetime(loaded_data['datetime'])

# Instantiate axes.
(fig, ax) = plt.subplots( figsize=(21, 7) )

def plot_pivots(X, pivots):
    plt.xlim(0, len(X))
    plt.ylim(X.min()*0.99, X.max()*1.01)
    ax.plot(np.arange(len(X)), X, 'k:', alpha=0.5)
    ax.plot(np.arange(len(X))[pivots != 0], X[pivots != 0], 'k-')
    plt.scatter(np.arange(len(X))[pivots == 1], X[pivots == 1], color='g')
    plt.scatter(np.arange(len(X))[pivots == -1], X[pivots == -1], color='r')



pivots = peak_valley_pivots(loaded_data['close'].values, 0.03, -0.03)
plot_pivots(loaded_data['close'].values,pivots)

plt.title( codename + "-" + Kl.cur_name + ' Prices - ZigZag trendline')
plt.savefig("images/" + codename+"_zigzag.png",dpi=200,bbox_inches='tight')

if display :
    plt.show()

