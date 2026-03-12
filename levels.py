from dataclasses import dataclass

from model.Comfort import Comfortmodel


@dataclass
class Level:
    name: str
    intro: list[str]
    start: int
    end: int
    start_TI: int
    reward: int

    # level difficulty parameters
    min_comfort: int  # level fail when falling below minimum comfort value [%]
    comfort: Comfortmodel


LEVELS = [
    Level(
        name="Level 1: Heating",
        intro=[
            "It's a cold January day! Make sure the building",
            "stays warm and cozy and the temperature does not",
            "drop below the minimum setpoint temperature",
            "(orange line)",
            "",
            "How to play: Press LMB to heat",
            "Goal: 50 % Comfort rating",
            "Duration: 1 Week",
        ],
        start=0,
        end=7 * 24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
        comfort=Comfortmodel(
            random=False,
            maximum_room_temperature=100,
        )
    ),

    Level(
        name="Level 2: Cooling",
        intro=[
            "Add Level description here!",
        ],
        start=0,
        end=7 * 24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
        comfort=Comfortmodel(
            p_change=1 / 6,
            alpha=0.25,
            sigma=0.8,
        )
    ),

    Level(
        name="Level 3: CO2 Intensity",
        intro=[
            "Add Level description here!",
        ],
        start=0,
        end=7 * 24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.5,
            sigma=0.8,
        )
    ),

    Level(
        name="Level 4: Energy price shock!",
        intro=[
            "Add Level description here!",
        ],
        start=0,
        end=7 * 24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.25,
            sigma=1.6,
        )
    ),

    Level(
        name="Level 5: A whole year",
        intro=[
            "Now its time to test your mettle! can you juggle",
            "fluctuating temperature demands, energy prices",
            "and CO2 intensities and survive an entire year?",
        ],
        start=0,
        end=7 * 24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
        comfort=Comfortmodel(
            p_change=1 / 12,
            alpha=0.25,
            sigma=0.8,
        )
    )
]
