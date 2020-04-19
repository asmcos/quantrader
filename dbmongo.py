# mongodb by pymongo
# python3 不用coding utf-8 支持中文了。
from pymongo import MongoClient
import datetime

#Step 1: Connect to MongoDB - Note: Change connection string as needed
client = MongoClient('mongodb://localhost:27017/')

db = client.quantrader # databasename

# collection name
# db.industry  股票代码，
# db.market  行情，

'''
industry{
date:
code:
name:
industry:
industryclass
}

market{
createdate:
type: 1,macd,2rsi,3kdj,4 boll
signaldate:
signaltype:1.buy,2,sell
score:0-100 分数 分数越大表面该信号越强， signaltype=1，100分 表示强买信号，金叉
       signaltype=2，100分表示强卖信号。 死叉
code:股票代码
name:股票名称
}

'''

def insertIndustry(date,code,name,industry,industryclass):
    industry = {
    'date':date,
    'code':code,
    'name':name,
    'industry':industry,
    'industryclass':industryclass
    }

    isExist = getIndustry(0,code)
    if isExist == None:
        db.industry.insert_one(industry)

def getIndustry(Id,code=None):
    if code:
        return db.industry.find_one({"code":code})


    return db.industry.find_one({"_id":Id})

def getIndustrys():
    return db.industry.find()


def insertMarket(indextype,signaldate,signaltype,score,code,name):
    m = {
    'createdate':str(datetime.date.today()),
    'type':indextype,
    'signaldate':signaldate,
    'signaltype':signaltype,
    'name':name,
    'code':code,
    'score':score
    }
    isExist = getMarket(0,indextype,signaldate,code)
    if isExist == None:
        db.market.insert_one(m)

def getMarket(Id,indextype=None,signaldate=None,code=None):
    if indextype:
        return db.market.find_one({
        'type':indextype,
        'signaldate':signaldate,
        'code':code
        })
    return db.market.find({'_id':Id})
