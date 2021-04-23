from common.framework import *

result_list = []
#greater than 大于
def isgt(dts):
    i1 = dts.index[-1]
    i2 = dts.index[-2]
    i3 = dts.index[-3]
    i4 = dts.index[-4]
    i5 = dts.index[-5]

    if (dts.close[i1] > dts.close[i2]
        and 
       dts.close[i1] > dts.close[i3]
        and 
       dts.close[i1] > dts.close[i4]
        and 
       dts.close[i1] > dts.close[i5]):
        return True
    else:
        return False

#less than 小于
def islt(dts):
    pass

def td9(code,name,datas):
    print(code,name)
    gtstatus = 0
    ltstatus = 0
    if len(datas)<7:
        return
    for i in range(5,len(datas)):
        if isgt(datas[i-4:i+1]):
            gtstatus += 1
            if gtstatus > 3 and i == (len(datas)-1):
                turn = datas.turn[datas.index[i]]
                volume = datas.volume[datas.index[i]]
                hqltsz = float(datas.close[datas.index[i]]) * float(volume) / float(turn) / 1000000 
                hqltsz = float('%.2f' % hqltsz)
                print(OKBLUE,datas.date[datas.index[i]],gtstatus,turn,volume,hqltsz,ENDC)
                result_list.append([name,code,datas.date[datas.index[i]],gtstatus,hqltsz])
        else:
            gtstatus = 0

        islt(datas[i-5:i])
def display():
    for i in result_list:
        print(i)

def save():
        df = pd.DataFrame(result_list, columns = ['name','code','date','9转第N天','流通股值'])
        save_df_tohtml('./datas/stock_'+endday+"9dt.html",df)

if __name__ == "__main__":
    init_stock_list()
    loop_all(td9)
    display()
    save()
