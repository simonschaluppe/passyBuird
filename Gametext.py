from attr import dataclass


class GameText:
    eng = {
        "game_over": "GAME OVER!",
        "start_new_game": "Start New Game",
        "shop": "Go To Shop",
        "start_level": "Start Level",
        "level_failed": "Level failed!",
        "retry": "Retry",
        "survived1": "You survived level ",
        "survived2": " !",
        "continue": "Continue",
        "victory": "You've completed the game, Good Job!",
        "description": [
            "We research climate-fit buildings, simulating building energy demand,",
            "CO2-Emissions and how to reduce the carbon footprint of the built environment.",
            "",
            "This game is based on a simulation model developed by students",
            "Try it out and play a round!",
            "",
            "",
            "More Info about what we do:",
            "   -Bachelor Renewable Energy",
            "   -Master Renewable Energy Engineering",
            "   -Master Climate-responsive Building Technology",
        ],
        "welcome": "Welcome to ",
        "upgrade": "Upgrade",
        "freeze_death": [
            "Everyone froze into icicles!",
            "",
            "If the temperature drops out of the green comfort zone,",
            "you will quickly lose indoor comfort.",
        ],
    }

    ger = {
        "game_over": "GAME OVER!",
        "start_new_game": "Neues Spiel starten",
        "shop": "Zum Shop",
        "start_level": "Level starten",
        "level_failed": "Level fehlgeschlagen!",
        "retry": "Nochmal",
        "survived1": "Du hast Level ",
        "survived2": " geschafft!",
        "continue": "Weiter",
        "victory": "Gratuliere! Du hast das Spiel gewonnen!",
        "description": [
            "Wir erforschen klimafitte Gebaeude, simulieren deren Energiebedarf und CO2-Emissionen",
            "und untersuchen, wie sich der CO2-Fussabdruck der bebauten Umwelt verringern laesst.",
            "",
            "Dieses Spiel basiert auf einem von Studierenden entwickelten Simulationsmodell",
            "Probieren Sie es aus und spielen Sie eine Runde!",
            "",
            "",
            "Weitere Informationen zu unseren Aktivitaeten:",
            "   -Bachelor-Studiengang Erneuerbare Energien",
            "   -Master-Studiengang Renewable Energy Engineering",
            "   -Master-Studiengang Klimabewusste Gebaeudetechnik",
        ],
        "welcome": "Willkommen zu ",
        "upgrade": "Upgrade",
        "freeze_death": [
            "Alle sind zu Eiszapfen gefroren!",
            "",
            "Wenn die Temperatur den grünen Komfortbereich verlässt,",
            "verlieren Sie schnell den Innenkomfort.",
        ],
    }

    @staticmethod
    def get(language: str, key: str):
        if language == "English":
            return GameText.eng[key]
        if language == "Deutsch":
            return GameText.ger[key]
        raise ValueError(f"Unsupported language: {language}")