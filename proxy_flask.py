#!/usr/bin/env python
from flask import Flask, request, Response, send_from_directory
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
from pytdx.hq import TdxHq_API
# from sendrequest_task import handle_task
from sendrequest import handle_task
#from requests.models import Response

tdxapi = TdxHq_API()

bridge = ["wss://bridge.duozhutuan.com/cacherelay", "wss://43.136.70.238/cacherelay"]


block_list = tdxblock.block_list

session = requests.Session()

from common.framework import init_stock_list, getstockinfo

code_list = {}


def get_finance(code):
    tdxapi.connect('119.147.212.81', 7709)
    zone,code = code[:2],code[2:]
    if zone == "sh":
        zone = 1
    else:
        zone = 0
    ret = tdxapi.get_finance_info(zone, code)
    return json.dumps(dict(ret))


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


# tdx 板块信息只有 个股code对应板块名
# 因此要获取code和股票名的 对应表
alllist = init_stock_list()
for i in alllist:
    code, name, tdxbk, tdxgn = getstockinfo(i)
    key = code.split('.')[1]
    code_list[key] = code

hostname = 'http://data.10jqka.com.cn'
proxyhost = "https://api.klang.org.cn"

root_path = sys.path[0]
path_map = {}


def set_pathmap(path, target):
    global path_map
    path_map[path] = target


def get_pathmap(path):
    for k in path_map.keys():
        if re.search(k, path) is not None:
            return path_map[k]
    return hostname


before_call = {}


def set_before(path, callback):
    global before_call
    before_call[path] = callback


def call_before(headers, path):
    for k in before_call.keys():
        if re.search(k, path) is not None:
            return before_call[k](headers)
    return headers


after_call = {}


def set_after(path, callback):
    global after_call
    after_call[path] = callback


def call_after(resp, path):
    for k in after_call.keys():
        if re.search(k, path) is not None:
            return after_call[k](resp)
    return resp.content


hexin_v = ""


app = Flask(__name__)
file_paths = ['/gn.html', '/gncookie.html', '/zx.html', '/klinebk.html', '/bk.json', '/etf.html', '/kline.html']

# 定义根目录
root_path = os.path.dirname(os.path.abspath(__file__))

def browser_file(filename):
    
    file_path = os.path.join(root_path, filename)
    # 检查文件是否存在
    if os.path.exists(file_path) and os.path.isfile(file_path):
       return send_from_directory(root_path, filename)
    else:
       return "File not found", 404

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    if request.method == 'GET':
        return handle_get_request(path)
    elif request.method == 'POST':
        return handle_post_request(path)


def handle_get_request(path):
    headers = dict(request.headers)
    
    if "/" + path in file_paths:
        return browser_file(path)


    query_params = request.args
    # 构建完整的请求路径，包含查询参数
    full_path = "/" + path
    if query_params:
        full_path += '?' + request.query_string.decode('utf-8')

    if full_path == "":
        return "Path not found", 404

    headers = call_before(headers, full_path)
    host = get_pathmap(full_path)
    if host is None:
        return "Path not found", 404
    url = '{}/{}'.format(host, path)

    headers['Host'] = host.split("//")[1]
    headers['Referer'] = url
    print(url,headers,query_params)
    resp = session.get(url, headers=headers,params=query_params)
    resp_content = call_after(resp, full_path)

    response = Response(resp_content,resp.status_code)
    
    for key, value in resp.headers.items():
        if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length',
                       'Content-Length']:
            response.headers[key] = value
    response.headers['Content-Length'] = len(resp_content)

    try:
        referer = request.headers.get('Referer', '')
        scheme = urlparse(referer).scheme
        netloc = urlparse(referer).netloc
        # response.headers['Access-Control-Allow-Origin'] = scheme + "://" + netloc
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    except:
        response.headers['Access-Control-Allow-Origin'] = "*"

    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'

    return response


def handle_post_request(path):
    headers = dict(request.headers)
    headers = call_before(headers, path)

    target_url = get_pathmap(path)
    if target_url is None:
        return "Path not found", 404

    data = request.get_data()
    resp = session.post(target_url, headers=headers, data=data)
    resp_content = call_after(resp, path)

    response = Response(resp_content)
    for key, value in resp.headers.items():
        if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length',
                       'Content-Length']:
            response.headers[key] = value
    response.headers['Content-Length'] = len(resp_content)

    try:
        referer = request.headers.get('Referer', '')
        scheme = urlparse(referer).scheme
        netloc = urlparse(referer).netloc
        # response.headers['Access-Control-Allow-Origin'] = scheme + "://" + netloc
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    except:
        response.headers['Access-Control-Allow-Origin'] = "*"

    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'

    return response


def parse_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Proxy HTTP requests')
    parser.add_argument('--port', dest='port', type=int, default=9999,
                        help='serve HTTP requests on specified port (default: random)')
    args = parser.parse_args(argv)
    return args


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    print('http server is starting on port {}...'.format(args.port))
    app.run(host='0.0.0.0', port=args.port)


################################
#
# 需要定制修改的内容
#
################################

def config():
    def modify_gn(resp):
        path = request.path
        print(path, "modify gn code")
        content = re.sub("http://q.10jqka.com.cn/gn/detail/code/", proxyhost + "/gn/detail/code/", resp.text,
                         flags=re.I | re.S)
        return content.encode('gbk')

    def modify_gnzjl(resp):
        path = request.path
        print(path, "get gn 50 table ")
        content = re.sub("http://q.10jqka.com.cn/gn/detail/code/", proxyhost + "/gn/detail/code/", resp.text,
                         flags=re.I | re.S)
        content1 = re.findall("<table.*?table>", content, re.I | re.S)[0]
        return content1.encode('gbk')

    def modify_bkcode(resp):
        path = request.path
        if resp.status_code == 401:
            return resp.text.replace("q.10jqka.com.cn",request.host)

        print(path, request.headers)

        if len(re.findall("<table.*?table>", resp.text, re.I | re.S)) < 1:
            return resp.content

        content = re.findall("<table.*?table>", resp.text, re.I | re.S)[0]
        df = pd.read_html(content, converters={'代码': str}, index_col=0)[0]
        df = df.drop(['涨跌', '涨速(%)', '换手(%)', '量比', '振幅(%)', '成交额', '流通股', '市盈率', ], axis=True)

        df['流通市值'] = df['流通市值'].apply(create_color_hqltgz)
        df['代码'] = df['代码'].apply(create_clickable_code)
        df['涨跌幅(%)'] = df['涨跌幅(%)'].apply(create_color_rise)

        pages = re.findall(r'page="(\d+)"', resp.text, re.I | re.S)
        print(pages)

        return df.to_html(escape=False, float_format='%.2f').encode('gbk')  # resp.content

    def modify_etf(resp):
        path = request.path
        print(path, "etf")
        content = re.findall(r"g\(({.*})\)", resp.text, re.I | re.S)[0]
        datas = []
        content = json.loads(content).get('data').get('data')
        for d in content.keys():
            datas.append(content[d])
        return json.dumps(datas).encode('gbk')

    def modify_sina(reqHeader):
        newHeader = reqHeader
        headers = {
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Dest': 'script',
            'Referer': 'http://finance.sina.com.cn/realstock/company/sh000001/nc.shtml',
            'Host': 'hq.sinajs.cn',
        }
        for k in headers:
            newHeader[k] = headers[k]
        return newHeader

    def modify_before_gn(reqHeader):
        newHeader = reqHeader
        if len(hexin_v) > 0:
            newHeader["hexin-v"] = hexin_v

        return newHeader

    set_after(r'/funds/gnzjl/field/tradezdf/order/desc/page/(\d+)/ajax/1/free/1/', modify_gn)
    set_after(r'/funds/gnzjl/field/tradezdf/order/desc/ajax/(\d+)/free/1/', modify_gn)
    set_after('/funds/gnzjl/$', modify_gnzjl)
    set_pathmap('/gn/detail/code', 'https://q.10jqka.com.cn')

    set_pathmap('/gn/detail/field/', 'https://q.10jqka.com.cn')
    set_before('/gn/detail/field', modify_before_gn)
    set_after('/gn/detail/field/', modify_bkcode)

    set_pathmap('/data/Net/info/ETF_F009_desc_0_0_1_9999_0_0_0_jsonp_g.html', 'http://fund.ijijin.cn')
    set_after('/data/Net/info/ETF_F009_desc_0_0_1_9999_0_0_0_jsonp_g.html', modify_etf)

    set_pathmap('list=', 'https://hq.sinajs.cn')
    set_before('list=', modify_sina)
    set_pathmap('data/index.php', 'https://stock.gtimg.cn')
    set_pathmap('cn/api/json_v2.php', 'https://quotes.sina.cn')
    set_pathmap('s3/', 'https://smartbox.gtimg.cn')
    set_pathmap('/realstock/company', 'https://finance.sina.com.cn')


if __name__ == '__main__':
    config()
    main()

