import datetime as dt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from jinja2 import Template
import os

from config.logging import init_logger
from config.tracker_config import ReporterConfig
from src.google_flight_analysis.airport import Airport

conf = ReporterConfig()
logger = init_logger(__name__)
airports = Airport().dictionary


class Reporter:
    def __init__(self):
        self.today = dt.datetime.today().strftime('%d/%m/%Y')

        with open('data/report_template.html', 'r') as f:
            self.template = Template(f.read()) 

    def send_report(self, flights):
        logger.debug(f'Number of recipients: {len(conf.recipients)}')
        if len(flights) == 0:
            logger.info('No flights to update --> Skipping daily report')
            return 

        for flight in flights:
            flight.generate_plot()

        html_content = self.template.render(flights=flights, airports=airports, today_date=self.today)

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = conf.login
        message["To"] = ', '.join(conf.recipients)
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
        with smtplib.SMTP(conf.smtp_server, conf.port) as server:
            server.starttls()
            server.login(conf.login, conf.password)
            server.sendmail(conf.login, conf.recipients, message.as_string())
            logger.info('Email sent')

        for flight in flights:
            flight.remove_plot()

        return
