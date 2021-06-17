from datetime import datetime as dt
import urllib.request
import json
import pandas as pd
import numpy as np


def get_ohlcv_week(p_meigaracode):
    return get_ohlcv(p_meigaracode, "1wk")


def get_ohlcv_day(p_meigaracode):
    return get_ohlcv(p_meigaracode, "1d")


def get_ohlcv(p_meigaracode, p_period):
    str_dtf = dt(dt.today().year - 3, dt.today().month, 1).strftime('%Y-%m-%d')
    str_dtt = dt(dt.today().year, dt.today().month, dt.today().day - 1).strftime('%Y-%m-%d')

    str_url = get_url(p_meigaracode, str_dtf, str_dtt, p_period)
    print(str_url)
    obj_req = urllib.request.urlopen(str_url)
    obj_res = obj_req.read()
    str_json = json.loads(obj_res)
    df_ohlcv = pd.DataFrame(np.array(str_json["chart"]["result"][0]["timestamp"]),
                            columns=["Timestamp"])
    df_ohlcv["Timestamp"] = pd.to_datetime(df_ohlcv['Timestamp'], unit='s')
    df_ohlcv["Open"] = np.array(str_json["chart"]["result"][0]["indicators"]["quote"][0]["open"]).astype(float)
    df_ohlcv["High"] = np.array(str_json["chart"]["result"][0]["indicators"]["quote"][0]["high"]).astype(float)
    df_ohlcv["Low"] = np.array(str_json["chart"]["result"][0]["indicators"]["quote"][0]["low"]).astype(float)
    df_ohlcv["Close"] = np.array(str_json["chart"]["result"][0]["indicators"]["quote"][0]["close"]).astype(float)
    df_ohlcv["Volume"] = np.array(str_json["chart"]["result"][0]["indicators"]["quote"][0]["volume"]).astype(float)

    # 欠損値の削除
    df_ohlcv = df_ohlcv.dropna()
    df_ohlcv.reset_index(drop=True, inplace=True)

    # DateTime列をIndexにする
    df_ohlcv = df_ohlcv.set_index('Timestamp')

    # 返却
    return df_ohlcv


def get_url(MeigaraCode, DateTimeFrom, DateTimeTo, Piriod):
    datetime_from = dt.strptime(DateTimeFrom, '%Y-%m-%d')
    datetime_to = dt.strptime(DateTimeTo, '%Y-%m-%d')

    return "https://query1.finance.yahoo.com/v8/finance/chart/" + MeigaraCode \
           + "?symbol=" + MeigaraCode \
           + "&period1=" + str("{:.0f}".format(datetime_from.timestamp())) \
           + "&period2=" + str("{:.0f}".format(datetime_to.timestamp())) \
           + "&interval=" + Piriod
