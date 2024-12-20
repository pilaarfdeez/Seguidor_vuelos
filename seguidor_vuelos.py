import smtplib
import schedule
import time
from ryanair import Ryanair
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os



# Inicializa la clase Ryanair
api = Ryanair(currency="EUR")  # Puedes especificar la moneda que prefieras
precio_anterior = 150  # Ejemplo de precio anterior
# Define las fechas de salida y regreso
fecha_ida = datetime(2025, 3, 2)

# Obtiene los vuelos más baratos desde el aeropuerto de origen al destino
vuelos_ida = api.get_cheapest_flights("FMM", fecha_ida, fecha_ida + timedelta(days=1))


    
def enviar_correo():
    # Configuración del correo
    correo = 'impersonal4333@gmail.com'  # Tu correo de Gmail
    contrasena_aplicacion = os.getenv("GMAIL_PASSWORD")
    destinatario = 'impersonal4333@gmail.com'  # Correo del destinatario

    # Crear el objeto MIME
    mensaje = MIMEMultipart()
    mensaje['From'] = correo
    mensaje['To'] = destinatario
    mensaje['Subject'] = "¡El precio de tu vuelo ha bajado!"


    # Cuerpo del mensaje    
    cuerpo = f"El vuelo de {origen} a {destino} ha bajado a {precio_actual} EUR. ¡Apresúrate y compra!"
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    try:
        # Conectar al servidor SMTP de Gmail
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()  # Inicia la conexión segura (TLS)

        # Iniciar sesión con tu correo y la contraseña de la aplicación
        servidor.login(correo, contrasena_aplicacion)

        # Enviar el correo
        servidor.sendmail(correo, destinatario, mensaje.as_string())

        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        # Cerrar la conexión con el servidor SMTP
        servidor.quit()


precio_anterior = 150  # Ejemplo de precio anterior
def verificar_vuelo():
  global precio_anterior
  vuelo_ida = []
  for ruta in vuelos_ida:
      if ruta.destination == "AGP":  # Filtra por el código IATA de París
          vuelo_ida.append(ruta)


  for vuelo in vuelo_ida:
          precio_actual = vuelo.price
          # Aquí debemos almacenar el precio anterior, podrías hacerlo en un archivo o en una base de datos
          # En este ejemplo, simplemente comparamos con un valor previo. 
          

          if precio_actual < precio_anterior:  # Si el precio ha bajado
              precio_anterior = precio_actual
              print("aqui")
              enviar_correo()
              
verificar_vuelo()
schedule.every().day.at("09:00").do(verificar_vuelo)
while True:
   schedule.run_pending()
   time.sleep(60)  # Espera 1 minuto entre las ejecuciones
# Muestra los resultados
for vuelo in vuelo_ida:
  print(f"Destino: {vuelo.destination}, Fecha de salida: {vuelo.departureTime}, Precio: {vuelo.price} EUR")
