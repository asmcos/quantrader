学习量化交易记录，
quantrader是基于backtrack框架的回测系统，包含常见的macd，二八动量等。
希望收集各种常见的交易策略算法，供各网友学习，交流。

## 新手上路（推荐）

根目录旧脚本很多已年久、环境依赖重，**请先跑编号目录**（旧文件一律保留作对照）：

```bash
cd 01-股票的数据获取
bash install.sh          # 或: pip3 install -r requirements.txt
python3 stock_list.py
python3 boards.py
python3 day_k_qq.py
python3 minute_qq.py
```

说明见 [`01-股票的数据获取/README.md`](01-股票的数据获取/README.md)（同一能力含东财/腾讯/eltdx/pytdx 多种途径）。

```bash
cd ../02-用pandas装股票数据
pip3 install pandas
python3 dayk_to_df.py
python3 analyze_examples.py
```

说明见 [`02-用pandas装股票数据/README.md`](02-用pandas装股票数据/README.md)。后续会继续加 `03-…`。

# 安装依赖库

pip3 install -r requirements.txt

我使用的是python3，所以都选用pip3

部分说明见 https://klang.org.cn

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


### 数据的获取

* common/*   #公共部分
* bs_get_industry_check.py #获取所有股票列表 包含板块信息
* bs_industry_klang.py  #获取板块信息，并且提交到 klang.org.cn
* tdxhy.py #获取 通达信板块信息

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

# 行情接口修复（2_ 前缀文件）

部分原有模块存在 bug，**不直接修改原文件**，修复版统一以 `2_` 开头命名，并配有说明文档。

| 原文件 | 修复文件 | 说明文档 |
|--------|----------|----------|
| `hk_qq.py` | `2_hk_qq.py` | `2_说明_hk_qq.md` |

## hk_qq 修复内容

原 `hk_qq.py` 的 `get_minute_data` 中最高/最低价字段取错 qt 数组下标（`high` 用了当前价，`low` 用了最高价），导致 `high < low`。修复版见 `2_hk_qq.py`，详细说明见 `2_说明_hk_qq.md`。

## 使用修复版

```bash
# 验证修复效果
python3 2_hk_qq.py
```

在 `proxy_flask.py` 中切换为修复版：

```python
from importlib import import_module
qq = import_module("2_hk_qq")
```

之后 `/tick/<code>`、`/day/<code>` 等路由无需其他改动。
