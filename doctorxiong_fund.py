# 基金接口 https://www.doctorxiong.club/api

import requests
import pandas as pd
import numpy as np

def get_all_fund():
    resp = requests.get("https://api.doctorxiong.club/v1/fund/all")
    df = pd.DataFrame(resp.json()['data'])
    print(len(df))
    print(df)
    df.to_csv("./datas/fund_list.csv")

def get_hot_fund():
    resp = requests.get("https://api.doctorxiong.club/v1/fund/hot")
    df = pd.DataFrame(resp.json()['data'])
    print(len(df))
    print(df)
    df.to_csv("./datas/fund_hot.csv")

def get_fund_stock(code):
    url = "https://api.doctorxiong.club/v1/fund/position?code=%d"%code
    resp = requests.get(url)
    print(resp.json())

#get_fund_stock(970016)

get_all_fund()

