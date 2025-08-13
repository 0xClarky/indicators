import pandas as pd
import sqlite3
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime

# --- Configuration ---
DB_FILE = "crypto_data.db"
SYMBOLS = [
    "TOTAL", "TOTAL2", "TOTAL3", "OTHERS", 
    "BTCUSD", "ETHUSD", 
    "USDT.D", "USDC.D", "BTC.D",
    "NDX"
]
TABLE_NAME_MAP = {
    "USDT.D": "USDT_D",
    "USDC.D": "USDC_D",
    "BTC.D": "BTC_D"
}

# --- Database Functions ---

def get_last_timestamp(table_name):
    """Gets the most recent timestamp from a specific table."""
    conn = sqlite3.connect(DB_FILE)
    try:
        last_date_str = pd.read_sql(f"SELECT MAX(datetime) FROM {table_name}", conn).iloc[0, 0]
        return pd.to_datetime(last_date_str) if last_date_str else None
    except Exception:
        return None
    finally:
        conn.close()

def append_data_to_db(df, table_name):
    """Appends new data to a specific table."""
    if df.empty:
        print(f"No new data to append for {table_name}.")
        return
    conn = sqlite3.connect(DB_FILE)
    try:
        df.to_sql(table_name, conn, if_exists='append', index=True)
        print(f"Successfully appended {len(df)} new records to table '{table_name}'.")
    finally:
        conn.close()

# --- Main Update Logic ---
def fetch_and_update():
    """Fetches only new data for all symbols and updates the DB."""
    tv = TvDatafeed()
    
    for symbol in SYMBOLS:
        table_name = TABLE_NAME_MAP.get(symbol, symbol)
        print(f"\n--- Updating {table_name} ---")
        
        last_timestamp = get_last_timestamp(table_name)
        
        if not last_timestamp:
            print(f"No history found for {table_name}. Run the main data_updater.py script first.")
            continue
            
        days_diff = (datetime.now() - last_timestamp).days
        
        if days_diff <= 0:
            print("Data is already up to date.")
            continue
            
        n_bars_to_fetch = days_diff + 5
        
        # --- CHANGE: Added logic for NDX ---
        if symbol in ["BTCUSD", "ETHUSD"]:
            exchange = "BITSTAMP"
        elif symbol == "NDX":
            exchange = "NASDAQ"
        else:
            exchange = "CRYPTOCAP"

        print(f"Last record is from {last_timestamp}. Fetching {n_bars_to_fetch} bars...")
        
        try:
            hist_df = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=Interval.in_daily,
                n_bars=n_bars_to_fetch
            )
            
            if hist_df is None or hist_df.empty:
                print(f"No new data returned for {symbol}.")
                continue

            hist_df.index.name = 'datetime'
            hist_df = hist_df[['open', 'high', 'low', 'close', 'volume']]
            
            new_data_df = hist_df[hist_df.index > last_timestamp]
            
            append_data_to_db(new_data_df, table_name)

        except Exception as e:
            print(f"An error occurred fetching data for {symbol}: {e}")

if __name__ == "__main__":
    # Helper functions need to be defined here or imported
    def get_last_timestamp(table_name):
        conn = sqlite3.connect(DB_FILE)
        try:
            last_date_str = pd.read_sql(f"SELECT MAX(datetime) FROM {table_name}", conn).iloc[0, 0]
            return pd.to_datetime(last_date_str) if last_date_str else None
        except Exception:
            return None
        finally:
            conn.close()

    def append_data_to_db(df, table_name):
        if df.empty:
            print(f"No new data to append for {table_name}.")
            return
        conn = sqlite3.connect(DB_FILE)
        try:
            df.to_sql(table_name, conn, if_exists='append', index=True)
            print(f"Successfully appended {len(df)} new records to table '{table_name}'.")
        finally:
            conn.close()
            
    fetch_and_update()
    print("\nDaily update process finished.")