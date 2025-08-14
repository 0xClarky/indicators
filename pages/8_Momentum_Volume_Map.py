import streamlit as st
import plotly.graph_objects as go
from utils import load_data
from indicators import calculate_market_character
from config import ALL_SYMBOLS
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="MoVol Map", layout="wide")
st.title("🧭 Momentum-Volatility Map (MoVol)")

# --- Data Loading ---
# Load all individual assets for the map
asset_data = load_data(asset_list=list(ALL_SYMBOLS.values()))

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

# Add the scatter plot trace for the assets
fig.add_trace(go.Scatter(
    x=character_df['volatility'],
    y=character_df['momentum'],
    mode='markers+text',
    text=character_df.index,
    textposition='top center',
    marker=dict(
        size=12,
        color=character_df['momentum'],
        colorscale='RdYlGn', # Red-Yellow-Green colorscale for momentum
        showscale=True,
        colorbar=dict(title="Momentum (%)")
    ),
    hoverinfo='text'
))

# --- Define and draw the quadrant dividers ---
# Use the median values as dynamic dividers for a balanced view
x_divider = character_df['volatility'].median()
y_divider = character_df['momentum'].median()

fig.add_vline(x=x_divider, line_width=1, line_dash="dash", line_color="gray")
fig.add_hline(y=y_divider, line_width=1, line_dash="dash", line_color="gray")

# --- Layout and Aesthetics ---
fig.update_layout(
    height=800,
    xaxis_title="30-Day Volatility (Annualized)",
    yaxis_title="30-Day Momentum (ROC %)",
    showlegend=False,
    plot_bgcolor='rgba(17, 17, 17, 1)'
)

# Add annotations for quadrant labels
fig.add_annotation(x=x_divider/2, y=y_divider + (character_df['momentum'].max()-y_divider)/2, text="Ideal Uptrend", showarrow=False, font=dict(color="lightgreen", size=14))
fig.add_annotation(x=x_divider + (character_df['volatility'].max()-x_divider)/2, y=y_divider + (character_df['momentum'].max()-y_divider)/2, text="Speculative Frenzy", showarrow=False, font=dict(color="yellow", size=14))
fig.add_annotation(x=x_divider/2, y=y_divider/2, text="Boring / Stable", showarrow=False, font=dict(color="orange", size=14))
fig.add_annotation(x=x_divider + (character_df['volatility'].max()-x_divider)/2, y=y_divider/2, text="Capitulation / Fear", showarrow=False, font=dict(color="tomato", size=14))


st.plotly_chart(fig, use_container_width=True)

# --- Indicator Explanation (Always visible) ---
st.markdown("---")
st.header("How to Use the MoVol Map")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    The MoVol map plots each asset based on two key 30-day metrics:
    
    1.  **Momentum (Y-Axis)**: The 30-day Rate of Change (ROC). This measures the asset's recent performance.
    2.  **Volatility (X-Axis)**: The 30-day realized volatility of daily returns, annualized for comparison. This measures the asset's price stability.
    
    The dashed lines represent the **median** momentum and volatility of the entire dataset, dynamically dividing the market into four character quadrants.
    """)

with col2:
    st.subheader("🎯 The Quadrants")
    st.markdown("""
    Each quadrant describes a distinct market character:

    - **<font color='lightgreen'>🟢 Ideal Uptrend</font>** (Top-Left): High momentum, low volatility. These are assets in a strong, stable uptrend.
    
    - **<font color='yellow'>🟡 Speculative Frenzy</font>** (Top-Right): High momentum, high volatility. Strong performance, but unstable and prone to sharp swings.
    
    - **<font color='orange'>🟠 Boring / Stable</font>** (Bottom-Left): Low momentum, low volatility. Assets are consolidating, grinding, or in a slow downtrend.
    
    - **<font color='tomato'>🔴 Capitulation / Fear</font>** (Bottom-Right): Low momentum, high volatility. The most dangerous quadrant, indicating a stressed, bearish regime.
    """, unsafe_allow_html=True)