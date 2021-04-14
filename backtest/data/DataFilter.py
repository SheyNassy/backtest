from datetime import datetime
from typing import List, Dict

from pandas import DataFrame


class DataFilter:

    @classmethod
    def getEntryLearningData(cls, df: DataFrame) -> DataFrame:
        pass

    @classmethod
    def getExitLearningData(cls, df: DataFrame) -> DataFrame:
        pass

    @classmethod
    def getTermData(cls, start: datetime, end: datetime, df: DataFrame) -> DataFrame:
        col: set = df.columns
        backDataTimeHeader: str = 'Unix Timestamp'
        learningDataTimeHeader: str = '発注時刻'

        timeHeader: str
        startStr: str
        endStr: str

        if {backDataTimeHeader}.issubset(col):
            timeHeader = backDataTimeHeader
            startStr = TimeUtil.getUnixTime3rdDecimal()
            endStr = ''
        elif {learningDataTimeHeader}.issubset(col):
            timeHeader = learningDataTimeHeader
            startStr = ''
            endStr = ''
        else:
            raise ValueError("Unmatch Header")

        return df.query('{e}>={h}>={s}'.format(e=endStr, h=timeHeader, s=startStr))
