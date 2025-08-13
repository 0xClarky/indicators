import streamlit as st
import plotly.graph_objects as go
from utils import load_all_data as load_main_data
from indicators import calculate_regime_scatter_data
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
st.set_page_config(page_title="Market Regime Scatter", page_icon="🧭", layout="wide")
st.title("🧭 Market Regime Scatter Plot")
st.info(
    """
    This chart plots the 30-day performance of the Meme Coin Index against the 30-day performance of the Total Market Cap. Each dot represents a single day.
    Use the slider to filter the view to a recent period and see the current market character.
    """
)

# --- UI Controls ---
lookback_days = st.slider(
    "Select Lookback Window (Days):",
    min_value=30,
    max_value=730,
    value=90, # Default to the last 90 days
    step=15
)

# --- Load Data & Calculate ---
main_data = load_main_data()
ad_data = load_ad_line_data()

if main_data is None or ad_data is None:
    st.warning("Could not load all required data.")
    st.stop()

# Calculate the data for the entire history first
full_regime_df = calculate_regime_scatter_data(ad_data, main_data['TOTAL'])

# --- Filter the data based on the slider ---
regime_df = full_regime_df.tail(lookback_days)


# --- Charting ---
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=regime_df['total_performance'],
    y=regime_df['meme_performance'],
    mode='markers',
    marker=dict(
        size=8,
        color=regime_df['meme_performance'],
        colorscale='RdYlGn',
        showscale=True,
        colorbar=dict(title="Meme Performance (%)")
    ),
    text=regime_df.index.strftime('%Y-%m-%d'),
    hoverinfo='text+x+y'
))

# --- Add reference lines ---
min_val = min(regime_df['total_performance'].min(), regime_df['meme_performance'].min())
max_val = max(regime_df['total_performance'].max(), regime_df['meme_performance'].max())
fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="gray", width=2, dash="dash"))

fig.add_vline(x=0, line_width=1, line_color="gray")
fig.add_hline(y=0, line_width=1, line_color="gray")

# --- Layout ---
fig.update_layout(
    height=800,
    xaxis_title="Total Market 30-Day Performance (%)",
    yaxis_title="Meme Index 30-Day Performance (%)",
    title=f"Market Regime: Last {lookback_days} Days",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)
