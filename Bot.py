import time
import ccxt
from datetime import datetime

# === CONFIG ===
API_KEY = "YOUR_BINANCE_API_KEY"
API_SECRET = "YOUR_BINANCE_SECRET"
STAKE_PER_TRADE = 20  # USDT as you wrote
LEVERAGE = 20
MAX_FUTURES_BALANCE = 80 # above this, move to spot
REST_MINUTES = 15

# Your 2 signal sources - you will paste them here
# Example: [{"coin":"BTCUSDT","signal":"short","time": "1h ago","dca":["entry1","entry2"],"tp2":...}]

def get_signals():
    # TODO: Connect your Cryptofocus and second signal here
    # Return only coins where signal time < 2hrs and <3hrs
    # Example return:
    # [{"symbol":"BTCUSDT","side":"short","dca_percents":[30,30,40],"tp2": 58000,"sl": 59000}]
    return []

exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'options': {'defaultType': 'future'}
})

def ensure_leverage(symbol):
    exchange.set_leverage(LEVERAGE, symbol)
    exchange.set_margin_mode('ISOLATED', symbol)

def trade_coin(signal):
    symbol = signal['symbol']
    ensure_leverage(symbol)
    print(f"[{datetime.now()}] Trading {symbol} Short with {STAKE_PER_TRADE} USDT x{LEVERAGE}")
    
    # 1. Enter short with first DCA %
    amount_usdt = STAKE_PER_TRADE * signal['dca_percents'][0]/100
    # ... create market short order
    
    # 2. Place other DCA limit orders
    # 3. Place TP2 and SL from DCA
    
    # If coin reverses and goes long, close short and open long (as you wrote)
    # if long_signal_detected: close and flip

def check_balance_transfer():
    bal = exchange.fetch_balance()
    futures_usdt = bal['USDT']['free']
    if futures_usdt > MAX_FUTURES_BALANCE:
        excess = futures_usdt - MAX_FUTURES_BALANCE
        print(f"Transferring {excess} USDT Futures -> Spot")
        exchange.transfer('USDT', excess, 'future', 'spot')

def main():
    while True:
        try:
            signals = get_signals()
            # Trade only 2 coins per day
            for sig in signals[:2]:
                trade_coin(sig)
            
            check_balance_transfer()
            
            print(f"Resting {REST_MINUTES} mins...")
            time.sleep(REST_MINUTES * 60)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
