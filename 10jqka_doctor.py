# 10jqka 诊断

import requests
import re
import os
import pandas as pd

import argparse
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("--offset", help="开始执行的位置",default='0')
args = parser.parse_args()

offset = args.offset

result_list = []

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}


def get_doctor_html(code,name):
    code1 = code.split('.')[1]
    url="http://doctor.10jqka.com.cn/%s/"% code1
    resp = requests.get(url,headers=headers)
    info = re.findall('<p class="cnt showlevel2 hide">(.*?)</p>',resp.text,re.S|re.M|re.I)
    info1 = re.findall('<div class="value_info">(.*?)</ul>',resp.text,re.S|re.M|re.I)
    if len(info) > 0:
        print(code,name,info[0])
        result_list.append([code,name,info[0],info1[0]])
        df = pd.DataFrame([code,name,info[0],info1[0]])
        df.to_csv("./datas/doctor/stock_"+code+"_text.csv")
    else:
        print(resp.text)

def create_clickable_code(code):
    code = code.split(".")[1]
    url_template= '''<a href="http://doctor.10jqka.com.cn/{code}/" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template

#key 是所搜的关键词，例如：涨
#count 是多少只基金购买了该股票
def get_stats_value(code,name,industry,key,count):
    p = os.popen("cd datas/doctor/ ; grep '"+key+"' stock_"+code+"_text.csv;cd ../../")
    content = p.read()
    if len(content) > 20:
        result_list.append([name,code,industry,int(count)])


#获取股票的名字和代码号
def getstockinfo(stock):
    #2019-12-09,sz.002094,青岛金王,化工,申万一级行业
    # 时间，股票代码，名称，类别
    d,code,name,skip1,skip2 = stock.split(',')
    return code,name,skip1


# 判断是否已经下载了股票分类代码

if not os.path.exists('./datas/stock_industry_check.csv'):
    print('正在下载股票库列表....')
    os.system('python3 bs_get_industry_check.py')

stocklist = open('./datas/stock_industry_check.csv').readlines()
stocklist = stocklist[1+int(offset):] #删除第一行

if not os.path.exists('./datas/stockcount.csv'):
    print('请先计算股票基金持股数....')
    os.system('python3 10jqka_fund.py')

stockfund = open('./datas/stockcount.csv').readlines()
stockfund = stockfund[1+int(offset):] #删除第一行
stockdict = {}

for stock in stockfund:
    skip0,code,skip2,count,skip4 = stock.split(',')
    stockdict[code] = count

key = "股价短线上涨概率较大"
#key = "该股长期投资价值较高"

for stock in stocklist:
    code,name,skip1 = getstockinfo(stock)
    #get_doctor_html(code,name)
    #time.sleep(0.5)
    count = stockdict[code]
    get_stats_value(code,name,skip1,key,count)

df = pd.DataFrame(result_list,columns=['name','code','行业','fund'])
df['code']=df['code'].apply(create_clickable_code)
df = df.sort_values(by="fund",ascending=False)
print(df.to_html(escape=False))
