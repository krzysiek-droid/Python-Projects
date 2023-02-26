from ccxt_ohlc import *
from price_indicators import *

import pandas as pd


# hh = dfLB.loc[dfLB['time'] == datetime(2023, 2, 22, 16, 35)]

def detect_swings(n_bar, length, target_market_state):
    highs = dfLB['high'].values.tolist()[:n_bar]
    lows = dfLB['low'].values.tolist()[:n_bar]
    # find highest and lowest price in the set of previous prices (in window of length)
    upper = max(highs[-length:])
    lower = min(lows[-length:])
    top, bottom = 0, 0

    if len(target_market_state) < 1:
        if highs[-length] >= upper and highs[-length] > dfLB['high'][n_bar]:
            target_market_state.append(0)
        elif lows[-length] <= lower and lows[-length] < dfLB['low'][n_bar]:
            target_market_state.append(1)
    else:
        if highs[-length] >= upper and highs[-length] > dfLB['high'][n_bar]:
            target_market_state.append(0)
            if target_market_state[-1] == 0 and target_market_state[-2] != 0:
                top = highs[-length]
        elif lows[-length] <= lower and lows[-length] < dfLB['low'][n_bar]:
            target_market_state.append(1)
            if target_market_state[-1] == 1 and target_market_state[-2] != 1:
                bottom = lows[-length]
        else:
            target_market_state.append(target_market_state[-1])
    return top, bottom


# Simple translation
def ob_coord(use_max: bool, n_bar, loc: int, order_block_df: pd.DataFrame,
             ob_filter='Atr'):
    """This function is used to calculate the coordinates of an order block within a price chart. It takes as input
    the type of order block (either a buy order block or a sell order block), a location parameter, and other optional
    parameters. It then searches for the highest/lowest high within the structure interval and gets the range.
    Finally, it returns the coordinates of the order block in the form of a dictionary with the top, bottom,
    left (time) and type (buy or sell) of the order block."""

    high = pd.Series(dfLB['high']).tolist()[:n_bar]
    low = pd.Series(dfLB['low']).tolist()[:n_bar]
    time = pd.Series(dfLB['time']).tolist()[:n_bar]

    min_val = 9999
    max_val = 0
    idx = 1

    ob_threshold = atr[:n_bar] if ob_filter == 'Atr' else cmean_range[:n_bar]

    # Search for highest/lowest high within the structure interval and get range
    if use_max:
        for i in range(1, (n_bar - loc)):
            if (high[-i] - low[-i]) < (ob_threshold[-i] * 2):
                if high[-i] > max_val:
                    max_val = high[-i]
                    min_val = low[-i]
                    idx = i
    else:
        for i in range(1, (n_bar - loc)):
            if (high[-i] - low[-i]) < (ob_threshold[-i] * 2):
                if low[-i] < min_val:
                    min_val = low[-i]
                    max_val = high[-i]
                    idx = i
    order_block_df.loc[len(order_block_df)] = [max_val, min_val, time[-idx], -1 if use_max else 1]


def cross_over(source1, source2):
    if source1[-1] > source2[-1] and source1[-2] <= source2[-2]:
        return True
    return False


def cross_under(source1, source2):
    if source1[-1] < source2[-1] and source1[-2] >= source2[-2]:
        return True
    return False


def filter_order_blocks(ob_df: pd.DataFrame, close, target_list):
    for row in ob_df.iterrows():
        if row[1]['btm'] > close and row[1]['type'] == 1:
            target_list.append(row[0])
        elif row[1]['top'] < close and row[1]['type'] == -1:
            target_list.append(row[0])


def find_low_pivots(arr: list, window_size, threshold):
    lows = []
    if window_size % 2 != 0:
        for i in range(len(arr))[window_size:-3]:
            window = arr[i - window_size:i + window_size + 1]
            if arr[i] == min(window) and \
                    round(abs(arr[i] - arr[i - 1]), 1) >= threshold and round(abs(arr[i] - arr[i + 1]), 1) >= threshold:
                lows.append(i)
        return lows
    else:
        for i in range(len(arr))[window_size:-3]:
            window = arr[i - window_size:i + window_size + 1]
            if arr[i] == min(window) and \
                    round(abs(arr[i] - arr[i - 1]), 1) >= threshold and round(abs(arr[i] - arr[i + 1]), 1) >= threshold:
                lows.append(i)
        return lows


def find_high_pivots(arr: list, window_size, threshold):
    highs = []
    if window_size % 2 != 0:
        for i in range(len(arr))[window_size:-3]:
            window = arr[i - window_size:i + window_size + 1]
            if arr[i] == max(window) and \
                    round(abs(arr[i] - arr[i - 1]), 1) >= threshold and round(abs(arr[i] - arr[i + 1]), 1) >= threshold:
                highs.append(i)
        return highs
    else:
        for i in range(len(arr))[window_size:-3]:
            window = arr[i - window_size:i + window_size + 1]
            if arr[i] == max(window) and \
                    round(abs(arr[i] - arr[i - 1]), 1) >= threshold and round(abs(arr[i] - arr[i + 1]), 1) >= threshold:
                highs.append(i)
        return highs


def get_ohlc(OHLCdata: pd.DataFrame, n_bar):
    p_close = OHLCdata['close'][n_bar - 1]
    p_open = OHLCdata['open'][n_bar - 1]
    high = OHLCdata['high'][n_bar]
    low = OHLCdata['low'][n_bar]
    pp_high = OHLCdata['high'][n_bar - 2]
    pp_low = OHLCdata['low'][n_bar - 2]

    return p_close, p_open, high, low, pp_high, pp_low


def show_previous_hl(new_timeframe):
    ohlcv = get_data(symbol, new_timeframe)
    prev_high = ohlcv['high'].tolist()[-2]
    prev_low = ohlcv['low'].tolist()[-2]
    print(f"Previous timeframe data for {new_timeframe} -> HIGH: {prev_high} | LOW: {prev_low}")
    return prev_high, prev_low
