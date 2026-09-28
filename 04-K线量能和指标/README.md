# 04 — K 线、成交量和均线、MACD

把 01 的日 K 画成三层图：上面是蜡烛和均线，中间是成交量，下面是 MACD。均线和 MACD 用 [03](../03-均线和MACD/README.md) 里的同一套公式，先在全部日 K 上算完，再截取最近一段来画，这样图的左边缘不会因为样本太短而失真。

```bash
pip3 install pandas matplotlib
python3 plot_kline.py
python3 plot_kline.py sh600000
python3 plot_kline.py sz002129 80
```

图片写到本目录，文件名如 `sz002129_kline.png`。默认画最近 120 根；第二个参数可以改根数。

## 图上有什么

| 图层 | 内容 | 算法 |
|------|------|------|
| K 线 | 开高低收。红色阳线（收盘 ≥ 开盘），绿色阴线 | 日 K 的 open / high / low / close |
| 均线 | MA5、MA10、MA20，叠在 K 线上 | 03 的 SMA，不是 EMA |
| 成交量 | 与当天 K 线同色 | `volume` |
| MACD | DIF、DEA，柱为 (DIF − DEA) × 2 | 参数 12、26、9，与 03 相同 |

K 线上的 MA 用的是简单移动平均。EMA 反应更快，03 的 `ma.py` 里有对照；这张图跟行情软件主图上的 MA5/10/20 一致，所以用 SMA。

## 和前几课的关系

- 行情来自 `01` 的 `day_k_qq`（腾讯日 K，前复权）
- `sma`、`macd` 从 `03-均线和MACD` 引入，不在这里重写公式
