import datetime as dt
import json
import pandas as pd

from config.logging import init_logger
# from src.destination_explorer.match import Match

logger = init_logger(__name__)

class Explorer:
    def __init__(self, conf):
        self.conf = conf

        columns=['Day', 'Country', 'City', 'Price_David', 'Price_Pilar', 'Total_Price', 'Flight_Time_David', 'Flight_Time_Pilar', 'Stops_David', 'Stops_Pilar']
        self.potential_matches = pd.DataFrame(columns=columns)
        self.matches = pd.DataFrame(columns=columns)

    def to_dict(self, matches='real'):
        if matches == 'potential':
            matches_df = self.potential_matches.copy()
        elif matches == 'real':
            matches_df = self.matches.copy()

        matches_dict = []
        for day in matches_df['Day'].unique():
            day_matches = matches_df[matches_df['Day'] == day].drop(columns=['Day'])

            # Format flight times as 'Xh Ymin'
            def format_flight_time(td):
                total_minutes = pd.to_timedelta(td).total_seconds() // 60
                hours = int(total_minutes // 60)
                minutes = int(total_minutes % 60)
                return f"{hours}h {minutes}min"
            for col in day_matches.columns:
                if 'Price' in col:
                    day_matches[col] = day_matches[col].apply(lambda x: f"{x}€")
                elif 'Flight_Time' in col:
                    day_matches[col] = day_matches[col].apply(format_flight_time)

            matches_dict.append({
                'Day': day,
                'Matches': day_matches.to_dict(orient='records')
            })
        return matches_dict

    def sort_matches(self):
        self.potential_matches = self.potential_matches.sort_values(by=['Day', 'Total_Price', 'Country', 'City'])
        self.matches = self.matches.sort_values(by=['Day', 'Total_Price', 'Country', 'City'])


    def process_matches(self, day, country, results_david: pd.DataFrame, results_pilar: pd.DataFrame):
        # Process common destinations for outbound flights

        if results_david.empty or results_pilar.empty:
            return

        match_keys = ['City']
        cross_joined = results_david.merge(results_pilar, on=match_keys, suffixes=('_David', '_Pilar'))
        filter = (
            (cross_joined['Price_David'] + cross_joined['Price_Pilar']  < 0.6 * self.conf.MAX_PRICE) &
            (cross_joined['Flight_Time_David'] < dt.timedelta(hours=self.conf.MAX_TRAVEL_HOURS)) &
            (cross_joined['Flight_Time_Pilar'] < dt.timedelta(hours=self.conf.MAX_TRAVEL_HOURS))
        )
        joined_filtered = cross_joined[filter].copy()
        if joined_filtered.empty:
            return

        joined_filtered.loc[:, 'Day'] = day
        joined_filtered.loc[:, 'Country'] = country
        joined_filtered.loc[:, 'Total_Price'] = joined_filtered['Price_David'] + joined_filtered['Price_Pilar']
        self.potential_matches = pd.concat([self.potential_matches, joined_filtered], axis=0)
        logger.info(f"--> {len(joined_filtered)} potential matches found!")


    def verify_matches(self, results_david, results_pilar):
        pass

    def save_matches(self, matches='real'):
        self.sort_matches()
        with open(f"data/{matches}_matches.json", "w+") as file:
            json.dump(self.to_dict(matches=matches), file, indent=4)
