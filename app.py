import streamlit as st
import yfinance as yf
import google.generativeai as genai
import plotly.graph_objects as go
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="AI Pro Stock Dashboard", layout="wide")

# --- 100 Popular Companies Data (S&P 100) ---
SP100_STOCKS = {
    "Nvidia": "NVDA", "Apple": "AAPL", "Microsoft": "MSFT", "Amazon": "AMZN",
    "Alphabet (Google A)": "GOOGL", "Alphabet (Google C)": "GOOG", "Meta (Facebook)": "META",
    "Tesla": "TSLA", "Berkshire Hathaway": "BRK-B", "JPMorgan Chase": "JPM",
    "Eli Lilly": "LLY", "Broadcom": "AVGO", "Visa": "V", "Exxon Mobil": "XOM",
    "UnitedHealth": "UNH", "Mastercard": "MA", "Johnson & Johnson": "JNJ",
    "Procter & Gamble": "PG", "Home Depot": "HD", "Costco": "COST",
    "AbbVie": "ABBV", "Chevron": "CVX", "Bank of America": "BAC", "Walmart": "WMT",
    "Salesforce": "CRM", "Netflix": "NFLX", "Coca-Cola": "KO", "PepsiCo": "PEP",
    "Adobe": "ADBE", "Oracle": "ORCL", "McDonald's": "MCD", "Accenture": "ACN",
    "Disney": "DIS", "T-Mobile": "TMUS", "Cisco": "CSCO", "Verizon": "VZ",
    "Intel": "INTC", "Comcast": "CMCSA", "Amgen": "AMGN", "Boeing": "BA",
    "Goldman Sachs": "GS", "IBM": "IBM", "Pfizer": "PFE", "Texas Instruments": "TXN",
    "Morgan Stanley": "MS", "Honeywell": "HON", "Intuit": "INTU", "CVS Health": "CVS",
    "Lowe's": "LOW", "Starbucks": "SBUX", "Qualcomm": "QCOM", "ServiceNow": "NOW",
    "Nike": "NKE", "BlackRock": "BLK", "Gilead Sciences": "GILD", "Union Pacific": "UNP",
    "Lockheed Martin": "LMT", "Medtronic": "MDT", "Caterpillar": "CAT", "UPS": "UPS",
    "American Express": "AXP", "Intuitive Surgical": "ISRG", "Palo Alto Networks": "PANW",
    "Chipotle": "CMG", "TJX Companies": "TJX", "NextEra Energy": "NEE", "Progressive": "PGR",
    "Regeneron": "REGN", "General Electric": "GE", "Uber": "UBER", "Marsh & McLennan": "MMC",
    "ConocoPhillips": "COP", "Booking Holdings": "BKNG", "HCA Healthcare": "HCA",
    "Automatic Data Processing": "ADP", "Southern Company": "SO", "Eaton": "ETN",
    "Vertex Pharmaceuticals": "VRTX", "3M": "MMM", "Ford": "F", "General Motors": "GM",
    "FedEx": "FDX", "Target": "TGT", "Freeport-McMoRan": "FCX", "MetLife": "MET",
    "Colgate-Palmolive": "CL", "Altria": "MO", "General Dynamics": "GD", "AIG": "AIG",
    "Emerson Electric": "EMR", "U.S. Bancorp": "USB", "Charles Schwab": "SCHW",
    "PayPal": "PYPL", "Palantir": "PLTR", "Airbnb": "ABNB", "Adobe": "ADBE"
}

# --- Sidebar: Configuration & Inputs ---
with st.sidebar:
    st.title("⚙️ Trading Terminal")
    
    # 1. API Key Section
    gemini_key = st.text_input("🔑 Gemini API Key", type="password")
    if gemini_key:
        genai.configure(api_key=gemini_key)
    
    st.divider()

    # 2. Company Directory (Select Box)
    st.subheader("🏢 Company Directory")
    selected_name = st.selectbox(
        "Search or Select a Company",
        options=["Manual Entry"] + list(SP100_STOCKS.keys())
    )

    # 3. Ticker Entry (Overrides if "Manual Entry" is selected)
    if selected_name == "Manual Entry":
        ticker_symbol = st.text_input("Enter Ticker Symbol", value="NVDA").upper()
    else:
        ticker_symbol = SP100_STOCKS[selected_name]
        st.info(f"Ticker: {ticker_symbol}")

    # 4. Settings
    st.subheader("📅 Parameters")
    period = st.selectbox("Time Frame", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
    
    st.subheader("🛠️ Analysis Tools")
    show_sma = st.checkbox("20-Day SMA")
    show_ema = st.checkbox("50-Day EMA")
    show_volume = st.checkbox("Show Volume", value=True)

# --- Main Dashboard Area ---
if ticker_symbol:
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period=period)
        info = stock.info

        if df.empty:
            st.error("Ticker not found. Please verify the symbol.")
        else:
            # Metrics Row
            curr_price = df['Close'].iloc[-1]
            change = curr_price - df['Close'].iloc[-2]
            
            st.title(f"{info.get('longName', ticker_symbol)}")
            st.metric("Price", f"${curr_price:.2f}", f"{change:.2f}")

            # Chart Tools Integration
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="Candlestick"
            ))

            if show_sma:
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), name="SMA 20"))
            if show_ema:
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(50).mean(), name="EMA 50"))

            fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=True)
            st.plotly_chart(fig, use_container_width=True)

            # AI Insights
            if st.button("🧠 Analyze Market Trend"):
                if not gemini_key:
                    st.warning("Enter API key in sidebar.")
                else:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"Analyze {ticker_symbol} price action: {df.tail(10).to_string()}")
                    st.success(response.text)

    except Exception as e:
        st.error(f"Error loading data: {e}")
