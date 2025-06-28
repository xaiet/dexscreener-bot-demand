
import time
import threading
import os
import requests

NOTIF_CHAT_ID = os.getenv("NOTIF_CHAT_ID")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

BIRDEYE_URL = (
    "https://public-api.birdeye.so/defi/tokenlist"
    "?sort_by=volume_24h&sort_type=desc&offset=0&limit=50"
)

HEADERS = {"x-api-key": BIRDEYE_API_KEY}


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
        print(f"[LOG] Error calculating score: {e}")
        return 0


def get_best_gem():
    try:
        response = requests.get(BIRDEYE_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        tokens = response.json().get("data", {}).get("tokens", [])

        if not tokens:
            return None

        scored_tokens = [(token, score_token(token)) for token in tokens]
        scored_tokens.sort(key=lambda x: x[1], reverse=True)

        best_token = scored_tokens[0][0]
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
    def loop():
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
            except Exception as e:
                print("[LOG] Error al bucle de notificació:", e)
            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()
    print("[LOG] Notificacions automàtiques iniciades.")
