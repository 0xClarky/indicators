import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_eth_breadth_wave
from config import ALL_SYMBOLS, MACRO_SYMBOLS
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="ETH Performance Wave", layout="wide")
st.title("🌊 ETH Performance Wave")

# --- Data Loading ---
# Load the full list of assets and the specific macro data needed for the benchmark (ETH)
asset_data = load_data(asset_list=list(ALL_SYMBOLS.values()))
macro_data = load_data(asset_list=list(MACRO_SYMBOLS.values()))


if asset_data is None or macro_data is None or 'ETHUSD' not in macro_data:
    st.warning("Could not load all required data for the ETH Breadth Wave. Please run the data updater scripts.")
    st.stop()

# --- Indicator Calculation ---
wave_df = calculate_eth_breadth_wave(asset_data, macro_data['ETHUSD'], lookback_period=30)

# --- Charting ---
# Define a clear, high-contrast color scheme for the bands
colors = {
    "Strongly Outperforming (>+20%)": '#00b300',      # Vibrant Green
    "Outperforming (0% to 20%)": '#66ff66',          # Light Green
    "Underperforming (-20% to 0%)": '#ff6666',      # Light Red
    "Strongly Underperforming (<-20%)": '#b30000'  # Deep Red
}

fig = go.Figure()

# Add a trace for each performance band
for band_name in wave_df.columns:
    fig.add_trace(go.Scatter(
        x=wave_df.index,
        y=wave_df[band_name],
        mode='lines',
        name=band_name,
        line=dict(width=0.5),
        fillcolor=colors.get(band_name, 'grey'), # Use .get for safety
        stackgroup='one', # Creates the stacked area effect
        groupnorm='percent' # Normalizes the stack to 100%
    ))

# --- Layout ---
fig.update_layout(
    height=600,
    title_text="Percentage of Market Outperforming vs. Ethereum (30-Day)",
    yaxis_title="Percentage of Assets (%)",
    xaxis_title="Date",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='rgba(17, 17, 17, 1)'
)

st.plotly_chart(fig, use_container_width=True)


# --- Indicator Explanation (Always visible) ---
st.markdown("---")
st.header("How to Use the ETH Performance Wave")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    This indicator measures the strength of the altcoin market relative to its leader, Ethereum.
    
    1.  **Relative Performance**: First, the 30-day performance of every asset is calculated and compared against the 30-day performance of `ETHUSD`.
    2.  **Banding**: Assets are then grouped into four bands based on how much they are outperforming or underperforming ETH.
    3.  **Stacking**: The chart shows the percentage of the total market that falls into each band on any given day. The total always sums to 100%.
    """)

with col2:
    st.subheader("🎯 The Signal")
    st.markdown("""
    The changing size of the colored bands reveals the health and nature of an altcoin rally.

    - **<font color='#66ff66'>🟢 Healthy Altseason</font>**: A large and expanding **green area** (both light and dark) shows that a broad range of altcoins are outperforming ETH. This is the sign of a healthy, participation-driven altseason.
    
    - **<font color='#ff6666'>🔴 Risk-Off / ETH Dominance</font>**: A large and expanding **red area** indicates that most assets are weaker than Ethereum. This is common in bearish, risk-off environments or during periods when capital flocks to the safety of ETH.
    
    - **<font color='white'>⚪ Transitions</font>**: Watch the boundary between the green and red areas. A rising boundary suggests growing market strength, while a falling boundary suggests weakening breadth.
    """, unsafe_allow_html=True)