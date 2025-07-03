import datetime as dt
import json
import pandas as pd

from config.config import ExplorerConfig
from config.logging import init_logger
from src.destination_explorer.explorer import Explorer
# from src.destination_explorer.match import Match
from src.google_flight_analysis.human_simulations import *
from src.google_flight_analysis.scrape import *
from report.report import FlightMatchReporter

conf = ExplorerConfig()
explorer = Explorer(conf)
logger = init_logger(__name__)
reporter = FlightMatchReporter()

if conf.ENV == 'production':
    logger.info('Running Explorer in GitHub Actions!')
elif conf.ENV == 'local':
    logger.info('Running Explorer locally!')


today_date = dt.date.today()
country_codes_path = "data/country_codes.json"
with open(country_codes_path, "r", encoding="utf-8") as f:
    country_codes = json.load(f)

for day in conf.DAYS_DEPARTURE:
    if dt.datetime.strptime(day, "%Y-%m-%d").date() < today_date:
        logger.warning(f"Date {day} is in the past --> Skipping.")
        continue
    for country, code in country_codes.items():
        logger.info(f"Exploring matching outbound flights to {country} on {day}")
        destination = code
        results_david = Scrape(conf.AIRPORT_DAVID, [destination], day)
        results_pilar = Scrape(conf.AIRPORT_PILAR, [destination], day)
        ScrapeObjects(results_david, conf.ENV)
        ScrapeObjects(results_pilar, conf.ENV)
        explorer.process_matches(day, country, results_david.data, results_pilar.data)
        random_wait(min_sec=0.1, max_sec=1)

    random_wait(min_sec=10, max_sec=15)

# for day in conf.DAYS_RETURN:
#     if dt.datetime.strptime(day, "%Y-%m-%d").date() < today_date:
#         logger.warning(f"Date {day} is in the past --> Skipping.")
#         continue
#     for country in explorer.potential_matches['Country'].unique():
#         origin = explorer.potential_matches[explorer.potential_matches['Country'] == country]['City'].unique()
#         # TODO: Get the freebase ID (alternatively airport code) for each of the cities
#         results_david = Scrape([origin], conf.AIRPORT_DAVID, day)
#         results_pilar = Scrape([origin], conf.AIRPORT_PILAR, day)
#         ScrapeObjects(results_david, conf.ENV)
#         ScrapeObjects(results_pilar, conf.ENV)
#         explorer.verify_matches(results_david.data, results_pilar.data)


explorer.save_matches(matches='potential')
logger.info('Explorer job terminated successfully!')

logger.info('Sending email...')
reporter.send_report()
