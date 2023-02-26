import pandas as pd
import ccxt
from datetime import datetime
import warnings
from ta import volatility
import numpy as np

warnings.filterwarnings("ignore")
symbol = "ETH/BUSD"  # Binance
pos_size = 1
timeframe = "5m"

account_binance = ccxt.binance({
    "apiKey": '',
    "secret": '',
    "enableRateLimit": True,
    'options': {
        'defaultType': 'spot'
    }
})


def get_data(sbl, tf):
    orderTime = datetime.utcnow()
    ohlcvLB = account_binance.fetch_ohlcv(sbl, tf)
    data = pd.DataFrame(ohlcvLB, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    indiPoint = pd.DataFrame(columns=['time'])
    if len(ohlcvLB):
        data['time'] = pd.to_datetime(data['time'], unit='ms')
        return data


dfLB = get_data(symbol, timeframe)
print(dfLB)
