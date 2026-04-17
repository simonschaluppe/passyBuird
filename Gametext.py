


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
            "CO₂-Emissions and how to reduce the carbon footprint of the built environment.",
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
        "bankrupt":"You spent all your money!",
        "too hot":"Everyone died of heat stroke!",
        "too_cold": """
                    Everyone froze into icicles!
                    
                    If the temperature drops out of the green comfort zone,
                    you will quickly loose indoor comfort."""
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
            "Wir erforschen klimafitte Gebäude, simulieren deren Energiebedarf und CO₂-Emissionen",
            "und untersuchen, wie sich der CO₂-Fußabdruck der bebauten Umwelt verringern lässt.",
            "",
            "Dieses Spiel basiert auf einem von Studierenden entwickelten Simulationsmodell",
            "Probieren Sie es aus und spielen Sie eine Runde!",
            "",
            "",
            "Weitere Informationen zu unseren Aktivitäten:",
            "   -Bachelor-Studiengang Erneuerbare Energien",
            "   -Master-Studiengang Renewable Energy Engineering",
            "   -Master-Studiengang Klimabewusste Gebäudetechnik",
        ],
        "welcome": "Willkommen zu ",
        "upgrade": "Upgrade",
        "bankrupt":"Du bist pleite!",
        "too hot":"Das wurde ein bisschen zu heiß!",
        "too_cold": """
                    Alle sind zu Eiszapfen gefroren!
                    
                    Wenn die Temperatur den grünen Komfortbereich verlässt,
                    wird der Komfortwert schnell negativ."""
    }

    wien = {
        "game_over": "GAME OVER!",
        "start_new_game": "Neichs Spü startn",
        "shop": "Zum Gschäftl",
        "start_level": "Level startn",
        "level_failed": "Level versemmelt!",
        "retry": "No amoi",
        "survived1": "Du hosts Level ",
        "survived2": " g'schafft!",
        "continue": "Weita",
        "victory": "I wea narrisch! Du hosts Spü g'wonnen!",
        "description": [
            "Ma erforschen klimafitte Gebäud, simuliern deren Energiebedarf und CO₂-Emissionen",
            "und schaugn, wia si da CO₂-Fußabdruck von da bebautn Umwelt verringern lässt.",
            "",
            "Des Spü basiert auf am Simulationsmodell, des von Studierenden entwickelt wor'n is.",
            "Probier's aus und spü a Rundn!",
            "",
            "",
            "Weitane Infos zu unsana Aktivitätn:",
            "   -Bachelor-Studiengang Erneuerbare Energien",
            "   -Master-Studiengang Renewable Energy Engineering",
            "   -Master-Studiengang Klimabewusste Gebäudetechnik",
        ],
        "welcome": "Servus bei ",
        "upgrade": "Upgrade",
        "bankrupt":"Fuat is die Marie!",
        "too hot":"Es is' hoasser wia in da U6!",
        "too_cold": """
                    I schlotter wie narrisch!
                    
                    Wenn d' Temperatur den grüna Komfortbereich verlasst,
                    verlierst da schnö an Innenkomfort."""
    }

    @staticmethod
    def get(language: str, key: str):
        if language == "English":
            return GameText.eng[key]
        if language == "Deutsch":
            return GameText.ger[key]
        raise ValueError(f"Unsupported language: {language}")