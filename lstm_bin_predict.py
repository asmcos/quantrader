import os
import numpy as np
from matplotlib import pyplot as plt
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import talib

from common.framework import save_df_tohtml



from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM

def DisplayOriginalLabel(values):
  cnt1 = 0
  cnt2 = 0
  for i in range(len(values)):
    if 1 == values[i] :
        cnt1 += 1
    else:
        cnt2 += 1

  print("origin: %.2f %% " % (100 * cnt1 / (cnt1 + cnt2)),len(values))




# 1. 获取数据

df = pd.read_csv('transverse_train2021-12-14.csv')
df = df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]
print(df.columns)

df1 = df[df['date']<'2021-07-15']
df2 = df[df['date']>'2021-07-30']


datas = df1 
prec = 10 #target 百分比
label = datas['target'].values > prec
label2 = df2['target'].values > prec
print(label)

DisplayOriginalLabel(label)


fields = [
     'ma10',
       'ma120', 'ma20', 'ma30', 'ma5', 'ma60', 'rise', 'risevol',
       'dea', 'diff', 'macd' ,'oc' ]

datas = datas.loc[:,fields]
print(datas)

# 准备预测的数据
# 

#使用sklearn数据
#X_train, X_test, y_train, y_test = train_test_split(datas, label, test_size=0.2, random_state=0)
#X2_train, X2_test, y2_train, y2_test = train_test_split(df2, label2, test_size=0.4, random_state=0)


def load_data(stock, target,seq_len, ratio=0.9):
    amount_of_features = len(stock.columns)
    data = stock.values
    sequence_length = seq_len + 1
    result = []
    y_result = []
    for index in range(len(data) - sequence_length):
        result.append(data[index: index + sequence_length])
        y_result.append(target[index+sequence_length])
    result = np.array(result)    # (len(), seq, cols) contains newest date

    row = round(ratio * result.shape[0])
    train = result[:int(row), :]

    x_train = train[:, :-1]      # (len(), 10, 4) drop last row(), because last row contain the label
    y_train = np.array(y_result[:int(row)])

    x_test = result[int(row):, :-1]
    y_test = np.array(y_result[int(row):])

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], amount_of_features))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], amount_of_features))

    return [x_train, y_train, x_test, y_test]

sequence_len = 25
X_train, y_train, X_test, y_test = load_data(datas,label, sequence_len)


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
    model.add(Dense(16,kernel_initializer='uniform',activation='relu'))
    model.add(Dense(1,kernel_initializer='uniform',activation='linear'))
    model.compile(loss='mse',optimizer='adam',metrics=['accuracy'])
    return model


model = build_model()
print(X_train.shape)
history = model.fit(
    X_train,
    y_train,
    batch_size=512,
    epochs=100)

# 对测试集进行预测

"""
ans = model.predict_proba(X2_test.loc[:,fields])
y_pred = model.predict(X2_test.loc[:,fields])
accuracy = accuracy_score(y2_test, y_pred)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
print(y_pred)
print(ans)

pcnt1 = 0
pcnt2 = 0
for i in range(len(y_pred)):

    if y_pred[i] == 0 or ans[i][1] < 0.7 :
        continue

    print(ans[i][1],X2_test['date'].values[i],X2_test['code'].values[i])
    if y_pred[i] == y2_test[i]:
        pcnt1 += 1
    else:
        pcnt2 += 1
DisplayOriginalLabel(y2_test)
print("Accuracy: %.2f %% " % (100 * pcnt1 / (pcnt1 + pcnt2)))

plot_importance(model)
plt.show()


png = xgb.to_graphviz(model,num_trees=0)
png.view("stock.png")


preds = pd.read_csv('transverse_pred'+end+'.csv')
preds1 = preds.loc[:,fields]
y_pred = model.predict(preds1)
ans = model.predict_proba(preds1)
pred_list = []
for i in range(0,len(y_pred)):
    if y_pred[i] == 1 and ans[i][1] > 0.6: #and preds['日期'].values[i] > '2021-11-01':
        print(preds['name'].values[i],preds['code'].values[i],preds['日期'].values[i],y_pred[i])
        pred_list.append([preds['name'].values[i],preds['code'].values[i],preds['日期'].values[i]])

df_pred = pd.DataFrame(pred_list,columns=['name','code','日期'])

print('file://'+os.getcwd()+ '/' + './datas/tree_pred'+end+'.html' )
save_df_tohtml('./datas/tree_pred'+end+'.html',df_pred)



#显示
#plot_importance(model)
#plt.show()
"""
