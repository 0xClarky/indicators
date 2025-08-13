import pandas as pd
from tvDatafeed import TvDatafeed, Interval
import sqlite3
import time

# --- Configuration ---
DB_FILE = "ad_line_data.db" # A new, separate database for this indicator
# The basket of assets from your Pine Script
AD_LINE_SYMBOLS = [
    "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:XRPUSDT", "BINANCE:BNBUSDT",
    "BINANCE:SOLUSDT", "BINANCE:DOGEUSDT", "BINANCE:TRXUSDT", "BINANCE:ADAUSDT",
    "CRYPTO:HYPEHUSD", "BINANCE:SUIUSDT", "BINANCE:XLMUSDT", "BINANCE:LINKUSDT",
    "BINANCE:FILUSDT", "BINANCE:HBARUSDT", "BINANCE:AVAXUSDT", "BINANCE:TONUSDT",
    "BINANCE:LTCUSDT", "BINANCE:SHIBUSDT", "BINANCE:DOTUSDT", "BINANCE:UNIUSDT",
    "BINANCE:PEPEUSDT", "BINANCE:AAVEUSDT", "BINANCE:ENAUSDT", "BINANCE:TAOUSDT",
    "BINANCE:ATOMUSDT", "BINANCE:ETCUSDT", "BINANCE:NEARUSDT", "BINANCE:APTUSDT",
    "BINANCE:ONDOUSDT", "BINANCE:JUPUSDT", "BINANCE:ICPUSDT", "BYBIT:MNTUSDT",
    "BINANCE:QNTUSDT", "BINANCE:POLUSDT", "BINANCE:ALGOUSDT", "BINANCE:BONKUSDT",
    "BINANCE:ARBUSDT", "BINANCE:VETUSDT", "BINANCE:RENDERUSDT", "BINANCE:WLDUSDT",
    "BINANCE:CRVUSDT", "COINBASE:SEIUSD", "BITSTAMP:FLRUSD", "COINBASE:SKYUSD",
    "BINANCE:LDOUSDT", "COINBASE:GRTUSD", "BINANCE:SANDUSDT",
    "BINANCE:THETAUSDT", "BINANCE:IOTAUSDT", "BINANCE:RAYUSDT", "CRYPTO:GALAUSD",
    "BINANCE:PENDLEUSDT", "BINANCE:BTTCUSDT", "COINBASE:MORPHOUSD", "BINANCE:JTOUSDT",
    "BINANCE:SYRUPUSDT", "BYBIT:HNTUSDT", "COINBASE:PENGUUSD", "COINBASE:TRUMPUSD", 
    "BYBIT:SPXUSDT", "CRYPTO:FLOKIUSD", "CRYPTO:FARTCOINUSD", "BINANCE:WIFUSDT",
    "BINANCE:RSRUSDT", "OKX:CFGUSD", "BYBIT:PLUMEUSDT", "BYBIT:XDCUSDT", "BYBIT:ONDOUSDT",
    "COINBASE:EULUSD", "BINANCE:INJUSDT", "COINBASE:AEROUSD", "OKX:MORPHOUSDT", "COINBASE:BCHUSD",
    "OKX:CROUSDT", "BINANCE:FETUSDT", "BYBIT:IPUSDT", "BINANCE:FORMUSDT", "BINANCE:STXUSDT", "BINANCE:TIAUSDT",
    "BYBIT:PUMPUSDT", "BINANCE:IMXUSDT", "BINANCE:ENSUSDT", "BINANCE:CFXUSDT", "BINANCE:CAKEUSDT", "BINANCE:SUSDT",
    "BINANCE:VIRTUALUSDT", "BINANCE:AUSDT", "MEXC:MUSDT", "BINANCE:PYTHUSDT"
    "CRYPTO:BUSD", "BYBIT:BRETTUSDT", "BYBIT:MOGUSDT", "CRYPTO:REKTCUSD", "CRYPTO:SNEKUSD",
    "OKX:TURBOUSDT", "COINBASE:TOSHIUSD", "BYBIT:POPCATUSDT"]

def fetch_and_save_all():
    """
    Performs a one-time full historical data download for all A/D line assets.
    This will take a significant amount of time to run.
    """
    tv = TvDatafeed()
    conn = sqlite3.connect(DB_FILE)

    for symbol_exchange in AD_LINE_SYMBOLS:
        try:
            exchange, symbol = symbol_exchange.split(':')
            table_name = symbol # Use the symbol name as the table name
            print(f"--- Fetching {symbol} from {exchange} ---")

            df = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=Interval.in_daily,
                n_bars=5000
            )

            if df is not None and not df.empty:
                # We only need the 'close' column for the A/D line calculation
                df = df[['close']]
                df.index.name = 'datetime'
                df.to_sql(table_name, conn, if_exists='replace', index=True)
                print(f"Successfully saved {len(df)} records for {symbol}.")
            else:
                print(f"No data found for {symbol}.")

            # Wait for a moment to avoid overwhelming the API
            time.sleep(1) 

        except Exception as e:
            print(f"An error occurred with {symbol_exchange}: {e}")
            continue
    
    conn.close()
    print("\n--- A/D Line data fetching complete! ---")

if __name__ == "__main__":
    fetch_and_save_all()
