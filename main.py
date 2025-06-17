import os
import time
import requests
<<<<<<< HEAD
from flask import Flask, request
=======
from flask import Flask, request, jsonify
>>>>>>> 481b565 (refactor de /tokens a /tendencia amb nous filtres)
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
<<<<<<< HEAD
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
=======
        r.raise_for_status()
        return r.json().get("data", {}).get("tokens", [])
    except requests.RequestException as e:
        print("[LOG] Error de xarxa a get_tokens_raw:", e)
>>>>>>> 481b565 (refactor de /tokens a /tendencia amb nous filtres)
        return []
    except Exception as e:
        print("[LOG] Excepció a get_tokens_raw:", e)
        return []

# Comprovar distribució de holders via Solscan
def is_holder_distribution_suspicious(token_address):
    try:
        url = f"https://public-api.solscan.io/token/holders?tokenAddress={token_address}&limit=5"
        headers = {"accept": "application/json"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        holders = r.json().get("data", [])

        if not holders:
            return True  # No info = sospitós

        # Comprovar si algun holder té més del 50% del supply
        for h in holders:
            percent = h.get("percent", 0)
            if percent and percent > 50:
                return True
        return False
    except Exception as e:
        print(f"[LOG] Error comprovant holders: {e}")
        return True

# Comprovar si token té ruta de swap viable a Jupiter
def is_token_swappable_in_jupiter(token_address):
    try:
        url = f"https://quote-api.jup.ag/v6/swap?inputMint=So11111111111111111111111111111111111111112&outputMint={token_address}&amount=1000000&slippage=5"
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and r.json().get("routes"):
            return True
        return False
    except Exception as e:
        print(f"[LOG] Error comprovant swap Jupiter: {e}")
        return False

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

<<<<<<< HEAD
# Comanda /tokens
def tokens(update: Update, ctx):
    update.message.reply_text("🔍 Cercant tokens actius (TOP volum)...")
=======
# Comanda /tendencia – tokens amb potencial alcista
def tendencia(update: Update, ctx):
    update.message.reply_text("📊 Cercant tokens en *tendència alcista potencial*...")
>>>>>>> 481b565 (refactor de /tokens a /tendencia amb nous filtres)
    tokens = get_tokens_raw(limit=50)
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
<<<<<<< HEAD

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
=======
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

        if is_holder_distribution_suspicious(address):
            continue  # Distribució de holders sospitosa

        if not is_token_swappable_in_jupiter(address):
            continue  # No es pot fer swap a Jupiter

        msg = (
            f"📈 *{name}* ({symbol})\n"
            f"📍 `{address}`\n"
            f"🕒 Creat fa: {hours_old} hores\n"
            f"💧 Liquidesa: ${round(liquidity):,}\n"
            f"🏷️ Market Cap: {format_mcap(mcap)}\n"
            f"🔄 Vol 24h: ${round(vol):,}\n"
            f"📈 Canvi 1h: {round(change_1h, 1)}% | 6h: {round(change_6h,1)}% | 24h: {round(change_24h,1)}%\n"
            f"💵 Preu: ${round(price, 4) if isinstance(price, float) else price}\n"
            f"🔗 [Birdeye Link](https://birdeye.so/token/{address}?chain=solana)"
>>>>>>> 481b565 (refactor de /tokens a /tendencia amb nous filtres)
        )
        update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)
        mostrats += 1
        if mostrats >= 3:
            break

    if mostrats == 0:
<<<<<<< HEAD
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
=======
        update.message.reply_text("❌ No s'ha trobat cap token amb potencial en aquest moment.")
    else:
        enviar_boto_refresh(update, ctx, tipus="tendencia")
>>>>>>> 481b565 (refactor de /tokens a /tendencia amb nous filtres)

# Comanda /help
def help_command(update: Update, ctx):
    text = (
<<<<<<< HEAD
        "🆘 *Ajuda del bot de tokens de Solana*\n\n"
        "Aquest bot et mostra tokens detectats a la plataforma [Birdeye](https://birdeye.so):\n\n"
        "🔹 `/tokens` – Mostra tokens amb més activitat (volum alt, mcap raonable...)\n"
        "🔹 `/nous` – Mostra tokens acabats de crear, útil per detectar memecoins\n"
        "🔹 Botó 🔄 – Torna a buscar resultats sense escriure la comanda\n\n"
        "💡 Només es mostren *3 tokens* per comanda per evitar saturar el xat.\n"
        "❗ Filtres aplicats: liquidesa mínima, volum mínim i mcap màxim."
=======
        "🧠 *Ajuda del bot de tokens de Solana*\n\n"
        "Aquest bot et mostra tokens detectats a la plataforma [Birdeye](https://birdeye.so):\n\n"
        "🔹 `/tendencia` – Tokens amb potencial alcista (early hype, però no scam)\n"
        "🔹 Botó 🔄 – Torna a buscar resultats sense escriure la comanda\n\n"
        "💡 Només es mostren *3 tokens* per comanda per evitar saturar el xat.\n"
        "❗ Filtres aplicats: liquidesa, mcap, volum, antiguitat, verificació, momentum, distribució de holders i swap a Jupiter."
>>>>>>> 481b565 (refactor de /tokens a /tendencia amb nous filtres)
    )
    update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

# Gestor del botó
def refrescar(update: Update, context):
    query = update.callback_query
    query.answer()
    accio = query.data

<<<<<<< HEAD
    if accio == "refresh_tokens":
        query.message.reply_text("🔄 Tornant a buscar tokens actius...")
        tokens(query, context)
    elif accio == "refresh_nous":
        query.message.reply_text("🔄 Tornant a buscar tokens nous...")
        nous(query, context)
=======
    if accio == "refresh_tendencia":
        query.message.reply_text("🔄 Tornant a buscar tokens en tendència...")
        tendencia(query, context)
>>>>>>> 481b565 (refactor de /tokens a /tendencia amb nous filtres)

# Dispatcher
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
dispatcher.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text(
<<<<<<< HEAD
    "Hola! Prova /tokens o /nous 🪙\nEscriu /help per veure què pot fer el bot."
)))
dispatcher.add_handler(CommandHandler("tokens", tokens))
dispatcher.add_handler(CommandHandler("nous", nous))
=======
    "Hola! Prova /tendencia 🪙\nEscriu /help per veure què pot fer el bot."
)))
dispatcher.add_handler(CommandHandler("tendencia", tendencia))
>>>>>>> 481b565 (refactor de /tokens a /tendencia amb nous filtres)
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CallbackQueryHandler(refrescar))

# Webhook
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type ha de ser application/json"}), 400

        update_data = request.get_json()

        if not isinstance(update_data, dict) or "update_id" not in str(update_data):
            return jsonify({"error": "Estructura d'update no vàlida"}), 400

        d = Update.de_json(update_data, bot)
        dispatcher.process_update(d)
        return "OK"
    except Exception as e:
        print("[LOG] Error processant el webhook:", e)
        return jsonify({"error": "Error processant la petició"}), 500

@app.route("/")
def home():
    return "Bot actiu amb Birdeye ✅"

if __name__ == "__main__":
    print("[LOG] Iniciant servidor Flask...")
<<<<<<< HEAD
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
=======
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    print("[LOG] Servidor iniciat. Esperant peticions...")
>>>>>>> 481b565 (refactor de /tokens a /tendencia amb nous filtres)
