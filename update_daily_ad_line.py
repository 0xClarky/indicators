import pandas as pd
import sqlite3
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime
import time

# --- Configuration ---
DB_FILE = "ad_line_data.db"
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
MAX_RETRIES = 5

# --- Database Functions ---
def get_last_timestamp(conn, table_name):
    """Gets the most recent timestamp from a specific table."""
    try:
        last_date_str = pd.read_sql(f'SELECT MAX(datetime) FROM "{table_name}"', conn).iloc[0, 0]
        return pd.to_datetime(last_date_str) if last_date_str else None
    except Exception:
        return None

def append_data_to_db(conn, df, table_name):
    """Appends new data to a specific table."""
    if df.empty:
        print(f"No new data to append for {table_name}.")
        return
    df.to_sql(table_name, conn, if_exists='append', index=True)
    print(f"Successfully appended {len(df)} new records to table '{table_name}'.")

# --- Main Update Logic ---
def fetch_and_update():
    """Fetches new data for all assets, with a retry mechanism for failures."""
    tv = TvDatafeed()
    conn = sqlite3.connect(DB_FILE)
    
    symbols_to_process = AD_LINE_SYMBOLS.copy()
    retry_count = 0

    while symbols_to_process and retry_count <= MAX_RETRIES:
        failed_symbols = []

        if retry_count > 0:
            delay = 5 * retry_count # Increasing delay
            print(f"\n--- RETRYING {len(symbols_to_process)} FAILED SYMBOLS (Attempt {retry_count}/{MAX_RETRIES}). Waiting for {delay} seconds... ---")
            time.sleep(delay)

        for symbol_exchange in symbols_to_process:
            try:
                exchange, symbol = symbol_exchange.split(':')
                table_name = symbol
                print(f"\n--- Processing {table_name} ---")
                
                last_timestamp = get_last_timestamp(conn, table_name)
                
                if not last_timestamp:
                    print(f"No history found for {table_name}. Run the initial fetch script first.")
                    continue
                    
                days_diff = (datetime.now() - last_timestamp).days
                
                if days_diff <= 0:
                    print("Data is already up to date.")
                    continue
                    
                n_bars_to_fetch = days_diff + 5
                
                print(f"Last record is from {last_timestamp}. Fetching {n_bars_to_fetch} bars...")
                
                hist_df = tv.get_hist(
                    symbol=symbol,
                    exchange=exchange,
                    interval=Interval.in_daily,
                    n_bars=n_bars_to_fetch
                )
                
                if hist_df is None or hist_df.empty:
                    print(f"No new data returned for {symbol}. Will retry.")
                    failed_symbols.append(symbol_exchange)
                    continue

                hist_df = hist_df[['close']]
                hist_df.index.name = 'datetime'
                
                new_data_df = hist_df[hist_df.index > last_timestamp]
                
                append_data_to_db(conn, new_data_df, table_name)
                
                time.sleep(1)

            except Exception as e:
                print(f"An error occurred with {symbol_exchange}: {e}. Will retry.")
                failed_symbols.append(symbol_exchange)
                continue
        
        symbols_to_process = failed_symbols
        retry_count += 1
            
    conn.close()

    if symbols_to_process:
        print("\n--- The following symbols failed to update after all retries: ---")
        for symbol in symbols_to_process:
            print(f"- {symbol}")
    else:
        print("\n--- All symbols updated successfully. ---")


if __name__ == "__main__":
    fetch_and_update()
    print("\n--- A/D Line daily update process finished. ---")
