import time
import threading
import os
import requests
from datetime import datetime, timedelta

# Variables d'entorn
NOTIF_CHAT_ID = os.getenv("NOTIF_CHAT_ID")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
BIRDEYE_CHAIN = os.getenv("BIRDEYE_CHAIN", "solana")  # cadena per defecte

# Endpoint Birdeye
BIRDEYE_URL = "https://public-api.birdeye.so/defi/tokenlist"

# Headers correctes segons documentació
HEADERS = {
    "X-API-KEY": BIRDEYE_API_KEY,
    "accept": "application/json",
    "x-chain": BIRDEYE_CHAIN
}

# Control per evitar inicialitzacions duplicades
notifier_started = False
notifier_lock = threading.Lock()


def score_token(token):
    try:
        score = 0
        score += token.get("priceChange", {}).get("h1", 0) * 2
        score += token.get("priceChange", {}).get("m5", 0)
        score += token.get("priceChange", {}).get("h24", 0)
        liquidity = token.get("liquidityUSD", 0)
        volume = token.get("v24hUSD", 0)
        if liquidity and 10000 < liquidity < 150000:
            score += 20
        if volume and 20000 < volume < 1000000:
            score += 20
        if token.get("marketCap", 0) and token["marketCap"] < 1000000:
            score += 10
        return score
    except Exception as e:
        print(f"[LOG] Error calculant score: {e}")
        return 0


def get_best_gem():
    try:
        params = {
            "sort_by": "v24hUSD",
            "sort_type": "desc",
            "offset": 0,
            "limit": 100  # agafem més per poder filtrar millor
        }

        print("[DEBUG] Enviant petició a Birdeye...")
        response = requests.get(BIRDEYE_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()

        tokens = response.json().get("data", {}).get("tokens", [])

        if not tokens:
            print("[DEBUG] No s'han rebut tokens.")
            return None

        # 🔍 Excloure tokens per nom i símbol
        excluded_symbols = {
            "wSOL", "WSOL", "Wrapped SOL",
            "USDC", "USDT", "DAI", "USDH", "UXD", "cUSDC", "cUSDT",
            "SOL", "ETH", "BTC", "wETH", "WBTC", "stSOL", "mSOL", "bSOL",
            "WETH", "Wrapped ETH", "Wrapped BTC", "Tether", "USD Coin"
        }

        now = datetime.utcnow()
        min_created_at = now - timedelta(hours=48)

        filtered_tokens = []
        for t in tokens:
            symbol = t.get("symbol", "").upper()
            name = t.get("name", "").upper()
            created_at_ts = t.get("createdAt", 0)

            # Valida nom, símbol i recència (< 48h)
            if (
                symbol not in excluded_symbols and
                name not in excluded_symbols and
                created_at_ts
            ):
                created_at = datetime.utcfromtimestamp(created_at_ts / 1000)
                if created_at >= min_created_at:
                    filtered_tokens.append(t)

        if not filtered_tokens:
            print("[DEBUG] Tots els tokens han estat exclosos per filtre.")
            return None

        scored_tokens = [(token, score_token(token)) for token in filtered_tokens]
        scored_tokens.sort(key=lambda x: x[1], reverse=True)

        print(f"[DEBUG] {len(filtered_tokens)} tokens candidats després de filtrar.")
        for token, score in scored_tokens[:5]:
            print(f"[DEBUG] {token.get('symbol')}: score = {score}")

        best_token, best_score = scored_tokens[0]
        print(f"[DEBUG] Seleccionat: {best_token.get('symbol')} amb score {best_score}")

        msg = f"""🚀 *Millor Gema del Moment!*
*Name:* {best_token.get('name')} ({best_token.get('symbol')})
*Price:* ${round(best_token.get('priceUsd', 0), 6)}
*1h:* {best_token.get('priceChange', {}).get('h1', 0)}%
*24h:* {best_token.get('priceChange', {}).get('h24', 0)}%
*Vol 24h:* ${int(best_token.get('v24hUSD', 0))}
*Liquidity:* ${int(best_token.get('liquidityUSD', 0))}
[🔗 Dexscreener](https://dexscreener.com/solana/{best_token.get('pairAddress')})
"""
        return msg
    except Exception as e:
        print("[LOG] Error a get_best_gem:", e)
        return None


def iniciar_notificacions(bot):
    global notifier_started
    with notifier_lock:
        if notifier_started:
            print("[LOG] Notificació ja iniciada, s'evita duplicació.")
            return
        notifier_started = True

    def loop():
        print("[LOG] Thread de notificació iniciat correctament.")
        last_sent = None
        while True:
            try:
                print("[LOG] Buscant millor gema del moment...")
                if NOTIF_CHAT_ID:
                    msg = get_best_gem()
                    if msg and msg != last_sent:
                        bot.send_message(
                            chat_id=NOTIF_CHAT_ID,
                            text=msg,
                            parse_mode="Markdown",
                            disable_web_page_preview=True
                        )
                        last_sent = msg
                        print("[LOG] Gema enviada.")
                    else:
                        print("[LOG] Cap nova gema diferent trobada.")
                else:
                    print("[LOG] Variable NOTIF_CHAT_ID no definida.")
            except Exception as e:
                print("[LOG] Error al bucle de notificació:", e)
            time.sleep(3600)

    threading.Thread(target=loop, daemon=True).start()
    print("[LOG] Notificacions automàtiques iniciades.")