import logging
import time
import traceback

import MetaTrader5 as mt5

from algotrade.exceptions import GeneralError

_logger = logging.getLogger(__name__)

class MeanReversionBot:
    def __init__(self, broker, symbols, timeframe, end, risk, comment):
        self.symbols = symbols
        self.timeframe = timeframe
        self.end = end
        self.risk = risk
        self.comment = comment

        if broker == "mt5":
            from brokers import mt5 as server
            self.broker = server.Mt5()
        else:
            raise GeneralError("Not implemented")

    def run(self):
        try:
            self.broker.init()

            # Store the initial trading day
            prev_day = None

            while True:
                # Get the symbol data
                for symbol in self.symbols:
                    rates = self.broker.get_symbol_data(symbol)

                    if not rates.empty:
                        # Get the datetime of the latest bar
                        current_time = rates['time'].iloc[-1].to_pydatetime()

                        # Get the current day from date
                        current_day = current_time.date()

                        if not prev_day:
                            # If there is not a prev_day stablished, assign the current day
                            prev_day = current_day
                            _logger.info('Bot started')

                        else:
                            # Else, check if a new trading day has started
                            if current_day > prev_day:
                                _logger.info('New Trading Day')

                                # Assign the new current day
                                prev_day = current_day

                                for symbol in self.symbols:
                                    # Extract symbol data
                                    symbol_data = self.broker.get_symbol_data(symbol, self.timeframe, 1, self.end)

                                    # Get the lowest, highest, and close price
                                    lowest_price = symbol_data['low'].min()
                                    highest_price = symbol_data['high'].max()
                                    close_price = symbol_data['close'].iloc[-1]

                                    # Get the low and high round numbers and pivot
                                    low_round = self.broker.get_round_number(symbol, lowest_price, "previous")
                                    high_round = self.broker.get_round_number(symbol, highest_price, "next")

                                    pivot_point = (highest_price + lowest_price + close_price) / 3

                                    # Get pip value
                                    pip = self.broker.get_pip_value(symbol)

                                    # Get data for buy limit
                                    buy_price = low_round + pip
                                    buy_tp = pivot_point
                                    buy_distance = buy_tp - buy_price
                                    buy_sl = buy_price - buy_distance / 2
                                    buy_sl_distance_in_pips = (buy_price - buy_sl) / pip

                                    # Get pip USD value
                                    pip_value = self.broker.get_pip_value_usd(symbol)

                                    # Get Lot Size
                                    buy_volume = self.broker.get_lot_size(symbol, self.risk, buy_sl_distance_in_pips)

                                    # Get data for sell limit
                                    sell_price = high_round
                                    sell_tp = pivot_point + pip
                                    sell_distance = sell_price - sell_tp
                                    sell_sl = sell_price + sell_distance / 2
                                    sell_sl_distance_in_pips = (sell_sl - sell_price) / pip

                                    # Get Lot Size
                                    sell_volume = self.broker.get_lot_size(symbol, self.risk, sell_sl_distance_in_pips)

                                    # Buy limit
                                    self.broker.send_operation(mt5.TRADE_ACTION_PENDING, symbol, buy_volume, buy_sl, buy_tp,
                                                            mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_FILLING_FOK,
                                                            mt5.ORDER_TIME_DAY, price=buy_price, comment=self.comment)

                                    # Sell limit
                                    self.broker.send_operation(mt5.TRADE_ACTION_PENDING, symbol, sell_volume, sell_sl,
                                                            sell_tp, mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_FILLING_FOK,
                                                            mt5.ORDER_TIME_DAY, price=sell_price, comment=self.comment)

                            else:
                                # Get all open positions
                                all_open_positions = self.broker.get_open_positions()

                                if not all_open_positions.empty:
                                    # Filter rows with comment 'comment'
                                    open_positions = all_open_positions[all_open_positions['comment'] == self.comment]

                                    for row in open_positions.iterrows():
                                        # Validate if sl is equal to price open
                                        # Else execute code
                                        if row[1]['sl'] == row[1]['price_open']:
                                            continue

                                        # Get break even price
                                        be_price = (row[1]['price_open'] + row[1]['tp']) / 2

                                        # If the position is sell then validate if the current
                                        # price is lower than or equal to the break even price
                                        # to execute the modification
                                        # If the position is buy then validate if the current
                                        # price is higher than or equal to the break even price
                                        # to execute the modification
                                        if row[1]['type'] == 1:
                                            if row[1]['price_current'] <= be_price:
                                                self.broker.send_operation(mt5.TRADE_ACTION_SLTP,
                                                                        position=row[1]['ticket'],
                                                                        stop_loss=row[1]['price_open'])
                                        else:
                                            if row[1]['price_current'] >= be_price:
                                                self.broker.send_operation(mt5.TRADE_ACTION_SLTP,
                                                                        position=row[1]['ticket'],
                                                                        stop_loss=row[1]['price_open'])

                # Wait for 1 second before the next iteration
                time.sleep(1)

        except Exception as e:
            _logger.error('Unexpected error {}'.format(e))
            traceback.print_exc()
        finally:
            self.broker.shutdown()
