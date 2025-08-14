import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_distance_from_ma
from config import (
    MAJORS_LARGE_CAP, MAJORS_MID_CAP,
    MAJORS_SMALL_CAP, MAJORS_MICRO_CAP, MEME_COIN_BASKET
)
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="MA Distance Map", layout="wide")
st.title("📊 MA Distance Map")

# --- UI Controls ---
col1, col2 = st.columns(2)
with col1:
    ma_period = st.radio("Select Moving Average Period:", (50, 200), index=1, horizontal=True)

with col2:
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
distance_series = calculate_distance_from_ma(asset_data, ma_length=ma_period)

# --- Charting ---
custom_colorscale = [[0.0, 'rgb(200, 0, 0)'], [0.5, 'rgb(80, 80, 80)'], [1.0, 'rgb(0, 200, 0)']]
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=distance_series.index, y=distance_series.values, mode='markers',
    marker=dict(size=12, color=distance_series.values, colorscale=custom_colorscale, cmin=-50, cmax=50,
                showscale=True, colorbar=dict(title=f"% from {ma_period}D MA")),
    text=[f"{val:.2f}%" for val in distance_series.values], hoverinfo='x+text'
))

fig.add_hline(y=0, line_dash="dash", line_color="gray")

fig.update_layout(title=f"Percentage Distance from {ma_period}D MA for {selected_basket_name}",
                  height=700, xaxis_title="Assets", yaxis_title=f"Distance from {ma_period}D MA (%)",
                  plot_bgcolor='rgba(17, 17, 17, 1)')

st.plotly_chart(fig, use_container_width=True)


# --- Indicator Explanation (Always visible) ---
st.markdown("---")
st.header(f"How to Use the {ma_period}D MA Distance Map")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown(f"""
    This chart measures how "stretched" each asset is from its medium-term (50D) or long-term (200D) trend.

    For each asset, the value is calculated as the percentage difference between its latest closing price and its {ma_period}-day simple moving average (SMA).
    """)
    # --- THIS IS THE FIX for the ValueError ---
    # We construct the LaTeX string outside the st.latex call to avoid formatting conflicts.
    latex_formula = fr'''
    \text{{Distance \%}} = \left( \frac{{\text{{Close}} - \text{{SMA}}_{{{ma_period}}}}}{{\text{{SMA}}_{{{ma_period}}}}} \right) \times 100
    '''
    st.latex(latex_formula)


with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    This map provides a snapshot of market breadth and identifies potential leaders and laggards.

    - **<font color='lightgreen'>🟢 Broad Strength</font>**: A large cluster of green dots above the 0 line indicates widespread bullish strength, confirming a healthy market uptrend.

    - **<font color='lightcoral'>🔴 Broad Weakness</font>**: A large cluster of red dots below the 0 line shows widespread weakness, confirming a bearish market regime.

    - **<font color='white'>⚪ Dispersion & Extremes</font>**: The vertical spread of the dots shows dispersion. Assets that are extremely far from the 0 line (> +50% or < -30%) may be over-extended and due for a reversion to the mean.
    """, unsafe_allow_html=True)