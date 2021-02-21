#统计每只股票的基金数据
import os
import pandas as pd

offset = 0
result_list = [] 
def create_clickable_code(code):
    code = code.split(".")[1]
    url_template= '''<a href="http://doctor.10jqka.com.cn/{code}/" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template


def get_stock_count(code,name,industry):
    p = os.popen("cd datas/fund ; grep '"+name+"' * | wc -l")
    count = p.read()
    print(code,name,count.strip('" \n'))
    result_list.append([code,name,count.strip('" \n'),industry])
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
    code,name,industry = getstockinfo(stock) 
    get_stock_count(code,name,industry)   

#print(result_list)

df = pd.DataFrame(result_list,columns=['code','code','fund','行业'])
df['code']=df['code'].apply(create_clickable_code)
print(df.to_html(escape=False))

#df = pd.DataFrame(result_list)
#df.to_csv("./datas/stockcount.csv")

