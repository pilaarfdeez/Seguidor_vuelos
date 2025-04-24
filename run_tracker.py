import datetime as dt
import sys

from config.logging import init_logger
from config.config import TrackerConfig
from src.flight_tracker.tracker import Tracker
from src.flight_tracker.report import TrackerReporter
from src.flight_tracker.tracked_flight import TrackedFlight
from src.google_flight_analysis.scrape import *
from src.telegram_bot.send_auto_message import send_auto_message, actualizacionprecio

conf = TrackerConfig()
logger = init_logger(__name__)
tracker = Tracker()
reporter = TrackerReporter()

'''
TODO: 
- Calculate elapsed time
- Adapt for production environment
'''

if conf.ENV == 'production':
    logger.info('Running Tracker in GitHub Actions!')
elif conf.ENV == 'local':
    logger.info('Running Tracker locally!')


for flight in conf.FLIGHTS_TO_TRACK:
    tracked_flight = TrackedFlight(flight)
    tracker.process_flight(tracked_flight=tracked_flight)

for flight in conf.FLIGHTS_TO_REMOVE:
    tracked_flight = TrackedFlight(flight)
    tracker.delete_flight(tracked_flight)

send_auto_message()

for key, flights in tracker.group_flights().items():
    logger.info(f'Checking {len(flights)} tracked flights for {key}')
    result = Scrape(key[1], key[2], key[0])
    ScrapeObjects(result, conf.ENV, headless=False)
    result_df = result.data
    
    for flight in flights:
        match_df = result_df[result_df['Departure datetime'].dt.strftime('%H:%M') == flight.time]
        if match_df.shape[0] == 1:
            tracked_flight = TrackedFlight(match_df)
            tracker.process_flight(tracked_flight=tracked_flight)

        elif match_df.shape[0] == 0:
            logger.warning(f"Could not find any matching flight for departure time {flight.time}")
        else:
            logger.warning(f"Two or more flights found for departure time {flight.time}")

tracker.save_flights()
logger.info('Tracker jobs terminated successfully!')

logger.info('Sending email...')
updated_flights = tracker.new_prices()
reporter.send_report(updated_flights, conf.ENV)


