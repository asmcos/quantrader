from pytdx.hq import TdxHq_API
import struct
import sys

code =  '601012'
market = 1

if len(sys.argv) > 1:
    zone, code = sys.argv[1].split('.')
    if zone == 'sz':
        market = 0

api = TdxHq_API()

api.connect('119.147.212.81', 7709)

info = api.get_company_info_category(market,code)

for i in info:
    #for k in i.keys():
    #print(k,i[k])
    #name,filename,start,length
    info2 = api.get_company_info_content(market,code,i['filename'],i['start'],i['length'])
    print(info2)

def get_data(fname):
    content = fname.decode('utf-8')
    print(content)


def get_and_parse_block_info(client, blockfile):
    try:
        meta = client.get_block_info_meta(blockfile)
    except Exception as e:
        return None

    if not meta:
        return None

    print(meta)

    size = meta['size']
    one_chunk = 0x7530


    chuncks = size // one_chunk
    if size % one_chunk != 0:
        chuncks += 1

    file_content = bytearray()
    for seg in range(chuncks):
        start = seg * one_chunk
        piece_data = client.get_block_info(blockfile, start, size)
        file_content.extend(piece_data)

    #print(len(file_content))

    #print(file_content)
    get_data(file_content)

def block(filename):
    ret = api.get_and_parse_block_info(filename)
    for i in ret:
        #if i['blockname'] == '多晶硅':
        #print(i)
        pass
'''
block("block_fg.dat")
block("block_zs.dat")
block("block_gn.dat")
block("block.dat")
block("incon.dat")
block("tdxhy.cfg")
'''
