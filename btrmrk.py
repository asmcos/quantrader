### python3 btrmsk.py --datafile ./datas/bs_sh.600600.csv  ###
### 根据股票数据计算金叉 和RSI，KDJ数据  ###

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import argparse
import datetime
import random
import math
import backtrader as bt
import dbmongo

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class nMACDHisto(bt.indicators.MACDHisto):
    lines = ('histo','abshisto','mahisto')
    plotlines = dict(histo=dict(color='grey', _fill_lt=(0, 'green'), _fill_gt=(0, 'red')),
    macd=dict(color="red"),
    signal=dict(color="blue"),
    abshisto=dict(alpha=0.0))


    def once(self, start, end):
        pass

    def __init__(self):
        super(nMACDHisto, self).__init__()
        self.lines.histo = self.lines.histo  * 2
        self.lines.abshisto = abs(self.lines.histo)

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


### MACD ，RSI， KDJ
class TheMRKStrategy(bt.Strategy):
    '''
    This strategy is loosely based on some of the examples from the Van
    K. Tharp book: *Trade Your Way To Financial Freedom*. The logic:

      - Enter the market if:
        - The MACD.macd line crosses the MACD.signal line to the upside
        - The Simple Moving Average has a negative direction in the last x
          periods (actual value below value x periods ago)

     - Set a stop price x times the ATR value away from the close

     - If in the market:

       - Check if the current close has gone below the stop price. If yes,
         exit.
       - If not, update the stop price if the new stop price would be higher
         than the current
    '''

    params = (
        # Standard MACD Parameters
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),   # ATR distance for stop price
        ('smaperiod', 30),  # SMA Period (pretty standard)
        ('dirperiod', 10),  # Lookback period to consider SMA trend direction
        ('code',1),
        ('name','zhanluejia'),
        ('savedb',0),
        # rsi
        ('safediv',True),
        ('period', 14),
        #KDJ

    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status == order.Completed:
            pass


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

        self.macd = nMACDHisto(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)




        # Cross of macd.macd and macd.signal
        # macd is dif， signal is dea
        # mcross 1 上冲，0 无变化，-1下冲

        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

        # To set the stop price
        #self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

        # Control market trend
        self.sma = bt.indicators.SMA(self.data, period=self.p.smaperiod)
        #self.smadir = self.sma - self.sma(-self.p.dirperiod)
        self.smadir1 = self.sma - self.sma(-1)
        self.smadir2 = self.sma(-1) - self.sma(-2)

        # 21,14
        self.rsi = bt.indicators.RSI(self.data.close)

        #TheKDJStrategy
        self.stochastic = bt.indicators.StochasticFull(self.data0, safediv =True,period=5, period_dfast=3, period_dslow=3)


    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order


    def getRsiBuy(self):
        if self.rsi > 50 and self.rsi < 80:
            return True
        else:
            return False

    def getMacdBuy(self):
        if self.mcross[0] > 0.0  and self.macd.macd > 0.0 and self.smadir1 >= 0 and self.smadir2 >=0:
            return True
        else:
            return False

    def getKdjBuy(self):
        if self.stochastic.percK < 10 or self.stochastic.percD < 20:
            return True
        else:
            return False

    def next(self):
        if self.order:
            return  # pending order execution

        # 昨天
        #print("-1",self.macd.macd.get(-1),self.macd.signal.get(-1))
        # 今天
        #print("00",self.macd.histo.get(),self.macd.abshisto.get(),self.macd.mahisto.get())

        if self.p.savedb != 0: #存数据库
            if self.getMacdBuy() and self.getRsiBuy() and self.getKdjBuy():
                dbmongo.insertMarket(1,self.datas[0].datetime.date(0).isoformat(),
                "1",self.rsi.get()[0],self.stochastic.percK.get()[0],
                self.p.code,self.p.name)

        if not self.position:  # not in the market
            # mcross > 0 是金叉穿越线,此时 macd （dif） >0

            if self.macd.histo > 0.0 and self.macd.macd > 0:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()


        else:  # in the market
            # mcross < 0 ,死叉 穿越，此时macd(dif) < 0
            if self.macd.histo < 0.0 :
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()


DATASETS = {
    'yhoo': './datas/yhoo-1996-2014.txt',
    'orcl': './datas/orcl-1995-2014.txt',
    'nvda': './datas/nvda-1999-2014.txt',
}


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
    dataname = DATASETS.get(args.dataset, args.data)
    if args.datafile:
        dataname = args.datafile

        data0 = bt.feeds.GenericCSVData(dataname=dataname,
            dtformat=('%Y-%m-%d'),
            date=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            openinterest=-1,
            **dkwargs)

    cerebro.adddata(data0)

    cerebro.addstrategy(TheMRKStrategy,
                        macd1=args.macd1, macd2=args.macd2,
                        macdsig=args.macdsig,
                        atrperiod=args.atrperiod,
                        atrdist=args.atrdist,
                        smaperiod=args.smaperiod,
                        dirperiod=args.dirperiod,
                        code=args.code,
                        name=args.name,
                        savedb=args.savedb)

    #cerebro.addsizer(FixedPerc, perc=0.96)
    cerebro.addsizer(LongOnly)



    cerebro.broker.setcash(50000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    results = cerebro.run()
    st0 = results[0]


    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


    if args.plot:
        pkwargs = dict(style='bar')
        pkwargs = dict()
        if args.plot is not True:  # evals to True but is not True
            npkwargs = eval('dict(' + args.plot + ')')  # args were passed
            pkwargs.update(npkwargs)

        cerebro.plot(**pkwargs)


def parse_args(pargs=None):

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sample for Tharp example with MACD')

    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--data', required=False, default=None,
                        help='Specific data to be read in')

    group1.add_argument('--datafile', required=False, default=None,
                            help='Specific data to be read in')

    group1.add_argument('--dataset', required=False, action='store',
                        default="orcl", choices=DATASETS.keys(),
                        help='Choose one of the predefined data sets')

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

    parser.add_argument('--macd1', required=False, action='store',
                        type=int, default=12,
                        help=('MACD Period 1 value'))

    parser.add_argument('--macd2', required=False, action='store',
                        type=int, default=26,
                        help=('MACD Period 2 value'))

    parser.add_argument('--macdsig', required=False, action='store',
                        type=int, default=9,
                        help=('MACD Signal Period value'))

    parser.add_argument('--atrperiod', required=False, action='store',
                        type=int, default=14,
                        help=('ATR Period To Consider'))

    parser.add_argument('--atrdist', required=False, action='store',
                        type=float, default=3.0,
                        help=('ATR Factor for stop price calculation'))

    parser.add_argument('--smaperiod', required=False, action='store',
                        type=int, default=30,
                        help=('Period for the moving average'))

    parser.add_argument('--dirperiod', required=False, action='store',
                        type=int, default=10,
                        help=('Period for SMA direction calculation'))

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
