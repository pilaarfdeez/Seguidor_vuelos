"""
This script runs the flight tracker workflow, which includes tracking, updating, and reporting flight information.
Workflow Steps:
1. Initializes configuration, logger, tracker, and reporter.
2. Logs the environment (production or local).
3. Processes flights to track and remove, as specified in the configuration.
4. Groups tracked flights and scrapes flight data for each group.
5. Matches scraped flight data with tracked flights by departure time and updates tracking information.
6. Saves the updated list of tracked flights.
7. Sends a report of updated flights via email and notifies via Telegram.
Modules Used:
- config.logging: Logger initialization.
- config.config: Tracker configuration.
- src.flight_tracker.tracker: Main tracker logic.
- src.flight_tracker.report: Reporting functionality.
- src.flight_tracker.tracked_flight: Tracked flight data structure.
- src.google_flight_analysis.scrape: Flight data scraping.
- src.telegram_bot.send_auto_message: Telegram notification.
- Calculate elapsed time for the workflow.
- Adapt the script for production environment deployment.
"""

import datetime as dt

from config.logging import init_logger
from config.config import TrackerConfig
from src.flight_tracker.tracker import Tracker
from src.flight_tracker.report import TrackerReporter
from src.flight_tracker.tracked_flight import TrackedFlight
from src.google_flight_analysis.scrape import Scrape, ScrapeObjects
# from src.telegram_bot.send_auto_message import send_auto_message

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


for key, flights in tracker.group_flights().items():
    search_date = dt.date.fromisoformat(key[0])
    today = dt.date.today()
    if search_date < today:
        logger.warning(f"Flights {key} are in the past --> removing from tracker")
        for flight in flights:
            tracker.delete_flight(tracked_flight=flight)
        continue

    logger.info(f'Checking {len(flights)} tracked flights for {key}')
    result = Scrape(key[1], key[2], key[0])
    ScrapeObjects(result, conf.ENV, headless=False)
    result_df = result.data
    if not result_df.shape[0]:
        logger.warning(f"No results found for {key}")
        continue

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
updated_flights = tracker.price_changes()
reporter.send_report(updated_flights, conf.ENV)
file_path = 'data/tracked_flights.json'
# send_auto_message(file_path)
