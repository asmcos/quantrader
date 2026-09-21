# 01 — 股票的数据获取

本课目标：先把**数据跑通**，再去做策略。

| 文件 | 作用 | 运行 |
|------|------|------|
| `stock_list.py` | A 股列表（代码 + 名称） | `python3 stock_list.py` |
| `boards.py` | 行业板块涨跌榜（东方财富） | `python3 boards.py` |
| `day_k.py` | 日K 线（腾讯，前复权） | `python3 day_k.py` |
| `minute.py` | 当日分时（腾讯，已修 high/low） | `python3 minute.py` |

## 安装依赖

本课只需 `requests`：

```bash
# 方式一：脚本
bash install.sh

# 方式二：手动
pip3 install -r requirements.txt
```

## 代码格式约定

- 股票代码：`sh600000`、`sz000001`、`hk00700`
- 也支持带点写法：`sz.002129`（日K/分时脚本会自动规范化）
