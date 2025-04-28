import requests
import re

def remake_code(code):
    code = code.lower()
    code = code.replace(".","")
    return code
def remake_codelist(codelist):
    if isinstance(codelist,str):
        codelist = codelist.split(",")

    return [remake_code(c) for c in codelist]

def remake_result(data):
    # 定义正则表达式模式
    pattern = r'v_s_([a-z]{2}\d+)="\d+~([^~]+)~\d+~([\d.]+)~[-\d.]+~([-\d.]+)~'

    # 使用 findall 方法查找所有匹配项
    matches = re.findall(pattern, data)

    results = []
    # 遍历匹配结果并输出
    for match in matches:
        code = match[0]
        name = match[1]
        price = match[2]
        rise  = match[3]
        #print(f"代码: {code}, 名称: {name}, 价格: {price},涨跌: {rise}")
        results.append([code,name,price,rise])
    return results
def search(keyword):
    url = "https://proxy.finance.qq.com/cgi/cgi-bin/smartbox/search?stockFlag=1&fundFlag=1&app=official_website&c=1&query=" + keyword
    resp = requests.get(url)
    results=[]
    data = resp.json()['stock'][:10]
    for d in data:
        results.append({"name":d['name'],"code":d['code']})
    return results

def qqlist(codelist):
    codelist = remake_codelist(codelist)
    url = "https://qt.gtimg.cn/?q=s_" + ",s_".join(codelist)
    
    resp = requests.get(url)
    result = remake_result(resp.text)
    return result

#qqlist("sh600769,hk00354,sz002714")
#print(search("0001"))
