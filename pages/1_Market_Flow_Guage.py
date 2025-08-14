import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_stablecoin_vs_total_roc
from config import MACRO_SYMBOLS

# --- Page Configuration ---
st.set_page_config(page_title="MFG", layout="wide") # Changed page title

# --- Data Loading ---
data = load_data(asset_list=list(MACRO_SYMBOLS.values()))

if data is None:
    st.warning("Could not load the required macro data. Please run the data updater scripts.")
    st.stop()

# --- Indicator Calculation ---
# The underlying calculation remains the same
roc_df = calculate_stablecoin_vs_total_roc(data['TOTAL'], data['USDT_D'], data['USDC_D'], roc_len=30)

# --- Charting ---
st.title("🌊 Market Flow Guage (MFG)") # Changed indicator name

# Create the figure
fig = go.Figure()

# Add the two main ROC lines
fig.add_trace(go.Scatter(
    x=roc_df.index,
    y=roc_df['roc_total'],
    mode='lines',
    name='30D ROC of TOTAL (%)', # Updated name for clarity
    line=dict(color='deepskyblue', width=2)
))
fig.add_trace(go.Scatter(
    x=roc_df.index,
    y=roc_df['roc_stable_inv'],
    mode='lines',
    name='Inverted 30D ROC of Stables (%)', # Updated name for clarity
    line=dict(color='white', width=2)
))

# Fill the area between the lines to visualize the gap
fig.add_trace(go.Scatter(
    x=roc_df.index,
    y=roc_df['roc_total'],
    fill='tonexty',
    mode='none',
    fillcolor='rgba(255, 255, 255, 0.1)',
    name='Flow Gap'
))

# Add key horizontal lines for context
fig.add_hline(y=20, line_dash="dash", line_color="lightgreen", line_width=1)
fig.add_hline(y=-20, line_dash="dash", line_color="lightcoral", line_width=1)
fig.add_hline(y=0, line_dash="dot", line_color="gray", line_width=1)

# --- Layout and Aesthetics ---
fig.update_layout(
    height=600,
    xaxis_title="Date",
    yaxis_title="30-Day Rate of Change (%)",
    yaxis_range=[-60, 60],
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='rgba(17, 17, 17, 1)'
)

st.plotly_chart(fig, use_container_width=True)

# --- Indicator Explanation (Always visible) ---
st.markdown("---")
st.header("How to Use the Market Flow Guage (MFG)") # Changed header

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    The RFI compares two 30-day Rate of Change (ROC) calculations to gauge market-wide risk appetite. The formula for ROC is:
    """)
    st.latex(r'''
    ROC = \left( \frac{\text{Current Price} - \text{Price 30 days ago}}{\text{Price 30 days ago}} \right) \times 100
    ''')
    st.markdown("""
    **The two lines on the chart are:**
    1.  **`Market Momentum`**: The ROC of the `TOTAL` market cap.
    2.  **`Capital Flow`**: The inverted average ROC of `USDT.D` and `USDC.D`.
    """)
    st.latex(r'''
    \text{Capital Flow} = -1 \times \left( \frac{ROC_{USDT.D} + ROC_{USDC.D}}{2} \right)
    ''')


with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    The relationship between these lines signals the character of capital flows:

    - **<font color='lightgreen'>🟢 Bullish Confirmation</font>**: Both lines are **above 0** and rising. This signals a healthy, risk-on environment where the market is growing and capital is rotating out of stablecoins.

    - **<font color='lightcoral'>🔴 Bearish Confirmation</font>**: Both lines are **below 0** and falling. This signals a risk-off environment where the market is contracting and capital is flowing into stablecoins for safety.

    - **<font color='white'>⚪ Flow Gap</font>**: A wide, positive gap (Market Momentum > Capital Flow) suggests new capital is entering the market, not just rotating from stables—a sign of strong conviction.

    - **<font color='orange'>🟠 Divergence</font>**: When the lines move in opposite directions, it warns of a potential trend change or market exhaustion. For example, if the market is rising but capital flow from stables is falling, the rally may be losing momentum.
    """, unsafe_allow_html=True)