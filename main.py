from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

def obtenir_dades():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("pairs", [])
    return []

def filtrar_tokens(parelles):
    resultats = []
    for p in parelles:
        try:
            volum = float(p.get("volumeUsd", 0))
            canvi = float(p.get("priceChange", {}).get("h1", 0))
            nom = p.get("baseToken", {}).get("name")
            enllac = p.get("url")

            if volum > 10000 and canvi > 10:
                resultats.append(f"🚀 {nom} ha pujat {canvi}% amb {volum}$ de volum\n👉 {enllac}")
        except:
            continue
    return resultats

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hola! Envia /tokens per veure criptos prometedores 🚀")

def tokens(update: Update, context: CallbackContext):
    update.message.reply_text("🔍 Buscant tokens amb potencial...")
    parelles = obtenir_dades()
    resultats = filtrar_tokens(parelles)
    if resultats:
        for msg in resultats[:5]:  # màxim 5 resultats
            update.message.reply_text(msg)
    else:
        update.message.reply_text("No s'han trobat tokens amb els filtres actuals.")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tokens", tokens))

    updater.start_polling()
    updater.idle()

if __name__ == '__m
