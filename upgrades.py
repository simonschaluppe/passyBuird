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

    "wall_insulation": Upgrades(
        name="Wall Insulation",
        upgrade_text="Insulate Walls",
        cost=1000,
        image="",
        available=True,
    ),

    "power": Upgrades(
        name="Power",
        upgrade_text="Increase Power",
        cost=1000,
        image="",
        available=True,
    ),

    "heatpump_efficiency": Upgrades(
        name="Heat Pump Efficiency",
        upgrade_text="Increase Efficiency",
        cost=1500,
        image="",
        available=True,
    ),

    "electricity_price_discount": Upgrades(
        name="Elect. Price Discount",
        upgrade_text="Negotiate Discount",
        cost=1500,
        image="",
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
        available=False,
    )
}
