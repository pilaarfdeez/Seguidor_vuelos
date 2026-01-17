import datetime as dt
import json
import pandas as pd

from config.logging import init_logger
from src.google_flight_analysis.airport import Airport
from src.google_flight_analysis.human_simulations import random_wait
# from src.destination_explorer.match import Match

logger = init_logger(__name__)
airp_helper = Airport() 

class Explorer:
    def __init__(self, conf):
        self.conf = conf

        self.match_columns=['Day', 'Country', 'City', 'Total_Price', 'Price_David', 'Price_Pilar', 'Travel_Time_David', 'Travel_Time_Pilar', 'Stops_David', 'Stops_Pilar']
        self.potential_matches = [pd.DataFrame(columns=self.match_columns), pd.DataFrame(columns=self.match_columns)]
        self.matches = pd.DataFrame(columns=self.match_columns)

        with open('data/country_codes.json', "r", encoding="utf-8") as f:
            self.country_to_fb = json.load(f)  # Dictionary mapping country names to Freebase IDs
        with open('data/city_codes.json', "r", encoding="utf-8") as f:
            self.city_to_fb = json.load(f)  # Dictionary mapping (city, country) tuples to Freebase IDs
        self.missing_ids = []

    def to_dict(self, matches='real'):
        if matches == 'potential':
            matches_df = self.potential_matches[0].copy()
        elif matches == 'real':
            matches_df = self.matches.copy()

        matches_dict = []
        for day in matches_df['Day'].unique():
            day_matches = matches_df[matches_df['Day'] == day].drop(columns=['Day'])

            # Format flight times as 'Xh Ymin'
            def format_travel_time(td):
                total_minutes = pd.to_timedelta(td).total_seconds() // 60
                hours = int(total_minutes // 60)
                minutes = int(total_minutes % 60)
                return f"{hours}h {minutes}min"
            for col in day_matches.columns:
                if 'Price' in col:
                    day_matches[col] = day_matches[col].apply(lambda x: f"{x}€")
                elif 'Travel_Time' in col:
                    day_matches[col] = day_matches[col].apply(format_travel_time)

            matches_dict.append({
                'Day': day,
                'Matches': day_matches.to_dict(orient='records')
            })
        return matches_dict

    def sort_matches(self, matches='both'):
        if matches in ['potential', 'both']:
            self.potential_matches[0] = self.potential_matches[0].sort_values(by=['Day', 'Total_Price', 'Country', 'City'])
        if matches in ['real', 'both']:
            self.matches = self.matches.sort_values(by=['Total_Price', 'Day', 'Country', 'City'])


    def process_matches(self, day, country, results_david: pd.DataFrame, results_pilar: pd.DataFrame):
        # Process common destinations for outbound flights

        if results_david.empty or results_pilar.empty:
            return

        match_keys = ['City']
        cross_joined = results_david.merge(results_pilar, on=match_keys, suffixes=('_David', '_Pilar'))
        filter = (
            (cross_joined['Price_David'] + cross_joined['Price_Pilar']  < 0.6 * self.conf.MAX_PRICE) &
            (cross_joined['Travel_Time_David'] < dt.timedelta(hours=self.conf.MAX_TRAVEL_HOURS)) &
            (cross_joined['Travel_Time_Pilar'] < dt.timedelta(hours=self.conf.MAX_TRAVEL_HOURS))
        )
        joined_filtered = cross_joined[filter].copy()
        if joined_filtered.empty:
            return

        joined_filtered.loc[:, 'Day'] = day
        joined_filtered.loc[:, 'Country'] = country
        joined_filtered.loc[:, 'Total_Price'] = joined_filtered['Price_David'] + joined_filtered['Price_Pilar']

        return joined_filtered


    def create_combinations(self):
        combinations_df = (
            self.potential_matches[0].set_index(['City', 'Country'])
            .merge(
                self.potential_matches[1].set_index(['City', 'Country']), 
                left_index=True, right_index=True, how='inner', suffixes=('_out', '_return')
            )
            .reset_index()
        )

        if combinations_df.empty:
            return
        
        matches_df = pd.DataFrame({
            'City': combinations_df['City'],
            'Country': combinations_df['Country']
        })

        double_columns = [c for c in self.match_columns if f'{c}_out' in combinations_df.columns and f'{c}_return' in combinations_df.columns]
        for col in double_columns:
            if col == 'Total_Price':
                matches_df[col] = (
                    combinations_df[f'{col}_out']  #.str.replace('€', '').astype('int') 
                    +
                    combinations_df[f'{col}_return']  #.str.replace('€', '').astype('int')
                )
                continue
            matches_df[col] = list(zip(combinations_df[f'{col}_out'], combinations_df[f'{col}_return']))

        matches_df = matches_df[matches_df['Total_Price'] <= self.conf.MAX_PRICE]

        self.matches = matches_df[self.match_columns]
        self.sort_matches(matches='real')


    def save_matches(self, matches='real'):
        self.sort_matches()
        with open(f"data/{matches}_matches.json", "w+") as file:
            json.dump(self.to_dict(matches=matches), file, indent=4)


    def get_freebase_ids(self, sleep=0.5, matches='potential'):
        if matches == 'potential':
            matches_df = self.potential_matches[0].copy()
        elif matches == 'real':
            matches_df = self.matches.copy()

        unique_cities = matches_df[["City", "Country"]].drop_duplicates()
        logger.info(f"Retrieving Freebase IDs for {len(unique_cities)} unique cities.")

        for _, row in unique_cities.iterrows():
            city = row["City"]
            country = row["Country"]

            if (city, country) in self.city_to_fb:
                fb_id = self.city_to_fb[(city, country)]
                logger.debug(f"Found cached FreebaseID for {city} ({fb_id})")
                continue

            try:
                fb_id = airp_helper.to_freebase_id(city, country)
                logger.debug(f"Received FreebaseID for {city} ({fb_id})")
                if fb_id:
                    self.city_to_fb[(city, country)] = fb_id

            except Exception as e:
                logger.warning(f"Error retrieving Freebase ID for {city}, {country}: {e}")
                self.missing_ids.append((city, country))
            random_wait(sleep, 1.05*sleep)  # polite rate limiting

        # Sort and export dictionary for future use
        self.city_to_fb = dict(sorted(self.city_to_fb.items(), key=lambda x: (x[0][1], x[0][0])))
        with open("data/city_codes.json", "w+", encoding="utf-8") as f:
            json.dump(self.city_to_fb, f, indent=4)
