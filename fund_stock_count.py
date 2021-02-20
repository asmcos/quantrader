#统计每只股票的基金数据
import os


offset = 0

def get_stock_count(name):
    os.system("echo '"+name+"'; cd datas/fund ; grep '"+name+"' * | wc")

#获取股票的名字和代码号
def getstockinfo(stock):
    #2019-12-09,sz.002094,青岛金王,化工,申万一级行业
    # 时间，股票代码，名称，类别
    d,code,name,skip1,skip2 = stock.split(',')
    return code,name


# 判断是否已经下载了股票分类代码

if not os.path.exists('./datas/stock_industry_check.csv'):
    print('正在下载股票库列表....')
    os.system('python3 bs_get_industry_check.py')

stocklist = open('./datas/stock_industry_check.csv').readlines()
stocklist = stocklist[1+int(offset):] #删除第一行

for stock in stocklist:
    code,name = getstockinfo(stock) 
    get_stock_count(name)   
