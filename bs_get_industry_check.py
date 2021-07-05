import baostock as bs
import pandas as pd
import os
# 登录系统
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

# 获取行业分类数据
rs = bs.query_stock_industry()
# rs = bs.query_stock_basic(code_name="浦发银行")
print('query_stock_industry error_code:'+rs.error_code)
print('query_stock_industry respond  error_msg:'+rs.error_msg)

filename_sl = os.path.expanduser("~/.klang_stock_list.csv")

if not os.path.exists(filename_sl):
    # 打印结果集
    industry_list = []

    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        row = rs.get_row_data()
        kdata = bs.query_history_k_data_plus(row[1], 'date,open,high,low,close,volume', start_date='2020-12-01', 
                                      frequency='d')	
        if len(kdata.get_row_data()) == 0:
            continue
        tdxbk = ""#tdxhy.gettdxbk(row[1])
        tdxgn = ""#tdxhy.gettdxgn(row[1])
        row.append(tdxbk)
        row.append(tdxgn)
        print(row)
        industry_list.append(row)	

    fields = rs.fields
    fields.append('tdxbk')
    fields.append('tdxgn')

    result = pd.DataFrame(industry_list, columns=rs.fields)
    # 结果集输出到csv文件
    result.to_csv(filename_sl, index=False)
    print(result)
else:    

    import tdxhy
    # 打印结果集
    industry_list = []

    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        row = rs.get_row_data()
        kdata = bs.query_history_k_data_plus(row[1], 'date,open,high,low,close,volume', start_date='2020-12-01', 
                                      frequency='d')	
        if len(kdata.get_row_data()) == 0:
            continue
        tdxbk = tdxhy.gettdxbk(row[1])
        tdxgn = tdxhy.gettdxgn(row[1])
        row.append(tdxbk)
        row.append(tdxgn)
        print(row)
        industry_list.append(row)	

    fields = rs.fields
    fields.append('tdxbk')
    fields.append('tdxgn')

    result = pd.DataFrame(industry_list, columns=rs.fields)
    # 结果集输出到csv文件
    result.to_csv(filename_sl, index=False)
    print(result)


# 登出系统
bs.logout()
