import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_altcoin_season_index
from config import (
    MACRO_SYMBOLS, MAJORS_LARGE_CAP, MAJORS_MID_CAP,
    MAJORS_SMALL_CAP, MAJORS_MICRO_CAP, MEME_COIN_BASKET
)
import numpy as np
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Altcoin Season Index", layout="wide")
st.title("Official Altcoin Season Index")

# --- UI Controls ---
asset_baskets = {
    "Everything (All Baskets)": {**MAJORS_LARGE_CAP, **MAJORS_MID_CAP, **MAJORS_SMALL_CAP, **MAJORS_MICRO_CAP, **MEME_COIN_BASKET},
    "Large Caps (>$1B)": MAJORS_LARGE_CAP,
    "Mid Caps (>$500M)": MAJORS_MID_CAP,
    "Small Caps (>$100M)": MAJORS_SMALL_CAP,
    "Micro Caps (>$50M)": MAJORS_MICRO_CAP,
    "Meme Coins": MEME_COIN_BASKET
}
selected_basket_name = st.selectbox("Select an Asset Basket:", options=list(asset_baskets.keys()), index=0)
selected_basket = asset_baskets[selected_basket_name]


# --- Data Loading ---
majors_data = load_data(asset_list=list(selected_basket.values()))
macro_data = load_data(asset_list=list(MACRO_SYMBOLS.values()))

if majors_data is None or macro_data is None or 'BTCUSD' not in macro_data or 'BTC_D' not in macro_data:
    st.warning("Could not load all required data. Please run the data updater scripts.")
    st.stop()

# --- Indicator Calculation ---
index_df = calculate_altcoin_season_index(majors_data, macro_data['BTCUSD'], macro_data['BTC_D'])

# --- Charting ---
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=index_df.index,
    y=index_df['altcoin_season_index'],
    mode='lines',
    name='Altcoin Season Index',
    line=dict(color='cyan', width=2.5)
))

fig.add_hline(y=75, line_dash="dash", line_color="lightgreen")
fig.add_hline(y=25, line_dash="dash", line_color="lightcoral")
fig.add_hrect(y0=75, y1=100, line_width=0, fillcolor="green", opacity=0.1,
              annotation_text="Altcoin Season", annotation_position="top left")
fig.add_hrect(y0=0, y1=25, line_width=0, fillcolor="red", opacity=0.1,
              annotation_text="Bitcoin Season", annotation_position="bottom left")

# --- Layout ---
fig.update_layout(
    height=600,
    title_text=f"Altcoin Season Index for {selected_basket_name} (0-100)",
    yaxis_title="Index Score",
    xaxis_title="Date",
    yaxis_range=[0, 100],
    showlegend=False,
    plot_bgcolor='rgba(17, 17, 17, 1)'
)

st.plotly_chart(fig, use_container_width=True)

# --- Indicator Explanation ---
st.markdown("---")
st.header(f"How the Index for {selected_basket_name} is Constructed")
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ The Three Core Components")
    st.markdown("""
    This index combines three key metrics into a single 0-100 score. Each metric is first converted into a statistical **Z-score** (how many standard deviations it is from its one-year average) to measure its significance.

    1.  **Price Breadth (50% weight)**: Based on the percentage of altcoins outperforming Bitcoin.
    2.  **Volume Breadth (25% weight)**: Based on the volume of those outperforming altcoins.
    3.  **BTC Dominance (25% weight)**: Based on the momentum of `BTC.D` (inverted).
    """)

with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    The Z-scores are combined and converted into the final 0-100 score, providing a clear view of the market's risk appetite.

    - **<font color='lightgreen'>🟢 Altcoin Season (Score > 75)</font>**: A high-conviction signal that a broad-based altseason is in effect for this market segment.
    
    - **<font color='lightcoral'>🔴 Bitcoin Season (Score < 25)</font>**: Indicates that market conditions heavily favor Bitcoin.
    
    - **<font color='white'>⚪ Neutral Zone (25-75)</font>**: The market is in a transitional or choppy state.
    """, unsafe_allow_html=True)