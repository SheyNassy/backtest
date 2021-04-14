import pathlib
import unittest
from datetime import datetime, timedelta

from backtest.io.CsvRW import CsvRW
from backtest.scraper.SignalDataScraper import SignalDataScraper
from backtest.scraper.WebParser import WebParser
from backtest.scraper.WebScraper import WebScraper


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # d = datetime.today() - timedelta(days=2)
        # df = SignalDataScraper.getData(startDate=d)
        #

        print({'a', 'b'}.issubset({'a'}))
        print({'a', }.issubset({'a', 'b'}))
        #
        # df = SignalDataScraper.getData()
        # path = str(pathlib.Path.cwd().parent) + '\data\signal'
        # CsvRW.createCsv(path, 'BotSignal', df)
        # self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
