import json
from telegram import Update
from telegram.ext import ContextTypes

DATA_PATH = "../../data/tracked_flights.json"

async def send_tracker_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as file:
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
                    last = prices[-1]
                    mensaje += f"\n   - {last.get("date")}: {last.get("price")} €"
                mensaje += "\n"

                # Enviamos el mensaje al usuario
                await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje)

    # except Exception as e:
    #     await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")

    except Exception as e:
        await update.message.reply_text(f"Error reading flights: {e}")
