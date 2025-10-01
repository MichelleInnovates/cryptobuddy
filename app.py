import os
import time
import requests
import streamlit as st
from typing import List, Optional

# -------------------- Config --------------------
st.set_page_config(page_title="CryptoBuddy 🤖", page_icon="💰", layout="wide")

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# -------------------- Offline Dataset --------------------
crypto_db = {
    "bitcoin": {"name": "Bitcoin", "symbol": "BTC", "trend": "rising 🚀", "sustainability": 3},
    "ethereum": {"name": "Ethereum", "symbol": "ETH", "trend": "stable ⚖️", "sustainability": 6},
    "cardano": {"name": "Cardano", "symbol": "ADA", "trend": "rising 📈", "sustainability": 8},
}

# -------------------- Rule-based Logic --------------------
def chatbot_logic(user_input: str) -> str:
    user_input = user_input.lower().strip()
    if not user_input:
        return "🤖 Ask about Bitcoin, Ethereum, Cardano, trends, or sustainability."

    if "sustainable" in user_input or "eco" in user_input or "green" in user_input:
        return "🌱 Cardano is the most eco-friendly crypto!"
    if "trend" in user_input or "trending" in user_input:
        return "📊 Bitcoin and Cardano are currently rising, while Ethereum is stable."
    if "bitcoin" in user_input:
        meta = crypto_db["bitcoin"]
        return f"Bitcoin is {meta['trend']} with sustainability score {meta['sustainability']}/10."
    if "ethereum" in user_input:
        meta = crypto_db["ethereum"]
        return f"Ethereum is {meta['trend']} and has a sustainability score of {meta['sustainability']}/10."
    if "cardano" in user_input:
        meta = crypto_db["cardano"]
        return f"Cardano is {meta['trend']} and scores {meta['sustainability']}/10 on sustainability."

    return "🤖 Hmm... I’m not sure. Try asking about Bitcoin, Ethereum, Cardano, trends, or sustainability."

# -------------------- Live Data (CoinGecko) --------------------
def _headers():
    headers = {"accept": "application/json"}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
    return headers

@st.cache_data(ttl=60)
def fetch_market(ids: Optional[List[str]] = None):
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

@st.cache_data(ttl=60)
def fetch_coin(coin_id: str):
    params = {
        "localization": "false",
        "tickers": "false",
        "community_data": "false",
        "developer_data": "false",
    }
    try:
        r = requests.get(f"{COINGECKO_BASE}/coins/{coin_id}", headers=_headers(), params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

# -------------------- UI Sidebar --------------------
with st.sidebar:
    st.header("⚙️ Settings")
    mode = st.radio("Mode", ["Rule-based", "Live (CoinGecko)"], index=0)
    st.caption("Live mode uses CoinGecko API and caches responses for 60s.")

    with st.expander("Shortcuts"):
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Trending", use_container_width=True):
                st.session_state.setdefault("history", []).append(("You", "Which crypto is trending?"))
                st.session_state.setdefault("pending_input", "Which crypto is trending?")
        with col_b:
            if st.button("Sustainable", use_container_width=True):
                st.session_state.setdefault("history", []).append(("You", "Which coin is most sustainable?"))
                st.session_state.setdefault("pending_input", "Which coin is most sustainable?")
        if st.button("Recommend", use_container_width=True):
            st.session_state.setdefault("history", []).append(("You", "Give me a recommendation"))
            st.session_state.setdefault("pending_input", "Give me a recommendation")

    st.divider()
    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.history = []
        st.session_state.pop("last_reco", None)
        st.session_state.pop("pending_input", None)
        st.cache_data.clear()

# -------------------- Header --------------------
st.title("💰 CryptoBuddy – Your AI Financial Sidekick 🤖")
st.write("Ask about crypto trends and sustainability. Live mode adds real-time prices.")
st.info("Disclaimer: Crypto is risky — always do your own research. This app is for educational purposes only.")

# -------------------- Chat Input --------------------
if "history" not in st.session_state:
    st.session_state.history = []

user_query = st.text_input("💬 Type your question:", value=st.session_state.pop("pending_input", ""))

# -------------------- Live Helpers --------------------
def live_trending_response():
    ids = list(crypto_db.keys())
    with st.spinner("Fetching trending coins..."):
        data = fetch_market(ids)
    if not data:
        return "❌ Unable to fetch live data. Try rule-based mode or later."
    trending = [c for c in data if (c.get("price_change_percentage_24h") or 0) > 0]
    trending.sort(key=lambda x: x.get("price_change_percentage_24h", 0), reverse=True)
    lines = ["📈 Trending (Live):"]
    for c in trending[:5]:
        lines.append(f"- {c['name']} ({c['symbol'].upper()}): ${c['current_price']:,.2f} | 24h {c.get('price_change_percentage_24h', 0):+.2f}%")
    if len(lines) == 1:
        lines.append("- No positive movers in the last 24h among selected coins.")
    return "\n".join(lines)

def live_recommendation_response():
    ids = list(crypto_db.keys())
    with st.spinner("Computing recommendation..."):
        data = fetch_market(ids)
    if not data:
        return "❌ Unable to fetch live data."
    best = None
    best_score = -1
    for c in data:
        score = 0
        change = c.get("price_change_percentage_24h", 0) or 0
        if change > 0:
            score += 3 + min(change * 0.1, 2)
        rank = c.get("market_cap_rank", 100)
        if rank <= 5:
            score += 2
        elif rank <= 15:
            score += 1
        # add sustainability from offline map if known
        sus = crypto_db.get(c["id"], {}).get("sustainability", None)
        if sus is not None:
            score += sus * 0.4
        if score > best_score:
            best, best_score = c, score
    if not best:
        return "❌ No recommendation available."
    reco = (f"🏆 Balanced pick (Live): {best['name']} ({best['symbol'].upper()})\n"
            f"Score: {best_score:.1f}/10 | Price: ${best['current_price']:,.2f} | 24h: {best.get('price_change_percentage_24h', 0):+.2f}%")
    st.session_state["last_reco"] = reco
    return reco

# -------------------- Compare UI --------------------
with st.expander("⚖️ Compare two coins"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        coin_a = st.selectbox("Coin A", list(crypto_db.keys()), format_func=lambda k: crypto_db[k]["name"])
    with col2:
        coin_b = st.selectbox("Coin B", list(crypto_db.keys()), index=1, format_func=lambda k: crypto_db[k]["name"])
    with col3:
        go = st.button("Compare")

    if go:
        if mode == "Live (CoinGecko)":
            with st.spinner("Fetching live comparison..."):
                a = fetch_coin(coin_a)
                b = fetch_coin(coin_b)
            if a and b:
                pa = a["market_data"]["current_price"]["usd"]
                pb = b["market_data"]["current_price"]["usd"]
                ca = a["market_data"].get("price_change_percentage_24h", 0) or 0
                cb = b["market_data"].get("price_change_percentage_24h", 0) or 0
                mca = a["market_data"]["market_cap"]["usd"]
                mcb = b["market_data"]["market_cap"]["usd"]
                st.success(f"{a['name']} vs {b['name']} (Live)\n\n"
                           f"Price: ${pa:,.2f} vs ${pb:,.2f}\n"
                           f"24h: {ca:+.2f}% vs {cb:+.2f}%\n"
                           f"Market Cap: ${mca:,.0f} vs ${mcb:,.0f}")
            else:
                st.error("Unable to fetch live comparison.")
        else:
            sa = crypto_db[coin_a]["sustainability"]
            sb = crypto_db[coin_b]["sustainability"]
            ta = crypto_db[coin_a]["trend"]
            tb = crypto_db[coin_b]["trend"]
            st.info(f"{crypto_db[coin_a]['name']} vs {crypto_db[coin_b]['name']} (Rule-based)\n\n"
                    f"Trend: {ta} vs {tb}\n"
                    f"Sustainability: {sa}/10 vs {sb}/10")

# -------------------- Quick Cards --------------------
st.subheader("🔎 Quick glance")
cols = st.columns(3)
for i, key in enumerate(crypto_db.keys()):
    with cols[i % 3]:
        box = st.container(border=True)
        with box:
            if mode == "Live (CoinGecko)":
                with st.spinner("Loading..."):
                    d = fetch_market([key])
                if d:
                    c = d[0]
                    st.markdown(f"**{c['name']} ({c['symbol'].upper()})**")
                    st.write(f"${c['current_price']:,.2f} | 24h {c.get('price_change_percentage_24h', 0):+.2f}%")
                else:
                    st.markdown(f"**{crypto_db[key]['name']}**")
                    st.write("Live data unavailable")
            else:
                st.markdown(f"**{crypto_db[key]['name']} ({crypto_db[key]['symbol']})**")
                st.write(f"{crypto_db[key]['trend']} | Sustainability {crypto_db[key]['sustainability']}/10")

# -------------------- Chat Flow --------------------
if user_query:
    if mode == "Live (CoinGecko)":
        # Map common intents to live responses
        q = user_query.lower()
        if "trend" in q or "trending" in q:
            answer = live_trending_response()
        elif "recommend" in q or "best" in q or "balanced" in q or "invest" in q:
            answer = live_recommendation_response()
        else:
            # Fallback to rule-based phrasing when no specific live intent
            answer = chatbot_logic(user_query)
    else:
        answer = chatbot_logic(user_query)

    st.session_state.history.append(("You", user_query))
    st.session_state.history.append(("CryptoBuddy", answer))

# Display chat history
st.subheader("💬 Chat")
for speaker, message in st.session_state.history:
    if speaker == "You":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 CryptoBuddy:** {message}")

# Copy last recommendation
colx, coly = st.columns([1, 3])
with colx:
    if st.button("📋 Copy last recommendation"):
        if st.session_state.get("last_reco"):
            st.code(st.session_state["last_reco"])
        else:
            st.warning("No recommendation yet — ask for one!") 