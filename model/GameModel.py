import sys
from pathlib import Path
from typing import Iterable
from unittest.mock import DEFAULT

from numpy import true_divide

ROOT_PATH = Path(__file__).parent.parent
sys.path.append(str(Path(__file__).parent.parent))

DATA_PATH = ROOT_PATH / "data"

import settings

from upgrades import Upgrade, UPGRADES
from levels import Level, LEVELS
from model.Simulation import EnergyModel

DEFAULT_SPEED = 24


class Curve:
    """Manages game time of timeseries in model time"""

    def __init__(
        self,
        label,
        points=None,
        x_list=None,
        y_list=None,
        display_y_offset=0,
        display_y_scale=1,
    ):
        self.wrap_length = 8760
        self.label = label
        if points is not None:
            self._mx_list, self.y_list = map(list, zip(*points))
        elif x_list is not None and y_list is not None:
            self._mx_list, self.y_list = x_list, y_list
        else:
            raise ValueError("Either points or x_list and y_list must be provided.")
        self.dyo = display_y_offset
        self.dys = display_y_scale

    def y_slice(self, start, stop):
        if not ((0 <= start < self.wrap_length) and (0 <= stop < self.wrap_length)):
            raise ValueError(f"Both {start=} and {stop=} must be between 0 and 8759")
        return (
            self.y_list[start:stop]
            if start <= stop
            else self.y_list[start:] + self.y_list[:stop]
        )

    def points_in_game(self, gamex_start, gamex_end):
        """returns the list of points in game time from the appropriate model time"""
        ys = self.y_slice(gamex_start % self.wrap_length, gamex_end % self.wrap_length)
        return [
            (x, (y + self.dyo) * self.dys)
            for x, y in zip(range(gamex_start, gamex_end), ys)
        ]

    def update_point(self, gamex, y):
        self.y_list[gamex % self.wrap_length] = y

    def update(self, point_or_points):
        if isinstance(point_or_points, tuple):
            gamex, y = point_or_points
            self.update_point(gamex, y)
        else:
            for gamex, y in point_or_points:
                self.update_point(gamex, y)

    def __repr__(self) -> str:
        return f"Curve({self.label=})"


class GameModel:
    money: int
    energy_discount: int

    forecast_hours: int
    backcast_hours: int

    speed: int
    paused: bool
    finished: bool
    heat_on: bool
    cool_on: bool

    model: EnergyModel
    hour: int  # ever increasing game hour
    _mh: int  # model hour (0-8759)
    final_hour_of_the_year: int  # after a year, wrap and reset

    curve_TI: Curve
    curve_TA: Curve
    curve_comfort_min: Curve
    curve_comfort_max: Curve
    curve_co2: Curve
    curve_date: Curve

    levels: Iterable[LEVELS]
    current_level: Level
    current_level_index: int

    def __init__(self, speed=24, godmode=False):
        global DEFAULT_SPEED
        DEFAULT_SPEED = speed  # simulated hours / game second
        self.godmode = godmode
        self.paused = False
        self.finished = False
        self.model = EnergyModel(DATA_PATH / settings.BUILDING_PATH, kWp=50)
        self.model.init_sim()
        self.hour = 0
        self._mh = 0  # energy model hour
        self.upgrades: dict[str, Upgrade] = UPGRADES
        self.levels = LEVELS
        self.setup_new_game()

    def toggle_godmode(self):
        self.godmode = not self.godmode
        status = "enabled" if self.godmod else "disabled"
        print(f"Godmode {status}!")

    def setup_new_game(
        self,
        starting_power=15,
        starting_cop=3,
    ):

        self.money = 1_000_000 if self.godmode else 1_000
        self.insulation_level = 0
        self.moneyspent = 0
        self.total_GHG_emitted = 0
        self.total_GHG_avoided = 0
        self.current_level_index = 0
        self.energy_discount = 0  # 0-100 [%]
        self.model.building.reset()
        self.set_heating_power(starting_power)
        self.set_cooling_power(starting_power)
        self.set_cop(starting_cop)
        self.setup_upgrades()
        self.reset_levels()

    def reset_levels(self):
        # self.levels = iter(LEVELS)
        # self.setup_next_level() # setup level 1
        self.total_comfort = 1  # average comfort score across all levels played
        self.total_duration = 0  # hours simulated across all levels played
        self.setup_level(0)

    def setup_next_level(self):
        self.current_level_index += 1
        self.setup_level(self.current_level_index)

    def setup_level(self, index=None):
        """Level number of optional, if missing, current level will be reset"""

        self.level_comfort = 100
        self.level_duration = 0
        if index is not None:
            self.current_level_index = index
        print(self.current_level_index)
        self.current_level = self.levels[self.current_level_index]
        self.set_speed(getattr(self.current_level, "speed", DEFAULT_SPEED))
        self.paused = self.current_level.start_paused
        start_hour = self.current_level.start

        if not (0 <= start_hour <= 8759):
            raise ValueError("Invalid start_hour. Must be between [0 and 8759].")
        self.hour = start_hour  # ever increasing
        self.final_hour_of_the_year = (self.current_level.end) % 8760
        self._mh = start_hour  # model hour always in [0-8759]

        self.model.comfort = self.current_level.comfort
        self.model.init_sim(start_hour=start_hour, TI_init=self.current_level.start_TI)

        self.forecast_hours = 72
        self.backcast_hours = 72
        self.curve_TI = Curve(
            "TI", points=[(h, ti) for h, ti in zip(range(8760), self.model.TI)]
        )
        self.curve_TA = Curve(
            "TA",
            points=[(h, ta) for h, ta in zip(range(8760), self.model.TA)],
            display_y_offset=+10,
        )
        self.curve_comfort_min = Curve(
            "Minimum comfort temperature",
            points=[
                (h, p)
                for h, p in zip(range(8760), self.model.comfort.TI_minimum_setpoints)
            ],
        )
        self.curve_comfort_max = Curve(
            "Minimum comfort temperature",
            points=[
                (h, p)
                for h, p in zip(range(8760), self.model.comfort.TI_maximum_setpoints)
            ],
        )
        self.curve_co2 = Curve(
            "CO2 Intensity",
            points=[(h, co2 * 100) for h, co2 in zip(range(8760), self.model.CO2)],
            display_y_offset=0,
        )
        self.curve_date = Curve(
            "Date",
            points=[(h, ts) for h, ts in zip(range(8760), self.model.timestamp)],
        )
        self.curve_pv = Curve(
            "PV",
            points=[(h, ts) for h, ts in zip(range(8760), self.model.PV.TSD)],
        )

        self.default_curve = Curve(
            "Default",
            points=[(h, 0) for h in range(8760)]
        )
        self.cleanup()

        return True

    def update_level_finished(self):
        """at the end of level, update comfort rating"""
        start, stop = self.current_level.start, self.current_level.end
        average = self.level_comfort
        l = len(self.model.comfort_score_tsd[start:stop])
        self.total_comfort = (
            self.total_duration * self.total_comfort + l * average
        ) / (l + self.total_duration)
        self.total_duration += l
        self.total_GHG_emitted += self.get_GHG_emitted()
        self.total_GHG_avoided += self.get_GHG_avoided()
        # print("Achieved comfort level (average):", average, "over", l, "hours")
        # print("Total comfort:", self.total_comfort, "over", self.total_duration, "hours total")

    def is_bankrupt(self) -> bool:
        if self.godmode:
            return False
        if self.money <= 0:
            return True
        return False

    def is_max_comfort_reached(self) -> bool:
        if self.godmode:
            return False

    def is_too_cold(self) -> bool:
        if self.godmode:
            return False
        if self.model.comfort.comfort_diff(self.TI) > 0:
            return False  # as long as TI - min setpoint is positive, no freeze
        cs = self.level_comfort
        mc = self.current_level.min_comfort
        if cs <= mc:
            print(f"FREEZE DEATH: comfort_score={cs} < min_comfort={mc}")
            return True
        return False

    def is_too_hot(self) -> bool:
        if self.godmode:
            return False
        if self.model.comfort.comfort_diff(self.TI) < 0:
            return False  # as long as TI - min setpoint is positive, no freeze
        cs = self.level_comfort
        mc = self.current_level.min_comfort
        if cs <= mc:
            print(f"HEAT DEATH: comfort_score={cs} < min_comfort={mc}")
            return True
        return False

    def update(self, hours: int):
        for _ in range(hours):
            year, self._mh = divmod(self.hour, 8760)
            

            if self._mh == self.final_hour_of_the_year:
                if not self.AUTOPILOT:
                    return
                else:
                    print("autopilot on")
                # print("next year")
                # self.next_year(year)
            if self.AUTOPILOT:
                self.money += 5


            self.model.timestep(hour=self._mh)

            if self.heat_on:
                self.model.apply_heat(self._mh)
            if self.cool_on:
                self.model.apply_cool(self._mh)

            self.model.calc_ED(self._mh)
            moneydelta = (
                self.model.ED[self._mh]
                * self.model.price_grid
                * (100 - self.energy_discount)
                / 100
            )
            self.moneyspent += moneydelta
            self.money -= moneydelta

            self.model.comfort.update(self._mh)
            self.model.comfort_score_tsd[self._mh] = self.model.comfort.comfort_score(
                self.TI
            )
            self.level_comfort = max(
                0, self.level_comfort - 0.1 * (100 - self.get_comfort_score())
            )
            # print(f"level average comfort: {self.level_comfort:.1f}%")

            self.curve_TI.update((self.hour, self.TI))

            self.hour += 1
            self.hour = self.hour % 8760

    def next_year(self, year=2020):
        self.hour = 0
        self._mh = 0

        self.model.init_sim(TI_init=self.model.TI[-1])

    def set_speed(self, simhours_per_second):
        """sets how many hours should be simulated for each second of the game"""
        self.speed = simhours_per_second

    def set_cop(self, cop):
        self.model.HVAC.HP_COP = cop

    def increment_cop(self, cop_change):
        self.model.HVAC.HP_COP += cop_change

    def set_heating_power(self, power):
        self.model.HVAC.HP_heating_power = power

    def set_cooling_power(self, power):
        self.model.HVAC.HP_cooling_power = power

    def toggle_pause(self):
        """Toggle the paused state of the game."""
        self.paused = not self.paused

        print(f"Game is {'paused' if self.paused else 'running'}")

    def heat(self):
        self.heat_on = True

    def cool(self):
        self.cool_on = True

    def cleanup(self):
        """cleans up logic and other flags for the next time step"""
        self.heat_on = False
        self.cool_on = False

    # model data wrappers
    def get_insulation(self):
        return self.model.building.LT

    def get_power(self):
        return self.model.HVAC.HP_heating_power

    def get_cop(self):
        return self.model.HVAC.HP_COP

    def get_hull_data(self) -> dict:
        return {"lines": self.model.building.__repr__()}

    def get_hvac_data(self) -> dict:
        return {"lines": self.model.HVAC.__repr__()}

    def get_ED(self):
        """total electricity used (kWh)"""
        return self.model.ED.sum() / 1000 * self.model.building.bgf

    def get_GHG_emitted(self):
        print("GHG_emitted", self.model.emissions.sum())
        return self.model.emissions.sum()

    def get_GHG_avoided(self):
        q = self.model.QH.sum() / 1000 * self.model.building.bgf
        gas_ghg = q * 0.201  # kg/kWh oib rl6'18
        return gas_ghg - self.get_GHG_emitted()

    def get_upgrade_text(self) -> dict:
        return {
            "lines": f"""
Insulation: Lvl {self.upgrades['wall_insulation'].level} ({round(self.model.building.LT, 2)} W/K/m²)

Heat Pump Power: Lvl {self.upgrades["power"].level} ({self.model.HVAC.HP_heating_power} W/m²)

Heat Pump Efficiency: Lvl {self.upgrades['heatpump_efficiency'].level} ({self.model.HVAC.HP_COP * 100} %)

Electricity Price Discount: Lvl {self.upgrades['electricity_price_discount'].level} ({self.energy_discount} %)
"""
        }  # todo: DUMMIES

    def get_remaining_level_hours(self):
        return self.final_hour_of_the_year - self.hour - 1

    def get_comfort_score(self):
        return self.model.comfort.comfort_score(self.TI)

    def get_temp_diff(self):
        return self.model.comfort.comfort_diff(self.TI)

    def get_menu_data(self) -> dict:
        return {
            "upgrades": self.upgrades,
            "player": {"money": round(self.money, 0)},
            "hull": self.get_hull_data(),
            "hvac": self.get_hvac_data(),
            "upgrade_text": self.get_upgrade_text(),
            "game_stats": self.get_game_stats(),
        }

    def get_curves_data(self):
        fc_index = self.hour + self.forecast_hours
        bc_index = self.hour - self.backcast_hours
        color = "comfort"
        if self.heat_on:
            color = "QH"
        if self.cool_on:
            color = "QC"
        return {
            "Indoor Temperature": self.curve_TI.points_in_game(bc_index, self.hour),
            "Outdoor Temperature": self.curve_TA.points_in_game(bc_index, fc_index),
            "Carbon Intensity": {
                "curve": self.curve_co2.points_in_game(bc_index, fc_index),
                "indicator": {
                    "pos": (self.hour, self.model.CO2[self.hour] * 100),
                    "text": f"CO2-Intensity: {self.model.CO2[self.hour]*100:.0f} g/kWh",
                },
            },
            "Minimum Comfort Temperature": {
                "curve": self.curve_comfort_min.points_in_game(bc_index, fc_index),
                "indicator": {
                    "pos": (self.hour - 30, self.model.comfort.minimum_room_temperature),
                    "text": f"Minimum Comfort Temperature: {self.model.comfort.minimum_room_temperature:.1f} °C",
                },
            },
            "Maximum Comfort Temperature": {
                "curve": self.curve_comfort_max.points_in_game(bc_index, fc_index),
                "indicator": {
                    "pos": (self.hour - 30, self.model.comfort.maximum_room_temperature),
                    "text": f"Maximum Comfort Temperature: {self.model.comfort.maximum_room_temperature:.1f} °C",
                },
            },
            "PV": {
                "curve": self.curve_pv.points_in_game(bc_index, fc_index),
                "base": self.default_curve.points_in_game(bc_index, fc_index),
                "indicator": {
                    "pos": (self.hour - 30, self.model.comfort.maximum_room_temperature),
                    "text": f"PV Ertrag: {self.model.PV.TSD[self._mh]:.1f} Wh",
                },
            } ,
            "TI Indicator": {
                "Position": self.position,
                "Comfort dT": self.get_temp_diff(),
                "Scale": self.get_comfort_score() / 100
                + 0.5 * (self.heat_on + self.cool_on),
                "Color": color,
                "score": self.get_comfort_score(),
            },
            "TA Indicator": {
                "TA": (self.hour, self.model.TA[self._mh]),
                "TI": (self.position[0]-5, self.position[1]-1),
            },
            "Date Indicator": [
                (x, ta + 18, ts)
                for (x, ta), ts in zip(
                    self.curve_TA.points_in_game(bc_index, fc_index),
                    self._timestamp_slice(bc_index, fc_index),
                )
                if ts.hour == 0
            ],
        }

    def get_ui_data(self):
        return {
            "player_activity": self.heat_on or self.cool_on,
            "Energy balance": {
                "anchorpoint": settings.UI_ANCHOR,
                "first": {
                    "QV": self.model.QV[self._mh] * 5,
                    "QT": self.model.QT[self._mh] * 5,
                },
                "second": {"QS": self.model.QS[self._mh] * 5},
                "QH": self.model.QH[self._mh] * 5,
                "QC": self.model.QC[self._mh] * 5,
            },
            "Scores": {
                "Money": int(self.money),
                "Comfort": {
                    "dT": self.model.comfort.comfort_diff(self.model.TI[self._mh]),
                    "score": self.level_comfort,
                    "change": self.get_comfort_score()
                    - self.model.comfort.comfort_score(self.model.TI[self._mh - 1]),
                },
            },
            "Price": f"Price {self.model.price_grid} €/Wh",
            "Feedin": f"Feed-In Price {self.model.price_feedin} €/Wh",
            "CO2": self.get_GHG_emitted(),
            "COP": f"Efficiency    {self.get_cop() * 100:.0f}%",
            "Power": f"Heating Power {self.get_power()} W/m²",
            "Remaining hours": f"{self.get_remaining_level_hours()}",
        }

    def get_kpis(self) -> dict:
        """Aggregierte Kennzahlen als zusammengefasste Werte für den End-of-Level-Bildschirm."""
        return {
            "Überlebte Stunden": f"{self.hour-self.current_level.start:.0f}%",
            "Erreichter Komfort": f"{self.level_comfort:.0f}%",
            "Verursachte CO2-Emissionen": f"{self.model.emissions.sum()/1000 * self.model.building.bgf:.0f} kg",
            "Detailergebnisse": "",
            "Benoetigte Heizenergie": f"{(self.model.QH.sum() / 1000 * self.model.building.bgf):.0f} kWh",
            "Benoetigte Kuehlenergie": f"{-self.model.QC.sum() / 1000 * self.model.building.bgf:.0f} kWh",
            "Verbrauchter Strom": f"{self.get_ED().sum():.0f} kWh",
            "Mittlerer Strompreis": f"{self.model.price_grid*100:.0f} ct/kWh",
            "": "",
            "Energiekosten ": f"{self.moneyspent:.0f} €",
            "Belohnung    ": f"{self.current_level.reward} €",
            "Saldo        ": f"{-self.moneyspent+self.current_level.reward:.0f} €",
        }

    def get_game_stats(self):
        current_level = self.current_level.name.split(":")[0]
        return {
            "lines": f"""
            Current Level    {current_level}
            Available Money  {self.money:.0f} €
            Average Comfort  {self.total_comfort:.0f}%
            Total CO2 caused  {self.total_GHG_emitted:.0f} kg
            Total GHG avoided {self.total_GHG_avoided:.0f} kg
        """
        }

    def setup_upgrades(self):
        def upgrade(upgrade: Upgrade, fn: callable):
            if upgrade.cost > self.money:
                print("Not enough money!")
                return False

            upgrade.level += 1
            self.money -= upgrade.cost
            fn()

        # todo: Use proper setter/getter functions throughout!
        def power():
            self.set_heating_power(self.model.HVAC.HP_heating_power + 1)
            self.set_cooling_power(self.model.HVAC.HP_cooling_power + 1)

        def wall_insulation():
            # todo: Hard coded key
            self.model.building.components["Aussenwand"].u_value *= 0.8
            self.model.building.components[
                "Dach"
            ].u_value *= 0.8  # IMPLEMENT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            self.model.building.components[
                "Fenster"
            ].u_value *= 0.8  # IMPLEMENT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            self.model.building.update_LT()
            if self.model.building.LT <= 0.4:
                self.insulation_level = 1
            if self.model.building.LT <= 0.2:
                self.insulation_level = 2

        def heatpump_efficiency():
            self.set_cop(self.model.HVAC.HP_COP + 0.5)

        def electricity_price_discount():
            self.energy_discount = min(
                90, self.energy_discount + 15 * (1 - self.energy_discount / 100)
            )

        self.upgrades["wall_insulation"].callback = lambda: upgrade(
            self.upgrades["wall_insulation"], wall_insulation
        )
        self.upgrades["power"].callback = lambda: upgrade(self.upgrades["power"], power)
        self.upgrades["heatpump_efficiency"].callback = lambda: upgrade(
            self.upgrades["heatpump_efficiency"], heatpump_efficiency
        )
        self.upgrades["electricity_price_discount"].callback = lambda: upgrade(
            self.upgrades["electricity_price_discount"], electricity_price_discount
        )

    @property
    def TI(self):
        return self.model.TI[self._mh]

    @property
    def position(self):
        """Game position is (x = hour, y = Indoor Temperature)"""
        return (self.hour, self.TI)

    @property
    def dT(self):
        return self.model.Q_loss[self._mh] / self.model.building.heat_capacity

    @property
    def qh(self):
        return self.model.QH[self._mh] / self.model.building.heat_capacity * 10

    @property
    def qc(self):
        return self.model.QC[self._mh] / self.model.building.heat_capacity * 10

    def _timestamp_slice(self, start, stop):
        start = start % 8760
        stop = stop % 8760

        if start <= stop:
            return list(self.model.timestamp.iloc[start:stop])
        else:
            return list(self.model.timestamp.iloc[start:]) + list(
                self.model.timestamp.iloc[:stop]
            )

    def __repr__(self) -> str:
        return f"t {self._mh:4} {self.hour:4}   Ti= {self.TI:.2f}°C   ED {self.model.ED.sum():.1f} Wh/m2"


if __name__ == "__main__":
    # test = GameModel(start_hour=7888)
    # print(test.get_curves_data())
    c = Curve("test", points=[(x, x) for x in range(8760)])
    print(c.points_in_game(8755, 8765))
    c.update((8760, "hello changed 8760"))
    print(c.points_in_game(8755, 8765))

    c.update(
        [
            (8761, "list of points 1"),
            (8762, "list of points 2"),
            (8765, "dont need to be in sequence"),
        ]
    )
    print(c.points_in_game(8755, 8766))
