import baostock as bs
import pandas as pd
import dbmongo

# 登陆系统
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
	print(row)
	kdata = bs.query_history_k_data_plus(row[1], 'date,open,high,low,close,volume', start_date='2020-12-01', 
                                      frequency='d')	
	if len(kdata.get_row_data()) == 0:
		continue
	industry_list.append(row)	
	""" default don't save to mongodb
	dbmongo.insertIndustry(industry_list[-1][0],
    industry_list[-1][1],
    industry_list[-1][2],
    industry_list[-1][3],
    industry_list[-1][4])
	"""
result = pd.DataFrame(industry_list, columns=rs.fields)
# 结果集输出到csv文件
result.to_csv("./datas/stock_industry_check.csv", index=False)
print(result)

# 登出系统
bs.logout()
