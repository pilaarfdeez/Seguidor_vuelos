import datetime as dt
import json
import matplotlib.pyplot as plt
import os
import pandas as pd

from src.google_flight_analysis.flight import Flight

class TrackedFlight():
    def __init__(self, flight):
        if isinstance(flight, Flight):
            self.origin = flight.origin
            self.destination = flight.dest
            self.date = flight.date
            self.time = flight.time_leave.strftime('%H:%M')
            self.prices = [
                {'date': flight.search_date, 'price': flight.price},
                ]
            
        elif isinstance(flight, pd.DataFrame):
            if flight.shape[0] == 1:
                df = flight.iloc[0,:]
                
                self.origin = df['Origin']
                self.destination = df['Destination']
                self.date = df['Departure datetime'].strftime('%Y-%m-%d')
                self.time = df['Departure datetime'].strftime('%H:%M')
                self.prices = [{'date': df['Search Date'], 'price': df['Price']}]

            else:
                print(f'Wrong DataFrame size passed! Only one-row df is accepted, {flight.shape[0]} were provided --> ignoring flight')
                return

        else:
            self.origin = flight['origin']
            self.destination = flight['destination']
            self.date = flight['date']
            self.time = flight['time']
            try:
                self.prices = flight['prices']
            except KeyError:
                self.prices = []

        self.plot_name = f"{self.origin}{self.destination}_{self.date.replace('-', '')}_{self.time.replace(':', '')}"
    
    
    def __str__(self):
        return f"({self.origin}to{self.destination}, {self.date} at {self.time})"


    def as_dict(self):
        keys = ['origin', 'destination', 'date', 'time', 'prices']
        return {k: v for k, v in self.__dict__.items() if k in keys}
    

    def remove_last_price(self):
        if len(self.prices) >= 1:
            self.prices.remove(self.prices[-1])
        return
    

    def generate_plot(self):
        out_folder = 'data/images/'
        file_name = self.plot_name + '.png'
        out_path = os.path.join(out_folder, file_name)
        
        fig, ax = plt.subplots()
        X = [search['date'] for search in self.prices]
        Y = [int(search['price']) for search in self.prices]

        ax.plot(X, Y)
        ax.set_title(f'Evolución de precios')
        ax.grid()
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Precio (€)')

        fig.savefig(out_path)
        return
    

    def remove_plot(self):
        out_folder = 'data/images/'
        file_name = self.plot_name + '.png'
        out_path = os.path.join(out_folder, file_name)
        if os.path.exists(out_path):
            os.remove(out_path)
