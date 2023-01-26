import requests
from datetime import timedelta,date 
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
import time

data=requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=600104.SHH&outputsize=full&apikey=demo')
data=data.json()
prices_low,prices_high,prices_close=[],[],[]
for i in range(200,1,-1):
  d=date.today()-timedelta(i)
  d=d.strftime("%Y-%m-%d")
  try:
    prices_high.append(float(data["Time Series (Daily)"][d]["2. high"]))
    prices_low.append(float(data["Time Series (Daily)"][d]["3. low"]))
    prices_close.append(float(data["Time Series (Daily)"][d]["4. close"]))
  except:
    continue

prices_low=np.array(prices_low)
prices_high=np.array(prices_high)


local_min_idx=argrelextrema(prices_low,np.less)[0]
local_max_idx=argrelextrema(prices_high,np.greater)[0]
local_min_idx=np.array(local_min_idx)
local_max_idx=np.array(local_max_idx)

local_min=[]
local_max=[]
for loc in local_min_idx:
  local_min.append(prices_low[loc])
for loc in local_max_idx:
  local_max.append(prices_high[loc])
local_min=np.array(local_min)
local_max=np.array(local_max)

for i in range(0,len(local_max)-3):
  (m,c),r,_,_,_= np.polyfit(local_max_idx[i:i+3],local_max[i:i+3],1,full=True)
  if(m<=3 and m>=-3 and (r[0]<20 and r[0]>-20)):
    start=local_max_idx[i+2]
    for k in range(start,start+7):
      if(k<len(prices_close) and prices_close[k]>(k*m+c)):
        plt.figure(figsize=(10,5))
        plt.plot(local_max_idx,m*local_max_idx+c,'m')
        plt.plot(prices_close)
        plt.plot(k,prices_close[k],'bo')
        break

plt.show()

