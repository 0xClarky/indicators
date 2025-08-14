import pandas as pd
import sqlite3
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime
import time
# --- THIS IS THE CHANGE ---
from config import ALL_SYMBOLS_TO_FETCH

# --- Configuration ---
DB_FILE = "market_data.db"
MAX_RETRIES = 5

def get_last_timestamp(conn, table_name):
    """Gets the most recent timestamp from a specific table."""
    try:
        query = f'SELECT MAX(datetime) FROM "{table_name}"'
        last_date_str = pd.read_sql(query, conn).iloc[0, 0]
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

def fetch_and_update():
    """Fetches only new data for all symbols and updates the unified DB."""
    tv = TvDatafeed()
    # Use the correct variable name here
    symbols_to_process = list(ALL_SYMBOLS_TO_FETCH.items())
    retry_count = 0

    with sqlite3.connect(DB_FILE) as conn:
        while symbols_to_process and retry_count <= MAX_RETRIES:
            failed_symbols = []

            if retry_count > 0:
                delay = 5 * retry_count
                print(f"\n--- RETRYING {len(symbols_to_process)} FAILED SYMBOLS (Attempt {retry_count}/{MAX_RETRIES}). Waiting for {delay} seconds... ---")
                time.sleep(delay)

            for symbol_exchange, table_name in symbols_to_process:
                try:
                    exchange, symbol = symbol_exchange.split(':')
                    print(f"\n--- Processing {table_name} ---")

                    last_timestamp = get_last_timestamp(conn, table_name)
                    if not last_timestamp:
                        print(f"No history found for {table_name}. Run the master_data_updater.py script first.")
                        continue

                    days_diff = (datetime.now() - last_timestamp).days
                    if days_diff <= 0:
                        print(f"{table_name} is already up to date.")
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
                        failed_symbols.append((symbol_exchange, table_name))
                        continue

                    hist_df = hist_df[['open', 'high', 'low', 'close', 'volume']]
                    hist_df.index.name = 'datetime'
                    new_data_df = hist_df[hist_df.index > last_timestamp]

                    append_data_to_db(conn, new_data_df, table_name)
                    time.sleep(1)

                except Exception as e:
                    print(f"An error occurred with {symbol_exchange}: {e}. Will retry.")
                    failed_symbols.append((symbol_exchange, table_name))
                    continue

            symbols_to_process = failed_symbols
            retry_count += 1

    if symbols_to_process:
        print("\n--- The following symbols failed to update after all retries: ---")
        for symbol, _ in symbols_to_process:
            print(f"- {symbol}")
    else:
        print("\n--- All symbols updated successfully. ---")

if __name__ == "__main__":
    fetch_and_update()
    print("\n--- Daily update process finished. ---")