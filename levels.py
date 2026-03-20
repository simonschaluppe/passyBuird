from dataclasses import dataclass

from model.Comfort import Comfortmodel


@dataclass
class Level:
    number: int
    name: str
    month: str
    intro: list[str]
    start: int
    end: int
    start_TI: int
    reward: int
    background: str

    # level difficulty parameters
    min_comfort: int  # level fail when falling below minimum comfort value [%]
    min_average_comfort: int
    comfort: Comfortmodel

    def get_hour_of_month(self, month):
        # First hour of every month
        values = {'January':1,
                  'February':745,
                  'March':1417,
                  'April':2161,
                  'May':2881,
                  'June':3625,
                  'July':4345,
                  'August':5089,
                  'September':5833,
                  'October':6553,
                  'November':7297,
                  'December':8017
                  }
        return values[month]


LEVELS = [
    Level(
        number=1,
        name="Level 1: Tutorial",
        month = "October",
        intro=[
            "It's the first week in your new home!",
            "Press left mouse button to engage the heating and try to stay over the light blue comfort line.",
            "",
            "Remember that heating is expensive! Keep an eye on your available money."
        ],
        start=6553,
        end=6553 + 7 * 24 * 2,
        start_TI=22,
        min_comfort=30,
        reward=300,
        background = "Fall.png",
        comfort=Comfortmodel(
            random=False,
            maximum_room_temperature=1000,
        )
    ),

    Level(
        number=2,
        name="Level 2: Heating",
        month = "December",
        intro=[
            "It's gotten really cold outside and the house cools off fast!",
            "Fight the cold as before but this time also keep an eye on the orange emissions line.",
        ],
        start = 8017,
        end= 8017 + 7 * 24 * 2,
        start_TI=22,
        min_comfort=10,
        min_average_comfort = 90,
        reward=700,
        background = "Winter.png",
        comfort=Comfortmodel(
            p_change=1 / 6,
            alpha=0.25,
            sigma=0.8,
            comfort_sensitivity= 10
        )
    ),

    Level(
        number=3,
        name="Level 3: Energy price shock",
        month = "February",
        intro=[
            "Somehow somewhere some port is blocked and now the energy prices are soaring!",
            "This is gonna be a challenge but I know you can make it!",
            "",
            "",
            "",
            "If you run into trouble, take a look at the upgrades in the shop!"
        ],
        start=745,
        end=745 + 7 * 24 * 2,
        start_TI=22,
        min_comfort=20,
        min_average_comfort = 90,
        reward=1000,
        background = "Dunkelflaute.png",
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.5,
            sigma=0.8,
            comfort_sensitivity= 5
        )
    ),

    Level(
        number=4,
        name="Level 4: Heating & Cooling",
        month = "April",
        intro=[
            "The cold days are almost over and the sun is getting intense.",
            "Now you have to heat aswell as cool to keep withing comfort limits.",
            "Press left mouse button to heat and right mouse button to cool.",
            "",
            "",
            "",
            "If you run into trouble, take a look at the upgrades in the shop!"
        ],
        start=2161,
        end=2161 + 7 * 24 * 2,
        start_TI=22,
        min_comfort=20,
        min_average_comfort = 90,
        reward=1500,
        background = "Spring.png",
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.25,
            sigma=0.5,
            comfort_sensitivity=4
        )
    ),

    Level(
        number=5,
        name="Level 4: Cooling",
        month = "June",
        intro=[
            "The weatherman just called - there's some seriously hot days ahead.",
            "Try to keep a cool head - and a cool house!",
            "Press left mouse button to heat and right mouse button to cool.",
            "",
            "",
            "",
            "If you run into trouble, take a look at the upgrades in the shop!"
        ],
        start=3625,
        end=3625 + 7 * 24 * 2,
        start_TI=25,
        min_comfort=20,
        min_average_comfort = 90,
        reward=1500,
        background = "Summer.png",
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.25,
            sigma=0.5,
            comfort_sensitivity=2
        )
    ),

    Level(
        number=6,
        name="Level 5: A whole year",
        month = "December",
        intro=[
            "Now its time to test your mettle! can you juggle fluctuating temperature",
            "demands, energy prices and CO2 intensities and survive an entire year?",
            "",
            "",
            "",
            "If you run into trouble, take a look at the upgrades in the shop!"
        ],
        start=0,
        end=8760,
        start_TI=22,
        min_comfort=30,
        min_average_comfort = 90,
        reward=1000,
        background = "Winter.png",
        comfort=Comfortmodel(
            p_change=1 / 6,
            alpha=0.25,
            sigma=0.8,
            comfort_sensitivity=3
        )
    )
]
