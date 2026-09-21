# 01 — 股票的数据获取

本课目标：先把**数据跑通**，再去做策略。同一能力可以有多种途径，按需选一种即可。

## 安装依赖

```bash
# 默认（东财 / 腾讯 HTTP）
bash install.sh
# 或: pip3 install -r requirements.txt

# 可选：通达信 eltdx / pytdx
pip3 install -r requirements-extra.txt
```

## 能力 × 途径

### 股票列表（代码 + 名称）

| 文件 | 途径 | 运行 |
|------|------|------|
| `stock_list.py` | 东方财富 HTTP（默认） | `python3 stock_list.py` |
| `stock_list_eltdx.py` | 通达信 eltdx | `python3 stock_list_eltdx.py` |

### 板块

| 文件 | 途径 | 运行 |
|------|------|------|
| `boards.py` | 东方财富 HTTP | `python3 boards.py` |

### 日 K

| 文件 | 途径 | 运行 |
|------|------|------|
| `day_k_qq.py` | 腾讯 HTTP（推荐入门） | `python3 day_k_qq.py` |
| `day_k_eltdx.py` | 通达信 eltdx（前复权） | `python3 day_k_eltdx.py sz000001` |
| `day_k_pytdx.py` | 通达信 pytdx（老库，主站常失效） | `python3 day_k_pytdx.py sz000001` |

### 分时

| 文件 | 途径 | 运行 |
|------|------|------|
| `minute_qq.py` | 腾讯 HTTP（推荐入门） | `python3 minute_qq.py` |
| `minute_eltdx.py` | 通达信 eltdx | `python3 minute_eltdx.py sz000001` |

新手建议先跑 `stock_list.py` / `day_k_qq.py` / `minute_qq.py`；通达信站不稳定时改用腾讯/东财脚本即可。

## 代码格式约定

- 股票代码：`sh600000`、`sz000001`、`hk00700`
- 也支持带点写法：`sz.002129`（日K/分时脚本会自动规范化）
