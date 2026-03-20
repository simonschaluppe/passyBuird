from typing import override

import pygame as pg
import random

from camera import Camera2D
from handler import Button, InputHandler
from model.GameModel import GameModel
from particles import ParticleManager
from renderer import Renderer

GODMODE = False

SCREEN_RESOLUTION = (1920, 1080)

# Initialize pygame
pg.init()
print(pg.version)

# Set up the main display surface
screen: pg.Surface = pg.display.set_mode(SCREEN_RESOLUTION)
pg.display.set_caption("passyBUIRLD")

# Create another surface to perform off-screen drawing
display = pg.Surface(SCREEN_RESOLUTION)

clock = pg.time.Clock()
game = GameModel()
particle_manager = ParticleManager()

# Set up the camera with a zoom feature
camera = Camera2D(surface=display, game_world_position=(game.position[0],0), zoom=(14, 100))
camera.follow(game, maxdist=0)

# Set up renderer
renderer = Renderer(display, camera, clock, font = "Comic Sans MS")

"""Callback functions"""

# Single line functions
return_home = lambda: title_screen.loop()
start_level = lambda: level_screen.loop()
enter_shop = lambda: shop_screen.loop()
money_death = lambda: level_fail('money')
heat_death = lambda: level_fail('heat')
freeze_death = lambda: level_fail('freeze')

def center_screen(size = 0.8):
    # Position & Size
    width = SCREEN_RESOLUTION[0] * size
    height = SCREEN_RESOLUTION[1] * size
    left = SCREEN_RESOLUTION[0] * 0.1
    top = SCREEN_RESOLUTION[1] * 0.1
    return (left, top, width, height)

def get_btn_pos(orientation = None):
    """
    Parameter "orientation" can be "top left", "top right", "bottom left", "bottom right", "popup left" or "popup right".
    
    Function returns a touple with relative button coordinates (x,y).

    "offset" reduces distance from center in percent for popups.
    """
    
    if orientation == None:
        raise ValueError("The parameter 'orientation' cannot be None.")
    elif orientation == "top left":
        return (SCREEN_RESOLUTION[0]*0.18, SCREEN_RESOLUTION[1]*0.07)
    elif orientation == "top right":
        return (SCREEN_RESOLUTION[0]*0.9, SCREEN_RESOLUTION[1]*0.07)
    elif orientation == "bottom left":
        return (SCREEN_RESOLUTION[0]*0.02, SCREEN_RESOLUTION[1]*0.93)
    elif orientation == "bottom right":
        return (SCREEN_RESOLUTION[0]*0.9, SCREEN_RESOLUTION[1]*0.93)
    elif orientation == "popup left":
        return (220, 900) # not dynamic yet
    elif orientation == "popup right":
        return (1550, 900) # not dynamic yet   
    else:
        return False
    

# Multi line functions
def level_entry():
    renderer.set_background(game.current_level.background)
    level_entry_popup = Popup(
        title=game.current_level.name,
        body=game.current_level.intro,
        buttons=[
            Button(get_btn_pos("popup right"), start_level, "OK")
        ],
        keys=[
            (pg.K_RETURN, start_level),
            (pg.K_ESCAPE, return_home),
        ],
    )
    level_entry_popup.loop()


def level_success():
    game.money += game.current_level.reward
    #level_success_popup.title= "You survived level " + str(game.current_level.number) + "!", # not working...
    level_success_popup.body = [f"{label}: {value}" for label, value in game.get_kpis().items()]
    for _ in range(300): 
        x = random.randint(0, SCREEN_RESOLUTION[0])
        y = random.randint(0, SCREEN_RESOLUTION[1])
        particle_manager.success(position=(x,y), velocity=(random.randint(-10,10), random.randint(-10,10)))

    victory = not game.setup_next_level()
    if victory:
        victory_loop()
    level_success_popup.loop()

def victory_loop():
    game.reset_levels()
    for _ in range(300): 
        x = random.randint(0, SCREEN_RESOLUTION[0])
        y = random.randint(0, SCREEN_RESOLUTION[1])
        particle_manager.success(position=(x,y), velocity=(random.randint(-10,10), random.randint(-10,10)))
    print("You've finished the game, Good Job!")
    Victory().loop()


def level_fail(cause: str):

    match cause:
        case "money":
            title = "Du hast kein Geld mehr!"
        case "heat":
            title = "Everyone died of heat stroke!"
        case "freeze":
            title = "Everyone froze into icicles!"
            text = "Your average comfort was ..."


    Popup(
        title=title,
        body=[f"{label}: {value}" for label, value in game.get_kpis().items()],
        buttons=[
            Button(get_btn_pos("popup left"), enter_shop, "Return to Shop", size = (250,60))
        ],
        keys=[
            (pg.K_RETURN, start_new_game),
            (pg.K_ESCAPE, start_new_game),
        ],
    ).loop()


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


def start_new_game():
    game.setup_new_game()
    return_home()



#def place_buttons()

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
            Button(get_btn_pos("popup left"), enter_shop, "Start the Game!", size = (240,60)),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, level_entry)

    @override
    def render(self) -> None:
        description = [
            "Congratulations! You just bought your very own house and you can't wait to spend",
            "the Winter warm and comfortable. The only issue is - heating has become very",
            "expensive... and a major contributor to climate change!",
            "But don't fret! You're smart! And dextrous! With these qualities, you can decide",
            "exactly how much heating energy you need to be super comfortable all year",
            "long and conserve the climate along the way.",
            "Come on, let's get started!"
        ]
        
        renderer.render_title_screen(title="Welcome to PassyBuirld!", body=description, screen_params = center_screen(size = 0.8))

        for button in self.handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


class ShopScreen(Screen):
    """Shop screen, where player can view and purchase upgrades."""

    @override
    def config_handler(self) -> None:
        # register buttons
        def upgrade_button(upgrade, pos):
            def callback():
                particale_amount = 10
                for _ in range(particale_amount):
                    particle_manager.purchase(position=pg.mouse.get_pos(), velocity=(0, 5)) 
                    particle_manager.purchase(position=pg.mouse.get_pos(), velocity=(0, -5)) 
                upgrade.callback()

            return Button(pos, callback, f"{upgrade.upgrade_text}  €{upgrade.cost}", size=(400, 60))


        buttons = [
            Button(get_btn_pos("bottom right"), level_entry, "Start Level", size = (190,60)),
            Button(get_btn_pos("bottom left"), quit_game, "Quit Game", size = (170,60)),
            upgrade_button(game.upgrades['wall_insulation'], (500, 375)),
            upgrade_button(game.upgrades['power'], (500, 425)),
            upgrade_button(game.upgrades['heatpump_efficiency'], (500, 475)),
            upgrade_button(game.upgrades['electricity_price_discount'], (500, 525)),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, level_entry)
        self.handler.bind_keypress(pg.K_q, quit)
        # self.handler.bind_keypress(pg.K_ESCAPE, quit_game)

    @override
    def render(self) -> None:
        renderer.render_menu(game.get_menu_data())

        for button in self.handler.buttons:
            renderer.render_button(button)

        renderer.draw_purchase_particles(particle_manager.groups["purchase"])

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
        self.handler.bind_keypress(pg.K_w, level_success)
        self.handler.bind_keypress(pg.K_v, victory_loop)
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

            if game.money <= 0 and not GODMODE:
                money_death()

            TI = game.model.TI[game._mh]
            if game.model.comfort.comfort_score(TI) < game.current_level.min_comfort and not GODMODE:
                if game.model.comfort.comfort_diff(TI) > 0:
                    heat_death()
                if game.model.comfort.comfort_diff(TI) < 0:
                    freeze_death()

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
        renderer.draw_background()
        renderer.render_popup(title=self.title, body=self.body, screen_params = center_screen(size = 0.8))
        for button in self.handler.buttons:
            renderer.render_button(button)
        renderer.draw_particles(particle_manager.groups["success"], color=(random.randint(100,200), random.randint(200,255), random.randint(100,200)))
        screen.blit(renderer.display, (0, 0))
        pg.display.update()

    @override
    def config_handler(self) -> None:
        if self.buttons:
            [self.handler.register_button(button) for button in self.buttons]
        if self.keys:
            [self.handler.bind_keypress(pg_key, fun) for pg_key, fun in self.keys]


class Victory(Screen):
    """Basic popup screen for short messages to the player.

    Generally has a title, text body (message) and simple buttons (e.g. 'Back', 'Continue')."""

    def __init__(self):
        self.title = "You beat the game!"
        self.body = "Congratulations, etc"
        self.buttons = Button(get_btn_pos("popup right"), enter_shop, "Start new Game!"),
        self.keys = [(pg.K_RETURN, enter_shop),(pg.K_ESCAPE, enter_shop),]
        super().__init__()

    @override
    def render(self) -> None:
        if random.random() < 0.5: 
            x = random.randint(0, SCREEN_RESOLUTION[0])
            y = random.randint(0, SCREEN_RESOLUTION[1])
            particle_manager.success(position=(x,y), velocity=(random.randint(-10,10), random.randint(-10,10)))

        renderer.render_popup(title=self.title, body=self.body, screen_params = center_screen(size = 0.8))
        for button in self.handler.buttons:
            renderer.render_button(button)
        renderer.draw_particles(particle_manager.groups["success"], color=(random.randint(100,255), random.randint(100,255), random.randint(100,255)))
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

level_success_popup = Popup(
    title="You survived level " + str(game.current_level.number) + "!", # not working...
    body=[f"{label}: {value}" for label, value in game.get_kpis().items()],
    buttons=[
        Button(get_btn_pos("popup right"), enter_shop, "OK")
    ],
    keys=[
        (pg.K_RETURN, enter_shop),
        (pg.K_ESCAPE, enter_shop),
    ],
)

"""Start"""
if GODMODE:
    game.money = 1_000_000
# start by entering title screen
return_home()
