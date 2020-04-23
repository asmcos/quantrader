#!/bin/bash

if [ "x$1" = "x" ]
then
	code=600500
else
	code=$1 
fi

rm ./datas/ts_$code.csv
python3 ts_to_csv.py --code $code
python3 btrmacd.py --datafile ./datas/ts_$code.csv
#python3 btrstoch.py --datafile ./datas/ts_$code.csv
#python3 btrrsi.py --datafile ./datas/ts_$code.csv
python3 btrboll.py --datafile ./datas/ts_$code.csv

