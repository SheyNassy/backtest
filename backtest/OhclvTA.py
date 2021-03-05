import numpy as np
import pandas as pd
import talib as ta


class OhclvTechnicalAnalyzeCalculator():
    def calc(marketItem):
        # 生配列をnp DataFrameに変換
        df_ohclv = pd.DataFrame(marketItem,
                                columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        # 欠損値の削除
        df_ohclv = df_ohclv.dropna()

        # PlotlyとTA-libでテクニカル分析チャートを描く
        # https://akatak.hatenadiary.jp/entry/2019/11/23/220836

        h = np.array(df_ohclv['High'].fillna(method='ffill'))
        l = np.array(df_ohclv['Low'].fillna(method='ffill'))
        c = np.array(df_ohclv['Close'].fillna(method='ffill'))
        v = np.array(df_ohclv['Volume'].fillna(method='ffill'))

        # Simple Moving Average 5
        df_ohclv['Sma5'] = ta.SMA(c, timeperiod=5)
        # Simple Moving Average 10
        df_ohclv['Sma10'] = ta.SMA(c, timeperiod=10)
        # Simple Moving Average 20
        df_ohclv['Sma20'] = ta.SMA(c, timeperiod=20)
        # Simple Moving Average 60
        df_ohclv['Sma60'] = ta.SMA(c, timeperiod=60)

        # Exponential Moving Average 5
        df_ohclv['Ema5'] = ta.EMA(c, timeperiod=5)
        # Exponential Moving Average 20
        df_ohclv['Ema20'] = ta.EMA(c, timeperiod=20)
        # Exponential Moving Average 40
        df_ohclv['Ema40'] = ta.EMA(c, timeperiod=40)

        # 標準偏差
        df_ohclv['StdDev'] = ta.STDDEV(c, timeperiod=26)

        # ADX(Average Directional Movement Index 平均方向性指数)
        df_ohclv['Adx'] = ta.ADX(h, l, c, timeperiod=14)

        # Bollinger Bands
        ary_uband, ary_mband, ary_lband = ta.BBANDS(c, timeperiod=21, nbdevup=0.75, nbdevdn=0.75, matype=0)
        df_ohclv['BbH'] = ary_uband
        df_ohclv['BbM'] = ary_mband
        df_ohclv['BbL'] = ary_lband

        # ATR(Average True Range)
        df_ohclv['ATR'] = ta.ATR(h, l, c, timeperiod=14)

        # SIC (期間中の最大と最小)
        df_ohclv["SicH"] = pd.Series(c).rolling(window=20).max()
        df_ohclv["SicL"] = pd.Series(c).rolling(window=20).min()

        # SAR (Stop and Reverse)
        df_ohclv["SarH"] = df_ohclv["SicH"] - df_ohclv['ATR'] * 3.3
        df_ohclv["SarL"] = df_ohclv["SicL"] + df_ohclv['ATR'] * 3.3

        # SAR Trend
        ary_SarH = np.array(df_ohclv["SarH"])
        ary_SarL = np.array(df_ohclv["SarL"])
        ary_SarT = []
        ary_SarTp = []
        ary_SarTm = []
        ary_Sar = []

        # 標準偏差ボラティリティトレード
        ary_StdDev = np.array(df_ohclv["StdDev"])
        ary_Adx = np.array(df_ohclv['Adx'])
        ary_SdBlaT = []
        ary_SdBlaTp = []
        ary_SdBlaTm = []

        # MFI
        df_ohclv['MOM'] = ta.MOM(c)

        # 自分でループしないと計算できないヤツラ
        for idx in range(df_ohclv.shape[0]):
            if idx == 0:
                ary_SarT.append(0)
                ary_SarTp.append(0)
                ary_SarTm.append(0)
                ary_Sar.append(0)

                ary_SdBlaT.append(0)
                ary_SdBlaTp.append(0)
                ary_SdBlaTm.append(0)
                continue

            # SAR (Stop and Reverse)
            # SarLをCloseが上抜け(Golden Cross)
            if ary_SarL[idx - 1] > c[idx - 1] and \
                    ary_SarL[idx] <= c[idx]:
                ary_SarT.append(1)
                ary_SarTp.append(1)
                ary_SarTm.append(0)
                ary_Sar.append(ary_SarH[idx])
            # SarHをCloseが下抜け(Golden Cross)
            elif ary_SarH[idx - 1] < c[idx - 1] and \
                    ary_SarH[idx] >= c[idx]:
                ary_SarT.append(-1)
                ary_SarTp.append(0)
                ary_SarTm.append(1)
                ary_Sar.append(ary_SarL[idx])
            else:
                # 前日のトレンドを保持
                ary_SarT.append(ary_SarT[idx - 1])
                ary_SarTp.append(ary_SarTp[idx - 1])
                ary_SarTm.append(ary_SarTm[idx - 1])

                if ary_SarT[idx] == 1:
                    ary_Sar.append(ary_SarH[idx])
                elif ary_SarT[idx] == -1:
                    ary_Sar.append(ary_SarL[idx])
                else:
                    ary_Sar.append(0)

            # 標準偏差ボラティリティトレードモデル
            if ary_StdDev[idx] > ary_StdDev[idx - 1] and \
                    ary_Adx[idx] > ary_Adx[idx - 1] and \
                    c[idx] >= ary_uband[idx]:
                ary_SdBlaT.append(1)
                ary_SdBlaTp.append(1)
                ary_SdBlaTm.append(0)
            elif ary_StdDev[idx] > ary_StdDev[idx - 1] and \
                    ary_Adx[idx] > ary_Adx[idx - 1] and \
                    c[idx] <= ary_lband[idx]:
                ary_SdBlaT.append(-1)
                ary_SdBlaTp.append(0)
                ary_SdBlaTm.append(1)
            elif ary_SdBlaT[idx - 1] == 1 and \
                    c[idx] >= ary_uband[idx]:
                ary_SdBlaT.append(1)
                ary_SdBlaTp.append(1)
                ary_SdBlaTm.append(0)
            elif ary_SdBlaT[idx - 1] == -1 and \
                    c[idx] <= ary_lband[idx]:
                ary_SdBlaT.append(-1)
                ary_SdBlaTp.append(0)
                ary_SdBlaTm.append(1)
            else:
                ary_SdBlaT.append(0)
                ary_SdBlaTp.append(0)
                ary_SdBlaTm.append(0)

        df_ohclv["SarT"] = ary_SarT
        df_ohclv["SarTp"] = ary_SarTp
        df_ohclv["SarTm"] = ary_SarTm
        df_ohclv["Sar"] = ary_Sar

        df_ohclv["SdBlaT"] = ary_SdBlaT
        df_ohclv["SdBlaTp"] = ary_SdBlaTp
        df_ohclv["SdBlaTm"] = ary_SdBlaTm

        # # Simple Moving Average 5
        # df_ohclv['Sma5'] = pd.Series(df_ohclv.Close).rolling(window=5).mean()
        # # Simple Moving Average 20
        # df_ohclv['Sma20'] = pd.Series(df_ohclv.Close).rolling(window=20).mean()
        # # Simple Moving Average 60
        # df_ohclv['Sma60'] = pd.Series(df_ohclv.Close).rolling(window=60).mean()
        #
        # # Exponential Moving Average 5
        # df_ohclv['Ema5'] = pd.Series(df_ohclv.Close).ewm(span=5).mean()
        # # Exponential Moving Average 20
        # df_ohclv['Ema20'] = pd.Series(df_ohclv.Close).ewm(span=20).mean()
        # # Exponential Moving Average 40
        # df_ohclv['Ema40'] = pd.Series(df_ohclv.Close).ewm(span=40).mean()
        #
        # # True Range
        # df_ohclv['Tr'] = np.max([df_ohclv.High - df_ohclv.Low,
        #                          (pd.Series(df_ohclv.Close).shift(1) - df_ohclv.High).abs(),
        #                          (pd.Series(df_ohclv.Close).shift(1) - df_ohclv.Low).abs()],
        #                         axis=0)
        # # Average True Range
        # df_ohclv["Atr"] = pd.Series(df_ohclv.Tr).rolling(window=7).mean()
        #
        # # SIC (期間中の最大と最小)
        # df_ohclv["SicH"] = pd.Series(df_ohclv.Close).rolling(window=20).max()
        # df_ohclv["SicL"] = pd.Series(df_ohclv.Close).rolling(window=20).min()
        #
        # # Wilder Volatility System Trend
        # df_ohclv["WVST"] = "None"
        #
        #
        #
        # # Stop And Reverse (SAR)

        return df_ohclv
