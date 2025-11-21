import os
import time
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from typing import List, Optional

# Config 
st.set_page_config(page_title="CryptoBuddy Pro 🚀", page_icon="💰", layout="wide")

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

#Offline Dataset 
crypto_db = {
    "bitcoin": {"name": "Bitcoin", "symbol": "BTC", "trend": "rising 🚀", "sustainability": 3},
    "ethereum": {"name": "Ethereum", "symbol": "ETH", "trend": "stable ⚖️", "sustainability": 6},
    "cardano": {"name": "Cardano", "symbol": "ADA", "trend": "rising 📈", "sustainability": 8},
    "solana": {"name": "Solana", "symbol": "SOL", "trend": "volatile ⚡", "sustainability": 7},
    "ripple": {"name": "XRP", "symbol": "XRP", "trend": "stable ⚖️", "sustainability": 8},
}

# Helper Functions 
def _headers():
    headers = {"accept": "application/json"}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
    return headers

@st.cache_data(ttl=60)
def fetch_market(ids: Optional[List[str]] = None):
    """Fetches current market data for a list of coin IDs."""
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "sparkline": "false",
        "price_change_percentage": "24h,7d",
    }
    if ids:
        params["ids"] = ",".join(ids)
    try:
        r = requests.get(f"{COINGECKO_BASE}/coins/markets", headers=_headers(), params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

@st.cache_data(ttl=300) # Cache charts longer (5 mins)
def fetch_chart_data(coin_id: str, days: str = "7"):
    """Fetches historical price data for charting."""
    try:
        url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": days}
        r = requests.get(url, headers=_headers(), params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            prices = data.get("prices", [])
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        return None
    except Exception:
        return None

# UI & Logic

# Sidebar
with st.sidebar:
    st.header("⚙️ Dashboard Settings")
    mode = st.radio("Data Source", ["Rule-based", "Live (CoinGecko)"], index=1)
    
    st.divider()
    st.subheader("💼 Mini Portfolio")
    st.caption("Enter amount owned to track value:")
    
    portfolio_holdings = {}
    portfolio_value = 0.0
    
    # Portfolio Inputs
    for coin_id, meta in crypto_db.items():
        amount = st.number_input(f"{meta['symbol']} Holdings", min_value=0.0, step=0.1, key=f"hold_{coin_id}")
        if amount > 0:
            portfolio_holdings[coin_id] = amount

    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# Main Header
st.title("💰 CryptoBuddy Pro")
st.markdown("### Your AI-Powered Financial Sidekick & Analytics Dashboard")

# Initialize portfolio value in session state
if "portfolio_value" not in st.session_state:
    st.session_state.portfolio_value = 0.0

#Live Dashboard (Top Section)
if mode == "Live (CoinGecko)":
    ids = list(crypto_db.keys())
    market_data = fetch_market(ids)
    
    if market_data:
        # 1. Calculate Portfolio Value if holdings exist
        portfolio_value = 0.0
        if portfolio_holdings:
            for coin in market_data:
                cid = coin['id']
                if cid in portfolio_holdings:
                    value = coin['current_price'] * portfolio_holdings[cid]
                    portfolio_value += value
            
            st.session_state.portfolio_value = portfolio_value
            st.info(f"💼 **Total Portfolio Value:** ${portfolio_value:,.2f}")
        else:
            st.session_state.portfolio_value = 0.0

        # 2. Quick Metric Cards
        cols = st.columns(len(market_data))
        for i, coin in enumerate(market_data):
            with cols[i]:
                change = coin.get('price_change_percentage_24h', 0)
                st.metric(
                    label=coin['symbol'].upper(),
                    value=f"${coin['current_price']:,.2f}",
                    delta=f"{change:.2f}%"
                )
        
        # 3. Interactive Charting Section
        st.subheader("📈 Market Trends Analysis")
        selected_coin = st.selectbox("Select coin to view 7-day history:", [c['name'] for c in market_data])
        
        # Find ID for selected coin
        selected_id = next(c['id'] for c in market_data if c['name'] == selected_coin)
        
        chart_df = fetch_chart_data(selected_id)
        if chart_df is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=chart_df['timestamp'], y=chart_df['price'], mode='lines', name='Price', line=dict(color='#00CC96')))
            fig.update_layout(
                title=f"{selected_coin} Price History (7 Days)",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                margin=dict(l=20, r=20, t=40, b=20),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Chart data unavailable (API rate limit or network error).")
            
        # 4. Data Export
        st.subheader("📊 Raw Data Explorer")
        df = pd.DataFrame(market_data)
        # Clean up dataframe for display
        display_cols = ['name', 'symbol', 'current_price', 'market_cap', 'total_volume', 'price_change_percentage_24h']
        df_display = df[display_cols].copy()
        df_display.columns = ['Name', 'Symbol', 'Price ($)', 'Market Cap', 'Volume', '24h Change (%)']
        
        st.dataframe(df_display, use_container_width=True)
        
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Market Data (CSV)",
            csv,
            "crypto_market_data.csv",
            "text/csv",
            key='download-csv'
        )

    else:
        st.error("⚠️ Live data unavailable. API limit reached or offline. Switch to Rule-based mode.")
else:
    # Rule-based mode: reset portfolio value
    st.session_state.portfolio_value = 0.0

#Chat Interface (Bottom Section)
st.divider()
st.subheader("💬 AI Chat Advisor")

if "history" not in st.session_state:
    st.session_state.history = []

# Chat Logic
def generate_response(query, mode_type):
    query = query.lower()
    
    # Rule-based fallback
    if mode_type == "Rule-based":
        if "bitcoin" in query: return "Bitcoin is rising 🚀 with a sustainability score of 3/10."
        if "ethereum" in query: return "Ethereum is stable ⚖️ with a sustainability score of 6/10."
        if "sustainable" in query: return "Cardano (ADA) is currently our top pick for eco-friendliness!"
        return "I can tell you about Bitcoin, Ethereum, or sustainability trends. Try switching to Live mode for real data!"
    
    # Live Logic
    if mode_type == "Live (CoinGecko)":
        if "price" in query:
            return "Check the dashboard above for the latest live prices! 👆"
        if "portfolio" in query:
            pv = st.session_state.get("portfolio_value", 0.0)
            if pv > 0:
                return f"Your current portfolio value is estimated at ${pv:,.2f} based on the holdings in the sidebar."
            else:
                return "You haven't entered any holdings yet. Use the sidebar to add your crypto holdings and track your portfolio value!"
        if "recommend" in query:
            return "Based on current data, Cardano scores highest on sustainability, while Bitcoin has the highest volume."
    
    return "I'm your CryptoBuddy! Ask me about trends, prices, or your portfolio."

# Chat Input
user_input = st.chat_input("Ask a question (e.g., 'How is my portfolio?', 'Is Bitcoin sustainable?')")

if user_input:
    st.session_state.history.append(("You", user_input))
    response = generate_response(user_input, mode)
    st.session_state.history.append(("Bot", response))

# Display Chat
for role, text in st.session_state.history:
    if role == "You":
        st.chat_message("user").write(text)
    else:
        st.chat_message("assistant").write(text)