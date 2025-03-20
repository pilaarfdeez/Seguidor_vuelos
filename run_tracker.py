import datetime as dt
import sys

from config.tracker_config import TrackerConfig
from src.flight_tracker.tracker import Tracker
from src.flight_tracker.report import Reporter
from src.google_flight_analysis.flight import Flight
from src.flight_tracker.tracked_flight import TrackedFlight
from src.google_flight_analysis.scrape import *

config = TrackerConfig()
tracker = Tracker()
reporter = Reporter()

'''
TODO: 
- Calculate elapsed time

'''
updated_flights = tracker.new_prices()
reporter.send_report(updated_flights)

sys.exit()


for flight in config.FLIGHTS_TO_TRACK:
    tracked_flight = TrackedFlight(flight)
    tracker.process_flight(tracked_flight=tracked_flight)

for flight in config.FLIGHTS_TO_REMOVE:
    tracked_flight = TrackedFlight(flight)
    tracker.delete_flight(tracked_flight)

for key, flights in tracker.group_flights().items():
    print(f'Checking {len(flights)} tracked flights for {key}')
    result = Scrape(flights[0].origin, flights[0].destination, flights[0].date)
    ScrapeObjects(result, headless=True)
    result_df = result.data
    
    for flight in flights:
        match_df = result_df[result_df['Departure datetime'].dt.strftime('%H:%M') == flight.time]
        if match_df.shape[0] == 1:
            tracked_flight = TrackedFlight(match_df)
            tracker.process_flight(tracked_flight=tracked_flight)

        elif match_df.shape[0] == 0:
            print(f"   Could not find any matching flight for departure time {flight.time}")
        else:
            print(f"   Two or more flights found for departure time {flight.time}")

print('Saving updated flight information...')
tracker.save_flights()

print('Tracker jobs terminated successfully!')

print('Sending email...')
# reporter.send_report(tracker.tracked_flights)
