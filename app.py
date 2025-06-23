import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz


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
    

if st.button("Get Options Data"):
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

            st.dataframe(df, height=400)

    except IndexError:
        st.error(f"Maturity index {maturity} not available. Please try a lower number.")
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

st.caption("Data is typically delayed by 15 minutes and may be more delayed outside trading hours.")