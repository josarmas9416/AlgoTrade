import numpy
import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta
import broker.mt5 as server
import traceback

server.init()

try:
    data = server.getSymbolData('GBPUSD', 10000, mt5.TIMEFRAME_M1)

    data['moving-average'] = ta.ema(data['close'], 25)
    data['dif'] = data['close'] - data['moving-average']

    data['dif'].hist(bins=30)

except Exception as e:
    print('Unexpected error {}'.format(e))
    traceback.print_exc()
finally:
    server.shutdown()