# mongodb by pymongo
# python3 不用coding utf-8 支持中文了。
from pymongo import MongoClient
import datetime

#Step 1: Connect to MongoDB - Note: Change connection string as needed
client = MongoClient('mongodb://localhost:27017/')

db = client.stock # databasename

# collection name
# db.day  股票代码，
# db.upordown  行情，

'''
dayK{
date:
code:
name:
close:
open:
high:
low:
volume:
}

upordown{
date:
code:
name:
close:
close1:
close20:
close100:
delta1:
delta100:
deltal20:
}

'''
#'open', 'high', 'low', 'close', 'volume'
def insertdayK(name,code,date,openk,high,low,close,volume):
    dayK = {
		'date':date,
		'code':code,
		'name':name,
		'close':close,
		'open':openk,
		'high':high,
		'low':low,
		'volume':volume,
	}

    db.dayK.find_and_modify(query={'code':code,'date':date}, update={"$set": dayK}, upsert=True)

def insertdayKs(name,code,datas):
	querys = []
	dates = []
	existdates = []
	for i in datas:
		dates.append(i[0])
	
	exists = db.dayK.find({'date':{'$in':dates},'code':code})
	for i in exists:
		existdates.append(i["date"])

	for i in datas:
		if i[0] not in existdates:
			querys.append({"name":name,"code":code,
         		"date":i[0],
         		"open":i[1],
         		"high":i[2],
         		"low":i[3],
         		"close":i[4],
         		"volume":i[5],
        	})	
	if len(querys) > 0:
		db.dayK.insert_many(querys)	

	print("%s %s 增加了%d 条数据" %(name,code,len(querys)))
	
def getdayK(code,date):
     return db.dayK.find_one({"code":code,'date':date})





