
# Import required modules and classes
import pygame as pg
import random 
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
    while running:
        running = input_handler.update()
        if game.paused: continue

        game.update()

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
        
        d = {
            "anchorpoint": (600, 250),
            "first": {"QV" : game.model.QV[game.hour] * 5,
                      "QT" : game.model.QT[game.hour] * 5},
            "second": {"QS": game.model.QS[game.hour] * 5},
            "QH": game.model.QH[game.hour] * 5,
            "QC": game.model.QC[game.hour] * 5
        }
        renderer.draw_energybalance(d)
        
        renderer.draw_score(int(game.money))
        renderer.draw_label(f"Price: {game.model.price_grid} €/Wh", 
                            pos=(550,50),
                            color=(50,80,30))
        renderer.draw_label(f"Efficiency    {game.get_cop()*100:.0f}%",
                            pos=(550,80),
                            color=colors["QT"])
        renderer.draw_label(f"Heaitng Power {game.get_power()} W/m²", 
                         color=colors["QT"],
                         pos=(550,100))
        
        for button in input_handler.buttons:
            renderer.render_button(button)

        renderer.debug({"FPS": lambda: round(clock.get_fps(),1)})


        screen.blit(renderer.display, (0, 0))
        pg.display.update()
        clock.tick(60)
        
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
    particle_manager.heat(game.position, (game.dt/2, -0.1))
    
def cool():
    game.cool()
    particle_manager.cool(game.position, (game.dt/2, 0.1))

# Set up the camera with a zoom feature
camera = Camera2D(surface=display, 
                    game_world_position=game.position,
                    zoom=(2, 5))
camera.follow(game, maxdist = 100)

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
input_handler.bind_keypress(pg.K_1, lambda: game.set_speed(1))
input_handler.bind_keypress(pg.K_2, lambda: game.set_speed(2))
input_handler.bind_keypress(pg.K_3, lambda: game.set_speed(5))
input_handler.bind_keypress(pg.K_4, lambda: game.set_speed(10))
input_handler.bind_keypress(pg.K_5, lambda: game.set_speed(50))
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

