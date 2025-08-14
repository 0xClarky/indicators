import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_altcoin_season_index_v1 # Corrected import
from config import MACRO_SYMBOLS
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="ASI1", layout="wide")

# --- Data Loading ---
data = load_data(asset_list=list(MACRO_SYMBOLS.values()))

if data is None:
    st.warning("Could not load the required macro data. Please run the data updater scripts.")
    st.stop()

# --- Indicator Calculation ---
# Corrected function call
asi_df = calculate_altcoin_season_index_v1(data['TOTAL3'], data['BTC_D'], ma_length=30)

# --- Charting ---
st.title("🔥 Altcoin Season Index 1")

fig = go.Figure()

# Add the bar chart for the daily ASI value
colors = ['limegreen' if val >= 0 else 'tomato' for val in asi_df['asi_value']]
fig.add_trace(go.Bar(
    x=asi_df.index,
    y=asi_df['asi_value'],
    name='Daily ASI Value',
    marker_color=colors,
    marker_opacity=0.5
))

# Add the moving average signal line
fig.add_trace(go.Scatter(
    x=asi_df.index,
    y=asi_df['signal_line'],
    mode='lines',
    name='30-Day Signal Line',
    line=dict(color='white', width=2.5)
))

fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)

# --- Layout and Aesthetics ---
fig.update_layout(
    height=600,
    xaxis_title="Date",
    yaxis_title="Momentum Spread (TOTAL3 vs. BTC.D)",
    yaxis_range=[-10, 10],
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='rgba(17, 17, 17, 1)'
)

st.plotly_chart(fig, use_container_width=True)

# --- Indicator Explanation ---
st.markdown("---")
st.header("How to Use the Altcoin Season Index 1")
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    This index measures the daily momentum spread between the altcoin market (`TOTAL3`) and Bitcoin's dominance (`BTC.D`).
    """)
    st.latex(r'''
    \text{ASI} = \text{ROC}_{1D}(\text{TOTAL3}) - \text{ROC}_{1D}(\text{BTC.D})
    ''')
    st.markdown("""
    - A **positive value** means the altcoin market cap grew faster than BTC dominance.
    - A **30-day moving average** is used as a signal line to identify the trend.
    """)

with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    - **<font color='lightgreen'>🟢 Altcoin Season</font>**: When the ASI value is consistently **above 0** and **above its signal line**, it indicates altcoins are outperforming Bitcoin.
    - **<font color='lightcoral'>🔴 Bitcoin Season</font>**: When the ASI value is consistently **below 0** and **below its signal line**, it signals capital is favoring Bitcoin.
    - **<font color='orange'>🟠 Crossovers</font>**: The crossing of the ASI and its signal line can be an early indicator of a shift in market leadership.
    """, unsafe_allow_html=True)
