from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, InlineQueryHandler
import json
import os
from uuid import uuid4

# from config.logging import init_logger


# logger = init_logger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8443))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def send_tracker_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open('data/tracked_flights.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Formateamos el mensaje
        if data:
            for vuelo in data:
                origin = vuelo.get("origin")
                destination = vuelo.get("destination")
                date = vuelo.get("date")
                time = vuelo.get("time")
                prices = vuelo.get("prices", [-1])

                mensaje = (f"✈️ Vuelo de {origin} a {destination} 🛫\n"
                           f"🗓️ Fecha de vuelo: {date}\n"
                           f"⏰ Hora: {time}\n"
                           f"💰 Precios disponibles:")

                # Extraemos los precios y los agregamos al mensaje
                if prices:
                    price_1 = prices[-1]
                    precio_fecha = price_1.get("date")
                    precio_valor = price_1.get("price")
                    mensaje += f"\n   - {precio_fecha}: ${precio_valor} 💸"
                mensaje += "\n"

                # Enviamos el mensaje al usuario
                await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje)

    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    tracker_handler = CommandHandler('tracker', send_tracker_updates)
    caps_handler = CommandHandler('caps', caps)
    inline_caps_handler = InlineQueryHandler(inline_caps)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(tracker_handler)
    application.add_handler(caps_handler)
    application.add_handler(inline_caps_handler)
    application.add_handler(unknown_handler)

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        secret_token=WEBHOOK_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
    )