import urllib.request
import json
import numpy as np
import pandas as pd
import talib as ta
from datetime import datetime as dt
from datetime import timedelta
from backtesting import Backtest, Strategy

from backtest import YahooF

print("Start")
str_meigara = "%5EN225"  # 日経平均

df_ohlcv_w = YahooF.get_ohlcv_week(str_meigara)  # 週足
df_ohlcv_d = YahooF.get_ohlcv_day(str_meigara)  # 日足

# 週足データ計算
# 移動平均
df_ohlcv_w['Sma13'] = ta.SMA(df_ohlcv_w["Close"], timeperiod=13)
df_ohlcv_w['Sma26'] = ta.SMA(df_ohlcv_w["Close"], timeperiod=26)

# ボリンジャーバンド
ary_uband1, ary_mband1, ary_lband1 = ta.BBANDS(df_ohlcv_w["Close"], timeperiod=26, nbdevup=1, nbdevdn=1, matype=0)
ary_uband2, ary_mband2, ary_lband2 = ta.BBANDS(df_ohlcv_w["Close"], timeperiod=26, nbdevup=2, nbdevdn=2, matype=0)
df_ohlcv_w['BbU1'] = ary_uband1
df_ohlcv_w['BbU2'] = ary_uband2

ary_flg_bb = []
ary_flg_sma = []
flg_bb = 0
for idx in range(df_ohlcv_w.shape[0]):
    if idx == 0:
        ary_flg_bb.append(0)
        ary_flg_sma.append(0)
        continue

    if df_ohlcv_w['Close'][idx] > df_ohlcv_w['BbU2'][idx]:
        flg_bb = 1

    if df_ohlcv_w['Close'][idx] < df_ohlcv_w['BbU1'][idx]:
        flg_bb = 0

    ary_flg_bb.append(flg_bb)

    if df_ohlcv_w['Sma13'][idx] > df_ohlcv_w['Sma13'][idx - 1] and \
            df_ohlcv_w['Sma26'][idx] > df_ohlcv_w['Sma26'][idx - 1]:
        ary_flg_sma.append(1)
    else:
        ary_flg_sma.append(0)

df_ohlcv_w['FlgBB'] = ary_flg_bb
df_ohlcv_w['FlgSMA'] = ary_flg_sma

# 日足データ計算
# 週足データを足しこむ
idxd = 0
idxw = 0
df_ohlcv_d['wk_Date'] = ""
df_ohlcv_d['wk_Open'] = ""
df_ohlcv_d['wk_Close'] = ""
df_ohlcv_d['wk_FlgBB'] = ""
df_ohlcv_d['wk_FlgSMA'] = ""
for idxd in range(df_ohlcv_d.shape[0]):
    print("Day:" + df_ohlcv_d.index[idxd].strftime('%Y/%m/%d %H:%M:%S'))

    for idxw in range(idxw, df_ohlcv_w.shape[0]):
        print("Week:" + df_ohlcv_w.index[idxw].strftime('%Y/%m/%d %H:%M:%S'))
        if df_ohlcv_w.index[idxw] >= df_ohlcv_d.index[idxd] - timedelta(days=7):
            break

        if (df_ohlcv_w.index[idxw] >= df_ohlcv_d.index[idxd] - timedelta(days=14)) and \
                (df_ohlcv_w.index[idxw] < df_ohlcv_d.index[idxd] - timedelta(days=7)):
            print("Week:" + df_ohlcv_w.index[idxw].strftime('%Y/%m/%d/%H:%M:%S'))
            df_ohlcv_d["wk_Date"][idxd] = df_ohlcv_w.index[idxw].strftime('%Y/%m/%d %H:%M:%S')
            df_ohlcv_d["wk_Open"][idxd] = df_ohlcv_w["Open"][idxw]
            df_ohlcv_d["wk_Close"][idxd] = df_ohlcv_w["Close"][idxw]
            df_ohlcv_d["wk_FlgBB"][idxd] = df_ohlcv_w["FlgBB"][idxw]
            df_ohlcv_d["wk_FlgSMA"][idxd] = df_ohlcv_w["FlgSMA"][idxw]
            break

# CSV 保存
filename = "data\\" + "Upstairs_" \
           + str_meigara + "_" \
           + dt.today().strftime('%Y-%m-%d_%H%M%S') \
           + ".csv"
df_ohlcv_d.to_csv(filename, index=True)
