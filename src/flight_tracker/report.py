import datetime as dt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from itertools import groupby
from jinja2 import Template
import json
import os

from config.logging import init_logger
from config.config import ReporterConfig
from src.google_flight_analysis.airport import Airport
from src.bargain_finder.discoverer import Discoverer

logger = init_logger(__name__)
airports = Airport().dictionary


class TrackerReporter:
    def __init__(self):
        self.conf = ReporterConfig()
        self.today = dt.datetime.today().strftime('%d/%m/%Y')

        with open('data/report_template.html', 'r') as f:
            self.template = Template(f.read()) 

    def send_report(self, flights, env):
        if len(flights) == 0:
            logger.info('No flights to update --> Skipping daily report')
            return 

        for flight in flights:
            flight.generate_plot()

        html_content = self.template.render(flights=flights, airports=airports, today_date=self.today)

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = self.conf.login
        message["To"] = ', '.join(self.conf.recipients)
        message["Subject"] = f"Tracker | Informe Diario {self.today}"

        message.attach(MIMEText(html_content, "html"))


        for flight in flights:
            plot_folder = 'data/images/'
            plot_path = f'{plot_folder}{flight.plot_name}.png'

            if os.path.exists(plot_path):
                # Open the image file in binary mode
                with open(plot_path, "rb") as img_file:
                    img = MIMEImage(img_file.read(), name=os.path.basename(plot_path))
                    img.add_header("Content-ID", f"<plot_{flight.plot_name}>")
                    message.attach(img)

        # Send the email
        with smtplib.SMTP(self.conf.smtp_server, self.conf.port) as server:
            server.starttls()
            server.login(self.conf.login, self.conf.password)
            server.sendmail(self.conf.login, self.conf.recipients, message.as_string())
            logger.info('Email sent')

        for flight in flights:
            flight.remove_plot()

        return


class BargainReporter:
    def __init__(self):
        self.conf = ReporterConfig()
        self.env = self.conf.ENV
        self.today = dt.datetime.today().strftime('%d/%m/%Y')

    def send_report(self):
        discoverer = Discoverer()
        with open("data/bargains.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        discoverer.generate_plot()        
        html_content = self.build_html_email(data)

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = self.conf.login
        message["To"] = ', '.join(self.conf.recipients)
        message["Subject"] = f"Chollos | Informe Diario {self.today}"

        message.attach(MIMEText(html_content, "html"))

        # Attach the bargain plot
        plot_path = 'data/images/bargains.png'
        with open(plot_path, "rb") as img_file:
            img = MIMEImage(img_file.read(), name=os.path.basename(plot_path))
            img.add_header("Content-ID", f"<plot_bargains>")
            message.attach(img)

        # Send the email
        with smtplib.SMTP(self.conf.smtp_server, self.conf.port) as server:
            server.starttls()
            server.login(self.conf.login, self.conf.password)
            server.sendmail(self.conf.login, self.conf.recipients, message.as_string())
            logger.info('Email sent')

        return


    def build_html_email(self, data: list):
        html = ['<html>']
        html.append('''
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe Diario de Chollos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            background: #ffffff;
            margin: auto;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .flight {
            border-bottom: 1px solid #ddd;
            padding: 10px 0;
        }
        .plot {
            text-align: center;
            margin-top: 10px;
        }
        .footer {
            text-align: center;
            font-size: 12px;
            color: #777;
            margin-top: 20px;
        }
    </style>
</head>
''')
        html.append('<body style="font-family: Arial, sans-serif;">')
        html.append('<p>¡Hola! ✈️<br>Aquí están los chollazos de las próximas semanas &#128176;</p>')
        html.append('<div class="plot"><img src="cid:plot_bargains" alt="Vista de chollazos" width="100%"></div>')

        for week_data in data:
            html.append(f'<h2>&#128198; Semana: {week_data["week"]}</h2>')
            grouped_bargains = {key: list(group) 
                           for key, group in groupby(week_data['combinations'], key=lambda f: (f['tocinillo']))}
            for tocinillo,bargains in grouped_bargains.items():
                html.append('<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">')
                html.append('<tr style="background-color:#f2f2f2;"><th>Ida</th><th>Vuelta</th><th>Aerolínea</th><th>Precio total</th></tr>')
                for bargain in bargains:
                    if bargain['new']:
                        html.append('<tr style="background-color:#ffa366;">')
                    else:
                        html.append('<tr>')
                    html.append(f'<td>{bargain["origin"][0]} &rarr; {bargain["destination"][0]} ({bargain["date"][0]}, {bargain["time"][0]})</td>')
                    html.append(f'<td>{bargain["origin"][1]} &rarr; {bargain["destination"][1]} ({bargain["date"][1]}, {bargain["time"][1]})</td>')
                    html.append(f'<td>{bargain["airline"][0]} / {bargain["airline"][1]}</td>')
                    html.append(f'<td')
                    if bargain['new_price']:
                        html.append(f'<td style="background-color:#ffa366;">{bargain["total_price"]}&euro;</td>')
                    else:
                        html.append(f'<td>{bargain["total_price"]}&euro;</td>')
                    html.append('</tr>')

            html.append('</table><br>')
        
        html.append(f'''<div class="footer"><p>Creado el {dt.datetime.today().strftime('%d/%m/%Y')}</p>
                    <p>&copy; Seguidor de Vuelos de los tocinillos</p>
                    </div>''')

        html.append('</body></html>')
        return "\n".join(html)
