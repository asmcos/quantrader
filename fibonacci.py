#
# 基于斐波那契理论定义的公式
#
#

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-X", help="X",default=0.0)
parser.add_argument("-A", help="A",default=0)
parser.add_argument("-B", help="B",default=0)
parser.add_argument("-C", help="C",default=0)
parser.add_argument("-D", help="D",default=0)
args = parser.parse_args()

X= float(args.X)
A= float(args.A)
B= float(args.B)
C= float(args.C)
D= float(args.D)

def approx(i,j):
    if i > j:
        dt = i - j
        if (dt / i < 0.05):
            return True  
    else :
        dt = j - i
        if (dt / i < 0.05):
            return True
    return False

datalist=[0.382, 0.50,0.618,0.786, 1.00,1.27,1.618 ,2.0, 2.24, 2.618, 3.14]

#0.382 , 2.24
#0.618 , 1.618
#0.786 , 1.27

# 下跌到0.618 左右回调

def downN(high,low,n):
    stopline = high-(high-low) * n
    stopline = float("%.3f"%stopline)
    print(stopline)
    return stopline

def upN(high,low,n): 
    stopline = low + (high-low) * n 
    stopline = float("%.3f"%stopline)
    print(stopline)
    return stopline

def down618(high,low):
    return downN(high,low,0.618)

# 上升到0.618后终止
def up618(high,low):
    return upN(high,low,0.618) 

###########################
# down618(99.5625,10.8125)
# 结果是 44.715
#########################




# 下跌到0.786 左右回调
def down786(high,low):
    return downN(high,low,0.786)

# 上升到0.786后终止
def up786(high,low):
    return upN(high,low,0.786) 
 
# 隆基股份 76
# down786(122.12,64)
# 2021.3.29


# 下跌到1.27 左右回调
def down1270(high,low):
    return downN(high,low,1.27)

# 上升到1.27后终止
def up1270(high,low):
    return upN(high,low,1.27) 


# 下跌到1.618 左右回调
def down1618(high,low):
    return downN(high,low,1.618)

# 上升到1.618后终止
def up1618(high,low):
    return upN(high,low,1.618) 



def detectDownN(high,low):
    for i in datalist:
        print(i)
        downN(high,low,i)

def detectUpN(high,low):
    for i in datalist:
        print(i)
        upN(high,low,i)


butterflylist = []

def addbutterfly(butter):
    for i in butterflylist:
        if i == butter:
            return
    butterflylist.append(butter)

def dumpDown(high,low,opt):
    ratio =  (high-opt)/(high-low)
    ratio = float("%.3f"%ratio)
    print (ratio)
    return ratio 

def dumpUp(high,low,opt):
    ratio =  (opt-low)/(high-low)
    ratio = float("%.3f"%ratio)
    print (ratio)
    return ratio 

def dumpratio(x1,a1,b1,c1,d1):
    print(x1,a1,b1,c1,d1)
    print("xa->b")
    dumpDown(a1,x1,b1)
    print("ab->c")
    dumpUp(a1,b1,c1)
    print("bc->d")
    dumpDown(c1,b1,d1)
    print("xa->d")
    dumpDown(a1,x1,d1)
    
def Displaybutterfly():
    for i in butterflylist:
        print("=====================================================")
        print("=====================================================")
        print("===========A=========================================")
        print("==========/==\=========C=============================")
        print("=========|=====\====/====|===========================")
        print("========|========B========\==========================")
        print("=======|====================\========================")
        print(i[0],i[1],i[2],i[3],i[4],i[5])
        print("======|======================\=======================")
        print("======/=======================\======================")
        print("=====|=========================\=====================")
        print("====X===========================\====================")
        print("==================================\==================")
        print("=====================================\===============")
        print("=========================================D===========")
        x1,a1,b1,c1,d1 = i[6]
        dumpratio(x1,a1,b1,c1,d1)

#-X=2.3 -A=5.1 -B=2.89 -C=4.6 -D=1.5
def bullish_butterfly(x1,a1,b1,c1,d1):
    okb = False
    okc = False
    okd = False
    # stop stock
    if x1 == a1 or a1 == b1:
        return
    if b1 < d1*1.05 or b1 > c1 * 0.9:
        return 
    print(x1,a1,b1,c1,d1)
    b2 = downN(a1,x1,0.786) #b
    b3 = downN(a1,x1,0.618) #b

    if(approx(b1,b2)):
        okb = True
        print(b1,"~~",b2,"0.786")    
    if(approx(b1,b3)):
        okb = True
        print(b1,"~~",b3,"0.618")    

    c2= upN(a1,b1,0.786) #c
    c3= upN(a1,b1,0.618) #c

    if(approx(c1,c2)):
        okc = True
        print(c1,"~~",c2,"0.786")    
    if(approx(c1,c3)):
        okc = True
        print(c1,"~~",c3,"0.618")    




    d2 = downN(c1,b1,1.618) # d
    
    d3 = downN(a1,x1,1.618) # d
    d4 = downN(a1,x1,1.27) # d

    if(approx(d1,d3)):
        okd = True
        print(d1,"~~",d3,"1.618")    
    if(approx(d1,d4)):
        okd = True
        print(d1,"~~",d4,"1.27")    

    if (okb and okc and okd):
        print("=====================================================")
        print("=====================================================")
        print("===========A=========================================")
        print("==========/==\=========C=============================")
        print("=========|=====\====/====|===========================")
        print("========|========B========\==========================")
        print("=======|====================\========================")
        print(XD[6],XD[0],AD[0],BD[0],CD[0],DD[0])
        print("======|======================\=======================")
        print("======/=======================\======================")
        print("=====|=========================\=====================")
        print("====X===========================\====================")
        print("==================================\==================")
        print("=====================================\===============")
        print("=========================================D===========")
        point5 = [x1,a1,b1,c1,d1]
        addbutterfly([XD[6],XD[0],AD[0],BD[0],CD[0],DD[0],point5])
        dumpratio(x1,a1,b1,c1,d1)
         
#bullish_butterfly(X,A,B,C,D)

NULL   = 0
STATEX = 1
STATEA = 2
STATEB = 3
STATEC = 4
STATED = 5
XD,AD,BD,CD,DD = "","","","",""
def switchlow(status,i):
    global X,A,B,C,D,XD,AD,BD,CD,DD
    if status == NULL:
        X = i[2]
        XD = i[1]
        return STATEX,True
    if status == STATEA:
        B = i[2]
        BD = i[1]
        return STATEB,True
    if status == STATEC:
        D = i[2]
        DD = i[1]
        return STATED,True
    if status == STATED:
        X = i[2]
        XD = i[1]
        return STATEX,True
    return status,False

def switchhigh(status,i):
    global X,A,B,C,D,XD,AD,BD,CD,DD
    if status == STATEX:
        A = i[2]
        AD = i[1]
        return STATEA,True
    if status == STATEB:
        C = i[2]
        CD = i[1]
        return STATEC,True
    return status,False


def _search_pattern(name,code,mnlist):
    status = NULL
    for i in mnlist:
        if i[0] == 0: # low
            status,ok = switchlow(status,i)
            if ok and (status == STATED):
                bullish_butterfly(X,A,B,C,D)
        if i[0] == 1: # high 
            status,ok = switchhigh(status,i)

def search_pattern(name,code,mnlist):
    for i in range(len(mnlist)):
        if mnlist[i][0] == 0:
            _search_pattern(name,code,mnlist[i+1:])

    # if mnlist 0 is X, and is Only one 
    _search_pattern(name,code,mnlist)
