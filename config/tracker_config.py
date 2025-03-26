import os
# from google_flight_analysis.flight import Flight
# from flight_tracker.tracked_flight import TrackedFlight

class TrackerConfig:
    def __init__(self):
        self.FLIGHTS_TO_TRACK = [
            # {'origin': '', 'destination': '', 'date': '', 'time': ''},
        ]

        self.FLIGHTS_TO_REMOVE = [
            # {'origin': '', 'destination': '', 'date': '', 'time': ''},
        ]


class ReporterConfig:
    def __init__(self):
        self.port = 587
        self.smtp_server = 'smtp.gmail.com'

        self.login = os.environ.get('GMAIL_LOGIN')
        self.password = os.environ.get('GMAIL_PASSWORD')
        self.recipients = os.environ.get('GMAIL_TO')
