import streamlit as st
from utils import load_all_data # Import from our new utils file

# --- Page Configuration ---
st.set_page_config(
    page_title="Crypto Macro Dashboard",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 Crypto Macro Indicators")
st.header("📈 Market Dashboard")

data = load_all_data()

if data is None:
    st.warning("Could not load data. Please ensure `crypto_data.db` exists and is populated.")
    st.stop()

# Display Key Metrics
col1, col2, col3 = st.columns(3)
btc_price = data['BTCUSD']['close'].iloc[-1]
total_mcap = data['TOTAL']['close'].iloc[-1]
btc_dom = data['BTC_D']['close'].iloc[-1]

col1.metric("BTC Price", f"${btc_price:,.2f}")
col2.metric("Total Market Cap", f"${total_mcap/1e12:.2f} T")
col3.metric("BTC Dominance", f"{btc_dom:.2f}%")

st.write("---")
st.info("Select an indicator from the sidebar to begin analysis.")
