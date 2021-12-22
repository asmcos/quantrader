#
# keras-2.7.0,tensorflow 2.7.0
# 使用lstm做股票二分类验证
#

import os
import numpy as np
from matplotlib import pyplot as plt
import requests
import pandas as pd
import talib
import datetime

from common.framework import save_df_tohtml


from tensorflow.keras import Input
from tensorflow.keras.models import Sequential,Model,load_model
from tensorflow.keras.layers import Dense, Dropout, Activation,LSTM,Bidirectional
import tensorflow as tf
import json
from tensorflow.keras.layers import Attention,GlobalMaxPooling1D,Concatenate

def DisplayOriginalLabel(values):
  cnt1 = 0
  cnt2 = 0
  for i in range(len(values)):
    if 1 == values[i] :
        cnt1 += 1
    else:
        cnt2 += 1

  print("origin: %.2f %% " % (100 * cnt1 / (cnt1 + cnt2)),len(values))



df_all = []
# 1. 获取数据
def load_data_fromfile(filename):
    global df_all

    content = open(filename).read()
    df_dict = json.loads(content)
    for k in df_dict.keys():
        df = pd.read_json(df_dict.get(k)) 
        df = df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]
        df_all.append(df)


load_data_fromfile('lstm_train2021-12-21.csv')

print(df_all[0].columns)



# 准备预测的数据
# 

sequence_len = 40
prec = 10 #target 百分比
fields = [
         'ma10',
         'ma120', 'ma20', 'ma30', 'ma5', 'ma60', 'rise', 'risevol',
         'dea', 'diff', 'macd' ,'oc','close']

X_train = []
y_train = []
X_test = []
y_test = []

def load_data(df, seq_len, ratio=0.9):

    df1 = df[df['date']<'2021-07-15']
    df2 = df[df['date']>'2021-07-16']

    label1 = df1['target'].values > prec
    label2 = df2['target'].values > prec

    datas1 = df1.loc[:,fields]
    datas2 = df2.loc[:,fields]

    sequence_length = seq_len

    if len(datas1) <= sequence_length or len(datas2) <= sequence_length:
        return 

    for index in range(len(datas1) - sequence_length):
         X_train.append(datas1[index: index + sequence_length].values)
         y_train.append(label1[index+sequence_length-1])

    for index in range(len(datas2) - sequence_length):
         X_test.append(datas2[index: index + sequence_length].values) 
         y_test.append(label2[index+sequence_length-1])



for df in df_all[:100]:
    load_data(df,sequence_len)

X_train = np.array(X_train)
X_train = np.reshape(X_train,(X_train.shape[0],X_train.shape[1],len(fields)))
y_train = np.array(y_train)

X_test = np.array(X_test)
X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],len(fields)))


def build_model():
    d = 0.2
    model = Sequential()

    # inputs: A 3D tensor with shape `[batch, timesteps, feature]`.
    # 输入的数据格式 是 总尺寸，时间步长，这里是 sequence_len, feature，特征维度
    # now model.output_shape == (None, 128)
    model.add(LSTM(128,  return_sequences=True))
    model.add(Dropout(d))

    # for subsequent layers, no need to specify the input size:
    model.add(LSTM(64, return_sequences=False))
    model.add(Dropout(d))

    # fully connected layer 
    model.add(Dense(16,activation='relu'))
    # 输入 1 维度 0，1
    model.add(Dense(1,activation='sigmoid'))

    lossfn = tf.keras.losses.BinaryCrossentropy(
        from_logits=False,
        label_smoothing=0.0,
        axis=-1,
        reduction="auto",
        name="binary_crossentropy",
    )
    # 二分类
    model.compile(optimizer='rmsprop',
              loss=lossfn, metrics=['accuracy'])
    return model

time_steps = X_train.shape[1]
input_dim  = X_train.shape[2]

print(time_steps,input_dim)

def build_model2():
    d = 0.2

    model_input = Input(shape=(time_steps, input_dim))
    x = Bidirectional(LSTM(128, return_sequences=True))(model_input)
    x = Dropout(d)(x)
    #x = Bidirectional(LSTM(64, return_sequences=False))(x)
    #x = Dropout(d)(x)
    a = Attention()([x,x])
    out1 = GlobalMaxPooling1D()(x)
    out2 = GlobalMaxPooling1D()(a)
    merge = Concatenate()([out1,out2])
    x = Dense(16,activation='relu')(merge)
    x = Dense(1,activation='sigmoid')(x)

    model = Model(model_input, x)

    lossfn = tf.keras.losses.BinaryCrossentropy(
        from_logits=False,
        label_smoothing=0.0,
        axis=-1,
        reduction="auto",
        name="binary_crossentropy",
    )
    # 二分类
    model.compile(optimizer='rmsprop',
              loss=lossfn, metrics=['accuracy'])
    return model

model = build_model2()

log_dir="logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

#X = pd.DataFrame(data = X_train, columns = fields)

model.fit(X_train,y_train,batch_size=200,
        epochs=2,callbacks=[tensorboard_callback])

y_pred = model.predict(X_test)

# 对测试集进行预测
# print(tf.greater(y_pred, .5))
print(y_pred)

pcnt1 = 0
pcnt2 = 0
for i in range(len(y_pred)):
     if y_pred[i][0] < 0.6 :
        continue

     if y_test[i] == True :
        pcnt1 += 1
     else:
        pcnt2 += 1

DisplayOriginalLabel(y_test)
if pcnt1+pcnt2 > 0:
    print("Accuracy: %.2f %% " % (100 * pcnt1 / (pcnt1 + pcnt2)),pcnt1 + pcnt2)



