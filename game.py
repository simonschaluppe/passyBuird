# Import required modules and classes
import pygame as pg
from camera import Camera2D
from model.GameModel import GameModel, create_game_model
from handler import Button, InputHandler
from renderer import Renderer
from particles import ParticleManager

pg.init()
print(pg.version)
# Set up the main display surface
screen = pg.display.set_mode((800, 600))
pg.display.set_caption("passyBUIRLD")
# Create another surface to perform off-screen drawing
display = pg.Surface((800, 600))
clock = pg.time.Clock()


def quit_game():
    print("Quitting game...")
    pg.quit()
    quit()


def main_loop(
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

        if game.hour + accumulated_gamehours >= game.final_hour_of_the_year - 1:
            # game.finished = True
            game.next_year()
            end_of_level_screen(screen, renderer, game, clock)
            enter_menu()

        if game.paused:
            continue

        if accumulated_gamehours >= 1:
            hours = int(accumulated_gamehours)
            accumulated_gamehours -= hours
            game.update(hours=hours)

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


def menu_loop(screen, renderer: Renderer, menu_handler: InputHandler, clock):
    running = True
    while running:
        running = menu_handler.update()

        renderer.render_menu(game.get_menu_data())

        for button in menu_handler.buttons:
            renderer.render_button(button)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()
        clock.tick(60)


def end_of_level_screen(screen, renderer: Renderer, game: GameModel, clock):
    """Displays end-of-level summary before returning to menu."""
    end_running = True
    end_handler = InputHandler()

    def continue_to_menu():
        nonlocal end_running
        end_running = False

    kpi_data = game.get_kpis()

    end_handler.bind_keypress(pg.K_RETURN, continue_to_menu)
    end_handler.bind_keypress(pg.K_ESCAPE, continue_to_menu)

    line_size = 24
    line_spacing = 30  # slightly more than size to avoid overlap
    y = 50

    while end_running:
        end_handler.update()
        renderer.display.fill((0, 0, 0))  # Clear background

        renderer.render_line(
            "End of Level Results:",
            pos=(100, y),
            size=32,
            color=(255, 255, 255),
            font=renderer.titlefont,
        )
        y += 50  # Larger space after title

        for label, value in kpi_data.items():
            renderer.render_line(
                f"{label}: {value}",
                pos=(120, y),
                size=line_size,
                color=(200, 200, 200),
            )
            y += line_spacing

        screen.blit(renderer.display, (0, 0))


game = create_game_model()

particle_manager = ParticleManager()


def heat():
    game.heat()
    particle_manager.heat(
        game.position, (0, -game.qh / game.model.building.heat_capacity * 10)
    )


def cool():
    game.cool()
    particle_manager.cool(
        game.position, (0, -game.qc / game.model.building.heat_capacity * 10)
    )


# Set up the camera with a zoom feature
camera = Camera2D(surface=display, game_world_position=game.position, zoom=(2, 5))
camera.follow(game, maxdist=0)

renderer = Renderer(display, camera, clock)

menu_handler = InputHandler()
input_handler = InputHandler()
end_handler = InputHandler()

enter_menu = lambda: menu_loop(
    screen, renderer=renderer, menu_handler=menu_handler, clock=clock
)
startgame = lambda: main_loop(
    screen=screen,
    game=game,
    renderer=renderer,
    input_handler=input_handler,
    clock=clock,
    particle_manager=particle_manager,
)

input_handler.bind_camera(camera)
input_handler.bind_continuous_keypress(pg.K_UP, heat)
input_handler.bind_continuous_keypress(pg.K_DOWN, cool)
input_handler.bind_continuous_mousebutton(0, heat)
input_handler.bind_continuous_mousebutton(2, cool)
input_handler.bind_keypress(pg.K_p, game.toggle_pause)
input_handler.bind_keypress(pg.K_1, lambda: game.set_speed(12))
input_handler.bind_keypress(pg.K_2, lambda: game.set_speed(24))
input_handler.bind_keypress(pg.K_3, lambda: game.set_speed(24 * 7))
input_handler.bind_keypress(pg.K_4, lambda: game.set_speed(24 * 7 * 2))
input_handler.bind_keypress(pg.K_5, lambda: game.set_speed(24 * 7 * 4))
input_handler.bind_keypress(pg.K_w, lambda: game.increment_cop(0.5))
input_handler.bind_keypress(pg.K_s, lambda: game.increment_cop(-0.5))
input_handler.bind_keypress(pg.K_q, quit_game)
input_handler.bind_keypress(pg.K_ESCAPE, enter_menu)


menu_handler.bind_keypress(pg.K_RETURN, startgame)
# menu_handler.bind_mousebutton(1, startgame)
menu_handler.bind_keypress(pg.K_q, quit)
menu_handler.bind_keypress(pg.K_ESCAPE, startgame)
start_button = Button((600, 480), startgame, "Start the Game!")
quit_button = Button((600, 530), quit_game, "Quit")
menu_handler.register_button(start_button)
menu_handler.register_button(quit_button)

enter_menu()
