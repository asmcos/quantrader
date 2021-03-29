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

#-X=2.3 -A=5.1 -B=2.89 -C=4.6 -D=1.5
def bullish_butterfly(x1,a1,b1,c1,d1):
    print("0.786 b=")
    downN(a1,x1,0.786) #b
    print("0.681 b = ")
    downN(a1,x1,0.618) #b

    print("0.786 c =")
    upN(a1,b1,0.786) #c
    print("0.618 c=") 
    upN(a1,b1,0.618) #c

    print("d=")
    downN(c1,b1,1.618) # d
    
    downN(a1,x1,1.618) # d
    downN(a1,x1,1.27) # d
    
bullish_butterfly(X,A,B,C,D)
     
