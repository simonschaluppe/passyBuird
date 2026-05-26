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
        # intro=[
        #     "Congratulations! You just bought your very own house and you can't wait to spend the",
        #     "Winter warm and comfortable. The only issue is - heating has become very expensive",
        #     "...and a major contributor to climate change!",
        #     "",
        #     "Press the left mouse button to engage the heating and ",
        #     "try to stay in the green comfort zone.",
        #     "If you don't, you will slowly lose comfort.",
        #     "",
        #     "Once it reaches Zero, you lose."
        #     "",
        #     "Remember that heating is expensive! ,"
        #     "Try to save your money for house upgrades.",
        #     "",
        #     "Good luck!"
        # ],
        intro=[
            "Glückwunsch! Du hast dir gerade dein eigenes Haus gekauft und kannst es kaum",
            "erwarten, den Winter warm und gemütlich zu verbringen. Das einzige Problem ist -",
            "Heizen ist sehr teuer geworden und verursacht klimaschädliche Emissionen!",
            "",
            "Drücke die linke Maustaste, um zu heizen und versuche, in der grünen Komfort-",
            "zone zu bleiben. Außerhalb der Zone verlierst du nach und nach Komfortpunkte.",
            "Sobald der Komfort Null erreicht, ist die Runde verloren.",
            "",
            "Viel Glück!"
        ],
        start=7297,
        end=7297 + 2 * 24 * 2,
        speed=12,
        start_TI=21,
        reward=300,
        background = "Fall.png",
        comfort=Comfortmodel(
            random=False,
            maximum_room_temperature=27,
        ),
        start_paused= False
    ),

    Level(
        number=2,
        name="Level 2: Winter is coming",
        month = "December",
        
        # intro=[
        #     "It's gotten really cold outside and the house cools off fast!",
        #     "Fight the cold as before but this time also keep an eye on the orange emissions line.",
        #     "",
        #     "If you run into trouble, take a look at the upgrades in the shop!"
        # ],

        intro=[
            "Draußen ist es richtig kalt geworden und das Haus kühlt schnell aus!",
            "Bekämpfe die Kälte wie zuvor, aber achte diesmal auch auf die orangefarbene",
            "Linie, die die erzeugten Emissionen darstellt.",
            "",
            "Wenn du Schwierigkeiten hast, wirf einen Blick auf die Upgrades im Shop!"
        ],

        start = 0,
        end= 7 * 24 * 2,
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
        name="Level 3: Energiepreisschock!",
        month = "February",
        # intro=[
        #     "Somewhere somehow some port is blocked and now the energy prices are soaring!",
        #     "This is gonna be a challenge but I know you can make it!",
        #     "",
        #     "",
        #     "",
        #     "If you run into trouble, take a look at the upgrades in the shop!"
        # ],

        intro=[
            "Irgendwie ist irgendwo irgendein Hafen blockiert, und jetzt schießen die",
            "Energiepreise in die Höhe! Das wird eine Herausforderung, aber ich weiß,",
            "du kannst es schaffen!",
            "",
            "",
            "Wenn du Schwierigkeiten hast, wirf einen Blick auf die Upgrades im Shop!"
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
        name="Level 4: Übergangszeit",
        month = "April",
        # intro=[
        #     "The cold days are almost over and the sun is getting intense.",
        #     "Now you have to heat as well as cool to keep withing comfort limits.",
        #     "Press left mouse button to heat and right mouse button to cool.",
        #     "",
        #     "",
        #     "",
        #     "If you run into trouble, take a look at the upgrades in the shop!"
        # ],
        intro=[
            "Die kalten Tage sind fast vorbei und die Sonne wird immer intensiver.",
            "Jetzt musst du sowohl heizen als auch kühlen, um innerhalb der",
            "Komfortgrenzen zu bleiben.",
            "Drücke die linke Maustaste zum Heizen und die rechte Maustaste zum Kühlen.",
            "",
            "",
            "Wenn du Schwierigkeiten hast, wirf einen Blick auf die Upgrades im Shop!"
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
        name="Level 5: Summer sweat",
        month = "June",
        # intro=[
        #     "The weatherman just called - there's some seriously hot days ahead.",
        #     "Try to keep a cool head - and a cool house!",
        #     "Press left mouse button to heat and right mouse button to cool.",
        #     "",
        #     "",
        #     "",
        #     "If you run into trouble, take a look at the upgrades in the shop!"
        # ],
        intro=[
            "Der Wetterfrosch hat gerade angerufen: es stehen ein paar richtig heiße",
            "Tage bevor. Versuche einen kühlen Kopf - und ein kühles Haus - zu bewahren!",
            "Drücke die linke Maustaste zum Heizen und die rechte Maustaste zum Kühlen.",
            "",
            "",
            "",
            "Wenn du Schwierigkeiten hast, wirf einen Blick auf die Upgrades im Shop!"
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
        name="Level 6: Game of Thaws",
        month = "February",
        # intro=[
        #     "That ski trip was amazing! Without heating, the house almost froze in your absence.",
        #     "",
        #     "Blast the heating and reach safe indoor temperatures!",
        #     "",
        #     "If you cannot heat the place quick enough, you may need an upgrade to your",
        #     "*Heat Power* "
        # ],
        intro=[
            "Dein Schiurlaub war fantastisch! Aber dein Haus ist in deiner Abwesenheit fast",
            "eingefroren! Dreh die Heizug auf underreiche eine sichere Innentemperatur!",
            "",
            "",
            "Tipp: Wenn dein Haus nicht schnell genug warm wird, brauchst du vielleicht ein",
            "Upgrade deiner Heizleistung."
        ],
        start=500,
        end=500 + 2 * 24 * 2,
        speed=6,
        start_TI=10,
        reward=1500,
        background = "Winter.png",
        start_paused=True,
        comfort=Comfortmodel(
            random=False,
            maximum_room_temperature=26,
            comfort_sensitivity=10
        )
    ),

        Level(
        number=7,
        name="Level 7: Toddler Trouble!",
        month = "Oktober",
        # intro=[
        #     "The baby is afoot! And it found the thermostat!",
        #     "",
        #     "Prepare for some seriously sudden setpoint shifts!!",
        # ],
        intro=[
            "Dein Baby hat das Gehen gelernt! Und es hat das Thermostat gefunden!",
            "",
            "Mach dich auf heftige Sollwertsprünge gefasst!!",
        ],
        start=6000,
        end=6000 + 14 * 24 * 2,
        speed=24,
        start_TI=21,
        reward=1500,
        background = "Fall.png",
        comfort=Comfortmodel(
            p_change=1 / 4,
            alpha=0.25,
            sigma=1.0,
            comfort_sensitivity=3
        )
    ),


    # Level(
    #     number=8,
    #     name="Level 8: Le quattro stagioni",
    #     month = "December",
    #     # intro=[
    #     #     "Now its time to test your mettle! can you juggle fluctuating temperature",
    #     #     "demands, energy prices and CO2 intensities and survive an entire year?",
    #     #     "",
    #     #     "",
    #     #     "",
    #     #     "If you run into trouble, take a look at the upgrades in the shop!"
    #     # ],
    #     intro=[
    #         "Jetzt ist es Zeit, dein Können zu testen! Kannst du schwankende Temperatur-",
    #         "anforderungen, Energiepreise und CO2-Intensitäten ein ganzes Jahr lang jonglieren?",
    #         "",
    #         "",
    #         "",
    #         "Wenn du in Schwierigkeiten gerätst, wirf einen Blick auf die Upgrades im Shop!"
    #     ],
    #     start=5, # some indexing issues with 0 too close to 8760
    #     end=8759, # avoid modulo 8760 = 0 weirdness
    #     start_TI=21,
    #     speed=30,
    #     reward=1000,
    #     background = "Winter.png",
    #     comfort=Comfortmodel(
    #         p_change=1 / 6,
    #         alpha=0.25,
    #         sigma=0.8,
    #         comfort_sensitivity=5
    #     )
    # ),
    #    Level(
    #     number=9,
    #     name="Great!",
    #     month = "December",
    #     intro=[
    #         "This is what we do in teaching and researching climate fit buildings and districts"
    #     ],
    #     start=5, # some indexing issues with 0 too close to 8760
    #     end=8760,
    #     start_TI=21,
    #     reward=1000,
    #     background = "Winter.png",
    #     comfort=Comfortmodel(
    #         p_change=1 / 6,
    #         alpha=0.25,
    #         sigma=0.8,
    #         comfort_sensitivity=31
    #     )
    # )
]
