from bs4 import Tag
import pandas as pd
from pandas import DataFrame


class WebParser:

    @classmethod
    def parseTable(cls, table: Tag, df: DataFrame = None) -> DataFrame:

        if table is None:
            return df

        rows = table.find_all('tr')
        # ヘッダー
        cHeader = [th.text for th in rows[0].find_all('th')]
        if df is None:
            df = pd.DataFrame(columns=cHeader)

        for i in range(len(rows)):
            tds = [td.text for td in rows[i].find_all('td')]
            if len(tds) == len(cHeader):
                df = df.append(pd.Series(tds, index=cHeader), ignore_index=True)
        return df
