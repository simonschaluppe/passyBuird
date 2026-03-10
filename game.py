from typing import override

import pygame as pg

from camera import Camera2D
from handler import Button, InputHandler
from model.GameModel import GameModel
from particles import ParticleManager
from renderer import Renderer

# Initialize pygame
pg.init()
print(pg.version)

# Set up the main display surface
screen: pg.Surface = pg.display.set_mode((800, 600))
pg.display.set_caption("passyBUIRLD")

# Create another surface to perform off-screen drawing
display = pg.Surface((800, 600))

clock = pg.time.Clock()
game = GameModel()
particle_manager = ParticleManager()

# Set up the camera with a zoom feature
camera = Camera2D(surface=display, game_world_position=game.position, zoom=(2, 5))
camera.follow(game, maxdist=0)

# Set up renderer
renderer = Renderer(display, camera, clock)

"""Callback functions"""

# Single line functions
return_home = lambda: title_screen.loop()
start_level = lambda: level_screen.loop()
enter_shop = lambda: shop_screen.loop()
level_entry = lambda: level_entry_popup.loop()
level_success = lambda: level_success_popup.loop()
level_fail = lambda: level_fail_popup.loop()


# Multi line functions
def quit_game():
    print("Quitting game...")
    pg.quit()
    quit()


def heat():
    game.heat()
    particle_manager.heat(
        game.position, (0, -game.qh)
    )


def cool():
    game.cool()
    particle_manager.cool(
        game.position, (0, -game.qc)
    )


def start_new_level():
    game.setup_next_level()
    level_entry()


def start_new_game():
    game.setup_new_game()
    return_home()


"""Classes"""


class Screen:
    """Basic Screen class."""

    def __init__(self):
        self.handler = InputHandler()
        self.config_handler()

    def loop(self) -> None:
        """Basic handler/render loop."""
        running = True
        while running:
            running = self.handler.update()
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
            Button((120, 480), enter_shop, "Start the Game!"),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, start_new_level)

    @override
    def render(self) -> None:
        description = ["This game is fun!", "This game is cool!"]
        renderer.render_title_screen(title="Welcome to PassyBuirld!", body=description)

        for button in self.handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


class ShopScreen(Screen):
    """Shop screen, where player can view and purchase upgrades."""

    @override
    def config_handler(self) -> None:
        # register buttons
        upgrade_button = lambda upgrade, pos: Button(
            pos, upgrade.callback, f"{upgrade.upgrade_text}  €{upgrade.cost}", size=(220, 30)
        )
        buttons = [
            Button((600, 530), start_new_level, "Next level"),
            Button((25, 530), quit_game, "Quit Run"),
            upgrade_button(game.upgrades['wall_insulation'], (335, 290)),
            upgrade_button(game.upgrades['power'], (335, 340)),
            upgrade_button(game.upgrades['heatpump_efficiency'], (335, 390)),
            upgrade_button(game.upgrades['electricity_price_discount'], (335, 440)),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, start_new_level)
        self.handler.bind_keypress(pg.K_q, quit)
        # self.handler.bind_keypress(pg.K_ESCAPE, quit_game)

    @override
    def render(self) -> None:
        renderer.render_menu(game.get_menu_data())

        for button in self.handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


class LevelScreen(Screen):
    """Level screen, where the actual gameplay happens."""

    @override
    def config_handler(self) -> None:

        # bind camera
        self.handler.bind_camera(camera)

        # bind key presses
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
        self.handler.bind_keypress(pg.K_ESCAPE, enter_shop)

    @override
    def loop(self) -> None:
        """The level loop responsible for processing events, updating game state, and rendering."""
        running = True
        accumulated_gamehours = 0
        while running:
            running = self.handler.update()

            dt_real = clock.tick(60) / 1000.0  # Convert milliseconds to seconds
            accumulated_gamehours += dt_real * game.speed * (not game.paused)  # h/s
            print(game.hour, accumulated_gamehours)

            if game.hour + accumulated_gamehours >= game.final_hour_of_the_year - 1:
                level_success()

            if game.paused:
                continue

            if accumulated_gamehours >= 1:
                hours = int(accumulated_gamehours)
                accumulated_gamehours -= hours
                game.update(hours=hours)

            if game.money <= 0:
                level_fail()

            particle_manager.update()

            # debug
            fps = clock.get_fps()
            debug = {
                "FPS": lambda: f"{fps:2.1f}",
                "Acc. hours": lambda: f"{accumulated_gamehours:.2f} h",
                "State": game.__repr__,
                "Speed": lambda: f"{game.speed:.0f} h/s",
            }
            renderer.debug(debug)

            self.render()

            game.cleanup()

            if game.finished:
                running = False

    @override
    def render(self) -> None:

        # render
        renderer.camera.update()
        renderer.draw_background(game.hour)

        renderer.draw_heat_particles(particle_manager.groups["heating"])
        renderer.draw_cool_particles(particle_manager.groups["cooling"])
        renderer.render_curves(game.get_curves_data())
        renderer.render_ui(game.get_ui_data())

        for button in self.handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


class Popup(Screen):
    """Basic popup screen for short messages to the player.

    Generally has a title, text body (message) and simple buttons (e.g. 'Back', 'Continue')."""

    def __init__(self, title: str, body: list[str], buttons: list[Button] = None,
                 keys: list[tuple[int, callable]] = None):
        self.title = title
        self.body = body
        self.buttons = buttons
        self.keys = keys
        super().__init__()

    @override
    def render(self) -> None:
        renderer.render_popup(title=self.title, body=self.body)
        for button in self.handler.buttons:
            renderer.render_button(button)
        screen.blit(renderer.display, (0, 0))
        pg.display.update()

    @override
    def config_handler(self) -> None:
        if self.buttons:
            [self.handler.register_button(button) for button in self.buttons]
        if self.keys:
            [self.handler.bind_keypress(pg_key, fun) for pg_key, fun in self.keys]


"""Screen instances"""

title_screen = TitleScreen()
shop_screen = ShopScreen()
level_screen = LevelScreen()

"""Popup screen instances"""

level_entry_popup = Popup(
    title="Ready?",
    body=["Ready?"],
    buttons=[
        Button((120, 480), start_level, "OK")
    ],
    keys=[
        (pg.K_RETURN, start_level),
        (pg.K_ESCAPE, return_home),
    ],
)
level_success_popup = Popup(
    title="You survived the year!",
    body=[f"{label}: {value}" for label, value in game.get_kpis().items()],
    buttons=[
        Button((120, 480), enter_shop, "OK")
    ],
    keys=[
        (pg.K_RETURN, enter_shop),
        (pg.K_ESCAPE, enter_shop),
    ],
)
level_fail_popup = Popup(
    title="Du hast kein Geld mehr!",
    body=[f"{label}: {value}" for label, value in game.get_kpis().items()],
    buttons=[
        Button((120, 480), start_new_game, "OK")
    ],
    keys=[
        (pg.K_RETURN, start_new_game),
        (pg.K_ESCAPE, start_new_game),
    ],
)

"""Start"""

# start by entering title screen
return_home()
