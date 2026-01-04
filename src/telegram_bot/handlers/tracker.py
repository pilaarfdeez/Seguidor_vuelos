import json
import re
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

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



ORIGIN, DESTINATION, DATE, TIME, CONFIRM = range(5)

@handle_error
async def addflight_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Vamos a añadir un nuevo vuelo para seguimiento! Para ello, voy a necesitar los datos del vuelo.\n"
        "Recuerda que puedes cancelar en cualquier momento escribiendo /cancelar.\n"
        "Primero, introduce el código del aeropuerto de origen (por ejemplo, 'MAD'):"
    )
    return ORIGIN

@handle_error
async def removeflight_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Vamos a eliminar uno de los vuelos del seguidor. Para ello, voy a necesitar los datos del vuelo.\n"
        "Recuerda que puedes cancelar en cualquier momento escribiendo /cancelar.\n"
        "Primero, introduce el código del aeropuerto de origen (por ejemplo, 'MAD'):"
    )
    return ORIGIN

@handle_error
async def tracker_origin(update, context):
    origin = update.message.text.upper()
    if not re.fullmatch("[A-Z]{3}", origin):
        await update.message.reply_text("El código de aeropuerto consiste en 3 letras mayúsculas. Por favor, inténtalo de nuevo:")
        return ORIGIN
    context.user_data["origin"] = origin
    await update.message.reply_text("Introduce el código del aeropuerto de destino:")
    return DESTINATION

@handle_error
async def tracker_destination(update, context):
    dest = update.message.text.upper()
    if not re.fullmatch("[A-Z]{3}", dest):
        await update.message.reply_text("El código de aeropuerto consiste en 3 letras mayúsculas. Por favor, inténtalo de nuevo:")
        return DESTINATION
    context.user_data["destination"] = dest
    await update.message.reply_text("Introduce la fecha del vuelo (YYYY-MM-DD):")
    return DATE

@handle_error
async def tracker_date(update, context):
    date = update.message.text
    if not re.fullmatch("\d{4}-\d{2}-\d{2}", date):
        await update.message.reply_text("La fecha debe tener el formato YYYY-MM-DD. Por favor, inténtalo de nuevo:")
        return DATE
    context.user_data["date"] = update.message.text
    await update.message.reply_text("Introduce la hora de salida del vuelo (HH:MM):")
    return TIME

@handle_error
async def tracker_time(update, context):
    time = update.message.text
    if not re.fullmatch("\d{2}:\d{2}", time):
        await update.message.reply_text("La hora debe tener el formato HH:MM. Por favor, inténtalo de nuevo:")
        return TIME
    context.user_data["time"] = update.message.text

    summary = (
        f"Has seleccionado el siguiente vuelo:\n"
        f"✈️ {context.user_data['origin']} → {context.user_data['destination']}\n"
        f"📅 {context.user_data['date']} {context.user_data['time']}\n"
    )

    keyboard = [["Confirmar", "Cancelar"]]
    await update.message.reply_text(summary, reply_markup=ReplyKeyboardMarkup(keyboard))
    return CONFIRM

@handle_error
async def addflight_confirm(update, context):
    if update.message.text != "Confirmar":
        await update.message.reply_text("Cancelado.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    user_id = update.effective_user.id
    new_flight = dict(context.user_data)
    new_flight["prices"] = []

    def updater(data):
        data.append(new_flight)

    update_json_file(
        DATA_PATH,
        updater,
        f"Add flight ({new_flight['origin']}-{new_flight['destination']}) on {new_flight['date']} ({user_id})"
    )

    await update.message.reply_text("Tu vuelo se ha guardado correctamente ✅", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

@handle_error
async def removeflight_confirm(update, context):
    if update.message.text != "Confirmar":
        await update.message.reply_text("Cancelado.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    user_id = update.effective_user.id
    selected_flight = dict(context.user_data)

    def updater(data):
        for idx, tracked_flight in enumerate(data):
            if all(selected_flight[key] == tracked_flight[key] for key in selected_flight.keys() if key != 'prices'):
                data.pop(idx)
                break

    update_json_file(
        DATA_PATH,
        updater,
        f"Remove flight ({selected_flight['origin']}-{selected_flight['destination']}) on {selected_flight['date']} ({user_id})"
    )

    await update.message.reply_text("Tu vuelo se ha eliminado correctamente ✅", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def tracker_cancel(update, context):
    await update.message.reply_text("Operación cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
