#pytdx

from pytdx.hq import TdxHq_API
import pandas as pd
from common.framework import * 
from common.common import endday 
import json
import talib
import numpy as np

api = TdxHq_API(auto_retry=True)

hostname="http://klang.org.cn"
#hostname="http://127.0.0.1:1337"

filename_sl = os.path.expanduser("~/.klang_stock_list.csv")
filename_st = os.path.expanduser("~/.klang_stock_trader.csv")

def updatestocklist(stname=filename_sl):

    json = requests.get(hostname+"/industries").json()
    #json = requests.get('http://klang.org.cn'+"/industries").json()
    for i in json:
        cm_dict[i['code']] = i.get('chouma','50')
    df = pd.json_normalize(json)
    df = df.drop(columns=['_id','updatedAt','id','createdAt'])
    # 结果集输出到csv文件
    df.to_csv(stname, index=False,columns=['updateDate','code','code_name','industry','industryClassification','tdxbk','tdxgn'])


def get_bar(name,code):
    zone,code1 = code.split('.') 

    if zone == "sz":
        zone = 0
    if zone == "sh":
        zone = 1
    
    print(name,code1)
    datas = api.get_security_bars(9,zone,code1, 0, 300)
    datas = api.to_df(datas)
    if len(datas) < 2:
        return

    datas = datas.assign(date=datas['datetime'].apply(lambda x: str(x)[0:10])).drop(['year', 'month', 'day', 'hour', 'minute', 'datetime'], axis=1)

    ma5 = talib.MA(datas.close,5)
    ma10 = talib.MA(datas.close,10)
    ma20 = talib.MA(datas.close,20)
    ma30 = talib.MA(datas.close,30)
    ma60 = talib.MA(datas.close,60)
    ma120 = talib.MA(datas.close,120)
    rise = (datas['close'].values[1:]/datas['close'].values[:-1] - 1) * 100
    rise = np.insert(rise,0,np.NaN)

    mavol5 = talib.MA(datas.vol,5)
    risevol = datas.vol / mavol5
 
    func = lambda name :getattr(talib,name)(datas.open, datas.high, datas.low, datas.close)
    
    talibdict = {i:func(i) for i in ['CDL2CROWS','CDL3BLACKCROWS','CDL3INSIDE','CDL3LINESTRIKE','CDL3OUTSIDE','CDL3STARSINSOUTH','CDL3WHITESOLDIERS',
                                    'CDLABANDONEDBABY','CDLADVANCEBLOCK','CDLBELTHOLD','CDLBREAKAWAY','CDLCLOSINGMARUBOZU','CDLCONCEALBABYSWALL',
                                    'CDLCOUNTERATTACK','CDLDARKCLOUDCOVER','CDLDOJI','CDLDOJISTAR','CDLDRAGONFLYDOJI','CDLENGULFING','CDLEVENINGDOJISTAR',
                                    'CDLEVENINGSTAR','CDLGAPSIDESIDEWHITE','CDLGRAVESTONEDOJI','CDLHAMMER','CDLHANGINGMAN','CDLHARAMI',
                                    'CDLHARAMICROSS','CDLHIGHWAVE','CDLHIKKAKE','CDLHIKKAKEMOD','CDLHOMINGPIGEON','CDLIDENTICAL3CROWS',
                                    'CDLINNECK','CDLINVERTEDHAMMER','CDLKICKING','CDLKICKINGBYLENGTH','CDLLADDERBOTTOM','CDLLONGLEGGEDDOJI',
                                    'CDLLONGLINE','CDLMARUBOZU','CDLMATCHINGLOW','CDLMATHOLD','CDLMORNINGDOJISTAR','CDLMORNINGSTAR',
                                    'CDLONNECK','CDLPIERCING','CDLRICKSHAWMAN','CDLRISEFALL3METHODS','CDLSEPARATINGLINES','CDLSHOOTINGSTAR',
                                    'CDLSHORTLINE','CDLSPINNINGTOP','CDLSTALLEDPATTERN','CDLSTICKSANDWICH','CDLTAKURI','CDLTASUKIGAP',
                                    'CDLTHRUSTING','CDLTRISTAR','CDLUNIQUE3RIVER','CDLUPSIDEGAP2CROWS','CDLXSIDEGAP3METHODS',
                                    ]}

    #个性化的
    talibdict.update({
                            'ma5':ma5,
                            'ma10':ma10,
                            'ma20':ma20,
                            'ma30':ma30,
                            'ma60':ma60,
                            'ma120':ma120,
                            'rise':rise,
                            'risevol':risevol,
                            'date':datas.date})

    print(len(datas),datas.iloc[-1].date)

    datas1  = pd.DataFrame(talibdict)
    print(datas1)
    df = datas1.to_json(orient='table')
    jsondatas = json.loads(df)['data']
    for d in jsondatas:
        d['name'] = name
        d['code'] = code
        del d['index']
    #print(jsondatas)
    try:
        requests.post(hostname+"/features/updates",json=jsondatas,timeout=2000)
    except:
        time.sleep(2)
        requests.post(hostname+"/features/updates",json=jsondatas,timeout=2000)

if api.connect('119.147.212.81', 7709):

    updatestocklist()

    init_stock_list()

    from common.framework import stocklist

    for stock in stocklist :
        code ,name ,tdxbk,tdxgn = getstockinfo(stock)        
        get_bar(name,code)
