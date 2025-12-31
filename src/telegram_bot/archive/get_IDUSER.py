import telebot

TOKEN = ''  # Asegúrate de colocar tu token aquí
bot = telebot.TeleBot(TOKEN)

# Manejador para cualquier mensaje recibido
@bot.message_handler(func=lambda message: True)
def get_user_id(message):
    user_id = message.from_user.id  # Captura el user_id
    bot.reply_to(message, f"Tu ID de usuario es: {user_id}")  # Envía el ID al usuario

# Inicia el bot
bot.polling(none_stop=True)
