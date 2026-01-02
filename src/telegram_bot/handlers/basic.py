from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "¡Hola! Muchas gracias por usar nuestro bot de seguimiento de vuelos. ✈️✈️\n\n"
        "Usa /tracker para obtener información sobre tus vuelos seguidos.\n"
        "Usa /buscador para encontrar las mejores ofertas de vuelos futuros.\n\n"
        "Para cualquier duda o sugerencia, no dudes en contactar con @DeividMay o @pilaar_fdeez :)"
    )
    await update.message.reply_text(text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await update.message.reply_text(text_caps)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that command.")
