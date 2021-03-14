from datetime import datetime

from pandas import pandas, DataFrame


class CsvRW:

    @classmethod
    def createCsv(cls, folderPath: str, fileNameBase: str, df: DataFrame) -> None:
        date = datetime.today()
        y = str(date.year)
        M = str(date.month)

        if len(M) == 1:
            M = "0{_M}".format(_M=M)

        D = str(date.day)
        if len(D) == 1:
            D = "0{_D}".format(_D=D)
        h = str(date.hour)
        m = str(date.minute)

        path: str = '{d}/{f}_{y}{M}{D}{h}{m}.csv'.format(d=folderPath,
                                                         f=fileNameBase, y=y, M=M, D=D, h=h, m=m)

        df.to_csv(path, mode='w', header=True, index=False)

    @classmethod
    def readDirCsv(cls, dirPath: str) -> DataFrame:
        pass

    @classmethod
    def readCsv(cls, filePath: str) -> DataFrame:
        pandas.read_csv()
