import urllib.request
import json
import numpy as np
import pandas as pd
from datetime import datetime as dt
from backtesting import Backtest, Strategy

from OhclvTA import OhclvTechnicalAnalyzeCalculator


class VolatilitySystem(Strategy):
    def init(self):
        price = self.data.Close
        # self.ma1 = self.I(SMA, price, 10)
        # self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if self.data.SarT[-1] > 0 and \
                self.data.SarT[-2] <= 0:
            self.position.close()
            self.buy()
        elif self.data.SarT[-1] < 0 and \
                self.data.SarT[-2] >= 0:
            self.position.close()
            self.sell()


class StdDevVolaModel(Strategy):
    def init(self):
        price = self.data.Close
        # self.ma1 = self.I(SMA, price, 10)
        # self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if self.data.SdBlaT[-1] > 0 and \
                self.data.SdBlaT[-2] <= 0:
            self.position.close()
            self.buy()
        elif self.data.SdBlaT[-1] < 0 and \
                self.data.SdBlaT[-2] >= 0:
            self.position.close()
            self.sell()


def get_url(MeigaraCode, DateTimeFrom, DateTimeTo, Piriod):
    datetime_from = dt.strptime(DateTimeFrom, '%Y-%m-%d')
    datetime_to = dt.strptime(DateTimeTo, '%Y-%m-%d')

    return "https://query1.finance.yahoo.com/v8/finance/chart/" + MeigaraCode \
           + "?symbol=" + MeigaraCode \
           + "&period1=" + str("{:.0f}".format(datetime_from.timestamp())) \
           + "&period2=" + str("{:.0f}".format(datetime_to.timestamp())) \
           + "&interval=" + Piriod


print("Start")
str_mei = "BTC-JPY"
# str_mei = "%5EN225" #日経225
str_dtf = "2020-02-01"
str_dtt = "2020-02-28"
str_url = get_url(str_mei, str_dtf, str_dtt, "1h")
str_csv = str_mei + "_" + str_dtf + "_" + str_dtt + ".csv"
readObj = urllib.request.urlopen(str_url)
response = readObj.read()
ohlcv_json = json.loads(response)
ohlcv_df = pd.DataFrame(np.array(ohlcv_json["chart"]["result"][0]["timestamp"]),
                        columns=["Timestamp"])
ohlcv_df["Timestamp"] = pd.to_datetime(ohlcv_df['Timestamp'], unit='s')
ohlcv_df["Open"] = np.array(ohlcv_json["chart"]["result"][0]["indicators"]["quote"][0]["open"]).astype(float)
ohlcv_df["High"] = np.array(ohlcv_json["chart"]["result"][0]["indicators"]["quote"][0]["high"]).astype(float)
ohlcv_df["Low"] = np.array(ohlcv_json["chart"]["result"][0]["indicators"]["quote"][0]["low"]).astype(float)
ohlcv_df["Close"] = np.array(ohlcv_json["chart"]["result"][0]["indicators"]["quote"][0]["close"]).astype(float)
ohlcv_df["Volume"] = np.array(ohlcv_json["chart"]["result"][0]["indicators"]["quote"][0]["volume"]).astype(float)

# 本家のほうがDataFrame渡しになったら変える
ohlcv_df = OhclvTechnicalAnalyzeCalculator.calc(ohlcv_df.values.tolist())

# DateTime列をIndexにする
ohlcv_df = ohlcv_df.set_index('Timestamp')

bt = Backtest(ohlcv_df, VolatilitySystem, cash=100000000,
              exclusive_orders=True)
stats = bt.run()
print(stats)
bt.plot()

bt = Backtest(ohlcv_df, StdDevVolaModel, cash=100000000,
              exclusive_orders=True)
stats = bt.run()
print(stats)
bt.plot()