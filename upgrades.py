from dataclasses import dataclass


@dataclass
class Upgrade:
    name: str
    upgrade_text: str
    cost: int
    image: str
    available: bool
    level: int = 0
    callback: callable = lambda: None


UPGRADES = {

    "wall_insulation": Upgrade(
        name="Wall Insulation",
        upgrade_text="Insulate Walls",
        cost=200,
        image="",
        available=True,
    ),

    "power": Upgrade(
        name="Power",
        upgrade_text="Increase Power",
        cost=200,
        image="",
        available=True,
    ),

    "heatpump_efficiency": Upgrade(
        name="Heat Pump Efficiency",
        upgrade_text="Increase Efficiency",
        cost=500,
        image="",
        available=True,
    ),

    "electricity_price_discount": Upgrade(
        name="Elect. Price Discount",
        upgrade_text="Negotiate Discount",
        cost=100,
        image="",
        available=True,
    ),
    "windows": Upgrade(
        name="Windows",
        upgrade_text="New Windows",
        cost=1500,
        image="window.png",
        available=False,
    ),

    "hvac": Upgrade(
        name="HVAC",
        upgrade_text="HVAC Upgrade",
        cost=2000,
        image="hvac.png",
        available=False,
    ),
    "pv": Upgrade(
        name="PV System",
        upgrade_text="Install 10 Panels",
        cost=200,
        image="PV.png",
        available=False,
    )
}
