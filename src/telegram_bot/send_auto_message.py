import telebot
import json
import schedule
import time
from threading import Thread

TOKEN = ''  # Asegúrate de colocar tu token aquí
bot = telebot.TeleBot(TOKEN)

# Aquí pones el ID del usuario al que quieres enviar el mensaje automáticamente
user_ids = ['']  # Pon el ID del usuario que recibirá el mensaje

def send_auto_message():
    try:
        # Abre el archivo JSON
        with open('C:/Users/Pilar/Downloads/BOT/datos.json', 'r', encoding='utf-8') as file:
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

# Función para programar el envío diario a la hora deseada
def job():
    send_auto_message()

# Configuramos la programación para que el mensaje se envíe todos los días a las 10:00 AM
schedule.every().day.at("9:00").do(job)  # Cambia la hora aquí según lo necesites

# Función que ejecuta el loop de `schedule`
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Espera 1 segundo entre chequeos para no sobrecargar el CPU

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Ya ha llegado el momento de tener nuestros vuelos controlados!!✈️😊")

@bot.message_handler(commands=['actualizacionprecio'])
def actualizacionprecio(message):
    send_auto_message()

# Inicia el hilo para la programación de tareas
Thread(target=run_schedule).start()

# Inicia el bot en modo polling
bot.polling(none_stop=True, timeout=20, interval=0)
