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


class jqData():
    def __init__(self):
        jq.auth(config.jqauth['name'],config.jqauth['passwd'])

    def week(self,stock_code,count=400,end=default_end):
        fields=['date','open','high','low','close','volume']
        df = jq.get_bars(stock_code,count,end_dt=end,unit='1w',fields=fields)
        df.index=pd.to_datetime(df.date)
        df['openinterest']=0
        df=df[['open','high','low','close','volume','openinterest']]

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
        ('savedb',0)
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
					'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
					(order.executed.price,
					 order.executed.value,
					 order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
						 (order.executed.price,
						  order.executed.value,
						  order.executed.comm))

        self.order = None

    def __init__(self):
        self.dataclose = self.datas[0].close

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

    def next(self):
        if self.order:
            return  # pending order execution



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
    
    df500 = bt.feeds.PandasData(dataname=df500)
    df300 = bt.feeds.PandasData(dataname=df300)

    cerebro.adddata(df500)
    cerebro.adddata(df300)

    cerebro.addstrategy(TheStrategy,
                        name=args.name,
                        savedb=args.savedb)

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
