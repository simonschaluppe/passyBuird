from dataclasses import dataclass


@dataclass
class Level:
    intro: str
    start: int
    end: int
    start_TI: int
    reward: int


LEVELS = [
    Level(
        intro="""
It's a cold January day! Make sure the building stays warm and cozy and the temperature does not drop below the minimum setpoint temperature (orange line)

How to play: Press LMB to heat
Goal: 90 % Comfort rating
Duration: 1 Week
""",
        start=8000,
        end=8759,
        start_TI=22,
        reward=1000,
    )
]
