import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

# Configure page
st.set_page_config(page_title="Options Market Data", layout="wide")

# Enable iframe embedding
st.markdown("""
<script>
// Allow iframe embedding
if (window.location !== window.parent.location) {
    document.domain = document.domain;
}
// Remove X-Frame-Options restrictions
window.addEventListener('load', function() {
    if (window.parent !== window) {
        console.log('Running in iframe - embedding allowed');
    }
});
</script>
""", unsafe_allow_html=True)

# CSS for responsive iframe scaling
st.markdown("""
<style>
/* Make the entire app responsive */
.main .block-container {
    max-width: 100% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Scale content to fit iframe */
.stApp {
    transform-origin: top left;
    width: 100%;
}

/* Ensure plots scale properly */
.js-plotly-plot {
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)


# Top control area
with st.container():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", value="AAPL")
    
    with col2:
        kind = st.selectbox("Option Type", ["call", "put"])
    
    with col3:
        maturity = st.number_input("Maturity Index", min_value=0, max_value=10, value=4, 
                                  help="Option maturity in order of maturities trading")

# Center the button below the controls
_, btn_col, _ = st.columns([1, 1, 1])
with btn_col:
    get_data = st.button("Get Options Data")

if get_data:
    try:
        with st.spinner(f"Fetching {kind} options data for {ticker.upper()}..."):
            est = pytz.timezone('US/Eastern')
            fmt = '%Y-%m-%d %H:%M:%S'
            now = datetime.today().astimezone(est).strftime(fmt)

            tick = yf.Ticker(ticker.upper())

            # Pull last stock price
            close = tick.history().iloc[-1].Close

            # Get maturity date
            date = tick.options[maturity]

            # Pull options data
            df = (
                tick.option_chain(date).calls
                if kind == "call"
                else tick.option_chain(date).puts
            )

            df.lastTradeDate = df.lastTradeDate.map(
                lambda x: x.astimezone(est).strftime(fmt)
            )

            # Formatting
            cols = [
                "strike",
                "bid",
                "ask",
                "lastPrice",
                "lastTradeDate",
                "volume",
                "openInterest",
            ]
            df = df[cols]
           
            df.columns = [
                "Strike",
                "Bid",
                "Ask",
                "Last Price",
                "Time of Last Trade",
                "Volume",
                "Open Interest",
            ] 
            df = df.set_index("Strike")

            # Display results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Maturity Date", date)
            with col2:
                st.metric(f"Last {ticker.upper()} Price", f"${close:.2f}")
            with col3:
                st.metric("Data Updated", now)

            st.dataframe(df, use_container_width=True)

    except IndexError:
        st.error(f"Maturity index {maturity} not available. Please try a lower number.")
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

st.caption("Data is typically delayed by 15 minutes and will be more delayed outside trading hours.")