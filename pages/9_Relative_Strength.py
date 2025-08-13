import streamlit as st
import plotly.graph_objects as go
from utils import load_all_data as load_main_data
from indicators import calculate_relative_strength
import sqlite3
import pandas as pd

# --- Data Loader for A/D Line Assets ---
@st.cache_data(ttl=3600)
def load_ad_line_data():
    """Loads all asset data from the separate ad_line_data.db."""
    db_file = "ad_line_data.db"
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()
        
        if not tables: return None
        data = {}
        for table_name in tables:
            df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn, index_col='datetime')
            df.index = pd.to_datetime(df.index)
            df = df[df.index >= '2019-01-01']
            data[table_name] = df
        return data
    except Exception as e:
        st.error(f"Error reading A/D Line database: {e}")
        return None
    finally:
        if 'conn' in locals() and conn: conn.close()

# --- Page Setup ---
st.set_page_config(page_title="Relative Strength", layout="wide")
st.title("📊 Relative Strength vs. BTC")
st.markdown(""" This chart shows each asset's performance relative to Bitcoin, calculated as the percentage outperformance or underperformance compared to BTC. It helps identify which assets are leading or lagging the market.""")


# --- Load Data & Calculate ---
main_data = load_main_data()
ad_data = load_ad_line_data()

if main_data is None or ad_data is None:
    st.warning("Could not load all required data. Please ensure both databases are populated.")
    st.stop()

rs_series = calculate_relative_strength(ad_data, main_data['BTCUSD'])

# --- Charting ---
# Define colors based on whether the value is positive or negative
colors = ['limegreen' if val >= 0 else 'tomato' for val in rs_series.values]

fig = go.Figure()

fig.add_trace(go.Bar(
    x=rs_series.values,
    y=rs_series.index,
    orientation='h', # This creates the horizontal bar chart
    marker=dict(color=colors),
    text=[f"{val:.2f}%" for val in rs_series.values],
    textposition='auto'
))

# --- Layout ---
fig.update_layout(
    height=1000, # Taller chart to accommodate all assets
    xaxis_title="Outperformance vs. BTC (%)",
    yaxis_title="Assets",
    yaxis=dict(autorange="reversed") # Display the strongest asset at the top
)

st.plotly_chart(fig, use_container_width=True)
