import mt5 as server
import MetaTrader5 as mt5
import traceback

def calculatePivotPoints(high, low, close):
    pivot = (high + low + close) / 3
    firstRessistance = 2 * pivot - low
    firstSupport = 2 * pivot - high
    secondRessistance = pivot + (high - low)
    secondSupport = pivot - (high - low)
    thirdRessistance = high + 2 * (pivot - low)
    thirdSupport = low - 2 * (high - pivot)

    mean = (high + low ) / 2
    return (pivot[-1], firstRessistance[-1], secondRessistance[-1], thirdRessistance[-1], firstSupport[-1], secondSupport[-1], thirdSupport[-1], mean[-1])

server.init()

try:
    # select the financial instrument to analyze
    symbol = ".USTECHCash"
    lastData = 2
    timeframe = mt5.TIMEFRAME_D1
    volume = 0.05

    # request historical prices
    prices_df = server.getSymbolData(symbol, lastData, timeframe)
    prices_df.set_index('time', inplace=True)

    # calculate support and resistance levels
    high = prices_df['high']
    low = prices_df['low']
    close = prices_df['close']

    pivot, firstRessistance, secondRessistance, thirdRessistance, firstSupport, secondSupport, thirdSupport, mean = calculatePivotPoints(high, low, close)

    print("Support and Resistance Levels for", symbol)
    print("Pivot Point:", pivot)
    print("Resistance 1:", firstRessistance)
    print("Support 1:", firstSupport)
    print("Resistance 2:", secondRessistance)
    print("Support 2:", secondSupport)
    print("Resistance 3:", thirdRessistance)
    print("Support 3:", thirdSupport)
    print("Mean:", mean)

    # Mean Reversal
    pendingOrderBuy = server.sendOperation(mt5.TRADE_ACTION_PENDING, symbol, volume, secondSupport, mean, mt5.ORDER_TYPE_BUY_LIMIT, price = firstSupport)
    pendingOrderSell = server.sendOperation(mt5.TRADE_ACTION_PENDING, symbol, volume, secondRessistance, mean, mt5.ORDER_TYPE_SELL_LIMIT, price = firstRessistance)

    # BreakThrough
    pendingOrderBuyB = server.sendOperation(mt5.TRADE_ACTION_PENDING, symbol, volume, firstRessistance, thirdRessistance, mt5.ORDER_TYPE_BUY_STOP, price = secondRessistance)
    pendingOrderSellB = server.sendOperation(mt5.TRADE_ACTION_PENDING, symbol, volume, firstSupport, thirdSupport, mt5.ORDER_TYPE_SELL_STOP, price = secondSupport)

except Exception as e:
    print('Unexpected error {}'.format(e))
    traceback.print_exc()
finally:
    server.shutdown()
