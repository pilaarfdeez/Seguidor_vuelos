import datetime as dt
import pandas as pd

from config.config import BargainFinderConfig
from config.logging import init_logger
from src.bargain_finder.discoverer import Discoverer
from src.bargain_finder.bargain import Bargain
from src.google_flight_analysis.human_simulations import *
from src.google_flight_analysis.scrape import *
from src.flight_tracker.report import BargainReporter

conf = BargainFinderConfig()
discoverer = Discoverer()
logger = init_logger(__name__)
reporter = BargainReporter()

if conf.ENV == 'production':
    logger.info('Running Discovery in GitHub Actions!')
elif conf.ENV == 'local':
    logger.info('Running Discovery locally!')


today_date = dt.date.today()
today_weekday = dt.date.weekday(today_date)
# today_isocalendar = dt.date.isocalendar(today_date)
# today_isocalendar.week
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
                if leg == 0:
                    result = Scrape(airports_origin, airports_dest, day_date.isoformat())
                elif leg == 1:
                    result = Scrape(airports_dest, airports_origin, day_date.isoformat())
                ScrapeObjects(result, conf.ENV, headless=True)
                result_df = result.data
                filter = ((result_df['Price'] < 0.9*conf.PRICE_THRESHOLD) 
                          & 
                          (result_df['Arrival datetime'] - result_df['Departure datetime']
                           < dt.timedelta(hours=conf.MAX_TRAVEL_HOURS)))
                filtered_df = result_df [filter]
                candidates_df[leg] = pd.concat([candidates_df[leg], filtered_df], axis=0)

        combinations_df = candidates_df[0].merge(candidates_df[1], how='cross', suffixes=('_out', '_return'))
        combinations_df['Total Price'] = combinations_df['Price_out'] + combinations_df['Price_return']

        combinations_df = combinations_df[combinations_df['Total Price'] <= conf.PRICE_THRESHOLD]

        for idx in range(len(combinations_df)):
            bargain = Bargain(combinations_df.iloc[idx,:], week_str, tocinillo)
            discoverer.add_bargain(bargain)

    random_wait(min_sec=1, max_sec=5)

discoverer.check_new_bargains()
discoverer.save_bargains()
logger.info('Discoverer jobs terminated successfully!')

logger.info('Sending email...')
reporter.send_report()
