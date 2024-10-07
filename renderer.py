import pygame as pg
import math
from font import Font

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
}


# Define color constants
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ALMOSTBLACK = (10,10,10)
GREEN = (0, 255, 0)

def color_interpolation(color1, color2, weight):
    colorvector1 = pg.Vector3(color1)
    colorvector2 = pg.Vector3(color2)
    dist = colorvector1.distance_to(colorvector2)
    return tuple(colorvector1.move_towards(colorvector2, weight*dist))

def seasonalcolor(timeofyear=0):
    """interpolate between Winter and Summer color"""
    return color_interpolation(color1=colors["Winter BG"], 
                               color2=colors["Summer BG"],
                               weight=(1-math.cos(2*math.pi*timeofyear/8760)))

def change_color(surf, old, new):
    new_surf = pg.Surface(surf.get_size())
    new_surf.fill(new)
    surf.set_colorkey(old)
    new_surf.blit(surf, (0,0))
    return new_surf


def circle_surf(radius, color):
    surf = pg.Surface((radius*2,radius*2))
    pg.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0,0,0))
    return surf



class Renderer:
    def __init__(self, display:pg.Surface, camera, ui, scale=1.0):
        self.display = display
        self.cx, self.cy = display.get_width()//2, display.get_height()//2
        self.camera = camera
        self.ui = ui
        self.scale = scale
        self.lineheight = 25
        self.font = Font('assets/fonts/small_font.png')
        self.titlefont = Font('assets/fonts/large_font.png')

    def outline(self, surf, loc, pixel, color=(0,0,0), onto=False):
        if not onto: onto = self.display
        mask = pg.mask.from_surface(surf)
        mask_surf = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0))
        mask_surf.set_colorkey((0,0,0))
        x,y = loc
        onto.blit(mask_surf, (x-pixel, y))
        onto.blit(mask_surf, (x+pixel, y))
        onto.blit(mask_surf, (x, y-pixel))
        onto.blit(mask_surf, (x, y+pixel))

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

    def render_title(self):
        self.display.fill(seasonalcolor(0))
        title = """
        PassyBUIRLD

        +++press Enter to start+++"""
        self.render_lines(title, colors["Title"], (self.cx-100, 10), 
                         font=self.titlefont)  # Label

    def render_panel(self, lines, color, pos, size):
        box = pg.Surface(size)
        box.fill(color)
        self.render_lines(lines, onto=box, pos=(10,10))
        self.display.blit(box, pos)

    def render_building_menu(self, lines, color=WHITE):
        self.render_panel(lines, color=color, pos=(10,10), size=(300,250))

    def render_hvac_menu(self, lines, color=WHITE):
        self.render_panel(lines, color=color, pos=(10,410), size=(300,150))

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

    def draw_label(self, text, pos=(0,0), color=ALMOSTBLACK, onto=None):
        if not onto: onto = self.display
        self.render_line(text, color=color, pos=pos, onto=onto)

    def draw_stats(self, Lt, PH, coph):
        x, y = 10, 100

        self.draw_label(f"Leitwert {Lt:.2f} W/m2K", 
                         color=colors["QT"],
                         pos=(x,y))
        
        self.draw_label(text=f"Heatpump Power {PH} W/m2", 
                         color=colors["QT"],
                         pos=(x,y+self.lineheight))
        self.draw_label(text=f"Heatpump COP {coph:.2f}", 
                         color=colors["QT"],
                         pos=(x,y+self.lineheight))
        
    def draw_ui(self, ui_data):
        """Render UI elements on the screen based on provided data."""
        anchor_x, anchor_y = ui_data["anchorpoint"]
        first = ui_data["first"]
        second = ui_data["second"]
        QH = ui_data["QH"]
        QC = ui_data["QC"]
        debug_statements = ui_data["debug_statements"]
        
        width = 10
        # Draw anchor point line (reference point)
        pg.draw.rect(self.display, WHITE, pg.Rect(anchor_x, anchor_y, 120, 2))  # White anchor line

        # Initial position is the anchor point
        current_y = anchor_y

        # Render the first set of bars (positive values go down)
        for i, (label, value) in enumerate(first.items()):
            pg.draw.rect(self.display, colors[label], pg.Rect(anchor_x + 3*width, current_y, width, abs(value)))  # Draw the bar
            self.render_line(f"{label}: {value:.1f}", colors[label], (anchor_x + 8*width, i*20))  # Label
            current_y -= value  # Move down

        # Render the second set of bars (negative values go up)
        for label, value in second.items():
            pg.draw.rect(self.display, colors[label], pg.Rect(anchor_x + 4*width, current_y - value, width, value))  # Draw bar
            self.render_line(f"{label}: {value:.1f}", colors[label], (anchor_x + 8*width, current_y - value))  # Label
            current_y -= value  # Move up

        # Render QH and QC bars relative to anchor point
        # QH (positive, down)
        pg.draw.rect(self.display, colors["QH"], pg.Rect(anchor_x + 50, current_y-QH, 10, QH))
        if QH != 0:
            self.render_line(f"QH: {QH:.1f}", colors["QH"], (anchor_x + 10*width, anchor_y))  # Label
            
        # QC (negative, up)
        pg.draw.rect(self.display, colors["QC"], pg.Rect(anchor_x + 50, current_y, 10, -QC))
        if QC != 0:
            self.render_line(f"QC: {QC:.1f}", colors["QC"], (anchor_x + 10*width, anchor_y-20))  # Label

        # Render debug statements
        for i, (label, callback) in enumerate(debug_statements.items()):
            debug_text = f"{label}: {callback()}"
            self.render_line(debug_text, colors["DEBUG"], (10, 10 + i*self.lineheight))

 
    def draw_curve(self, curve):
        """Draw curves representing game data."""
        if len(curve.coordinates) < 2: return
        screencoords = [self.camera.screen_coords(coord) for coord in curve.coordinates[-300:]]  # Only last 300 points
    
        pg.draw.lines(self.display, curve.color, closed=False, points=screencoords, width=3)


    def draw_indoor_temperature(self, pos, dT, size):
        """Draw game objects like players or enemies."""
        x, y = self.camera.screen_coords(pos)

        if dT > 0:
            color = RED
        elif dT < 0:
            color = BLUE
        else:
            color = GREEN

        pg.draw.circle(self.display, color, (x, y), size)

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
    renderer = Renderer(screen, camera, ui=mock_ui_data)

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
        renderer.draw_ui(mock_ui_data)

        # Update the screen
        pg.display.flip()
        clock.tick(60)  # Cap the frame rate at 60 FPS

    pg.quit()

if __name__ == "__main__":
    test()