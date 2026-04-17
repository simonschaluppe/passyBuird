import os
from pathlib import Path
import pygame as pg

class Music:
    def __init__(self, freq=44100, size=-16, channels=2, buffer=512):
        self.enabled = False
        self.silenced = False  # soft mute flag
        self._level_music = []
        self._level_music_index = 0

        self.enabled = self._init_mixer(freq, size, channels, buffer)
        if not self.enabled:
            return

        self._load_assets()
        self._setup_channels()

    def _init_mixer(self, freq, size, channels, buffer):
        try:
            pg.mixer.init(frequency=freq, size=size, channels=channels, buffer=buffer)
            print("Audio: initialized")
            return True
        except pg.error as e:
            print(f"Audio disabled (init failed): {e}")
            return False

    def _load_assets(self):
        assets = Path("assets/music")
        self._level_music = [pg.mixer.Sound(assets / path) for path in [
            "music2.mp3",
            "music3.mp3",
            "music4.mp3",
            "music5.mp3",
        ]]
        self.game_over_track = pg.mixer.Sound(assets / "gameover.mp3")
        self.shop_track      = pg.mixer.Sound(assets / "music1.mp3")
        self.heat_sound      = pg.mixer.Sound(assets / "heating.mp3")
        self.cool_sound      = pg.mixer.Sound(assets / "cooling.mp3")
        self.brrr_sound      = pg.mixer.Sound(assets / "brrr.mp3")
        self.beep_sound      = pg.mixer.Sound(assets / "beep.mp3")
        self.yipie_sound     = pg.mixer.Sound(assets / "yipie.mp3")

    def _setup_channels(self):
        pg.mixer.set_num_channels(max(pg.mixer.get_num_channels(), 4))
        self.music  = pg.mixer.Channel(1)
        self.sounds = pg.mixer.Channel(2)
        self.hvac   = pg.mixer.Channel(3)

        # Store base volumes so we can mute/unmute cleanly
        self._music_vol  = 0.2
        self._sounds_vol = 1.0
        self._hvac_vol   = 0.5

        self.music.set_volume(self._music_vol)
        self.sounds.set_volume(self._sounds_vol)
        self.hvac.set_volume(self._hvac_vol)

    # --- Mid-game audio control ---

    def mute(self):
        if not self.enabled or self.silenced:
            return
        self.silenced = True
        # Pause all channels so both music and SFX stop and can resume
        try:
            pg.mixer.pause()  # pauses all channels
        except Exception:
            # Fallback: pause known channels explicitly
            for ch in (self.music, self.sounds, self.hvac):
                try:
                    ch.pause()
                except Exception:
                    pass

    def unmute(self):
        if not self.enabled or not self.silenced:
            return
        self.silenced = False
        # Resume all channels
        try:
            pg.mixer.unpause()
        except Exception:
            for ch in (self.music, self.sounds, self.hvac):
                try:
                    ch.unpause()
                except Exception:
                    pass

    def toggle_mute(self):
        if self.silenced:
            self.unmute()
        else:
            self.mute()

    # Ensure all play methods bail out while muted so you don't queue new sounds
    def play(self, cat):
        if not self.enabled or self.silenced:
            return
        if self.music.get_busy():
            self.music.fadeout(100)
        if cat == "game_over":
            self.music.play(self.game_over_track)
        elif cat == "level":
            self.music.play(self._level_music[self._level_music_index], loops=-1)
            self._level_music_index = (self._level_music_index + 1) % len(self._level_music)
        elif cat == "shop":
            self.music.play(self.shop_track)
        elif cat == "victory":
            self.music.play(self.shop_track)

    def button(self, volume=1):
        if not self.enabled or self.silenced:
            return
        if not self.sounds.get_busy():
            self.sounds.set_volume(volume)
            self.sounds.play(self.beep_sound, maxtime=300)

    def yipie(self, volume=1):
        if not self.enabled or self.silenced:
            return
        self.sounds.set_volume(self._sounds_vol * volume)
        self.sounds.play(self.yipie_sound)

    def cold_warning(self, volume=1):
        if not self.enabled or self.silenced:
            return
        if not self.sounds.get_busy():
            self.sounds.set_volume(self._sounds_vol * volume)
            self.sounds.play(self.brrr_sound)

    def heat(self, volume=None):
        if not self.enabled or self.silenced:
            return
        if not self.hvac.get_busy():
            v = self._hvac_vol if volume is None else volume
            self.hvac.set_volume(v)
            self.hvac.play(self.heat_sound)

    def cool(self, volume=None):
        if not self.enabled or self.silenced:
            return
        if not self.hvac.get_busy():
            v = self._hvac_vol if volume is None else volume
            self.hvac.set_volume(v)
            self.hvac.play(self.cool_sound)


if __name__ == "__main__":
    pg.init()
    music = Music()
    if music.enabled:
        music.play("level")
        print("Audio started. Press m to mute/unmute, q to quit.")
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    break
            cmd = input().strip().lower()
            if cmd == "m":
                music.toggle_mute()
            elif cmd == "q":
                break
    else:
        print("Running with audio disabled.")