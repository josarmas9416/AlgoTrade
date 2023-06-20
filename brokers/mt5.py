import datetime
import logging
import math

import MetaTrader5 as mt5
import pandas as pd

from algotrade.config import Config
from algotrade.exceptions import GeneralError, OrderError

_logger = logging.getLogger(__name__)

class Mt5:
    def __init__(self):
        # Create an instance of AlgoTraderConfig
        config = Config()

        self.account = config.get_account()
        self.password = config.get_password()
        self.server = config.get_server()
        self.path = config.get_path()

    def init(self):
        # Display data on the MetaTrader 5 package
        _logger.info("MetaTrader5 package author: %s", mt5.__author__)
        _logger.info("MetaTrader5 package version: %s", mt5.__version__)

        # Establish MetaTrader 5 connection to a specified trading account
        if not mt5.initialize(path=self.path, login=self.account, server=self.server, password=self.password):
            _logger.error("Initialize() failed, error code = %s", mt5.last_error())
            quit()

    def shutdown(self):
        # Shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()

    def get_symbol_info(self, symbol):
        symbol_info = mt5.symbol_info(symbol)

        if not symbol_info:
            _logger.error(symbol, "Not found, can not call order_check()")
            return False

        return symbol_info

    def get_symbol_info_tick(self, symbol):
        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            _logger.error(symbol, "Tick not found, error code =", mt5.last_error())
            return False

        return tick

    def get_symbol_data(self, symbol, timeframe=mt5.TIMEFRAME_M1, start=0, end=1):
        if not self.get_symbol_info(symbol):
            return False

        rates = mt5.copy_rates_from_pos(symbol, timeframe, start, end)
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")

        return df

    def get_symbol_exchange_rate(self, symbol):
        # Get the symbol info
        symbol_info = self.get_symbol_info(symbol)

        # Get the exchange rate
        exchange_rate = symbol_info.bid

        return exchange_rate

    def send_operation(self, action, symbol=None, volume=None, stop_loss=None, take_profit=None, order_type=None,
                       order_type_filling=None, order_type_time=None, magic=None, order=None, price=None,
                       stop_limit=None, deviation=None, expiration=None, comment=None, position=None,
                       position_by=None):
        if not magic:
            now = datetime.datetime.now()
            magic_str = now.strftime("%d%m%y%H%M%S")
            magic = int(magic_str)

        if not comment:
            comment = f"JA open {magic_str}"

        request = {
            "action": action,
        }

        if symbol:
            request["symbol"] = symbol

        if volume:
            request["volume"] = volume

        if stop_loss:
            request["sl"] = stop_loss

        if take_profit:
            request["tp"] = take_profit

        if order_type:
            request["type"] = order_type

        if order_type_filling:
            request["type_filling"] = order_type_filling

        if order_type_time:
            request["type_time"] = order_type_time

        if magic:
            request["magic"] = magic

        if order:
            request["order"] = order

        if price:
            request["price"] = price

        if stop_limit:
            request["stoplimit"] = stop_limit

        if deviation:
            request["deviation"] = deviation

        if expiration:
            request["expiration"] = expiration

        if comment:
            request["comment"] = comment

        if position:
            request["position"] = position

        if position_by:
            request["position_by"] = position_by

        # send a trading request
        result = mt5.order_send(request)

        # check result
        if not result:
            raise OrderError(f"Order_send() failed, error code = {mt5.last_error()}")

        _logger.warn(f"1. Order_send(): ", request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            error_message = f"2. Order_send failed, retcode={result.retcode}"
            result_dict = result._asdict()
            for field in result_dict.keys():
                error_message += f"\n   {field}={result_dict[field]}"
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_field in traderequest_dict:
                        error_message += f"\n       traderequest: {tradereq_field}={traderequest_dict[tradereq_field]}"

            raise OrderError(error_message)


    def get_open_positions(self, symbol=None, group=None, ticket=None):
        if symbol:
            positions = mt5.positions_get(symbol=symbol)
        elif group:
            positions = mt5.positions_get(group=group)
        elif ticket:
            positions = mt5.positions_get(ticket=ticket)
        else:
            positions = mt5.positions_get()

        if positions:
            positions_df = pd.DataFrame(
                list(positions), columns=positions[0]._asdict().keys()
            )
            positions_df["time"] = pd.to_datetime(positions_df["time"], unit="s")

            return positions_df

        return pd.DataFrame()

    def close_all_positions(self):
        operations = self.get_open_positions()
        if operations:
            raise GeneralError('TODO')

    def get_lot_size(self, symbol, risk, stop_loss):
        # Calculate the maximum amount that can be risked based on the balance and risk percentage
        balance = self.get_balance()
        pip_usd_value = self.get_pip_value_usd(symbol)
        max_risk_amount = balance * (risk / 100)

        # Calculate the lot size based on the stop loss and pip USD value
        lot_size = max_risk_amount / (stop_loss * pip_usd_value)

        # Return the lot size with 2 decimal places
        return round(lot_size, 2)

    def get_round_number(self, symbol, number, direction):
        pip_value = self.get_pip_value(symbol)

        pip_value_str = str(pip_value)
        pip_decimal = len(pip_value_str.split('.')[1])

        desired_positions = ['00', '20', '50', '80']

        while True:
            number_str = str(number)
            decimal = number_str.split('.')[1][:pip_decimal]

            if decimal[-2:] in desired_positions:
                rounded_number = math.floor(number * (10 ** pip_decimal)) / (10 ** pip_decimal)
                return rounded_number

            if direction == "next":
                number += pip_value
            else:
                number -= pip_value

    def get_balance(self):
        # Get account summary
        account_info = mt5.account_info()
        if account_info is None:
            _logger.error("Failed to retrieve account information. Error code:", mt5.last_error())
            return False
        else:
            balance = account_info.balance
            _logger.info("Account balance:", balance)
            return balance

    def get_pip_value(self, symbol):
        # Get symbol information
        symbol_info = self.get_symbol_info(symbol)

        # Calculate the Pip value
        return symbol_info.point * 10

    def get_pip_value_usd(self, symbol):
        # Get pipSize
        pip_value = self.get_pip_value(symbol)
        exchange_rate = self.get_symbol_exchange_rate(symbol)

        if symbol[:3] == "USD":
            pip_value = pip_value / exchange_rate * 100000
        else:
            pip_value = pip_value * 100000

        return pip_value
