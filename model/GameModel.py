import random
from typing import Any

import numpy as np

from model.Simulation import EnergyModel
from entities import Curve

class GameModel:
    def __init__(self, dt=1, start_hour=0) -> None:
        self.hour = start_hour
        if start_hour == 0:
            self.stop_hour = 8759
        else: self.stop_hour = start_hour - 1
        self.dt = dt
        self.paused = False
        self.finished = False
        self.model = EnergyModel()
        self.model.init_sim(dt=self.dt)

        self.model.HVAC.HP_heating_power = 30
        self.model.HVAC.HP_cooling_power = 30
        self.model.HVAC.HP_COP = 1
        
        self.heat_on = False    
        self.cool_on = False

        self.forecast_hours = 72

        self.temperature_curve = Curve()
        self.outdoor_temp_curve = Curve.from_points(self.model.TA[self.hour:self.hour+self.forecast_hours], self.hour, "blue")
        self.curve_comfort_min = Curve.from_points(
            [self.model.comfort.minimum_room_temperature]*self.forecast_hours,self.hour, "lightblue")
        self.curve_comfort_max = Curve.from_points(
            [self.model.comfort.maximum_room_temperature]*self.forecast_hours,self.hour, "orange")
        self.curves = {
            "Temperature Curve": self.temperature_curve,
            "Outdoor Temperature": self.outdoor_temp_curve,
            "Minimum Comfort Temperature": self.curve_comfort_min,
            "Maximum Comfort Temperature": self.curve_comfort_max,
        }

    @property
    def position(self):
        """Game position is (x = hour, y = Indoor Temperature)"""
        return (self.hour, self.model.TI[self.hour])
    
    @property
    def dT(self):
        return self.model.Q_loss[self.hour]/self.model.building.heat_capacity

    @property
    def qh(self):
        return self.model.QH[self.hour]

    @property
    def comfort_diff(self):
        """Kelvin difference to comfortable temp"""
        dmin = self.model.TI[self.hour] - self.model.comfort.minimum_room_temperature
        dmax = self.model.TI[self.hour] - self.model.comfort.maximum_room_temperature
        if dmin < 0:
            return dmin
        elif dmax > 0:
            return dmax
        else:
            return 0
    

    @property
    def qc(self):
        return self.model.QC[self.hour]

    def toggle_pause(self):
        """Toggle the paused state of the game."""
        self.paused = not self.paused
        print(f"Game is {'paused' if self.paused else 'running'}")

    def heat(self):
        self.heat_on = True

    def cool(self):
        self.cool_on = True 

    def set_speed(self, speed):
        self.dt = speed

    def update(self):
        for _ in range(self.dt):
            if self.hour == self.stop_hour:
                pass
                #  if input("rerun year? (Y/N").capitalize() != "Y":
                #     self.finished = True
                #     return
            if self.hour == 8759: 
                self.hour = 0
            self.hour += 1
            self.model.timestep(hour=self.hour)

            if self.heat_on:
                self.model.apply_heat(self.hour)
            if self.cool_on:
                self.model.apply_cool(self.hour)
            #print(self.model.TI[self.hour])
            self.model.calc_ED(self.hour)

            x_horizon = min(self.hour + self.forecast_hours, 8759)
            self.temperature_curve.update(self.position)
            self.outdoor_temp_curve.update((x_horizon, self.model.TA[x_horizon]))
            self.curve_comfort_min.extend()  
            self.curve_comfort_max.extend()

    def cleanup(self):
        """cleans up logic and other flags for the next time step"""
        self.heat_on = False
        self.cool_on = False
        
    def get_insulation(self)->dict:
        return self.model.building.LT

    def get_power_info(self)->dict:
        return self.model.HVAC.HP_heating_power, self.model.HVAC.HP_COP
    
    def __repr__(self) -> str:
        return f"hour: {self.hour:4}  Ti= {self.model.TI[self.hour]:.2f}°C   ED {self.model.ED.sum():.1f} Wh/m2"