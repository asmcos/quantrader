#pytdx

from pytdx.hq import TdxHq_API
import pandas as pd
from common.framework import * 
from common.common import endday 
import json
import talib

api = TdxHq_API(auto_retry=True)

hostname="http://klang.org.cn"
hostname="http://127.0.0.1:1337"
#hostname="http://klang.zhanluejia.net.cn"

filename_sl = os.path.expanduser("~/.klang_stock_list.csv")
filename_st = os.path.expanduser("~/.klang_stock_trader.csv")

def updatestocklist(stname=filename_sl):

    json = requests.get(hostname+"/industries").json()
    json = requests.get('http://klang.org.cn'+"/industries").json()
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
    datas = api.get_security_bars(9,zone,code1, 0, 150)
    datas = api.to_df(datas)
    if len(datas) < 2:
        return

    datas = datas.assign(date=datas['datetime'].apply(lambda x: str(x)[0:10])).drop(['year', 'month', 'day', 'hour', 'minute', 'datetime'], axis=1)
    #datas.rename(columns={'vol':'volume'},inplace = True)
    ma5 = talib.MA(datas.close,5)
    ma10 = talib.MA(datas.close,10)
    ma20 = talib.MA(datas.close,20)
    ma30 = talib.MA(datas.close,30)
    ma60 = talib.MA(datas.close,60)
    ma120 = talib.MA(datas.close,120)

    print(len(datas),datas.iloc[-1].date)

    datas1  = pd.DataFrame({
                            'ma5':ma5,
                            'ma10':ma10,
                            'ma20':ma20,
                            'ma30':ma30,
                            'ma60':ma60,
                            'ma120':ma120,
                            'date':datas.date})
    print(datas1)
    df = datas1.to_json(orient='table')
    jsondatas = json.loads(df)['data']
    for d in jsondatas:
        d['name'] = name
        d['code'] = code
        del d['index']
    #print(jsondatas)
    #print(d)
    #return
    try:
        requests.post(hostname+"/features/updates",json=jsondatas,timeout=2000)
    except:
        time.sleep(2)
        requests.post(hostname+"/features/updates",json=jsondatas,timeout=2000)

if api.connect('119.147.212.81', 7709):

    updatestocklist()

    init_stock_list()

    from common.framework import stocklist

    for stock in stocklist[:10]:
        code ,name ,tdxbk,tdxgn = getstockinfo(stock)        
        get_bar(name,code)
