from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from Klang import Kl,Klang

import backtrader as bt
import pandas as pd
import math

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


def PandasData(columns):
    lines = ()
    params = (
        ('datetime', None),
        ('open','open'),
        ('high','high'),
        ('low','low'),
        ('close','close'),
        ('volume','vol'),
        ('openinterest',None),
    )

    for c in columns:
        lines = lines + (c,)
        params = params + ( (c, -1), )

    return type('PandasDataFeed', (bt.feeds.PandasData, ), {'lines':lines, 'params':params} )

# Create a Stratey
class KStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None
        self.macdhist = bt.ind.MACDHisto(self.data)
        print(self.data)
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
    def next(self):
        # Simply log the closing price of the series from the reference
        
        d = eval("self.datas[0]."+"digit"+"[0]")
        print(d[0])

        if not self.position:
            if self.macdhist > 0:
                self.order=self.buy()
        else:
            if self.macdhist < 0:
                self.order = self.sell()


def init_btr():
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(KStrategy)

    Kl.code("sh.600062")
    df = Kl.currentdf['df'] 

    df.index=pd.to_datetime(df.datetime)
    df['openinterest'] = 0
    df= df[['open','high','low','close','vol','openinterest']]

    df.insert(6,"digit",[x+5.0 for x in range(200)])
   
    PandasField = PandasData(["digit"]) 
    data = PandasField(dataname=df)

    cerebro.adddata(data)

    cerebro.addsizer(LongOnly)
    cerebro.broker.setcash(100000.0)
    
    print('成本: %.2f' % cerebro.broker.getvalue())
    # Run over everything
    cerebro.run()

    print('总剩余: %.2f' % cerebro.broker.getvalue())
    # Plot the result
    cerebro.plot(style='bar')   

if __name__ == '__main__':
    Klang.Klang_init(); #加载所有股票列表

    init_btr();


