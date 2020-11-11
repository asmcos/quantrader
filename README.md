学习量化交易记录

# 安装依赖库

pip3 install -r requirements.txt

我使用的是python3，所以都选用pip3

文档会记录在 http://www.zhanluejia.net.cn
```
.
├── README.md
├── bs_to_csv.py # baostock 内容存到csv文件
├── btr1.py #backtrader 代码例子
├── btr2.py #backtrader 代码的sma例子
├── btrmacd.py # btr macd 例子，4.13调试第一版
├── btrmrk.py  # btr MACD,KDJ,RSI三个维度判断买卖
├── start.py   # 执行脚本
├── datas
│   ├── bs_sh.600600.csv # 通过baostock网站存储的数据
│   └── orcl-1995-2014.txt #数据来自backtrader 源代码
├── macd1.py # baostock + talib + macd 例子，
├── macd2.py # tushare + talib + macd 例子
├── bs_get_industry.py #获取沪市、深市数据
├── bs_get_industry_check.py #获取沪市、深市股票，并且有在线数据
├── dbmongo.py # 数据 存储
├── requirements.txt # 安装一些python3依赖库
└── ts_to_csv.py # tushare to csv
```

## 运行其中一个例子


```
# 获取青岛啤酒的数据
python3 ts_to_csv.py --code 600600
# 使用macd策略
python3 btrmacd.py --datafile ./datas/ts_600600.csv
```

### 结果如下：
```
Starting Portfolio Value: 50000.00
2018-03-26, BUY CREATE, 39.81
2018-03-27, BUY EXECUTED, Price: 39.95, Cost: 47661.54, Comm 157.28
2018-07-31, SELL CREATE, 43.92
2018-08-01, SELL EXECUTED, Price: 43.92, Cost: 47661.54, Comm 172.91
2019-01-16, BUY CREATE, 36.10
2019-01-17, BUY EXECUTED, Price: 36.50, Cost: 52231.50, Comm 172.36
2020-01-06, SELL CREATE, 50.01
2020-01-07, SELL EXECUTED, Price: 50.20, Cost: 52231.50, Comm 237.06
Final Portfolio Value: 73601.29
```

结果是5万的启动资金2年后7万3.


# AI图谱

![](http://www.zhanluejia.net.cn/static/uploads/5b1dea78fd13d5f1869043d867906e0c.png)

#使用LSTM 预测股票

```bash
python3 stock_prediction_lstmV1.py 600600
```
最后一行数据就是未来5天的预测。

代码说明
 * 使用的是 tensorflow 的keras LSTM算法,tf是2.x版本
 * 股票数据接口来自tushare,建议切换成tushare pro版本
 * 例子代码是30为一个数据周期预测未来5天。
 * 股票预测仅仅是一个趋势，不是很准，大家不能用来炒股，仅仅用来学习

 # 二八轮动例子

 ```bash
 python3 btr28.py
 ```

代码说明
 * 采用沪深300，中证500作为轮动
 * 交易框架使用backtrader
 * 采用聚宽获取数据接口，其中切换了几个其他的数据接口没有完整的中证500周数据
 * 在原始数据里增加了计算好的4周增长率数据
