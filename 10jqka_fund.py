# 10jqka
import requests
import pandas as pd
import argparse
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("--offset", help="开始执行的位置",default='0')
args = parser.parse_args()

offset = args.offset


if not os.path.exists('./datas/fund_list.csv'):
    print('正在下载基金库列表....')
    os.system('python3 doctorxiong_fund.py')

fundlist = open('./datas/fund_list.csv').readlines()
fundlist = fundlist[1+int(offset):] #删除第一行

fund_ok_list = []
def get_fund_stock(code,name):
    url = "https://fund.10jqka.com.cn/web/fund/stockAndBond/%s"%code
    resp = requests.get(url)
    fund_stock = (resp.json()['data']['stock'])
    if (len(fund_stock)==0):
        print(code,"is empty")
        return -1
    df = pd.DataFrame(fund_stock)
    print(df)
    df.to_csv("./datas/fund/fund_stock_"+code+".csv")

    fund_ok_list.append([code,name])

def get_fund_info(fund):
    order,code,jc,name,skip1,skip2 = fund.split(",")
    return code,name

for fund in fundlist[:2000]:
    code,name = get_fund_info(fund)
    print(code,name)
    get_fund_stock(code,name)
    time.sleep(0.2)
df = pd.DataFrame(fund_ok_list)
df.to_csv("./datas/fund_ok_list.csv")
print(fund_ok_list)
