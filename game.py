# Import required modules and classes

import pygame as pg
from camera import Camera2D
from model.GameModel import GameModel
from handler import Button, InputHandler
from renderer import Renderer
from particles import ParticleManager


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


enter_shop = lambda: shop_screen.loop()
level_success = lambda: level_success_popup.loop()
level_fail = lambda: level_fail_popup.loop()


class TitleScreen:
    def __init__(self, screen, renderer, clock):
        self.screen = screen
        self.renderer = renderer
        self.clock = clock

        # handler
        self.handler = InputHandler()
        self.config_handler()

    def config_handler(self):
        # register buttons
        buttons = [
            Button((120, 480), enter_shop, "Start the Game!"),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, enter_shop)

    def loop(self):
        running = True
        while running:
            running = self.handler.update()
            self.render()
            self.clock.tick(60)

    def render(self):
        description = ["This game is fun!", "This game is cool!"]
        self.renderer.render_title_screen(title="Welcome to PassyBuirld!", body=description)

        for button in self.handler.buttons:
            self.renderer.render_button(button)

        self.screen.blit(self.renderer.display, (0, 0))
        pg.display.update()


class ShopScreen:
    def __init__(self, screen, renderer, clock):
        self.screen = screen
        self.renderer = renderer
        self.clock = clock

        # handler
        self.handler = InputHandler()
        self.config_handler()

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

    def loop(self):
        running = True
        while running:
            running = self.handler.update()
            self.render()
            self.clock.tick(60)

    def render(self):
        self.renderer.render_menu(game.get_menu_data())

        for button in self.handler.buttons:
            self.renderer.render_button(button)

        self.screen.blit(self.renderer.display, (0, 0))
        pg.display.update()


class LevelScreen:
    def __init__(self, screen, renderer, clock):
        self.screen = screen
        self.renderer = renderer
        self.clock = clock

        # handler
        self.handler = InputHandler()
        self.config_handler()

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
        self.handler.bind_keypress(pg.K_ESCAPE, enter_shop)

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

            fps = clock.get_fps()
            debug = {
                "FPS": lambda: f"{fps:2.1f}",
                "Acc. hours": lambda: f"{accumulated_gamehours:.2f} h",
                "State": game.__repr__,
                "Speed": lambda: f"{game.speed:.0f} h/s",
            }

            self.render(debug=debug)

            game.cleanup()

            if game.finished:
                running = False

    def render(self, debug):

        # render
        self.renderer.camera.update()
        self.renderer.draw_background(game.hour)

        self.renderer.draw_heat_particles(particle_manager.groups["heating"])
        self.renderer.draw_cool_particles(particle_manager.groups["cooling"])
        self.renderer.render_curves(game.get_curves_data())
        self.renderer.render_ui(game.get_ui_data())

        for button in self.handler.buttons:
            self.renderer.render_button(button)

        self.renderer.debug(debug)

        screen.blit(self.renderer.display, (0, 0))
        pg.display.update()


class LevelSuccessPopup:
    def __init__(self, screen, renderer, game):
        self.screen = screen
        self.renderer = renderer
        self.game = game

        # handler
        self.handler = InputHandler()
        self.config_handler()

    def config_handler(self):

        # register buttons
        buttons = [
            Button((120, 480), enter_shop, "OK"),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, enter_shop)
        self.handler.bind_keypress(pg.K_ESCAPE, enter_shop)

    def loop(self):
        """Displays end-of-level summary before returning to menu."""
        end_running = True
        while end_running:
            self.handler.update()
            self.render()

    def render(self):

        lines = [f"{label}: {value}" for label, value in game.get_kpis().items()]
        renderer.render_popup("You survived the year!", lines)
        for button in self.handler.buttons:
            renderer.render_button(button)
        screen.blit(renderer.display, (0, 0))
        pg.display.update()


class LevelFailPopup:
    def __init__(self, screen, renderer, game):
        self.screen = screen
        self.renderer = renderer
        self.game = game

        # handler
        self.handler = InputHandler()
        self.config_handler()

    def config_handler(self):

        # register buttons
        buttons = [
            Button((120, 480), enter_shop, "OK"),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, enter_shop)
        self.handler.bind_keypress(pg.K_ESCAPE, enter_shop)

    def loop(self):
        """Displays end-of-level summary before returning to menu."""

        game.setup_new_game()

        end_running = True
        while end_running:
            self.handler.update()
            self.render()

    def render(self):

        lines = [f"{label}: {value}" for label, value in game.get_kpis().items()]
        renderer.render_popup("Du hast kein Geld mehr!", lines)
        for button in self.handler.buttons:
            renderer.render_button(button)
        screen.blit(renderer.display, (0, 0))
        pg.display.update()


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

renderer = Renderer(display, camera, clock)

title_screen = TitleScreen(screen=screen, renderer=renderer, clock=clock)
shop_screen = ShopScreen(screen=screen, renderer=renderer, clock=clock)
level_screen = LevelScreen(screen=screen, renderer=renderer, clock=clock)

level_success_popup = LevelSuccessPopup(screen=screen, renderer=renderer, game=game)
level_fail_popup = LevelFailPopup(screen=screen, renderer=renderer, game=game)

# start by entering title screen
title_screen.loop()
