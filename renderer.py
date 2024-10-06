import pygame as pg
import math

colors = {
    "QV": (200, 0, 100),
    "QT": (250, 0, 0),
    "QS": (200, 200, 0),
    "QH": (255, 0, 0),
    "QC": (0, 0, 255),
    "Title": (255, 230, 225),
    "DEBUG": (255, 230, 225),
    "Winter BG": (60, 84, 153), #(61, 98, 116),
    "Summer BG": (255, 232, 197),
}

def seasonalcolor(timeofyear=0):
    """interpolate between Winter and Summer color"""
    winter = pg.Vector3(colors["Winter BG"])
    summer = pg.Vector3(colors["Summer BG"])
    inbetween = winter.move_towards(summer, 
                250*(1-math.cos(2*math.pi*timeofyear/8760)))
    return tuple(inbetween)

# Define color constants
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)


class Renderer:
    def __init__(self, display:pg.Surface, camera, ui, scale=1.0):
        self.display = display
        self.camera = camera
        self.ui = ui
        self.scale = scale
        self.lineheight = 15
        self.titlefont = pg.font.Font("assets/fonts/8-BIT WONDER.ttf", size=int(self.lineheight*self.scale*2))
        self.font = pg.font.Font("assets/fonts/cour.ttf", size=int(self.lineheight*self.scale))

    def render_line(self, text:str, color=(100,100,100), pos=(0,0), font=None):
        """Render a text line using the font."""
        if not font: font = self.font
        px, py = pos
        dy = 0
        for line in text.splitlines():
            dy += self.lineheight
            self.display.blit(font.render(line, True, color), (px, py+dy))

    def render_menu(self):
        self.display.fill(BLACK)
        title = """
        PassyBUIRLD

        <<<press Enter to start>>>"""
        self.render_line(title, colors["Title"], self.camera.position)  # Label

    def draw_background(self, hour_of_year):
        self.display.fill(seasonalcolor(hour_of_year))

    def draw_heat_particles(self, particleList):
        for p in particleList:
            pos = self.camera.screen_coords(p.pos)
            pg.draw.circle(self.display, colors["QH"], pos, p.lifetime/5)
            
    def draw_cool_particles(self, particleList):
        for p in particleList:
            pos = self.camera.screen_coords(p.pos)
            pg.draw.circle(self.display, colors["QC"], pos, p.lifetime/5)
          

    def draw_stats(self, game):
        x, y = 10, 500

        Lt = game.get_insulation()
        self.render_line(f"Leitwert {Lt:.2f} W/m²K", 
                         color=colors["QT"],
                         pos=(x,y))
        
        PH, coph = game.get_power_info()
        text = f"Wärmepumpe Leistung {PH} W/m²\nWärmepumpe Effizienz {coph*100:.1f}%" 
        self.render_line(text, 
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
        for label, value in first.items():
            pg.draw.rect(self.display, colors[label], pg.Rect(anchor_x + 3*width, current_y, width, abs(value)))  # Draw the bar
            self.render_line(f"{label}: {value:.1f}", colors[label], (anchor_x + 8*width, current_y))  # Label
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
            self.render_line(f"QH: {QH:.1f}", colors["QH"], (anchor_x + 8*width, current_y - QH))  # Label
            
        # QC (negative, up)
        pg.draw.rect(self.display, colors["QC"], pg.Rect(anchor_x + 50, current_y, 10, -QC))
        if QC != 0:
            self.render_line(f"QC: {QC:.1f}", colors["QC"], (anchor_x + 8*width, current_y - QC))  # Label

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
