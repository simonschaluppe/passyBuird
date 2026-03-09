from dataclasses import dataclass


@dataclass
class Upgrades:
    name: str
    upgrade_text: str
    cost: int
    image: str
    available: bool
    level: int = 0
    callback: callable = lambda: None


UPGRADES = {
    "power": Upgrades(
        name="Power",
        upgrade_text="Increase power",
        cost=1000,
        image="hvac.png",
        available=True,
    ),

    "wall_insulation": Upgrades(
        name="Wall Insulation",
        upgrade_text='',
        cost=1000,
        image="wall.png",
        available=True,
    ),

    "windows": Upgrades(
        name="Windows",
        upgrade_text="New Windows",
        cost=1500,
        image="window.png",
        available=False,
    ),

    "hvac": Upgrades(
        name="HVAC",
        upgrade_text="HVAC Upgrade",
        cost=2000,
        image="hvac.png",
        available=True,
    )
}
