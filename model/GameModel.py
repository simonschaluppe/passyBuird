import sys
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent
sys.path.append(str(Path(__file__).parent.parent))

DATA_PATH = ROOT_PATH / "data"

from model.Simulation import EnergyModel

UPGRADES = [
    {
        "name": "Wall Insulation",
        "cost": 1000,
        "image": "wall.png",
        "available": True,
    },
    {
        "name": "New Windows",
        "cost": 1500,
        "image": "window.png",
        "available": False,
    },
    {
        "name": "HVAC Upgrade",
        "cost": 2000,
        "image": "hvac.png",
        "available": True,
    },
]


class Curve:
    """Manages game time of timeseries in model time"""

    def __init__(self, label, points=None, x_list=None, y_list=None):
        self.wrap_length = 8760
        self.label = label
        if points is not None:
            self._mx_list, self.y_list = map(list, zip(*points))
        elif x_list is not None and y_list is not None:
            self._mx_list, self.y_list = x_list, y_list
        else:
            raise ValueError("Either points or x_list and y_list must be provided.")

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
        return [(x, y) for x, y in zip(range(gamex_start, gamex_end), ys)]

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

    def update(self, hours: int):
        for _ in range(hours):
            year, self._mh = divmod(self.hour, 8760)
            if self._mh == self.final_hour_of_the_year:
                print("next year")
                self.next_year(year)

            self.model.timestep(hour=self._mh)

            if self.heat_on:
                self.model.apply_heat(self._mh)
            if self.cool_on:
                self.model.apply_cool(self._mh)

            self.model.calc_ED(self._mh)
            self.money -= self.model.ED[self._mh] * self.model.price_grid
            self.model.comfort_score_tsd[self._mh] = self.comfort_score

            self.curve_TI.update((self.hour, self.TI))

            self.hour += 1

    def next_year(self, year=2020):
        self.hour = 0
        self._mh = 0
        self.model.init_sim()

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
        return self.model.QH[self._mh]

    @property
    def comfort_diff(self):
        """Kelvin difference to comfortable temp"""
        dmin = self.TI - self.model.comfort.minimum_room_temperature
        dmax = self.TI - self.model.comfort.maximum_room_temperature
        if dmin < 0:
            return dmin
        elif dmax > 0:
            return dmax
        else:
            return 0

    @property
    def comfort_score(self):
        return max(100 - 20 * abs(self.comfort_diff), 0)

    @property
    def qc(self):
        return self.model.QC[self._mh]

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

    def get_menu_data(self) -> dict:
        return {
            "upgrades": self.upgrades,
            "player": {"money": self.money},
            "hull": self.get_hull_data(),
            "hvac": self.get_hvac_data(),
        }

    def get_curves_data(self):
        fc_index = self.hour + self.forecast_hours
        bc_index = self.hour - self.backcast_hours
        return {
            "Indoor Temperature": self.curve_TI.points_in_game(bc_index, self.hour),
            "Outdoor Temperature": self.curve_TA.points_in_game(bc_index, fc_index),
            "Carbon Intensity": self.curve_co2.points_in_game(bc_index, fc_index),
            "Minimum Comfort Temperature": self.curve_comfort_min.points_in_game(
                bc_index, fc_index
            ),
            "Maximum Comfort Temperature": self.curve_comfort_max.points_in_game(
                bc_index, fc_index
            ),
            "TI Indicator": {
                "Position": self.position,
                "Comfort dT": self.comfort_diff,
                "Scale": 1 + 0.5 * (self.heat_on + self.cool_on),
            },
            "TA Indicator": {
                "TA": (self.hour, self.model.TA[self._mh]),
                "TI": self.position,
            },
        }

    def get_ui_data(self):
        return {
            "Energy balance": {
                "anchorpoint": (600, 250),
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
                "Comfort": {"dT": self.comfort_diff, "score": self.comfort_score},
            },
            "Price": f"Price: {self.model.price_grid} €/Wh",
            "CO2": f"CO2: {self.model.CO2[self._mh]*1000:.0f} g/kWh",
            "COP": f"Efficiency    {self.get_cop()*100:.0f}%",
            "Power": f"Heating Power {self.get_power()} W/m²",
        }

    def get_kpis(self) -> dict:
        """Aggregierte Kennzahlen als zusammengefasste Werte für den End-of-Level-Bildschirm."""
        return {
            "Wärmebedarf (QH)": f"{self.model.QH.sum():.1f} Wh",
            "Kältebedarf (QC)": f"{self.model.QC.sum():.1f} Wh",
            "Stromeinsatz (ED)": f"{self.model.ED.sum():.1f} Wh",
            "CO₂-Emissionen": f"{sum(self.model.CO2)/1000:.0f} kg",
            "Ø Strompreis": f"{self.model.price_grid:.3f} e/Wh",
            "Geldstand": f"{self.money:.2f} e",
            "Komfortabweichung": f"{self.model.comfort_score_tsd.mean():.1f} Kh",
        }

    def __repr__(self) -> str:
        return f"t {self._mh:4} {self.hour:4}   Ti= {self.TI:.2f}°C   ED {self.model.ED.sum():.1f} Wh/m2"


def create_game_model(
    start_hour=0, start_TI=22, starting_power=15, starting_cop=3, final_hour=8759
) -> GameModel:

    game = GameModel()
    game.speed = 24  # simulated hours / game second
    game.paused = False
    game.finished = False
    game.money = 100_000

    if not (0 <= start_hour <= 8759):
        raise ValueError("Invalid start_hour. Must be between [0 and 8759].")
    game.hour = start_hour  # ever increasing
    game.final_hour_of_the_year = (final_hour) % 8760
    game._mh = start_hour  # model hour always in [0-8759]
    game.model = EnergyModel()
    game.model.init_sim()
    game.model.TI[start_hour] = start_TI

    game.set_heating_power(starting_power)
    game.set_cooling_power(starting_power)
    game.set_cop(starting_cop)

    game.upgrades = UPGRADES

    game.forecast_hours = 72
    game.backcast_hours = 72

    game.curve_TI = Curve(
        "TI", points=[(h, ti) for h, ti in zip(range(8760), game.model.TI)]
    )
    game.curve_TA = Curve(
        "TA", points=[(h, ta) for h, ta in zip(range(8760), game.model.TA)]
    )
    game.curve_comfort_min = Curve(
        "Minimum comfort temperature",
        points=[(h, game.model.comfort.minimum_room_temperature) for h in range(8760)],
    )
    game.curve_comfort_max = Curve(
        "Minimum comfort temperature",
        points=[(h, game.model.comfort.maximum_room_temperature) for h in range(8760)],
    )

    game.curve_co2 = Curve(
        "CO2 Intensity",
        points=[(h, co2 * 200) for h, co2 in zip(range(8760), game.model.CO2)],
    )

    game.cleanup()
    return game


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
