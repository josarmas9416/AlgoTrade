import pandas as pd
import MetaTrader5 as mt5

def close_all_positions(positions):
    # check if the position is already closed
    # for position in positions:
    for index, row in positions.iterrows():
        ticket = row["ticket"]

        # get information about the position
        position_info = mt5.positions_get(ticket=ticket)[0]
        request = {}
        # close the position using the PositionSell function
        if row["type"] == 0:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position_info.symbol,
                "volume": position_info.volume,
                "type": mt5.ORDER_TYPE_SELL,
                "magic": 2404231842,
                "position": ticket,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
        else:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position_info.symbol,
                "volume": position_info.volume,
                "type": mt5.ORDER_TYPE_BUY,
                "magic": 2404231842,
                "position": ticket,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
        result = mt5.order_send(request)

        if not result:
            print("order_send() failed, error code =",mt5.last_error())
            quit()

        # check the result of the order_send function
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to close position {ticket}, error code: {result.retcode}")
        else:
            print(f"Successfully closed position {ticket}")
                

account = 67079242
password = 'FV82*DG4yhBH'
server = 'RoboForex-ECN'
path = r"C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe"

# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish MetaTrader 5 connection to a specified trading account
if not mt5.initialize(path=path, login=account, server=server,password=password, timeout=10000):
    print("initialize() failed, error code =",mt5.last_error())
    quit()

# prepare the buy request structure
symbol = "EURUSD"
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(symbol, "not found, can not call order_check()")
    mt5.shutdown()
    quit()

# get open positions on symbol
positions=mt5.positions_get(symbol=symbol)
if not positions:
    print("No positions with symbol=\"{}\", error code={}".format(symbol, mt5.last_error()))
elif len(positions)>0:
    print("positions_get(symbol=\"{}\")={}".format(symbol, len(positions)))
    # display these positions as a table using pandas.DataFrame
    df=pd.DataFrame(list(positions),columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    print(df)
    close_all_positions(df)


# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
    