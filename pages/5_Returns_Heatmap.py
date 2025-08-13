import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import load_all_data

st.set_page_config(page_title="Returns Heatmap", layout="wide")
st.title("📊 Monthly Returns Heatmap")
st.markdown(""" The Monthly Returns Heatmap visualizes each month's percent return (using month-end closes) across years for a selected asset, highlighting streaks, seasonality, and extremes. """)


# --- Data Loading ---
data = load_all_data()
if data is None:
    st.stop()

# Define asset options first
asset_options = list(data.keys())
# Use a session state to remember the selection, or set a default
if 'selected_asset' not in st.session_state:
    st.session_state.selected_asset = asset_options[0]

# --- Data Processing Function ---
def calculate_monthly_returns_grid(daily_prices_df):
    """
    Transforms a DataFrame of daily prices into a pivot table of monthly returns.
    """
    monthly_close = daily_prices_df['close'].resample('M').last()
    monthly_returns = monthly_close.pct_change() * 100
    
    heatmap_data = pd.pivot_table(
        pd.DataFrame(monthly_returns), 
        values='close', 
        index=monthly_returns.index.year, 
        columns=monthly_returns.index.month
    )
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    heatmap_data.columns = [month_names[col-1] for col in heatmap_data.columns]
    
    return heatmap_data

# --- Charting ---

# Use the selected asset from session state to generate the chart
returns_grid = calculate_monthly_returns_grid(data[st.session_state.selected_asset])

# --- THIS IS THE CHANGE: Define a better colorscale ---
# This custom scale goes from a deep red to a dark gray to a vibrant green.
custom_colorscale = [
    [0.0, 'rgb(200, 0, 0)'],      # Strong red for negative returns
    [0.5, 'rgb(40, 40, 40)'],     # Dark gray for zero returns
    [1.0, 'rgb(0, 200, 0)']       # Strong green for positive returns
]

# Create the heatmap figure
fig = go.Figure(data=go.Heatmap(
    z=returns_grid.values,
    x=returns_grid.columns,
    y=returns_grid.index,
    colorscale=custom_colorscale, # Use our new custom scale
    zmid=0,
    text=returns_grid.values,
    texttemplate="%{text:.2f}%",
    textfont={"size":12, "color":"white"}
))

fig.update_layout(
    title=f"{st.session_state.selected_asset} Monthly Returns Heatmap (%)",
    height=800,
    yaxis_title="Year",
    yaxis_autorange='reversed'
)

# Display the chart first
st.plotly_chart(fig, use_container_width=True)

# --- Asset Selection (Moved to the bottom) ---
# Now, display the selectbox below the chart. Its value will be used on the next script run.
selected = st.selectbox(
    "Select Asset:",
    asset_options,
    index=asset_options.index(st.session_state.selected_asset) # Set current selection
)

# If the selection changes, update the state and rerun the script
if selected != st.session_state.selected_asset:
    st.session_state.selected_asset = selected
    st.rerun()

# --- Interpretation ---
with st.expander("How to interpret"):
    st.markdown("""
**Monthly Returns Heatmap**

What it shows:
- Each cell is the monthly return (%) using month-end close.
- Rows = years; columns = months. Colors: red (negative), gray (near 0), green (positive).
- The number in each cell is the exact monthly % change.

How to read:
- Horizontal streaks of green/red indicate persistent trends across months.
- Compare current month to history for context; extreme greens can signal overextension, deep reds can mark capitulation.
- Check seasonality patterns: months that repeatedly skew positive/negative for the selected asset.

Notes:
- The current month is partial until month-end; early readings can change.
- Early data rows may include partial first/last months depending on data availability.
- Switch assets with the selector to compare regimes and seasonality across markets.
""")
