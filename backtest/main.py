import urllib.request
import json
import numpy as np
import pandas as pd
import talib as ta
from datetime import datetime as dt
from backtesting import Backtest, Strategy


class VolatilitySystem(Strategy):
    def init(self):
        h = self.data.df['High'].fillna(method='ffill')
        l = self.data.df['Low'].fillna(method='ffill')
        c = self.data.df['Close'].fillna(method='ffill')
        ary_SarT = []

        # ATR(Average True Range)
        self.data.df['Atr'] = ta.ATR(h, l, c, timeperiod=7)
        # SIC (期間中の最大と最小)
        self.data.df['SicH'] = c.rolling(20).max()
        self.data.df['SicL'] = c.rolling(20).min()

        # SAR (Stop and Reverse)
        self.data.df['Sar2S'] = self.data.df['SicH'] - 3 * self.data.df['Atr']
        self.data.df['Sar2L'] = self.data.df['SicL'] + 3 * self.data.df['Atr']
        self.data.df['SarLP'] = self.data.df['SicH'] - 1 * self.data.df['Atr']

        # 自分でループしないと計算できないヤツラ
        for idx in range(self.data.df.shape[0]):
            if idx == 0:
                ary_SarT.append(0)
            else:
                # SAR Trend
                if c[idx] > self.data.df['Sar2L'][idx]:
                    ary_SarT.append(1)
                elif c[idx] < self.data.df['Sar2S'][idx]:
                    ary_SarT.append(-1)
                else:
                    # 前日のトレンドを保持
                    ary_SarT.append(ary_SarT[idx - 1])

        # SAR Trend
        self.data.df['SarT'] = ary_SarT
        # CSV 保存
        filename = "data\\" + self.__class__.__name__ + "_" \
                   + str_mei + "_" \
                   + dt.today().strftime('%Y-%m-%d_%H%M%S') \
                   + ".csv"
        self.data.df.to_csv(filename, index=False)

    def next(self):
        if self.position.is_long:
            if self.data.df['SarT'][-1] < 0:
                self.position.close()
        else:
            if self.data.df['SarT'][-1] > 0 and self.data.df['SarT'][-2] < 0:
                self.buy()


class BreakOut(Strategy):
    def init(self):
        K_ATR = 0
        h = self.data.df['High'].fillna(method='ffill')
        l = self.data.df['Low'].fillna(method='ffill')
        c = self.data.df['Close'].fillna(method='ffill')

        # ATR(Average True Range)
        self.data.df['Atr'] = ta.ATR(h, l, c, timeperiod=20)
        # SIC (期間中の最大と最小)
        self.data.df['SicH'] = c.rolling(20).max() - K_ATR * self.data.df['Atr']
        self.data.df['SicL'] = c.rolling(20).min() + K_ATR * self.data.df['Atr']

        # CSV 保存
        filename = "data\\" + self.__class__.__name__ + "_" \
                   + str_mei + "_" \
                   + dt.today().strftime('%Y-%m-%d_%H%M%S') \
                   + ".csv"
        self.data.df.to_csv(filename, index=False)

    def next(self):
        if self.position.is_long:
            if self.data.df['Close'][-1] <= self.data.df['SicL'][-1]:
                self.position.close()
        else:
            if self.data.df['Close'][-1] >= self.data.df['SicH'][-1]:
                self.buy()


class MovingCycle(Strategy):
    def init(self):
        h = self.data.df['High'].fillna(method='ffill')
        l = self.data.df['Low'].fillna(method='ffill')
        c = self.data.df['Close'].fillna(method='ffill')
        # MovingCycleTrend
        ary_MocT = []
        # Simple Moving Average 5
        self.data.df['Sma5'] = ta.SMA(c, timeperiod=5)
        # Simple Moving Average 20
        self.data.df['Sma20'] = ta.SMA(c, timeperiod=20)
        # Simple Moving Average 60
        self.data.df['Sma60'] = ta.SMA(c, timeperiod=60)

        # 自分でループしないと計算できないヤツラ
        for idx in range(self.data.df.shape[0]):
            if idx == 0:
                ary_MocT.append('None')
            else:
                # 移動平均大循環分析
                if self.data.df['Sma5'][idx] >= self.data.df['Sma20'][idx] >= self.data.df['Sma60'][idx]:
                    ary_MocT.append('ST1')
                elif self.data.df['Sma20'][idx] >= self.data.df['Sma5'][idx] >= self.data.df['Sma60'][idx]:
                    ary_MocT.append('ST2')
                elif self.data.df['Sma20'][idx] >= self.data.df['Sma60'][idx] >= self.data.df['Sma5'][idx]:
                    ary_MocT.append('ST3')
                elif self.data.df['Sma60'][idx] >= self.data.df['Sma20'][idx] >= self.data.df['Sma5'][idx]:
                    ary_MocT.append('ST4')
                elif self.data.df['Sma60'][idx] >= self.data.df['Sma5'][idx] >= self.data.df['Sma20'][idx]:
                    ary_MocT.append('ST5')
                elif self.data.df['Sma5'][idx] >= self.data.df['Sma60'][idx] >= self.data.df['Sma20'][idx]:
                    ary_MocT.append('ST6')
                else:
                    ary_MocT.append('None')

        # MovingCycleTrend
        self.data.df['MocT'] = ary_MocT
        # CSV 保存
        filename = "data\\" + self.__class__.__name__ + "_" \
                   + str_mei + "_" \
                   + dt.today().strftime('%Y-%m-%d_%H%M%S') \
                   + ".csv"
        self.data.df.to_csv(filename)

    def next(self):
        if self.position.is_long:
            if self.data.df['MocT'][-1] != 'ST1':
                self.position.close()
        else:
            if self.data.df['MocT'][-1] == 'ST1':
                self.buy()


class StdDevVolaModel(Strategy):
    def init(self):
        price = self.data.Close
        # self.ma1 = self.I(SMA, price, 10)
        # self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if self.data.SdBlaT[-1] > 0 and self.data.SdBlaT[-2] <= 0:
            self.position.close()
            self.buy()
        elif self.data.SdBlaT[-1] <= 0 and self.data.SdBlaT[-2] > 0:
            self.position.close()
            # self.sell()


class TrendBalancePointSystem(Strategy):
    def init(self):
        h = self.data.df['High'].fillna(method='ffill')
        l = self.data.df['Low'].fillna(method='ffill')
        c = self.data.df['Close'].fillna(method='ffill')

        # 過去2日間のMFとは今日と前日のMF
        ary_mf = c - c.shift(2)

        # 買いに転換する場合 翌日のTBPは過去2日間のMFの小さいほうを前日の終値に足す
        # TBP 上昇トレンド転換値
        ary_TbppNext = pd.Series(c).shift(1) + np.min([ary_mf,
                                                       ary_mf.shift(1)],
                                                      axis=0)

        # 売りに転換する場合 翌日のTBPは過去2日間のMFの大きいほうを前日の終値に足す
        # TBP 下降トレンド転換値
        ary_TbpmNext = pd.Series(c).shift(1) + np.max([ary_mf,
                                                       ary_mf.shift(1)],
                                                      axis=0)

        ary_TbpT = []  # Trend Balance Point トレンド方向
        ary_TbpNext = []  # 翌日のTrend Balance Point
        ary_tr = np.max([
            pd.Series(h) - pd.Series(l),
            (pd.Series(c).shift(1) - pd.Series(h)).abs(),
            (pd.Series(c).shift(1) - pd.Series(l)).abs(),
        ], axis=0)
        ary_xb = np.average([h, l, c], axis=0)
        ary_StpB = ary_xb - ary_tr
        ary_StpS = ary_xb + ary_tr
        ary_PrfB = ary_xb * 2 - l
        ary_PrfS = ary_xb * 2 - h
        # 自分でループしないと計算できないヤツラ
        for idx in range(len(c)):
            if idx < 1:
                ary_TbpT.append(0)
                ary_TbpNext.append(0)
                continue

            # Trend Balance Point
            if c[idx] < ary_TbppNext[idx - 1]:
                ary_TbpNext.append(ary_TbpmNext[idx])
                ary_TbpT.append(-1)
            elif c[idx] > ary_TbpmNext[idx - 1]:
                ary_TbpNext.append(ary_TbppNext[idx])
                ary_TbpT.append(1)
            else:
                ary_TbpT.append(ary_TbpT[idx - 1])
                if ary_TbpT[idx - 1] > 0:
                    ary_TbpNext.append(ary_TbppNext[idx])
                else:
                    ary_TbpNext.append(ary_TbpmNext[idx])

        self.data.df["MF"] = ary_mf
        self.data.df["TR"] = ary_tr
        self.data.df["XB"] = ary_xb
        # df["TBPp"] = ary_TbppNext
        # df["TBPm"] = ary_TbpmNext
        self.data.df["Tbp"] = pd.Series(ary_TbpNext, index=c.index).shift(1)
        self.data.df["TbpT"] = pd.Series(ary_TbpT, index=c.index)
        self.data.df["StpB"] = pd.Series(ary_StpB, index=c.index).shift(1)
        self.data.df["StpS"] = pd.Series(ary_StpS, index=c.index).shift(1)
        self.data.df["PrfB"] = pd.Series(ary_PrfB).shift(1)
        self.data.df["PrfS"] = pd.Series(ary_PrfS).shift(1)

        # CSV 保存
        filename = "data\\" + self.__class__.__name__ + "_" \
                   + str_mei + "_" \
                   + dt.today().strftime('%Y-%m-%d_%H%M%S') \
                   + ".csv"
        self.data.df.to_csv(filename)

    def next(self):
        flg_hold = False
        if self.position.is_long:
            if self.data.StpB[-1] > self.data.Close[-1]:
                self.position.close()
            elif self.data.PrfB[-1] < self.data.Close[-1]:
                self.position.close()
            else:
                flg_hold = True

        if self.position.is_short:
            if self.data.StpS[-1] > self.data.Close[-1]:
                self.position.close()
            elif self.data.PrfS[-1] < self.data.Close[-1]:
                self.position.close()
            else:
                flg_hold = True

        if flg_hold == False:
            if self.data.TbpT[-1] > 0:
                self.buy()
            elif self.data.TbpT[-1] < 0:
                self.sell()


class Nichidai(Strategy):
    def init(self):
        h = self.data.df['High'].fillna(method='ffill')
        l = self.data.df['Low'].fillna(method='ffill')
        c = self.data.df['Close'].fillna(method='ffill')

        # Simple Moving Average 5
        self.data.df['Sma5'] = ta.SMA(c, timeperiod=5)
        # Simple Moving Average 20
        self.data.df['Sma20'] = ta.SMA(c, timeperiod=20)
        # Simple Moving Average 60
        self.data.df['Sma60'] = ta.SMA(c, timeperiod=60)

        # MovingCycleTrend
        ary_MocT = []
        # 自分でループしないと計算できないヤツラ
        for idx in range(self.data.df.shape[0]):
            if idx == 0:
                ary_MocT.append('None')
            else:
                # 移動平均大循環分析
                if self.data.df['Sma5'][idx] >= self.data.df['Sma20'][idx] >= self.data.df['Sma60'][idx]:
                    ary_MocT.append('ST1')
                elif self.data.df['Sma20'][idx] >= self.data.df['Sma5'][idx] >= self.data.df['Sma60'][idx]:
                    ary_MocT.append('ST2')
                elif self.data.df['Sma20'][idx] >= self.data.df['Sma60'][idx] >= self.data.df['Sma5'][idx]:
                    ary_MocT.append('ST3')
                elif self.data.df['Sma60'][idx] >= self.data.df['Sma20'][idx] >= self.data.df['Sma5'][idx]:
                    ary_MocT.append('ST4')
                elif self.data.df['Sma60'][idx] >= self.data.df['Sma5'][idx] >= self.data.df['Sma20'][idx]:
                    ary_MocT.append('ST5')
                elif self.data.df['Sma5'][idx] >= self.data.df['Sma60'][idx] >= self.data.df['Sma20'][idx]:
                    ary_MocT.append('ST6')
                else:
                    ary_MocT.append('None')

        # MovingCycleTrend
        self.data.df['MocT'] = ary_MocT
        # CSV 保存
        filename = "data\\" + self.__class__.__name__ + "_" \
                   + str_mei + "_" \
                   + dt.today().strftime('%Y-%m-%d_%H%M%S') \
                   + ".csv"
        self.data.df.to_csv(filename)

    def next(self):
        if self.position.is_long:
            # 5日線を2日連続で下回ったら手放す
            if self.data.df['Close'][-1] < self.data.df['Sma5'][-1]:
                self.position.close()
        else:
            # 5日線を半分の法則で上回ったら
            if (self.data.df['Open'][-1] + self.data.df['Close'][-1]) / 2 > self.data.df['Sma5'][-1]:
                self.buy()


def get_url(MeigaraCode, DateTimeFrom, DateTimeTo, Piriod):
    datetime_from = dt.strptime(DateTimeFrom, '%Y-%m-%d')
    datetime_to = dt.strptime(DateTimeTo, '%Y-%m-%d')

    return "https://query1.finance.yahoo.com/v8/finance/chart/" + MeigaraCode \
           + "?symbol=" + MeigaraCode \
           + "&period1=" + str("{:.0f}".format(datetime_from.timestamp())) \
           + "&period2=" + str("{:.0f}".format(datetime_to.timestamp())) \
           + "&interval=" + Piriod


print("Start")
# ---------------------------------------------
# str_mei = "1571.T" # 日経インバ
# str_mei = "1545.T" # NASDAQ ETF
# str_mei = "BTC-JPY"
str_mei = "%5EN225"  # 日経225
# ---------------------------------------------
str_dtf = dt(dt.today().year - 3, dt.today().month, 1).strftime('%Y-%m-%d')
str_dtt = dt(dt.today().year, dt.today().month, dt.today().day - 1).strftime('%Y-%m-%d')

str_url = get_url(str_mei, str_dtf, str_dtt, "1d")
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

# 欠損値の削除
ohlcv_df = ohlcv_df.dropna()
ohlcv_df.reset_index(drop=True, inplace=True)

# DateTime列をIndexにする
ohlcv_df = ohlcv_df.set_index('Timestamp')

# ---------------------------------------------
# sample_df = pd.DataFrame(
#     pd.to_datetime([
#         '1977/8/15'
#         , '1977/8/16'
#         , '1977/8/17'
#         , '1977/8/18'
#         , '1977/8/19'
#         , '1977/8/22'
#         , '1977/8/23'
#         , '1977/8/24'
#         , '1977/8/25'
#         , '1977/8/26'
#         , '1977/8/29'
#         , '1977/8/30'
#         , '1977/8/31'
#         , '1977/9/1'
#         , '1977/9/2'
#         , '1977/9/6'
#         , '1977/9/7'
#         , '1977/9/8'
#         , '1977/9/9'
#         , '1977/9/12'
#         , '1977/9/13'
#         , '1977/9/14'
#         , '1977/9/15'
#         , '1977/9/16'
#         , '1977/9/19'
#         , '1977/9/20'
#         , '1977/9/21'
#         , '1977/9/22'
#         , '1977/9/23'
#         , '1977/9/26'
#         , '1977/9/27'
#         , '1977/9/28'
#         , '1977/9/29'
#         , '1977/9/30'
#         , '1977/10/3'
#         , '1977/10/4'
#         , '1977/10/5'
#         , '1977/10/6'
#         , '1977/10/7'
#         , '1977/10/10'
#         , '1977/10/11'
#         , '1977/10/12'
#         , '1977/10/13'
#         , '1977/10/14']),
#     columns=["Timestamp"])
# # DateTime列をIndexにする
# sample_df = sample_df.set_index('Timestamp')
#
# sample_df["Open"] = [
#     206.2, 206.3, 208.4, 210, 208, 209, 202.5, 195.8, 196, 195, 200, 206, 209, 202.3, 201.3, 205, 205.2, 206.5, 205,
#     206, 201.5, 200.5, 200.8, 202, 198.7, 198.6, 199.2, 198.5, 196.5, 201, 201, 203.8, 203, 203.6, 205.2, 208.1, 208.5,
#     210.2, 209.6, 208.7, 207.5, 203, 199, 197
# ]
# sample_df["High"] = [
#     207.8, 208, 212.5, 212.5, 212, 213, 208.5, 204, 203, 202, 206.5, 209, 210.9, 209.3, 205.4, 207, 209.2, 211, 208,
#     208.2, 206.5, 204.2, 203.3, 204, 201, 201.6, 201.3, 200, 201.8, 203, 206, 206.3, 205.3, 206.3, 209.5, 210.8, 209.9,
#     213.9, 213.2, 211.5, 211, 208, 203, 202
# ]
# sample_df["Low"] = [
#     206.2, 206.3, 208.4, 210, 208, 209, 202.5, 195.8, 196, 195, 200, 206, 209, 202.3, 201.3, 205, 205.2, 206.5, 205,
#     206, 201.5, 200.5, 200.8, 202, 198.7, 198.6, 199.2, 198.5, 196.5, 201, 201, 203.8, 203, 203.6, 205.2, 208.1, 208.5,
#     210.2, 209.6, 208.7, 207.5, 203, 199, 197
# ]
# sample_df["Close"] = [
#     206.8, 206.5, 212, 210.5, 210.8, 209.5, 202.5, 203, 196.3, 199.5, 206, 208.8, 209.3, 202.3, 205.2, 205.5, 208.5,
#     206.7, 206.5, 206.8, 201.5, 203, 203.2, 202.7, 198.8, 200, 200.6, 198.9, 201.5, 201.5, 206, 204.3, 205.2, 203.8,
#     209, 208.1, 209.5, 213.4, 211.4, 208.9, 208.1, 203.5, 199.1, 201.6
# ]
#
# bt = Backtest(sample_df, TrendBalancePointSystem, cash=100000000,
#               exclusive_orders=True)

# bt = Backtest(ohlcv_df, TrendBalancePointSystem, cash=100000000,
#               exclusive_orders=True)

# ストラテジの選択
# bt = Backtest(ohlcv_df, VolatilitySystem, cash=100000000,
#               exclusive_orders=True)

# bt = Backtest(ohlcv_df, BreakOut, cash=100000000,
#               exclusive_orders=True)

# bt = Backtest(ohlcv_df, MovingCycle, cash=100000000,
#               exclusive_orders=True)

# bt = Backtest(ohlcv_df, StdDevVolaModel, cash=100000000,
#               exclusive_orders=False)

bt = Backtest(ohlcv_df, Nichidai, cash=100000000,
              exclusive_orders=True)

# BackTest実行
stats = bt.run()
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
print(stats.array[29][['EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice', 'ReturnPct']])
print('- - - - - - - - - - - - - - - - - - - - - - -')
print(stats)
# bt.plot()
