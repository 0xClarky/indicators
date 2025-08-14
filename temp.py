import sqlite3
import time
from tvDatafeed import TvDatafeed, Interval

# --- Configuration ---
DB_FILE = "market_data.db"
N_BARS = 5000  # Fetch max history

# --- Assets to Add ---
# This dictionary contains only the new assets that are missing from your database.
ASSETS_TO_ADD = {
    'BINANCE:CGPTUSDT': 'CGPTUSDT',
    'BINANCE:DODOUSDT': 'DODOUSDT',
    'BINANCE:DOGSUSDT': 'DOGSUSDT',
    'BINANCE:HYPERUSDT': 'HYPERUSDT',
    'BINANCE:INITUSDT': 'INITUSDT',
    'BINANCE:JOEUSDT': 'JOEUSDT',
    'BINANCE:KNCUSDT': 'KNCUSDT',
    'BINANCE:LAUSDT': 'LAUSDT',
    'BINANCE:MOVRUSDT': 'MOVRUSDT',
    'BINANCE:MTLUSDT': 'MTLUSDT',
    'BINANCE:NEWTUSDT': 'NEWTUSDT',
    'BINANCE:NMRUSDT': 'NMRUSDT',
    'BINANCE:NTRNUSDT': 'NTRNUSDT',
    'BINANCE:OGNUSDT': 'OGNUSDT',
    'BINANCE:OGUSDT': 'OGUSDT',
    'BINANCE:ONGUSDT': 'ONGUSDT',
    'BINANCE:PONDUSDT': 'PONDUSDT',
    'BINANCE:RADUSDT': 'RADUSDT',
    'BINANCE:SANTOSUSDT': 'SANTOSUSDT',
    'BINANCE:SLPUSDT': 'SLPUSDT',
    'BINANCE:SOPHUSDT': 'SOPHUSDT',
    'BINANCE:STEEMUSDT': 'STEEMUSDT',
    'BINANCE:TKOUSDT': 'TKOUSDT',
    'BINANCE:TOWNSUSDT': 'TOWNSUSDT',
    'BINANCE:TREEUSDT': 'TREEUSDT',
    'BINANCE:TUTUSDT': 'TUTUSDT',
    'BINANCE:VELODROMEUSDT': 'VELODROMEUSDT',
    'BINANCE:1000CATUSDT': '1000CATUSDT',
    'BINANCE:ALPINEUSDT': 'ALPINEUSDT',
    'BINANCE:ARPAUSDT': 'ARPAUSDT',
    'BINANCE:AUCTIONUSDT': 'AUCTIONUSDT',
    'BINANCE:CELRUSDT': 'CELRUSDT',
    'BINANCE:CTSIUSDT': 'CTSIUSDT'
}


def add_missing_assets():
    """
    Fetches and saves only the specified new assets to the database.
    """
    tv = TvDatafeed()
    print(f"Connecting to database: {DB_FILE}")
    
    with sqlite3.connect(DB_FILE) as conn:
        for symbol_exchange, table_name in ASSETS_TO_ADD.items():
            try:
                # Check if table already exists to avoid re-downloading
                cursor = conn.cursor()
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                if cursor.fetchone():
                    print(f"✅ Table for {table_name} already exists. Skipping.")
                    continue

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
                    df.to_sql(table_name, conn, if_exists='replace', index=True)
                    print(f"✅ Successfully created table for {table_name} with {len(df)} records.")
                else:
                    print(f"⚠️ No data found for {symbol_exchange}.")

                time.sleep(1)

            except Exception as e:
                print(f"❌ An error occurred with {symbol_exchange}: {e}")
                continue

    print("\n--- Temporary asset update process finished. ---")

if __name__ == "__main__":
    add_missing_assets()
