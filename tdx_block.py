from tdxhy import get_code_list
from common.common import *
import os

parser.add_argument('--bkname', type=str, default="环境保护", help='板块名称')
parser.add_argument('--bkcode', type=str, default="880465", help='板块代码')

args = parser.parse_args() 
bkname = args.bkname
bkcode = args.bkcode
get_code_list(bkname,bkcode)

filename = './datas/stock_tdx_block'+endday+ bkcode+'.html'

from tdxhy import content
print("save to ", 'file://'+os.getcwd()+ '/' + filename)
save_file(filename,content)
