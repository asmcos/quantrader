import baostock as bs
import pandas as pd
import requests
import json
import tdxhy 
import time
import os
from common.common import *

# 登录系统
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

# 获取行业分类数据
rs = bs.query_stock_industry()
# rs = bs.query_stock_basic(code_name="浦发银行")
print('query_stock_industry error_code:'+rs.error_code)
print('query_stock_industry respond  error_msg:'+rs.error_msg)


filename_cm = os.path.expanduser("~/.klang_stock_cm.csv")
if not os.path.exists(filename_cm):
    cm = 0
else:
    cm = 1
    cmdict = {}
    cm_list = open(filename_cm).readlines()
    cm_list = cm_list[1+int(offset):] #删除第一行

    for i in cm_list:
        ilist = i.split(',')
        code = ilist[0].split('.')[1].lower() + '.' + ilist[0].split('.')[0]
        cmdict[code] = ilist[2]
# 打印结果集
industry_list = []
while (rs.error_code == '0') & rs.next() :
    # 获取一条记录，将记录合并在一起
    row = rs.get_row_data()
    kdata = bs.query_history_k_data_plus(row[1], 'date,open,high,low,close,volume', start_date='2020-12-01', 
                                      frequency='d')	
    if len(kdata.get_row_data()) == 0:
        continue
    tdxbk = tdxhy.gettdxbk(row[1])
    tdxgn = tdxhy.gettdxgn(row[1])
        
    row.append(tdxbk)
    row.append(tdxgn)
    if cm == 1:
        code = row[1]    
        chouma = cmdict.get(code,"50")
        row.append(chouma)
    print(row)
    industry_list.append(row)	

fields = rs.fields
fields.append('tdxbk')
fields.append('tdxgn')

if cm == 1:
    fields.append('chouma')

datas = pd.DataFrame(industry_list, columns=fields)

datas = datas.to_json(orient='table')
jsondatas = json.loads(datas)['data']

hostname = "https://klang.org.cn"
#hostname = "http://klang.zhanluejia.net.cn"
resp = requests.post(hostname+"/industries/drop")   
print(resp.content)
try:
   resp = requests.post(hostname+"/industries/updates",json=jsondatas,timeout=2000)
   print(resp.content)
except:
   time.sleep(2)
   requests.post(hostname+"/industries/updates",json=jsondatas,timeout=2000)

# 登出系统
bs.logout()
