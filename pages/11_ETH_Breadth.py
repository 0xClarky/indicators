import streamlit as st
import plotly.graph_objects as go
from utils import load_all_data as load_main_data
from indicators import calculate_eth_breadth_wave
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
st.set_page_config(page_title="ETH Breadth Wave", page_icon="🌊", layout="wide")
st.title("🌊 ETH Outperformance Breadth Wave (30-Day)")
st.info(
    """
    This chart shows the percentage of the market that is outperforming or underperforming Ethereum.
    - **Green Area Expansion:** A growing green area shows a healthy, broad-based altseason is underway.
    - **Red Area Dominance:** A large red area indicates a risk-off environment where most assets are weaker than Ethereum.
    """
)

# --- Load Data & Calculate ---
main_data = load_main_data()
ad_data = load_ad_line_data()

if main_data is None or ad_data is None:
    st.warning("Could not load all required data.")
    st.stop()

wave_df = calculate_eth_breadth_wave(ad_data, main_data['ETHUSD'])

# --- Charting ---
fig = go.Figure()

# --- NEW: Define a clearer, high-contrast color scheme ---
colors = {
    "Strongly Outperforming (>+20%)": '#00b300', # Vibrant Green
    "Outperforming (0% to 20%)": '#66ff66',      # Light Green
    "Underperforming (-20% to 0%)": '#ff6666',      # Light Red
    "Strongly Underperforming (<-20%)": '#b30000'  # Deep Red
}

# Add a trace for each performance band
for band_name in wave_df.columns:
    fig.add_trace(go.Scatter(
        x=wave_df.index,
        y=wave_df[band_name],
        mode='lines',
        name=band_name,
        line=dict(width=0.5),
        fillcolor=colors[band_name],
        stackgroup='one', # This creates the stacked area effect
        # --- NEW: This normalizes the stack to 100% ---
        groupnorm='percent' 
    ))

# --- Layout ---
fig.update_layout(
    height=900,
    title_text="Percentage of Market Outperforming vs. Ethereum",
    yaxis_title="Percentage of Assets (%)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)
