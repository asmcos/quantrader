#!/usr/bin/env python
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import os
import random
import sys
import requests
import re
import traceback
import pandas as pd
import json
from urllib.parse import urlparse
import tdxbk as tdxblock
import time
import threading
block_list = tdxblock.block_list

session=requests.Session()

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


from common.framework import init_stock_list, getstockinfo,get_chouma

code_list = {}

def create_clickable_code(code):
    code = code_list.get(code,code).replace('.','')
    url_template= '''<a href="https://klang.org.cn/kline.html?code={code}" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template

def create_color_hqltgz(hqltsz):
    
    hqltsz = float(hqltsz.split('亿')[0])
    if hqltsz >= 200.0:
        url_template= '''<font color="#ef4136">{hqltsz}</font></a>'''.format(hqltsz=hqltsz)
    else:
        url_template = '''{hqltsz}'''.format(hqltsz=hqltsz)
    return url_template

def create_color_rise(rise):
    try: 
        rise = float(rise)
    except:
        rise = 0
    if rise >= 0.0:
        url_template= '''<font color="#ef4136">+{rise}</font></a>'''.format(rise=rise)
    else:
        url_template= '''<font color="#41ef36">{rise}</font></a>'''.format(rise=rise)
    return url_template



def create_chouma(code):
    chouma = str(get_chouma(code_list.get(code,code)))
    code = code_list.get(code,code).replace('.','')
    return """<a href="https://gu.qq.com/"""+code+'''" target="_blank">''' +chouma+"""</a>"""

#tdx 板块信息只有 个股code对应板块名
#因此要获取code和股票名的 对应表
alllist = init_stock_list()
for i in alllist:
    code,name,tdxbk,tdxgn = getstockinfo(i)
    key = code.split('.')[1]
    code_list[key] = code



hostname = 'http://data.10jqka.com.cn'
proxyhost = "https://api.klang.org.cn"

root_path = sys.path[0]
path_map ={}

def set_pathmap(path,target):
    global path_map 

    path_map[path] = target

def get_pathmap(path):

    for k in path_map.keys():
        if re.search(k,path) != None:
            return path_map[k]

    return hostname


before_call = {}

def set_before(path,callback):
    global before_call

    before_call[path] = callback

def call_before(self,headers):

    for k in before_call.keys():
        if re.search(k,self.path) != None:
            return before_call[k](self,headers)

    return headers

after_call = {}

def set_after(path,callback):
    global after_call

    after_call[path] = callback

def call_after(self,resp):

    for k in after_call.keys():
        if re.search(k,self.path) != None:
            return after_call[k](self,resp)

    return resp.content

hexin_v = ""

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
        sent = False
        try: #split("?") 删除参数
            if self.path.split("?")[0] in ['/gn.html','/gncookie.html','/zx.html',
                                           '/klinebk.html','/bk.json','/etf.html','/kline.html']:
                # bk.json 使用tdxbk.py生成
                gncontent = open(root_path + self.path.split("?")[0]).read()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-Length', len(gncontent.encode()))
                self.end_headers()

                self.wfile.write(gncontent.encode())
                return
            if self.path.split("?")[0] in ["/blocklist"]:
                threading.Thread(target=tdxblock.connect).start()

                content = json.dumps(block_list).encode('utf-8')

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
                return
            if self.path.split("?")[0] in ["/block"]:
                time.sleep(100) # 100ms
                params = self.path.split("?")[1]
                code = params.split("&")[0]
                name = params.split("&")[1]
                jsondata = tdxblock.get_block_bar(code,name)
                content  =  json.dumps(jsondata).encode('utf-8')

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
                return

            host = get_pathmap(self.path)
            url = '{}{}'.format(host, self.path)
            req_header = self.parse_headers()
            req_header = call_before(self,req_header)

            print(req_header)
            print(self.path)

            resp = session.get(url, headers= req_header)
            sent = True

            content = call_after(self,resp)

            self.send_response(resp.status_code)
            self.send_resp_headers(resp,content)
            if body:
                self.wfile.write(content)
            return

        except Exception as e:
            print ('str(Exception):\t', str(Exception))
            print ('str(e):\t\t', str(e))
            print ('repr(e):\t', repr(e))
            print ('traceback.print_exc():\n')
            traceback.print_exc()
            print ('traceback.format_exc():\n%s' % traceback.format_exc())

            # 发现有些网站第一次不成功需要第二次才能成功。所以再试一次
            resp = session.get(url, headers= req_header)
            sent = True

            content = call_after(self,resp)

            self.send_response(resp.status_code)
            self.send_resp_headers(resp,content)
            if body:
                self.wfile.write(content)
            return






    def do_POST(self, body=True):
        sent = False
        try:
            host = get_pathmap(self.path)
            url = '{}{}'.format(host, self.path)
            print(self.path)
            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len)
            post_body = json.loads(post_body)
            req_header = self.parse_headers()
            req_header = call_before(self,req_header)
            if post_body.get("parserData") == None:
                resp = session.post(url, data=post_body, headers= req_header)
    
                sent = True
                content = call_after(self,resp)
            else:
                # 获取一个空的resp
                resp = session.get("http://127.0.0.1/test")
                sent = True
                resp.headers['Content-Type'] = "text/html;charset=gbk"
                resp.status_code = 200
                class Resp():
                    def __init__(self):
                        pass
                resp1 = Resp()
                resp1.status_code = 200
                resp1.text = post_body['data']
                content = call_after(self,resp1)

            self.send_response(resp.status_code)
            self.send_resp_headers(resp,content)
            if body:
                self.wfile.write(content)
            return
        except Exception as e:
            print ('str(Exception):\t', str(Exception))
            print ('str(e):\t\t', str(e))
            print ('repr(e):\t', repr(e))
            #print ('e.message:\t', e.message)
            print ('traceback.print_exc():\n')
            traceback.print_exc()
            print ('traceback.format_exc():\n%s' % traceback.format_exc())

    def parse_headers(self):
        global hexin_v
        del self.headers['Host']
        host = get_pathmap(self.path)
        self.headers['Host'] = host.split("://")[1]
        del self.headers["User-Agent"]
        self.headers["User-Agent"]= "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"

        del self.headers["Referer"]
        self.headers["Referer"]= "http://127.0.0.1:999/"

        if self.headers.get('cook',None):
            self.headers["Cookie"] = self.headers.get('cook');


        if self.headers.get("hexin-v",None):
            hexin_v = self.headers.get("hexin-v")

        return self.headers #req_header


    def send_resp_headers(self, resp,content):
        respheaders = resp.headers
        print ('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                #print (key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', len(content))
        try:
            scheme = urlparse(self.headers['Referer']).scheme
            netloc = urlparse(self.headers['Referer']).netloc
            #self.send_header('Access-Control-Allow-Origin', scheme+"://"+netloc);
            self.send_header('Access-Control-Allow-Origin', "*");
            self.send_header('Access-Control-Allow-Credentials','true');
        except:
            self.send_header('Access-Control-Allow-Origin', "*");

        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'); 
        self.end_headers()




def parse_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Proxy HTTP requests')
    parser.add_argument('--port', dest='port', type=int, default=9999,
                        help='serve HTTP requests on specified port (default: random)')
    args = parser.parse_args(argv)
    return args

def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    print('http server is starting on port {}...'.format(args.port))
    server_address = ('0.0.0.0', args.port)
    httpd = ThreadingSimpleServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running as reverse proxy')
    httpd.serve_forever()

################################
#
# 需要定制修改的内容
#
################################

def config():

    def modify_gn(self,resp):
        path = self.path
        print(path,"modify gn code")
        content = re.sub("http://q.10jqka.com.cn/gn/detail/code/",proxyhost+"/gn/detail/code/",resp.text,flags = re.I|re.S)
        return content.encode('gbk') 

    def modify_gnzjl(self,resp):
        path = self.path
        print(path,"get gn 50 table ")
        content = re.sub("http://q.10jqka.com.cn/gn/detail/code/",proxyhost+"/gn/detail/code/",resp.text,flags = re.I|re.S)
        content1 = re.findall("<table.*?table>",content,re.I|re.S)[0]
        return content1.encode('gbk') 

    def modify_bkcode(self,resp):
        path = self.path
        
        print(path,self.headers)

        if len(re.findall("<table.*?table>",resp.text,re.I|re.S)) < 1:
            return resp.content

        content = re.findall("<table.*?table>",resp.text,re.I|re.S)[0]
        df = pd.read_html(content,converters={'代码': str},index_col=0)[0]
        df = df.drop(['涨跌',  '涨速(%)',  '换手(%)' ,    '量比',  '振幅(%)'  \
            ,'成交额'    ,'流通股'     ,'市盈率'  ,'加自选'],axis=True)

        df['流通市值'] = df['流通市值'].apply(create_color_hqltgz) 
        #df['筹码'] = df['代码'].apply(create_chouma) 
        df['代码'] = df['代码'].apply(create_clickable_code) 
        df['涨跌幅(%)'] = df['涨跌幅(%)'].apply(create_color_rise)

        pages = re.findall('page="(\d+)"',resp.text,re.I|re.S)
        print(pages)

        return df.to_html(escape=False,float_format='%.2f').encode('gbk') #resp.content 

    def modify_etf(self,resp):
        path = self.path
        print(path,"etf")
        content = re.findall("g\(({.*})\)",resp.text,re.I|re.S)[0]
        datas  = []
        content = json.loads(content).get('data').get('data')
        for d in content.keys():
            datas.append(content[d])
        return json.dumps(datas).encode('gbk') 


    def modify_sina(self,reqHeader):
        newHeader = reqHeader
        headers = {
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Dest': 'script',
            'Referer': 'http://finance.sina.com.cn/realstock/company/sh000001/nc.shtml',
        }       
        for k in headers:
            newHeader[k] = headers[k]
        return newHeader
        
        
    def modify_before_gn(self,reqHeader):
        newHeader = reqHeader
        if len(hexin_v) > 0: 
            newHeader["hexin-v"] = hexin_v
 
        return newHeader

    set_after('/funds/gnzjl/field/tradezdf/order/desc/page/(\d+)/ajax/1/free/1/',modify_gn)
    set_after('/funds/gnzjl/field/tradezdf/order/desc/ajax/(\d+)/free/1/',modify_gn)
    set_after('/funds/gnzjl/$',modify_gnzjl)
    set_pathmap('/gn/detail/code','http://q.10jqka.com.cn')

    set_pathmap('/gn/detail/field/','http://q.10jqka.com.cn')
    set_before('/gn/detail/field',modify_before_gn)
    set_after('/gn/detail/field/',modify_bkcode)

    set_pathmap('/data/Net/info/ETF_F009_desc_0_0_1_9999_0_0_0_jsonp_g.html','http://fund.ijijin.cn')
    set_after('/data/Net/info/ETF_F009_desc_0_0_1_9999_0_0_0_jsonp_g.html',modify_etf)

    set_pathmap('list=','https://hq.sinajs.cn')
    set_before('list=',modify_sina)
    set_pathmap('data/index.php','https://stock.gtimg.cn')
    set_pathmap('cn/api/json_v2.php','https://quotes.sina.cn')
    set_pathmap('s3/','https://smartbox.gtimg.cn')
    set_pathmap('/realstock/company','https://finance.sina.com.cn')

if __name__ == '__main__':
    config()

    main()
