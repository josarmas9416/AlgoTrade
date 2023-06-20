import broker.mt5 as server
import MetaTrader5 as mt5
import pandas as pd
import traceback

server.init()

try:
    # select the financial instrument to analyze
    symbol = "USDCHF"
    timeframe = mt5.TIMEFRAME_M30

    # get the last 30 days of historical data
    rates = server.getSymbolData(symbol, 10000, timeframe)

    # create a DataFrame with the historical data
    rates.set_index('time', inplace=True)
    rates.drop(['spread', 'real_volume'], axis=1, inplace=True)
    print(rates)
    # define the strike prices
    strike_prices = []
    
    # check if each close price is a strike price
    for close_price in rates['close']:
        if close_price % 100 in [0, 50, 20, 80]:
            print(f"{close_price} is a strike price")

except Exception as e:
    print('Unexpected error {}'.format(e))
    traceback.print_exc()
finally:
    server.shutdown()
