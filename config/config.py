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
            {'origin': 'AGP', 'destination': 'VIE', 'date': '2026-09-29', 'time': '08:25'},
            {'origin': 'AGP', 'destination': 'VIE', 'date': '2026-10-01', 'time': '07:20'},
            {'origin': 'AGP', 'destination': 'VIE', 'date': '2026-09-27', 'time': '07:10'},
            {'origin': 'VIE', 'destination': 'AGP', 'date': '2026-12-23', 'time': '06:20'},
            {'origin': 'VIE', 'destination': 'AGP', 'date': '2026-12-22', 'time': '10:20'},
            {'origin': 'AGP', 'destination': 'VIE', 'date': '2027-01-06', 'time': '10:20'},
            {'origin': 'AGP', 'destination': 'VIE', 'date': '2027-01-05', 'time': '06:40'},
            {'origin': 'AGP', 'destination': 'VIE', 'date': '2027-01-05', 'time': '09:15'},
            {'origin': 'AGP', 'destination': 'VIE', 'date': '2027-01-07', 'time': '12:00'}
            
            # {'origin': '', 'destination': '', 'date': 'YYYY-MM-DD', 'time': ''},
        ]

        self.FLIGHTS_TO_REMOVE = [
        
        ] 


class BargainFinderConfig:
    def __init__(self):
        self.ENV = env

        self.WEEK_START = 4     # In how many weeks from now should the Finder start searching? 
        self.WEEKS_SEARCH = 10  # How many weeks from the start week should the Finder search?

        self.AIRPORTS_PILAR = (['AGP','GRX'], ['MUC','FMM','NUE'])
        self.AIRPORTS_DAVID = (['MUC','FMM','NUE'], ['AGP','MAD','BIO', 'GRX'])
        self.DAYS_PILAR = ([4,5], [7])  # Each of the lists corresponds to each flight of the round trip
        self.DAYS_DAVID = ([3,4,5], [7,8])  # 1 is Monday, 7 is Sunday. Higher numbers correpond to the next week
        
        self.PRICE_THRESHOLD = 150
        self.MAX_TRAVEL_HOURS = 6

class ExplorerConfig:
    def __init__(self):
        self.ENV = env

        self.AIRPORT_DAVID = 'HAM'
        self.AIRPORT_PILAR = 'AGP'

        self.DAYS_DEPARTURE = ["2026-07-02", "2026-07-03"]
        self.DAYS_RETURN = ["2026-07-05"]

        self.MAX_TRAVEL_HOURS = 6
        self.MAX_PRICE = 200
        self.COUNTRY_TRIP = False  # If True, return from any city in the country are considered


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



