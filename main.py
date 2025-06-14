import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

# Configuració
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ruta-secreta")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Obtenir tokens (amb logs)
def get_tokens_raw(limit=50):
    url = (
        "https://public-api.birdeye.so/defi/tokenlist"
        "?sort_by=v24hUSD&sort_type=desc&offset=0"
        f"&limit={limit}"
    )
    headers = {"x-api-key": BIRDEYE_API_KEY}
    try:
        print("[LOG] Cridant Birdeye API...")
        r = requests.get(url, headers=headers, timeout=10)
        print(f"[LOG] Status code: {r.status_code}")
        if r.status_code != 200:
            print("[LOG] Error de resposta:", r.text)
            return []
        data = r.json()
        tokens = data.get("data", {}).get("tokens", [])
        print(f"[LOG] Tokens rebuts: {len(tokens)}")
        print("[LOG] Primer token (exemple):", tokens[0] if tokens else "Cap")
        return tokens
    except Exception as e:
        print("[LOG] Excepció durant la crida a Birdeye:", e)
        return []

# Format Market Cap
def format_mcap(m):
    if not m: return "?"
    if m > 1_000_000:
        return f"${round(m/1_000_000,2)}M"
    elif m > 1_000:
        return f"${round(m/1_000,2)}k"
    else:
        return f"${int(m)}"

# Comandes
def start(update: Update, ctx):
    update.message.reply_text("Hola! Envia /tokens per veure tokens actius a Solana 🪙")

def tokens(update: Update, ctx):
    if not BIRDEYE_API_KEY:
        print("[LOG] Falta la BIRDEYE_API_KEY")
        return update.message.reply_text("❌ Falten credencials: BIRDEYE_API_KEY")

    update.message.reply_text("🔍 Cercant tokens a Solana (logs activats)...")
    tokens = get_tokens_raw(limit=50)
    mostrats = 0

    for t in tokens:
        if t.get("chain") != "solana":
            continue

        name = t.get("name", "Sense nom")
        symbol = t.get("symbol", "")
        address = t.get("address", "")
        price = t.get("price_usd", "?")
        liquidity = t.get("liquidity", 0)
        mcap = t.get("market_cap", 0)
        vol = t.get("v24hUSD", 0)

        print(f"[LOG] Mostrant token: {name} ({symbol})")

        msg = (
            f"🚀 {name} ({symbol})\n"
            f"📍 {address}\n"
            f"💧 Liquidity: ${round(liquidity):,}\n"
            f"📈 Market Cap: {format_mcap(mcap)}\n"
            f"📊 Vol 24h: ${round(vol):,}\n"
            f"💵 Price: ${price}\n"
            f"🔗 https://birdeye.so/token/{address}?chain=solana"
        )
        update.message.reply_text(msg)
        mostrats += 1
        if mostrats >= 5:
            break

    if mostrats == 0:
        print("[LOG] Cap token mostrat.")
        update.message.reply_text("No s'ha trobat cap token de Solana.")

# Dispatcher
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("tokens", tokens))

# Webhook
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    d = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(d)
    return "OK"

@app.route("/")
def home():
    return "Bot actiu amb Birdeye ✅"

if __name__ == "__main__":
    print("[LOG] Iniciant servidor Flask...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))