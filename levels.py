from dataclasses import dataclass


@dataclass
class Level:
    name: str
    intro: list[str]
    start: int
    end: int
    start_TI: int
    min_comfort: int  # level fail when falling below minimum comfort value [%]
    reward: int


LEVELS = [
    Level(
        name="Level 1",
        intro=["It's a cold January day! Make sure the building",
               "stays warm and cozy and the temperature does not",
               "drop below the minimum setpoint temperature",
               "(orange line)",
               "",
               "How to play: Press LMB to heat",
               "Goal: 50 % Comfort rating",
               "Duration: 1 Week",
               ],
        start=0,
        end=7*24,
        start_TI=22,
        min_comfort=50,
        reward=1000,
    )
]
