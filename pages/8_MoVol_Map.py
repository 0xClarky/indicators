import streamlit as st
import plotly.graph_objects as go
from utils import load_all_data as load_main_data
from indicators import calculate_market_character
import sqlite3
import pandas as pd

# --- Data Loader for A/D Line Assets ---
@st.cache_data(ttl=3600)
def load_ad_line_data():
    """Loads all asset data from the separate ad_line_data.db."""
    db_file = "ad_line_data.db"
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()
        
        if not tables: return None
        data = {}
        for table_name in tables:
            df = pd.read_sql(f'SELECT * FROM "{table_name}"', conn, index_col='datetime')
            df.index = pd.to_datetime(df.index)
            df = df[df.index >= '2019-01-01']
            data[table_name] = df
        return data
    except Exception as e:
        st.error(f"Error reading A/D Line database: {e}")
        return None
    finally:
        if 'conn' in locals() and conn: conn.close()

# --- Page Setup ---
st.set_page_config(page_title="MoVol Map", layout="wide")
st.title("📊 Momentum-Volatility Quandrant Map (MoVol)")
st.markdown(""" The MoVol Map plots each asset by 30-day momentum (ROC %) versus 30-day annualized volatility, colored by momentum to reveal regime and dispersion, into four quadrants: ideal uptrend, speculative frenzy, capitulation/fear, and boring/stable.""")

# --- Load Data & Calculate ---
ad_data = load_ad_line_data()
if ad_data is None:
    st.warning("Could not load asset data. Please ensure `ad_line_data.db` exists.")
    st.stop()

character_df = calculate_market_character(ad_data)

# --- Charting ---
fig = go.Figure()

# Add the scatter plot trace for the assets
fig.add_trace(go.Scatter(
    x=character_df['volatility'],
    y=character_df['momentum'],
    mode='markers+text',
    text=character_df.index,
    textposition='top center',
    marker=dict(size=12, color=character_df['momentum'], colorscale='RdYlGn', showscale=True, colorbar=dict(title="Momentum (%)")),
    hoverinfo='text'
))

# --- Define and draw the quadrants ---
# Use the median values as dynamic dividers
x_divider = character_df['volatility'].median()
y_divider = character_df['momentum'].median()

fig.add_vline(x=x_divider, line_width=1, line_dash="dash", line_color="gray")
fig.add_hline(y=y_divider, line_width=1, line_dash="dash", line_color="gray")

# --- Layout ---
fig.update_layout(
    height=800,
    xaxis_title="30-Day Volatility (Annualized)",
    yaxis_title="30-Day Momentum (ROC %)",
    showlegend=False
)

# Add annotations for quadrant labels
fig.add_annotation(x=0.02, y=0.98, xref="paper", yref="paper", text="Ideal Uptrend", showarrow=False, font=dict(color="lightgreen"))
fig.add_annotation(x=0.98, y=0.98, xref="paper", yref="paper", text="Speculative Frenzy", showarrow=False, font=dict(color="yellow"))
fig.add_annotation(x=0.02, y=0.02, xref="paper", yref="paper", text="Boring / Stable", showarrow=False, font=dict(color="orange"))
fig.add_annotation(x=0.98, y=0.02, xref="paper", yref="paper", text="Capitulation / Fear", showarrow=False, font=dict(color="tomato"))


st.plotly_chart(fig, use_container_width=True)

# --- Interpretation ---
with st.expander("How to interpret"):
    st.markdown("""
**Market Character (Momentum vs. Volatility)**

What it shows:
- Each point = an asset.
- X = 30‑day volatility (annualized); Y = 30‑day momentum (ROC %).
- Color = momentum (RdYlGn). Dashed lines = median vol/momentum dividers.

Quadrants:
- Top‑Left (low vol, high mom): Ideal Uptrend — strong and stable.
- Top‑Right (high vol, high mom): Speculative Frenzy — strong but unstable.
- Bottom‑Right (high vol, low/neg mom): Capitulation/Fear — stressed regime.
- Bottom‑Left (low vol, low/neg mom): Boring/Stable — grind or consolidation.

How to use:
- Leadership: favor assets with high momentum and moderate/declining volatility.
- Risk: many points in Bottom‑Right → defensive posture; in Top‑Left → risk‑on.
- Rotation: watch assets migrating between quadrants over time for regime shifts.

Notes:
- Momentum/volatility computed per calculate_market_character; medians are dynamic and dataset‑dependent.
- Asset universe and data gaps affect dispersion and medians.
""")