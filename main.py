from src.google_flight_analysis.scrape import *


result = Scrape('AGP', 'HAM', '2025-05-15', '2025-05-20') # obtain our scrape object, represents out query

print(result) # get unqueried str representation

ScrapeObjects(result) # runs selenium through ChromeDriver, modifies results in-place
print(result.data) # returns pandas DF
print(result) # get queried representation of result

print('Loading the search results in flights.json')
result.data.to_json('data/flights.json', orient='records', indent=4)
print('Scraper jobs terminated successfully!')
