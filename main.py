from src.google_flight_analysis.scrape import *


result = Scrape('AGP', 'HAM', '2025-07-20', '2025-08-20') # obtain our scrape object, represents out query
# result.type # This is in a round-trip format
# result.origin # ['JFK', 'IST']
# result.dest # ['IST', 'JFK']
# result.dates # ['2023-07-20', '2023-08-20']
print(result) # get unqueried str representation

ScrapeObjects(result) # runs selenium through ChromeDriver, modifies results in-place
print(result.data) # returns pandas DF
print(result) # get queried representation of result