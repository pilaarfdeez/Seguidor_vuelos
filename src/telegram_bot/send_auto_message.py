import os
import telebot
import json
import schedule
import time
from threading import Thread

TOKEN = '7630436278:AAEEH1KtqNsA2sesOii1-VySNWvhHXcvfAA'  # Asegúrate de colocar tu token aquí
bot = telebot.TeleBot(TOKEN)

# Aquí pones el ID del usuario al que quieres enviar el mensaje automáticamente
user_ids = [os.environ.get('USER_ID')]  # Pon el ID del usuario que recibirá el mensaje

def send_auto_message(file_path):
    try:
        # Abre el archivo JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Formateamos el mensaje
        if data:
            for vuelo in data:
                origin = vuelo.get("origin")
                destination = vuelo.get("destination")
                date = vuelo.get("date")
                time = vuelo.get("time")
                prices = vuelo.get("prices", [])

                mensaje = (f"✈️ Vuelo de {origin} a {destination} 🛫\n"
                           f"🗓️ Fecha de vuelo: {date}\n"
                           f"⏰ Hora: {time}\n"
                           f"💰 Precios disponibles:")

                # Extraemos los precios y los agregamos al mensaje
                if prices:
                    for precio in prices:
                        precio_fecha = precio.get("date")
                        precio_valor = precio.get("price")
                        mensaje += f"\n   - {precio_fecha}: ${precio_valor} 💸"

                # Enviamos el mensaje automáticamente a cada usuario
                for user_id in user_ids:
                    bot.send_message(user_id, mensaje)

    except Exception as e:
        bot.send_message(user_id, f"Error: {e}")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Ya ha llegado el momento de tener nuestros vuelos controlados!!✈️😊")

@bot.message_handler(commands=['actualizacionprecio'])
def actualizacionprecio(message):
    send_auto_message()


# Inicia el bot en modo polling
# bot.polling(none_stop=True, timeout=20, interval=0)
