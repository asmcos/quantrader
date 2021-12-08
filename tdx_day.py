#pytdx

from pytdx.hq import TdxHq_API
import pandas as pd
from common.framework import * 
from common.common import endday 
import json

api = TdxHq_API(auto_retry=True)

hostname="http://klang.org.cn"
hostname="http://klang.zhanluejia.net.cn"

filename_sl = os.path.expanduser("~/.klang_stock_list.csv")
filename_st = os.path.expanduser("~/.klang_stock_trader.csv")

def updatestocklist(stname=filename_sl):

    json = requests.get(hostname+"/industries").json()
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
    datas = api.get_security_bars(9,zone,code1, 0, 500)
    info = api.get_finance_info(zone, code1)  
    datas = api.to_df(datas)
    if len(datas) < 2:
        return

    liutonggu = float(info['liutongguben'])
    datas = datas.assign(date=datas['datetime'].apply(lambda x: str(x)[0:10])).drop(['year', 'month', 'day', 'hour', 'minute', 'datetime'], axis=1)
    datas.rename(columns={'vol':'volume'},inplace = True)

    print(len(datas),datas.iloc[-1].date)
    datas = datas [datas['volume'] > 0]
    df = datas.to_json(orient='table')
    jsondatas = json.loads(df)['data']
    for d in jsondatas:
        d['name'] = name
        d['code'] = code
        d['volume'] = float("%.4f" % (d['volume'] * 100)) #股 = 手*100
        d['turn'] = float("%.4f" %(d['volume']*100 / liutonggu)) 
        del d['index']
    #print(jsondatas)
    #print(datas.iloc[-1],liutonggu,d)
    try:
        requests.post(hostname+"/dayks/updates",json=jsondatas,timeout=2000)
    except:
        time.sleep(2)
        requests.post(hostname+"/dayks/updates",json=jsondatas,timeout=2000)

if api.connect('119.147.212.81', 7709):

    updatestocklist()

    init_stock_list()

    from common.framework import stocklist

    for stock in stocklist:
        code ,name ,tdxbk,tdxgn = getstockinfo(stock)        
        get_bar(name,code)
