# CryptoBuddy Pro 🚀 – Your AI Financial Sidekick & Dashboard

A comprehensive cryptocurrency advisor that combines an AI-powered chatbot with a professional analytics dashboard. Now features interactive charts, portfolio tracking, and live data export.

## 🌟 New Pro Features
- **Interactive Market Charts:** Visualise 7-day price trends with zoomable interactive graphs (powered by Plotly).
- **Personal Portfolio Tracker:** Input your holdings to see your real-time total portfolio value.
- **Data Export:** Download live market data as a CSV file for your own analysis.
- **Live Dashboard:** Real-time metric cards for top cryptocurrencies.
- **Smart Chat:** AI advisor aware of your portfolio context and market trends.

## ⚡ Standard Features
- **Hybrid Modes:** Switch between "Live" (CoinGecko API) and "Rule-based" (Offline) modes.
- **Sustainability Insights:** ESG scores, energy usage, and consensus mechanism details.
- **Comparison Tool:** Compare coins side-by-side.
- **CLI Version:** A lightweight command-line interface for quick checks.

## 📦 Requirements
See `requirements.txt` for pinned versions.
* **Core:** `requests`, `streamlit`
* **Analytics & Viz:** `pandas`, `plotly`

## 🚀 Installation

```bash
# 1. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies (now includes pandas & plotly)
pip install -r requirements.txt
🔑 Environment Setup
Optionally set a CoinGecko API key (a demo key is used by default, which has rate limits):

Bash

export COINGECKO_API_KEY=your_key_here
🖥️ Running the Web App (Recommended)
The Streamlit app contains the new Pro Dashboard features.

Bash

streamlit run app.py
Open the URL: Usually http://localhost:8501

Portfolio: Open the Sidebar (left) to enter your crypto holdings.

Charts: Select a coin in the "Market Trends Analysis" section to view its history.

Export: Scroll to "Raw Data Explorer" to download the CSV.

📟 Running the CLI (Legacy)
The command-line tool is still available for text-only interactions:

Bash

python crypto_buddy.py
🛠️ Troubleshooting
"Module not found: pandas/plotly": Ensure you re-ran pip install -r requirements.txt after the update.

API Rate Limits: If charts or data stop loading, wait 60 seconds (the cache will clear) or switch to "Rule-based" mode in the sidebar.

Urllib3 errors: If you see SSL warnings, try pip install urllib3==2.2.3.

🤖 Optional: ChatterBot
The CLI version supports ChatterBot for small talk. This is optional and not required for the Web Dashboard.

Bash

python3 -m pip install chatterbot==1.0.8 chatterbot-corpus==1.2.0 SQLAlchemy==1.4.46 pytz