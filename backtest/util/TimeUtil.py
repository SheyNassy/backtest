from datetime import datetime
import time


class TimeUtil:

    # 現在時刻のUnixTime。 msecまでを整数化して返す（ccxtのTimeStampに合わせて）
    @classmethod
    def getUnixTime3rdDecimal(cls):
        return int(time.time() * 1000)

    @classmethod
    def getPastTime(cls, sec: int):
        return cls.getUnixTime3rdDecimal() - sec * 1000

    @classmethod
    def getLocalTime(cls):
        return datetime.fromtimestamp(time.time())

    # unixtime(msec)整数を　DateTimeで返す
    @classmethod
    def convertUnixToDateTime(cls, unixtime) -> datetime:
        return datetime.fromtimestamp(float(unixtime / 1000))

    @classmethod
    def convertDateTimeToUnix(cls, dt: datetime) -> int:
        ud = dt.timestamp()
        return ud * 1000
