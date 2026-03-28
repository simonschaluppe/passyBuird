from asyncio.trsock import TransportSocket
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
        self.current_track = None

        self.sounds = pg.mixer.Channel(2)
        self.heat_sound = pg.mixer.Sound(Path("assets/music")/"fartas_brutos.mp3")
        self.brrr_sound = pg.mixer.Sound(Path("assets/music")/"brrr.mp3")

    def play(self, cat):
        if self.current_track:
            self.current_track.fadeout(1)
        match cat:
            case "game_over":
                self.current_track = self.game_over_track
            case "level":
                self.current_track = self._level_music[self._level_music_index]
                self._level_music_index = (self._level_music_index + 1) % len(self._level_music)
            case "shop":
                self.current_track = self.shop_track
        self.current_track.play(loops=-1)

    def cold_warning(self, volume=2):
        if not self.sounds.get_busy():
            self.sounds.set_volume(volume)
            self.sounds.play(self.brrr_sound)


    def heat(self, volume=1):
        if not self.sounds.get_busy():
            self.sounds.set_volume(volume)
            self.sounds.play(self.heat_sound)

    def start_level_music(self):
        track = self._level_music[self._level_music_index]
        self._level_music_index = (self._level_music_index + 1) % len(self._level_music)
        print(TransportSocket)
        track.play()

if __name__ == "__main__":
    music = Music()
    music.start_level_music()
    input()