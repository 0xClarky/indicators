import streamlit as st
import plotly.graph_objects as go
from utils import load_all_data
from indicators import calculate_traffic_light

st.set_page_config(page_title="Total Traffic Lights", layout="wide")
st.title("🚦 TOTAL: SMA Traffic Lights")
st.markdown(""" The Traffic Lights is a regime indicator that overlays TOTAL with the 21 EMA, 50 SMA, and 200 SMA. The colours in the background (green/yellow/red) are based on trend alignment and price relative to these moving averages. It helps identify macro regimes and trend strength.""")

data = load_all_data()
if data is None:
    st.stop()

# --- Calculate the regime colors and MAs ---
regime_df = calculate_traffic_light(data['TOTAL'])


# --- Create the plot ---
fig = go.Figure()

# Add the moving average lines first
fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['EMA_21'], mode='lines', name='21 EMA', line=dict(color='cyan', width=1.5)))
fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['SMA_50'], mode='lines', name='50 SMA', line=dict(color='magenta', width=1.5)))
fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['SMA_200'], mode='lines', name='200 SMA', line=dict(color='yellow', width=2)))

# Add the main price line on top
fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['close'], mode='lines', name='TOTAL Market Cap', line=dict(color='white', width=2.5)))


# --- Logic to draw the background colors ---
# This replicates the bgcolor() effect from TradingView
current_color = regime_df['regime_color'].iloc[0]
start_date = regime_df.index[0]

for i in range(1, len(regime_df)):
    if regime_df['regime_color'].iloc[i] != current_color:
        # Add a rectangle for the previous color block
        fig.add_vrect(
            x0=start_date, x1=regime_df.index[i-1],
            fillcolor=current_color, opacity=0.5, layer="below", line_width=0,
        )
        # Start a new block
        start_date = regime_df.index[i]
        current_color = regime_df['regime_color'].iloc[i]

# Add the final colored block
fig.add_vrect(
    x0=start_date, x1=regime_df.index[-1],
    fillcolor=current_color, opacity=0.5, layer="below", line_width=0,
)


# --- Update Layout ---
fig.update_layout(
    height=800,
    yaxis_title="Market Cap (USD)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)


# --- Interpretation ---
with st.expander("How to interpret"):
    st.markdown("""
**Macro Traffic Light (Regime)**

What it shows:
- TOTAL price with 21 EMA, 50 SMA, and 200 SMA overlays.
- Background color = regime_color from indicators.calculate_traffic_light().

Reading the colors:
- Green → bullish regime (trend alignment, positive momentum).
- Yellow/Amber → neutral or corrective regime (mixed signals, consolidation).
- Red → bearish regime (negative momentum/trend).

Transitions:
- Green → Yellow → Red = deterioration. Rallies into MAs often fade in Red regimes.
- Red → Yellow → Green = improvement. Pullbacks to MAs often hold in Green regimes.

MA stack and price:
- Bullish bias when price > 21 EMA > 50 SMA > 200 SMA.
- Bearish bias when price < 21 EMA < 50 SMA < 200 SMA.
- 50/200 crosses (golden/death) hint at longer‑term regime changes.

Usage:
- Increase exposure in Green, reduce/hedge in Red, size down/manage risk in Yellow.
- Use with support/resistance and breadth; this is a regime filter, not a standalone signal.

Caveats:
- Expect whipsaws near flips; wait for confirmation or confluence.
""")