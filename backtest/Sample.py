from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtest import SMA, N225_2020


class VolatilitySystem(Strategy):
    def init(self):
        price = self.data.Close
        # self.ma1 = self.I(SMA, price, 10)
        # self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if self.data.SarT[-1] > 0 and \
                self.data.SarT[-2] <= 0:
            self.buy()
        elif self.data.SarT[-1] < 0 and \
                self.data.SarT[-2] >= 0:
            self.position.close()


class StdDevVolaModel(Strategy):
    def init(self):
        price = self.data.Close
        # self.ma1 = self.I(SMA, price, 10)
        # self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if self.data.SdBlaT[-1] > 0 and \
                self.data.SdBlaT[-2] <= 0:
            self.buy()
        elif self.data.SdBlaT[-1] < 0 and \
                self.data.SdBlaT[-2] >= 0:
            self.position.close()
            # self.sell()


bt = Backtest(N225_2020, StdDevVolaModel, cash=500000,
              exclusive_orders=True)
stats = bt.run()
print(stats)
# bt.plot()
