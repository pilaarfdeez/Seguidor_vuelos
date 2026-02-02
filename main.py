from src.google_flight_analysis.scrape import *
from src.telegram_bot.utils import report_warnings

from config.setup_logging import init_logger
logger = init_logger(__name__)


result = Scrape(['AGP'], ["LBC"], '2026-11-16') # obtain our scrape object, represents out query

print(result) # get unqueried str representation

ScrapeObjects(result, "local", headless=False) # runs selenium through ChromeDriver, modifies results in-place
print(result.data) # returns pandas DF
print(result) # get queried representation of result

# print('Loading the search results in flights.json')
# result.data.to_json('data/flights.json', orient='records', indent=4)
# print('Scraper jobs terminated successfully!')

report_warnings(job = "Scrape Test")
