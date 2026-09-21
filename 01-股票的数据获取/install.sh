#!/usr/bin/env bash
# 安装本课依赖
set -e
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
echo "依赖安装完成。可运行: python3 stock_list.py"
