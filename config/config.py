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
            # {'origin': '', 'destination': '', 'date': '', 'time': ''},
        ]

        self.FLIGHTS_TO_REMOVE = [
        {"origin": "AGP",
        "destination": "HAM",
        "date": "2025-06-20",
        "time": "14:35"},
        {"origin": "HAM",
        "destination": "AGP",
        "date": "2025-06-22",
        "time": "06:00"},
        {"origin": "HAM",
        "destination": "BIO",
        "date": "2025-06-30",
        "time": "06:50"},
        {"origin": "HAM",
        "destination": "BIO",
        "date": "2025-06-30",
        "time": "10:00"},
        {"origin": "HAM",
        "destination": "MAD",
        "date": "2025-06-30",
        "time": "15:45"},
        {"origin": "HAM",
        "destination": "MAD",
        "date": "2025-07-01",
        "time": "06:50"},
        {"origin": "HAM",
        "destination": "MAD",
        "date": "2025-07-01",
        "time": "15:45"},
        {"origin": "BIO",
        "destination": "HAM",
        "date": "2025-07-04",
        "time": "20:10"},
        {"origin": "MAD",
        "destination": "HAM",
        "date": "2025-07-04",
        "time": "19:50"},
        {"origin": "BIO",
        "destination": "HAM",
        "date": "2025-07-05",
        "time": "17:35"},
        {"origin": "MAD",
        "destination": "HAM",
        "date": "2025-07-05",
        "time": "19:50"},
        {"origin": "MAD",
        "destination": "HAM",
        "date": "2025-07-06",
        "time": "08:40"},
        {"origin": "MAD",
        "destination": "HAM",
        "date": "2025-07-06",
        "time": "16:15"},
        {"origin": "MAD",
        "destination": "HAM",
        "date": "2025-07-06",
        "time": "19:50"},
        {"origin": "BIO",
        "destination": "HAM",
        "date": "2025-07-07",
        "time": "13:10"}
        ] 


class BargainFinderConfig:
    def __init__(self):
        self.ENV = env

        self.WEEK_START = 7     # In how many weeks from now should the Finder start searching? 
        self.WEEKS_SEARCH = 10  # How many weeks from the start week should the Finder search?

        self.AIRPORTS_PILAR = (['AGP','GRX'], ['HAM','BRE','LBC'])
        self.AIRPORTS_DAVID = (['HAM','BRE','LBC'], ['AGP','MAD','BIO'])
        self.DAYS_PILAR = ([5], [7])  # Each of the lists corresponds to each flight of the round trip
        self.DAYS_DAVID = ([3,4,5], [7,8])  # 1 is Monday, 7 is Sunday. Higher numbers correpond to the next week
        
        self.PRICE_THRESHOLD = 180
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



