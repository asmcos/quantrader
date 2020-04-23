import dbmongo
import numpy as np 


startlist=[]
finallist=[]

all = dbmongo.get_all_backtest('2019-10-08','2020-04-22')
for a in all:
	startlist.append(a['startvalue'])
	finallist.append(a['finalvalue'])

print(np.array(startlist).mean(),np.array(finallist).mean())
print(np.array(startlist).sum(),np.array(finallist).sum())
