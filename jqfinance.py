### python3 btr28.py
### 源自二八轮动策略 张翼轸

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import datetime
import random
import config
import jqdatasdk as jq
import pandas as pd
import sys

#默认结束日期是今天
today = datetime.datetime.now()
default_end = "-".join([str(today.year) , str(today.month) , str(today.day)])

# 茅台600519,青岛啤酒600600 ,格力 XSHE: 000651.XSHE
code = '600519.XSHG'
if len(sys.argv) > 1:
    code = sys.argv[1]


def add_roe(df):

	df['roe'] = 0.0

	for i in range(0,len(df)):
		df['roe'][i] = df['pb_ratio'][i] / df['pe_ratio'][i]
	return df

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
        return df

    def financeData(self,stock_code):
        q = jq.query(jq.valuation.turnover_ratio,
              jq.valuation.market_cap,
			  jq.valuation.pb_ratio,
			  jq.valuation.pe_ratio,
			  jq.valuation.pcf_ratio,
              jq.indicator.eps
            ).filter(jq.valuation.code.in_([stock_code]))

		#ROE = PB/PE

        df = jq.get_fundamentals_continuously(q, end_date=default_end, count=20)
        df = add_roe(df)
        return df

    def day(self,stock_code,end=default_end):
        fields=['open','high','low','close','volume']
        df = jq.get_price(stock_code, count = 200, end_date=end, frequency='daily', fields=fields)
        return df

    def remain_count(self):
        count=jq.get_query_count()
        return count 

def main():
    # if dataset is None, args.data has been given
    # 获取数据
    data = jqData()

    df = data.financeData( code )
    print(df)
    df = data.day( code )
    print(df)
	
    print(data.remain_count())
	
if __name__ == '__main__':
    main()
