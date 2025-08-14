import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_data
from indicators import calculate_ad_line
from config import (
    MACRO_SYMBOLS, MAJORS_LARGE_CAP, MAJORS_MID_CAP,
    MAJORS_SMALL_CAP, MAJORS_MICRO_CAP, MEME_COIN_BASKET
)
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="A/D Line", layout="wide")
st.title("📈 Market Breadth: Advance/Decline (A/D) Line")

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
ad_line_assets = load_data(asset_list=list(selected_basket.values()))
macro_data = load_data(asset_list=list(MACRO_SYMBOLS.values()))

if ad_line_assets is None or macro_data is None:
    st.warning("Could not load all required data. Please run the data updater scripts.")
    st.stop()

# --- Indicator Calculation ---
ad_line_df = calculate_ad_line(ad_line_assets)

# --- Charting ---
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.6, 0.4])

fig.add_trace(go.Scatter(x=macro_data['TOTAL'].index, y=macro_data['TOTAL']['close'], mode='lines', name='TOTAL Market Cap', line=dict(color='white')), row=1, col=1)

colors = ['limegreen' if val >= 0 else 'tomato' for val in ad_line_df['daily_ad_score']]
fig.add_trace(go.Bar(x=ad_line_df.index, y=ad_line_df['daily_ad_score'], name='Daily A/D Score', marker_color=colors, marker_opacity=0.7), row=2, col=1)
fig.add_trace(go.Scatter(x=ad_line_df.index, y=ad_line_df['ad_line'], mode='lines', name='A/D Line (Cumulative)', line=dict(color='cyan', width=2)), row=2, col=1)

fig.update_layout(height=700, title_text=f"A/D Line for {selected_basket_name}", showlegend=True,
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                  plot_bgcolor='rgba(17, 17, 17, 1)')
fig.update_yaxes(title_text="Market Cap (USD)", type="log", row=1, col=1)
fig.update_yaxes(title_text="A/D Score / Line", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

# --- Indicator Explanation ---
st.markdown("---")
st.header("How to Use the A/D Line")
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    The Advance/Decline (A/D) Line is a classic breadth indicator that measures market participation.
    1.  **Daily A/D Score**: For each day, we count the number of assets that closed higher ("advancers") and lower ("decliners"). The score is `Advancers - Decliners`.
    2.  **A/D Line**: This is the cumulative sum of the Daily A/D Score over time, providing a running total of market breadth.
    """)

with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    The primary use of the A/D Line is to confirm price trends or spot divergences.
    - **<font color='lightgreen'>🟢 Confirmation</font>**: `TOTAL` price and the A/D Line are both making new highs, confirming a healthy rally.
    - **<font color='lightcoral'>🔴 Negative Divergence</font>**: `TOTAL` makes a new high, but the **A/D Line fails to**, signaling weakening participation.
    - **<font color='cyan'>🔵 Positive Divergence</font>**: `TOTAL` makes a new low, but the **A/D Line makes a higher low**, suggesting selling pressure is fading.
    """, unsafe_allow_html=True)