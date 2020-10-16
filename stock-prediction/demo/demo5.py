import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM,Dense
import matplotlib.pyplot as plt

from keras.models import load_model

nsteps = 30


##################
# 1. 加载股票数据
##################

import tushare as ts

#青岛啤酒
code = '600600' 
start  = '2019-04-14'

df = ts.get_k_data(code,start=start,index=False,ktype='D')

df = df.set_index('date').sort_index(ascending=True)

df = df['close']

#############
# 2. 处理数据
#############

array = df.values.reshape(df.shape[0],1)
from sklearn.preprocessing import MinMaxScaler
scl = MinMaxScaler()
array = scl.fit_transform(array)

#split in Train and Test
division = len(array) - 2 * nsteps
array_test = array[division:]
array_train = array[:division]

#Get the data and splits in input X and output Y, by spliting in `n` past days as input X 
#and `m` coming days as Y.
def processData(data, nsteps,jump=1):
    X,Y = [],[]
    for i in range(0,len(data) - nsteps , jump):
        X.append(data[i:(i+nsteps)])
        Y.append(data[(i+1):(i+1+nsteps)])
    return np.array(X),np.array(Y)

X,y = processData(array_train,nsteps)
y = np.array([list(a.ravel()) for a in y])

from sklearn.model_selection import train_test_split
X_train, X_validate, y_train, y_validate = train_test_split(X, y, test_size=0.20, random_state=42)



######################
# 建立模型,训练数据
######################

NUM_NEURONS_FirstLayer = 50
NUM_NEURONS_SecondLayer = 30
EPOCHS = 20

#input_shape:(batch_size, timesteps, input_dim)
#default None = batch_size  = len(X) 
# input_shape(timesteps,dim) = (None,timesteps,input_dim) = (len(X),timesteps,input_dim)

#Build the model
model = Sequential()
model.add(LSTM(NUM_NEURONS_FirstLayer,input_shape=(nsteps,1), return_sequences=True))
model.add(LSTM(NUM_NEURONS_SecondLayer,input_shape=(NUM_NEURONS_FirstLayer,1)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')

history = model.fit(X_train,y_train,epochs=EPOCHS,validation_data=(X_validate,y_validate),shuffle=True,batch_size=2, verbose=2)


##################
# 预测
##################


Xtrain,ytrain = processData(array_train,nsteps)
Xtest,ytest = processData(array_test,nsteps)

Xtrain = model.predict(Xtrain)
Xtrain = Xtrain.ravel()

Xpred = model.predict(Xtest)
Xpred = Xpred.ravel()
print(scl.inverse_transform(Xtest[-1].reshape(-1, 1)))
print(scl.inverse_transform(Xpred.reshape(-1, 1)))
y = np.concatenate((ytrain, ytest), axis=0)

plt.figure(figsize = (15,10))

"""
# Data in Train/Validation
plt.plot([x for x in range(nsteps+leftover, len(Xtrain)+nsteps+leftover)], scl.inverse_transform(Xtrain.reshape(-1,1)), color='r', label='Train')
# Data in Test
plt.plot([x for x in range(nsteps +leftover+ len(Xtrain), len(Xtrain)+len(Xtest)+nsteps+leftover)], scl.inverse_transform(Xtest.reshape(-1,1)), color='y', label='Test')

#Data used
plt.plot([x for x in range(nsteps+leftover, nsteps+leftover+len(Xtrain)+len(Xtest))], scl.inverse_transform(y.reshape(-1,1)), color='b', label='Target')

"""
plt.legend(loc='best')
#plt.show()
