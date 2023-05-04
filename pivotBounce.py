import mt5 as server
import MetaTrader5 as mt5
import time
import traceback

def calculatePivotPoints(high, low, close):
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)
    return (pivot, r1, r2, r3, s1, s2, s3)

server.init()

try:
    # select the financial instrument to analyze
    symbol = "EURUSD"
    lastData = 1000
    timeframe = mt5.TIMEFRAME_D1

    # request historical prices
    prices_df = server.getSymbolData(symbol, lastData, timeframe)
    prices_df.set_index('time', inplace=True)

    # calculate support and resistance levels
    high = prices_df['high']
    low = prices_df['low']
    close = prices_df['close']

    pivot, r1, r2, r3, s1, s2, s3 = calculatePivotPoints(high, low, close)

    print("Support and Resistance Levels for", symbol)
    print("Pivot Point:", pivot[-1])
    print("Resistance 1:", r1[-1])
    print("Support 1:", s1[-1])
    print("Resistance 2:", r2[-1])
    print("Support 2:", s2[-1])
    print("Resistance 3:", r3[-1])
    print("Support 3:", s3[-1])

except Exception as e:
    print('Unexpected error {}'.format(e))
    traceback.print_exc()
finally:
    server.shutdown()
