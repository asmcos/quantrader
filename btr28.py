### python3 btr28.py
### 源自二八轮动策略 张翼轸

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import argparse
import datetime
import random
import math
import backtrader as bt
import dbmongo
import config
import jqdatasdk as jq
import pandas as pd


#默认结束日期是今天
today = datetime.datetime.now()
default_end = "-".join([str(today.year) , str(today.month) , str(today.day)])

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))

class PandasData(bt.feeds.PandasData):
    lines = ('d4w',)
    params = (
        ('datetime', None),
        ('open','open'),
        ('high','high'),
        ('low','low'),
        ('close','close'),
        ('volume','volume'),
        ('openinterest',None),
        ('d4w','d4w'),

    )

# 计算涨幅比率
#（本周-4周前）/4周前

def delta4w(df):
    df['d4w'] = 0.0
    for i in range(4,len(df)):
        df['d4w'][i] = (df['close'][i] - df['close'][i-4]) / df['close'][i-4]
    return df

#比较2个指数的最大涨幅
#返回值1含义，谁是涨幅最大的指数 0表示d0涨幅大，1表示d1涨幅大
#返回值2含义，买卖信号， False 卖信号，True 买信号
#BTW：头四周内容都是0，返回值2为也是0，不发会生交易
# 二八轮动时，d0，d1 表示沪深300，和中证500
def compare28(d0,d1):
    maxval = 0  #默认选择d0为交易股票
    buy = False # 默认卖信号

    if d1 > d0 : #如果d1大，改d1为交易股票
        maxval = 1

    # 如果最大值大于0，视为买信号，否则是卖信号
    if max(d0,d1) > 0:
        buy = True

    return maxval,buy

#通过聚宽网络获取 指数的周数据，并计算 本周和4周前的增长比率
class jqData():
    def __init__(self):
        jq.auth(config.jqauth['name'],config.jqauth['passwd'])

    def week(self,stock_code,count=380,end=default_end):
        fields=['date','open','high','low','close','volume']
        df = jq.get_bars(stock_code,count,end_dt=end,unit='1w',fields=fields)
        df.index=pd.to_datetime(df.date)
        df['openinterest']=0
        df= df[['open','high','low','close','volume','openinterest']]
        df = delta4w(df)
        return df

class LongOnly(bt.Sizer):
	params = (('stake', 1),)
	def _getsizing(self, comminfo, cash, data, isbuy):
        # buy 1/2
		cash = math.floor(cash * 95 / 100 )

		if isbuy:
			divide = math.floor(cash/data.close[0])
			self.p.stake = divide
			return self.p.stake
		# Sell situation
		position = self.broker.getposition(data)
		if not position.size:
			return 0  # do not sell if nothing is open
		return self.p.stake


class TheStrategy(bt.Strategy):
    '''
    '''
    params = (
        ('name','zhanluejia'),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status == order.Completed:
            pass

        if not order.alive():
            self.order = None  # indicate no order is pending

        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                self.log(
					'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f,value %.2f' %
					(order.executed.price,
					 order.executed.value,
					 order.executed.comm,self.broker.getvalue()))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f,value %.2f' %
						 (order.executed.price,
						  order.executed.value,
						  order.executed.comm,self.broker.getvalue()))

        self.order = None

    def __init__(self):
        self.dataclose0 = self.datas[0].close
        self.dataclose1 = self.datas[1].close
        self.stockname=['中证500','沪深300']


    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order
        self.b = 0

    def next(self):
        if self.order:
            return  # pending order execution
        #每周比较 哪个指数涨幅大，更适合买卖，
        d,buy =  compare28(self.datas[0].d4w,self.datas[1].d4w)
        #d 代表谁最大，buy表示买卖信号
        if buy: #买信号
            if self.b == 1 and self.d != d: #切换股票
                self.close(data=self.datas[self.d],price=self.datas[self.d].close[0])
                self.log("switch sell: %s price %2f " % (self.stockname[self.d],
                    self.datas[self.d].close[0]))
            self.d = d
            self.buy(data=self.datas[d],price=self.datas[d].close[0])
            self.log("buy: %s price %2f " % (self.stockname[self.d],
                self.datas[d].close[0]))
            self.b = 1 # 已经购买了股票设置为买过标志

        elif self.b == 1 : #卖信号时判断是否买过
            self.b = 0
            self.close(data=self.datas[self.d],price=self.datas[self.d].close[0])
            self.log("sell: %s price %2f " % (self.stockname[self.d],
                self.datas[self.d].close[0]))

def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(args.cash)
    comminfo = bt.commissions.CommInfo_Stocks_Perc(commission=args.commperc,
                                                   percabs=True)

    cerebro.broker.addcommissioninfo(comminfo)
    #cerebro.broker.setcommission(commission=0.0)

    dkwargs = dict()
    if args.fromdate is not None:
        fromdate = datetime.datetime.strptime(args.fromdate, '%Y-%m-%d')
        dkwargs['fromdate'] = fromdate

    if args.todate is not None:
        todate = datetime.datetime.strptime(args.todate, '%Y-%m-%d')
        dkwargs['todate'] = todate

    # if dataset is None, args.data has been given
    # 获取数据
    data = jqData()
    #中证500ETF,沪深300

    df500 = data.week("510500.XSHG")
    df300 = data.week("000300.XSHG")
    print(df500)
    print(df300)
    df500 = PandasData(dataname=df500)
    df300 = PandasData(dataname=df300)

    cerebro.adddata(df500)
    cerebro.adddata(df300)

    cerebro.addstrategy(TheStrategy,
                        name=args.name,
                        )

    #cerebro.addsizer(FixedPerc, perc=0.96)
    cerebro.addsizer(LongOnly)


    #测试数据5万元本金
    cerebro.broker.setcash(50000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    results = cerebro.run()
    st0 = results[0]


    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #是否显示图表
    if args.plot:
        pkwargs = dict(style='bar')
        pkwargs = dict()
        if args.plot is not True:  # evals to True but is not True
            npkwargs = eval('dict(' + args.plot + ')')  # args were passed
            pkwargs.update(npkwargs)

        cerebro.plot(**pkwargs)

# 主要是获取参数，和策略逻辑无关
def parse_args(pargs=None):

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sample for Tharp example with 28轮动')

    group1 = parser.add_mutually_exclusive_group(required=False)
    group1.add_argument('--data', required=False, default=None,
                        help='Specific data to be read in')

    group1.add_argument('--datafile', required=False, default=None,
                            help='Specific data to be read in')

    parser.add_argument('--fromdate', required=False,
                        default='2005-01-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', required=False,
                        default=None,
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--cash', required=False, action='store',
                        type=float, default=50000,
                        help=('Cash to start with'))

    parser.add_argument('--cashalloc', required=False, action='store',
                        type=float, default=0.20,
                        help=('Perc (abs) of cash to allocate for ops'))

    parser.add_argument('--commperc', required=False, action='store',
                        type=float, default=0.0033,
                        help=('Perc (abs) commision in each operation. '
                              '0.001 -> 0.1%%, 0.01 -> 1%%'))

    parser.add_argument('--riskfreerate', required=False, action='store',
                        type=float, default=0.01,
                        help=('Risk free rate in Perc (abs) of the asset for '
                              'the Sharpe Ratio'))
    # Plot options
    parser.add_argument('--plot', '-p', nargs='?', required=False,
                        metavar='kwargs', const=True,
                        help=('Plot the read data applying any kwargs passed\n'
                              '\n'
                              'For example:\n'
                              '\n'
                              '  --plot style="candle" (to plot candles)\n'))

    parser.add_argument('--savedb', required=False,
                            type=int, default=0,
                            help=('是否存到数据'))

    parser.add_argument('--code', required=False,
                                 default=0,
                                help=('股票代码'))
    parser.add_argument('--name', required=False,
                                     default='战略家',
                                    help=('股票名称'))

    if pargs is not None:
        return parser.parse_args(pargs)

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()
