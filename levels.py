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
    comfort: Comfortmodel
    min_comfort: int = 0 # level fail when falling below minimum comfort value [%]
    min_average_comfort: int = 0
    speed: int = 12 # game hour per real second
    start_paused: bool = False

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
        month = "November",
        intro=[
            "Congratulations! You just bought your very own house and you can't wait to spend the",
            "Winter warm and comfortable. The only issue is - heating has become very expensive",
            "...and a major contributor to climate change!",
            "",
            "Press the left mouse button to engage the heating and ",
            "try to stay in the green comfort zone.",
            "If you don't, you will slowly loose comfort.",
            "",
            "Once it reaches Zero, you loose."
            "",
            "Remember that heating is expensive! ,"
            "Try to save your money for house upgrades.",
            "",
            "Good luck!"
        ],
        start=7297,
        end=7297 + 2 * 24 * 2,
        speed=12,
        start_TI=21,
        reward=300,
        background = "Fall.png",
        comfort=Comfortmodel(
            random=False,
            maximum_room_temperature=100,
        ),
        start_paused= True
    ),

    Level(
        number=2,
        name="Level 2: Heating",
        month = "December",
        intro=[
            "It's gotten really cold outside and the house cools off fast!",
            "Fight the cold as before but this time also keep an eye on the orange emissions line.",
        ],
        start = 0,
        end= 0 + 7 * 24 * 2,
        speed=14,
        start_TI=18,
        reward=700,
        background = "Winter.png",
        comfort=Comfortmodel(
            minimum_comfort_band=10,
            p_change=1 / 6,
            alpha=0.25,
            sigma=0.8,
            comfort_sensitivity= 1
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
        speed=16,
        start_TI=21,
        reward=1000,
        background = "Dunkelflaute.png",
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.5,
            sigma=0.8,
            comfort_sensitivity= 2,
            minimum_comfort_band=4
        )
    ),

    Level(
        number=4,
        name="Level 4: Heating and Cooling",
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
        speed=20,
        start_TI=21,
        reward=1500,
        background = "Spring.png",
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.25,
            sigma=0.5,
            comfort_sensitivity=2
        )
    ),

    Level(
        number=5,
        name="Level 5: Cooling",
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
        speed=24,
        start_TI=21,
        reward=1500,
        background = "Summer.png",
        comfort=Comfortmodel(
            p_change=1 / 6,
            alpha=0.25,
            sigma=0.5,
            comfort_sensitivity=1
        )
    ),

    Level(
        number=6,
        name="Level 6: A whole year",
        month = "December",
        intro=[
            "Now its time to test your mettle! can you juggle fluctuating temperature",
            "demands, energy prices and CO2 intensities and survive an entire year?",
            "",
            "",
            "",
            "If you run into trouble, take a look at the upgrades in the shop!"
        ],
        start=5, # some indexing issues with 0 too close to 8760
        end=8759, # avoid modulo 8760 = 0 weirdness
        start_TI=21,
        speed=30,
        reward=1000,
        background = "Winter.png",
        comfort=Comfortmodel(
            p_change=1 / 6,
            alpha=0.25,
            sigma=0.8,
            comfort_sensitivity=31
        )
    ),
       Level(
        number=7,
        name="Great!",
        month = "December",
        intro=[
            "This is what we do in teaching and researching climate fit buildings and districts"
        ],
        start=5, # some indexing issues with 0 too close to 8760
        end=8760,
        start_TI=21,
        reward=1000,
        background = "Winter.png",
        comfort=Comfortmodel(
            p_change=1 / 6,
            alpha=0.25,
            sigma=0.8,
            comfort_sensitivity=31
        )
    )
]
