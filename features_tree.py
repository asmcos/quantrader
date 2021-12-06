from Klang import (Kl,Klang_init,
    C,O,V,H,L, CLOSE,HIGH,DATETIME,
    MA,CROSS,BARSLAST,HHV,LLV,COUNT,BARSLASTFIND,
    MAX,MIN,MACD)
from Klang.common import end as today
import talib 

import sys
import linecache
import pandas as pd
import requests,time

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

all_list = []
target_day = 10 #收盘价之后的几天内最高价格，判断是否有涨价空间
hostname = "http://klang.org.cn"

def get_features(code,end):
    try:
        json = requests.get(hostname+"/features",
            params={"code":code,"end":end,"limit":200},timeout=1000).json()
    except:
        time.sleep(2)
        json = requests.get(hostname+"/features",
            params={"code":code,"end":end,"limit":200},timeout=1000).json()

    df = pd.json_normalize(json)
    if len(df) < 1:
       return []
    df = df.drop(columns=['_id','codedate','id'])
    datas = df.sort_values(by="date",ascending=True) 

    return datas

def main_loop(start,endday):
    global all_list

    for df in Kl.df_all[:1000]:
    #for df in Kl.df_all:

        Kl.code(df["code"])

        if start is None:
            Kl.date(end=endday)
        else:
            Kl.date(start=start,end=endday)
        try:
            allDate = DATETIME.data
            # 如果target_day = N,表示，最后的N 天数据不能作为训练或者测试数据
            # 我们会计算这个 N 天的最大值作为目标值，计算涨幅空间

            featureday = allDate[-target_day]
            datas = get_features(df['code'],featureday)   
            print(df['code'],df['name'])
            datas = datas[(datas['date'] >= allDate[0]) & (datas['date'] < featureday)]

            #print(datas.date,len(datas),C.data[:-target_day])
            #print(pd.DataFrame({"max":talib.MAX(C.data,target_day)[target_day:].values,"close":C.data[:-target_day].values}))
            #  计算涨幅空间
            rise_target = (talib.MAX(C.data,target_day)[target_day:].values / C.data[:-target_day].values - 1) * 100

            datas['target'] = rise_target > 10
            all_list += datas.values.tolist()

        except KeyboardInterrupt:
            break
        except:
            PrintException()


fields = [
       'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE',
       'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS',
       'CDLABANDONEDBABY', 'CDLADVANCEBLOCK', 'CDLBELTHOLD', 'CDLBREAKAWAY',
       'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL', 'CDLCOUNTERATTACK',
       'CDLDARKCLOUDCOVER', 'CDLDOJI', 'CDLDOJISTAR', 'CDLDRAGONFLYDOJI',
       'CDLENGULFING', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR',
       'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER',
       'CDLHANGINGMAN', 'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE',
       'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS',
       'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH',
       'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI', 'CDLLONGLINE', 'CDLMARUBOZU',
       'CDLMATCHINGLOW', 'CDLMATHOLD', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR',
       'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS',
       'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR', 'CDLSHORTLINE',
       'CDLSPINNINGTOP', 'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI',
       'CDLTASUKIGAP', 'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER',
       'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS', 'code', 'date', 'ma10',
       'ma120', 'ma20', 'ma30', 'ma5', 'ma60', 'name', 'rise', 'risevol',
       'target']


Klang_init()

main_loop(start=None,endday='2021-07-01')
df = pd.DataFrame(all_list,columns=fields)
df.to_csv('transverse_train'+today+'.csv',index=False)


all_list = []
main_loop(start='2021-07-15',endday=today)
df = pd.DataFrame(all_list,columns=fields)
df.to_csv('transverse_test'+today+'.csv',index=False)
"""
all_list = []
pred_data = 1
main_loop(start='2021-07-15',endday=today)
df = pd.DataFrame(all_list,columns=fields)
df.to_csv('transverse_pred'+today+'.csv',index=False)
"""
