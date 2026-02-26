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


def level_loop(
        screen,
        game: GameModel,
        renderer: Renderer,
        input_handler: InputHandler,
        clock: pg.time.Clock,
        particle_manager: ParticleManager,
):
    """The main game loop responsible for processing events, updating game state, and rendering."""
    running = True
    accumulated_gamehours = 0
    while running:
        running = input_handler.update()

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
        # render
        renderer.camera.update()
        renderer.draw_background(game.hour)

        renderer.draw_heat_particles(particle_manager.groups["heating"])
        renderer.draw_cool_particles(particle_manager.groups["cooling"])
        renderer.render_curves(game.get_curves_data())
        renderer.render_ui(game.get_ui_data())

        for button in input_handler.buttons:
            renderer.render_button(button)

        fps = clock.get_fps()
        renderer.debug(
            {
                "FPS": lambda: f"{fps:2.1f}",
                "Acc. hours": lambda: f"{accumulated_gamehours:.2f} h",
                "State": game.__repr__,
                "Speed": lambda: f"{game.speed:.0f} h/s",
            }
        )

        screen.blit(renderer.display, (0, 0))
        pg.display.update()

        game.cleanup()

        if game.finished:
            running = False


def shop_screen(screen, renderer: Renderer, menu_handler: InputHandler, clock):
    running = True
    while running:
        running = menu_handler.update()

        renderer.render_menu(game.get_menu_data())

        for button in menu_handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()
        clock.tick(60)


def level_success_popup(screen, renderer: Renderer, game: GameModel):
    """Displays end-of-level summary before returning to menu."""
    end_running = True
    lines = [f"{label}: {value}" for label, value in game.get_kpis().items()]
    while end_running:
        popup_handler.update()
        renderer.render_popup("You survived the year!", lines)
        for button in popup_handler.buttons:
            renderer.render_button(button)
        screen.blit(renderer.display, (0, 0))
        pg.display.update()


def level_fail_popup(screen, renderer: Renderer, game: GameModel):
    end_running = True
    lines = [f"{label}: {value}" for label, value in game.get_kpis().items()]
    game.setup_new_game()
    while end_running:
        popup_handler.update()
        renderer.render_popup("Du hast kein Geld mehr!", lines)
        for button in popup_handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


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
    level_loop(
        screen=screen,
        game=game,
        renderer=renderer,
        input_handler=level_handler,
        clock=clock,
        particle_manager=particle_manager,
    )


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

shop_handler = InputHandler()
level_handler = InputHandler()
popup_handler = InputHandler()

enter_shop = lambda: shop_screen(
    screen, renderer=renderer, menu_handler=shop_handler, clock=clock
)

level_success = lambda: level_success_popup(
    screen, renderer=renderer, game=game)

level_fail = lambda: level_fail_popup(
    screen, renderer=renderer, game=game)

# shop handler
shop_buttons = [
    Button((600, 480), start_game, "Start the Game!"),
    Button((600, 530), quit_game, "Quit"),
]

shop_handler.bind_keypress(pg.K_RETURN, start_game)
shop_handler.bind_keypress(pg.K_q, quit)
shop_handler.bind_keypress(pg.K_ESCAPE, quit_game)
# menu_handler.bind_mousebutton(1, startgame)
[shop_handler.register_button(button) for button in shop_buttons]

# level handler
level_handler.bind_camera(camera)
level_handler.bind_continuous_keypress(pg.K_UP, heat)
level_handler.bind_continuous_keypress(pg.K_DOWN, cool)
level_handler.bind_continuous_mousebutton(0, heat)
level_handler.bind_continuous_mousebutton(2, cool)
level_handler.bind_keypress(pg.K_p, game.toggle_pause)
level_handler.bind_keypress(pg.K_1, lambda: game.set_speed(12))
level_handler.bind_keypress(pg.K_2, lambda: game.set_speed(24))
level_handler.bind_keypress(pg.K_3, lambda: game.set_speed(24 * 7))
level_handler.bind_keypress(pg.K_4, lambda: game.set_speed(24 * 7 * 2))
level_handler.bind_keypress(pg.K_5, lambda: game.set_speed(24 * 7 * 4))
level_handler.bind_keypress(pg.K_w, lambda: game.increment_cop(0.5))
level_handler.bind_keypress(pg.K_s, lambda: game.increment_cop(-0.5))
level_handler.bind_keypress(pg.K_q, quit_game)
level_handler.bind_keypress(pg.K_ESCAPE, enter_shop)

# popup handler
ok_button = Button((120, 480), enter_shop, "OK")

popup_handler.bind_keypress(pg.K_RETURN, enter_shop)
popup_handler.bind_keypress(pg.K_ESCAPE, enter_shop)
popup_handler.register_button(ok_button)

title_screen = TitleScreen(screen=screen, renderer=renderer, clock=clock)

# start by entering title screen
title_screen.loop()
