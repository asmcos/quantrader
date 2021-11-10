import os
import xgboost as xgb
import numpy as np
from xgboost import plot_importance
from matplotlib import pyplot as plt
import requests
import pandas as pd

#1. 准备训练数据 500组，10个维度
# numpy 数据例子
data = np.random.rand(500, 10)  # 5 entities, each contains 10 features


# stock data 例子
end = '2021-11-09'
hostname= "http://klang.zhanluejia.net.cn"
def get_stock_data(code):
    try:
        json = requests.get(hostname+"/dayks",
            params={"code":code,"end":end,"limit":200},timeout=1000).json()
    except:
        json = requests.get(hostname+"/dayks",
            params={"code":code,"end":end,"limit":200},timeout=1000).json()

    df = pd.json_normalize(json)

    if len(df) < 1:
       return []

    df = df.drop(columns=['_id','codedate','id'])
    datas = df.sort_values(by="date",ascending=True)

    datas['datetime'] = datas['date']
    close  = datas['close'].iloc[-1]
    volume = datas['volume'].iloc[-1]
    turn   = datas['turn'].iloc[-1]
    try :
        datas['hqltsz'] = float(volume) * float(close)/ float(turn) / 1000000
    except:
        datas['hqltsz'] = 0.0001 #没有交易量
    datas.rename(columns={'volume':'vol'},inplace = True)
    datas = datas.loc[:,['close','high', 'low','vol','turn']]                                                                                                                                                   
    return datas

# 600111 北方稀土
data = get_stock_data('sh.600111')
print(data)

#2. 准备训练的标签
# numpy 例子
label = np.random.randint(2, size=len(data))  # binary target

# 股票例子
def get_label(data):
    label = []
    for i in range(1,len(data)):
        if data['close'].iloc[i] > data['close'].iloc[i-1]:
            label.append(1)
        else:
            label.append(0)
    return label

label = get_label(data)
dtrain = xgb.DMatrix(data.loc[len(data)-1:1,], label=label)

# 准备预测的数据
# 
dtest = xgb.DMatrix(data)

#参数
param = {'booster': 'gbtree','max_depth': 2, 'eta': 1, 'objective': 'binary:logistic'}
param['eval_metric'] = 'auc'
#训练
num_round = 3
bst = xgb.train(param, dtrain, num_round)

#预测
print('start testing predict the leaf indices')
leafindex = bst.predict(dtest,pred_leaf=True) #, ntree_limit=2, pred_leaf=True)
print(leafindex.shape)
print(leafindex)

png = xgb.to_graphviz(bst,num_trees=0)
png.view("stock.png")
#显示
#plot_importance(bst)
plt.show()
