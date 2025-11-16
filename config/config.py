import os
import json
# from google_flight_analysis.flight import Flight
# from flight_tracker.tracked_flight import TrackedFlight


if os.getenv("ENV", "local") == 'production' or os.getenv("GITHUB_ACTIONS") == "true":
    env = 'production'
else:
    env = 'local'


class TrackerConfig:
    def __init__(self):
        self.ENV = env

        self.FLIGHTS_TO_TRACK = [
            {'origin': 'MAD', 'destination': 'AGP', 'date': '2025-12-19', 'time': '19:05'},
            {'origin': 'MAD', 'destination': 'AGP', 'date': '2025-12-30', 'time': '19:05'},
            {'origin': 'AGP', 'destination': 'MAD', 'date': '2025-12-28', 'time': '8:30'},
            {'origin': 'AGP', 'destination': 'MAD', 'date': '2025-12-19', 'time': '21:05'},
            {'origin': 'AGP', 'destination': 'MAD', 'date': '2025-12-19', 'time': '17:00'},
            # {'origin': '', 'destination': '', 'date': 'YYYY-MM-DD', 'time': ''},
        ]

        self.FLIGHTS_TO_REMOVE = [
        
        ] 


class BargainFinderConfig:
    def __init__(self):
        self.ENV = env

        self.WEEK_START = 5     # In how many weeks from now should the Finder start searching? 
        self.WEEKS_SEARCH = 10  # How many weeks from the start week should the Finder search?

        self.AIRPORTS_PILAR = (['AGP','GRX'], ['HAM','BRE','LBC'])
        self.AIRPORTS_DAVID = (['HAM','BRE','LBC', 'HAJ'], ['AGP','MAD','BIO'])
        self.DAYS_PILAR = ([5], [7])  # Each of the lists corresponds to each flight of the round trip
        self.DAYS_DAVID = ([3,4,5], [7,8])  # 1 is Monday, 7 is Sunday. Higher numbers correpond to the next week
        
        self.PRICE_THRESHOLD = 150
        self.MAX_TRAVEL_HOURS = 6


class ReporterConfig:
    def __init__(self):
        self.ENV = env

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



