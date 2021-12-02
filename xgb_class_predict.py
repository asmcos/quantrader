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

from common.framework import save_df_tohtml

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

df = pd.read_csv('~/.test_feat.csv')
df = df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]
print(df.columns)

df1 = df[df['datetime']<'2021-07-30']
df2 = df[df['datetime']>'2021-07-30']

datas = df1
label = datas['target']
label2 = df2['target']
print(label.values)

DisplayOriginalLabel(label.values)


fields = [
       'fist_location_of_max.close',
       'fist_location_of_min.close', 'ndex_mass_quantile_50.close',
       'ndex_mass_quantile_75.close', '_ndex_mass_quantile_25.close',
       'kurtosis.close', 'last_location_of_max.close',
       'last_location_of_min.close', 'ma.close', 'macd.close', 'max.close',
       'mean.close', 'min_change.close', 'min.close', 'none_rate.close',
       'number_peaks_1.close', 'number_peaks_2.close', 'number_peaks_3.close',
       'percentage_below_mean.close', 'ratio_value_number_to_seq_length.close',
       'skewness.close', 'standard_deviation.close', 'variance.close',
       'ma10.close', 'ma20.close', 'ma30.close', 'rise.vol', 'ma20.vol']


datas = datas.loc[:,fields]
print(datas)

# 准备预测的数据
# 

#使用sklearn数据
X_train, X_test, y_train, y_test = train_test_split(datas, label.values, test_size=0.2, random_state=0)
X2_train, X2_test, y2_train, y2_test = train_test_split(df2, label2.values, test_size=0.2, random_state=0)

### fit model for train data
model = XGBClassifier(learning_rate=0.01,
                      use_label_encoder=False,
                      booster='gbtree',             # 分类树
                      n_estimators=300,             # 树的个数--1000棵树建立xgboost
                      max_depth= 6,                 # 树的深度
                      min_child_weight = 1,         # 叶子节点最小权重
                      gamma=0.,                     # 惩罚项中叶子结点个数前的参数
                      subsample=0.8,                # 随机选择80%样本建立决策树
                      objective='reg:squarederror', # 指定损失函数
                      scale_pos_weight=1,           # 解决样本个数不平衡的问题
                      random_state=27,               # 随机数
                      colsample_bytree=0.7,
                      )
model.fit(X_train,
          y_train,
          eval_set = [(X_test,y_test)],
          eval_metric=['rmse'],
          early_stopping_rounds = 10,
          verbose = False)

# 对测试集进行预测

ans = model.predict_proba(X2_test.loc[:,fields])
y_pred = model.predict(X2_test.loc[:,fields])
accuracy = accuracy_score(y2_test, y_pred)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
print(y_pred)
print(ans)

pcnt1 = 0
pcnt2 = 0
for i in range(len(y_pred)):

    if y_pred[i] == 0 or ans[i][1] < 0.5 :
        continue

    print(ans[i][1],X2_test['datetime'].values[i],X2_test['code'].values[i])
    if y_pred[i] == y2_test[i]:
        pcnt1 += 1
    else:
        pcnt2 += 1
DisplayOriginalLabel(y2_test)
print("Accuracy: %.2f %% " % (100 * pcnt1 / (pcnt1 + pcnt2)))

"""
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

#png = xgb.to_graphviz(model,num_trees=0)
#png.view("stock.png")


#显示
#plot_importance(model)
#plt.show()
"""
