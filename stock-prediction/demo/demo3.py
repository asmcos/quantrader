import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM,Dense
import matplotlib.pyplot as plt

from keras.models import load_model

look_back = 40
forward_days = 10
num_periods = 2
predict_days = 5

import tushare as ts

#青岛啤酒
code = '600600'
start  = '2019-04-14'

df = ts.get_k_data(code,start=start,index=False,ktype='D')

df = df.set_index('date').sort_index(ascending=True)

df = df['close']

array = df.values.reshape(df.shape[0],1)


from sklearn.preprocessing import MinMaxScaler
scl = MinMaxScaler()
array = scl.fit_transform(array)

division = len(array) - num_periods*forward_days

array_test = df.shift(-predict_days).values.reshape(df.shape[0],1)[division-look_back:]

array_test = scl.fit_transform(array_test)

print(array_test)


array_train = array[:division]


def processData(data, look_back, forward_days,jump=1):
    X,Y = [],[]
    for i in range(0,len(data) -look_back -forward_days +1, jump):
        X.append(data[i:(i+look_back)])
        Y.append(data[(i+look_back):(i+look_back+forward_days)])
    return np.array(X),np.array(Y)

X,y = processData(array_train,look_back,forward_days)

y = np.array([list(a.ravel()) for a in y])

from sklearn.model_selection import train_test_split
X_train, X_validate, y_train, y_validate = train_test_split(X, y, test_size=0.20, random_state=42)

NUM_NEURONS_FirstLayer = 50
NUM_NEURONS_SecondLayer = 30
EPOCHS = 50

#Build the model
model = Sequential()
model.add(LSTM(NUM_NEURONS_FirstLayer,input_shape=(look_back,1), return_sequences=True))
model.add(LSTM(NUM_NEURONS_SecondLayer,input_shape=(NUM_NEURONS_FirstLayer,1)))
model.add(Dense(forward_days))
model.compile(loss='mean_squared_error', optimizer='adam')

history = model.fit(X_train,y_train,epochs=EPOCHS,validation_data=(X_validate,y_validate),shuffle=True,batch_size=2, verbose=2)



Xtrain,ytrain = processData(array_train,look_back,forward_days,forward_days)
Xtest,ytest = processData(array_test,look_back,forward_days,forward_days)

Xtrain = model.predict(Xtrain)
Xtrain = Xtrain.ravel()


Xtest = model.predict(Xtest)
Xtest = Xtest.ravel()


y = np.concatenate((ytrain, ytest), axis=0)

plt.figure(figsize = (15,10))

# Data in Train/Validation
plt.plot([x for x in range(look_back, len(Xtrain)+look_back)], scl.inverse_transform(Xtrain.reshape(-1,1)), color='r', label='Train')
# Data in Test
plt.plot([x for x in range(look_back + len(Xtrain), len(Xtrain)+len(Xtest)+look_back)], scl.inverse_transform(Xtest.reshape(-1,1)), color='y', label='Test')

#Data used
#plt.plot([x for x in range(look_back , look_back+len(Xtrain)+len(Xtest))], scl.inverse_transform(y.reshape(-1,1)), color='b', label='Target')
plt.plot([x for x in range(look_back , look_back+len(Xtrain)+len(Xtest))], scl.inverse_transform(array[look_back:]), color='b', label='Target')

plt.legend(loc='best')
plt.show()

