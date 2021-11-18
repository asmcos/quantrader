from Klang.lang import kparser,setPY,Kexec
from Klang import (Kl,
    C,O,V,H,L, CLOSE,HIGH,DATETIME,
    MA,CROSS,BARSLAST,HHV,LLV,COUNT,BARSLASTFIND,
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
        check_day = 5

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
            allV = V.data
            allDate = DATETIME.data

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
                ma60 = MA(C,60)
                if(valc1 < 8) or V[1] == 0 or V == 0 or C < ma60:
                        continue

                ma5  = MA(C,5)
                ma10 = MA(C,10)
                ma30 = MA(C,30)
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

                #
                cnext4 = allC[-7-i]
                cnext2 = allC[-9-i]
                valnc2 = (C.data[-1] - cnext2 ) / C.data[-1] * 100
                valnc4 = (C.data[-1] - cnext4 ) / C.data[-1] * 100
                valnc2 = round(valnc2,2)
                valnc4 = round(valnc4,2)

                vnext4 = allV[-7-i]
                vnext2 = allV[-9-i]
                valnv2 = vnext2/V.data[-1]
                valnv4 = vnext4/V.data[-1]
                valnv2 = round(valnv2,2)
                valnv4 = round(valnv4,2)



                r5 = (C[1] - LLV(C,5))/LLV(C,5) * 100
                diff,dea,macd = MACD(C) 
                HDAY = BARSLASTFIND(C,HHV(C,45))
                if pred_data == 0:
                    maxc10 = talib.MAX(allC[-7-i:-i-1],7-1)[-1]
                    target = ((maxc10- allC[-7-i] ) / allC[-i-7] )* 100
                    #target = (allC[-i-1] - allC[-7-i]) / allC[-i-7] * 100
                else:
                    target = 0

                tran = TRANSVERSE() #60日波动，<15判定为横盘震荡

                if target > 10:
                    label = 1
                else:
                    label = 0
                #print(C.data[-1],allC[-11-i],maxc10)
                print(Kl.currentdf['name'],Kl.currentdf['code'],d,valc5,valc10,valc30,valc60,valc1,valh1,valo1,vall1,valv1,valv40,tran,macd,r5,HDAY,valnc2,valnc4,valnv2,valnv4,label)
                all_list.append([Kl.currentdf['name'],Kl.currentdf['code'],d,valc5,valc10,valc30,valc60,valc1,valh1,valo1,vall1,valv1,valv40,tran,macd,r5,HDAY,valnc2,valnc4,valnv2,valnv4,label])
            except :
                print("Klang ERROR",df['code'],df['name'])

                PrintException()

fields = ['name','code','日期','5日均线比','10日均线比','30日均线比','60日均线比','C涨幅','H涨幅','O涨幅','L涨幅','V涨幅','40日量比','60日震荡','macd','5日涨幅','45日新高','2next','4next','2nextv','4nextv','是否涨幅10%']


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

