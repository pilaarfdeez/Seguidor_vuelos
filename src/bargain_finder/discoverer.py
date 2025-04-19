import datetime as dt
from itertools import groupby
import json
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import os
import pandas as pd

from config.config import BargainFinderConfig
from config.logging import init_logger
from src.bargain_finder.bargain import Bargain

conf = BargainFinderConfig()
logger = init_logger(__name__)

class Discoverer():
    def __init__(self):
        self.bargains = []


    # This defines which format the bargains are saved in
    def bargains_dict(self):
        bargains_dict = []
        for key, bargains in self.group_bargains().items():
            combination_group = {
                'week': key,
                'combinations': []
            }
            for bargain in bargains:
                combination_group['combinations'].append(bargain.as_dict())
            bargains_dict.append(combination_group)

        return bargains_dict


    def add_bargain(self, bargain: Bargain):
        self.bargains.append(bargain)


    def sort_bargains(self):
        self.bargains = sorted(self.bargains, key=lambda f: (f.week, f.tocinillo, int(f.total_price)))


    def group_bargains(self) -> dict:
        self.sort_bargains()
        grouped_bargains = {key: list(group) 
                           for key, group in groupby(self.bargains, key=lambda f: (f.week))}
        return grouped_bargains
    

    def group_bargains_by(self, bargain_list: list, by: str) -> dict:
        grouped_bargains = {key: list(group) 
                           for key, group in groupby(bargain_list, key=lambda f: (f[by]))}
        return grouped_bargains
    

    def check_new_bargains(self):
        with open("data/bargains.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, new_bargains in self.group_bargains().items():  # every week
            old_bargains = next((week['combinations'] for week in data if week['week'] == key), [])
            old_bargain_prices = {}
            for bargain in old_bargains:  # build compare price dictionary
                k = Bargain.get_key(bargain)
                old_bargain_prices[k] = int(bargain["total_price"])
            for bargain in new_bargains:
                k = Bargain.get_key(bargain)
                if k not in old_bargain_prices:
                    bargain.new_bargain = True
                elif int(bargain.total_price) != old_bargain_prices[k]:
                    bargain.new_price = True 

    
    def save_bargains(self):
        logger.info('Saving bargains...')
        self.sort_bargains()
        self.check_new_bargains()
        with open("data/bargains.json", "w") as file:
            json.dump(self.bargains_dict(), file, indent=4)


    def generate_plot(self, from_json: bool = True):
        out_folder = 'data/images/'
        file_name = 'bargains.png'
        out_path = os.path.join(out_folder, file_name)

        if from_json:
            with open("data/bargains.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            fig, ax = plt.subplots()

            end_date = dt.datetime.today() + dt.timedelta(weeks=conf.WEEK_START)
            for week_data in data:
                grouped_bargains = self.group_bargains_by(week_data['combinations'], 'tocinillo')
                for tocinillo,bargains in grouped_bargains.items():
                    if tocinillo == 'David':
                        color = 'blue'
                    elif tocinillo == 'Pilar':
                        color = 'orange'
                    for bargain in bargains:
                        X = [dt.datetime.strptime(date, "%Y-%m-%d") for date in bargain['date']]
                        Y = [int(bargain['total_price']), int(bargain['total_price'])]
                        ax.plot(X, Y, color=color)
                        if end_date < X[1]:
                            end_date = X[1]

            # ax.grid()
            fig.autofmt_xdate(rotation=45)
            date_format = DateFormatter('%Y-%m-%d')
            ax.xaxis.set_major_formatter(date_format)

            # dates = pd.date_range("2025-04-01", "2025-04-30", freq="D")
            start_date = dt.datetime.today() + dt.timedelta(weeks=conf.WEEK_START-1)
            dates = [start_date + dt.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
            for date in dates:
                if date.weekday() == 4:
                    start = date
                    end = date + dt.timedelta(days=2)
                    ax.axvspan(start, end, color="lightgray", alpha=0.5)

            ax.set_title(f'Chollazos próximos')
            ax.set_ylabel('Precio total (€)')

            fig.savefig(out_path)
            return
        
        else:
            logger.warning('Not implemented')
