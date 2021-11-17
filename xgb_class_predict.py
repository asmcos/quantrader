import os
import xgboost as xgb
from xgboost import XGBClassifier
import numpy as np
from xgboost import plot_importance
from matplotlib import pyplot as plt
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
import talib

# 1. 获取数据
# stock data 例子
end = '2021-11-17'


datas = pd.read_csv('transverse_train'+end+'.csv')
label = datas['是否涨幅10%']
print(label.values)

fields = ['5日均线比','10日均线比','60日均线比','C涨幅','H涨幅','O涨幅','L涨幅','V涨幅','20日量比','60日震荡']
fields = ['5日均线比','10日均线比','60日均线比','C涨幅','H涨幅','O涨幅','L涨幅','20日量比','60日震荡']
datas = datas.loc[:,fields]                                                                                                                                                   
print(datas)
# 准备预测的数据
# 

#使用sklearn数据
X_train, X_test, y_train, y_test = train_test_split(datas, label.values, test_size=0.2, random_state=0)

### fit model for train data
model = XGBClassifier(learning_rate=0.1,
                      use_label_encoder=False,
                      booster='gbtree',             # 分类树
                      n_estimators=500,             # 树的个数--1000棵树建立xgboost
                      max_depth= 6,                 # 树的深度
                      min_child_weight = 1,         # 叶子节点最小权重
                      gamma=0.,                     # 惩罚项中叶子结点个数前的参数
                      subsample=0.8,                # 随机选择80%样本建立决策树
                      objective='reg:squarederror', # 指定损失函数
                      scale_pos_weight=1,           # 解决样本个数不平衡的问题
                      random_state=27               # 随机数
                      )
model.fit(X_train,
          y_train,
          eval_set = [(X_test,y_test)],
          eval_metric=['rmse'],
          early_stopping_rounds = 10,
          verbose = True)

# 对测试集进行预测

tests = pd.read_csv('transverse_test'+end+'.csv')
label = tests['是否涨幅10%']
print(label.values)

tests = tests.loc[:,fields]                                                                                                                                                   

ans = model.predict_proba(tests)
y_pred = model.predict(tests)
accuracy = accuracy_score(label.values, y_pred)
print("Accuracy: %.2f%%" % (accuracy * 100.0))

png = xgb.to_graphviz(model,num_trees=0)
#png.view("stock.png")


#显示
#plot_importance(model)
#plt.show()
