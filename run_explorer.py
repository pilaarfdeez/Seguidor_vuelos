import datetime as dt
import json
import pandas as pd

from config.config import ExplorerConfig
from config.logging import init_logger
from src.destination_explorer.explorer import Explorer
# from src.destination_explorer.match import Match
from src.google_flight_analysis.human_simulations import *
from src.google_flight_analysis.scrape import *
from src.report.report import FlightMatchReporter

conf = ExplorerConfig()
explorer = Explorer(conf)
logger = init_logger(__name__)
reporter = FlightMatchReporter()

if conf.ENV == 'production':
    logger.info('Running Explorer in GitHub Actions!')
elif conf.ENV == 'local':
    logger.info('Running Explorer locally!')


today_date = dt.date.today()

for day in conf.DAYS_DEPARTURE:
    if dt.datetime.strptime(day, "%Y-%m-%d").date() < today_date:
        logger.warning(f"Date {day} is in the past --> Skipping.")
        continue
    for country, code in explorer.country_to_fb.items():
        logger.info(f"Exploring matching outbound flights to {country} on {day}")
        destination = code
        results_david = Scrape(conf.AIRPORT_DAVID, [destination], day)
        results_pilar = Scrape(conf.AIRPORT_PILAR, [destination], day)
        ScrapeObjects(results_david, conf.ENV)
        ScrapeObjects(results_pilar, conf.ENV)

        processed_matches = explorer.process_matches(day, country, results_david.data, results_pilar.data)
        if processed_matches is not None:
            if explorer.potential_matches[0].empty:
                explorer.potential_matches[0] = processed_matches
            else:
                explorer.potential_matches[0] = pd.concat([explorer.potential_matches[0], processed_matches], axis=0)
            logger.info(f"--> {len(processed_matches)} potential matches found!")

        random_wait(min_sec=0.1, max_sec=0.5)

    random_wait(min_sec=10, max_sec=15)

explorer.save_matches(matches='potential')
explorer.get_freebase_ids()

for country in explorer.potential_matches[0]['Country'].unique():
    for day in conf.DAYS_RETURN:
        if dt.datetime.strptime(day, "%Y-%m-%d").date() < today_date:
            logger.warning(f"Date {day} is in the past --> Skipping.")
            continue

        logger.info(f"Exploring matching return flights from {country} on {day}")
        origin = explorer.potential_matches[0][explorer.potential_matches[0]['Country'] == country]['City'].unique().tolist()
        origin_ids = [explorer.city_to_fb[(city, country)] for city in origin if (city, country) in explorer.city_to_fb]
        if conf.COUNTRY_TRIP:
            # TODO: Explore matching return flights from any city
            pass
        for i in range(0, len(origin_ids), 6):
            batch = origin_ids[i:i+6]
            results_david = Scrape(batch, conf.AIRPORT_DAVID, day)
            results_pilar = Scrape(batch, conf.AIRPORT_PILAR, day)
            ScrapeObjects(results_david, conf.ENV)
            ScrapeObjects(results_pilar, conf.ENV)

            processed_matches = explorer.process_matches(day, country, results_david.data, results_pilar.data)
            if processed_matches is not None:
                if explorer.potential_matches[1].empty:
                    explorer.potential_matches[1] = processed_matches
                else:
                    explorer.potential_matches[1] = pd.concat([explorer.potential_matches[1], processed_matches], axis=0)

        random_wait(min_sec=0.1, max_sec=0.5)

explorer.create_combinations()

explorer.save_matches(matches='real')
logger.info('Explorer job terminated successfully!')

logger.info('Sending email...')
# reporter.send_report()
