
import time
import threading
import os
import requests

NOTIF_CHAT_ID = os.getenv("NOTIF_CHAT_ID")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

BIRDEYE_URL = (
    "https://public-api.birdeye.so/defi/tokenlist"
    "?sort_by=fdv&sort_type=asc&offset=0&limit=50"
)

HEADERS = {"x-api-key": BIRDEYE_API_KEY}


def is_token_promising(token):
    try:
        # Condicions bàsiques per considerar-la una "possible gema"
        price_change_1h = token.get("priceChange", {}).get("h1", 0)
        price_change_5m = token.get("priceChange", {}).get("m5", 0)
        price_change_24h = token.get("priceChange", {}).get("h24", 0)
        market_cap = token.get("marketCap", 0)
        volume_24h = token.get("v24hUSD", 0)
        liquidity = token.get("liquidityUSD", 0)
        buyers = token.get("buyers", 0)

        if not token.get("pairAddress") or not token.get("tokenAddress"):
            return False

        if price_change_1h >= 50 or price_change_5m >= 25 or price_change_24h >= 100:
            if 20000 < volume_24h < 1000000:
                if 10000 < liquidity < 150000:
                    if market_cap and market_cap < 1000000:
                        return True
        return False
    except Exception as e:
        print(f"[LOG] Error a is_token_promising: {e}")
        return False


def get_potential_x2_gems():
    try:
        response = requests.get(BIRDEYE_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        tokens = response.json().get("data", {}).get("tokens", [])
        promising = []
        for token in tokens:
            if is_token_promising(token):
                msg = f"""🚀 *Possible 2x Gem Detected!*
*Name:* {token.get('name')} ({token.get('symbol')})
*Price:* ${round(token.get('priceUsd', 0), 6)}
*1h:* {token.get('priceChange', {}).get('h1', 0)}%
*24h:* {token.get('priceChange', {}).get('h24', 0)}%
*Vol 24h:* ${int(token.get('v24hUSD', 0))}
*Liquidity:* ${int(token.get('liquidityUSD', 0))}
[🔗 Dexscreener](https://dexscreener.com/solana/{token.get('pairAddress')})
"""
                promising.append(msg)
        return promising
    except Exception as e:
        print("[LOG] Error a get_potential_x2_gems:", e)
        return []


def iniciar_notificacions(bot):
    def loop():
        already_sent = set()
        while True:
            try:
                print("[LOG] Buscant gemes amb potencial x2...")
                if NOTIF_CHAT_ID:
                    gems = get_potential_x2_gems()
                    if not gems:
                        print("[LOG] Cap gema trobada aquest minut.")
                    else:
                        for msg in gems:
                            if msg not in already_sent:
                                bot.send_message(
                                    chat_id=NOTIF_CHAT_ID,
                                    text=msg,
                                    parse_mode="Markdown",
                                    disable_web_page_preview=True
                                )
                                already_sent.add(msg)
                                time.sleep(2)
            except Exception as e:
                print("[LOG] Error al bucle de notificació:", e)
            time.sleep(60)  # espera 1 minut entre escanejades

    threading.Thread(target=loop, daemon=True).start()
    print("[LOG] Notificacions automàtiques iniciades.")