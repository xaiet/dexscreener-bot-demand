import os
import time
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

# Obtenir tokens
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
        if tokens:
            print("[LOG] Primer token (exemple):", tokens[0])
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
    update.message.reply_text("Hola! Envia /tokens per veure tokens nous actius a Solana 🪙")

def tokens(update: Update, ctx):
    if not BIRDEYE_API_KEY:
        print("[LOG] Falta la BIRDEYE_API_KEY")
        return update.message.reply_text("❌ Falten credencials: BIRDEYE_API_KEY")

    update.message.reply_text("🔍 Cercant tokens nous i actius a Solana...")
    tokens = get_tokens_raw(limit=50)
    mostrats = 0

    now = int(time.time())
    max_age_seconds = 48 * 3600  # 48 hores

    for t in tokens:
        name = t.get("name", "Sense nom")
        symbol = t.get("symbol", "")
        address = t.get("address", "")
        price = t.get("price", 0)
        liquidity = t.get("liquidity", 0)
        mcap = t.get("mc", 0)
        vol = t.get("v24hUSD", 0)
        created_at = t.get("created_at") or t.get("createdUnixTime")

        # FILTRES
        if not created_at:
            print(f"[LOG] {symbol} no té data de creació")
            continue
        if (now - int(created_at)) > max_age_seconds:
            print(f"[LOG] {symbol} descartat per ser massa antic")
            continue
        if liquidity < 2_000:
            print(f"[LOG] Descarta {symbol} per baixa liquidesa: {liquidity}")
            continue
        if mcap > 10_000_000:
            print(f"[LOG] Descarta {symbol} per mcap alt: {mcap}")
            continue
        if vol < 1_000:
            print(f"[LOG] Descarta {symbol} per volum baix: {vol}")
            continue

        print(f"[LOG] Mostrant token NOU: {name} ({symbol})")

        msg = (
            f"🚀 {name} ({symbol})\n"
            f"📍 {address}\n"
            f"🕒 Creat fa: {round((now - int(created_at)) / 3600, 1)} hores\n"
            f"💧 Liquidity: ${round(liquidity):,}\n"
            f"📈 Market Cap: {format_mcap(mcap)}\n"
            f"📊 Vol 24h: ${round(vol):,}\n"
            f"💵 Price: ${round(price, 4) if isinstance(price, float) else price}\n"
            f"🔗 https://birdeye.so/token/{address}?chain=solana"
        )
        update.message.reply_text(msg)
        mostrats += 1
        if mostrats >= 5:
            break

    if mostrats == 0:
        print("[LOG] Cap token ha passat els filtres de novetat.")
        update.message.reply_text("No s'ha trobat cap token nou amb aquests criteris.")

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