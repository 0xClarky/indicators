import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_regime_scatter_data
from config import MEME_COIN_BASKET, MACRO_SYMBOLS
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Meme Strength", layout="wide")
st.title("Meme Strength Indicator: Memes vs. Total Market")

# --- UI Controls ---
lookback_days = st.slider(
    "Select Lookback Window (Days):",
    min_value=30,
    max_value=365,
    value=90, # Default to the last 90 days
    step=15,
    help="Adjust the slider to see how the market character has changed over different timeframes."
)

# --- Data Loading ---
# Load the necessary assets for the calculation
meme_assets = load_data(asset_list=list(MEME_COIN_BASKET.values()))
macro_data = load_data(asset_list=list(MACRO_SYMBOLS.values()))


if meme_assets is None or macro_data is None:
    st.warning("Could not load all required data for the Meme Index. Please run the data updater scripts.")
    st.stop()

# --- Indicator Calculation ---
# Calculate the data for the entire history first
full_regime_df = calculate_regime_scatter_data(meme_assets, macro_data['TOTAL'])

# Filter the data based on the slider
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
        colorbar=dict(title="Meme Index Perf. (%)")
    ),
    text=regime_df.index.strftime('%Y-%m-%d'),
    hoverinfo='text+x+y'
))

# --- Add reference lines ---
# Diagonal line for 1:1 performance
min_val = min(regime_df['total_performance'].min(), regime_df['meme_performance'].min())
max_val = max(regime_df['total_performance'].max(), regime_df['meme_performance'].max())
fig.add_shape(type="line", x0=min_val, y0=min_val, x1=max_val, y1=max_val, line=dict(color="gray", width=2, dash="dash"))
# Zero lines for quadrants
fig.add_vline(x=0, line_width=1, line_color="gray")
fig.add_hline(y=0, line_width=1, line_color="gray")

# --- Layout ---
fig.update_layout(
    height=700,
    xaxis_title="Total Market 30-Day Performance (%)",
    yaxis_title="Meme Index 30-Day Performance (%)",
    title=f"Market Regime: Last {lookback_days} Days",
    showlegend=False,
    plot_bgcolor='rgba(17, 17, 17, 1)'
)

st.plotly_chart(fig, use_container_width=True)


# --- Indicator Explanation (Always visible) ---
st.markdown("---")
st.header("How to use the Meme Strength Indicator")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    This plot maps the relationship between the broader crypto market and the highly speculative "meme coin" sector.
    
    1.  **Meme Index**: An equally-weighted index is created from the assets in the `MEME_COIN_BASKET`.
    2.  **Performance Calculation**: For each day, the 30-day performance (ROC) is calculated for both the Meme Index (Y-Axis) and the `TOTAL` market cap (X-Axis).
    3.  **Plotting**: Each dot on the chart represents a single day, plotted according to these two performance metrics.
    """)

with col2:
    st.subheader("🎯 The Quadrants")
    st.markdown("""
    The location of the dots reveals the market's risk appetite:

    - **<font color='lightgreen'>🟢 Broad Rally</font>** (Top-Right): Both the market and meme coins are performing well. Memes outperforming (dots above the dashed line) signals high risk appetite.
    
    - **<font color='lightblue'>🔵 Risk-On Rotation</font>** (Top-Left): Meme coins are rising while the broader market is falling. This can signal speculative rotation or a "last hurrah" for a rally.
    
    - **<font color='orange'>🟠 Defensive</font>** (Bottom-Left): Both the market and memes are falling, a clear risk-off environment.
    
    - **<font color='tomato'>🔴 Market-Led Weakness</font>** (Bottom-Right): The market is falling faster than meme coins, or memes are flat while the market drops. This can signal broader weakness that hasn't fully hit the speculative corners yet.
    """, unsafe_allow_html=True)