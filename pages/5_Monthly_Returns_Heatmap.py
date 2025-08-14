import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_data
from config import MACRO_SYMBOLS

# --- Page Configuration ---
st.set_page_config(page_title="Returns Heatmap", layout="wide")
st.title("📅 Monthly Returns Heatmap")

# --- Data Loading ---
# --- THIS IS THE FIX ---
# We now correctly pass the dictionary *values* (the table names) to the loader.
data = load_data(asset_list=list(MACRO_SYMBOLS.values()))

if data is None:
    st.warning("Could not load the required data. Please run the data updater scripts.")
    st.stop()

# --- UI Controls: Asset Selection ---
asset_options = list(data.keys())
selected_asset = st.selectbox(
    "Select an Asset to Analyze:",
    asset_options,
    index=asset_options.index('BTCUSDT') if 'BTCUSDT' in asset_options else 0 # Default to BTC
)

# --- Data Processing Function ---
def calculate_monthly_returns_grid(daily_prices_df):
    """Transforms a DataFrame of daily prices into a pivot table of monthly returns."""
    monthly_close = daily_prices_df['close'].resample('M').last()
    monthly_returns = monthly_close.pct_change() * 100
    
    heatmap_data = pd.pivot_table(
        pd.DataFrame(monthly_returns), 
        values='close', 
        index=monthly_returns.index.year, 
        columns=monthly_returns.index.month
    )
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    heatmap_data.columns = [month_names[col-1] for col in heatmap_data.columns]
    
    return heatmap_data

# --- Charting ---
returns_grid = calculate_monthly_returns_grid(data[selected_asset])

custom_colorscale = [
    [0.0, 'rgb(200, 0, 0)'],
    [0.5, 'rgb(40, 40, 40)'],
    [1.0, 'rgb(0, 200, 0)']
]

fig = go.Figure(data=go.Heatmap(
    z=returns_grid.values,
    x=returns_grid.columns,
    y=returns_grid.index,
    colorscale=custom_colorscale,
    zmid=0,
    text=returns_grid.values,
    texttemplate="%{text:.2f}%",
    textfont={"size":12, "color":"white"}
))

fig.update_layout(
    height=600,
    title=f"{selected_asset} Monthly Returns (%)",
    yaxis_title="Year",
    yaxis_autorange='reversed',
    plot_bgcolor='rgba(17, 17, 17, 1)'
)

st.plotly_chart(fig, use_container_width=True)


# --- Indicator Explanation (Always visible) ---
st.markdown("---")
st.header(f"How to Interpret the {selected_asset} Heatmap")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚙️ How It's Computed")
    st.markdown("""
    This heatmap visualizes the percentage return for each calendar month. The calculation is straightforward:
    1.  First, the closing price at the **end of each month** is identified.
    2.  Then, the percentage change between each month-end close and the previous one is calculated.
    
    The value in each cell represents that specific month's performance.
    """)
    st.latex(r'''
    \text{Return} = \left( \frac{\text{End Price} - \text{Start Price}}{\text{Start Price}} \right) \times 100
    ''')

with col2:
    st.subheader("🎯 How to Read It")
    st.markdown("""
    The heatmap allows for the quick identification of historical patterns and performance characteristics.

    - **<font color='lightgreen'>🟢 Seasonality</font>**: Look for columns (months) that are consistently green or red across the years. This can reveal potential seasonal tendencies for the asset.

    - **<font color='white'>⚪ Streaks</font>**: Horizontal runs of green or red cells show periods of sustained positive or negative performance, helping you understand momentum.

    - **<font color='orange'>🟠 Volatility</font>**: Cells with very high (bright green) or very low (bright red) numbers highlight periods of extreme volatility. Months that are consistently gray (close to 0%) indicate stability.
    """, unsafe_allow_html=True)