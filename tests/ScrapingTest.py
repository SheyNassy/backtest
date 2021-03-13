import unittest
from datetime import datetime, timedelta

from backtest.scraper.SignalDataScraper import SignalDataScraper
from backtest.scraper.WebParser import WebParser
from backtest.scraper.WebScraper import WebScraper


class MyTestCase(unittest.TestCase):
    def test_something(self):
        df = SignalDataScraper.getData()
        # t = WebScraper.getIdFilteredContent('https://realtime-chart.com/ja/bitflyer/resultday_20210312.html', 'tbldtl')
        # WebParser.parseTable(t)
        # s = 'str'
        # l = len(s)
        # print(l)
        # u = SignalDataScraper.createUrl(datetime.today() - timedelta(days=5))
        # print(u)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
