#pytdx

from pytdx.hq import TdxHq_API
import pandas as pd
from common.common import * 

api = TdxHq_API()

block_list = []

filename = './datas/stock_tdx_block'+endday+'.html'

def get_block():
    all_list = api.get_security_list(1, 0)
    for i in all_list:
        code  = int (i['code'])
        if (code >= 880300) and (code <=880999) and (code != 880650):
            print(i['code'],i['name'])
            block_list.append([i['code'],i['name']])
dayK_list = []
def get_bar():
    for i in block_list:
        code = i[0]
        name = i[1]
        datas = api.get_index_bars(9,1, code, 0, 20)
        if datas == None or len(datas)<1:
            continue
        c1 = datas[-1]['close']
        d1 = datas[-1]['datetime']
        c2 = datas[-2]['close']
        c5 = datas[-5]['close']
        c10 = datas[-10]['close']
        c20 = datas[-20]['close']
        print(name,code,d1,c1,(c1-c2)*100/c2,(c1-c5)*100/c5,(c1-c10)*100/c10,(c1-c20)*100/c20)
        dayK_list.append([name,code,d1,c1,(c1-c2)*100/c2,(c1-c5)*100/c5,(c1-c10)*100/c10,(c1-c20)*100/c20])

    df = pd.DataFrame(dayK_list,columns=['name','code','date','close','今日涨幅','周涨幅','半月涨幅','月涨幅'])
    df = df.sort_values(by='今日涨幅',ascending=False).reset_index()
    del df['index']

    content = df.to_html(escape=False,float_format='%.2f') 

    content +='周涨幅排序:\n'

    df = df.sort_values(by='周涨幅',ascending=False).reset_index()
    del df['index']

    content += df.to_html(escape=False,float_format='%.2f') 
    print("save file",filename)
    save_file(filename,content)

if api.connect('119.147.212.81', 7709):
    # 获取板块
    get_block()
    get_bar()

