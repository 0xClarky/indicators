import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_data
from indicators import calculate_ad_line
from config import ALL_SYMBOLS, MACRO_SYMBOLS

# --- Page Configuration ---
st.set_page_config(page_title="A/D Line", layout="wide")

# --- Data Loading ---
# --- THIS IS THE FIX ---
# We now correctly pass the dictionary *values* (the table names) to the loader.
ad_line_assets = load_data(asset_list=list(ALL_SYMBOLS.values()))
macro_data = load_data(asset_list=list(MACRO_SYMBOLS.values()))


if ad_line_assets is None or macro_data is None:
    st.warning("Could not load all required data. Please run the data updater scripts.")
    st.stop()

# --- Indicator Calculation ---
ad_line_df = calculate_ad_line(ad_line_assets)

# --- Charting ---
st.title("📈 Market Breadth: Advance/Decline (A/D) Line")

# Create a figure with 2 subplots, stacked vertically
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.6, 0.4]
)

# Plot 1: TOTAL Price Chart for context
fig.add_trace(go.Scatter(
    x=macro_data['TOTAL'].index,
    y=macro_data['TOTAL']['close'],
    mode='lines',
    name='TOTAL Market Cap',
    line=dict(color='white')
), row=1, col=1)

# Plot 2: A/D Line and Daily Score
# Daily Score (Histogram)
colors = ['limegreen' if val >= 0 else 'tomato' for val in ad_line_df['daily_ad_score']]
fig.add_trace(go.Bar(
    x=ad_line_df.index,
    y=ad_line_df['daily_ad_score'],
    name='Daily A/D Score',
    marker_color=colors,
    marker_opacity=0.7 # Make bars slightly transparent
), row=2, col=1)

# Cumulative A/D Line
fig.add_trace(go.Scatter(
    x=ad_line_df.index,
    y=ad_line_df['ad_line'],
    mode='lines',
    name='A/D Line (Cumulative)',
    line=dict(color='cyan', width=2)
), row=2, col=1)

# --- Layout ---
fig.update_layout(
    height=700,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='rgba(17, 17, 17, 1)' # Dark background
)
fig.update_yaxes(title_text="Market Cap (USD)", type="log", row=1, col=1)
fig.update_yaxes(title_text="A/D Score / Line", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)


# --- Indicator Explanation (Always visible) ---
st.markdown("---")
st.header("How to Use the A/D Line")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    The Advance/Decline (A/D) Line is a classic breadth indicator that measures the participation of individual assets in a market move.

    1.  **Daily A/D Score**: For each day, we count the number of assets that closed higher ("advancers") and the number that closed lower ("decliners"). The score is:
        `Advancers - Decliners`
    
    2.  **A/D Line**: This is the cumulative sum of the Daily A/D Score over time. It provides a running total of market breadth.
    """)

with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    The primary use of the A/D Line is to confirm price trends or spot divergences.

    - **<font color='lightgreen'>🟢 Confirmation</font>**: If the market (`TOTAL`) is making new highs and the A/D Line is also making new highs, it confirms that the rally is healthy and has broad support.

    - **<font color='lightcoral'>🔴 Negative Divergence</font>**: If the market is making a new high but the **A/D Line is failing to make a new high**, it signals that fewer assets are participating in the rally. This is a classic warning sign that the trend may be weakening.

    - **<font color='cyan'>🔵 Positive Divergence</font>**: If the market makes a new low but the **A/D Line makes a higher low**, it suggests that selling pressure is decreasing and the downtrend may be nearing exhaustion.
    """, unsafe_allow_html=True)