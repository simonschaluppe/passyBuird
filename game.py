import pygame as pg

from typing import override

from camera import Camera2D
from handler import Button, InputHandler
from renderer import Renderer
from particles import ParticleManager
from model.GameModel import GameModel

# Initialize pygame
pg.init()
print(pg.version)

# Set up the main display surface
screen = pg.display.set_mode((800, 600))
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


def start_game():
    game.setup_sim()
    level_screen.loop()


class Screen:
    def __init__(self):
        self.handler = InputHandler()
        self.config_handler()

    def loop(self):
        running = True
        while running:
            running = self.handler.update()
            self.render()
            clock.tick(60)

    def config_handler(self):
        ...

    def render(self):
        ...


class TitleScreen(Screen):

    @override
    def config_handler(self):
        # register buttons
        buttons = [
            Button((120, 480), shop_screen.loop(), "Start the Game!"),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, shop_screen.loop())

    @override
    def render(self):
        description = ["This game is fun!", "This game is cool!"]
        renderer.render_title_screen(title="Welcome to PassyBuirld!", body=description)

        for button in self.handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


class ShopScreen(Screen):

    @override
    def config_handler(self):
        # register buttons
        buttons = [
            Button((600, 480), start_game, "Start the Game!"),
            Button((600, 530), quit_game, "Quit"),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, start_game)
        self.handler.bind_keypress(pg.K_q, quit)
        self.handler.bind_keypress(pg.K_ESCAPE, quit_game)

    @override
    def render(self):
        renderer.render_menu(game.get_menu_data())

        for button in self.handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


class LevelScreen(Screen):

    @override
    def config_handler(self):

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
        self.handler.bind_keypress(pg.K_ESCAPE, shop_screen.loop())

    @override
    def loop(self):
        """The main game loop responsible for processing events, updating game state, and rendering."""
        running = True
        accumulated_gamehours = 0
        while running:
            running = self.handler.update()

            dt_real = clock.tick(60) / 1000.0  # Convert milliseconds to seconds
            accumulated_gamehours += dt_real * game.speed * (not game.paused)  # h/s
            print(game.hour, accumulated_gamehours)

            if game.hour + accumulated_gamehours >= game.final_hour_of_the_year - 1:
                level_success_popup.loop()()

            if game.paused:
                continue

            if accumulated_gamehours >= 1:
                hours = int(accumulated_gamehours)
                accumulated_gamehours -= hours
                game.update(hours=hours)

            if game.money <= 0:
                level_fail_popup.loop()()

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
    def render(self):

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
    def __init__(self, title, body):
        self.title = title
        self.body = body
        super().__init__()

    @override
    def config_handler(self):

        # register buttons
        buttons = [
            Button((120, 480), shop_screen.loop(), "OK"),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, shop_screen.loop())
        self.handler.bind_keypress(pg.K_ESCAPE, shop_screen.loop())

    @override
    def loop(self):
        """Displays end-of-level summary before returning to menu."""
        end_running = True
        while end_running:
            self.handler.update()
            self.render()

    @override
    def render(self):
        renderer.render_popup(title=self.title, body=self.body)
        for button in self.handler.buttons:
            renderer.render_button(button)
        screen.blit(renderer.display, (0, 0))
        pg.display.update()


# Screen instances
title_screen = TitleScreen()
shop_screen = ShopScreen()
level_screen = LevelScreen()

# Popup screen instances
level_success_popup = Popup(
    title="You survived the year!",
    body=[f"{label}: {value}" for label, value in game.get_kpis().items()],
)
level_fail_popup = Popup(
    title="Du hast kein Geld mehr!",
    body=[f"{label}: {value}" for label, value in game.get_kpis().items()],
)

# start by entering title screen
title_screen.loop()
