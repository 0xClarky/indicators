import streamlit as st
import pandas as pd
import sqlite3

DB_FILE = "crypto_data.db"

@st.cache_data(ttl=3600) # Cache data for 1 hour
def load_all_data():
    """
    Loads all tables from the SQLite DB, filtering them to start from 2019-01-01.
    """
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()
        
        if not tables:
            return None

        data = {}
        for table_name in tables:
            query = f'SELECT * FROM "{table_name}"'
            df = pd.read_sql(query, conn, index_col='datetime')
            df.index = pd.to_datetime(df.index)
            df = df[df.index >= '2019-12-31']
            data[table_name] = df
        return data
    except Exception as e:
        st.error(f"Error connecting to or reading the database: {e}")
        return None
    finally:
        if 'conn' in locals() and conn:
            conn.close()
