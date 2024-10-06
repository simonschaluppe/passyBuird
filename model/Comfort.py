


import numpy as np
import pandas as pd


class Comfortmodel:
    def __init__(self) -> None:        
        self.heating_months = [1, 2, 3, 4, 9, 10, 11, 12]  # specify which months should the heating be useed
        self.minimum_room_temperature = 20.

        self.cooling_months = [4, 5, 6, 7, 8, 9]
        self.maximum_room_temperature = 26.

        self.timestamp =  pd.Series(np.arange('2021-01-01 00:00', '2022-01-01 00:00', dtype='datetime64[h]'))
        

    def heating_season(self, t):
        return self.timestamp[t].month in self.heating_months
    
    def cooling_season(self, t):
        return self.timestamp[t].month in self.cooling_months
