from typing import override

import pygame as pg
import random

from music import Music
import settings
from camera import Camera2D
from handler import Button, InputHandler, TextInput
from model.GameModel import GameModel
from particles import ParticleManager
from renderer import Renderer
from pathlib import Path
from Highscores import Scoreboard
import datetime
import language.german as language  # set language here
from joystick import JoystickManager

DEBUG_MODE = settings.DEBUG_MODE
AUTOPILOT = False

# Initialize pygame
pg.init()
print(pg.version)
sound_manager = Music()
scoreboard = Scoreboard()

# Initialize the joystick manager
joystick_manager = JoystickManager()

# Set up the main display surface
screen: pg.Surface = pg.display.set_mode(
    settings.SCREEN_RESOLUTION, 
    #pg.FULLSCREEN
    )
pg.display.set_caption("passyBUIRD")
# Create another surface to perform off-screen drawing
display = pg.Surface(settings.SCREEN_RESOLUTION)

clock = pg.time.Clock()
game = GameModel(speed=settings.GAME_SPEED, godmode=settings.GODMODE)
game.AUTOPILOT = AUTOPILOT
# Set up the camera with a zoom feature
camera = Camera2D(
    surface=display, game_world_position=(game.position[0], 0), zoom=settings.GAME_ZOOM
)
camera.follow(game, maxdist=0)

# Set up renderer
renderer = Renderer(game, display, camera, scale=0.8, font=settings.FONT)
particle_manager = ParticleManager(renderer=renderer)


def center_screen(size=0.8):
    # Position & Size
    width = settings.SCREEN_RESOLUTION[0] * size
    height = settings.SCREEN_RESOLUTION[1] * size
    left = settings.SCREEN_RESOLUTION[0] * 0.1
    top = settings.SCREEN_RESOLUTION[1] * 0.1
    return (left, top, width, height)


def get_btn_pos(orientation=None):
    """
    Parameter "orientation" can be "top left", "top right", "bottom left", "bottom right", "popup left" or "popup right".

    Function returns a touple with screen coordinates (x,y).
    """
    return tuple(
        pixel * factor
        for pixel, factor in zip(
            settings.SCREEN_RESOLUTION, settings.SCREEN_ANCHORS.get(orientation, (0, 0))
        )
    )

# TODO: Move to utility or renderer
def get_background(hour_of_year):
    # Use modular arithmetic to cycle through the backgrounds
    background_paths = [
        "Dunkelflaute.png",
        "Spring.png",
        "Summer.png",
        "Fall.png",
        "Winter.png",
    ]
    try:
        index = round(hour_of_year / 8760 * len(background_paths))
        # print("In Game Hour ", game.hour, " the index is ", index, " and the background is ", background_paths[index])
        return background_paths[index]
    except:
        return background_paths[1]


"""Callback functions"""

# Events

def start_title_loop():
    sound_manager.play("shop")
    title_screen.loop()
def start_level_loop():
    sound_manager.play("level")
    level_screen.loop()
def start_shop_loop():
    #sound_manager.play("shop")
    shop_screen.loop()
def start_highscore_loop():
    #sound_manager.play("highscore")
    highscore_screen.loop()
def save_highscore(name, score):
    #sound_manager.play("highscore")
    scoreboard.add_score(name, score)
    start_highscore_loop()


# Multi line functions
def start_new_game():
    game.setup_new_game()
    start_title_loop()

def toggle_autopilot():
    global AUTOPILOT
    AUTOPILOT = not AUTOPILOT
    game.AUTOPILOT = not game.AUTOPILOT

def toggle_audio():
    sound_manager.toggle_mute()

def game_over(reason="You have lost the game."):
    sound_manager.play("game_over")
    Popup(
        title=language.GAME_OVER,
        body=[f"{label}: {value}" for label, value in game.get_kpis().items()],
        buttons=[
            Button(
                get_btn_pos("popup right"),
                start_new_game,
                language.START_NEW_GAME,
                size=settings.BUTTON_SIZE["Start New Game"],
            )
        ],
        keys=[
            (pg.K_RETURN, start_new_game),
            (pg.K_ESCAPE, start_new_game),
            (pg.K_r, start_new_game),
        ],
        fail_reason=reason
    ).loop()


def start_level_intro(level=None):
    if level:
        game.setup_level(level)
    # renderer.set_background(game.current_level.background)
    level_intro_popup = Popup(
        title=game.current_level.name,
        body=game.current_level.intro,
        buttons=[
            Button(
                get_btn_pos("popup left"),
                start_shop_loop,
                language.SHOP,
                size=settings.BUTTON_SIZE["Go to Shop"],
            ),
            Button(
                get_btn_pos("popup right"),
                start_level_loop,
                language.START_LEVEL,
                size=settings.BUTTON_SIZE["Start Level"],
            ),
        ],
        keys=[
            (pg.K_RETURN, start_level_loop),
            (pg.K_ESCAPE, start_title_loop),
            (pg.K_r, start_new_game),
        ],
    )
    level_intro_popup.loop()


def level_fail(text: str, reason="None"):
    sound_manager.play("game_over")
    game.update_level_finished()
    game.setup_level()
    game.money += game.moneyspent
    game.moneyspent = 0
    title = language.LEVEL_FAILED
    level_fail_screen = Popup(
        title=title,
        body=[*text.split("\n")],
        buttons=[
            Button(
                get_btn_pos("popup left"),
                start_level_intro,
                language.RETRY,
                size=settings.BUTTON_SIZE["Retry"],
            )
        ],
        keys=[
            (pg.K_RETURN, start_level_loop),
            (pg.K_ESCAPE, start_new_game),
            (pg.K_r, start_new_game),
        ],
        fail_reason=reason,
    )
    level_fail_screen.loop()


def level_success():
    sound_manager.yipie()
    sound_manager.play("victory")
    game.update_level_finished()
    title = language.SURVIVED1 + str(game.current_level.number) + language.SURVIVED2
    level_success_popup = Popup(
        title=title,
        body=[f"{label} {value}" for label, value in game.get_kpis().items()],
        buttons=[
            Button(
                get_btn_pos("popup right"),
                start_level_intro,
                language.CONTINUE,
                size=settings.BUTTON_SIZE["Continue"],
            )
        ],
        keys=[
            (pg.K_RETURN, start_shop_loop),
            (pg.K_ESCAPE, start_shop_loop),
            (pg.K_r, start_new_game),
        ],
    )
    game.money += game.current_level.reward
    game.moneyspent = 0
    try:
        game.setup_next_level()
    except IndexError:
        victory_loop()

    for _ in range(50):
        x = random.randint(0, settings.SCREEN_RESOLUTION[0])
        y = random.randint(0, settings.SCREEN_RESOLUTION[1])
        particle_manager.success(
            position=(x, y), velocity=(random.randint(-10, 10), random.randint(-10, 10))
        )
    level_success_popup.loop()


def victory_loop():
    game.reset_levels()
    for _ in range(50):
        x = random.randint(0, settings.SCREEN_RESOLUTION[0])
        y = random.randint(0, settings.SCREEN_RESOLUTION[1])
        particle_manager.success(
            position=(x, y), velocity=(random.randint(-10, 10), random.randint(-10, 10))
        )
    print(language.VICTORY)
    Victory().loop()


def toggle_debug_mode():
    global DEBUG_MODE
    DEBUG_MODE = not DEBUG_MODE
    print("DEBUG_MODE ", DEBUG_MODE)

def take_screenshot(filename=None):
        """Speichert einen Screenshot des aktuellen Engine-Bildschirms."""
        screenshot_dir = Path("Screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)  # Ordner anlegen falls nicht vorhanden

        now = datetime.datetime.now().strftime('%d-%m-%y_%H-%M-%S')
        #datetime.datetime(2009, 1, 6, 15, 8, 24, 78915)

        if filename is None:
            filename = "Screenshot " + str(now) + ".png"
            
        filepath = screenshot_dir / filename

        pg.image.save(screen, filepath)
        print(f"Screenshot saved at {filename}")  


def quit_game():
    print("Quitting game...")
    pg.quit()
    quit()


def heat():
    game.heat()
    sound_manager.heat()
    particle_manager.heat(game.position, (-game.qh * 0.5, -game.qh))


def cool():
    game.cool()
    sound_manager.cool()
    particle_manager.cool(game.position, (0.5 * game.qc, -game.qc))

def calculate_score():
    return int(game.total_GHG_avoided)
    comfort_score = game.get_comfort_score()
    ui_data = game.get_ui_data()
    comfort = ui_data["Scores"]["Comfort"]["score"]
    money = ui_data["Scores"]["Money"]
    emissions = ui_data["CO2"]

    score = comfort + money - emissions
    print("comfort_score",comfort_score,
          "comfort",comfort,
          "money",money,
          "emissions", emissions,
          "score",score)


# def place_buttons()

"""Classes"""


class Screen:
    """Basic Screen class."""

    def __init__(self):
        self.handler = InputHandler(sound_manager)
        self.config_handler()

    def loop(self) -> None:
        """Basic handler/render loop."""
        running = True
        while running:
            # Process discrete button navigation
            joystick_manager.update_menu(self.handler.buttons)

            running = self.handler.update()
            particle_manager.update()
            self.render()

            clock.tick(60)

    def config_handler(self) -> None:
        """Put handler configuration here."""
        ...

    def render(self) -> None:
        """Put render lines here."""
        ...


class TitleScreen(Screen):
    """Title screen serves as Home/Welcome page."""

    @override
    def config_handler(self) -> None:
        # register buttons
        buttons = [
            Button(
                get_btn_pos("popup left"),
                start_highscore_loop,
                language.HIGHSCORE,
                size=settings.BUTTON_SIZE["Start New Game"],
            ),
            Button(
                get_btn_pos("popup right"),
                start_level_intro,
                language.START_NEW_GAME,
                size=settings.BUTTON_SIZE["Start New Game"],
            ),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, start_level_intro)
        self.handler.bind_keypress(pg.K_v, victory_loop)
        self.handler.bind_keypress(pg.K_q, quit_game)
        self.handler.bind_keypress(pg.K_s, take_screenshot)
        self.handler.bind_keypress(pg.K_m, toggle_audio)
        self.handler.bind_keypress(pg.K_h, start_highscore_loop)
        self.handler.bind_keypress(pg.K_r, start_new_game)

    @override
    def render(self) -> None:
        description = language.DESCRIPTION

        renderer.render_title_screen(
            title=language.WELCOME,
            body=description,
            screen_params=center_screen(0.8),
            index=game.insulation_level,
        )

        for button in self.handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


class ShopScreen(Screen):
    """Shop screen, where player can view and purchase upgrades."""

    @override
    def config_handler(self) -> None:
        # register buttons
        def upgrade_button(upgrade, pos) -> Button:
            def callback():
                particle_manager.purchase(position=pg.mouse.get_pos())
                res = upgrade.callback()
                if not res:
                    renderer.draw_no_money_warning()

            b = Button(
                pos,
                callback,
                f"{upgrade.upgrade_text}  €{upgrade.cost}",
                size=settings.BUTTON_SIZE["Upgrade"],
            )
            b.upgrade = upgrade
            return b

        self.upgrade_buttons = [
            upgrade_button(game.upgrades["wall_insulation"], (100, 345)),
            upgrade_button(game.upgrades["power"], (100, 395)),
            upgrade_button(game.upgrades["heatpump_efficiency"], (100, 445)),
            upgrade_button(game.upgrades["electricity_price_discount"], (100, 495)),
            upgrade_button(game.upgrades["pv"], (100, 545)),
        ]
        buttons = [
            Button(
                get_btn_pos("bottom right"),
                start_level_intro,
                language.START_LEVEL,
                size=settings.BUTTON_SIZE["Start Level"],
            ),
            Button(
                get_btn_pos("bottom left"),
                start_title_loop,
                language.MAIN_MENU,
            ),
            Button(
                (get_btn_pos("bottom center")),
                start_highscore_loop,
                "Highscores",
                size=settings.BUTTON_SIZE["170x60"],
            ),
            *self.upgrade_buttons,
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, start_level_intro)
        self.handler.bind_keypress(pg.K_q, quit)
        self.handler.bind_keypress(pg.K_s, take_screenshot)
        self.handler.bind_keypress(pg.K_m, toggle_audio)
        # self.handler.bind_keypress(pg.K_ESCAPE, quit_game)
        self.handler.bind_keypress(pg.K_r, start_new_game)

    @override
    def render(self) -> None:
        renderer.render_menu(game.get_menu_data(), index=game.insulation_level)

        for button in self.handler.buttons:
            renderer.render_button(button)

        particle_manager.render()

        screen.blit(renderer.display, (0, 0))
        pg.display.update()

    @override
    def loop(self) -> None:
        """Basic handler/render loop."""
        running = True
        while running:
            # Process discrete button navigation
            joystick_manager.update_menu(self.handler.buttons)

            running = self.handler.update()
            particle_manager.update()
            for b in self.upgrade_buttons:
                b.disabled = False
                if b.upgrade.cost > game.money:
                    b.disabled = True
            self.render()

            clock.tick(60)


class LevelScreen(Screen):
    """Level screen, where the actual gameplay happens."""

    @override
    def config_handler(self) -> None:
        # bind camera
        self.handler.bind_camera(camera)
        # bind key pressed
        self.handler.bind_continuous_keypress(pg.K_UP, heat)
        self.handler.bind_continuous_keypress(pg.K_DOWN, cool)
        self.handler.bind_continuous_mousebutton(0, heat)
        self.handler.bind_continuous_mousebutton(2, cool)
        self.handler.bind_keypress(pg.K_p, game.toggle_pause)
        self.handler.bind_keypress(pg.K_1, lambda: game.set_speed(12))
        self.handler.bind_keypress(pg.K_2, lambda: game.set_speed(24))
        self.handler.bind_keypress(pg.K_3, lambda: game.set_speed(24 * 7))
        self.handler.bind_keypress(pg.K_4, lambda: game.set_speed(24 * 7 * 2))
        self.handler.bind_keypress(pg.K_5, lambda: game.set_speed(24 * 7 * 4))
        self.handler.bind_keypress(pg.K_w, lambda: game.increment_cop(0.5))
        self.handler.bind_keypress(pg.K_s, lambda: game.increment_cop(-0.5))
        self.handler.bind_keypress(pg.K_q, quit_game)
        self.handler.bind_keypress(pg.K_w, level_success)
        self.handler.bind_keypress(pg.K_v, victory_loop)
        self.handler.bind_keypress(pg.K_d, toggle_debug_mode)
        self.handler.bind_keypress(pg.K_a, toggle_autopilot)
        self.handler.bind_keypress(pg.K_ESCAPE, start_shop_loop)
        self.handler.bind_keypress(pg.K_s, take_screenshot)
        self.handler.bind_keypress(pg.K_m, toggle_audio)
        self.handler.bind_joybutton(1, game.toggle_pause)
        self.handler.bind_joybutton(0, game.toggle_pause)
        self.handler.bind_joycombo(3, 0, level_success)
        self.handler.bind_joycombo(3, 1, victory_loop) 
        self.handler.bind_joycombo(3, 2, quit_game)

    @override
    def loop(self) -> None:
        """The level loop responsible for processing events, updating game state, and rendering."""
        running = True
        accumulated_gamehours = 0
        while running:
            # Handle continuous game logic instead of UI
            if joystick_manager.is_heating():
                heat()
            if joystick_manager.is_cooling():
                cool()

            # (If you add an in-game pause menu with buttons later, you would add:
            # if game.paused: joystick_manager.update_menu(self.handler.buttons) )
            
            running = self.handler.update()

            dt_real = clock.tick(60) / 1000.0  # Convert milliseconds to seconds
            accumulated_gamehours += dt_real * game.speed * (not game.paused)  # h/s
            # print(f"{game.hour=}, {accumulated_gamehours:1f}, {game.model.comfort_score_tsd[game._mh]}")

            self.debug = {
                "FPS": lambda: f"{clock.get_fps():2.1f}",
                "Acc. hours": lambda: f"{accumulated_gamehours:.2f} h",
                "State": game.__repr__,
                "Speed": lambda: f"{game.speed:.0f} h/s",
                "Camera Zoom": lambda: f"{camera.zoom_level} h/s",
                "LEVEL": lambda: f"{game.current_level_index:.0f}",
            }

            if not game.paused and accumulated_gamehours >= 1:
                hours = int(accumulated_gamehours)
                accumulated_gamehours -= hours

                if AUTOPILOT:
                    if game.TI < 0.5+game.model.comfort.minimum_room_temperature:
                        heat()
                        
                    if game.TI > -0.5+game.model.comfort.maximum_room_temperature:
                        cool()

                game.update(hours=hours)

                if game.hour + accumulated_gamehours >= game.final_hour_of_the_year - 1:
                    if not AUTOPILOT: 
                        level_success()

                if game.is_bankrupt():
                    game_over(reason=language.BANKRUPT)

                if game.is_too_hot():
                    level_fail(text=language.TOO_HOT, reason="Too hot")

                if game.is_too_cold():
                    level_fail(text=language.TOO_COLD, reason="Too cold")

            
            particle_manager.update()

            self.render()

            game.cleanup()

            if game.finished and not AUTOPILOT:
                running = False

    @override
    def render(self) -> None:
        renderer.camera.update()
        renderer.set_background(get_background(game.hour))
        renderer.draw_background(game.hour)
        renderer.render_curves(game.get_curves_data(), game.paused)

        particle_manager.render()
        if game.get_temp_diff() > settings.TEMP_WARNING_THRESHOLD:
            renderer.draw_too_hot_warning()
        if game.get_temp_diff() < -settings.TEMP_WARNING_THRESHOLD:
            renderer.draw_too_cold_warning()
            sound_manager.cold_warning()
        if game.money < settings.MONEY_WARNING_THRESHOLD:
            renderer.draw_low_money_warning()

        renderer.render_ui(game.get_ui_data())

        if game.paused:
            renderer.draw_paused_overlay()

        if AUTOPILOT:
            renderer.draw_overlay("Autopilot engaged. Press <a> to take control!")

        if DEBUG_MODE:
            renderer.debug(self.debug)

        for button in self.handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


class Popup(Screen):
    """Basic popup screen for short messages to the player.

    Generally has a title, text body (message) and simple buttons (e.g. 'Back', 'Continue').
    """

    def __init__(
        self,
        title: str,
        body: list[str],
        buttons: list[Button] = None,
        keys: list[tuple[int, callable]] = None,
        fail_reason = False,
    ):
        self.title = title
        self.body = body
        self.buttons = buttons
        self.keys = keys
        self.fail_reason = fail_reason
        super().__init__()

    @override
    def render(self) -> None:
        index = game.insulation_level  
        if self.fail_reason:
            index = 5 # no money
            if self.fail_reason == "Too hot":
                index = 3 
            elif self.fail_reason == "Too cold":
                index = 4
                
        renderer.render_popup(
            title=self.title,
            body=self.body,
            screen_params=center_screen(size=0.8),
            index=index,
        )
        for button in self.handler.buttons:
            renderer.render_button(button)
        particle_manager.render()
        screen.blit(renderer.display, (0, 0))
        pg.display.update()

    @override
    def config_handler(self) -> None:
        self.handler.bind_keypress(pg.K_q, quit_game)
        self.handler.bind_keypress(pg.K_s, take_screenshot)
        self.handler.bind_keypress(pg.K_m, toggle_audio)
        
        if self.buttons:
            [self.handler.register_button(button) for button in self.buttons]
        if self.keys:
            [self.handler.bind_keypress(pg_key, fun) for pg_key, fun in self.keys]


class Victory(Screen):
    """Basic popup screen for short messages to the player.

    Generally has a title, text body (message) and simple buttons (e.g. 'Back', 'Continue').
    """

    def __init__(self):
        self.title = language.VICTORY_HEAD
        self.body = [language.VICTORY_TEXT]         # needs to be list
        # Text input position near center popup; adjust as needed
        input_pos = (180,300)  # or a fixed (x, y)
        submit_score = None
        self.name_input = TextInput(
            pos=input_pos,
            size=(900, 60),
            placeholder="Enter your name",
            text="",
            max_length=24,
        )
        def submit_score():
            save_highscore(self.name_input.text, calculate_score())
            start_highscore_loop

        self.buttons = (
            Button(
                get_btn_pos("popup right"),
                submit_score,
                language.SAVE_HIGHSCORE,
                size=settings.BUTTON_SIZE["Start New Game"],
            ),
            # Button(
            #     get_btn_pos("bottom center"),
            #     lambda: calculate_score(),
            #     "Calculate Score",
            #     size=settings.BUTTON_SIZE["Start New Game"],
            # )
        )
        self.keys = [
            (pg.K_RETURN, submit_score),  # keep if you want Enter to also start
            (pg.K_ESCAPE, start_new_game),
            (pg.K_r, start_new_game)
        ]
        super().__init__()

    @override
    def render(self) -> None:
        renderer.menu_renderer.render_background(index=game.insulation_level)
        if random.random() < 0.5:
            x = random.randint(0, settings.SCREEN_RESOLUTION[0])
            y = random.randint(0, settings.SCREEN_RESOLUTION[1])
            particle_manager.success(
                position=(x, y),
                velocity=(random.randint(-10, 10), random.randint(-10, 10)),
            )

        renderer.render_popup(
            title=self.title,
            body=self.body,
            screen_params=center_screen(size=0.8),
            index=game.insulation_level
        )

        # NEW: draw the input
        renderer.render_text_input(self.name_input)

        for button in self.handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()

    @override
    def config_handler(self) -> None:
        self.handler.bind_keypress(pg.K_q, quit_game)
        self.handler.bind_keypress(pg.K_s, take_screenshot)
        self.handler.bind_keypress(pg.K_m, toggle_audio)
        if self.buttons:
            [self.handler.register_button(button) for button in self.buttons]
        # NEW: register text input
        self.handler.register_input(self.name_input)
        if self.keys:
            [self.handler.bind_keypress(pg_key, fun) for pg_key, fun in self.keys]           

class HighscoreScreen(Screen):
    """Highscore screen, where player can view the best scores."""

    @override
    def config_handler(self) -> None:
        # register buttons

        buttons = [
            Button(
                get_btn_pos("bottom left"),
                start_title_loop,
                language.MAIN_MENU,
            ),
            Button(
                (get_btn_pos("bottom center")),
                start_shop_loop,
                language.SHOP,
            ),
            Button(
                get_btn_pos("bottom right"),
                start_new_game,
                language.START_NEW_GAME,
            ),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, start_level_intro)
        self.handler.bind_keypress(pg.K_q, quit)
        self.handler.bind_keypress(pg.K_s, take_screenshot)
        self.handler.bind_keypress(pg.K_m, toggle_audio)
        self.handler.bind_keypress(pg.K_r, start_new_game)
        # self.handler.bind_keypress(pg.K_ESCAPE, quit_game)

    @override
    def render(self) -> None:
        renderer.render_highscores(scoreboard.get_highscores())

        for button in self.handler.buttons:
            renderer.render_button(button)

        particle_manager.render()

        screen.blit(renderer.display, (0, 0))
        pg.display.update()

    @override
    def loop(self) -> None:
        """Basic handler/render loop."""
        running = True
        while running:
            # Process discrete button navigation
            joystick_manager.update_menu(self.handler.buttons)

            running = self.handler.update()
            particle_manager.update()
            self.render()

            clock.tick(60)

"""Screen instances"""

title_screen = TitleScreen()
shop_screen = ShopScreen()
level_screen = LevelScreen()
highscore_screen = HighscoreScreen()


"""Start"""

# start by entering title screen


start_new_game()
