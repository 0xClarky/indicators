import streamlit as st
import plotly.graph_objects as go
from utils import load_all_data as load_main_data
from indicators import calculate_distance_from_ma
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
            df = df[df.index >= '2019-01-01']
            data[table_name] = df
        return data
    except Exception as e:
        st.error(f"Error reading A/D Line database: {e}")
        return None
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# --- Page Setup ---
st.set_page_config(page_title="MA Scatter", layout="wide")
st.title("📊 MA Distance Map")
st.markdown(""" MA Scatter plots each asset's percent distance from a selected moving average (50D or 200D), coloured green above the MA and red below. It highlights breadth, dispersion, and extremes to spot leaders/laggards. """)

# --- UI Controls ---
ma_period = st.radio(
    "Select Moving Average Period:",
    (50, 200),
    horizontal=True,
    key="ma_dist_toggle"
)

# --- Load Data & Calculate ---
ad_data = load_ad_line_data()
if ad_data is None:
    st.warning("Could not load asset data. Please ensure `ad_line_data.db` exists.")
    st.stop()

distance_series = calculate_distance_from_ma(ad_data, ma_length=ma_period)

# --- Charting ---

# Define our custom colorscale for high contrast
custom_colorscale = [
    [0.0, 'rgb(200, 0, 0)'],      # Strong red for negative
    [0.5, 'rgb(80, 80, 80)'],     # Dark gray for neutral
    [1.0, 'rgb(0, 200, 0)']       # Strong green for positive
]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=distance_series.index,
    y=distance_series.values,
    mode='markers',
    marker=dict(
        size=16,
        color=distance_series.values, # Color bubbles based on their y-value
        colorscale=custom_colorscale,
        cmin=-50, # Set a floor for the color scale
        cmax=50,  # Set a ceiling for the color scale
        showscale=True, # Display the color bar legend
        colorbar=dict(title=f"% from {ma_period}D MA")
    ),
    text=[f"{val:.2f}%" for val in distance_series.values], # Text to show on hover
    hoverinfo='x+text'
))

# Add a zero line for reference
fig.add_hline(y=0, line_dash="dash", line_color="gray")

fig.update_layout(
    title=f"Percentage Above/Below {ma_period}D Moving Average",
    height=700,
    xaxis_title="Assets",
    yaxis_title=f"Percentage Above/Below {ma_period}D MA",
    yaxis_zeroline=False
)

st.plotly_chart(fig, use_container_width=True)

# --- Interpretation ---
with st.expander("How to interpret"):
    st.markdown("""
**MA Distance Map**

What it shows:
- Each dot = one asset. Y‑value = percent distance from the selected moving average (50D or 200D).
- Color: green above MA (positive), red below MA (negative). Zero line is the MA itself.
- Toggle 50/200 with the control above to switch between tactical (50D) and regime (200D) views.

How to read:
- Above 0 → asset trades above the chosen MA (bullish vs that timeframe).
- Below 0 → asset trades below the chosen MA (bearish vs that timeframe).
- Many greens above 0 → broad strength; many reds below 0 → broad weakness (breadth context).
- Wide dispersion (big spread between leaders and laggards) → rotation/dispersion regime; tight clustering near 0 → compression/indecision.

Thresholds (rules of thumb; asset vol matters):
- ±5–10% = mild deviation.
- ±10–20% = notable strength/weakness.
- >20% from MA = stretched; watch for mean‑reversion or consolidation.

Use cases:
- 50D: tactical momentum/rotation; identify short‑term leaders/laggards.
- 200D: long‑term regime filter; above 0 favors long bias, below 0 favors defense.
- Screen for extremes and manage risk/position sizing based on distance.

Notes:
- Uses latest close per asset; missing data may exclude symbols.
- Thin/illiquid assets can show noisy, outsized deviations.
""")