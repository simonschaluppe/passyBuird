
# Import required modules and classes
import pygame as pg
from camera import Camera2D
from model.GameModel import GameModel
from handler import Button, InputHandler
from renderer import Renderer, colors
from particles import ParticleManager

pg.init()
print(pg.version)
# Set up the main display surface
screen = pg.display.set_mode((800, 600))
pg.display.set_caption("passyBUIRLD")
# Create another surface to perform off-screen drawing
display = pg.Surface((800, 600))
clock = pg.time.Clock()

game = GameModel(dt=1, start_hour=6000)

def quit_game():
    print("Quitting game...")
    pg.quit()
    quit()

def main_loop(screen, game:GameModel, renderer:Renderer, input_handler:InputHandler, 
              clock:pg.time.Clock, particle_manager:ParticleManager):
    """The main game loop responsible for processing events, updating game state, and rendering."""
    running = True
    accumulated_gamehours = 0
    while running:
        
        running = input_handler.update()
        if game.paused: continue

        dt_real = clock.tick(60) / 1000.0  # Convert milliseconds to seconds
        accumulated_gamehours += dt_real * game.speed # h/s

        if accumulated_gamehours >= 1:
            game.dt = int(accumulated_gamehours)
            accumulated_gamehours -= game.dt
            game.update()

        particle_manager.update()
            
        #render
        renderer.camera.update()
        renderer.draw_background(game.hour)

        renderer.render_curves(game.get_curves_data())
        
        renderer.draw_heat_particles(particle_manager.groups["heating"])
        renderer.draw_cool_particles(particle_manager.groups["cooling"])

        renderer.render_ui(game.get_ui_data())
               
        for button in input_handler.buttons:
            renderer.render_button(button)

        fps = clock.get_fps()
        renderer.debug({"FPS": lambda: f"{fps:2.1f}", 
                        "Acc. hours": lambda: f"{accumulated_gamehours:.2f} h",
                        "State": game.__repr__,
                        "Speed": lambda: f"{game.speed:.0f} h/s"
                        })

        screen.blit(renderer.display, (0, 0))
        pg.display.update()
        
        game.cleanup()
        
        if game.finished: running = False

def menu_loop(screen, renderer:Renderer, menu_handler:InputHandler, clock):
    running = True
    while running:
        running = menu_handler.update()
               
        renderer.render_title(pos=(50, 50))
        renderer.render_building_menu(game.model.building.__repr__())
        
        renderer.render_hvac_menu(game.model.HVAC.__repr__())

        for button in menu_handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()
        clock.tick(60)

#new
particle_manager = ParticleManager()
def heat():
    game.heat()
    particle_manager.heat(game.position, (game.dt, -game.qh/game.model.building.heat_capacity*10))
    
def cool():
    game.cool()
    particle_manager.cool(game.position, (game.dt, -game.qc/game.model.building.heat_capacity*10))

# Set up the camera with a zoom feature
camera = Camera2D(surface=display, 
                    game_world_position=game.position,
                    zoom=(2, 5))
camera.follow(game, maxdist = 0)

renderer = Renderer(display, camera, clock)

menu_handler = InputHandler()
input_handler = InputHandler()
end_handler = InputHandler()

enter_menu = lambda: menu_loop(screen, renderer=renderer,menu_handler=menu_handler, clock=clock)
startgame = lambda: main_loop(
    screen=screen, 
    game=game, 
    renderer=renderer, 
    input_handler=input_handler, 
    clock=clock,
    particle_manager=particle_manager
    )

input_handler.bind_camera(camera)
input_handler.bind_continuous_keypress(pg.K_UP, heat)
input_handler.bind_continuous_keypress(pg.K_DOWN, cool)
input_handler.bind_keypress(pg.K_p, game.toggle_pause)
input_handler.bind_keypress(pg.K_1, lambda: game.set_speed(12))
input_handler.bind_keypress(pg.K_2, lambda: game.set_speed(24))
input_handler.bind_keypress(pg.K_3, lambda: game.set_speed(24*7))
input_handler.bind_keypress(pg.K_4, lambda: game.set_speed(24*7*2))
input_handler.bind_keypress(pg.K_5, lambda: game.set_speed(24*7*4))
input_handler.bind_keypress(pg.K_w, lambda: game.set_cop(0.5))
input_handler.bind_keypress(pg.K_s, lambda: game.set_cop(-0.5))
input_handler.bind_keypress(pg.K_q, quit_game)
input_handler.bind_keypress(pg.K_ESCAPE, enter_menu)


menu_handler.bind_keypress(pg.K_RETURN, startgame)
#menu_handler.bind_mousebutton(1, startgame)
menu_handler.bind_keypress(pg.K_q, quit)
menu_handler.bind_keypress(pg.K_ESCAPE, startgame)
start_button = Button((10, 200), startgame, "Start the Game!")
quit_button = Button((10, 250), quit_game, "Quit")
menu_handler.register_button(start_button)
menu_handler.register_button(quit_button)

enter_menu()

