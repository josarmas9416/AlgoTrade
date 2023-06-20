import broker.mt5 as server
import MetaTrader5 as mt5
import numpy as np
import statsmodels.api as sm
import traceback

server.init()

try:
    # select the financial instrument to analyze
    symbol = "EURUSD"
    lastData = 100
    timeframe = mt5.TIMEFRAME_M5

    # request historical prices
    prices_df = server.getSymbolData(symbol, lastData, timeframe)

    # extract close prices
    prices = np.array(prices_df['close'])

    # calculate linear regression
    x = np.arange(len(prices))
    x = sm.add_constant(x)
    model = sm.OLS(prices, x).fit()
    slope = model.params[1]
    p_value = model.pvalues[1]

    # output results
    print("Linear regression slope:", slope)
    print("Linear regression p-value:", p_value)

    # operations


except Exception as e:
    print('Unexpected error {}'.format(e))
    traceback.print_exc()
finally:
    server.shutdown()
