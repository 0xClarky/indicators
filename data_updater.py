from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import sqlite3

# --- Configuration ---
DB_FILE = "crypto_data.db"
# --- CHANGE: Added 'NDX' ---
SYMBOLS = [
    "TOTAL", "TOTAL2", "TOTAL3", "OTHERS", 
    "BTCUSD", "ETHUSD", 
    "USDT.D", "USDC.D", "BTC.D",
    "NDX" # Nasdaq 100 Index
]
TABLE_NAME_MAP = {
    "USDT.D": "USDT_D",
    "USDC.D": "USDC_D",
    "BTC.D": "BTC_D"
}

# --- Main Functions ---
def fetch_data_for_symbol(tv, symbol, n_bars=5000):
    """Fetches historical data for a single symbol."""
    # --- CHANGE: Added logic for NDX ---
    if symbol in ["BTCUSD", "ETHUSD"]:
        exchange = "BITSTAMP"
    elif symbol == "NDX":
        exchange = "NASDAQ"
    else:
        exchange = "CRYPTOCAP"
        
    print(f"Fetching {n_bars} bars for {symbol} from {exchange}...")
    try:
        df = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=Interval.in_daily,
            n_bars=n_bars
        )
        if df is None or df.empty:
            print(f"No data returned for {symbol}.")
            return None
            
        df.index.name = 'datetime'
        return df[['open', 'high', 'low', 'close', 'volume']]
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def save_to_db(df, table_name):
    """Saves a DataFrame to a table in the SQLite DB, replacing existing data."""
    conn = sqlite3.connect(DB_FILE)
    try:
        df.to_sql(table_name, conn, if_exists='replace', index=True)
        print(f"Successfully saved {len(df)} records to table '{table_name}'.")
    finally:
        conn.close()

# --- Main Execution ---
if __name__ == "__main__":
    tv = TvDatafeed()
    
    for symbol in SYMBOLS:
        hist_df = fetch_data_for_symbol(tv, symbol)
        
        if hist_df is not None:
            table_name = TABLE_NAME_MAP.get(symbol, symbol)
            save_to_db(hist_df, table_name)
    
    print("\nData fetching complete.")
