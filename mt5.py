import MetaTrader5 as mt5
import pandas as pd
import datetime


def init():
    # set data
    account = 67079242
    password = "FV82*DG4yhBH"
    server = "RoboForex-ECN"
    path = r"C:\Program Files\RoboForex - MetaTrader 5\terminal64.exe"

    # display data on the MetaTrader 5 package
    print("MetaTrader5 package author: ", mt5.__author__)
    print("MetaTrader5 package version: ", mt5.__version__)

    # establish MetaTrader 5 connection to a specified trading account
    if not mt5.initialize(
        path=path, login=account, server=server, password=password, timeout=10000
    ):
        print("initialize() failed, error code =", mt5.last_error())
        quit()


def shutdown():
    # shut down connection to the MetaTrader 5 terminal
    mt5.shutdown()


def getSymbolInfo(symbol):
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(symbol, "not found, can not call order_check()")
        return False

    return symbol_info


def getSymbolData(symbol, end, timeframe=mt5.TIMEFRAME_M1, start=0):
    if not getSymbolInfo(symbol):
        return False

    rates = mt5.copy_rates_from_pos(symbol, timeframe, start, end)
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")

    return df


def sendOperation(
    action,
    symbol,
    volume,
    stopLoss,
    takeProfit,
    orderType,
    magic=None,
    order=None,
    price=None,
    stoplimit=None,
    deviation=None,
    expiration=None,
    comment=None,
    position=None,
    position_by=None,
):
    if not magic:
        now = datetime.datetime.now()
        magicStr = now.strftime("%d%m%y%H%M%S")
        magic = int(magicStr)

    if not comment:
        comment = "JA open " + magicStr

    request = {
        "action": action,
        "magic": magic,
        "symbol": symbol,
        "volume": volume,
        "sl": stopLoss,
        "tp": takeProfit,
        "type": orderType,
        "type_filling": mt5.ORDER_FILLING_FOK,
        "type_time": mt5.ORDER_TIME_GTC,
        "comment": comment,
    }

    if order:
        request.update({"order": order})

    if price:
        request.update({"price": price})

    if stoplimit:
        request.update({"stoplimit": stoplimit})

    if deviation:
        request.update({"deviation": deviation})

    if expiration:
        request.update({"expiration": expiration})

    if position:
        request.update({"position": position})

    if position_by:
        request.update({"position_by": position_by})

    # send a trading request
    result = mt5.order_send(request)

    # check result
    if not result:
        print("order_send() failed, error code =", mt5.last_error())
        return False

    # check the execution result
    print("1. order_send(): by {} {} lots ".format(symbol, volume))
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("2. order_send failed, retcode={}".format(result.retcode))
        # request the result as a dictionary and display it element by element
        result_dict = result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field, result_dict[field]))
            # if this is a trading request structure, display it element by element as well
            if field == "request":
                traderequest_dict = result_dict[field]._asdict()
                for tradereq_filed in traderequest_dict:
                    print(
                        "       traderequest: {}={}".format(
                            tradereq_filed, traderequest_dict[tradereq_filed]
                        )
                    )
        print("Goodbye!")


def getOpenPositions():
    positions = mt5.positions_get()
    if positions:
        positionsDf = pd.DataFrame(
            list(positions), columns=positions[0]._asdict().keys()
        )
        positionsDf["time"] = pd.to_datetime(positionsDf["time"], unit="s")

        return positionsDf

    return pd.DataFrame()

def closeAllPositions():
    operations = getOpenPositions()
    if operations:
        print('TODO')