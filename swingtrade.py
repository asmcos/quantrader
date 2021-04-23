#波段交易

from common.framework import *

result_list = []

#近似值，考虑有一点浮动
approx = 0.05

def up(datas):
    a = datas[-1][2]
    b = datas[-2][2]
    c = datas[-3][2]
    approx = 1 - approx 
    if (a*approx >b and b*approx > c):
        return True
    else :
        return False

def swing(code,name,datas):
    print(code,name)
    mlist = [] #max
    nlist = [] #min

    if len(datas)<7:
        return
    mnlist = get_mnlist(datas,7)
    mnlist1 = []
    length = len(mnlist)

    # 寻找一个强上升趋势 上升空间 20%

    for i in range(0,len(mnlist)-1):
        if mnlist[i][0] == 0 and mnlist[i+1][0] == 1:    
            a = mnlist[i][2] #close value
            b = mnlist[i+1][2] # close value
            if (b / a) > 1.5:
                print(OKRED,b / a ,a,b,ENDC)
                mnlist1 = mnlist[i:]                
                break
    
    if len(mnlist1) < 3:
        return

    #将列表分离 最大 和最小分开     
    for i in mnlist1:
        if i[0] == 1:
            mlist.append(i)
        if i[0] == 0:
            nlist.append(i)

    if len(nlist) < 3:
        return 


    #查找最小值是不是趋势向上的
    count = 0
    for i in range(2,len(nlist)):
        if up(nlist[i-2:i+1]):
            count +=1
        else:
            count = 0
        if count > 1:
            print(OKBLUE,name,code,nlist[i-2][2],nlist[i-1][2],nlist[i][2],ENDC)

def display():
    for i in result_list:
        print(i)

def save():
        df = pd.DataFrame(result_list ,columns = ['name','code','date','9转第N天','流通股值'])
        save_df_tohtml('./datas/stock_'+endday+"swing.html",df)

if __name__ == "__main__":
    init_stock_list()
    loop_all(swing)
    display()
