import requests
import re
import time
import gn_dict 

gndict = gn_dict.gndict
headers = {
    'Connection': 'keep-alive',
    'Accept': 'text/html, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'hexin-v': 'A1jUmtUwjTrX5KG-XkGeHIBdL43pQbw-HqaQ75JJpetEv_a7OlGMW261YNfh',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4573.0 Mobile Safari/537.36',
    'Referer': 'http://q.10jqka.com.cn/gn/',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    }
 
urlcode = 'http://q.10jqka.com.cn/gn/detail/code/%s/'

url8 = urlcode % '300008' # 新能源
url7 = urlcode % '300777' 
url1 = urlcode % '300382' # 稀土永磁，赚钱的板块

page = 1
def get_gnpage(page):
    time.sleep(1)

    response = requests.get('http://q.10jqka.com.cn/gn/index/field/addtime/order/desc/page/%s/ajax/1/' % page, headers=headers, verify=False)
    print(response.text.split("<input type")[0])
   

def get_gnsort(page):   
    time.sleep(1)
    session = requests.session()
    url = 'http://data.10jqka.com.cn/funds/gnzjl/field/tradezdf/order/desc/page/%s/ajax/1/free/1/' % page

    response = session.get(url, headers=headers, verify=False)
    print(response.text)
    print(re.findall("<table(.+?)table>",response.text,re.S|re.M))

    time.sleep(0.5)
    response = session.get(url)
    print(response.text)
    print(re.findall("<table(.+?)table>",response.text,re.S|re.M))

def get_gndict_home():
    time.sleep(1)
    resp = requests.get('http://q.10jqka.com.cn/gn/',headers=headers)
    all_gn = re.findall('''<a href="http://q.10jqka.com.cn/gn/detail/code/(\d+)/" target="_blank">(.*?)</a>''',resp.text,re.S|re.M)
    gn_dict1 = {}
    for i in all_gn:
        gn_dict1[i[0]]=i[1]
    print(gn_dict1)

#
# gndict save to gn_dict.py file
#

#get_gndict_home()

get_gnsort(1)

#get_gnpage(1) 
#get_gnpage(2) 

