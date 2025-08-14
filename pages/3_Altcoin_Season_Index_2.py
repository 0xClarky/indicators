import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_official_altcoin_season_index
from config import (
    MACRO_SYMBOLS, MAJORS_LARGE_CAP, MAJORS_MID_CAP,
    MAJORS_SMALL_CAP, MAJORS_MICRO_CAP, MEME_COIN_BASKET
)
import numpy as np
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Official Altcoin Season Index", layout="wide")
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
index_df = calculate_official_altcoin_season_index(majors_data, macro_data['BTCUSD'], macro_data['BTC_D'])

# --- Charting ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=index_df.index, y=index_df['altcoin_season_index'], mode='lines', name='Altcoin Season Index', line=dict(color='cyan', width=2.5)))
fig.add_hline(y=75, line_dash="dash", line_color="lightgreen")
fig.add_hline(y=25, line_dash="dash", line_color="lightcoral")
fig.add_hrect(y0=75, y1=100, line_width=0, fillcolor="green", opacity=0.1, annotation_text="Altcoin Season", annotation_position="top left")
fig.add_hrect(y0=0, y1=25, line_width=0, fillcolor="red", opacity=0.1, annotation_text="Bitcoin Season", annotation_position="bottom left")
fig.update_layout(height=600, title_text=f"Altcoin Season Index for {selected_basket_name} (0-100)", yaxis_title="Index Score", xaxis_title="Date", yaxis_range=[0, 100], showlegend=False, plot_bgcolor='rgba(17, 17, 17, 1)')
st.plotly_chart(fig, use_container_width=True)


# --- Indicator Explanation ---
st.markdown("---")
st.header(f"How to Use the Altcoin Season Index 2")

# --- Use a two-column layout for the full explanation ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    This index combines three key metrics into a single 0-100 score. The process involves four main steps:
    """)
    st.markdown("<h6>Step 1: Calculate the Raw Metrics</h6>", unsafe_allow_html=True)
    st.markdown("""
    - **Price Breadth**: The percentage of altcoins outperforming Bitcoin over the last 90 days.
    - **Volume Breadth**: The total USD volume of those outperforming altcoins.
    - **Dominance Momentum**: The 90-day performance of Bitcoin Dominance (`BTC.D`).
    """)
    st.markdown("<h6>Step 2: Measure Significance with Z-Scores</h6>", unsafe_allow_html=True)
    st.markdown("""
    We convert each raw metric into a **Z-score** to measure its statistical significance relative to its one-year history.
    """)
    st.markdown("<h6>Step 3: Combine Scores with Weights</h6>", unsafe_allow_html=True)
    st.markdown("""
    The three Z-scores are combined using a balanced **50/25/25** weighting (Price/Volume/Dominance).
    """)
    st.markdown("<h6>Step 4: Convert to a 0-100 Index</h6>", unsafe_allow_html=True)
    st.markdown("""
    The combined score is mapped to a 0-100 scale and smoothed to produce the final index.
    """)

with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    The final score provides a clear, at-a-glance view of the market's risk appetite.

    - **<font color='lightgreen'>🟢 Altcoin Season (Score > 75)</font>**: Indicates that a strong majority of factors are aligned in favor of altcoins. This is a high-conviction signal that a broad-based altseason is in effect for this market segment.
    
    - **<font color='lightcoral'>🔴 Bitcoin Season (Score < 25)</font>**: Indicates that market conditions heavily favor Bitcoin. Breadth is weak, conviction is low, and/or BTC Dominance is high.
    
    - **<font color='white'>⚪ Neutral Zone (25-75)</font>**: The market is in a transitional or choppy state. Conditions do not strongly favor either asset class.
    """, unsafe_allow_html=True)