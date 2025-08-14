import sqlite3
import time
from tvDatafeed import TvDatafeed, Interval
import pandas as pd
# --- THIS IS THE CHANGE ---
from config import ALL_SYMBOLS_TO_FETCH

# --- Configuration ---
DB_FILE = "market_data.db"
N_BARS = 5000
MAX_RETRIES = 10

def fetch_and_save_all():
    """
    Performs a one-time full historical data download for all assets
    and saves them to a single SQLite database, with a retry mechanism.
    """
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
                    print(f"--- Fetching {symbol} from {exchange} for table {table_name} ---")

                    df = tv.get_hist(
                        symbol=symbol,
                        exchange=exchange,
                        interval=Interval.in_daily,
                        n_bars=N_BARS
                    )

                    if df is not None and not df.empty:
                        df = df[['open', 'high', 'low', 'close', 'volume']]
                        df.index.name = 'datetime'
                        df.to_sql(table_name, conn, if_exists='replace', index=True)
                        print(f"Successfully saved {len(df)} records for {table_name}.")
                    else:
                        print(f"No data returned for {symbol_exchange}. Will retry.")
                        failed_symbols.append((symbol_exchange, table_name))
                        continue

                    time.sleep(1)

                except Exception as e:
                    print(f"An error occurred with {symbol_exchange}: {e}. Will retry.")
                    failed_symbols.append((symbol_exchange, table_name))
                    continue

            symbols_to_process = failed_symbols
            retry_count += 1

    if symbols_to_process:
        print("\n--- The following symbols failed to download after all retries: ---")
        for symbol, _ in symbols_to_process:
            print(f"- {symbol}")
    else:
        print("\n--- Unified data fetching complete! ---")

if __name__ == "__main__":
    fetch_and_save_all()