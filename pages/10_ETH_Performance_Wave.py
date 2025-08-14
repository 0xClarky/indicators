import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_eth_breadth_wave
from config import (
    MACRO_SYMBOLS, MAJORS_LARGE_CAP, MAJORS_MID_CAP,
    MAJORS_SMALL_CAP, MAJORS_MICRO_CAP, MEME_COIN_BASKET
)
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="ETH Breadth Wave", page_icon="🌊", layout="wide")
st.title("🌊 ETH Outperformance Breadth Wave")

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
asset_data = load_data(asset_list=list(selected_basket.values()))
macro_data = load_data(asset_list=list(MACRO_SYMBOLS.values()))

if asset_data is None or macro_data is None or 'ETHUSD' not in macro_data:
    st.warning("Could not load all required data for the ETH Breadth Wave. Please run the data updater scripts.")
    st.stop()

# --- Indicator Calculation ---
wave_df = calculate_eth_breadth_wave(asset_data, macro_data['ETHUSD'], lookback_period=30)

# --- Charting ---
colors = {
    "Strongly Outperforming (>+20%)": '#00b300', "Outperforming (0% to 20%)": '#66ff66',
    "Underperforming (-20% to 0%)": '#ff6666', "Strongly Underperforming (<-20%)": '#b30000'
}
fig = go.Figure()

for band_name in wave_df.columns:
    fig.add_trace(go.Scatter(
        x=wave_df.index, y=wave_df[band_name], mode='lines', name=band_name,
        line=dict(width=0.5), fillcolor=colors.get(band_name, 'grey'),
        stackgroup='one', groupnorm='percent'
    ))

# --- Layout ---
fig.update_layout(
    height=600, title_text=f"Percentage of {selected_basket_name} Outperforming vs. Ethereum (30-Day)",
    yaxis_title="Percentage of Assets (%)", xaxis_title="Date",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='rgba(17, 17, 17, 1)'
)

st.plotly_chart(fig, use_container_width=True)

# --- Explanation ---
st.markdown("---")
st.header(f"How to Use the ETH Breadth Wave for {selected_basket_name}")
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    This indicator measures the strength of an asset class relative to Ethereum.
    1.  **Relative Performance**: The 30-day performance of every asset in the basket is compared against the 30-day performance of `ETHUSD`.
    2.  **Banding**: Assets are grouped into four bands based on their level of outperformance or underperformance.
    3.  **Stacking**: The chart shows the percentage of the market that falls into each band, always summing to 100%.
    """)

with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    The changing size of the colored bands reveals the health of a rally relative to ETH.
    - **<font color='#66ff66'>🟢 Broad Strength</font>**: An expanding **green area** shows that a broad range of assets are outperforming ETH, a sign of a healthy, participation-driven rally.
    - **<font color='#ff6666'>🔴 ETH Dominance</font>**: An expanding **red area** indicates most assets are weaker than Ethereum, common in risk-off periods or when capital flocks to the safety of ETH.
    """, unsafe_allow_html=True)