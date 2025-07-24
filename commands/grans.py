from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
import requests
import os

def grans_handler(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        return update.message.reply_text("Ús: /grans [token_address]")

    address = context.args[0]
    url = f"https://public-api.birdeye.so/public/token/{address}/holders"
    headers = {"x-api-key": os.getenv("BIRDEYE_API_KEY")}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        holders = res.json().get("data", {}).get("holders", [])

        if not holders:
            return update.message.reply_text("No s'han trobat wallets per aquest token.")

        holders = sorted(holders, key=lambda h: float(h.get("balance_ui", 0)), reverse=True)

        msg = f"📊 *TOP 5 wallets del token:*\n🔗 `{address}`\n\n"
        for i, h in enumerate(holders[:5]):
            owner = h.get("owner", "wallet")
            balance = h.get("balance_ui", "?")
            msg += f"{i+1}. `{owner}` – {balance} tokens\n"

        update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        print("[ERROR] /grans:", e)
        update.message.reply_text("❌ Error obtenint les dades de holders.")

grans = CommandHandler("grans", grans_handler)
