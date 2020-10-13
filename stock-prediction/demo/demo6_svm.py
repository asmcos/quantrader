import tushare as ts
import talib
from sklearn import svm

# 获取上证指数数据
#青岛啤酒
code='600600'
#df=ts.get_hist_data(code,start='2018-07-09',end='2020-10-10')
df=ts.get_hist_data(code,start='2018-07-09')
close_pri=df['close']
close_pri = close_pri.sort_index(ascending=True)

print(close_pri)
# 定义训练数据
x_train = []
y_train = []

for index in range(2,len(close_pri)):
    # 取数据[-2]表示使用的特征是由今天之前的数据计算得到的
    sma_data = talib.SMA(close_pri[:index],timeperiod=7)[-2]
    wma_data = talib.WMA(close_pri[:index],timeperiod=7)[-2]
    mom_data = talib.MOM(close_pri[:index],timeperiod=7)[-2]
    
    features = []
    features.append(sma_data)
    features.append(wma_data)
    features.append(mom_data)
    x_train.append(features)
    
    # 对今天的交易进行打标签，涨则标记1，跌则标记-1
    if close_pri[index-1] < close_pri[index]:
        label = 1
    else:
        label = -1
    y_train.append(label)


# 去除前7天的数据，因为部分sma/wma/mom数值为nan
X_Train = x_train[7:]
Y_Train = y_train[7:]

# svm进行分类
clf = svm.SVC()
clf.fit(X_Train,Y_Train)

# 数据仅仅使用了2到len(close_pri)，所以最后一个数据没有参与分类，拿来试试
sma_test = talib.SMA(close_pri,timeperiod=7)[-2]
wma_test = talib.WMA(close_pri,timeperiod=7)[-2]
mom_test = talib.MOM(close_pri,timeperiod=7)[-2]
x_test = [[sma_test,wma_test,mom_test]]
y_test = -1
if close_pri[-2] < close_pri[-1] :
	y_test = 1

prediction = clf.predict(x_test)
print(prediction)
print(prediction == y_test)

# 数据仅仅使用了2到len(close_pri)
sma_test = talib.SMA(close_pri,timeperiod=7)[-1]
wma_test = talib.WMA(close_pri,timeperiod=7)[-1]
mom_test = talib.MOM(close_pri,timeperiod=7)[-1]
x_test = [[sma_test,wma_test,mom_test]]
prediction = clf.predict(x_test)
print(prediction)

