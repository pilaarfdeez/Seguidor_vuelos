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
from src.bargain_discovery.discoverer import Discovery

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
        discovery = Discovery()
        with open("data/bargains.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        html_content = self.build_html_email(data)
        if not html_content:
            logger.info('No new deals today --> Skipping daily report')
            return
        discovery.generate_plot()

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
        new_information = False
        weekday_abbr = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

        html = ['<!DOCTYPE html>']
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
        .table-header {
            background-color:#f2f2f2;
        }
        .new {
            background-color:#ffa366;
        }
        .lower {
            background-color:#60b041;
        }
        .higher {
            background-color:#ff4c26;
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
        html.append('<body>')
        html.append('<div class="container">')

        html.append('<h1>&#128184; Informe Diario de Chollos</h1>')
        html.append('<p>¡Hola! ✈️<br>Aquí están los chollazos de las próximas semanas &#128176;</p>')
        html.append('<div class="plot"><img src="cid:plot_bargains" alt="Vista de chollazos" width="90%"></div>')

        # Tables
        for week_data in data:
            html.append(f'<h2>&#128198; Semana: {week_data["week"]}</h2>')
            grouped_bargains = {key: list(group) 
                           for key, group in groupby(week_data['combinations'], key=lambda f: (f['job']))}
            for tocinillo,bargains in grouped_bargains.items():
                html.append('<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; margin-bottom: 10px;">')
                html.append('<thead><tr class="table-header"><th>Ida</th><th>Vuelta</th><th>Aerolínea</th><th>Precio total</th></tr></thead>')
                html.append('<tbody>')
                for bargain in bargains:
                    out_date = dt.date.fromisoformat(bargain['date'][0])
                    ret_date = dt.date.fromisoformat(bargain['date'][1])
                    if bargain['new']:
                        html.append('<tr class="new">')
                        new_information = True
                    else:
                        html.append('<tr>')
                    html.append(
                        f'<td>{bargain["origin"][0]} &rarr; {bargain["destination"][0]}<br>'
                        f'({bargain["date"][0]}, {bargain["time"][0]}) [{weekday_abbr[out_date.weekday()]}]</td>'
                    )
                    html.append(
                        f'<td>{bargain["origin"][1]} &rarr; {bargain["destination"][1]}<br>'
                        f'({bargain["date"][1]}, {bargain["time"][1]}) [{weekday_abbr[ret_date.weekday()]}]</td>'
                    )
                    html.append(f'<td>{bargain["airline"][0]} / {bargain["airline"][1]}</td>')
                    if bargain['price_change'] == 1:  # cheaper
                        html.append(f'<td class="lower">{bargain["total_price"]}&euro;</td>')
                        new_information = True
                    elif bargain['price_change'] == 2:  # more expensive
                        html.append(f'<td class="higher">{bargain["total_price"]}&euro;</td>')
                        new_information = True
                    else:
                        html.append(f'<td>{bargain["total_price"]}&euro;</td>')
                    html.append('</tr>')
                html.append('</tbody>')
                html.append('</table>')
        html.append(f'''<div class="footer"><p>Creado el {dt.datetime.today().strftime('%d/%m/%Y')}</p>
                    <p>&copy; Seguidor de Vuelos de los tocinillos</p>
                    </div>''')
        html.append('</div></body></html>')

        with open("data/bargain_report.html", "w", encoding="utf-8") as f:
            f.write("".join(html))

        if new_information:
            return "\n".join(html)
        else:
            return None


class CustomBargainReporter:
    def __init__(self, job):
        self.conf = ReporterConfig()
        self.env = self.conf.ENV
        self.today = dt.datetime.today().strftime('%d/%m/%Y')
        self.job = job


    def send_report(self):
        discovery = Discovery()
        with open(f'data/bargains_{self.job["alias"]}.json', "r", encoding="utf-8") as f:
            data = json.load(f)

        html_content = self.build_html_email(data)
        if not html_content:
            logger.info(f'No new deals today for job {self.job["name"]} --> Skipping daily report')
            return
        discovery.generate_plot(job=self.job)

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = self.conf.login
        message["To"] = ', '.join(self.job['email'])
        message["Subject"] = f"Chollos ({self.job['name']}) | Informe Diario {self.today}"

        message.attach(MIMEText(html_content, "html"))

        # Attach the bargain plot
        plot_path = f'data/images/bargains_{self.job["alias"]}.png'
        with open(plot_path, "rb") as img_file:
            img = MIMEImage(img_file.read(), name=os.path.basename(plot_path))
            img.add_header("Content-ID", f"<plot_bargains>")
            message.attach(img)

        # Send the email
        with smtplib.SMTP(self.conf.smtp_server, self.conf.port) as server:
            server.starttls()
            server.login(self.conf.login, self.conf.password)
            server.sendmail(self.conf.login, self.job['email'], message.as_string())
            logger.info('Email sent.')

        return


    def build_html_email(self, data: list):
        new_information = False
        weekday_abbr = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

        html = ['<!DOCTYPE html>']
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
        .table-header {
            background-color:#f2f2f2;
        }
        .new {
            background-color:#ffa366;
        }
        .lower {
            background-color:#60b041;
        }
        .higher {
            background-color:#ff4c26;
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
        html.append('<body>')
        html.append('<div class="container">')

        html.append(f'<h1>&#128184; Informe Diario de {self.job["name"]}</h1>')
        html.append('<p>¡Hola! ✈️<br>Aquí están los chollazos de las próximas semanas &#128176;</p>')
        html.append('<div class="plot"><img src="cid:plot_bargains" alt="Vista de chollazos" width="90%"></div>')

        # Tables
        for week_data in data:
            html.append(f'<h2>&#128198; Semana: {week_data["week"]}</h2>')
            html.append('<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; margin-bottom: 10px;">')
            html.append('<thead><tr class="table-header"><th>Ida</th><th>Vuelta</th><th>Aerolínea</th><th>Precio total</th></tr></thead>')
            html.append('<tbody>')
            for bargain in week_data['combinations']:
                out_date = dt.date.fromisoformat(bargain['date'][0])
                ret_date = dt.date.fromisoformat(bargain['date'][1])

                if bargain['new']:
                    html.append('<tr class="new">')
                    new_information = True
                else:
                    html.append('<tr>')
                html.append(
                    f'<td>{bargain["origin"][0]} &rarr; {bargain["destination"][0]}<br>'
                    f'({bargain["date"][0]}, {bargain["time"][0]}) [{weekday_abbr[out_date.weekday()]}]</td>'
                )
                html.append(
                    f'<td>{bargain["origin"][1]} &rarr; {bargain["destination"][1]}<br>'
                    f'({bargain["date"][1]}, {bargain["time"][1]}) [{weekday_abbr[ret_date.weekday()]}]</td>'
                )
                html.append(f'<td>{bargain["airline"][0]} / {bargain["airline"][1]}</td>')
                if bargain['price_change'] == 1:  # cheaper
                    html.append(f'<td class="lower">{bargain["total_price"]}&euro;</td>')
                    new_information = True
                elif bargain['price_change'] == 2:  # more expensive
                    html.append(f'<td class="higher">{bargain["total_price"]}&euro;</td>')
                    new_information = True
                else:
                    html.append(f'<td>{bargain["total_price"]}&euro;</td>')
                html.append('</tr>')
            html.append('</tbody>')
            html.append('</table>')

        html.append(f'''<div class="footer"><p>Creado el {dt.datetime.today().strftime('%d/%m/%Y')}</p>
                    <p>&copy; Seguidor de Vuelos de Pilar y David</p>
                    </div>''')
        html.append('</div></body></html>')

        with open("data/bargain_report.html", "w", encoding="utf-8") as f:
            f.write("".join(html))

        if new_information:
            return "\n".join(html)
        else:
            return None


class FlightMatchReporter:
    def __init__(self):
        self.conf = ReporterConfig()
        self.env = self.conf.ENV
        self.today = dt.datetime.today().strftime('%d/%m/%Y')

    def send_report(self, matches='real'):
        with open(f"data/{matches}_matches.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        html_content = self.build_html_email(data)
        if not html_content:
            logger.info('No new flight matches today --> Skipping report')
            return

        message = MIMEMultipart()
        message["From"] = self.conf.login
        message["To"] = ', '.join(self.conf.recipients)
        message["Subject"] = f"Explorador | Informe Semanal {self.today}"

        message.attach(MIMEText(html_content, "html"))

        # Optional: Add a plot/image if available
        # plot_path = 'data/images/matches.png'
        # if os.path.exists(plot_path):
        #     with open(plot_path, "rb") as img_file:
        #         img = MIMEImage(img_file.read(), name=os.path.basename(plot_path))
        #         img.add_header("Content-ID", "<plot_matches>")
        #         message.attach(img)

        with smtplib.SMTP(self.conf.smtp_server, self.conf.port) as server:
            server.starttls()
            server.login(self.conf.login, self.conf.password)
            server.sendmail(self.conf.login, self.conf.recipients, message.as_string())
            logger.info('Flight match report email sent.')

    def build_html_email(self, data: list):
        if not data:
            return None
        
        matches = data

        html = ['<!DOCTYPE html>']
        html.append('''
    <head>
        <meta charset="UTF-8">
        <title>Informe de Vuelos Conjuntos</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px; }
            .container { max-width: 700px; margin: auto; background: white; padding: 20px; border-radius: 8px; }
            h1 { text-align: center; color: #333; }
            h2 { color: #444; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; }
            .footer { text-align: center; font-size: 12px; color: #777; margin-top: 20px; }
        </style>
    </head>
    ''')

        html.append('<body><div class="container">')
        html.append('<h1>✈️ Informe de Exploración de Vuelos</h1>')
        html.append('<p>Estas son las mejores coincidencias encontradas para que David y Pilar hagan su próximo viaje juntitos:</p>')


        html.append('<table>')
        html.append('''
            <thead>
                <tr>
                    <th>Destino</th>
                    <th>Fechas<br>(Ida &rarr; Vuelta)</th>
                    <th>Precio Total</th>
                    <th>Precios<br>(Ida &rarr; Vuelta)</th>
                    <th>Duración vuelo<br>(Ida &rarr; Vuelta)</th>
                    <th>Alcachofilla</th>
                </tr>
            </thead>
            <tbody>
        ''')

        for match in matches:
            html.append('<tr>')
            html.append(f'<td>{match["City"]} ({match["Country"]})</td>')
            html.append(f'<td>{match["Day"][0]}  &rarr; {match["Day"][1]}</td>')
            html.append(f'<td><strong>{match["Total_Price"]}</strong></td>')
            html.append(  # Divide cell top-bottom
                '<td style="padding:6px;">'
                '<div style="display:flex;flex-direction:column;align-items:center;gap:4px;">'
                f'<div>{match["Price_David"][0]} &rarr; {match["Price_David"][1]}</div>'
                f'<div style="border-top:1px solid #ddd;padding-top:4px;">{match["Price_Pilar"][0]} &rarr; {match["Price_Pilar"][1]}</div>'
                '</div></td>'
            )
            html.append(
                '<td style="padding:6px;">'
                '<div style="display:flex;flex-direction:column;align-items:center;gap:4px;">'
                f'<div>{match["Travel_Time_David"][0]} &rarr; {match["Travel_Time_David"][1]}</div>'
                f'<div style="border-top:1px solid #ddd;padding-top:4px;">{match["Travel_Time_Pilar"][0]} &rarr; {match["Travel_Time_Pilar"][1]}</div>'
                '</div></td>'
            )

            html.append(
                '<td style="padding:6px;">'
                '<div style="display:flex;flex-direction:column;align-items:center;gap:4px;">'
                '<div style="color:#888">David</div>'
                '<div style="border-top:1px solid #ddd;padding-top:4px;color:#888">Piluca</div>'
                '</div></td>'
            )

            html.append('</tr>')

        html.append('</tbody></table>')

        html.append(f'''
            <div class="footer">
                <p>Generado el {self.today}</p>
                <p>&copy; Seguidor de Vuelos de los tocinillos</p>
            </div>
        </div></body></html>
        ''')

        return "".join(html)
