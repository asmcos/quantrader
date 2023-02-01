import pandas as pd
from zigzag_lib import peak_valley_pivots, max_drawdown, compute_segment_returns, pivots_to_modes
import numpy as np
import matplotlib.pyplot as plt


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



def plot_pivots(X, pivots):
    plt.xlim(0, len(X))
    plt.ylim(X.min()*0.99, X.max()*1.01)
    plt.plot(np.arange(len(X)), X, 'k:', alpha=0.5)
    plt.plot(np.arange(len(X))[pivots != 0], X[pivots != 0], 'k-')
    plt.scatter(np.arange(len(X))[pivots == 1], X[pivots == 1], color='g')
    plt.scatter(np.arange(len(X))[pivots == -1], X[pivots == -1], color='r')



pivots = peak_valley_pivots(loaded_data['close'].values, 0.03, -0.03)
plot_pivots(loaded_data['close'].values,pivots)


plt.show()

