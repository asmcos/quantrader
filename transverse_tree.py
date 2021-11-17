from Klang.lang import kparser,setPY,Kexec
from Klang import (Kl,
    C,O,V,H,L, CLOSE,HIGH,DATETIME,
    MA,CROSS,BARSLAST,HHV,COUNT,
    MAX,MIN,MACD,TRANSVERSE)
from Klang.common import end as today
import talib 

import sys
import linecache
import pandas as pd



def getpyglobals(name):
    return globals().get(name)

def setpyglobals(name,val):
    globals()[name]=val


setPY(getpyglobals,setpyglobals)

def getstockinfo(a):
    return Kl.currentdf['name'] + "-" + Kl.currentdf['code']

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

all_list = []
pred_data = 0
def main_loop(start,endday):
    offset = 60 #要计算MA60，所以之前的60不能计算
    check_day = 10

    if pred_data == 1:
        check_day = 0

    #for df in Kl.df_all[:500]:
    for df in Kl.df_all:

        Kl.code(df["code"])

        if start is None:
            Kl.date(end=endday)
        else:
            Kl.date(start=start,end=endday)
        try:
            if len(C) < 70:
                continue

            allC = C.data

            datelist = []
        
            for i in range(check_day,len(C)-offset):
                datelist.append(str(DATETIME[i]))

        except:
            pass

        for i in range(0,len(datelist)):
            d = datelist[i]
            Kl.date(end=d)
            try:
                valc1 = ((C-C[1]) / C[1]) * 100
                if(valc1 < 8) or V[1] == 0 or V == 0:
                        continue

                ma5  = MA(C,5)
                ma10 = MA(C,10)
                ma30 = MA(C,30)
                ma60 = MA(C,60)
                v40 =  MA(V,40)
                valv40 = V / v40 
                valo1 = ((O-O[1]) / O) * 100
                valh1 = ((H-H[1]) / H) * 100
                vall1 = ((L-C) / L) * 100
                valv1 = ((V-V[1]) / V[1]) * 100
                valc5 = C / ma5  
                valc10 = C / ma10  
                valc30 = C / ma30  
                valc60 = C / ma60 
                if pred_data == 0:
                    maxc10 = talib.MAX(allC[-check_day-i:-i-1],check_day-1)[-1]
                    target = ((maxc10- C.data[-1] ) / C.data[-1] )* 100
                else:
                    target = 0

                tran = TRANSVERSE() #60日波动，<15判定为横盘震荡

                if target > 10:
                    label = 1
                else:
                    label = 0
                #print(C.data[-1],allC[-11-i],maxc10)
                print(Kl.currentdf['name'],Kl.currentdf['code'],d,valc5,valc10,valc30,valc60,valc1,valh1,valo1,vall1,valv1,valv40,tran,label)
                all_list.append([Kl.currentdf['name'],Kl.currentdf['code'],d,valc5,valc10,valc30,valc60,valc1,valh1,valo1,vall1,valv1,valv40,tran,label])
            except :
                print("Klang ERROR",df['code'],df['name'])

                PrintException()

fields = ['name','code','日期','5日均线比','10日均线比','30日均线比','60日均线比','C涨幅','H涨幅','O涨幅','L涨幅','V涨幅','40日量比','60日震荡','是否涨幅10%']


main_loop(start=None,endday='2021-07-01')
df = pd.DataFrame(all_list,columns=fields)
df.to_csv('transverse_train'+today+'.csv',index=False)


all_list = []
main_loop(start='2021-07-15',endday=today)
df = pd.DataFrame(all_list,columns=fields)
df.to_csv('transverse_test'+today+'.csv',index=False)

all_list = []
pred_data = 1
main_loop(start='2021-07-15',endday=today)
df = pd.DataFrame(all_list,columns=fields)
df.to_csv('transverse_pred'+today+'.csv',index=False)


