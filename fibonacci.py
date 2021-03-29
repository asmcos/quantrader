#
# 基于斐波那契理论定义的公式
#
#

datalist=[0.382, 0.50,0.618,0.786, 1.00,1.27,1.618 ,2.0, 2.24, 2.618, 3.14]

#0.382 , 2.24
#0.618 , 1.618
#0.786 , 1.27

# 下跌到0.618 左右回调

def downN(high,low,n):
    stopline = high-(high-low) * n
    print(stopline)
    return stopline

def upN(high,low,n): 
    stopline = low + (high-low) * n 
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

