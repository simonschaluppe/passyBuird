from dataclasses import dataclass

from model.Comfort import Comfortmodel


@dataclass
class Level:
    number: int
    name: str
    intro: list[str]
    start: int
    end: int
    start_TI: int
    reward: int
    background: str

    # level difficulty parameters
    min_comfort: int  # level fail when falling below minimum comfort value [%]
    comfort: Comfortmodel


LEVELS = [
    Level(
        number=1,
        name="Level 1: Heating",
        intro=[
            "It's your first day in your new home! Just make sure to stay over the light blue line,",
            "but remember that heating is expensive! Press left mouse button to heat your home.",
            "If it gets too cold or if you run out of money, you will fail the level!",
            "",
            "How to play: Press LMB to heat",
            "Goal: Stay above the light-blue line",
            "Duration: 3 Weeks",
        ],
        start=0,
        end=7 * 24,
        start_TI=28,
        min_comfort=20,
        reward=1000,
        background = "Winter.png",
        comfort=Comfortmodel(
            random=False,
            maximum_room_temperature=1000,
        )
    ),

    Level(
        number=2,
        name="Level 2: Cooling",
        intro=[
            "The month of june has come around! By now we don't just care about heating",
            "but also cooling! Press right mouse button to "
        ],
        start = 4000,
        end= 4000 + 7 * 24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
        background = "Summer.png",
        comfort=Comfortmodel(
            p_change=1 / 6,
            alpha=0.25,
            sigma=0.8,
        )
    ),

    Level(
        number=3,
        name="Level 3: CO2 Intensity",
        intro=[
            "Add Level description here!",
        ],
        start=0,
        end=7 * 24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
        background = "Winter.png",
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.5,
            sigma=0.8,
        )
    ),

    Level(
        number=4,
        name="Level 4: Energy price shock!",
        intro=[
            "Add Level description here!",
        ],
        start=2000,
        end=7 * 24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
        background = "Spring.png",
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.25,
            sigma=1.6,
        )
    ),

    Level(
        number=5,
        name="Level 5: A whole year",
        intro=[
            "Now its time to test your mettle! can you juggle fluctuating temperature",
            "demands, energy prices and CO2 intensities and survive an entire year?",
        ],
        start=0,
        end=7 * 24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
        background = "Winter.png",
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.25,
            sigma=0.8,
        )
    )
]
