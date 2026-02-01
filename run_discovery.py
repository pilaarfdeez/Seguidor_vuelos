"""
This script performs automated flight bargain discovery and reporting.
Workflow:
1. Initializes configuration, logging, and reporting utilities.
2. Determines the reference date for weekly searches based on configuration.
3. Iterates over a configured number of weeks, searching for flight bargains for two users ("Pilar" and "David"):
    - For each user, retrieves origin/destination airports and search days from configuration.
    - For each leg (outbound/return) and each search day:
        - Skips dates in the past.
        - Scrapes flight data using the `Scrape` function.
        - Filters results by price and maximum travel duration.
        - Aggregates filtered results.
    - Combines outbound and return flights, calculates total price, and filters by price threshold.
    - Logs the number of valid combinations and adds each as a `Bargain` to the discovery object.
4. Waits a random interval between weeks to simulate human behavior.
5. Saves discovered bargains and sends a report via email.
Modules used:
- `datetime`, `pandas`
- Custom modules for configuration, logging, scraping, and reporting
Intended for use in both local and production environments, with logging to indicate the execution context.
"""
import datetime as dt
import pandas as pd

from config.config import BargainFinderConfig
from config.setup_logging import init_logger
from src.bargain_discovery.discoverer import Discovery
from src.bargain_discovery.bargain import Bargain
from src.google_flight_analysis.human_simulations import *
from src.google_flight_analysis.scrape import *
from src.report.report import BargainReporter
from src.telegram_bot.utils import report_warnings

conf = BargainFinderConfig()
discovery = Discovery()
logger = init_logger(__name__)
reporter = BargainReporter()

if conf.ENV == 'production':
    logger.info('Running Discovery in GitHub Actions!')
elif conf.ENV == 'local':
    logger.info('Running Discovery locally!')


today_date = dt.date.today()
today_weekday = dt.date.weekday(today_date)
delta_to_start = dt.timedelta(days=(-today_weekday + 7*conf.WEEK_START))
date_ref = today_date + delta_to_start

for week in range(conf.WEEKS_SEARCH):
    date_ref += dt.timedelta(7)
    week_str = f'{date_ref.isoformat()} to {(date_ref + dt.timedelta(6)).isoformat()}'
    logger.info(f'Checking week {week_str}')

    for tocinillo in ['Pilar', 'David']:
        if tocinillo == 'David':
            airports_origin = conf.AIRPORTS_DAVID[0]
            airports_dest = conf.AIRPORTS_DAVID[1]
            days_search = conf.DAYS_DAVID
        elif tocinillo == 'Pilar':
            airports_origin = conf.AIRPORTS_PILAR[0]
            airports_dest = conf.AIRPORTS_PILAR[1]
            days_search = conf.DAYS_PILAR

        candidates_df = [pd.DataFrame() for _ in range(2)]
        for leg,days in enumerate(days_search): 
            for day in days:
                day_date = date_ref + dt.timedelta(days=day-1)
                if day_date < today_date:
                    logger.warning(f"Date {day_date.isoformat()} is in the past --> Skipping.")
                    continue
                if leg == 0:
                    result = Scrape(airports_origin, airports_dest, day_date.isoformat())
                elif leg == 1:
                    result = Scrape(airports_dest, airports_origin, day_date.isoformat())
                ScrapeObjects(result, conf.ENV, headless=True)
                result_df = result.data
                if result_df.empty:
                    logger.warning(f"No results found for {day_date.isoformat()} --> Skipping.")
                    continue
                filter = ((result_df['Price'] < 0.9*conf.PRICE_THRESHOLD) 
                          & 
                          (result_df['Arrival datetime'] - result_df['Departure datetime']
                           < dt.timedelta(hours=conf.MAX_TRAVEL_HOURS)))
                filtered_df = result_df [filter]
                candidates_df[leg] = pd.concat([candidates_df[leg], filtered_df], axis=0)

        if candidates_df[0].empty or candidates_df[1].empty:
            logger.info(f'  No matches found for {tocinillo} in week {week_str}')
            continue
        combinations_df = candidates_df[0].merge(candidates_df[1], how='cross', suffixes=('_out', '_return'))
        try:
            combinations_df['Total Price'] = combinations_df['Price_out'] + combinations_df['Price_return']
            combinations_df = combinations_df[combinations_df['Total Price'] <= conf.PRICE_THRESHOLD]
        except KeyError:
            pass

        logger.info(f'  Found {len(combinations_df)} combinations for {tocinillo}')
        for idx in range(len(combinations_df)):
            bargain = Bargain(combinations_df.iloc[idx,:], week_str, tocinillo)
            discovery.add_bargain(bargain)

    random_wait(min_sec=1, max_sec=5)

discovery.save_bargains()
logger.info('Discovery jobs terminated successfully!')

logger.info('Sending email...')
reporter.send_report()

report_warnings(job = "Discovery")
