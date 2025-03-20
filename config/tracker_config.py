# from google_flight_analysis.flight import Flight
# from flight_tracker.tracked_flight import TrackedFlight

class TrackerConfig:
    def __init__(self):
        self.FLIGHTS_TO_TRACK = [
            {'origin': 'HAM', 'destination': 'AGP', 'date': '2025-06-22', 'time': '06:00'},
            {'origin': 'AGP', 'destination': 'HAM', 'date': '2025-06-20', 'time': '14:35'},
            # {'origin': '', 'destination': '', 'date': '', 'time': ''},
            # {'origin': '', 'destination': '', 'date': '', 'time': ''},
        ]

        self.FLIGHTS_TO_REMOVE = [
            # {}
        ]

class BargainSpotterConfig:
    def __init__(self):
        self.AIRPORTS_PILAR = ['AGP', 'BIO']
        self.AIRPORTS_DAVID = ['HAM', 'BRE', 'LBC']
        self.PRICE_THRESHOLD = []
        self.MIN_STAY = 3
        self.MAX_STAY = 6
        self.MAX_STOP_HOURS = 3

class ReporterConfig:
    def __init__(self):
        self.port = 587
        self.smtp_server = 'smtp.gmail.com'

        self.login = 'seguidor.pilideivid@gmail.com'
        self.password = 'vwln xaca nrkx gsbm'
        self.recipients = ['davidmayoral1505@gmail.com']
