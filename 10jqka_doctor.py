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

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}


def get_doctor_html(code,name):
    code1 = code.split('.')[1]
    url="http://doctor.10jqka.com.cn/%s/"% code1
    resp = requests.get(url,headers=headers)
    info = re.findall('<p class="cnt showlevel2 hide">(.*?)</p>',resp.text,re.S|re.M|re.I)
    if len(info) > 0:
        print(code,name,info[0])
        result_list.append([code,name,info[0]])
        df = pd.DataFrame([code,name,info[0]])
        df.to_csv("./datas/doctor/stock_"+code+"_text.csv")
    else:
        print(resp.text)

def create_clickable_code(code):
    code = code.split(".")[1]
    url_template= '''<a href="http://doctor.10jqka.com.cn/{code}/" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template


def get_stats_value(code,name,industry):
    p = os.popen("cd datas/doctor/ ; grep '该股长期投资价值较高' stock_"+code+"_text.csv;cd ../../")
    count = p.read()
    if len(count) > 20:
        result_list.append([name,code,industry])
result_list = []

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

for stock in stocklist:
    code,name,skip1 = getstockinfo(stock)
    #get_doctor_html(code,name)
    #time.sleep(0.5)
    get_stats_value(code,name,skip1)

df = pd.DataFrame(result_list,columns=['name','code','行业'])
df['code']=df['code'].apply(create_clickable_code)
print(df.to_html(escape=False))
