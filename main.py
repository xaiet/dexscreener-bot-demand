from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests, os

BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_pairs():
    res = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
    return res.json().get("pairs", []) if res.status_code == 200 else []

def is_locked(pair):
    return pair.get("liquidityLocked", False)

def holder_distribution_ok(pair):
    holders = pair.get("baseToken", {}).get("holders", {})
    top10 = holders.get("top10Share", 100)
    return top10 <= 25

def filter_pairs(pairs):
    candidates = []
    for p in pairs:
        try:
            mcap = float(p.get("liquidityUsd",0))*2  # simplificació
            volume = float(p.get("volumeUsd",0))
            change = float(p.get("priceChange",{}).get("h1",0))
            age = p.get("age")  # en dies, si disponible
            if 300_000 <= mcap <= 5_000_000 \
               and volume > 100_000 \
               and change > 5 \
               and is_locked(p) \
               and holder_distribution_ok(p):
                candidates.append(p)
        except:
            pass
    return candidates

def tokens(update: Update, context: CallbackContext):
    update.message.reply_text("🔍 Cercant early-stage meme tokens...")
    pairs = get_pairs()
    filtered = filter_pairs(pairs)
    if filtered:
        for p in filtered[:5]:
            update.message.reply_text(f"{p['baseToken']['name']} | mcap ~{int(float(p.get('volumeUsd',0))*2)} U$D | +{p['priceChange']['h1']}% | {p['url']}")
    else:
        update.message.reply_text("No s'han trobat tokens amb aquests criteris.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hola! Envia /tokens per veure possibles gemmes.")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tokens", tokens))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
