# 2_ 前缀修复说明 — hk_qq

> 原则：**不修改**原有 `hk_qq.py`，所有修复放在 `2_` 开头的文件中。

## 涉及文件

| 原文件 | 新文件 | 说明 |
|--------|--------|------|
| `hk_qq.py` | `2_hk_qq.py` | 修复分时/日K 数据解析问题 |
| `proxy_flask.py`（引用处） | 见下方「如何切换」 | 可选改用修复版接口 |

---

## 修复 1：`get_minute_data` 最高/最低价字段错误

**原文件**：`hk_qq.py` 第 196-197 行

**问题**：从腾讯 qt 数组取 high/low 时下标用错，导致 `high < low`：

```python
# 原代码（错误）
'high': float(info_list[9])   # [9] 是当前价，不是最高价
'low':  float(info_list[33])  # [33] 是当日最高价，不是最低价
```

**实测**（sz300199）：
- 原：high=25.85, low=26.31 → high < low，明显错误
- 新：high=26.31, low=25.42 → 正确

**qt 数组正确含义**（经接口实测）：
- `[3]` 当前价
- `[33]` 当日最高价
- `[34]` 当日最低价

**修复位置**：`2_hk_qq.py` → `get_minute_data()`

---

## 修复 2：分时首根 K 线 open 为 0

**原文件**：`hk_qq.py` 第 164-184 行

**问题**：第一根分时数据的 `open` 初始化为 0，首条记录 open=0 不合理。

**修复**：用昨收价 `info_list[4]`（或开盘价）作为首根 open 的初始值。

**修复位置**：`2_hk_qq.py` → `get_minute_data()`

---

## 修复 3：日K 首根涨跌幅计算

**原文件**：`hk_qq.py` 第 89-100 行

**问题**：第一根日K 的 `rise` 用 `(收盘-开盘)/开盘`，未使用接口返回的昨收价 `prec`，与行情软件显示的涨跌幅不一致。

**修复**：首根 K 线用 `prec`（昨收）计算涨跌幅，后续 K 线仍用前一根收盘价。

**修复位置**：`2_hk_qq.py` → `get_dayk()`

---

## 修复 4：HTTP 请求超时

**原文件**：`hk_qq.py` 中 `requests.get()` 无 timeout

**问题**：网络异常时可能长时间阻塞。

**修复**：`2_hk_qq.py` 中统一使用 `timeout=(5, 30)`。

---

## 未改动的函数（直接复用原模块）

以下函数经测试正常，在 `2_hk_qq.py` 中直接从 `hk_qq` 导入：

- `remake_code` / `remake_codelist` / `remake_result`
- `search` / `qqlist`

---

## 如何切换使用修复版

在 `proxy_flask.py` 中，将：

```python
import hk_qq as qq
```

改为：

```python
import 2_hk_qq as qq   # 语法不允许数字开头，实际写法见下
```

Python 模块名不能以数字开头，请用以下方式之一：

```python
# 方式 A：importlib
import importlib
qq = importlib.import_module("2_hk_qq")

# 方式 B：按函数导入
from importlib import import_module
qq = import_module("2_hk_qq")
```

然后 `/tick/<code>` 和 `/day/<code>` 路由无需其他改动。

---

## 验证

```bash
python 2_hk_qq.py
```

输出会对比原 `hk_qq` 与 `2_hk_qq` 的 high/low 及首根日K涨跌幅。
