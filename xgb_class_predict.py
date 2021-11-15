import os
import xgboost as xgb
from xgboost import XGBClassifier
import numpy as np
from xgboost import plot_importance
from matplotlib import pyplot as plt
import requests
import pandas as pd

from sklearn.model_selection import train_test_split

# 1. 获取数据
# stock data 例子
end = '2021-11-15'
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

# 准备预测的数据
# 

#使用sklearn数据
X_train, X_test, y_train, y_test = train_test_split(data.loc[len(data)-1:1,], label, test_size=0.2, random_state=0)


### fit model for train data
model = XGBClassifier(learning_rate=0.1,
                      use_label_encoder=False,
                      booster='gbtree',   #分类树
                      n_estimators=100,         # 树的个数--1000棵树建立xgboost
                      max_depth=5,               # 树的深度
                      min_child_weight = 1,      # 叶子节点最小权重
                      gamma=0.,                  # 惩罚项中叶子结点个数前的参数
                      subsample=0.8,             # 随机选择80%样本建立决策树
                      objective='binary:logistic', # 指定损失函数
                      scale_pos_weight=1,        # 解决样本个数不平衡的问题
                      random_state=27            # 随机数
                      )
model.fit(X_train,
          y_train,
          eval_set = [(X_test,y_test)],
          eval_metric = "auc",
          early_stopping_rounds = 10,
          verbose = True)

# 对测试集进行预测
ans = model.predict(X_test)

png = xgb.to_graphviz(model,num_trees=0)
png.view("stock.png")
print(ans)



#显示
#plot_importance(model)
#plt.show()
