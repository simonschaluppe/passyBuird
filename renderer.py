import pygame as pg
import math
from camera import Camera2D
from font import Font
from handler import Button

from utils import color_interpolation, seasonalcolor, circle_surf, change_color

colors = {
    "QV": (200, 0, 100),
    "QT": (76, 37, 29),
    "QS": (200, 200, 0),
    "QH": (255, 0, 0),
    "QC": (0, 0, 255),
    "Title": (100,30,0),
    "DEBUG": (40, 64, 123),
    "Winter BG": (60, 84, 153), #(61, 98, 116),
    "Summer BG": (255, 232, 197),
    "Button hovered": (61, 98, 116),
    "Button": (51, 58, 96),
}

# Define color constants
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ALMOSTBLACK = (10,10,10)
GREEN = (0, 255, 0)

def color_indicator(dT):
    if dT > 0:
        return RED
    elif dT < 0:
        return BLUE
    else:
        return GREEN

class Renderer:
    def __init__(self, display:pg.Surface, camera:Camera2D, clock:pg.time.Clock, scale=1.0):
        self.display = display
        self.cx, self.cy = display.get_width()//2, display.get_height()//2
        self.camera = camera
        self.clock = clock
        self.scale = scale

        #defaults
        self.lineheight = 25
        self.font = Font('assets/fonts/small_font.png')
        self.titlefont = Font('assets/fonts/large_font.png')

    def outline(self, surf, loc, pixel, color=(10,10,10), onto=False):
        if not onto: onto = self.display
        mask = pg.mask.from_surface(surf)
        mask_surf = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0))
        mask_surf.set_colorkey((0,0,0))
        x,y = loc
        onto.blit(mask_surf, (x-pixel, y))
        onto.blit(mask_surf, (x+pixel, y))
        onto.blit(mask_surf, (x, y-pixel))
        onto.blit(mask_surf, (x, y+pixel))
        onto.blit(mask_surf, (x-pixel, y-pixel))
        onto.blit(mask_surf, (x+pixel, y+pixel))
        onto.blit(mask_surf, (x+pixel, y-pixel))
        onto.blit(mask_surf, (x-pixel, y+pixel))

    def render_line(self, text:str, color=ALMOSTBLACK, pos=(0,0), size=20, border_width=2, border_color=WHITE, font=None, onto=None):
        """Render a single text line onto a surface."""
        if not font: font = self.font
        if not onto: onto = self.display
        px, py = pos
        textsurf = font.surface(text, size, color)
        self.outline(textsurf, (px, py), border_width, border_color, onto=onto)
        font.render(onto, text, (px, py), size, color)

    def render_lines(self, text:str, color=ALMOSTBLACK, pos=(0,0), size=20, font=None, onto=None):
        px, py = pos
        dy = 0
        for line in text.splitlines():
            dy += self.lineheight
            self.render_line(line, color, (px, py+dy), size, font=font, onto=onto)

    def render_button(self, button:Button):
        button_surf = pg.Surface(button.size)
        button_surf.fill(colors["Button hovered"] if button.hovered else colors["Button"])
        # outline
        self.outline(button_surf, button.position, pixel=1+button.hovered-button.pressed)
        # text
        offset = 5+2*button.pressed
        self.render_line(button.text, pos=(5, offset), onto=button_surf, size=20, border_width=1+button.hovered)
        # button
        self.display.blit(button_surf, button.position)

    def render_title(self, pos):
        self.display.fill(seasonalcolor(0))
        title = """PassyBUIRLD

+++press Enter to start+++"""
        self.render_lines(title, colors["Title"], pos, 
                         font=self.titlefont, size=40)  # Label

    def draw_label(self, text, pos=(0,0), color=ALMOSTBLACK, onto=None):
        self.render_line(text, color=color, pos=pos, onto=onto)

    def render_panel(self, lines, color, pos, size):
        box = pg.Surface(size)
        box.fill(color)
        self.render_lines(lines, onto=box, pos=(10,10))
        self.display.blit(box, pos)
    
    def render_hvac_menu(self, lines, color=WHITE):
        self.render_panel(lines, color=color, pos=(450,100), size=(300,100))

    def render_building_menu(self, lines, color=WHITE):
        self.render_panel(lines, color=color, pos=(450,300), size=(300,250))

    def draw_background(self, hour_of_year):
        #self.display.fill((0,0,0))
        self.display.fill(seasonalcolor(hour_of_year))

    def draw_particles(self, particleList, color):
        for p in particleList:
            pos = self.camera.screen_coords(p.pos)
            x,y = pos
            pg.draw.circle(self.display, color, pos, p.lifetime/8)
            glow_color = color_interpolation((0,0,0), color, 0.2)
            radius = p.lifetime/3
            self.display.blit(circle_surf(radius,glow_color), (x-radius, y-radius), special_flags=pg.BLEND_RGB_ADD)

    def draw_heat_particles(self, particleList):
        self.draw_particles(particleList, colors["QH"])   

    def draw_cool_particles(self, particleList):
        self.draw_particles(particleList, colors["QC"])


    def draw_stats(self, Lt, PH, coph):
        x, y = 10, 100

        self.draw_label(f"Leitwert {Lt:.2f} W/m2K", 
                         color=colors["QT"],
                         pos=(x,y))
        
        self.draw_label(text=f"Heatpump Power {PH} W/m2", 
                         color=colors["QT"],
                         pos=(x,y+self.lineheight))
        
    def draw_energybalance(self, balance_data):
        """Render energy balance as waterfall diagram."""
        anchor_x, anchor_y = balance_data["anchorpoint"]
        first = balance_data["first"]
        second = balance_data["second"]
        QH = balance_data["QH"]
        QC = balance_data["QC"]
        
        width = 10
        # Draw anchor point line (reference point)
        pg.draw.rect(self.display, WHITE, pg.Rect(anchor_x, anchor_y, 120, 2))  # White anchor line

        # Initial position is the anchor point
        current_y = anchor_y

        # Render the first set of bars (positive values go down)
        for i, (label, value) in enumerate(first.items()):
            pg.draw.rect(self.display, colors[label], pg.Rect(anchor_x + 3*width, current_y, width, abs(value)))  # Draw the bar
            self.render_line(f"{label}: {value:.1f} W/m²", colors[label], (anchor_x + 8*width, anchor_y+i*self.lineheight))  # Label
            current_y -= value  # Move down

        # Render the second set of bars (negative values go up)
        for label, value in second.items():
            pg.draw.rect(self.display, colors[label], pg.Rect(anchor_x + 4*width, current_y - value, width, value))  # Draw bar
            if value != 0.: 
                self.render_line(f"{label}: {value:.1f} W/m²", colors[label], (anchor_x + 8*width, anchor_y-self.lineheight))  # Label
            current_y -= value  # Move up

        # Render QH and QC bars relative to anchor point
        # QH (positive, down)
        pg.draw.rect(self.display, colors["QH"], pg.Rect(anchor_x + 50, current_y-QH, 10, QH))
        if QH != 0:
            self.render_line(f"QH: {QH:.1f} W/m²", colors["QH"], (anchor_x + 8*width, anchor_y+2*self.lineheight))  # Label
            
        # QC (negative, up)
        pg.draw.rect(self.display, colors["QC"], pg.Rect(anchor_x + 50, current_y, 10, -QC))
        if QC != 0:
            self.render_line(f"QC: {QC:.1f} W/m²", colors["QC"], (anchor_x + 8*width, anchor_y+2*self.lineheight))  # Label

    def draw_curve(self, curve):
        """Draw curves representing game data."""
        if len(curve.coordinates) < 2: return
        screencoords = [self.camera.screen_coords(coord) for coord in curve.coordinates[-300:]]  # Only last 300 points
    
        pg.draw.lines(self.display, curve.color, closed=False, points=screencoords, width=3)

    def draw_indoor_temperature(self, pos, dT, size):
        """Draw game objects like players or enemies."""
        x, y = self.camera.screen_coords(pos)

        color = color_indicator(dT)

        pg.draw.circle(self.display, color, (x, y), size)

    def draw_score(self, score, pos=(650,10)):
        self.render_line(str(score), color=(100,255,120), size=40, pos=pos, font=self.titlefont, )

    def draw_comfort_indicator(self, dT):
        comfort_score = max(100-20*abs(dT),0)
        text = f"Comfort {comfort_score:.1f} %"
        color = color_indicator(dT)
        color = color_interpolation(color, GREEN, comfort_score/100)
        self.render_line(text, color, pos=(550,120), size=20)

    def draw_TA_indicator(self, TA, hour, y=10):
        textcolor = seasonalcolor(hour)
        bordercolor = color_interpolation(textcolor, (255, 255,255),0.8)
        textcolor = color_interpolation(textcolor, (0,0,0), 0.5)
        text = f"Outdoor Temp {TA:2.1f}°C"
        self.render_line(text, textcolor, 
                         pos=self.camera.screen_coords((hour, y)), 
                         border_color=bordercolor
                         )

    def debug(self, statements):
        # Render debug statements
        for i, (label, callback) in enumerate(statements.items()):
            debug_text = f"{label}: {callback()}"
            self.render_line(debug_text, colors["DEBUG"], (10, 10 + i*self.lineheight))

 
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
        "debug_statements": {"FPS": lambda: 60}
    }

    pg.init()

    # Set up the Pygame window
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    
    # Initialize mock camera and renderer
    camera = Camera2D(screen, zoom=(1,1))
    renderer = Renderer(screen, camera, clock)

    # Mock particle lists for heat and cool particles
    heat_particles = [Particle(Vector2(random.randint(100, 700), random.randint(100, 500)),
                               Vector2(random.uniform(-1, 1), random.uniform(-1, 1)), 50) for _ in range(10)]
    
    cool_particles = [Particle(Vector2(random.randint(100, 700), random.randint(100, 500)),
                               Vector2(random.uniform(-1, 1), random.uniform(-1, 1)), 50) for _ in range(10)]

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

        # Draw some mock stats (testing draw_stats)
        mock_game_data = {
            "Lt": 0.5,
            "PH": 20,
            "coph": 4.3
        }
        renderer.draw_stats(**mock_game_data)

        # Draw UI (testing draw_ui)
        renderer.draw_energybalance(mock_ui_data)

        # Update the screen
        pg.display.flip()
        clock.tick(60)  # Cap the frame rate at 60 FPS

    pg.quit()

if __name__ == "__main__":
    test()