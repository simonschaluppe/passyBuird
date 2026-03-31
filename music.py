
from pathlib import Path
import pygame as pg


class Music:
    def __init__(self):
        pg.mixer.init()
        self._level_music = [pg.mixer.Sound(Path("assets/music")/path) for path in [
            "music2.mp3",
            "music3.mp3",
            "music4.mp3",
            "music5.mp3",
        ]]
        self._level_music_index = 0
        self.game_over_track = pg.mixer.Sound(Path("assets/music")/"gameover.mp3")
        self.shop_track = pg.mixer.Sound(Path("assets/music")/"music1.mp3")
        #self.heat_sound = pg.mixer.Sound(Path("assets/music")/"fartas_brutos.mp3")
        self.heat_sound = pg.mixer.Sound(Path("assets/music")/"blub.mp3")
        self.cool_sound = pg.mixer.Sound(Path("assets/music")/"pfuu.mp3")
        self.brrr_sound = pg.mixer.Sound(Path("assets/music")/"brrr.mp3")
        self.beep_sound = pg.mixer.Sound(Path("assets/music")/"beep.mp3")
        self.yipie_sound = pg.mixer.Sound(Path("assets/music")/"yipie.mp3")

        self.music = pg.mixer.Channel(1)
        self.sounds = pg.mixer.Channel(2)
        self.hvac = pg.mixer.Channel(3)

        self.music.set_volume(0.2)

    def play(self, cat):
        if self.music.get_busy:
            self.music.fadeout(1)
        match cat:
            case "game_over":
                self.music.play(self.game_over_track)
            case "level":
                self.music.play(self._level_music[self._level_music_index], loops=-1)
                self._level_music_index = (self._level_music_index + 1) % len(self._level_music)
            case "shop":
                self.music.play(self.shop_track)
            case "victory":
                self.music.play(self.shop_track)

    def button(self, volume=1):
        if not self.sounds.get_busy():
            self.sounds.set_volume(volume)
            self.sounds.play(self.beep_sound, maxtime=300)

    def yipie(self, volume=1):
        self.sounds.set_volume(volume)
        self.sounds.play(self.yipie_sound)

    def cold_warning(self, volume=1):
        if not self.sounds.get_busy():
            self.sounds.set_volume(volume)
            self.sounds.play(self.brrr_sound)

    def heat(self, volume=.5):
        if not self.hvac.get_busy():
            self.hvac.set_volume(volume)
            self.hvac.play(self.heat_sound)
    def cool(self, volume=0.5):
        if not self.hvac.get_busy():
            self.hvac.set_volume(volume)
            self.hvac.play(self.cool_sound)


if __name__ == "__main__":
    music = Music()
    music.play("level")
    input()