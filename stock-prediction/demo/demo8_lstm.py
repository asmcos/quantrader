#https://github.com/ICEJM1020/LSTM_Stock/blob/master/Code/LSTM_stock.ipynb
import tushare as ts
import pandas as pd

class StockData(object):
    def __init__(self):
        self.pro = ts.pro_api('191f98ec62b6953e19200384e71e983c113f8bd1ac12d5e787323844')

    def get_data(self,code, start='19900101', end='20190901'):
        stock_code = self.tran_code(code)
        return self.pro.query('daily', ts_code=stock_code, start_date=start, end_date=end)

    def tran_code(self,code):
        if code[0:1] == '6':
            return code + '.SH'
        else:
            return code + '.SZ'

from matplotlib import pyplot as plt
from matplotlib.pyplot import MultipleLocator
def plot_stock(stock_data):
    temp_data = stock_data[['close','high','low','trade_date']]
    temp_data = temp_data.iloc[-30:]
    temp_data.set_index(['trade_date'], inplace=True)
    plt.plot(temp_data['close'],color='orange', label='Close Price')
    ax=plt.gca()
    x_major_locator=MultipleLocator(5)
    ax.xaxis.set_major_locator(x_major_locator)
    plt.xticks(rotation=60)
    plt.legend(loc='best')
    plt.show()

stock = StockData()
data = stock.get_data("600519",start="20100101",end='20201021')

# 从
data_test = stock.get_data("600519", start = '20190901',end = '20191201')
# 按照时间进行排序
data.sort_values("trade_date", inplace=True)
data = data.reset_index()
#plot_stock(data)
print(data.shape)
data.tail()

from sklearn import preprocessing as process
# 在数据分析之前先对所有的数据进行分析
# 后两项特征的数量级远大于其他项

X = data.loc[:,'open':'amount']
# X = data.loc[:,'close':'vol']
# X = X.drop(columns = ['pct_chg','pre_close'])
X = X.values
# y = data["close"].values
print(X.shape)

plt.plot(X.min(axis=0),'v',label='min')
plt.plot(X.max(axis=0),'^',label='max')
plt.yscale('log')
plt.legend(loc='best', fontsize = 14)
plt.xlabel('features', fontsize = 14)
plt.ylabel('feature magnitude', fontsize = 14)


# 训练集数据处理
# _max = data['close'].max()
# _min = data['close'].min()
# scaler = process.MinMaxScaler(feature_range=(_min, _max))
# scaler = process.MinMaxScaler(feature_range=(-1, 1))
scaler = process.StandardScaler()
scaler.fit(X)
X_scalerd = scaler.transform(X)
y = pd.DataFrame(X_scalerd)[3].values

temp_data = pd.DataFrame(X_scalerd)
temp_data = temp_data.iloc[-30:]

"""
plt.plot(temp_data[3],color='orange', label='Close Price')
ax=plt.gca()
x_major_locator=MultipleLocator(5)
ax.xaxis.set_major_locator(x_major_locator)
plt.xticks(rotation=60)
plt.legend(loc='best')
plt.show()
"""

print(X_scalerd.shape, y.shape)

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM
from keras.models import load_model
from keras.layers import RepeatVector
import keras

# 用t天的数据预测t+1天的，所以把y前移
# X有一个会多出来，所以删掉X的最后一个和y的第一个
import numpy as np

# X_train = X_pca
X_train = pd.DataFrame(X_scalerd)[[3,5,7]].values

X_train = np.delete(X_train, -1, axis=0)
y_train = np.delete(y, [1])


X_train = X_train.reshape(X_train.shape[0],1, X_train.shape[1])
y_train = y_train.reshape(y_train.shape[0],1, 1)
print(X_train.shape, y_train.shape)

model = Sequential()

model.add(LSTM(128, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True))

model.add(Dense(16,kernel_initializer="uniform",activation='relu'))        
model.add(Dense(1,kernel_initializer="uniform",activation='linear'))
 
adam = keras.optimizers.Adam(decay=0.2)
model.compile(loss='mae', optimizer='adam', metrics=['accuracy'])
model.summary()

# 训练模型
print(X_train.shape, y_train.shape)
history = model.fit(X_train, y_train, epochs=100, verbose=2, shuffle=False)

model.save("1-1.h5")

# plot history
plt.plot(history.history['loss'], label='loss')
#plt.plot(history.history['accuracy'], label='train')
plt.legend()
plt.show()

model = load_model('1-1.h5')

predictes_stock_price = model.predict(X_train)

predictes_stock_price = predictes_stock_price.reshape(predictes_stock_price.shape[0])
y_train = y_train.reshape(y_train.shape[0])

plt.plot(predictes_stock_price[-30:], label='pre', color='red')
plt.plot(y_train[-30:], label='ori', color='blue')
plt.legend()


# 测试集数据处理
X_test = data_test.loc[:,'close':'vol']
X_test = X_test.drop(columns = ['change','pct_chg'])
X_test = X_test.values

scaler = process.StandardScaler()
scaler.fit(X_test)
X_test_scalerd = scaler.transform(X_test)
y_test = pd.DataFrame(X_test_scalerd)[0].values

X_test_scalerd = X_test_scalerd.reshape(X_test_scalerd.shape[0],1, X_test_scalerd.shape[1])

pre_test = model.predict(X_test_scalerd)

pre_test = pre_test.reshape(pre_test.shape[0])

plt.plot(pre_test, label='pre', color='red')
plt.plot(y_test, label='ori', color='blue')
plt.legend()
plt.show()
