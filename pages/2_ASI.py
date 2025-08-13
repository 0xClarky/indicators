import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_all_data
from indicators import calculate_altcoin_season_index

st.set_page_config(page_title="ASI", layout="wide")
st.title("📊 TOTAL3: Altcoin Season Index (ASI)")
st.markdown(""" The ASI measures the momentum spread between altcoins and Bitcoin dominance. ASI = 1 day ROC (TOTAL3) - 1 day ROC (BTC.D), with a 30-day MA as a signal. """)

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

# --- Plot 1: TOTAL3 Price Chart (Top subplot) ---
fig.add_trace(go.Scatter(
    x=data['TOTAL3'].index,
    y=data['TOTAL3']['close'],
    mode='lines',
    name='TOTAL3 Market Cap'
), row=1, col=1)


# --- Plot 2: ASI Indicator (Bottom subplot) ---
asi_df = calculate_altcoin_season_index(data['TOTAL3'], data['BTC_D'])
colors = ['limegreen' if val >= 0 else 'tomato' for val in asi_df['asi_value']]
fig.add_trace(go.Bar(
    x=asi_df.index, 
    y=asi_df['asi_value'], 
    name='ASI Value', 
    marker_color=colors
), row=2, col=1)
fig.add_trace(go.Scatter(
    x=asi_df.index, 
    y=asi_df['signal_line'], 
    mode='lines', 
    name='Signal Line', 
    line=dict(color='orange', width=2)
), row=2, col=1)

# Add horizontal line to the second subplot
fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)


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
fig.update_yaxes(title_text="Momentum Spread", row=2, col=1, range=[-10, 10])

st.plotly_chart(fig, use_container_width=True)

# --- Interpretation ---
with st.expander("How to interpret"):
    st.markdown("""
**Altcoin Season Index (ASI)**

What it shows:
- ASI Value: Daily momentum spread = 1D ROC(TOTAL3) − 1D ROC(BTC.D).
- Signal Line: 30‑day moving average of ASI to smooth the regime.

How to use:
- Above 0 → Altcoins gaining share (risk‑on, alt‑led conditions).
- Below 0 → BTC dominance gaining (risk‑off or BTC‑led conditions).
- Stronger when ASI is above its Signal and rising; weaker when below and falling.

Crossovers:
- ASI crossing above the Signal from below → early alt‑season impulse.
- ASI crossing below the Signal → rotation back to BTC leadership.

Read the bars:
- Consecutive green bars above 0 and expanding → broadening alt participation and momentum.
- Red bars below 0 and deepening → narrowing market, BTC‑led or defensive posture.

Divergences:
- TOTAL3 rising while ASI falls → rally narrowing; risk of fade.
- TOTAL3 falling while ASI rises → early broadening under the surface.

Note:
- The zero line is balance; persistent readings far from 0 indicate stronger regime.
""")