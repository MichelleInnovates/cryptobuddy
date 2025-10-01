# CryptoBuddy  Your AI-Powered Cryptocurrency Advisor

Friendly rule-based chatbot with optional ChatterBot conversation and CoinGecko live data.

## Features
- Live prices and market data (CoinGecko) when online
- Rule-based offline fallback using a predefined dataset
- Sustainability insights (energy use, consensus, scores)
- Compare coins, trending coins, long-term picks, and a balanced recommendation
- Optional ChatterBot training for small talk

## Requirements
See `requirements.txt` for pinned versions. Minimal run requires only `requests`.

## Installation
```bash
# Create virtual env (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# Install minimal or full
pip install -r requirements.txt
```

## Environment
Optionally set a CoinGecko API key (a demo key is used by default):
```bash
export COINGECKO_API_KEY=your_key_here
```

## Run
```bash
python crypto_buddy.py
```

Pass `install` to print quick install notes:
```bash
python crypto_buddy.py install
```

## Example Prompts
- What's the price of Bitcoin?
- Which crypto is trending?
- What's the most sustainable coin?
- Best for long-term growth?
- Compare Bitcoin and Ethereum
- Show all cryptocurrencies
- Give me a recommendation

## Offline Fallback
If the API or internet is unavailable, CryptoBuddy answers using a small built-in dataset with rule-based logic so you can still complete the assignment and demo.

## For the PLP Assignment
Include in your repo:
- `crypto_buddy.py` (main bot)
- `requirements.txt`
- `README.md` with screenshots of a short conversation

Submission checklist:
- Record ~30s screen capture interacting with the bot
- Add a 50-word summary: "How does this chatbot mimic basic AI decision-making?"
- Push to GitHub and share the repo link

## Troubleshooting
- If ChatterBot fails to install, you can still run in rule-based mode (requests only)
- Ensure internet access for live data
- If rate-limited, try again later or rely on offline responses 

## Streamlit Web App
Run the lightweight UI:
```bash
pip install -r requirements.txt  # ensures streamlit is installed
streamlit run app.py
```

Open the URL printed in the terminal (usually http://localhost:8501). Type questions like:
- "Which crypto is trending?"
- "Which coin is most sustainable?"
- "Bitcoin" 

## Streamlit Features (app.py)
- Clear chat button and quick prompts (Trending, Sustainable, Recommend)
- Mode switch: Rule-based vs Live (CoinGecko, cached 60s)
- Compare two coins (live or rule-based)
- Quick glance cards for BTC/ETH/ADA
- Copy last recommendation button

## Run Streamlit on a different port
```bash
streamlit run app.py --server.port 8502
```

## Troubleshooting (common)
- urllib3 missing: install via `python3 -m pip install urllib3==2.2.3`
- ChatterBot optional: if install fails, the CLI still runs in rule-based mode
- Rate limit/API errors: wait 60s (cache TTL) or switch to Rule-based mode
- pyenv/venv: ensure you install packages with the same interpreter used to run

## Optional: ChatterBot (CLI conversational extras)
ChatterBot is not installed by default because compatible wheels are often unavailable on some Python versions (e.g., 3.8 in some environments). The CLI (`crypto_buddy.py`) works without it using rule-based logic and live data.

If you want to try ChatterBot, install separately (may require specific environments):
```bash
python3 -m pip install chatterbot==1.0.8 chatterbot-corpus==1.2.0 SQLAlchemy==1.4.46 pytz
```
If installation fails, skip it — the bot runs fine without it.

## 50-word summary (template)
This chatbot mimics basic AI by mapping user intents to decision rules and combining simple heuristics with optional live market data. It scores coins using trend, market rank, and sustainability to produce recommendations. A conversational layer is optional; the core uses deterministic logic to provide consistent, explainable advice. 