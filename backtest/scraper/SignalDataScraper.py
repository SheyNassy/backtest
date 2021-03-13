from datetime import datetime, timedelta

from pandas import DataFrame

from backtest.scraper.WebParser import WebParser
from backtest.scraper.WebScraper import WebScraper
import calendar


class SignalDataScraper:

    @classmethod
    def getData(cls, startDate=None, endDate=None) -> DataFrame:

        if startDate is None:
            # 開始日指定がない場合 サイト内の一番古い日付
            startDate = datetime.strptime('2018-05-27', '%Y-%m-%d')

        if endDate is None:
            # 終了日指定がない場合
            # 昨日
            endDate = datetime.today() - timedelta(days=1)

        def dateToUrl(_start, _end) -> datetime:
            for n in range((_end - _start).days):
                delta = _start + timedelta(n)
                print(delta)
                yield cls.__createUrl(delta)

        df: DataFrame = None

        for url in dateToUrl(startDate, endDate):
            dataTable = WebScraper.getIdFilteredContent(url, 'tbldtl')
            df = WebParser.parseTable(dataTable, df=df)
            print(df.size)

        return df

    @classmethod
    def __createUrl(cls, date: datetime) -> str:
        y = str(date.year)
        m = str(date.month)

        if len(m) == 1:
            m = "0{_m}".format(_m=m)

        d = str(date.day)
        if len(d) == 1:
            d = "0{_d}".format(_d=d)

        # 'https://realtime-chart.com/ja/bitflyer/resultday_20210312.html'
        return 'https://realtime-chart.com/ja/bitflyer/resultday_{y}{m}{d}.html'.format(y=y, m=m, d=d)
