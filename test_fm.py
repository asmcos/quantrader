from common.framework import *


def testcb(code,name,datas):
    print(code,name,datas)

if __name__ == "__main__":
    init_stock_list()
    loop_all(testcb)
