


import math
import random
import numpy as np
import pandas as pd


class Comfortmodel:
    def __init__(self) -> None:        
        self.heating_months = [1, 2, 3, 4, 9, 10, 11, 12]  # specify which months should the heating be useed
        self.minimum_room_temperature = 20.

        self.cooling_months = [4, 5, 6, 7, 8, 9]
        self.maximum_room_temperature = 26.

        self.timestamp =  pd.Series(np.arange('2021-01-01 00:00', '2022-01-01 00:00', dtype='datetime64[h]'))
        
        self.comfort = np.ones(8760)*100

        self.TI_minimum_setpoints = self.create_minimum_setpoints()
        self.TI_maximum_setpoints = self.create_maximum_setpoints()

        self.comfort_sensitivity = 1

        print(sum(self.TI_minimum_setpoints)/8760)

    def update(self, t, TI):
        pass


    def create_minimum_setpoints(self):
        mu = self.minimum_room_temperature

        p_change = 1 / 12          # average one change per 12 hours
        alpha = 0.25               # pull strength toward center (applied only on change)
        sigma = 0.8                # randomness on change

        points = [mu]

        for _ in range(1, 8760):
            x = points[-1]

            if random.random() < p_change:
                # mean-reverting "step"
                drift = alpha * (mu - x)
                noise = random.gauss(0, sigma)
                x = x + drift + noise

            points.append(x)

        return points
    
    def create_maximum_setpoints(self):
        p_change = 1 / 12          # average one change per day
        alpha = 0.4                # pull toward center of [1, 5]
        sigma = 0.8                # randomness of change

        dT_min = 1.0
        dT_max = 5.0
        dT_center = 3.0            # midpoint

        dT = dT_center
        Tmax = []

        for Tmin in self.TI_minimum_setpoints:
            if random.random() < p_change:
                drift = alpha * (dT_center - dT)
                noise = random.gauss(0, sigma)
                dT = dT + drift + noise

                # enforce bounds
                dT = max(dT_min, min(dT_max, dT))

            Tmax.append(Tmin + dT)

        return Tmax
    
    def comfort_diff(self, TI): #TODO: move to comfortModel
        """Kelvin difference to comfortable temp"""
        dmin = TI - self.minimum_room_temperature
        dmax = TI - self.maximum_room_temperature
        if dmin < 0:
            return dmin
        elif dmax > 0:
            return dmax
        else:
            return 0

    def comfort_score(self, TI): #TODO: move to comfort model
            d = abs(self.comfort_diff(TI))

            gamma = 1.6  # steepness
            score = 100 * math.exp(-math.log(2) * (d / self.comfort_sensitivity) ** gamma)

            return max(min(score, 100), 0)


    def heating_season(self, t):
        return self.timestamp[t].month in self.heating_months
    
    def cooling_season(self, t):
        return self.timestamp[t].month in self.cooling_months
