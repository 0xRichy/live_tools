import sys
sys.path.append("./live_tools")
import ccxt
import ta
from utilities.perp_bitget import PerpBitget
import pandas as pd
import json

account_to_select = "bitget_exemple"
production = True

pair = "BTC/USDT:USDT"
leverage = 1

f = open(
    "./live_tools/secret.json",
)
secret = json.load(f)
f.close()

bitget = PerpBitget(
    apiKey=secret[account_to_select]["apiKey"],
    secret=secret[account_to_select]["secret"],
    password=secret[account_to_select]["password"],
)

candles = bitget.get_last_historical(pair, "1h", 100)
df = pd.DataFrame(candles)

# Calcul des moyennes mobiles
fast_length = 9
slow_length = 21
df['fast_ma'] = ta.trend.sma_indicator(close=df['close'], window=fast_length)
df['slow_ma'] = ta.trend.sma_indicator(close=df['close'], window=slow_length)

# Conditions d'entrée
df['long_condition'] = df['fast_ma'].gt(df['slow_ma'].shift(1)) & df['fast_ma'].lt(df['slow_ma'])
df['short_condition'] = df['fast_ma'].lt(df['slow_ma'].shift(1)) & df['fast_ma'].gt(df['slow_ma'])

balance = float(bitget.get_usdt_equity())
balance = balance * leverage
print(f"Balance: {round(balance, 2)} $", )

# Exécution des ordres
if df.iloc[-1]['long_condition']:
    # Entrer en position longue
    amount = balance / df.iloc[-1]['close']
    print(f"Place buy order of {amount} {pair} at price {round(df.iloc[-1]['close'], 2)} $")
    bitget.place_limit_order(
        symbol=pair,
        side="buy",
        amount=amount,
        price=df.iloc[-1]['close'],
        reduce=False,
    )

if df.iloc[-1]['short_condition']:
    # Entrer en position courte
    amount = balance / df.iloc[-1]['close']
    print(f"Place sell order of {amount} {pair} at price {round(df.iloc[-1]['close'], 2)} $")
    bitget.place_limit_order(
        symbol=pair,
        side="sell",
        amount=amount,
        price=df.iloc[-1]['close'],
        reduce=False,
    )
