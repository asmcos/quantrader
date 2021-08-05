#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import os
import random
import sys
import requests
import re
import traceback
import pandas as pd

from common.framework import init_stock_list, getstockinfo,get_chouma

code_list = {}

def create_clickable_code(code):
    url_template= '''<a href="https://gu.qq.com/{code}" target="_blank"><font color="blue">{code}</font></a>'''.format(code=code)
    return url_template

def create_color_hqltgz(hqltsz):
    
    hqltsz = float(hqltsz.split('亿')[0])
    if hqltsz >= 200.0:
        url_template= '''<font color="#ef4136">{hqltsz}</font></a>'''.format(hqltsz=hqltsz)
    else:
        url_template = '''{hqltsz}'''.format(hqltsz=hqltsz)
    return url_template

def create_chouma(code):
    chouma = str(get_chouma(code_list.get(code,code)))
    return chouma

#tdx 板块信息只有 个股code对应板块名
#因此要获取code和股票名的 对应表
alllist = init_stock_list()
for i in alllist:
    code,name,tdxbk,tdxgn = getstockinfo(i)
    key = code.split('.')[1]
    code_list[key] = code



hostname = 'http://data.10jqka.com.cn'

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

def call_before(path,headers):

    for k in before_call.keys():
        if re.search(k,path) != None:
            return before_call[k](path,headers)

    return headers

after_call = {}

def set_after(path,callback):
    global after_call

    after_call[path] = callback

def call_after(path,resp):

    for k in after_call.keys():
        if re.search(k,path) != None:
            return after_call[k](path,resp)

    return resp.content


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
        sent = False
        try:
            if (self.path == '/gn.html'):
                gncontent = open('gn.html').read()

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-Length', len(gncontent.encode()))
                self.end_headers()

                self.wfile.write(gncontent.encode())
                return

            host = get_pathmap(self.path)
            url = '{}{}'.format(host, self.path)
            req_header = self.parse_headers()

            print(req_header)
            print(self.path)
            req_header = call_before(self.path,req_header)
            resp = requests.get(url, headers= req_header, verify=False)
            sent = True

            content = call_after(self.path,resp)

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


    def do_POST(self, body=True):
        sent = False
        try:
            host = get_pathmap(self.path)
            url = '{}{}'.format(host, self.path)
            print(self.path)
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            req_header = self.parse_headers()

            req_header = call_before(self.path,req_header)
            resp = requests.post(url, data=post_body, headers= req_header, verify=False)
            sent = True

            content = call_after(self.path,resp)
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
        del self.headers['Host']
        host = get_pathmap(self.path)
        self.headers['Host'] = host.split("://")[1]

        return self.headers #req_header


    def send_resp_headers(self, resp,content):
        respheaders = resp.headers
        print ('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                print (key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', len(content))
        self.end_headers()
        #self.send_header('Access-Control-Allow-Origin', '*')
        #self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')




def parse_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Proxy HTTP requests')
    parser.add_argument('--port', dest='port', type=int, default=9999,
                        help='serve HTTP requests on specified port (default: random)')
    args = parser.parse_args(argv)
    return args

def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    print('http server is starting on port {}...'.format(args.port))
    server_address = ('127.0.0.1', args.port)
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running as reverse proxy')
    httpd.serve_forever()

################################
#
# 需要定制修改的内容
#
################################

def config():

    def modify_gn(path,resp):
        print(path,"modify gn code")
        content = re.sub("http://q.10jqka.com.cn/gn/detail/code/","http://127.0.0.1:9999/gn/detail/code/",resp.text,flags = re.I|re.S)
        return content.encode('gbk') 

    def modify_gnzjl(path,resp):
        print(path,"get gn 50 table ")
        content = re.sub("http://q.10jqka.com.cn/gn/detail/code/","http://127.0.0.1:9999/gn/detail/code/",resp.text,flags = re.I|re.S)
        content1 = re.findall("<table.*?table>",content,re.I|re.S)[0]
        return content1.encode('gbk') 

    def modify_bkcode(path,resp):
        print(path,"get bkcode ")
        content = re.findall("<table.*?table>",resp.text,re.I|re.S)[0]
        df = pd.read_html(content,converters={'代码': str})[0]
        df = df.drop(['涨跌',  '涨速(%)',  '换手(%)' ,    '量比',  '振幅(%)'  \
            ,'成交额'    ,'流通股'     ,'市盈率'  ,'加自选'],axis=True)

        df['流通市值'] = df['流通市值'].apply(create_color_hqltgz) 
        df['筹码'] = df['代码'].apply(create_chouma) 
        df['代码'] = df['代码'].apply(create_clickable_code) 

        return df.to_html(escape=False,float_format='%.2f').encode('gbk') #resp.content 


    set_after('/funds/gnzjl/field/tradezdf/order/desc/page/(\d+)/ajax/1/free/1/',modify_gn)
    set_after('/funds/gnzjl/field/tradezdf/order/desc/ajax/(\d+)/free/1/',modify_gn)
    set_after('/funds/gnzjl/$',modify_gnzjl)
    set_pathmap('/gn/detail/code','http://q.10jqka.com.cn')
    set_pathmap('/gn/detail/field/','http://q.10jqka.com.cn')
    set_after('/gn/detail/field/',modify_bkcode)

if __name__ == '__main__':
    config()

    main()
