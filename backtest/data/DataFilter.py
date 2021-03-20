from datetime import datetime

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
        pass
