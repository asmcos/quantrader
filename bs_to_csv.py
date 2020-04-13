#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

""" 从baostock获取daily数据到datas目录下的csv文件当中，文件名如：bs_sh.000001.csv """
""" python3 bs_to_csv.py --code sh.600600 """
import baostock as bs
import pandas as pd
import click

""" 函数参数装饰器 """
@click.command()
@click.option("--code", default="sh.600000", help="baostock股票/指数代码，如sh.600000")
@click.option("--start", default="2010-01-01", help="开始日期, 格式如：2010-01-01")
@click.option("--end", default="2020-03-01", help="结束日期, 格式如：2010-01-01")
@click.option("--adj", default="1", help="复权类型(只针对股票)：3: 未复权 2:前复权 1:后复权 , 默认1")
def get_data(code, start, end, adj):
    lg = bs.login()
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    rs = bs.query_history_k_data_plus(code, 'date,open,high,low,close,volume', start_date=start, end_date=end,
                                      frequency='d', adjustflag=adj)
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    data = pd.DataFrame(data_list, columns=rs.fields)

    columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    data.to_csv("./datas/bs_{0}.csv".format(code),
                           sep=',', index=False, columns=columns)


if __name__ == "__main__":
    get_data()
