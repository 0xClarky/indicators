import sqlite3
import time
from tvDatafeed import TvDatafeed, Interval

# --- Configuration ---
DB_FILE = "market_data.db"
N_BARS = 5000  # Fetch max history

# --- Assets to Add ---
# A small dictionary containing only the assets you need to add.
ASSETS_TO_ADD = {
    "BINANCE:SUSHIUSDT": "SUSHIUSDT",
    "BINANCE:KMNOUSDT": "KMNOUSDT"
}

def add_missing_assets():
    """
    Fetches and saves only the specified assets to the database.
    This will create the table if it's missing or replace it if it exists.
    """
    tv = TvDatafeed()
    print(f"Connecting to database: {DB_FILE}")
    
    with sqlite3.connect(DB_FILE) as conn:
        for symbol_exchange, table_name in ASSETS_TO_ADD.items():
            try:
                exchange, symbol = symbol_exchange.split(':')
                print(f"--- Fetching full history for {symbol} from {exchange} ---")

                df = tv.get_hist(
                    symbol=symbol,
                    exchange=exchange,
                    interval=Interval.in_daily,
                    n_bars=N_BARS
                )

                if df is not None and not df.empty:
                    df = df[['open', 'high', 'low', 'close', 'volume']]
                    df.index.name = 'datetime'
                    # Use if_exists='replace' to ensure a clean table is created.
                    df.to_sql(table_name, conn, if_exists='replace', index=True)
                    print(f"✅ Successfully created/updated table for {table_name} with {len(df)} records.")
                else:
                    print(f"⚠️ No data found for {symbol_exchange}.")

                time.sleep(1) # Pause between requests

            except Exception as e:
                print(f"❌ An error occurred with {symbol_exchange}: {e}")
                continue

    print("\n--- Temporary asset update process finished. ---")

if __name__ == "__main__":
    add_missing_assets()
