import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
BASE_URL = os.environ["BASE_URL"]  # např. https://moje-sluzba.onrender.com

app = Flask(__name__)

# → vytvoříme Telegram application
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# → napevno nastavíme webhook u Telegramu (během importu, tedy před tím, než je
#   Gunicorn spustí Flask)
asyncio.get_event_loop().run_until_complete(
    telegram_app.bot.set_webhook(f"{BASE_URL}/{BOT_TOKEN}")
)

#
# handlers
#

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇨🇿 Čeština", callback_data="lang_cs"),
            InlineKeyboardButton("🌍 English", callback_data="lang_en"),
        ]
    ]
    await update.message.reply_text(
        "☕️ Welcome to Coffee Perk!\n"
        "We’re happy to see you here. 🌟\n"
        "Please choose your language. 🗣️",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def lang_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.callback_query.data
    await update.callback_query.answer()
    if code == "lang_cs":
        keyboard = [
            [InlineKeyboardButton("🧾 Menu a nabídka", callback_data="menu_cs")],
            [InlineKeyboardButton("🕐 Otevírací doba", callback_data="hours_cs")],
            [InlineKeyboardButton("📍 Kde nás najdete", callback_data="where_cs")],
            [InlineKeyboardButton("📞 Kontakt / Rezervace", callback_data="contact_cs")],
            [InlineKeyboardButton("📦 Předobjednávka", callback_data="preorder_cs")],
            [InlineKeyboardButton("😎 Proč k nám?", callback_data="why_cs")],
        ]
        await update.callback_query.edit_message_text(
            "Na co se mě můžeš zeptat:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🧾 Menu & Offer", callback_data="menu_en")],
            [InlineKeyboardButton("🕐 Opening Hours", callback_data="hours_en")],
            [InlineKeyboardButton("📍 Location", callback_data="where_en")],
            [InlineKeyboardButton("📞 Contact / Booking", callback_data="contact_en")],
            [InlineKeyboardButton("📦 Pre-order", callback_data="preorder_en")],
            [InlineKeyboardButton("😎 Why Visit", callback_data="why_en")],
        ]
        await update.callback_query.edit_message_text(
            "What can you ask me:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

SECTIONS = {
    # ... sem vložte přesně všechny texty z příspěvku výše ...
}

async def show_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.callback_query.data
    await update.callback_query.answer()
    text = SECTIONS.get(key, "❌ Sekce nenalezena.")
    await update.callback_query.edit_message_text(text)

# přidáme do botu handlery
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(lang_select, pattern=r"^lang_"))
telegram_app.add_handler(CallbackQueryHandler(show_section, pattern=r"^(menu|hours|where|contact|preorder|why)_"))

#
# Flask route pro přijímání Telegram webhooků
#
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    telegram_app._handle_update(update)
    return "OK"

#
# jednoduchá health-check stránka, aby GET / nepadalo 404
#
@app.route("/", methods=["GET"])
def index():
    return "OK"

# A tímto končí tento soubor – žádné __main__, žádné start_webhook(), žádné idle()

