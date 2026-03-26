from re import DEBUG
from typing import override

import pygame as pg
import random

import settings
from camera import Camera2D
from handler import Button, InputHandler
from model.GameModel import GameModel
from particles import ParticleManager
from renderer import Renderer



DEBUG_MODE = True

# Initialize pygame
pg.init()
print(pg.version)
# Set up the main display surface
screen: pg.Surface = pg.display.set_mode(settings.SCREEN_RESOLUTION)
pg.display.set_caption("passyBUIRD")
# Create another surface to perform off-screen drawing
display = pg.Surface(settings.SCREEN_RESOLUTION)

clock = pg.time.Clock()
game = GameModel(speed=settings.GAME_SPEED, godmode=settings.GODMODE)

# Set up the camera with a zoom feature
camera = Camera2D(surface=display, game_world_position=(game.position[0],0), zoom=settings.GAME_ZOOM)
camera.follow(game, maxdist=0)

# Set up renderer
renderer = Renderer(display, camera, scale=0.8, font = settings.FONT)
particle_manager = ParticleManager(renderer=renderer)

def center_screen(size = 0.8):
    # Position & Size
    width = settings.SCREEN_RESOLUTION[0] * size
    height = settings.SCREEN_RESOLUTION[1] * size
    left = settings.SCREEN_RESOLUTION[0] * 0.1
    top = settings.SCREEN_RESOLUTION[1] * 0.1
    return (left, top, width, height)

def get_btn_pos(orientation = None):
    """
    Parameter "orientation" can be "top left", "top right", "bottom left", "bottom right", "popup left" or "popup right".
    
    Function returns a touple with screen coordinates (x,y).
    """
    return tuple(pixel * factor for pixel, factor in zip(settings.SCREEN_RESOLUTION, settings.SCREEN_ANCHORS.get(orientation, (0,0))))
    
#TODO: Move to utility or renderer
def get_background(hour_of_year):
        # Use modular arithmetic to cycle through the backgrounds
        background_paths = ["Dunkelflaute.png", "Spring.png", "Summer.png", "Fall.png", "Winter.png"]
        try:
            index = round(hour_of_year / 8760 * len(background_paths))
            #print("In Game Hour ", game.hour, " the index is ", index, " and the background is ", background_paths[index])
            return background_paths[index]
        except: return background_paths[1]


"""Callback functions"""

# Events

start_title_loop = lambda: title_screen.loop()
start_level_loop = lambda: level_screen.loop()
start_shop_loop = lambda: shop_screen.loop()


# Multi line functions
def start_new_game():
    game.setup_new_game()
    start_title_loop()

def game_over(reason="You have lost the game."):
    Popup(
        title="Game over!",
        body=[f"{label}: {value}" for label, value in game.get_kpis().items()],
        buttons=[
            Button(get_btn_pos("popup right"), start_new_game, "Start new game", size =settings.BUTTON_SIZE["Start New Game"])
        ],
        keys=[
            (pg.K_RETURN, start_new_game),
            (pg.K_ESCAPE, start_new_game),
        ],
    ).loop()

def start_level_intro(level=None):
    if level: game.setup_level(level)
    #renderer.set_background(game.current_level.background)
    level_intro_popup = Popup(
        title=game.current_level.name,
        body=game.current_level.intro,
        buttons=[
            Button(get_btn_pos("popup left"), start_shop_loop, "Go to Shop", size=settings.BUTTON_SIZE["Go to Shop"]),
            Button(get_btn_pos("popup right"), start_level_loop, "Start Level", size=settings.BUTTON_SIZE["Start Level"])
        ],
        keys=[
            (pg.K_RETURN, start_level_loop),
            (pg.K_ESCAPE, start_title_loop),
        ],
    )
    level_intro_popup.loop()

def level_fail(text: str):
    game.update_level_finished()
    game.setup_level()
    game.money += game.moneyspent
    game.moneyspent = 0

    title = "Level failed!"
    Popup(
        title=title,
        body=[text],
        buttons=[
            Button(get_btn_pos("popup left"), start_level_intro, "Retry", size=settings.BUTTON_SIZE["Retry"])
        ],
        keys=[
            (pg.K_RETURN, start_level_loop),
            (pg.K_ESCAPE, start_new_game),
        ],
    ).loop()

def level_success(): 
    game.update_level_finished()
    if game.current_level_index == len(game.levels):
        victory_loop()
    title=f"You survived level {game.current_level.number}!"
    level_success_popup = Popup(
        title=title,
        body=[f"{label}: {value}" for label, value in game.get_kpis().items()],
        buttons=[
            Button(get_btn_pos("popup right"), start_level_intro, "Continue", size = settings.BUTTON_SIZE["Continue"])
        ],
        keys=[
            (pg.K_RETURN, start_shop_loop),
            (pg.K_ESCAPE, start_shop_loop),
        ],
    )
    game.money += game.current_level.reward
    game.moneyspent = 0
    game.setup_next_level()
    for _ in range(50): 
        x = random.randint(0, settings.SCREEN_RESOLUTION[0])
        y = random.randint(0, settings.SCREEN_RESOLUTION[1])
        particle_manager.success(position=(x,y), velocity=(random.randint(-10,10), random.randint(-10,10)))
    level_success_popup.loop()

def victory_loop():
    game.reset_levels()
    for _ in range(50): 
        x = random.randint(0, settings.SCREEN_RESOLUTION[0])
        y = random.randint(0, settings.SCREEN_RESOLUTION[1])
        particle_manager.success(position=(x,y), velocity=(random.randint(-10,10), random.randint(-10,10)))
    print("You've finished the game, Good Job!")
    Victory().loop()


def toggle_debug_mode():
    global DEBUG_MODE
    DEBUG_MODE = not DEBUG_MODE
    print("DEBUG_MODE ", DEBUG_MODE)

def quit_game():
    print("Quitting game...")
    pg.quit()
    quit()


def heat():
    game.heat()
    particle_manager.heat(
        game.position, (-game.qh*0.5, -game.qh)
    )


def cool():
    game.cool()
    particle_manager.cool(
        game.position, (0.5*game.qc, -game.qc)
    )

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
            Button(get_btn_pos("popup right"), start_level_intro, "Start the Game!", size = settings.BUTTON_SIZE["Start New Game"]),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, start_level_intro)
        self.handler.bind_keypress(pg.K_q, quit_game)

    @override
    def render(self) -> None:
        description = [
            "Congratulations! You just bought your very own house and you can't wait to spend the",
            "Winter warm and comfortable. The only issue is - heating has become very expensive",
            "...and a major contributor to climate change!",
            "",
            "But don't fret! You're smart! And dextrous! With these qualities, you can decide",
            "exactly how much heating energy you need to be comfortable and conserve the climate",
            "along the way.",
            "",
            "Come on, let's get started!"
        ]
        
        renderer.render_title_screen(title="Welcome to ", body=description, screen_params = center_screen(0.8))

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

            return Button(pos, callback, f"{upgrade.upgrade_text}  €{upgrade.cost}", size=(450, 50))


        buttons = [
            Button(get_btn_pos("bottom right"), start_level_intro, "Start Level", size = settings.BUTTON_SIZE["170x60"]),
            Button(get_btn_pos("bottom left"), start_new_game, "Start new game", size = settings.BUTTON_SIZE["170x60"]),
            Button((get_btn_pos("bottom center")), lambda: start_level_intro(5), "Start level 5", size=settings.BUTTON_SIZE["170x60"]),
            upgrade_button(game.upgrades['wall_insulation'], (500, 345)),
            upgrade_button(game.upgrades['power'], (500, 395)),
            upgrade_button(game.upgrades['heatpump_efficiency'], (500, 445)),
            upgrade_button(game.upgrades['electricity_price_discount'], (500, 495)),
        ]
        [self.handler.register_button(button) for button in buttons]

        # bind key presses
        self.handler.bind_keypress(pg.K_RETURN, start_level_intro)
        self.handler.bind_keypress(pg.K_q, quit)
        # self.handler.bind_keypress(pg.K_ESCAPE, quit_game)

    @override
    def render(self) -> None:
        renderer.render_menu(game.get_menu_data())

        for button in self.handler.buttons:
            renderer.render_button(button)

        particle_manager.render()

        screen.blit(renderer.display, (0, 0))
        pg.display.update()


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
        self.handler.bind_keypress(pg.K_ESCAPE, start_shop_loop)

    @override
    def loop(self) -> None:
        """The level loop responsible for processing events, updating game state, and rendering."""
        running = True
        accumulated_gamehours = 0
        while running:
            running = self.handler.update()

            dt_real = clock.tick(60) / 1000.0  # Convert milliseconds to seconds
            accumulated_gamehours += dt_real * game.speed * (not game.paused)  # h/s
            #print(f"{game.hour=}, {accumulated_gamehours:1f}, {game.model.comfort_score_tsd[game._mh]}")

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
                game.update(hours=hours)
                
                if game.hour + accumulated_gamehours >= game.final_hour_of_the_year - 1:
                    level_success()

                if game.is_bankrupt(): 
                    game_over(reason="You spent all your money!")

                if game.is_too_hot():
                    level_fail(text="Everyone died of heat stroke!")

                if game.is_too_cold():
                    level_fail(text="Everyone froze into icicles!")

            renderer.set_background(get_background(game.hour))
            particle_manager.update()

            self.render()

            game.cleanup()

            if game.finished:
                running = False

    @override
    def render(self) -> None:
        renderer.camera.update()
        renderer.draw_background(game.hour)
        renderer.render_curves(game.get_curves_data(), game.paused)

        particle_manager.render()
        if game.get_temp_diff() > settings.TEMP_WARNING_THRESHOLD: renderer.draw_too_hot_warning()
        if game.get_temp_diff() <-settings.TEMP_WARNING_THRESHOLD: renderer.draw_too_cold_warning()
        if game.money < settings.MONEY_WARNING_THRESHOLD: renderer.draw_low_money_warning()

        renderer.render_ui(game.get_ui_data())

        if game.paused:
            renderer.draw_paused_overlay()

        if DEBUG_MODE: renderer.debug(self.debug)

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
        particle_manager.render()
        screen.blit(renderer.display, (0, 0))
        pg.display.update()

    @override
    def config_handler(self) -> None:
        self.handler.bind_keypress(pg.K_q, quit_game)
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
        self.buttons = Button(get_btn_pos("popup right"), start_shop_loop, "Start new Game!"),
        self.keys = [(pg.K_RETURN, start_shop_loop),(pg.K_ESCAPE, start_shop_loop),]
        super().__init__()

    @override
    def render(self) -> None:
        if random.random() < 0.5: 
            x = random.randint(0, settings.SCREEN_RESOLUTION[0])
            y = random.randint(0, settings.SCREEN_RESOLUTION[1])
            particle_manager.success(position=(x,y), velocity=(random.randint(-10,10), random.randint(-10,10)))

        renderer.render_popup(title=self.title, body=self.body, screen_params = center_screen(size = 0.8))
        for button in self.handler.buttons:
            renderer.render_button(button)
        
        #particle_manager.render(renderer)
        #renderer.draw_particles(particle_manager.groups["success"], color=(random.randint(100,255), random.randint(100,255), random.randint(100,255)))
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


"""Start"""

# start by entering title screen


start_new_game()


