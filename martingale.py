import mt5 as server
import MetaTrader5 as mt5
import time

server.init()
try:
    i = 0
    while i < 20:
        symbol = 'BTCUSD'
        lastData = 300
        variation = 10
        volume = 0.01
        symbolData = server.getSymbolData(symbol, lastData)
        symbolData['ma50'] = symbolData['close'].rolling(50).mean()
        referenceLine = symbolData['ma50'].iloc[-1]
        lastPrice = symbolData['close'].iloc[- 1]

        operationsDf = server.getOpenPositions()
        operationsLenght = 0
        if not operationsDf.empty:
            operationsLenght = len(operationsDf)
        if operationsLenght == 0:
            if lastPrice > referenceLine + variation:
                server.sendOperation(symbol, volume, mt5.ORDER_TYPE_SELL, mt5.symbol_info_tick(symbol).bid + variation, referenceLine)
            elif lastPrice < referenceLine - variation:
                server.sendOperation(symbol, volume, mt5.ORDER_TYPE_BUY, mt5.symbol_info_tick(symbol).ask - variation, referenceLine)
            else:
                print('No conditions were met, last price: {}, reference line: {}, variation: {}'.format(lastPrice, referenceLine, variation))

        else:
            profit = operationsDf['profit'].iloc[-1]
            if operationsDf['profit'].iloc[-1] < 0:
                lastOpType = operationsDf['type'].iloc[-1]
                newVolume = operationsDf['volume'].iloc[-1] * 2
                # 0 is purchase, 1 is sell
                if lastOpType == 1:
                    server.sendOperation(symbol, newVolume, mt5.ORDER_TYPE_SELL, mt5.symbol_info_tick(symbol).bid + variation, referenceLine)
                else:
                    server.sendOperation(symbol, newVolume, mt5.ORDER_TYPE_BUY, mt5.symbol_info_tick(symbol).ask - variation, referenceLine)
            else:
                print('No conditions were met, Profit: {}'.format(profit))
        time.sleep(30)
        i += 1

except Exception as e:
    print('Unexpected error {}'.format(e))

finally:
    server.shutdown()