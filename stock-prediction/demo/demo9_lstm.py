import tushare as ts
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime
import sys

####################
#1. 获取股票数据
####################
today = datetime.now()
end = str(today.year) + str(today.month) + str(today.day)

# 茅台,青岛啤酒600600
code = '600519'
if len(sys.argv) > 1:
    code = sys.argv[1]

df=ts.get_hist_data(code,start='2018-07-09')
df1 = df['close']
df1 = df1.sort_index(ascending=True)

print(df1)
#for i in range(0,len(df1)): 
#    df1[i] = i 

#######################
# 2. 处理数据
#######################
time_step = 100
epochs = 500
pred_days = 5

from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler(feature_range=(0,1))
df1=scaler.fit_transform(np.array(df1).reshape(-1,1))


##splitting dataset into train and test split
training_size=int(len(df1)*0.75)
test_size=len(df1)-training_size
train_data,test_data=df1[0:training_size,:],df1[training_size:,:1]

# convert an array of values into a dataset matrix
def create_dataset(dataset, time_step=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-time_step-pred_days):
        a = dataset[i:(i+time_step), 0]   ###i=0, 0,1,2,3-----99   100 
        dataX.append(a)
        dataY.append(dataset[i + time_step:i+time_step+pred_days, 0])
    return np.array(dataX), np.array(dataY)

# reshape into X=t,t+1,t+2,t+3 and Y=t+4
X, y = create_dataset(df1, time_step)
X_test, ytest = create_dataset(test_data, time_step)

# 乱序
#
from sklearn.model_selection import train_test_split
X_train, X_validate, y_train, y_validate = train_test_split(X, y, test_size=0.20, random_state=42)


# reshape input to be [samples, time steps, features] which is required for LSTM
X_test = X_test.reshape(X_test.shape[0],X_test.shape[1] , 1)
X_train = X_train.reshape(X_train.shape[0],X_train.shape[1] , 1)

### Create the Stacked LSTM model
# 3. 建立LSTM 模型
###########################
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM


model=Sequential()
model.add(LSTM(50,return_sequences=True,input_shape=(time_step,1)))
model.add(LSTM(50,return_sequences=True))
model.add(LSTM(50))
model.add(Dense(pred_days))
model.compile(loss='mean_squared_error',optimizer='adam')

#model.summary()

#############
# 4. 训练
#############
model.fit(X_train,y_train,validation_data=(X_test,ytest),epochs=epochs,batch_size=64,verbose=1)


### Lets Do the prediction and check performance metrics
#
# 5. 预测
##############

test_predict=model.predict(X_test)

##Transformback to original form
test_predict=scaler.inverse_transform(test_predict)

print(test_predict)

