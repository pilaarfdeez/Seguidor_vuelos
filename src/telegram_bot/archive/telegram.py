import telebot
import json


TOKEN = ('ID_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,"Ya ha llegado el momento de tener tus vuelos controlados!!✈️😊")
    
@bot.message_handler(commands=['actualizacionprecio'])
def actualizacionprecio(message):
    try:
        with open('data/tracked_flights.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            bot.reply_to(message, "He leído el archivo JSON correctamente.")
        # Itera sobre la lista de vuelos
        if data:
            for vuelo in data:
                origin = vuelo.get("origin")
                destination = vuelo.get("destination")
                date = vuelo.get("date")
                time = vuelo.get("time")
                prices = vuelo.get("prices", [])

                # Envía la información del vuelo
                mensaje = (f"✈️ Vuelo de {origin} a {destination} 🛫\n"
                           f"🗓️ Fecha de vuelo: {date}\n"
                           f"⏰ Hora: {time}\n"
                           f"💰 Últimos precios:")

                # Extrae los precios y los agrega al mensaje
                if prices:
                    for precio in prices:
                        precio_fecha = precio.get("date")
                        precio_valor = precio.get("price")
                        mensaje += f"\n   - {precio_fecha}: ${precio_valor}"

                # Envía el mensaje con los detalles del vuelo
                bot.reply_to(message, mensaje)

        # Extrae la lista de vuelos del archivo JSON
        else:
            bot.reply_to(message, "No se encontraron vuelos en el archivo JSON.")

    except Exception as e:
        bot.reply_to(message, f"Error al leer el archivo JSON: {e}")

# Inicia el bot en modo polling
bot.polling(none_stop=True, timeout=20, interval=0)
