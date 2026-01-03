import json
from telegram import Update
from telegram.ext import ContextTypes

from github_utils import update_json_file
from utils import handle_error


DATA_PATH = "data/tracked_flights.json"

@handle_error
async def send_tracker_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(f"../../{DATA_PATH}", 'r', encoding='utf-8') as file:
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
                mensaje += f"\n   - {last.get('date')}: {last.get('price')} €"
            mensaje += "\n"

            # Enviamos el mensaje al usuario
            await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje)

# except Exception as e:
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")


@handle_error
async def add_tracked_flight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # origin, dest, date = context.args

    def add_flight_fn(data):
        data.append({
            "origin": "MAD",
            "destination": "BCN",
            "date": "2026-01-01",
            "time": "12:00",
            "prices": []
        })

    update_json_file(
        DATA_PATH,
        add_flight_fn,
        "(Test2) Add flight (MAD-BCN) on 2026-01-01"
    )

    await update.message.reply_text("Flight added and pushed to GitHub ✅")
