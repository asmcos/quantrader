import baostock as bs
import pandas as pd
import os
import tdxhy
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

# 打印结果集
industry_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    row = rs.get_row_data()
    kdata = bs.query_history_k_data_plus(row[1], 'date,open,high,low,close,volume', start_date='2020-12-01', 
                                      frequency='d')	
    if len(kdata.get_row_data()) == 0:
        continue
    """
    #增加流通值
    rs_profit = bs.query_profit_data(code=row[1],year=2020)
    rs_row = rs_profit.get_row_data()
    if len(rs_row)> 0:
        row.append(rs_row[-1])
        print(rs_row)
    else:
        row.append(0)
    """
    tdxbk = tdxhy.gettdxbk(row[1])
    tdxgn = tdxhy.gettdxgn(row[1])
    row.append(tdxbk)
    row.append(tdxgn)
    print(row)
    industry_list.append(row)	

fields = rs.fields
fields.append('tdxbk')
fields.append('tdxgn')

#rs.fields.append('流通值')
result = pd.DataFrame(industry_list, columns=rs.fields)
# 结果集输出到csv文件
filename_sl = os.path.expanduser("~/.klang_stock_list.csv")
result.to_csv(filename_sl, index=False)
print(result)

# 登出系统
bs.logout()
