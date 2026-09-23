# 02 — 用 pandas 装股票数据

本课接在 [01-股票的数据获取](../01-股票的数据获取/README.md) 后面：接口拿到的是 dict，这里转成 pandas 的 DataFrame，再做均线、收益、合并和筛选。

依赖：`pandas`（日 K 存 parquet 时还需要 `pyarrow`，没有就只存 CSV）

```bash
pip3 install pandas pyarrow
```

先装好 01 的依赖（`requests`），本目录脚本会直接调用 01 的 `day_k_qq` / `minute_qq` / `stock_list`。

## 文件

| 文件 | 内容 | 运行 |
|------|------|------|
| `dayk_to_df.py` | 日K → DataFrame，日期索引，存 `data/*.csv` | `python3 dayk_to_df.py sz002129` |
| `minute_to_df.py` | 分时 → DataFrame，带交易日的时间索引 | `python3 minute_to_df.py hk00700` |
| `stock_list_to_df.py` | 股票列表 → DataFrame，可按名称筛选 | `python3 stock_list_to_df.py` |
| `analyze_examples.py` | 均线、收益回撤、多股合并、按星期分组、分时重采样、名称筛选 | `python3 analyze_examples.py` |

## 跑完能看到什么

- **日K**：`open/close/high/low/volume/rise` 变成数值，索引用交易日。CSV 写到本目录 `data/`。
- **分时**：`time` 是当天的 `2026-09-23 09:30` 这种时间，不是 1900 年。`amount` 用接口里的累计成交额，`volume` 是这一分钟的成交量。
- **列表**：默认只拉第一页（约 20 只，按代码从大到小，多半是沪市科创）。全市场筛选：

```bash
python3 stock_list_to_df.py --all --filter 银行
```

- **分析例子**里六段依次是：rolling 均线、收益率/波动/最大回撤、三只股票对齐后的相关性和各自区间涨幅、按星期几统计涨跌、分时合成 30 分钟、列表里筛名称含「科技」的股票。

## 数据来源

- `day_k_qq.get_dayk(code)` → `data.dayks`
- `minute_qq.get_minute(code)` → `trends`，另有 `date`、`high`、`low`
- `stock_list.get_stock_list()` → `(列表, 总数)`

股票代码写法与 01 相同：`sh600000`、`sz000001`、`hk00700`。
