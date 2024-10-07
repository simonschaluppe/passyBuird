
# Import required modules and classes
import pygame as pg
import random 
from camera import Camera2D
from model.GameModel import GameModel
from handler import InputHandler
from renderer import Renderer
from particles import Particle, ParticleManager
from ui import UI


pg.init()
print(pg.version)
# Set up the main display surface
screen = pg.display.set_mode((800, 600))
pg.display.set_caption("passyBUIRLD")
# Create another surface to perform off-screen drawing
display = pg.Surface((800, 600))
clock = pg.time.Clock()

game = GameModel(dt=1, start_hour=6000)

def main_loop(screen, game:GameModel, renderer:Renderer, input_handler:InputHandler, 
              clock:pg.time.Clock, ui:UI, particle_manager:ParticleManager):
    """The main game loop responsible for processing events, updating game state, and rendering."""
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            input_handler.handle_event(event)
        input_handler.handle_continuous_keypresses()
        input_handler.handle_continuous_mousebuttons()

        if game.paused: continue

        game.update()
        
        ui.update(game)
        particle_manager.update()
            
        #render
        renderer.camera.update()
        renderer.draw_background(game.hour)

        for curve in game.curves.values():
            renderer.draw_curve(curve)
            
        renderer.draw_indoor_temperature(pos=game.position, dT=game.comfort_diff,
                                         size=(10 + (game.heat_on + game.cool_on)*5))

        renderer.draw_heat_particles(particle_manager.groups["heating"])
        renderer.draw_cool_particles(particle_manager.groups["cooling"])
        
        renderer.draw_ui(ui.get_ui_elements())
        renderer.draw_stats(
            game.get_insulation(),
            game.get_power(),
            game.get_cop())

        screen.blit(renderer.display, (0, 0))
        pg.display.update()
        clock.tick(60)
        
        game.cleanup()
        
        if game.finished: running = False

def menu_loop(screen, renderer:Renderer, input_handler:InputHandler, clock):
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            input_handler.handle_event(event)
        input_handler.handle_continuous_keypresses()
        input_handler.handle_continuous_mousebuttons()
       
        renderer.render_title()
        renderer.render_building_menu(game.model.building.__repr__())
        
        renderer.render_hvac_menu(game.model.HVAC.__repr__())


        screen.blit(renderer.display, (0, 0))
        pg.display.update()
        clock.tick(60)

#new
particle_manager = ParticleManager()
def heat():
    game.heat()
    particle_manager.heat(game.position, (game.dt/2, -0.1))
    
def cool():
    game.cool()
    particle_manager.cool(game.position, (game.dt/2, 0.1))

ui = UI(anchorpoint=(100, screen.get_height()//2))
# Set up the camera with a zoom feature
camera = Camera2D(surface=display, 
                    game_world_position=game.position,
                    zoom=(1, 5))
camera.follow(game, maxdist = 100)

ui.debug("FPS", clock.get_fps)

renderer = Renderer(display, camera, ui)


menu_handler = InputHandler()
input_handler = InputHandler()
end_handler = InputHandler()

enter_menu = lambda: menu_loop(screen, renderer=renderer,input_handler=menu_handler, clock=clock)
startgame = lambda: main_loop(
    screen=screen, 
    game=game, 
    renderer=renderer, 
    input_handler=input_handler, 
    clock=clock, 
    ui=ui,
    particle_manager=particle_manager
    )

input_handler.bind_camera(camera)
input_handler.bind_continuous_keypress(pg.K_UP, heat)
input_handler.bind_continuous_keypress(pg.K_DOWN, cool)
input_handler.bind_keypress(pg.K_p, game.toggle_pause)
input_handler.bind_keypress(pg.K_1, lambda: game.set_speed(1))
input_handler.bind_keypress(pg.K_2, lambda: game.set_speed(2))
input_handler.bind_keypress(pg.K_3, lambda: game.set_speed(5))
input_handler.bind_keypress(pg.K_4, lambda: game.set_speed(10))
input_handler.bind_keypress(pg.K_5, lambda: game.set_speed(50))
input_handler.bind_keypress(pg.K_q, quit)
input_handler.bind_keypress(pg.K_ESCAPE, enter_menu)


menu_handler.bind_keypress(pg.K_RETURN, startgame)
menu_handler.bind_mousebutton(1, startgame)
menu_handler.bind_keypress(pg.K_q, quit)
menu_handler.bind_keypress(pg.K_ESCAPE, startgame)

enter_menu()

