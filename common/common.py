import requests
import re
import os
import pandas as pd

import argparse
import time
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--offset", help="开始执行的位置",default='0')
parser.add_argument("--endday", help="日期",default='0')
args = parser.parse_args()

offset = args.offset
endday = args.endday

today = datetime.now()
if endday== '0':
    endday = str(today.year) + str(today.month) + str(today.day)

def save_file(filename,content):
    f = open(filename,"w+")
    f.write(content)
    f.close()
