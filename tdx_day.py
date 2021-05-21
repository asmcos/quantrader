#pytdx

from pytdx.hq import TdxHq_API
import pandas as pd
from common.framework import * 
from common.common import today

api = TdxHq_API()


def get_bar(name,code):
    zone,code = code.split('.') 

    if zone == "sz":
        zone = 0
    if zone == "sh":
        zone = 1
    
    print(name,code)
    datas = api.get_security_bars(9,zone, str(code), 0, 20)
    if datas == None :
       return
    df = api.to_df(datas)
    print(df)

if api.connect('119.147.212.81', 7709):

    init_stock_list()

    from common.framework import stocklist

    for stock in stocklist:
        code ,name = getstockinfo(stock)        
        get_bar(name,code)
