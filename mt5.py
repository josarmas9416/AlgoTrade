import pandas as pd
import MetaTrader5 as mt5

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
 
rates = mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_M1,0,60)
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
print(df)

# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
