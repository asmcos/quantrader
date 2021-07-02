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
        if datas == None or len(datas)<20:
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



tdxblockdf = ''

def QA_fetch_get_tdx_industry() -> pd.DataFrame:
    import random
    import tempfile
    import shutil
    import os
    from urllib.request import urlopen
    global tdxblockdf

    def gettempdir():
        tmpdir_root = tempfile.gettempdir()
        subdir_name = 'tdx_base' #+ str(random.randint(0, 1000000))
        tmpdir = os.path.join(tmpdir_root, subdir_name)
        if not os.path.exists(tmpdir): 
            os.makedirs(tmpdir)

        return tmpdir
 
    def download_tdx_file(tmpdir) -> str:
        url = 'http://www.tdx.com.cn/products/data/data/dbf/base.zip'
        try:
            file = tmpdir + '/' + 'base.zip'
            f = urlopen(url)
            data = f.read()
            with open(file, 'wb') as code:
                code.write(data)
            f.close()
            shutil.unpack_archive(file, extract_dir=tmpdir)
            os.remove(file)
        except:
            pass
        return tmpdir

    def read_industry(folder:str) -> pd.DataFrame:
        incon = folder + '/incon.dat' # tdx industry file
        hy = folder + '/tdxhy.cfg' # tdx stock file

        # tdx industry file
        with open(incon, encoding='GB18030', mode='r') as f:
            incon = f.readlines()
        incon_dict = {}
        for i in incon:
            if i[0] == '#' and i[1] != '#':
                j = i.replace('\n', '').replace('#', '')
                incon_dict[j] = []
            else:
                if i[1] != '#':
                    incon_dict[j].append(i.replace('\n', '').split(' ')[0].split('|'))

        incon = pd.concat([pd.DataFrame.from_dict(v).assign(type=k) for k,v in incon_dict.items()]) \
            .rename({0: 'code', 1: 'name'}, axis=1).reset_index(drop=True)

        with open(hy, encoding='GB18030', mode='r') as f:
            hy = f.readlines()
        hy = [line.replace('\n', '') for line in hy]
        hy = pd.DataFrame(line.split('|') for line in hy)
        # filter codes
        hy = hy[~hy[1].str.startswith('9')]
        hy = hy[~hy[1].str.startswith('2')]

        hy1 = hy[[1, 2]].set_index(2).join(incon.set_index('code')).set_index(1)[['name', 'type']]
        hy2 = hy[[1, 3]].set_index(3).join(incon.set_index('code')).set_index(1)[['name', 'type']]
        # join tdxhy and swhy
        df = hy.set_index(1) \
            .join(hy1.rename({'name': hy1.dropna()['type'].values[0], 'type': hy1.dropna()['type'].values[0]+'_type'}, axis=1)) \
            .join(hy2.rename({'name': hy2.dropna()['type'].values[0], 'type': hy2.dropna()['type'].values[0]+'_type'}, axis=1)).reset_index()

        df.rename({0: 'sse', 1: 'code', 2: 'TDX_code', 3: 'SW_code'}, axis=1, inplace=True)
        df = df[[i for i in df.columns if not isinstance(i, int) and  '_type' not in str(i)]]
        df.columns = [i.lower() for i in df.columns]

        #shutil.rmtree(folder, ignore_errors=True)
        return df
    folder = gettempdir()
    dirpath = folder
    print(os.path.exists(folder + '/incon.dat'))
    print(os.path.exists(folder + '/tdxhy.cfg'))
    if not os.path.exists(folder + '/incon.dat') or not os.path.exists(folder + '/tdxhy.cfg'): 
        print("Save file to ",folder)
        download_tdx_file(folder)
    print("Read file from ",folder)
    df = read_industry(folder)

    tdxblockdf = df
    return df






if api.connect('119.147.212.81', 7709):
    # 获取板块
    df = QA_fetch_get_tdx_industry()
    hy = df.loc[df['code']  == '601012',:]
    for i in range(0,len(hy)):
        print(hy.iloc[i])

    #get_block()
    #get_bar()
