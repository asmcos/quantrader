import time
import requests
import demjson
import re
import pandas as pd

url = "http://q.jrjimg.cn/?q=cn|bk|17&n=hqa&c=l&o=pl,d&p=1020&_dc=%d" % int(time.time()*1000)

resp = requests.get(url)

data = re.findall("var hqa=(.+);",resp.text,re.M|re.S)
if(len(data) > 0):
	data = data[0]
jsondata = demjson.decode(data)

df = pd.DataFrame(jsondata['HqData'])

print(df.loc[:,[1,2,6,7,8,10,14,16]])
