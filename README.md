学习量化交易记录

# 安装依赖库

pip3 install -r requirements.txt

我使用的是python3，所以都选用pip3

文档会记录在 http://www.zhanluejia.net.cn
```
.
├── README.md
├── bs_to_csv.py # baostock 内容存到csv文件,有些数据有问题，可能是代码问题
├── btr1.py #backtrader 代码例子
├── btr2.py #backtrader 代码的sma例子
├── btrmacd.py # btr macd 例子，还在迭代中
├── datas
│   ├── bs_sh.600600.csv # 通过baostock网站存储的数据
│   └── orcl-1995-2014.txt #数据来自backtrader 源代码
├── macd1.py # baostock + talib + macd 例子，
├── macd2.py # tushare + talib + macd 例子
├── requirements.txt # 安装一些python3依赖库
└── ts_to_csv.py # tushare to csv 
```
