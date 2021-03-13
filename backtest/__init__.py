"""Data and utilities for testing."""
import pandas as pd


def _read_file(filename):
    from os.path import dirname, join

    return pd.read_csv(join(dirname(__file__), filename),
                       index_col=0, parse_dates=True, infer_datetime_format=True)


# GOOG = _read_file('data\\GOOG.csv')
"""DataFrame of daily NASDAQ:GOOG (Google/Alphabet) stock price data from 2004 to 2013."""

# EURUSD = _read_file('data\\EURUSD.csv')
"""DataFrame of hourly EUR/USD forex data from April 2017 to February 2018."""

# N225_2020 = _read_file('data\\%5EN225_2018-12-01_2019-12-31.csv')


def SMA(arr: pd.Series, n: int) -> pd.Series:
    """
    Returns `n`-period simple moving average of array `arr`.
    """
    return pd.Series(arr).rolling(n).mean()
