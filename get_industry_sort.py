import time
import requests
import demjson
import re
import pandas as pd

url = "http://q.jrjimg.cn/?q=cn|bk|17&n=hqa&c=l&o=pl,d&p=1020&_dc=%d" % int(time.time()*1000)
urlbk = "http://q.jrjimg.cn/?q=cn|s|bk%s&c=m&n=hqa&o=pl,d&p=1020&_dc=%d"

def getbktop20():
	resp = requests.get(url)

	data = re.findall("var hqa=(.+);",resp.text,re.M|re.S)
	if(len(data) > 0):
		data = data[0]
	jsondata = demjson.decode(data)

	df = pd.DataFrame(jsondata['HqData'])

	bkdf = df.loc[:,[1,2,6,7,8,10,14,16]]
	return bkdf

def create_clickable_code(code):
    code = code.replace(".","")
    url_template= '''<a href="http://quote.eastmoney.com/{code}.html" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template
def create_clickable_name(name):
    url_template= '''<a href="http://so.eastmoney.com/News/s?keyword={name}" target="_blank"><font color="blue">{name}</font></a>'''.format(name=name)
    return url_template

def create_color_rise(rise):
    url_template= '''<font color="#ef4136">{rise}</font></a>'''.format(rise=rise)
    return url_template


def getonebkinfo(bkcode,bkname):
	print(bkname)
	resp = requests.get(urlbk%(bkcode,int(time.time()*1000)))
	data = re.findall("var hqa=(.+);",resp.text,re.M|re.S)
	if(len(data) > 0):
		data = data[0]
	jsondata = demjson.decode(data)

	df = pd.DataFrame(jsondata['HqData'])
	df[0] = df[0].apply(create_clickable_code)
	df[12] = df[12].apply(create_color_rise)

	print(df.loc[:,[0,1,2,8,12]].to_html(escape=False))	

bkdf = getbktop20()
print(bkdf.to_html(escape=False))

for i in range(len(bkdf)):
	bkcode = bkdf[1][i]
	bkname = bkdf[2][i]
	getonebkinfo(bkcode,bkname)
