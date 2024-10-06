# Import required modules and classes
import pygame as pg
from camera import Camera2D
from entities import Curve
from model.GameModel import GameModel
from handler import InputHandler
from ui import UI

# Optional profiling to check performance
PROFILE = False
if PROFILE:
    import cProfile

# Main function definition
def main() -> None:
    # Initialize the pygame module
    pg.init()
    print(pg.version)
    # Set up the main display surface
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption("passyBird")

    # Create another surface to perform off-screen drawing
    display = pg.Surface((800, 600))

    # Clock for managing frame rates
    clock = pg.time.Clock()
    # Initialize the game model
    game = GameModel(dt=1)

    # Create curves to visualize various game data
    temperature_curve = Curve()
    outdoor_temp_curve = Curve.from_points(game.model.TA, "blue")
    curve_comfort_min = Curve.from_points([game.model.comfort.minimum_room_temperature]*8760, "lightblue")
    curve_comfort_max = Curve.from_points([game.model.comfort.maximum_room_temperature]*8760, "orange")

    # Initialize UI elements
    ui = UI(anchorpoint=(100, screen.get_height()//2))
    ui.debug("Model", game.__repr__)
    ui.debug("FPS", clock.get_fps)

    # Set up the camera with a zoom feature
    camera = Camera2D(surface=display, 
                      game_world_position=game.position,
                      zoom=(1, 5))
    camera.follow(game, maxspeed=game.dt)

    # Configure input handling
    input_handler = InputHandler()
    input_handler.bind_continuous_keypress(pg.K_UP, game.heat)
    input_handler.bind_continuous_keypress(pg.K_DOWN, game.cool)

    # Game main loop
    running = True
    while running:
        # Handle game events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            input_handler.handle_event(event)
        input_handler.handle_continuous_keypresses()
        input_handler.handle_continuous_mousebuttons()

        # Update game logic and elements
        game.update()
        temperature_curve.update(game.position)
        ui.update(game)
        camera.update()

        # Draw elements onto the display surface
        display.fill((255, 255, 255))
        temperature_curve.draw(display, camera)
        outdoor_temp_curve.draw(display, camera)
        curve_comfort_min.draw(display, camera)
        curve_comfort_max.draw(display, camera)

        # Draw game-related graphics
        x, y = camera.screen_coords(game.position)
        pg.draw.circle(display, (255, 0, 0), (x, y), 10)
        pg.draw.line(display, (0, 0, 180), (x, y),
                     camera.screen_coords(pg.Vector2(*game.position) + (game.dt, game.dT)))
        pg.draw.rect(display, (255, 0, 0), pg.Rect(x-5, y-game.model.QH[game.hour], 10, y))
        pg.draw.rect(display, (0, 0, 255), pg.Rect(x-5, y, 10, -game.model.QC[game.hour]))

        # Render UI elements
        ui.draw(display)
        ui.draw_debug(display)

        # Display everything onto the main screen
        screen.blit(display, (0, 0))
        pg.display.update()

        # Manage the frame rate
        clock.tick(60)

# Entry point of the program
if __name__ == '__main__':
    if PROFILE:
        cProfile.run('main()', "profile.prof")
        import pstats
        p = pstats.Stats("profile.prof")
        p.sort_stats("cumulative").print_stats(20)
    main()
