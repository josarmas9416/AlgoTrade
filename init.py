from strategies.mean_reversal import MeanReversionBot
import MetaTrader5 as mt5

# Define the parameters for MeanReversionBot
broker = "mt5"
symbols = ['EURUSD']
timeframe = mt5.TIMEFRAME_H1
end = 24
risk = 0.5
comment = "Test 1"

# Create an instance of the MeanReversionBot class
mean_reversion_bot = MeanReversionBot(broker, symbols, timeframe, end, risk, comment)

# Run the mean reversion bot
mean_reversion_bot.run()