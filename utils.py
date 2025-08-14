import streamlit as st
import pandas as pd
import sqlite3
from config import DB_FILE

@st.cache_data(ttl=3600)
def load_data(asset_list=None):
    """
    Loads tables from the SQLite DB. If asset_list is provided, attempts to
    load only those tables. Skips any tables that are not found.

    Args:
        asset_list (list, optional): A list of table names to load. Defaults to None.

    Returns:
        dict: A dictionary of DataFrames for the tables that were successfully found and loaded.
    """
    try:
        with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
            # First, get a list of all tables that actually exist in the database
            existing_tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()

            if not asset_list:
                # If no specific list is provided, load all existing tables
                tables_to_load = existing_tables
            else:
                # If a list is provided, load only the assets that are in both the requested list AND the database
                tables_to_load = [asset for asset in asset_list if asset in existing_tables]
                
                # --- NEW: Warn the user if some requested assets are missing ---
                missing_assets = [asset for asset in asset_list if asset not in existing_tables]
                if missing_assets:
                    st.warning(f"Could not find data for the following assets: {', '.join(missing_assets)}. They may have failed to download.")


            if not tables_to_load:
                st.error("No matching data found in the database.")
                return None

            data = {}
            for table_name in tables_to_load:
                try:
                    query = f'SELECT * FROM "{table_name}"'
                    df = pd.read_sql(query, conn, index_col='datetime')
                    df.index = pd.to_datetime(df.index)
                    df = df[df.index >= '2019-12-31']
                    if not df.empty:
                        data[table_name] = df
                except Exception as e:
                    st.warning(f"Could not load table '{table_name}': {e}")
                    continue # Skip to the next table if an error occurs

            return data

    except Exception as e:
        st.error(f"Error connecting to or reading the database: {e}")
        return None