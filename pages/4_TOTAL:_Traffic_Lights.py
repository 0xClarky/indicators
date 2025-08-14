import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_traffic_light
from config import MACRO_SYMBOLS

# --- Page Configuration ---
st.set_page_config(page_title="Regime Map", layout="wide")

# --- Data Loading ---
data = load_data(asset_list=list(MACRO_SYMBOLS.values()))

if data is None:
    st.warning("Could not load the required macro data. Please run the data updater scripts.")
    st.stop()

# --- Indicator Calculation ---
regime_df = calculate_traffic_light(data['TOTAL'])

# --- Charting ---
st.title("🚦 TOTAL Regime Map (Traffic Lights)")

fig = go.Figure()

# --- Logic to draw the background color fills ---
# This creates the colored rectangles for each regime
current_color = regime_df['regime_color'].iloc[0]
start_date = regime_df.index[0]

for i in range(1, len(regime_df)):
    if regime_df['regime_color'].iloc[i] != current_color:
        fig.add_vrect(
            x0=start_date, x1=regime_df.index[i-1],
            fillcolor=current_color, opacity=0.4, layer="below", line_width=0,
        )
        start_date = regime_df.index[i]
        current_color = regime_df['regime_color'].iloc[i]
# Add the final colored block
fig.add_vrect(
    x0=start_date, x1=regime_df.index[-1],
    fillcolor=current_color, opacity=0.4, layer="below", line_width=0,
)

# --- Add the price and moving average lines ---
fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['close'], mode='lines', name='TOTAL Market Cap', line=dict(color='white', width=2.5)))
fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['EMA_21'], mode='lines', name='21 EMA', line=dict(color='cyan', width=1.5, dash='dot')))
fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['SMA_50'], mode='lines', name='50 SMA', line=dict(color='magenta', width=1.5, dash='dot')))
fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['SMA_200'], mode='lines', name='200 SMA', line=dict(color='yellow', width=2)))


# --- Layout and Aesthetics ---
fig.update_layout(
    height=600,
    yaxis_title="Market Cap (USD)",
    xaxis_title="Date",
    yaxis_type="log", # Log scale is often better for viewing market cap over long periods
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='rgba(17, 17, 17, 1)' # Dark background
)
st.plotly_chart(fig, use_container_width=True)

# --- Indicator Explanation (Always visible) ---
st.markdown("---")
st.header("How to Use the Regime Map")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    The background color is determined by the alignment of the `TOTAL` price relative to its key moving averages (21 EMA, 50 SMA, 200 SMA).
    
    - **Green Regime**: The market is in a full bullish alignment.
      `Close > 21 EMA > 50 SMA > 200 SMA`
      
    - **Red Regime**: The market is in a clear bearish trend.
      `Close < 200 SMA`
      
    - **Yellow Regime**: The market is in a neutral, corrective, or transitional state. This occurs when the conditions for Green or Red are not met.
    """)

with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    This indicator provides a high-level view of the macro trend, helping you to align your strategy with the dominant market character.

    - **<font color='lightgreen'>🟢 Green (Bull Market)</font>**: Conditions are favorable. Dips are often bought, and trend-following strategies tend to perform well.
    
    - **<font color='lightcoral'>🔴 Red (Bear Market)</font>**: Conditions are unfavorable. Rallies are often sold, and a defensive posture is typically warranted.
    
    - **<font color='orange'>🟡 Yellow (Transition / Chop)</font>**: The trend is unclear. The market may be consolidating or reversing. This is often a time for increased caution and reduced position sizing.
    """, unsafe_allow_html=True)