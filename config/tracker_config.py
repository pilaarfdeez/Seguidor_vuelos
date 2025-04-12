import os
import json
# from google_flight_analysis.flight import Flight
# from flight_tracker.tracked_flight import TrackedFlight
        

class TrackerConfig:
    def __init__(self):
        env = os.getenv("ENV", "local")
        if env == 'production' or os.getenv("GITHUB_ACTIONS") == "true":
            self.ENV = 'production'
        else:
            self.ENV = 'local'

        self.FLIGHTS_TO_TRACK = [
            # {'origin': '', 'destination': '', 'date': '', 'time': ''},
        ]

        self.FLIGHTS_TO_REMOVE = [
            # {'origin': '', 'destination': '', 'date': '', 'time': ''},
        ]


class ReporterConfig:
    def __init__(self, env):
        self.port = 587
        self.smtp_server = 'smtp.gmail.com'

        self.login = os.environ.get('GMAIL_LOGIN')
        self.password = os.environ.get('GMAIL_PASSWORD')

        raw_recipients = os.environ.get('GMAIL_TO')
        if env == 'production':
            self.recipients = json.loads(raw_recipients)
        elif env == 'local':
            self.recipients = raw_recipients
        
        # print(f"Raw value: {raw_recipients}")
        # print(f"Type: {type(raw_recipients)}\n")

        # self.recipients = json.loads(raw_recipients)
        # print(f"Recipients: {self.recipients}")
        # print(f"Type: {type(self.recipients)}")
        # print(f"Length: {len(self.recipients)}")



