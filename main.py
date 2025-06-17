import os
import time
import requests
import threading
from flask import Flask, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

# Configuració
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "ruta-secreta")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
NOTIF_CHAT_ID = os.getenv("NOTIF_CHAT_ID")  # Afegit per notificacions
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Comanda per obtenir el chat_id
def show_id(update: Update, ctx):
    update.message.reply_text(f"El teu ID és: `{update.message.chat_id}`", parse_mode="Markdown")

# Comanda per comprovar l'estat del bot
def show_status(update: Update, ctx):
    update.message.reply_text("✅ El bot està actiu i escoltant.")

# Comanda per mostrar tokens tendència manualment
def cmd_tendencia(update: Update, ctx):
    chat_id = update.message.chat_id
    update.message.reply_text("🔍 Cercant tokens en tendència...")
    enviar_tokens_filtrats(chat_id)

# Ruta per rebre actualitzacions del webhook
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        return "OK"
    except Exception as e:
        print("[LOG] Error processant el webhook:", e)
        return jsonify({"error": "Error processant la petició"}), 500

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
        r.raise_for_status()
        return r.json().get("data", {}).get("tokens", [])
    except requests.RequestException as e:
        print("[LOG] Error de xarxa a get_tokens_raw:", e)
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
            return True

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

# Enviar tokens filtrats
def enviar_tokens_filtrats(chat_id):
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
        )
        bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown", disable_web_page_preview=True)
        mostrats += 1
        if mostrats >= 3:
            break
    if mostrats == 0:
        bot.send_message(chat_id=chat_id, text="❌ No s'ha trobat cap token que compleixi els filtres ara mateix.")

# Loop automàtic cada 4 hores
def iniciar_notificacions():
    def loop():
        while True:
            try:
                print("[LOG] Iniciant cerca automàtica de tokens...")
                if NOTIF_CHAT_ID:
                    enviar_tokens_filtrats(NOTIF_CHAT_ID)
            except Exception as e:
                print("[LOG] Error al bucle de notificació:", e)
            time.sleep(4 * 3600)

    threading.Thread(target=loop, daemon=True).start()

# Inicialitzar notificacions si s'executa com a script
if __name__ == "__main__":
    iniciar_notificacions()
    print("[LOG] Iniciant servidor Flask...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

# Dispatcher (registre de comandes Telegram)
dispatcher = Dispatcher(bot, update_queue=None, use_context=True)
dispatcher.add_handler(CommandHandler("id", show_id))
dispatcher.add_handler(CommandHandler("status", show_status))
dispatcher.add_handler(CommandHandler("tendencia", cmd_tendencia))
