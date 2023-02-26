import numpy as np
from ta import volatility
import pandas as pd
from ccxt_ohlc import *


def cumulative_sum(arr1, arr2, i=0):
    if len(arr1) != len(arr2):
        raise ValueError

    if i == len(arr1):
        return []

    if not i == len(arr1):
        curr_sum = (arr1[i] - arr2[i]) / (i + 1)
        i += 1
        result = [curr_sum] + cumulative_sum(arr1, arr2, i)
        return result


atr_smoothing_range = 200
atr = np.array(volatility.average_true_range(pd.Series(dfLB['high'].values),
                                    pd.Series(dfLB['low'].values),
                                    pd.Series(dfLB['close'].values),
                                    window=atr_smoothing_range))

cmean_range = cumulative_sum(dfLB['high'].tolist(), dfLB['low'].tolist())