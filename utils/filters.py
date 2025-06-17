import requests
import time
from utils.helpers import format_token_message


def get_tokens_raw(limit=50):
    from os import getenv
    url = (
        "https://public-api.birdeye.so/defi/tokenlist"
        "?sort_by=v24hUSD&sort_type=desc&offset=0"
        f"&limit={limit}"
    )
    headers = {"x-api-key": getenv("BIRDEYE_API_KEY")}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json().get("data", {}).get("tokens", [])
    except Exception as e:
        print("[LOG] Error a get_tokens_raw:", e)
        return []


def is_holder_distribution_suspicious(token_address):
    try:
        url = f"https://public-api.solscan.io/token/holders?tokenAddress={token_address}&limit=5"
        headers = {"accept": "application/json"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        holders = r.json().get("data", [])
        for h in holders:
            percent = h.get("percent", 0)
            if percent > 50:
                return True
        return False
    except Exception as e:
        print(f"[LOG] Error comprovant holders: {e}")
        return True


def is_token_swappable_in_jupiter(token_address):
    try:
        url = (
            f"https://quote-api.jup.ag/v6/swap"
            f"?inputMint=So11111111111111111111111111111111111111112"
            f"&outputMint={token_address}&amount=1000000&slippage=5"
        )
        r = requests.get(url, timeout=10)
        return r.status_code == 200 and r.json().get("routes")
    except Exception as e:
        print(f"[LOG] Error comprovant swap Jupiter: {e}")
        return False


def get_filtered_tokens():
    now = int(time.time())
    results = []

    for t in get_tokens_raw():
        name = t.get("name", "Sense nom")
        symbol = t.get("symbol", "")
        address = t.get("address", "")
        price = t.get("price", 0)
        liquidity = t.get("liquidity", 0)
        mcap = t.get("mc", 0)
        vol = t.get("v24hUSD", 0)
        created_at = t.get("created_at") or t.get("createdUnixTime")
        is_verified = t.get("is_verified", True)
        change_1h = t.get("priceChange1hPercent", 0)
        change_6h = t.get("priceChange6hPercent", 0)
        change_24h = t.get("priceChange24hPercent", 0)

        if not created_at:
            continue

        hours_old = round((now - int(created_at)) / 3600, 2)

        if liquidity < 3_000: continue
        if mcap < 10_000 or mcap > 1_500_000: continue
        if vol < 2_000 or vol > 30_000: continue
        if hours_old < 0.5 or hours_old > 2.5: continue
        if not is_verified: continue
        if len(symbol) > 10 or any(c in symbol for c in "!@#$%^&*()"): continue
        if change_24h > 200 or change_6h > 150: continue
        if not (5 < change_1h < 50): continue
        if is_holder_distribution_suspicious(address): continue
        if not is_token_swappable_in_jupiter(address): continue

        results.append(format_token_message(name, symbol, address, price, liquidity, mcap, vol, hours_old, change_1h, change_6h, change_24h))

    return results