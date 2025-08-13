import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_all_data
from indicators import calculate_stablecoin_vs_total_roc

st.set_page_config(page_title="DIVROC", layout="wide")
st.title("📈 TOTAL: Stablecoin vs TOTAL ROC (30D)")
st.markdown(""" DVIROC compares the 30-day rate of change of total crypto market cap to the inverted 30-day rate of change of stablecoin dominance (USDT.D and USDC.D) to guage risk-on/off capital flows.""")

data = load_all_data()
if data is None:
    st.stop()

# --- Create a figure with 2 subplots, stacked vertically ---
fig = make_subplots(
    rows=2, 
    cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.03, # Minimal space between charts
    row_heights=[0.6, 0.4]  # Top chart is 70% height, bottom is 30%
)

# --- Plot 1: TOTAL Price Chart (Top subplot) ---
fig.add_trace(go.Scatter(
    x=data['TOTAL'].index, 
    y=data['TOTAL']['close'], 
    mode='lines',
    name='TOTAL Market Cap'
), row=1, col=1)

# --- Plot 2: ROC Indicator (Bottom subplot) ---
roc_df = calculate_stablecoin_vs_total_roc(data['TOTAL'], data['USDT_D'], data['USDC_D'])
fig.add_trace(go.Scatter(
    x=roc_df.index, 
    y=roc_df['roc_total'], 
    mode='lines', 
    name='TOTAL ROC', 
    line=dict(color='deepskyblue')
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=roc_df.index, 
    y=roc_df['roc_stable_inv'], 
    mode='lines', 
    name='Inverted Stablecoin ROC', 
    line=dict(color='white')
), row=2, col=1)

# Add horizontal lines to the second subplot
fig.add_hline(y=20, line_dash="dash", line_color="lightgreen", row=2, col=1)
fig.add_hline(y=-20, line_dash="dash", line_color="lightcoral", row=2, col=1)
fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)


# --- Update Layout for the entire figure ---
fig.update_layout(
    height=800, # Total height for the combined chart
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    # Remove the default range slider for a cleaner look
    xaxis_rangeslider_visible=False
)

# Update y-axis titles
fig.update_yaxes(title_text="Market Cap (USD)", row=1, col=1)
fig.update_yaxes(title_text="ROC (%)", row=2, col=1, range=[-50, 50])

st.plotly_chart(fig, use_container_width=True)

# --- Interpretation ---
with st.expander("How to interpret"):
    st.markdown("""
**Stablecoin Dominance 30D ROC vs. TOTAL 30D ROC**

What it shows:
- TOTAL ROC: 30‑day percent change of total crypto market cap.
- iROC (Inverted Stablecoin ROC): Average 30‑day ROC of USDT.D and USDC.D, multiplied by −1.
  Rising iROC = falling stablecoin dominance (risk‑on). Falling iROC = rising dominance (risk‑off).

Levels:
- ±20% dashed lines mark strong momentum zones.
- Both lines above +20% and rising → strong bullish, risk‑on.
- Both below −20% and falling → risk‑off rotation; inflows to stables.

Gap analysis:
- Uptrend, widening gap (TOTAL ROC > iROC and both > 0) → capital enters crypto faster than it leaves stables; conviction/new capital.
- Downtrend, widening gap (TOTAL ROC < iROC and both < 0) → market shrinks faster than stables absorb; potential net outflows/capitulation.

Divergences:
- If TOTAL ROC and iROC move in opposite directions, flows and price may be misaligned → watch for exhaustion or reversals.

Note: iROC is inverted; a drop in iROC means stablecoin dominance is rising.
""")