import numpy as np
import matplotlib.pyplot as plt
import math, time, itertools, datetime
import pandas as pd

from operator import itemgetter
from sklearn.metrics import mean_squared_error
from math import sqrt

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM

def get_stock_data(normalized=0):
    def get_ma_day(df, index, days):
        #return np.round(df[index].rolling(window = days, center = False).mean(), 2)
        # df need to be a DataFrame
        if not isinstance(df, pd.DataFrame):
            return None
        col = df[index]
        l = len(col)
        return [ col[i-days+1:i+1].mean() for i in range(l)] # first days-1 will be None because of the indexing handling

    def get_price_change(df):
        close_price = df['close']
        return  np.log(close_price) - np.log(close_price.shift(1))
    
    import baostock as bs
    bs.login()

    #青岛啤酒
    code = 'sh.600600'
    start  = '2019-04-14'

    rs = bs.query_history_k_data_plus(code, 'date,open,high,low,close,volume,code,turn', start_date=start,
                                      frequency='d' )
    df = rs.get_data()
    if len(df) < 2:
        return

    df['close'] = df['close'].astype(np.float32)
    df['volume'] = df['volume'].astype(np.float32)
    print(df.columns)
    df = df.set_index('date').sort_index(ascending=True)

	#df = df['close']


    # Get
    #stocks = pd.read_csv(url, header=0, names=col_names) 
    # reverse cuz it was backward
    stocks = df
    stocks = stocks[::-1]
    
    stocks['MA5'] = get_ma_day(stocks,'close',5)
    stocks['MA10']= get_ma_day(stocks,'close',10)
    stocks['MA20']= get_ma_day(stocks,'close',20)

    stocks['VMA5'] = get_ma_day(stocks,'volume',5)
    stocks['VMA10'] = get_ma_day(stocks,'volume',10)
    stocks['VMA20'] = get_ma_day(stocks,'volume',20)

    stocks['price_change'] = get_price_change(stocks)
    #print(stocks.head(10))
    
    # Drop
    #print(stocks)
    stocks = stocks.drop(columns=['code'],axis=1)
    
    # Normalize
    df = pd.DataFrame(stocks)
    if normalized:
        df = df/df.mean() -1
    
    # drop first 19 NaN rows caused by MA/VMA
    return df[20:]


df = get_stock_data(normalized=1)


def load_data(stock, seq_len, ratio=0.9):
    amount_of_features = len(stock.columns)
    data = stock.values
    sequence_length = seq_len + 1
    result = []
    for index in range(len(data) - sequence_length):
        result.append(data[index: index + sequence_length])

    result = np.array(result)    # (len(), seq, cols) contains newest date
    
    row = round(0.9 * result.shape[0])
    train = result[:int(row), :]
    #np.random.shuffle(train)
    
    x_train = train[:, :-1]      # (len(), 10, 4) drop last row(), because last row contain the label
    y_train = train[:, -1][:,2] # with last row, and only keep "close" column @ [Open, High,"Close", Volume,...]
    x_test = result[int(row):, :-1]
    y_test = result[int(row):, -1][:,2]

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], amount_of_features))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], amount_of_features))  
   
    x_train = x_train.astype('float64') 
    y_train = y_train.astype('float64') 
    x_test = x_test.astype('float64') 
    y_test = y_test.astype('float64') 
    return [x_train, y_train, x_test, y_test]

sequence_len = 25
X_train, y_train, X_test, y_test = load_data(df, sequence_len)

print(X_train.shape)

def build_model(layers):
    d = 0.2
    model = Sequential()
    
    # now model.output_shape == (None, 128)
    model.add(LSTM(128, input_shape=(layers[1], layers[0]), return_sequences=True))
    model.add(Dropout(d))
    
    # for subsequent layers, no need to specify the input size:
    model.add(LSTM(64, return_sequences=False))
    model.add(Dropout(d))
    
    # fully connected layer
    model.add(Dense(16,kernel_initializer='uniform',activation='relu'))        
    model.add(Dense(1,kernel_initializer='uniform',activation='linear'))
    model.compile(loss='mse',optimizer='adam',metrics=['accuracy'])
    return model


model = build_model([X_train.shape[-1],sequence_len])

history = model.fit(
    X_train,
    y_train,
    batch_size=512,
    epochs=500,
    validation_split=0.1,
    verbose=0)

"""
trainScore = model.evaluate(X_train, y_train, verbose=0)
print('Train Score: %.2f MSE (%.2f RMSE)' % (trainScore[0], math.sqrt(trainScore[0])))

testScore = model.evaluate(X_test, y_test, verbose=0)
print('Test Score: %.2f MSE (%.2f RMSE)' % (testScore[0], math.sqrt(testScore[0])))
"""

diff=[]
ratio=[]
p = model.predict(X_test)
for u in range(len(y_test)):
    pr = p[u][0]
    ratio.append((y_test[u]/pr)-1)
    diff.append(abs(y_test[u]- pr))


plt.plot(p,color='red', label='prediction')
#plt.plot(ratio, color='black', label='ratio')
#plt.plot(diff, color='purple', label='diff')
plt.plot(y_test,color='blue', label='y_test')
plt.legend(loc='best')
plt.show()
