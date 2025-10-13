import pandas as pd

from config.config import BargainFinderConfig

conf = BargainFinderConfig()

class Bargain():
    def __init__(self, combination_df: pd.DataFrame, week: str, tocinillo: str):
        self.week = week
        self.tocinillo = tocinillo
        self.ida = BargainFlight(combination_df, 'out')
        self.vuelta = BargainFlight(combination_df, 'return')
        self.new_bargain = False
        self.price_change = 0  # 0: same price, 1: cheaper, 2: more expensive
        self.total_price = combination_df['Total Price']


    def as_dict(self) -> dict:
        attrs = ['date', 'origin', 'destination', 'time', 'travel_time', 'airline', 'stops', 'price']
        bargain_dict = {attr: [str(getattr(self.ida, attr)), str(getattr(self.vuelta, attr))] for attr in attrs}
        bargain_dict['job'] = self.tocinillo
        bargain_dict['new'] = self.new_bargain
        bargain_dict['price_change'] = self.price_change
        bargain_dict['total_price'] = str(self.total_price)
        return bargain_dict
    
    
    @staticmethod
    def get_key(bargain) -> list:
        if isinstance(bargain, Bargain):
            bargain = bargain.as_dict()
        return (
            bargain["origin"][0], bargain["destination"][0], bargain["date"][0], bargain["time"][0],
            bargain["origin"][1], bargain["destination"][1], bargain["date"][1], bargain["time"][1]
        )


class BargainFlight():
    def __init__(self, combination_df, leg):
        flight_df = combination_df.filter(like=leg)

        self.origin = flight_df[f'Origin_{leg}']
        self.destination = flight_df[f'Destination_{leg}']
        self.date = flight_df[f'Departure datetime_{leg}'].strftime('%Y-%m-%d')
        self.time = flight_df[f'Departure datetime_{leg}'].strftime('%H:%M')
        self.travel_time = flight_df[f'Travel Time_{leg}']
        self.airline = flight_df[f'Airline(s)_{leg}']
        self.stops = str(flight_df[f'Num Stops_{leg}'])
        self.price = str(flight_df[f'Price_{leg}'])
