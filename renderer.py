import sys
import pygame as pg
import math
from pathlib import Path

from camera import Camera2D
from font import Font
from handler import Button  # necessary?
from utils import color_interpolation, seasonalcolor, circle_surf, change_color

ROOT_PATH = Path(__file__).parent
sys.path.append(ROOT_PATH)

DATA_PATH = ROOT_PATH / "data"
FONT_PATH = ROOT_PATH / "assets" / "fonts"
IMAGE_PATH = ROOT_PATH / "assets" / "images"

colors = {
    "QV": (200, 0, 100),
    "QT": (76, 37, 29),
    "QS": (200, 200, 0),
    "QH": (255, 0, 0),
    "QC": (0, 0, 255),
    "Title": (100, 30, 0),
    "DEBUG": (40, 64, 123),
    "Winter BG": (60, 84, 153),  # (61, 98, 116),
    "Summer BG": (255, 232, 197),
    "Button hovered": (61, 98, 116),
    "Button": (51, 58, 96),
    "Price": (50, 80, 30),
    "UI Text": (76, 37, 29),
    "Upgrade text": (153, 64, 154),
    "Emission text": (66, 62, 56),
    "Emissions": (105, 95, 78),
}

# Define color constants
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ALMOSTBLACK = (10, 10, 10)
GREEN = (0, 255, 0)


def color_indicator(dT):
    if dT > 0:
        return RED
    elif dT < 0:
        return BLUE
    else:
        return GREEN


class Renderer:
    def __init__(
        self, display: pg.Surface, camera: Camera2D, clock: pg.time.Clock, scale=1.0
    ):
        self.display = display
        self.cx, self.cy = display.get_width() // 2, display.get_height() // 2
        self.camera = camera
        self.clock = clock
        self.scale = scale

        # defaults
        self.lineheight = 25
        self.font = Font(FONT_PATH / "small_font.png")
        self.titlefont = Font(FONT_PATH / "large_font.png")

        # components
        self.ui_renderer = UIRenderer(self)
        self.curves_renderer = CurvesRenderer(self)
        self.menu_renderer = MenuRenderer(self)

    # debug stuff, should be low level
    def debug(self, statements):
        # Render debug statements
        for i, (label, callback) in enumerate(statements.items()):
            debug_text = f"{label}: {callback()}"
            self.render_line(
                debug_text, colors["DEBUG"], (10, 10 + i * self.lineheight)
            )

    # basic rendering
    def outline(self, surf, loc, pixel, color=(10, 10, 10), onto=False):
        if not onto:
            onto = self.display
        mask = pg.mask.from_surface(surf)
        mask_surf = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0))
        mask_surf.set_colorkey((0, 0, 0))
        x, y = loc
        onto.blit(mask_surf, (x - pixel, y))
        onto.blit(mask_surf, (x + pixel, y))
        onto.blit(mask_surf, (x, y - pixel))
        onto.blit(mask_surf, (x, y + pixel))
        onto.blit(mask_surf, (x - pixel, y - pixel))
        onto.blit(mask_surf, (x + pixel, y + pixel))
        onto.blit(mask_surf, (x + pixel, y - pixel))
        onto.blit(mask_surf, (x - pixel, y + pixel))

    def render_line(
        self,
        text: str,
        color=ALMOSTBLACK,
        pos=(0, 0),
        size=20,
        border_width=2,
        border_color=WHITE,
        font=None,
        onto=None,
    ):
        """Render a single text line onto a surface."""
        if not font:
            font = self.font
        if not onto:
            onto = self.display
        px, py = pos
        textsurf = font.surface(text, size, color)
        self.outline(textsurf, (px, py), border_width, border_color, onto=onto)
        font.render(onto, text, (px, py), size, color)

    def render_lines(
        self,
        text: str,
        color=ALMOSTBLACK,
        pos=(0, 0),
        size=20,
        font=None,
        onto=None,
        lineheight=None,
    ):
        px, py = pos
        dy = 0
        for line in text.splitlines():
            dy += lineheight if lineheight else self.lineheight
            self.render_line(line, color, (px, py + dy), size, font=font, onto=onto)

    def draw_grid(self, spacing, color=BLACK):
        for x in range(0, self.display.get_width(), spacing):
            pg.draw.line(self.display, color, (x, 0), (x, self.display.get_height()))
        for y in range(0, self.display.get_height(), spacing):
            pg.draw.line(self.display, color, (0, y), (self.display.get_width(), y))

    # button
    def render_button(self, button: Button):
        button_surf = pg.Surface(button.size)
        button_surf.fill(
            colors["Button hovered"] if button.hovered else colors["Button"]
        )
        # outline
        self.outline(
            button_surf, button.position, pixel=1 + button.hovered - button.pressed
        )
        # text
        offset = 5 + 2 * button.pressed
        self.render_line(
            button.text,
            pos=(5, offset),
            onto=button_surf,
            size=20,
            border_width=1 + button.hovered,
        )
        # button
        self.display.blit(button_surf, button.position)

    # main game loop
    def draw_background(self, hour_of_year):
        # self.display.fill((0,0,0))
        self.display.fill(seasonalcolor(hour_of_year))

    # draw stuff using camera (game)
    def render_curves(self, curve_data):
        self.curves_renderer.render(curve_data)

    # particle renderer
    def draw_particles(self, particleList, color):
        for p in particleList:
            pos = self.camera.screen_coords(p.pos)
            x, y = pos
            pg.draw.circle(self.display, color, pos, p.lifetime / 8)
            glow_color = color_interpolation((0, 0, 0), color, 0.2)
            radius = p.lifetime / 3
            self.display.blit(
                circle_surf(radius, glow_color),
                (x - radius, y - radius),
                special_flags=pg.BLEND_RGB_ADD,
            )

    def draw_heat_particles(self, particleList):
        self.draw_particles(particleList, colors["QH"])

    def draw_cool_particles(self, particleList):
        self.draw_particles(particleList, colors["QC"])

    # main game UI
    def render_ui(self, ui_data):
        self.ui_renderer.render(ui_data)

    # menu screen
    def render_menu(self, data):
        self.menu_renderer.render(data)

    def render_popup(self, title:str, body:list):
        line_size = 24
        line_spacing = 30  # slightly more than size to avoid overlap

        self.menu_renderer.render_background()
        panel_rect = pg.Rect(80, 30, 640, 640)
        pg.draw.rect(
            self.display,
            (30, 30, 30),   # fill color
            panel_rect,
            border_radius=8
        )
        pg.draw.rect(
            self.display,
            (220, 220, 220),  # border color
            panel_rect,
            width=2,
            border_radius=8
        )
   
        self.render_line(
            title,
            pos=(120, 80),
            size=50,
            font=self.titlefont,
        )
        y = 150  # Larger space after title

        for line in body:
            self.render_line(
                line,
                pos=(120, y),
                size=line_size,
            )
            y += line_spacing

class MenuRenderer:
    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer
        self.display = renderer.display
        self.render_line = renderer.render_line
        self.render_lines = renderer.render_lines

        self.topleft = (40, 40)  # corner anchor
        self.tile_size = (100, 100)  # Size for each upgrade tile

        self.stats_text_color = ALMOSTBLACK

        # Load the background image for the upgrade menu
        bg_image = pg.image.load(IMAGE_PATH / "bg_house.png").convert()
        self.menu_background = pg.transform.scale(bg_image, self.display.get_size())

    def render(self, data):
        """Render the upgrade menu including background, tiles, and costs."""
        # Draw the menu background first
        self.render_background()

        # self.renderer.draw_grid(100)

        self.render_hull_stats(
            data["hull"], pos=(self.topleft[0], 200), color=self.stats_text_color
        )

        self.render_hvac_stats(
            data["hvac"], (self.topleft[0], 400), self.stats_text_color
        )

        # Render upgrade tiles and costs
        self.render_upgrade_tiles(data["upgrades"], pos=(600, 100))
        self.render_player_stats(data["player"], pos=(600, 50))

        self.render_title(self.topleft)

    def render_background(self):
        self.display.blit(self.menu_background, (0, 0))

    def render_title(self, pos):
        title = "PassyBUIRD"
        self.render_line(
            title, colors["Title"], pos, font=self.renderer.titlefont, size=50
        )

    def render_upgrade_tiles(self, upgrades, pos):
        """Render upgrade tiles on the screen."""
        start_x, start_y = pos  # Starting position for the grid of tiles
        padding = 10  # Space between tiles

        for idx, upgrade in enumerate(upgrades):
            x = start_x + (idx // 3) * (self.tile_size[0] + padding)
            y = start_y + (idx % 3) * (self.tile_size[1] + padding)

            # Render the upgrade tile
            self.render_upgrade_tile(upgrade, (x, y))

    def render_upgrade_tile(self, upgrade: dict, pos):
        """Render a single upgrade tile with its cost and state."""
        tile_surf = pg.Surface(self.tile_size)

        # Render the tile image
        tile_image = pg.image.load(IMAGE_PATH / upgrade["image"]).convert_alpha()
        tile_image = pg.transform.scale(tile_image, size=self.tile_size)

        if not upgrade["available"]:
            grey_surf = pg.Surface(self.tile_size)
            grey_surf.fill((150, 150, 150, 100))
            grey_surf.blit(tile_image, (0, 0))

        tile_surf.blit(tile_image, (0, 0))
        tile_surf.set_colorkey((0, 0, 0))

        self.render_line(
            f"{upgrade['name']}",
            pos=(10, 10),
            color=colors["Upgrade text"],
            size=20,
            onto=tile_surf,
        )
        # Draw the cost below the tile
        self.render_line(
            f"€{upgrade['cost']}",
            pos=(10, 45),
            color=colors["Upgrade text"],
            size=20,
            onto=tile_surf,
        )

        # Blit the tile to the display
        self.display.blit(tile_surf, pos)

    def render_player_stats(self, player_data, pos):
        """Render player stats such as available money."""
        self.render_line(
            f"€{player_data['money']}",
            color=GREEN,
            pos=pos,
            size=40,
        )

    def render_hvac_stats(
        self,
        data,
        pos,
        color,
    ):
        self.render_lines(data["lines"], color=color, pos=pos)

    def render_hull_stats(self, data, pos, color):
        self.render_lines(data["lines"], color=color, pos=pos)


class CurvesRenderer:
    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer
        self.screen_coords = renderer.camera.screen_coords
        self.curve_width = 2
        self.size_TI_indicator = 10

        # Load the house image for the indicator
        house = pg.image.load(IMAGE_PATH / "glide.png").convert()
        house.set_colorkey((255, 255, 0))
        self.house = pg.transform.scale(house, (40, 40))

    def render(self, data):
        self.draw_curve("orange", data["Maximum Comfort Temperature"])
        self.draw_curve("lightblue", data["Minimum Comfort Temperature"])
        self.draw_curve("red", data["Indoor Temperature"])
        self.draw_curve("blue", data["Outdoor Temperature"])
        self.draw_curve(colors["Emissions"], data["Carbon Intensity"])
        self.draw_house_indicator(data["TI Indicator"])
        self.draw_TA_indicator(data["TA Indicator"])

    # curve renderer
    def draw_curve(self, color, curve):
        """Draw curves representing game data."""
        if len(curve) < 2:
            return
        screencoords = [self.screen_coords(point) for point in curve]  # Only last 300 points
        pg.draw.lines(
            self.renderer.display,
            color,
            closed=False,
            points=screencoords,
            width=self.curve_width,
        )

    def draw_house_indicator(self, data):
        """Draw game objects like players or enemies."""
        x, y = self.screen_coords(data["Position"])
        color = color_indicator(data["Comfort dT"])
        size = self.size_TI_indicator * data["Scale"]
        pg.draw.circle(self.renderer.display, color, (x, y), size)

        self.renderer.outline(self.house, (x - 15, y - 15), 2)
        self.renderer.display.blit(self.house, (x - 15, y - 15))

    def draw_indicator(self, gamepos1, gamepos2, color):
        screenpos1 = self.screen_coords(gamepos1)
        screenpos2 = self.screen_coords(gamepos2)
        pg.draw.line(self.renderer.display, color, screenpos1, screenpos2)

    def draw_TA_indicator(self, data):
        hour, TA = data["TA"]
        TA_pos = self.screen_coords((hour, TA))
        textcolor = seasonalcolor(hour)
        bordercolor = color_interpolation(textcolor, (255, 255, 255), 0.8)
        textcolor = color_interpolation(textcolor, (0, 0, 0), 0.5)
        self.draw_indicator((hour, TA), data["TI"], "blue")
        text = f"Outdoor Temp {TA:+2.1f}°C"
        self.renderer.render_line(
            text,
            textcolor,
            pos=self.screen_coords((hour - 100, TA)),
            border_color=bordercolor,
        )


class UIRenderer:
    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer
        self.display = renderer.display
        self.render_line = renderer.render_line

    def render(self, ui_data):
        self.energybalance(ui_data["Energy balance"])
        self.money(ui_data["Scores"]["Money"])

        comfort_data = ui_data["Scores"]["Comfort"]
        self.render_comfort_score(score=comfort_data["score"], dT=comfort_data["dT"])

        self.render_line(ui_data["Price"], pos=(550, 80), color=colors["Price"])
        self.render_line(ui_data["CO2"], pos=(550, 100), color=colors["Emission text"])
        self.render_line(ui_data["COP"], pos=(550, 120), color=colors["UI Text"])
        self.render_line(ui_data["Power"], pos=(550, 140), color=colors["UI Text"])

    def energybalance(self, balance_data):
        """Render energy balance as waterfall diagram."""
        anchor_x, anchor_y = 600, self.renderer.cy
        first = balance_data["first"]
        second = balance_data["second"]
        QH = balance_data["QH"]
        QC = balance_data["QC"]

        width = 10
        # Draw anchor point line (reference point)
        pg.draw.rect(
            self.display, WHITE, pg.Rect(anchor_x, anchor_y, 120, 2)
        )  # White anchor line

        # Initial position is the anchor point
        current_y = anchor_y

        # Render the first set of bars (positive values go down)
        for i, (label, value) in enumerate(first.items()):
            pg.draw.rect(
                self.display,
                colors[label],
                pg.Rect(anchor_x + 3 * width, current_y, width, abs(value)),
            )  # Draw the bar
            self.renderer.render_line(
                f"{label}: {value:+.1f} W/m²",
                colors[label],
                (anchor_x + 8 * width, anchor_y + i * self.renderer.lineheight),
            )  # Label
            current_y -= value  # Move down

        # Render the second set of bars (negative values go up)
        for label, value in second.items():
            pg.draw.rect(
                self.display,
                colors[label],
                pg.Rect(anchor_x + 4 * width, current_y - value, width, value),
            )  # Draw bar
            if value != 0.0:
                self.renderer.render_line(
                    f"{label}: {value:+.1f} W/m²",
                    colors[label],
                    (anchor_x + 8 * width, anchor_y - self.renderer.lineheight),
                )  # Label
            current_y -= value  # Move up

        # Render QH and QC bars relative to anchor point
        # QH (positive, down)
        pg.draw.rect(
            self.display, colors["QH"], pg.Rect(anchor_x + 50, current_y - QH, 10, QH)
        )
        if QH != 0:
            self.renderer.render_line(
                f"QH: {QH:+.1f} W/m²",
                colors["QH"],
                (anchor_x + 8 * width, anchor_y + 2 * self.renderer.lineheight),
            )  # Label

        # QC (negative, up)
        pg.draw.rect(
            self.display, colors["QC"], pg.Rect(anchor_x + 50, current_y, 10, -QC)
        )
        if QC != 0:
            self.renderer.render_line(
                f"QC: {QC:+.1f} W/m²",
                colors["QC"],
                (anchor_x + 8 * width, anchor_y + 2 * self.renderer.lineheight),
            )  # Label

    def money(self, money, pos=(650, 10)):
        self.render_line(
            str(money),
            color=(100, 255, 120),
            size=40,
            pos=pos,
            font=self.renderer.titlefont,
        )

    def render_comfort_score(self, score, dT, pos=(550, 50)):
        text = f"Comfort {score:.1f} %"
        color = color_indicator(dT)
        color = color_interpolation(color, GREEN, score / 100)
        self.render_line(text, color, pos=pos, size=30)


# test code
def test():
    import pygame as pg
    from pygame.math import Vector2  # For handling positions
    import random
    from camera import Camera2D  # Assuming you have a simple Camera2D implementation
    from font import Font  # Your Font class for text rendering
    from renderer import Renderer  # The Renderer class
    from particles import Particle

    # A basic mock for UI, simulating the data that UI would pass to the Renderer
    mock_ui_data = {
        "anchorpoint": (100, 500),
        "first": {"QV": 150, "QT": 120},
        "second": {"QS": 60},
        "QH": 100,
        "QC": 50,
        "debug_statements": {"FPS": lambda: 60},
    }

    pg.init()

    # Set up the Pygame window
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()

    # Initialize mock camera and renderer
    camera = Camera2D(screen, zoom=(1, 1))
    renderer = Renderer(screen, camera, clock)

    # Mock particle lists for heat and cool particles
    heat_particles = [
        Particle(
            Vector2(random.randint(100, 700), random.randint(100, 500)),
            Vector2(random.uniform(-1, 1), random.uniform(-1, 1)),
            50,
        )
        for _ in range(10)
    ]

    cool_particles = [
        Particle(
            Vector2(random.randint(100, 700), random.randint(100, 500)),
            Vector2(random.uniform(-1, 1), random.uniform(-1, 1)),
            50,
        )
        for _ in range(10)
    ]

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # Fill the screen with a background color
        renderer.draw_background(6000)  # Example hour of year

        # Draw particles (testing draw_heat_particles and draw_cool_particles)
        renderer.draw_heat_particles(heat_particles)
        renderer.draw_cool_particles(cool_particles)

        # Draw UI (testing draw_ui)
        renderer.draw_energybalance(mock_ui_data)

        # Update the screen
        pg.display.flip()
        clock.tick(60)  # Cap the frame rate at 60 FPS

    pg.quit()


if __name__ == "__main__":
    test()
