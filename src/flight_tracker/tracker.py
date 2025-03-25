from itertools import groupby
import json
import pandas as pd

from config.logging import init_logger
from src.google_flight_analysis.flight import Flight
from src.flight_tracker.tracked_flight import TrackedFlight

logger = init_logger(__name__)

#TODO: tracked_flights must be a list of TrackedFlight objects and not dictionaries... come on...


class Tracker:
    def __init__(self):
        try:
            self.tracked_flights = []
            with open("data/tracked_flights.json", "r") as file:
                json_flights = json.load(file)
            for flight in json_flights:
                tracked_flight = TrackedFlight(flight)
                self.tracked_flights.append(tracked_flight)

        except FileNotFoundError:
            self.tracked_flights = []

    
    def tracked_flights_dict(self):
        tracked_flights_dict = []
        for flight in self.tracked_flights:
            tracked_flights_dict.append(flight.as_dict())
        return tracked_flights_dict


    def process_flight(self, flight: Flight = None, tracked_flight: TrackedFlight = None):
        if flight:
            new_flight = TrackedFlight(flight)
        elif tracked_flight:
            new_flight = tracked_flight
        
        classified_flight = self.classify_flight(new_flight)
        if classified_flight[0] == 'new':
            self.tracked_flights.append(new_flight)
            logger.debug('Adding new flight')

        elif classified_flight[0] == 'existing':
            idx = classified_flight[1]
            self.tracked_flights[idx].prices.append(new_flight.prices[0])
            logger.debug('Adding new price')


    def delete_flight(self, tracked_flight: TrackedFlight):
        classified_flight = self.classify_flight(tracked_flight)
        if classified_flight[0] == 'new':
            logger.warning('Tried to delete a non-tracked flight')
        elif classified_flight[0] == 'existing':
            logger.info('Removing flight...')
            flight_remove = self.tracked_flights[classified_flight[1]]
            self.tracked_flights.remove(flight_remove)


    def classify_flight(self, new_flight: TrackedFlight) -> list:
        new_flight = new_flight.as_dict()
        is_new = True
        for idx, tracked_flight in enumerate(self.tracked_flights):
            tracked_flight_dict = tracked_flight.as_dict()
            if all(new_flight[key] == tracked_flight_dict[key] for key in new_flight.keys() if key != 'prices'):
                is_new = False
                break

        if is_new:
            return ['new']
        elif new_flight['prices'] == []:
            return ['skip']  # no need to re-initialize an existing flight
        elif self.tracked_flights[idx].prices == []:
            return ['existing', idx]  # append flight price straightaway if there are no historical prices
        elif self.tracked_flights[idx].prices[-1]['date'] != new_flight['prices'][0]['date']:
            return ['existing', idx]  # if there are historical prices, check that it hasn't been checked today yet
        elif self.tracked_flights[idx].prices[-1]['price'] != new_flight['prices'][0]['price']:
            self.tracked_flights[idx].remove_last_price()
            return ['existing', idx]  # if it was checked today but the price has changed anyways
        else:
            return ['skip']
        
    
    def sort_flights(self):
        sorted_flights = sorted(self.tracked_flights, key=lambda f: (f.date, f.origin, f.destination, f.time))
        self.tracked_flights = sorted_flights

    
    def group_flights(self) -> dict:
        self.sort_flights()
        grouped_flights = {key: list(group) 
                           for key, group in groupby(self.tracked_flights, key=lambda f: (f.date, f.origin, f.destination))}
        return grouped_flights
    

    def new_prices(self):
        self.sort_flights()
        updated_flights = []
        updated_flights = [flight for flight in self.tracked_flights 
                           if len(flight.prices) >= 2 if flight.prices[-1]['price'] != flight.prices[-2]['price']]
        return updated_flights


    def save_flights(self):
        logger.info('Saving updated flight information...')
        self.sort_flights()
        with open("data/tracked_flights.json", "w") as file:
            json.dump(self.tracked_flights_dict(), file, indent=4)
            