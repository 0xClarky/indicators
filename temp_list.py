import sqlite3
import pandas as pd

DB_FILE = "market_data.db"

def list_all_tables():
    """
    Connects to the database and prints a sorted list of all table names.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()
            
            if not tables:
                print("No tables found in the database.")
                return

            print("--- Existing Tables in market_data.db ---")
            for table_name in sorted(tables):
                print(table_name)
            print(f"\nTotal tables found: {len(tables)}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_all_tables()