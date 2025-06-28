"""
This script runs a custom flight discovery and reporting workflow based on jobs defined in a JSON configuration file.
It performs the following steps for each custom job:
1. Loads configuration and initializes logging.
2. Reads custom job definitions from 'config/custom_jobs.json'.
3. For each job:
    - Initializes a Discovery object and a CustomBargainReporter.
    - Calculates the search window in weeks and iterates through each week.
    - For each leg (outbound and return), scrapes flight data for specified days, filters results by price and trip duration, and aggregates candidates.
    - Combines outbound and return flights to form round-trip combinations, filtering by total price.
    - Creates Bargain objects for each valid combination and adds them to the discovery.
    - Saves discovered bargains to a JSON file and sends a report via email.
    - Waits a random interval between jobs to simulate human behavior.
4. Logs the completion of all jobs.
Modules used:
- datetime, json, pandas
- Custom modules for configuration, logging, scraping, discovery, and reporting
Intended for use in both local and production environments.
"""
import datetime as dt
import json
import pandas as pd

from config.config import BargainFinderConfig
from config.logging import init_logger
from src.bargain_discovery.discoverer import Discovery
from src.bargain_discovery.bargain import Bargain
from src.google_flight_analysis.human_simulations import *
from src.google_flight_analysis.scrape import *
from src.flight_tracker.report import CustomBargainReporter

conf = BargainFinderConfig()
logger = init_logger(__name__)

if conf.ENV == 'production':
    logger.info('Running Discovery in GitHub Actions!')
elif conf.ENV == 'local':
    logger.info('Running Discovery locally!')

with open(f"config/custom_jobs.json", "r", encoding="utf-8") as f:  
    custom_jobs = json.load(f)

for job in custom_jobs:
    discovery = Discovery()
    reporter = CustomBargainReporter(job)

    today_date = dt.date.today()
    day_start = dt.date.fromisoformat(job["days_search"][0])
    day_stop = dt.date.fromisoformat(job["days_search"][1])

    start_isoweek = dt.date.isocalendar(day_start).week
    stop_isoweek = dt.date.isocalendar(day_stop).week
    weeks_search = stop_isoweek - start_isoweek + 1

    start_weekday = dt.date.weekday(day_start)  # 0 is Monday, 6 is Sunday
    delta_to_start = dt.timedelta(days=-start_weekday)
    date_ref = day_start + delta_to_start  # Starts on a Monday

    airports_origin = job['airports'][0]
    airports_dest = job['airports'][1]
    days_search = job['days_availability']    

    for week in range(weeks_search):
        week_str = f'{date_ref.isoformat()} to {(date_ref + dt.timedelta(6)).isoformat()}'
        logger.info(f'Checking week {week_str}')

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
                filter = ((result_df['Price'] < 0.9*job['price_threshold']) 
                          & 
                          (result_df['Arrival datetime'] - result_df['Departure datetime']
                           < dt.timedelta(hours=job['max_trip_duration'])))
                filtered_df = result_df [filter]
                candidates_df[leg] = pd.concat([candidates_df[leg], filtered_df], axis=0)

        combinations_df = candidates_df[0].merge(candidates_df[1], how='cross', suffixes=('_out', '_return'))
        combinations_df['Total Price'] = combinations_df['Price_out'] + combinations_df['Price_return']

        combinations_df = combinations_df[combinations_df['Total Price'] <= job['price_threshold']]

        logger.info(f'  Found {len(combinations_df)} combinations for week {week_str}')
        for idx in range(len(combinations_df)):
            bargain = Bargain(combinations_df.iloc[idx,:], week_str, job['name'])
            discovery.add_bargain(bargain)
            
        date_ref += dt.timedelta(7)
        
    logger.info(f'Job {job["name"]} terminated successfully. Saving deals...')
    discovery.save_bargains(file=f'bargains_{job["alias"]}.json')
    logger.info('Sending email...')
    reporter.send_report()

    random_wait(min_sec=1, max_sec=5)

logger.info('All custom jobs terminated successfully!')

    
