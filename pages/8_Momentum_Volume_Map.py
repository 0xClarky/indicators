import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_market_character
from config import (
    MAJORS_LARGE_CAP, MAJORS_MID_CAP,
    MAJORS_SMALL_CAP, MAJORS_MICRO_CAP, MEME_COIN_BASKET
)
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="MoVol Map", layout="wide")
st.title("🧭 Momentum-Volatility Map (MoVol)")

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

if asset_data is None:
    st.warning("Could not load asset data. Please ensure the data updater has been run.")
    st.stop()

# --- Indicator Calculation ---
character_df = calculate_market_character(asset_data)

if character_df.empty:
    st.warning("Could not compute Market Character. Not enough historical data available for calculation.")
    st.stop()

# --- Charting ---
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=character_df['volatility'], y=character_df['momentum'],
    mode='markers+text', text=character_df.index, textposition='top center',
    marker=dict(size=12, color=character_df['momentum'], colorscale='RdYlGn',
                showscale=True, colorbar=dict(title="Momentum (%)")),
    hoverinfo='text'
))

# --- Quadrant Dividers ---
x_divider = character_df['volatility'].median()
y_divider = character_df['momentum'].median()
fig.add_vline(x=x_divider, line_width=1, line_dash="dash", line_color="gray")
fig.add_hline(y=y_divider, line_width=1, line_dash="dash", line_color="gray")

# --- Layout ---
fig.update_layout(
    height=800, title_text=f"MoVol Map for {selected_basket_name}",
    xaxis_title="30-Day Volatility (Annualized)", yaxis_title="30-Day Momentum (ROC %)",
    showlegend=False, plot_bgcolor='rgba(17, 17, 17, 1)'
)

# --- Quadrant Labels ---
fig.add_annotation(x=x_divider/2, y=y_divider + (character_df['momentum'].max()-y_divider)/2, text="Ideal Uptrend", showarrow=False, font=dict(color="lightgreen", size=14))
fig.add_annotation(x=x_divider + (character_df['volatility'].max()-x_divider)/2, y=y_divider + (character_df['momentum'].max()-y_divider)/2, text="Speculative Frenzy", showarrow=False, font=dict(color="yellow", size=14))
fig.add_annotation(x=x_divider/2, y=y_divider/2, text="Boring / Stable", showarrow=False, font=dict(color="orange", size=14))
fig.add_annotation(x=x_divider + (character_df['volatility'].max()-x_divider)/2, y=y_divider/2, text="Capitulation / Fear", showarrow=False, font=dict(color="tomato", size=14))

st.plotly_chart(fig, use_container_width=True)

# --- Explanation ---
st.markdown("---")
st.header(f"How to Use the MoVol Map for {selected_basket_name}")
col1, col2 = st.columns(2)
with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    The MoVol map plots each asset based on two key 30-day metrics:
    1.  **Momentum (Y-Axis)**: The 30-day Rate of Change (ROC).
    2.  **Volatility (X-Axis)**: The 30-day annualized realized volatility.
    The dashed lines represent the **median** values, dynamically dividing the market into four quadrants.
    """)
with col2:
    st.subheader("🎯 The Quadrants")
    st.markdown("""
    - **<font color='lightgreen'>🟢 Ideal Uptrend</font>** (Top-Left): High momentum, low volatility. Strong, stable uptrends.
    - **<font color='yellow'>🟡 Speculative Frenzy</font>** (Top-Right): High momentum, high volatility. Strong but unstable.
    - **<font color='orange'>🟠 Boring / Stable</font>** (Bottom-Left): Low momentum, low volatility. Consolidating or grinding.
    - **<font color='tomato'>🔴 Capitulation / Fear</font>** (Bottom-Right): Low momentum, high volatility. Stressed, bearish regime.
    """, unsafe_allow_html=True)