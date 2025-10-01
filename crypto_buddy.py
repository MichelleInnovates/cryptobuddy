import os
import sys
import json
import requests
from datetime import datetime

# Optional: ChatterBot fallback if available
try:
    from chatterbot import ChatBot
    from chatterbot.trainers import ListTrainer
    CHATTERBOT_AVAILABLE = True
except Exception:
    CHATTERBOT_AVAILABLE = False


class CryptoBuddy:
    def __init__(self):
        self.name = "CryptoBuddy"
        self.api_key = os.getenv("COINGECKO_API_KEY", "")  # No hardcoded key - use environment variable
        self.base_url = "https://api.coingecko.com/api/v3"

        # Map friendly names to CoinGecko IDs
        self.crypto_ids = {
            "Bitcoin": "bitcoin",
            "Ethereum": "ethereum",
            "Cardano": "cardano",
            "Solana": "solana",
            "Ripple": "ripple",
            "BNB": "binancecoin",
            "Dogecoin": "dogecoin",
            "Polkadot": "polkadot",
        }

        # Sustainability and consensus data (curated)
        self.sustainability_data = {
            "bitcoin": {"energy_use": "high", "sustainability_score": 3, "consensus": "Proof of Work"},
            "ethereum": {"energy_use": "low", "sustainability_score": 8, "consensus": "Proof of Stake"},
            "cardano": {"energy_use": "low", "sustainability_score": 9, "consensus": "Proof of Stake"},
            "solana": {"energy_use": "low", "sustainability_score": 7, "consensus": "Proof of Stake"},
            "ripple": {"energy_use": "low", "sustainability_score": 8, "consensus": "Federated Consensus"},
            "binancecoin": {"energy_use": "low", "sustainability_score": 6, "consensus": "Proof of Stake"},
            "dogecoin": {"energy_use": "high", "sustainability_score": 3, "consensus": "Proof of Work"},
            "polkadot": {"energy_use": "low", "sustainability_score": 8, "consensus": "Nominated Proof of Stake"},
        }

        # Offline dataset for rule-based fallback
        self.offline_db = {
            "Bitcoin": {
                "price_trend": "rising",
                "market_cap": "high",
                "energy_use": "high",
                "sustainability_score": 3,
            },
            "Ethereum": {
                "price_trend": "stable",
                "market_cap": "high",
                "energy_use": "low",
                "sustainability_score": 8,
            },
            "Cardano": {
                "price_trend": "rising",
                "market_cap": "medium",
                "energy_use": "low",
                "sustainability_score": 9,
            },
        }

        self.chatbot = None
        if CHATTERBOT_AVAILABLE:
            try:
                self.chatbot = ChatBot(
                    "CryptoBuddy",
                    storage_adapter="chatterbot.storage.SQLStorageAdapter",
                    database_uri="sqlite:///cryptobuddy.db",
                    logic_adapters=[
                        {
                            "import_path": "chatterbot.logic.BestMatch",
                            "default_response": "I'm not sure about that. Try asking about trending coins, prices, sustainability, or investment advice!",
                            "maximum_similarity_threshold": 0.90,
                        }
                    ],
                )
                self._train_chatbot()
            except Exception:
                # If ChatterBot fails to init, stay in rule-based mode
                self.chatbot = None

    def _train_chatbot(self):
        if not self.chatbot:
            return
        trainer = ListTrainer(self.chatbot)
        training_data = [
            "Hello",
            "Hi! I'm CryptoBuddy, your crypto advisor with REAL-TIME data!",
            "Hi",
            "Hey there! Ready to explore live cryptocurrency prices?",
            "Hey",
            "Hello! Let's find you the perfect crypto investment!",
            "What's the price of Bitcoin?",
            "Let me fetch the current Bitcoin price for you!",
            "Show me crypto prices",
            "I'll get you the latest cryptocurrency prices!",
            "Which crypto is trending?",
            "Let me show you the trending cryptocurrencies from the market!",
            "What's the most sustainable coin?",
            "I'll find you the greenest crypto option!",
            "Compare Bitcoin and Ethereum",
            "I'll compare these cryptocurrencies with live data!",
            "Help",
            "I can help with live prices, trends, sustainability, comparisons, and advice!",
            "Bye",
            "Goodbye! Stay green and grow your wealth!",
        ]
        trainer.train(training_data)

    def greet(self):
        print("\n" + "=" * 70)
        print(f"\U0001F44B Hey there! I'm {self.name}, your crypto sidekick!")
        print("I use REAL-TIME data from CoinGecko API when available.")
        print("Get live prices, market trends, and sustainability insights!")
        print("=" * 70 + "\n")

    # -------------------- Live Data Helpers --------------------
    def _fetch(self, url, params=None):
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key
        try:
            res = requests.get(url, headers=headers, params=params or {}, timeout=10)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception:
            return None

    def fetch_coin_data(self, coin_id):
        url = f"{self.base_url}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "false",
            "developer_data": "false",
        }
        return self._fetch(url, params)

    def fetch_market_data(self):
        url = f"{self.base_url}/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": ",".join(self.crypto_ids.values()),
            "order": "market_cap_desc",
            "sparkline": "false",
            "price_change_percentage": "24h,7d",
        }
        return self._fetch(url, params)

    # -------------------- Features --------------------
    def get_price(self, crypto_name):
        if crypto_name.title() not in self.crypto_ids:
            return f"\n			Sorry, I don't have data for {crypto_name}. Try: {', '.join(self.crypto_ids.keys())}\n"
        coin_id = self.crypto_ids[crypto_name.title()]
        data = self.fetch_coin_data(coin_id)
        if not data:
            # Offline fallback
            return self._offline_price(crypto_name.title())

        try:
            price = data["market_data"]["current_price"]["usd"]
            change_24h = data["market_data"]["price_change_percentage_24h"]
            market_cap = data["market_data"]["market_cap"]["usd"]
            volume = data["market_data"]["total_volume"]["usd"]
            response = f"\n			{data['name']} ({data['symbol'].upper()}) - LIVE DATA\n"
            response += "-" * 70 + "\n"
            response += f"   Current Price: ${price:,.2f}\n"
            response += (
                f"   24h Change:  {change_24h:+.2f}%\n".replace("\u000f", "\U0001F4C8" if change_24h and change_24h > 0 else "\U0001F4C9")
            )
            response += f"   Market Cap: ${market_cap:,.0f}\n"
            response += f"   24h Volume: ${volume:,.0f}\n"
            if coin_id in self.sustainability_data:
                sus = self.sustainability_data[coin_id]
                response += f"\n   			Sustainability: {sus['sustainability_score']}/10\n"
                response += f"   			Energy Use: {sus['energy_use'].upper()}\n"
                response += f"   			Consensus: {sus['consensus']}\n"
            response += "\n"
            return response
        except Exception as e:
            return f"\n			Error parsing price data: {e}\n"

    def find_trending(self):
        market_data = self.fetch_market_data()
        if not market_data:
            return self._offline_trending()
        trending = [c for c in market_data if c.get("price_change_percentage_24h", 0) > 0]
        trending.sort(key=lambda x: x.get("price_change_percentage_24h", 0), reverse=True)
        response = "\n			TRENDING CRYPTOCURRENCIES (LIVE DATA):\n" + "=" * 70 + "\n"
        for coin in trending[:5]:
            change_24h = coin.get("price_change_percentage_24h", 0)
            response += f"\n			{coin['name']} ({coin['symbol'].upper()})\n"
            response += f"   Price: ${coin['current_price']:,.2f}\n"
            response += f"   24h Change: {change_24h:+.2f}%\n"
            response += f"   Market Cap: ${coin['market_cap']:,.0f}\n"
            if coin["id"] in self.sustainability_data:
                sus = self.sustainability_data[coin["id"]]["sustainability_score"]
                response += f"   Sustainability: {sus}/10\n"
        response += "\n"
        return response

    def find_sustainable(self):
        most_id = max(self.sustainability_data.items(), key=lambda x: x[1]["sustainability_score"])[0]
        data = self.fetch_coin_data(most_id)
        if not data:
            # Offline
            best = max(self.offline_db.items(), key=lambda x: x[1]["sustainability_score"])[0]
            return f"\n			Most sustainable (offline): {best} \U0001F331\n"
        sus = self.sustainability_data[most_id]
        price = data["market_data"]["current_price"]["usd"]
        change = data["market_data"]["price_change_percentage_24h"]
        response = "\n			MOST SUSTAINABLE CRYPTO (LIVE DATA):\n" + "=" * 70 + "\n"
        response += f"{data['name']} ({data['symbol'].upper()})\n\n"
        response += f"   Price: ${price:,.2f}\n"
        response += f"   24h Change: {change:+.2f}%\n"
        response += f"   Sustainability: {sus['sustainability_score']}/10\n"
        response += f"   Energy: {sus['energy_use'].upper()}\n"
        response += f"   Consensus: {sus['consensus']}\n\n"
        return response

    def find_long_term(self):
        market_data = self.fetch_market_data()
        if not market_data:
            # Offline heuristic: rising + high/medium cap, high sustainability
            ranked = []
            for name, meta in self.offline_db.items():
                score = 0
                if meta["price_trend"] == "rising":
                    score += 3
                if meta["market_cap"] == "high":
                    score += 2
                elif meta["market_cap"] == "medium":
                    score += 1
                score += meta["sustainability_score"] * 0.3
                ranked.append((name, score))
            ranked.sort(key=lambda x: x[1], reverse=True)
            top = ", ".join([f"{n} ({s:.1f})" for n, s in ranked[:3]])
            return f"\n			Best for long-term (offline): {top}\n"

        candidates = []
        for coin in market_data:
            score = 0
            if coin.get("price_change_percentage_24h", 0) > 0:
                score += 3
            if coin["market_cap_rank"] <= 10:
                score += 2
            cid = coin["id"]
            if cid in self.sustainability_data:
                sus = self.sustainability_data[cid]["sustainability_score"]
                if sus >= 7:
                    score += 3
                score += sus * 0.2
            candidates.append((coin, score))
        candidates.sort(key=lambda x: x[1], reverse=True)
        response = "\n			BEST FOR LONG-TERM GROWTH (LIVE DATA):\n" + "=" * 70 + "\n"
        for i, (coin, score) in enumerate(candidates[:3], 1):
            response += f"\n{i}. {coin['name']} ({coin['symbol'].upper()}) - Score: {score:.1f}/10\n"
            response += f"   Price: ${coin['current_price']:,.2f}\n"
            response += f"   24h Change: {coin.get('price_change_percentage_24h', 0):+.2f}%\n"
            response += f"   Market Cap Rank: #{coin['market_cap_rank']}\n"
            if coin["id"] in self.sustainability_data:
                sus = self.sustainability_data[coin["id"]]["sustainability_score"]
                response += f"   Sustainability: {sus}/10\n"
        response += "\n"
        return response

    def show_all(self):
        market_data = self.fetch_market_data()
        if not market_data:
            # Offline list
            lines = ["\n			ALL CRYPTOCURRENCIES (OFFLINE):", "=" * 70]
            for name, meta in self.offline_db.items():
                lines.append(f"\n{name}\n   Trend: {meta['price_trend']} | Cap: {meta['market_cap']} | Sustainability: {meta['sustainability_score']}/10")
            lines.append("\n")
            return "\n".join(lines)
        response = "\n			ALL CRYPTOCURRENCIES (LIVE DATA):\n" + "=" * 70 + "\n"
        for coin in market_data:
            response += f"\n{coin['name']} ({coin['symbol'].upper()})\n"
            response += f"   Price: ${coin['current_price']:,.2f} | 24h: {coin.get('price_change_percentage_24h', 0):+.2f}%\n"
            response += f"   Market Cap: ${coin['market_cap']:,.0f}\n"
            if coin["id"] in self.sustainability_data:
                sus = self.sustainability_data[coin["id"]]
                response += f"   Sustainability: {sus['sustainability_score']}/10 | Energy: {sus['energy_use']}\n"
        response += "\n" + "=" * 70 + "\n"
        return response

    def compare_coins(self, query):
        names = [n for n in self.crypto_ids.keys() if n.lower() in query.lower()]
        if len(names) < 2:
            return ("\nPlease specify two cryptocurrencies to compare.\n"
                    f"Available: {', '.join(self.crypto_ids.keys())}\n"
                    "Example: 'compare Bitcoin and Ethereum'\n")
        c1, c2 = names[0], names[1]
        id1, id2 = self.crypto_ids[c1], self.crypto_ids[c2]
        d1, d2 = self.fetch_coin_data(id1), self.fetch_coin_data(id2)
        if not d1 or not d2:
            # Offline compare by sustainability + trend
            s1 = self.sustainability_data.get(id1, {}).get("sustainability_score", 0)
            s2 = self.sustainability_data.get(id2, {}).get("sustainability_score", 0)
            t1 = self.offline_db.get(c1, {}).get("price_trend", "stable")
            t2 = self.offline_db.get(c2, {}).get("price_trend", "stable")
            return (f"\nComparison (offline): {c1} vs {c2}\n"
                    f"   Sustainability: {s1}/10 vs {s2}/10\n"
                    f"   Trend: {t1} vs {t2}\n")
        try:
            p1 = d1["market_data"]["current_price"]["usd"]
            p2 = d2["market_data"]["current_price"]["usd"]
            ch1 = d1["market_data"]["price_change_percentage_24h"]
            ch2 = d2["market_data"]["price_change_percentage_24h"]
            m1 = d1["market_data"]["market_cap"]["usd"]
            m2 = d2["market_data"]["market_cap"]["usd"]
        except Exception:
            return "\nUnable to parse comparison data.\n"
        lines = [
            f"\nComparison (live): {c1} vs {c2}",
            "=" * 70,
            f"Current Price\t ${p1:,.2f}\t\t ${p2:,.2f}",
            f"24h Change\t {ch1:+.2f}%\t\t {ch2:+.2f}%",
            f"Market Cap\t ${m1:,.0f}\t ${m2:,.0f}",
        ]
        if id1 in self.sustainability_data and id2 in self.sustainability_data:
            s1 = self.sustainability_data[id1]
            s2 = self.sustainability_data[id2]
            lines.append(f"Sustainability\t {s1['sustainability_score']}/10\t\t {s2['sustainability_score']}/10")
            lines.append(f"Energy Use\t {s1['energy_use']}\t\t {s2['energy_use']}")
        return "\n".join(lines) + "\n"

    def balanced_recommendation(self):
        market_data = self.fetch_market_data()
        if not market_data:
            # Offline balanced: rising + medium/high cap + sustainability
            best_name = None
            best_score = -1
            for name, meta in self.offline_db.items():
                score = 0
                if meta["price_trend"] == "rising":
                    score += 3
                if meta["market_cap"] == "high":
                    score += 2
                elif meta["market_cap"] == "medium":
                    score += 1
                score += meta["sustainability_score"] * 0.4
                if score > best_score:
                    best_name, best_score = name, score
            return f"\nBalanced pick (offline): {best_name} with score {best_score:.1f}/10\n"

        scores = {}
        for coin in market_data:
            score = 0
            change = coin.get("price_change_percentage_24h", 0)
            if change > 0:
                score += 3 + min(change * 0.1, 2)
            if coin["market_cap_rank"] <= 5:
                score += 2
            elif coin["market_cap_rank"] <= 15:
                score += 1
            cid = coin["id"]
            if cid in self.sustainability_data:
                score += self.sustainability_data[cid]["sustainability_score"] * 0.4
            scores[cid] = (score, coin)
        winner_id = max(scores, key=lambda x: scores[x][0])
        winner_score, coin = scores[winner_id]
        lines = [
            "\nCRYPTOBUDDY'S BALANCED PICK (LIVE DATA):",
            "=" * 70,
            f"Winner: {coin['name']} ({coin['symbol'].upper()})",
            f"Score: {winner_score:.1f}/10",
            f"Price: ${coin['current_price']:,.2f}",
            f"24h: {coin.get('price_change_percentage_24h', 0):+.2f}%",
            f"Market Cap Rank: #{coin['market_cap_rank']}",
        ]
        if winner_id in self.sustainability_data:
            sus = self.sustainability_data[winner_id]
            lines.append(f"Sustainability: {sus['sustainability_score']}/10, Energy: {sus['energy_use'].upper()}")
        lines.append("\nDisclaimer: Crypto is risky—always do your own research!\n")
        return "\n".join(lines)

    # -------------------- Offline Helpers --------------------
    def _offline_price(self, name):
        meta = self.offline_db.get(name)
        if not meta:
            return "\nNo offline data available.\n"
        return (f"\n{name} (offline)\n"
                f"   Trend: {meta['price_trend']} | Market cap: {meta['market_cap']}\n"
                f"   Sustainability: {meta['sustainability_score']}/10 | Energy: {meta['energy_use']}\n")

    # -------------------- Router --------------------
    def process_response(self, user_input):
        q = user_input.lower()
        if "price" in q:
            for coin in self.crypto_ids.keys():
                if coin.lower() in q:
                    return self.get_price(coin)
            return self.show_all()
        if any(w in q for w in ["trending", "rising", "hot", "growing"]):
            return self.find_trending()
        if any(w in q for w in ["sustainable", "green", "eco", "environment"]):
            return self.find_sustainable()
        if any(w in q for w in ["long-term", "long term", "growth", "future"]):
            return self.find_long_term()
        if "compare" in q:
            return self.compare_coins(user_input)
        if any(w in q for w in ["all", "list", "show all"]):
            return self.show_all()
        if any(w in q for w in ["recommend", "best", "balanced", "invest"]):
            return self.balanced_recommendation()
        if self.chatbot:
            try:
                return f"\n{self.chatbot.get_response(user_input)}\n"
            except Exception:
                pass
        return "\nI'm not sure about that. Try asking about trending coins, prices, sustainability, or investment advice!\n"

    def run(self):
        self.greet()
        print("Disclaimer: This bot may use real-time data from CoinGecko. Crypto is risky.")
        print("Always do your own research!\n")
        print("Try:")
        print(" - What's the price of Bitcoin?")
        print(" - Which crypto is trending?")
        print(" - What's the most sustainable coin?")
        print(" - Best for long-term growth?")
        print(" - Compare Bitcoin and Ethereum")
        print(" - Show all cryptocurrencies")
        print(" - Give me a recommendation")
        print("\nType 'bye', 'exit', or 'quit' to end\n")
        print("-" * 70)
        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nGoodbye! - CryptoBuddy\n")
                break
            if not user_input:
                continue
            if user_input.lower() in ["bye", "exit", "quit", "goodbye"]:
                print("\nGoodbye! Stay green and grow your wealth!\n")
                break
            print(f"\n{self.name}: Processing... ⏳")
            response = self.process_response(user_input)
            print(f"\n{self.name}: {response}")
            print(datetime.now().strftime("%H:%M:%S"))
            print("-" * 70)


def print_installation():
    print(
        """
Before running, install packages (recommended pinned versions):

pip install requests
# Optional conversational mode
pip install chatterbot==1.0.8 chatterbot-corpus SQLAlchemy==1.4.46 pytz

Run the bot:
python crypto_buddy.py

Set an API key (optional, demo key by default):
export COINGECKO_API_KEY=your_key_here
        """
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        print_installation()
        sys.exit(0)
    bot = CryptoBuddy()
    bot.run() 