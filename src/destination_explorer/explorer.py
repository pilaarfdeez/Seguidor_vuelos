import datetime as dt
import pandas as pd
from src.destination_explorer.match import Match

class Explorer:
    def __init__(self, conf):
        self.conf = conf
        self.potential_matches = pd.DataFrame(
            columns=['Day', 'Country', 'City', 'Price_David', 'Price_Pilar', 'Flight_Time_David', 'Flight_Time_Pilar', 'Stops_David', 'Stops_Pilar']
        )
        self.matches = pd.DataFrame(columns=['Day', 'Country', 'City', 'Price_Pilar', 'Price_David', 'Flight_Time_Pilar', 'Flight_Time_David', 'Stops_Pilar', 'Stops_David'])

    def process_matches(self, day, country, results_david: pd.DataFrame, results_pilar: pd.DataFrame):
        # Process common destinations for outbound flights

        if results_david.empty or results_pilar.empty:
            return

        match_keys = ['City']
        cross_joined = results_david.merge(results_pilar, on=match_keys, suffixes=('_David', '_Pilar'))
        filter = (
            (cross_joined['Price_David'] + cross_joined['Price_Pilar']  < 0.9 * self.conf.MAX_PRICE) &
            (cross_joined['Flight_Time_David'] < dt.timedelta(hours=self.conf.MAX_TRAVEL_HOURS)) &
            (cross_joined['Flight_Time_Pilar'] < dt.timedelta(hours=self.conf.MAX_TRAVEL_HOURS))
        )
        joined_filtered = cross_joined[filter]
        if joined_filtered.empty:
            return

        joined_filtered['Day'] = day
        joined_filtered['Country'] = country
        self.potential_matches = pd.concat([self.potential_matches, joined_filtered], axis=0)


    def verify_matches(self, results_david, results_pilar):
        pass