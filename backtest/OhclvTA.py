from typing import Callable, Tuple, List, Dict

import numpy as np
import pandas as pd
import talib as ta
from pandas import DataFrame


class OhclvTechnicalAnalyzeCalculator():

    @classmethod
    def calc(cls, marketItem):
        # 生配列をnp DataFrameに変換
        df_ohclv = pd.DataFrame(marketItem,
                                columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        # 欠損値の削除
        df_ohclv = df_ohclv.dropna()

        # PlotlyとTA-libでテクニカル分析チャートを描く
        # https://akatak.hatenadiary.jp/entry/2019/11/23/220836

        o = np.array(df_ohclv['Open'].fillna(method='ffill'))
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

        # ▽▲▽▲▽▲ 2021/3/6 袋 とりあえず talibの全追加 ▽▲▽▲▽▲
        # ◆◆ OverWrap ◆◆
        # ● BBANDS - Bollinger Bands
        # 済

        # ● DEMA - Double Exponential Moving Average    real = DEMA(close, timeperiod=30)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='DEMA', timeperiods=(5, 10, 20, 40, 60))

        # ● EMA - Exponential Moving Average    real = EMA(close, timeperiod=30)
        # 済

        # ● HT_TRENDLINE - Hilbert Transform - Instantaneous Trendline  real = HT_TRENDLINE(close)
        # df_ohclv["HT_TRENDLINE"] = ta.HT_TRENDLINE(c)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='HT_TRENDLINE')

        # ● KAMA - Kaufman Adaptive Moving Average  real = KAMA(close, timeperiod=30)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='KAMA', timeperiods=(5, 10, 20, 40, 60))

        # ● MA - Moving average real = MA(close, timeperiod=30, matype=0)
        # SMAと一緒？

        # ● MAMA - MESA Adaptive Moving Average mama, fama = MAMA(close, fastlimit=0, slowlimit=0)
        # df_ohclv["MAMA"] = ta.MAMA(c, fastlimit=0, slowlimit=0)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='MIDPOINT', timeperiods=(5, 10, 20, 40, 60),
                                        multiReturns=('MAMA', 'FAMA'))

        # ● MAVP - Moving average with variable period  real = MAVP(close, periods, minperiod=2, maxperiod=30, matype=0)
        # real = MAVP(close, periods, minperiod=2, maxperiod=30, matype=0)
        # periodの使い方がよくわからんから後回し

        # ● MIDPOINT - MidPoint over period real = MIDPOINT(close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='MIDPOINT', timeperiods=(5, 10, 20, 40, 60))

        # ● MIDPRICE - Midpoint Price over period   real = MIDPRICE(high, low, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, df=df_ohclv, func='MIDPRICE', timeperiods=(5, 10, 20, 40, 60))

        # ● SAR - Parabolic SAR real = SAR(high, low, acceleration=0, maximum=0)
        df_ohclv = cls.__appendTAColumn(h, l, acceleration=0, maximum=0, df=df_ohclv, func='SAR')

        # ● SAREXT - Parabolic SAR - Extended   real = SAREXT(high, low, startvalue=0, offsetonreverse=0, accelerationinitlong=0, accelerationlong=0, accelerationmaxlong=0, accelerationinitshort=0, accelerationshort=0, accelerationmaxshort=0)
        df_ohclv = cls.__appendTAColumn(h, l, startvalue=0, offsetonreverse=0, accelerationinitlong=0,
                                        accelerationlong=0,
                                        accelerationmaxlong=0, accelerationinitshort=0, accelerationshort=0,
                                        accelerationmaxshort=0, df=df_ohclv, func='SAREXT')

        # ● SMA - Simple Moving Average
        # 済

        # ● T3 - Triple Exponential Moving Average (T3) real = T3(close, timeperiod=5, vfactor=0)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='T3', timeperiods=(5, 10, 20, 40, 60))

        # ● TEMA - Triple Exponential Moving Average    real = TEMA(close, timeperiod=30)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='TEMA', timeperiods=(5, 10, 20, 40, 60))

        # ● TRIMA - Triangular Moving Average   real = TRIMA(close, timeperiod=30)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='TRIMA', timeperiods=(5, 10, 20, 40, 60))

        # ● WMA - Weighted Moving Average   real = WMA(close, timeperiod=30)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='WMA', timeperiods=(5, 10, 20, 40, 60))

        # ◆◆ Momentum Indicator Functions ◆◆
        # ● ADX - Average Directional Movement Index    real = ADX(high, low, close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='ADX', timeperiods=(5, 10, 20, 40, 60))

        # ● ADXR - Average Directional Movement Index Rating real = ADXR(high, low, close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='ADXR', timeperiods=(5, 10, 20, 40, 60))

        # ● APO - Absolute Price Oscillator real = APO(close, fastperiod=12, slowperiod=26, matype=0)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='APO', fastperiod=12, slowperiod=26, matype=0)

        # ● AROON - Aroon   aroondown, aroonup = AROON(high, low, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, df=df_ohclv, func='AROON', timeperiods=(5, 10, 20, 40, 60),
                                        multiReturns=('DOWN', 'UP'))

        # ● AROONOSC - Aroon Oscillator real = AROONOSC(high, low, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, df=df_ohclv, func='AROONOSC', timeperiods=(5, 10, 20, 40, 60))

        # ●BOP - Balance Of Power   real = BOP(open, high, low, close)
        df_ohclv = cls.__appendTAColumn(o, h, l, c, df=df_ohclv, func='BOP')

        # ● CCI - Commodity Channel Index   real = CCI(high, low, close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='CCI', timeperiods=(5, 10, 20, 40, 60))

        # ●CMO - Chande Momentum Oscillator real = CMO(close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='CMO', timeperiods=(5, 10, 20, 40, 60))

        # ●DX - Directional Movement Index  real = DX(high, low, close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='DX', timeperiods=(5, 10, 20, 40, 60))

        # ●MACD - Moving Average Convergence/Divergence macd, macdsignal, macdhist = MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        df_ohclv = cls.__appendTAColumn(c, fastperiod=12, slowperiod=26, signalperiod=9, df=df_ohclv, func='MACD',
                                        multiReturns=('MACD', 'SIGNAL', 'HIST'))

        # ● MACDEXT - MACD with controllable MA type  macd, macdsignal, macdhist = MACDEXT(close, fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9, signalmatype=0)
        df_ohclv = cls.__appendTAColumn(c, fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9,
                                        signalmatype=0, df=df_ohclv, func='MACDEXT',
                                        multiReturns=('MACD', 'SIGNAL', 'HIST'))

        # ● MACDFIX - Moving Average Convergence/Divergence Fix 12/26   macd, macdsignal, macdhist = MACDFIX(close, signalperiod=9)
        df_ohclv = cls.__appendTAColumn(c, signalperiod=9, df=df_ohclv, func='MACDFIX',
                                        multiReturns=('MACD', 'SIGNAL', 'HIST'))

        # ● MFI - Money Flow Index  real = MFI(high, low, close, volume, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, c, v, df=df_ohclv, func='MFI', timeperiods=(5, 10, 20, 40, 60))

        # ● MINUS_DI - Minus Directional Indicator  real = MINUS_DI(high, low, close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='MINUS_DI', timeperiods=(5, 10, 20, 40, 60))

        # ● MINUS_DM - Minus Directional Movement   real = MINUS_DM(high, low, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, df=df_ohclv, func='MINUS_DM', timeperiods=(5, 10, 20, 40, 60))

        # ● MOM - Momentum  real = MOM(close, timeperiod=10)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='MOM', timeperiods=(5, 10, 20, 40, 60))

        # ● PLUS_DI - Plus Directional Indicator    real = PLUS_DI(high, low, close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='PLUS_DI', timeperiods=(5, 10, 20, 40, 60))

        # ● PLUS_DM - Plus Directional Movement real = PLUS_DM(high, low, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, df=df_ohclv, func='PLUS_DM', timeperiods=(5, 10, 20, 40, 60))

        # ● PPO - Percentage Price Oscillator   real = PPO(close, fastperiod=12, slowperiod=26, matype=0)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='PPO', fastperiod=12, slowperiod=26, matype=0)

        # ● ROC - Rate of change : ((price/prevPrice)-1)*100    real = ROC(close, timeperiod=10)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='ROC', timeperiods=(5, 10, 20, 40, 60))

        # ●ROCP - Rate of change Percentage: (price-prevPrice)/prevPrice    real = ROCP(close, timeperiod=10)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='ROCP', timeperiods=(5, 10, 20, 40, 60))

        # ● ROCR - Rate of change ratio: (price/prevPrice) real = ROCR(close, timeperiod=10)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='ROCR', timeperiods=(5, 10, 20, 40, 60))

        # ● ROCR100 - Rate of change ratio 100 scale: (price/prevPrice)*100 real = ROCR100(close, timeperiod=10)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='ROCR100', timeperiods=(5, 10, 20, 40, 60))

        # ● RSI - Relative Strength Index real = RSI(close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='RSI', timeperiods=(5, 10, 20, 40, 60))

        # ● STOCH - Stochastic slowk, slowd = STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='STOCH', fastk_period=5, slowk_period=3,
                                        slowk_matype=0, slowd_period=3, slowd_matype=0,
                                        multiReturns=('SLOWK', 'SLOWD'))

        # ● STOCHF - Stochastic Fast    fastk, fastd = STOCHF(high, low, close, fastk_period=5, fastd_period=3, fastd_matype=0)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='STOCHF', fastk_period=5, fastd_period=3,
                                        fastd_matype=0,
                                        multiReturns=('FASTK', 'FASTD'))

        # ●STOCHRSI - Stochastic Relative Strength Index    fastk, fastd = STOCHRSI(close, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='STOCHRSI', fastk_period=5, fastd_period=3, fastd_matype=0,
                                        multiReturns=('FASTK', 'FASTD'), timeperiods=(5, 10, 20, 40, 60))

        # ● TRIX - 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA    real = TRIX(close, timeperiod=30)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='TRIX', timeperiods=(5, 10, 20, 40, 60))

        # ● ULTOSC - Ultimate Oscillator    real = ULTOSC(high, low, close, timeperiod1=7, timeperiod2=14, timeperiod3=28)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='ULTOSC', timeperiod1=7, timeperiod2=14,
                                        timeperiod3=28)

        # ● WILLR - Williams' %R    real = WILLR(high, low, close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='WILLR', timeperiods=(5, 10, 20, 40, 60))

        # ◆◆ Volume Indicators ◆◆

        # ● AD - Chaikin A/D Line   real = AD(high, low, close, volume)
        df_ohclv = cls.__appendTAColumn(h, l, c, v, df=df_ohclv, func='AD')

        # ● ADOSC - Chaikin A/D Oscillator  real = ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
        df_ohclv = cls.__appendTAColumn(h, l, c, v, df=df_ohclv, func='ADOSC', fastperiod=3, slowperiod=10)

        # ● OBV - On Balance Volume real = OBV(close, volume)
        df_ohclv = cls.__appendTAColumn(c, v, df=df_ohclv, func='OBV')

        # ◆◆ Volatility Indicators ◆◆
        # ● ATR - Average True Range
        # 済

        # ● NATR - Normalized Average True Range    real = NATR(high, low, close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='NATR', timeperiods=(5, 10, 20, 40, 60))

        # ● TRANGE - True Range real = TRANGE(high, low, close)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='TRANGE')

        # ◆◆ Price Transform Functions◆◆
        # ● AVGPRICE - Average Price    real = AVGPRICE(open, high, low, close)
        df_ohclv = cls.__appendTAColumn(o, h, l, c, df=df_ohclv, func='AVGPRICE')

        # ● MEDPRICE - Median Price real = MEDPRICE(high, low)
        df_ohclv = cls.__appendTAColumn(h, l, df=df_ohclv, func='MEDPRICE')

        # ● TYPPRICE - Typical Price    real = TYPPRICE(high, low, close)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='TYPPRICE')

        # ● WCLPRICE - Weighted Close Price real = WCLPRICE(high, low, close)
        df_ohclv = cls.__appendTAColumn(h, l, c, df=df_ohclv, func='WCLPRICE')

        # ◆◆ Cycle Indicator Functions ◆◆

        # ● HT_DCPERIOD - Hilbert Transform - Dominant Cycle Period real = HT_DCPERIOD(close)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='HT_DCPERIOD')

        # ● HT_DCPHASE - Hilbert Transform - Dominant Cycle Phase   real = HT_DCPHASE(close)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='HT_DCPHASE')

        # ● HT_PHASOR - Hilbert Transform - Phasor Components inphase, quadrature = HT_PHASOR(close)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='HT_PHASOR', multiReturns=('INPHASE', 'QUADRATURE'))

        # ● HT_SINE - Hilbert Transform - SineWave  sine, leadsine = HT_SINE(close)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='HT_SINE', multiReturns=('SINE', 'LEADSINE'))

        # ● HT_TRENDMODE - Hilbert Transform - Trend vs Cycle Mode  integer = HT_TRENDMODE(close)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='HT_TRENDMODE')

        # ◆◆ Pattern Recognition Functions ◆◆

        _func: Tuple = (
            'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE', 'CDL3OUTSIDE', 'CDL3STARSINSOUTH',
            'CDL3WHITESOLDIERS', 'CDLADVANCEBLOCK', 'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU',
            'CDLCONCEALBABYSWALL', 'CDLCOUNTERATTACK', 'CDLDOJI', 'CDLDOJISTAR', 'CDLDRAGONFLYDOJI',
            'CDLENGULFING', 'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN',
            'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON',
            'CDLIDENTICAL3CROWS', 'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH',
            'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI', 'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW',
            'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS', 'CDLSEPARATINGLINES',
            'CDLSHOOTINGSTAR', 'CDLSHORTLINE', 'CDLSPINNINGTOP', 'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH',
            'CDLTAKURI', 'CDLTASUKIGAP', 'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER',
            'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS')

        for f in _func:
            df_ohclv = cls.__appendTAColumn(o, h, l, c, df=df_ohclv, func=f)

        _func: Tuple = ('CDLABANDONEDBABY', 'CDLDARKCLOUDCOVER', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLMATHOLD',
                        'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR')
        for f in _func:
            df_ohclv = cls.__appendTAColumn(o, h, l, c, df=df_ohclv, func=f, penetration=0)

        # ◆◆ Statistic Functions ◆◆

        # ● BETA - Beta real = BETA(high, low, timeperiod=5)
        df_ohclv = cls.__appendTAColumn(h, l, df=df_ohclv, func='BETA', timeperiods=(5, 10, 20, 40, 60))

        # ● CORREL - Pearson's Correlation Coefficient (r)  real = CORREL(high, low, timeperiod=30)
        df_ohclv = cls.__appendTAColumn(h, l, df=df_ohclv, func='CORREL', timeperiods=(5, 10, 20, 40, 60))

        # ● LINEARREG - Linear Regression   real = LINEARREG(close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='LINEARREG', timeperiods=(5, 10, 20, 40, 60))

        # ● LINEARREG_ANGLE - Linear Regression Angle   real = LINEARREG_ANGLE(close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='LINEARREG_ANGLE', timeperiods=(5, 10, 20, 40, 60))

        # ● LINEARREG_INTERCEPT - Linear Regression Intercept   real = LINEARREG_INTERCEPT(close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='LINEARREG_INTERCEPT', timeperiods=(5, 10, 20, 40, 60))

        # ● LINEARREG_SLOPE - Linear Regression Slope   real = LINEARREG_SLOPE(close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='LINEARREG_SLOPE', timeperiods=(5, 10, 20, 40, 60))

        # ● STDDEV - Standard Deviation real = STDDEV(close, timeperiod=5, nbdev=1)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='STDDEV', timeperiods=(5, 10, 20, 40, 60), nbdev=1)

        # ● TSF - Time Series Forecast  real = TSF(close, timeperiod=14)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='TSF', timeperiods=(5, 10, 20, 40, 60))

        # ● VAR - Variance  real = VAR(close, timeperiod=5, nbdev=1)
        df_ohclv = cls.__appendTAColumn(c, df=df_ohclv, func='VAR', timeperiods=(5, 10, 20, 40, 60), nbdev=1)

        # ◆◆ Statistic Functions ◆◆

        # ●
        # ●

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

    @classmethod
    def __appendTAColumn(*args, **kwargs) -> DataFrame:
        df: DataFrame = kwargs.pop('df')
        func: str = kwargs.pop('func')

        # cls取り除く
        _al: List = list(args)
        del _al[0]
        _at: Tuple = tuple(_al)

        timePeriods: Tuple
        tHas: bool = True
        multiReturns: Tuple
        isMulti: bool = True

        try:
            timePeriods = kwargs.pop('timeperiods')
        except KeyError:
            tHas = False

        try:
            multiReturns: tuple = kwargs.pop('multiReturns')
        except KeyError:
            isMulti = False

        if tHas:  # timeperiodアリの場合
            if isMulti:  # 戻り値複数の場合
                for tp in timePeriods:
                    kwargs['timeperiod'] = tp
                    _ret: Tuple = eval('ta.' + func)(*_at, **kwargs)
                    for i in range(len(multiReturns)):
                        df["{f}_{r}_{p}".format(f=func, r=multiReturns[i], p=tp)] = _ret[i]
            else:  # 戻り値1つのとき
                for tp in timePeriods:
                    kwargs['timeperiod'] = tp
                    df["{f}_{p}".format(f=func, p=tp)] = eval('ta.' + func)(*_at, **kwargs)

        else:  # timeperiodナシの場合
            if isMulti:  # 戻り値複数の場合
                _ret: Tuple = eval('ta.' + func)(*_at, **kwargs)
                for i in range(len(multiReturns)):
                    df["{f}_{r}".format(f=func, r=multiReturns[i])] = _ret[i]
            else:  # 戻り値1つのとき
                df["{f}".format(f=func)] = eval('ta.' + func)(*_at, **kwargs)
        return df
