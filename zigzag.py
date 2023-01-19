#!/usr/bin/python3
import matplotlib
#matplotlib.use('Agg') # Bypass the need to install Tkinter GUI framework
 
# Avoid FutureWarning: Pandas will require you to explicitly register matplotlib converters.
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
 
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
 
import pandas as pd

## Klang
from Klang import Kl,Klang 
Klang.Klang_init()
## 

# Load data from CSV file.
##########################
my_headers = ['datetime', 'open', 'high', 'low', 'close', 'volume']
my_dtypes = {'datetime': 'str', 'open': 'float', 'high': 'float', 'low': 'float', 
                                                'close': 'float', 'volume': 'int'}
my_parse_dates = ['datetime']

#
# load stock data by code
# 
Kl.code('sh.600010')
loaded_data = Kl.day_df 
print(loaded_data)

# Convert 'Timestamp' to 'float'.
#   Need time be in float days format - see date2num.
loaded_data['datetime'] = [mdates.date2num(np.datetime64(d)) for d in loaded_data['datetime']]
 
# Re-arrange so that each line contains values of a day: 'date','open','high','low','close'.
quotes = [tuple(x) for x in loaded_data[['datetime','open','high','low','close']].values]
 
 
# Create zigzag trendline.
########################################
# Find peaks(max).
data_x = loaded_data['datetime'].values
data_y = loaded_data['close'].values
peak_indexes = signal.argrelextrema(data_y, np.greater)
peak_indexes = peak_indexes[0]
 
# Find valleys(min).
valley_indexes = signal.argrelextrema(data_y, np.less)
valley_indexes = valley_indexes[0]
 
# Instantiate axes.
(fig, ax) = plt.subplots()
 
# Merge peaks and valleys data points using pandas.
df_peaks = pd.DataFrame({'datetime': data_x[peak_indexes], 'zigzag_y': data_y[peak_indexes]})
df_valleys = pd.DataFrame({'datetime': data_x[valley_indexes], 'zigzag_y': data_y[valley_indexes]})
df_peaks_valleys = pd.concat([df_peaks, df_valleys], axis=0, ignore_index=True, sort=True)
 
# Sort peak and valley datapoints by date.
df_peaks_valleys = df_peaks_valleys.sort_values(by=['datetime'])
 
# Plot zigzag trendline.
ax.plot(df_peaks_valleys['datetime'].values, df_peaks_valleys['zigzag_y'].values, 
                                                        color='red', label="zigzag")
 
# Plot close price line.
ax.plot(data_x, data_y, linestyle='dashed', color='black', label="Close Price", linewidth=1)
 
 
# Customize graph.
##########################
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Prices - ZigZag trendline')
 
# Format time.
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
 
plt.gcf().autofmt_xdate()   # Beautify the x-labels
plt.autoscale(tight=True)
 
plt.legend(loc='best')
plt.grid(True, linestyle='dashed')

plt.show()
 
# Save graph to file.
plt.savefig('argrelextrema-zigzag.png')
