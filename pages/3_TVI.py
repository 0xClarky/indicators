import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_all_data
from indicators import calculate_volatility_index

st.set_page_config(page_title="TVI", layout="wide")
st.title("📊 TOTAL: Volatility Index")
st.markdown(""" The TVI measures market turbulence for the total crypto market by expressing ATR(14) as a percentage of price, with a 30-day MA to define regimes.""")

data = load_all_data()
if data is None:
    st.stop()

# --- Create a figure with 2 subplots, stacked vertically ---
fig = make_subplots(
    rows=2, 
    cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.03,
    row_heights=[0.6, 0.4]
)

# --- Plot 1: TOTAL Price Chart (Top subplot) ---
fig.add_trace(go.Scatter(
    x=data['TOTAL'].index, 
    y=data['TOTAL']['close'], 
    mode='lines',
    name='TOTAL Market Cap'
), row=1, col=1)

# --- Plot 2: Volatility Index (Bottom subplot) ---
# Note: This will fail until high/low data is added to the database.
try:
    vol_df = calculate_volatility_index(data['TOTAL'])
    fig.add_trace(go.Scatter(
        x=vol_df.index, 
        y=vol_df['volatility_index'], 
        mode='lines', 
        name='Volatility Index', 
        line=dict(color='cyan')
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=vol_df.index, 
        y=vol_df['vol_ma'], 
        mode='lines', 
        name='Volatility MA', 
        line=dict(color='yellow')
    ), row=2, col=1)
except Exception as e:
    st.error(f"Could not calculate Volatility Index. This is likely because 'high' and 'low' data are missing from the database. Error: {e}")


# --- Update Layout for the entire figure ---
fig.update_layout(
    height=800,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis_rangeslider_visible=False
)

# Update y-axis titles
fig.update_yaxes(title_text="Market Cap (USD)", row=1, col=1)
fig.update_yaxes(title_text="Volatility (%)", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

# --- Interpretation ---
with st.expander("How to interpret"):
    st.markdown("""
**Crypto Volatility Index (TVI/CVI)**

What it shows:
- Volatility Index = ATR(14) / Close × 100 on TOTAL market cap (ATR captures the average high‑low range).
- Volatility MA = 30‑day moving average of the index to smooth the regime.

How to read:
- Spikes higher → turbulence/liquidations, risk‑off or unstable conditions.
- Troughs and contraction → calmer markets, trends can persist (risk‑on/complacency).
- Rising above its MA and expanding → volatility regime shift up; more whipsaw risk.
- Falling below its MA and contracting → calming regime; breakouts less likely.

Context with price:
- Price up + falling vol → healthy, steady uptrend.
- Price up + rising vol → vulnerable advance, distribution risk.
- Price down + rising vol → stress/capitulation risk.
- Price down + falling vol → selling exhaustion; mean‑reversion potential.

Usage:
- Adjust position size and stop width with volatility (wider in high vol, tighter in low vol).
- Combine with trend/levels; this is not a directional signal on its own.

Data note:
- Requires high/low/close for ATR. If missing, the calculation will fail.
""")