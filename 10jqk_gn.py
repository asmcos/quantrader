import requests
import re

headers = {
    'Connection': 'keep-alive',
    'Accept': 'text/html, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'hexin-v': 'A1jUmtUwjTrX5KG-XkGeHIBdL43pQbw-HqaQ75JJpetEv_a7OlGMW261YNfh',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4573.0 Mobile Safari/537.36',
    'Referer': 'http://q.10jqka.com.cn/gn/',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    }
 


page = 1
def get_gnpage(page):
    response = requests.get('http://q.10jqka.com.cn/gn/index/field/addtime/order/desc/page/%s/ajax/1/' % page, headers=headers, verify=False)
    print(response.text.split("<input type")[0])
   

def get_gnsort(page):   
    url = 'http://data.10jqka.com.cn/funds/gnzjl/field/tradezdf/order/desc/page/%s/ajax/1/free/1/' % page
    response = requests.get(url, headers=headers, verify=False)
    print(re.findall("<table.+?table>",response.text,re.S|re.M))

def get_home():
    resp = requests.get('http://q.10jqka.com.cn/gn/',headers=headers)
    print(reesp.text)

get_gnsort(1)

#get_gnpage(1) 
#get_gnpage(2) 
#get_home()

