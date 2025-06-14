import os
import time
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

# Configuració
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ruta-secreta")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Obtenir tokens per volum
def get_tokens_raw(limit=50):
    url = (
        "https://public-api.birdeye.so/defi/tokenlist"
        "?sort_by=v24hUSD&sort_type=desc&offset=0"
        f"&limit={limit}"
    )
    headers = {"x-api-key": BIRDEYE_API_KEY}
    try:
        print("[LOG] Cridant Birdeye API (TOP tokens)...")
        r = requests.get(url, headers=headers, timeout=10)
        print(f"[LOG] Status code: {r.status_code}")
        if r.status_code != 200:
            print("[LOG] Error de resposta:", r.text)
            return []
        return r.json().get("data", {}).get("tokens", [])
    except Exception as e:
        print("[LOG] Excepció a get_tokens_raw:", e)
        return []

# Obtenir tokens més nous
def get_newest_tokens(limit=50):
    url = (
        "https://public-api.birdeye.so/defi/tokenlist"
        "?sort_by=created_at&sort_type=desc&offset=0"
        f"&limit={limit}"
    )
    headers = {"x-api-key": BIRDEYE_API_KEY}
    try:
        print("[LOG] Cridant Birdeye API (tokens nous)...")
        r = requests.get(url, headers=headers, timeout=10)
        print(f"[LOG] Status code: {r.status_code}")
        if r.status_code != 200:
            print("[LOG] Error de resposta:", r.text)
            return []
        return r.json().get("data", {}).get("tokens", [])
    except Exception as e:
        print("[LOG] Excepció a get_newest_tokens:", e)
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

# Botó "Tornar a buscar"
def enviar_boto_refresh(update, context, tipus):
    keyboard = [
        [InlineKeyboardButton("🔄 Tornar a buscar", callback_data=f"refresh_{tipus}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text("Vols tornar a buscar?", reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text("Vols tornar a buscar?", reply_markup=reply_markup)

# Comanda /tokens
def tokens(update: Update, ctx):
    update.message.reply_text("🔍 Cercant tokens actius (TOP volum)...")
    tokens = get_tokens_raw(limit=50)
    mostrats = 0

    for t in tokens:
        name = t.get("name", "Sense nom")
        symbol = t.get("symbol", "")
        address = t.get("address", "")
        price = t.get("price", 0)
        liquidity = t.get("liquidity", 0)
        mcap = t.get("mc", 0)
        vol = t.get("v24hUSD", 0)

        if liquidity < 2_000 or mcap > 10_000_000 or vol < 1_000:
            continue

        msg = (
            f"🚀 {name} ({symbol})\n"
            f"📍 {address}\n"
            f"💧 Liquidity: ${round(liquidity):,}\n"
            f"📈 Market Cap: {format_mcap(mcap)}\n"
            f"📊 Vol 24h: ${round(vol):,}\n"
            f"💵 Price: ${round(price, 4) if isinstance(price, float) else price}\n"
            f"🔗 https://birdeye.so/token/{address}?chain=solana"
        )
        update.message.reply_text(msg)
        mostrats += 1
        if mostrats >= 3:
            break

    if mostrats == 0:
        update.message.reply_text("❌ No s'ha trobat cap token amb aquests criteris.")
    else:
        enviar_boto_refresh(update, ctx, tipus="tokens")

# Comanda /nous
def nous(update: Update, ctx):
    update.message.reply_text("🆕 Cercant tokens nous a Solana...")
    tokens = get_newest_tokens(limit=50)
    mostrats = 0
    now = int(time.time())

    for t in tokens:
        name = t.get("name", "Sense nom")
        symbol = t.get("symbol", "")
        address = t.get("address", "")
        price = t.get("price", 0)
        liquidity = t.get("liquidity", 0)
        mcap = t.get("mc", 0)
        vol = t.get("v24hUSD", 0)
        created_at = t.get("created_at") or t.get("createdUnixTime")

        if not created_at:
            continue
        hours_old = round((now - int(created_at)) / 3600, 1)
        if liquidity < 2_000 or mcap > 10_000_000 or vol < 1_000:
            continue

        msg = (
            f"🚀 {name} ({symbol})\n"
            f"📍 {address}\n"
            f"🕒 Creat fa: {hours_old} hores\n"
            f"💧 Liquidity: ${round(liquidity):,}\n"
            f"📈 Market Cap: {format_mcap(mcap)}\n"
            f"📊 Vol 24h: ${round(vol):,}\n"
            f"💵 Price: ${round(price, 4) if isinstance(price, float) else price}\n"
            f"🔗 https://birdeye.so/token/{address}?chain=solana"
        )
        update.message.reply_text(msg)
        mostrats += 1
        if mostrats >= 3:
            break

    if mostrats == 0:
        update.message.reply_text("❌ No s'ha trobat cap token nou amb aquests criteris.")
    else:
        enviar_boto_refresh(update, ctx, tipus="nous")

# Comanda /help
def help_command(update: Update, ctx):
    text = (
        "🆘 *Ajuda del bot de tokens de Solana*\n\n"
        "Aquest bot et mostra tokens detectats a la plataforma [Birdeye](https://birdeye.so):\n\n"
        "🔹 `/tokens` – Mostra tokens amb més activitat (volum alt, mcap raonable...)\n"
        "🔹 `/nous` – Mostra tokens acabats de crear, útil per detectar memecoins\n"
        "🔹 Botó 🔄 – Torna a buscar resultats sense escriure la comanda\n\n"
        "💡 Només es mostren *3 tokens* per comanda per evitar saturar el xat.\n"
        "❗ Filtres aplicats: liquidesa mínima, volum mínim i mcap màxim."
    )
    update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# Gestor del botó
def refrescar(update: Update, context):
    query = update.callback_query
    query.answer()
    accio = query.data

    if accio == "refresh_tokens":
        query.message.reply_text("🔄 Tornant a buscar tokens actius...")
        tokens(query, context)
    elif accio == "refresh_nous":
        query.message.reply_text("🔄 Tornant a buscar tokens nous...")
        nous(query, context)

# Dispatcher
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
dispatcher.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text(
    "Hola! Prova /tokens o /nous 🪙\nEscriu /help per veure què pot fer el bot."
)))
dispatcher.add_handler(CommandHandler("tokens", tokens))
dispatcher.add_handler(CommandHandler("nous", nous))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CallbackQueryHandler(refrescar))

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