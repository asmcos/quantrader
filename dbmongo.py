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
rsi:
kdj:
code:股票代码
name:股票名称
}

backtest{
code,
name,
startdate
enddate
testdate
startvalue
finalvalue
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


def insertMarket(indextype,signaldate,signaltype,rsi,kdj,code,name):
    m = {
    'createdate':str(datetime.date.today()),
    'type':indextype,
    'signaldate':signaldate,
    'signaltype':signaltype,
    'name':name,
    'code':code,
    'rsi':rsi,
    'kdj':kdj
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

def Newbacktest(code,name,start,end,startvalue,finalvalue,testdate=None):
    query = {'code':code,
        'startdate':start,
        'enddate':end,
        }

    if db.backtest.find_one(query) == None:
        if testdate == None:
            testdate = str(datetime.date.today())

        db.backtest.insert_one(
        {
            'code':code,
            'name':name,
            'startdate':start,
            'enddate':end,
            'testdate':testdate,
            'startvalue':startvalue,
            'finalvalue':finalvalue
        }
        )

def get_all_backtest(start,end,testdate=None):
    if testdate == None:
        query = {
                'startdate':start,
                'enddate':end,
                }
    else :
        query = {'testdate':testdate,
                'startdate':start,
                'enddate':end,
                }
    return db.backtest.find(query)
