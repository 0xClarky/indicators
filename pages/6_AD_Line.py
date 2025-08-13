import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_all_data as load_main_data # Main data loader
from indicators import calculate_ad_line
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
        
        if not tables:
            return None

        data = {}
        for table_name in tables:
            df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn, index_col='datetime')
            df.index = pd.to_datetime(df.index)
            df = df[df.index >= '2020-01-01'] # Filter to match other charts
            data[table_name] = df
        return data
    except Exception as e:
        st.error(f"Error reading A/D Line database: {e}")
        return None
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# --- Page Setup ---
st.set_page_config(page_title="AD Line", layout="wide")
st.title("📊 Market Breadth: A/D Line")
st.markdown(""" Advance/Decline (A/D) Line is a market breadth guage that cumulatively sums daily net advancers minus decliners across 40+ assets. A rising A/D Line confirms broad participation in uptrends, while a falling A/D Line indicates narrowing breadth and potential weakness in rallies.""")

# --- Load Data ---
main_data = load_main_data()
ad_data = load_ad_line_data()

if main_data is None or ad_data is None:
    st.warning("Could not load all required data. Please ensure both `crypto_data.db` and `ad_line_data.db` exist and are populated.")
    st.stop()

# --- Calculate Indicator ---
ad_line_df = calculate_ad_line(ad_data)

# --- Charting ---
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

# Plot 1: TOTAL Price Chart for context
fig.add_trace(go.Scatter(
    x=main_data['TOTAL'].index, 
    y=main_data['TOTAL']['close'], 
    mode='lines',
    name='TOTAL Market Cap'
), row=1, col=1)

# Plot 2: A/D Line and Daily Score
# Daily Score (Histogram)
colors = ['limegreen' if val >= 0 else 'tomato' for val in ad_line_df['daily_ad_score']]
fig.add_trace(go.Bar(
    x=ad_line_df.index, 
    y=ad_line_df['daily_ad_score'], 
    name='Daily A/D Score',
    marker_color=colors
), row=2, col=1)

# Cumulative A/D Line
fig.add_trace(go.Scatter(
    x=ad_line_df.index, 
    y=ad_line_df['ad_line'], 
    mode='lines', 
    name='A/D Line', 
    line=dict(color='cyan', width=2)
), row=2, col=1)

# --- Layout ---
fig.update_layout(
    height=800,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_rangeslider_visible=False
)
fig.update_yaxes(title_text="Market Cap (USD)", row=1, col=1)
fig.update_yaxes(title_text="A/D Score / Line", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

# --- Interpretation ---
with st.expander("How to interpret"):
    st.markdown("""
**Market Breadth: Advance/Decline (A/D) Line**

What it shows:
- Daily A/D Score (histogram): Net breadth each day (advancers − decliners across the tracked asset universe). Green = more advancers; red = more decliners.
- A/D Line (cyan): Cumulative sum of the Daily A/D Score — a running measure of breadth over time.
- Top panel price (TOTAL) provides context.

How to read:
- Rising A/D Line → breadth expanding; rallies are broadly supported.
- Falling A/D Line → breadth deteriorating; gains are carried by fewer assets or more assets are declining.
- Clusters of green bars above 0 indicate persistent positive breadth; clusters of red indicate persistent negative breadth.

Divergences:
- Price up while A/D Line trends down → negative breadth divergence; rally may be narrowing and vulnerable.
- Price down while A/D Line trends up → positive breadth divergence; selling pressure may be fading, potential for reversal.

Usage:
- Use breadth to confirm or question the strength of price trends and regime changes.
- Look for higher highs/lows in the A/D Line to confirm new uptrends; lower highs/lows to confirm downtrends.

Notes:
- Breadth here is equally weighted across assets (not market‑cap weighted).
- Universe and data coverage (ad_line_data.db) affect results; changes in constituents or missing data can shift the level.
""")