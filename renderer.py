import sys
import math
from pathlib import Path

import pygame as pg
from pyparsing import White

from model import GameModel
import settings

from camera import Camera2D
from font import Font
from handler import Button  # necessary?
from upgrades import Upgrade
from utils import color_interpolation, seasonalcolor, circle_surf

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
    "PV": (255, 220, 30),
    "Title": (100, 30, 0),  # (164, 196, 146), #
    "DEBUG": (255,255,255),
    "Winter BG": (60, 84, 153),  # (61, 98, 116),
    "Summer BG": (255, 232, 197),
    "Button hovered": (156, 252, 186),  # (61, 98, 116),
    "Button pressed": (12, 70, 25),  # (61, 98, 116),
    "Button": (56, 161, 90),  # (51, 58, 96),
    "Price": (255, 255, 255),  # (50, 80, 30),
    "UI Text": (255, 255, 255),  # (76, 37, 29),
    "Upgrade text": (255, 255, 255),  # (153, 64, 154),
    "Emission text": (255, 255, 255),  # (66, 62, 56),
    "Emissions": (50, 50, 50),  # (105, 95, 78),
    "Purchase": (230, 255, 100),
    "TitleBG": (80, 80, 80),
    "PopupBG": (80, 80, 80),
}

# Define color constants
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ALMOSTBLACK = (10, 10, 10)
GREEN = (0, 255, 0)
GREY = (50, 50, 50)
OUTLINE = (10, 10, 10)

WARNING_PARAMS = dict(size=50, border_width=4, pulse=1.15, centered=True)

HOT_WARNING_PARAMS = dict(color=RED, border_color=(255, 100, 100), **WARNING_PARAMS)

COOL_WARNING_PARAMS = dict(color=BLUE, border_color=(100, 100, 255), **WARNING_PARAMS)

MONEY_WARNING_PARAMS = dict(color=GREEN, border_color=(100, 255, 100), **WARNING_PARAMS)


def color_indicator(dT):
    if dT > 0:
        return RED
    elif dT < 0:
        return BLUE
    else:
        return GREEN


class Renderer:
    def __init__(
        self, game:GameModel, display: pg.Surface, camera: Camera2D, scale=1.0, font="couriernew",
    ):
        self.game = game
        self.display = display
        self.cx, self.cy = display.get_width() // 2, display.get_height() // 2
        self.center = (self.cx, self.cy)
        self.camera = camera
        self.scale = scale

        # defaults
        self.lineheight = int(25 * self.scale)
        self.fontsize = int(30 * self.scale)
        self.font_custom_small = Font(FONT_PATH / "small_font.png")
        self.font_custom_large = Font(FONT_PATH / "large_font.png")
        if font == "custom":
            self.font = self.font_custom_small
            self.titlefont = self.font_custom_large
        else:
            self.font = pg.font.SysFont(font, self.fontsize, bold=False)
            self.titlefont = pg.font.SysFont(font, self.fontsize, bold=True)

        # load QR code
        self.qr_code = pg.image.load(IMAGE_PATH / "qrcode.png").convert()
        #self.qr_code.set_colorkey(WHITE)
        self.qr_code = pg.transform.scale(self.qr_code, size=(180, 180))

        # components
        self.ui_renderer = UIRenderer(self)
        self.curves_renderer = CurvesRenderer(self)
        self.menu_renderer = MenuRenderer(self)
        self.highscores_renderer = HighscoreRenderer(self)

        # Load the background image for the upgrade menu
        self.level_backgrounds = {}
        background_paths = [
            "Dunkelflaute.png",
            "Spring.png",
            "Summer.png",
            "Fall.png",
            "Winter.png",
        ]
        for background in background_paths:
            bg_image = pg.image.load(
                IMAGE_PATH / settings.BACKGROUND_FOLDER / background
            ).convert()
            scaled_image = pg.transform.scale(bg_image, self.display.get_size())
            self.level_backgrounds[background] = scaled_image

        self.level_background = self.level_backgrounds[background_paths[0]]

        

        self.bg_overlay = pg.Surface(self.display.get_size(), pg.SRCALPHA)
        self.bg_overlay.fill((0, 0, 0))
        

    def set_background(self, path):
        self.level_background = self.level_backgrounds[path]

    # debug stuff, should be low level
    def debug(self, statements):
        # Render debug statements
        for i, (label, callback) in enumerate(statements.items()):
            debug_text = f"{label}: {callback()}"
            self.render_line(
                debug_text,
                colors["DEBUG"],
                (900, 20 + i * self.lineheight)
            )

    def pulse(self):
        """Global pulse in [0, 1]."""
        t = pg.time.get_ticks() / 1000.0
        return 0.5 + 0.5 * math.sin(t * 2 * math.pi * 2.0)  # 2 Hz

    # basic rendering
    def outline(self, surf, loc, pixel, color=OUTLINE, onto=False, orig_color=None):
        if not onto:
            onto = self.display
        orig_color = orig_color or color
        color = color_interpolation(orig_color, BLACK, 0.5)
        mask = pg.mask.from_surface(surf)
        mask_surf = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0))
        mask_surf.set_colorkey((0, 0, 0))
        x, y = loc
        #onto.blit(mask_surf, (x - pixel, y))
        onto.blit(mask_surf, (x + pixel, y))
        #onto.blit(mask_surf, (x, y - pixel))
        onto.blit(mask_surf, (x, y + pixel))
        #onto.blit(mask_surf, (x - pixel, y - pixel))
        onto.blit(mask_surf, (x + pixel, y + pixel))
        #onto.blit(mask_surf, (x + pixel, y - pixel))
        #onto.blit(mask_surf, (x - pixel, y + pixel))

    def render_line(
        self,
        text: str,
        color=WHITE,
        pos=(0, 0),  # by default topleft corner of text
        size=None,
        border_width=3,  # pixel
        border_color=OUTLINE,
        font=None,
        onto=None,
        pulse=False,
        centered=False,  # interprets pos as center of text, not topleft
    ):
        """Render a single text line onto a surface"""
        if not font:
            font = self.font
        if not onto:
            onto = self.display
        if not size:
            size = self.fontsize
        px, py = pos
        alpha = None
        scale_factor = 1.0

        if pulse:
            p = self.pulse()  # expected 0..1
            # alpha = int(120 + 135 * p)  # 120..255
            if isinstance(pulse, (int, float)):
                # animate between 100% and the given pulse factor
                scale_factor = 1.0 + (pulse - 1.0) * p

        if type(font) is Font:
            base_surf = font.surface(text, size, color).convert_alpha()
        else:
            base_surf = font.render(text, True, color).convert_alpha()

        if centered:
            base_rect = base_surf.get_rect(center=(px, py))
        else:
            base_rect = base_surf.get_rect(topleft=(px, py))
        center = base_rect.center

        textsurf = base_surf
        if scale_factor != 1.0:
            w, h = base_surf.get_size()
            new_size = (max(1, int(w * scale_factor)), max(1, int(h * scale_factor)))
            textsurf = pg.transform.smoothscale(base_surf, new_size)

        if alpha is not None:
            textsurf.set_alpha(alpha)

        rect = textsurf.get_rect(center=center)

        if border_width:
            self.outline(textsurf, rect.topleft, border_width, border_color, onto=onto)
        onto.blit(textsurf, rect.topleft)

    def render_lines(
        self,
        text: str,
        color=WHITE,
        pos=(0, 0),
        size=26,
        font=None,
        onto=None,
        lineheight=None,
        **kwargs,
    ):
        px, py = pos
        dy = 0
        for line in text.splitlines():
            self.render_line(
                line, color, (px, py + dy), size, font=font, onto=onto, **kwargs
            )
            dy += lineheight if lineheight else self.lineheight

    def draw_grid(self, spacing, color=BLACK):
        for x in range(0, self.display.get_width(), spacing):
            pg.draw.line(self.display, color, (x, 0), (x, self.display.get_height()))
        for y in range(0, self.display.get_height(), spacing):
            pg.draw.line(self.display, color, (0, y), (self.display.get_width(), y))

    def render_button(self, button: Button):

        button_surf = pg.Surface(button.size, pg.SRCALPHA)
        #button_surf.fill(WHITE)  # clear
        bw, bh = button_surf.get_size()
        text_color = WHITE
        color = colors["Button"]
        pulse = 1.03
        if button.hovered:
            color = colors["Button hovered"]
        if button.pressed:
            color = colors["Button pressed"]
        if button.disabled:
            #print("disabled gray")
            color = GREY
            text_color = GREY
            pulse = None
        radius = 12
        border = 4 + 2 * button.hovered - button.pressed
        offset = 2 + 4 * button.pressed
        center_pos = (bw // 2 + offset, bh // 2 + int(offset / 2))
        rect = button_surf.get_rect().move(offset, int(offset / 2))
        # --- BORDER ---
        pg.draw.rect(
            button_surf,
            settings.BUTTON_BORDER_COLOR,  # or your outline color
            rect,
            border_radius=radius,
        )
        # --- INNER BUTTON ---
        inner_rect = rect.inflate(-border * 2, -border * 2)
        pg.draw.rect(
            button_surf,
            color,
            inner_rect,
            border_radius=radius - border,
        )
        self.render_line(
            button.text,
            color=text_color,
            pos=center_pos,
            onto=button_surf,
            size=25,
            border_width=2 + 1 * button.hovered,
            pulse=pulse,
            font=self.font_custom_small,
            centered=True,
        )
        
        self.display.blit(button_surf, button.position)
        

    def draw_background(self, hour_of_year=0):
        self.display.blit(self.level_background, (0, 0))

        hour = hour_of_year % 24
        darkness = 0.2 * (1 - math.cos(2 * math.pi * (hour - 12) / 24))
        alpha = int(255 * darkness)   # 0..127

        if alpha > 0:
            self.bg_overlay.set_alpha(alpha)
            self.display.blit(self.bg_overlay, (0, 0))

    # draw stuff using camera (game)
    def render_curves(self, curve_data, paused: bool):
        self.curves_renderer.render(curve_data, paused)

    def ring_effect(self, pos, radius, color, width=1, game_coords=False):
        pos = self.camera.screen_coords(pos) if game_coords else pos
        x, y = pos
        pg.draw.circle(self.display, color, pos, radius / 8, width=width)

    def glow_effect(self, pos, radius, color, game_coords=False):
        pos = self.camera.screen_coords(pos) if game_coords else pos
        x, y = pos
        pg.draw.circle(self.display, color, pos, radius / 8)
        glow_color = color_interpolation((0, 0, 0), color, 0.2)
        self.display.blit(
            circle_surf(radius, glow_color),
            (x - radius, y - radius),
            special_flags=pg.BLEND_RGB_ADD,
        )

    def draw_too_hot_warning(self):
        self.render_lines(
            "Warning: Too Hot!",
            pos=(self.cx, self.cy - 100),
            font=self.font_custom_small,
            **HOT_WARNING_PARAMS,
        )
        self.render_line(
            "Press <RMB> to Cool!",
            pos=(self.cx, self.cy - 150),
            font=self.font_custom_small,
            **HOT_WARNING_PARAMS,
        )

    def draw_too_cold_warning(self):
        self.render_line(
            "Warning: Too COLD!",
            pos=(self.cx, self.cy + 100),
            font=self.font_custom_large,
            **COOL_WARNING_PARAMS,
        )
        self.render_line(
            "Press <LMB> to Heat!",
            pos=(self.cx, self.cy + 150),
            font=self.font_custom_small,
            **COOL_WARNING_PARAMS,
        )

    def draw_low_money_warning(self):
        self.render_line(
            "Low money!",
            pos=(self.cx, self.cy - 200),
            font=self.font_custom_large,
            **HOT_WARNING_PARAMS,
        )

    def draw_no_money_warning(self):
        self.render_line(
            "Not enough money!",
            pos=(self.cx, self.cy + 100),
            font=self.font_custom_large,
            **COOL_WARNING_PARAMS,
        )

    def draw_overlay(self, text):
        params = WARNING_PARAMS
        self.render_line(
                    text,
                    color=WHITE,
                    border_color=GREY,
                    pos=(self.cx, self.cy + 250),
                    font=self.font_custom_small,
                    **params,
                )

    def draw_paused_overlay(self):
        params = WARNING_PARAMS
        self.draw_overlay("Game Paused. Press <P> to Unpause!")

    # main game UI
    def render_ui(self, ui_data):
        self.ui_renderer.render(ui_data)

    # menu screen
    def render_menu(self, data, index=0):
        self.menu_renderer.render(data, index)

    def render_highscores(self, data, index = 0):
        self.highscores_renderer.render(data, index)

    def render_popup(self, title: str, body: list, screen_params, index):
        line_size = 24
        line_spacing = 30  # slightly more than size to avoid overlap

        self.menu_renderer.render_background(index=index)

        panel_rect = pg.Rect(*screen_params)

        self.left = screen_params[0] + 20
        self.top = screen_params[1] + 20
        overlay = pg.Surface(panel_rect.size, pg.SRCALPHA)
        overlay.fill((*colors["PopupBG"], 150))  # 150 = alpha (0–255)

        self.display.blit(overlay, panel_rect.topleft)
        pg.draw.rect(
            self.display,
            (220, 220, 220),  # border color
            panel_rect,
            width=2,
            border_radius=8,
        )

        self.render_line(
            title,
            pos=(self.left, self.top),
            size=50,
            font=self.font_custom_large,
        )
        y = self.top + 100  # Larger space after title

        for line in body:
            self.render_line(
                line,
                pos=(self.left, y),
                size=line_size,
            )
            y += line_spacing

    def render_title_screen(self, title: str, body: list, screen_params, index):
        line_size = 24
        line_spacing = 30  # slightly more than size to avoid overlap

        self.menu_renderer.render_background(index=index)

        panel_rect = pg.Rect(*screen_params)

        self.left = screen_params[0] + 20
        self.top = screen_params[1] + 20

        overlay = pg.Surface(panel_rect.size, pg.SRCALPHA)
        overlay.fill((*colors["PopupBG"], 150))  # 150 = alpha (0–255)

        self.display.blit(overlay, panel_rect.topleft)
        pg.draw.rect(
            self.display,
            (220, 220, 220),  # border color
            panel_rect,
            width=2,
            border_radius=8,
        )

        pg.draw.rect(
            self.display,
            colors["TitleBG"],  # border color
            panel_rect,
            width=2,
            border_radius=8,
        )

        self.render_line(
            title,
            pos=(self.left, self.top),
            size=40,
            font=self.font_custom_large,
        )
        y = self.top + self.lineheight * 2  # Larger space after title
        self.render_line(
            "PassyBUIRD!",
            color=WHITE,
            pos=(self.left + 10, y),
            size=80,
            font=self.font_custom_small,
            border_width=10,
            pulse=1.05,
        )
        y = y + 100  # Larger space after title

        for line in body:
            self.render_line(
                line,
                pos=(self.left, y),
                size=line_size,
            )
            y += line_spacing


        # self.draw_grid(100)

        self.display.blit(self.qr_code, (930, 370))


class MenuRenderer:
    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer
        self.display = renderer.display
        self.render_line = renderer.render_line
        self.render_lines = renderer.render_lines

        self.tile_size = (160, 133)  # Size for each upgrade tile

        # Load the background image for the upgrade menu
        bg_image = pg.image.load(
            IMAGE_PATH / settings.BACKGROUND_FOLDER / "Closeup2.png"
        ).convert()
        bg_image_upgraded = pg.image.load(
            IMAGE_PATH / settings.BACKGROUND_FOLDER / "Closeup2_upgraded.png"
        ).convert()
        bg_image_upgraded_max = pg.image.load(
            IMAGE_PATH / settings.BACKGROUND_FOLDER / "Closeup2_upgraded_max.png"
        ).convert()
        bg_image_fail = pg.image.load(
            IMAGE_PATH / settings.BACKGROUND_FOLDER / "Heat_Stroke.png"
        ).convert()
        self.bg_images = [
            pg.transform.scale(img, self.display.get_size())
            for img in [bg_image, bg_image_upgraded, bg_image_upgraded_max, bg_image_fail]
        ]
    def render(self, data, index=0):
        """Render the upgrade menu including background, tiles, and costs."""
        # Draw the menu background first
        self.display.blit(self.bg_images[index], (0, 0))

        x,y = settings.ANCHOR_SHOP_TITLE
        self.render_title((x,y))
        self.render_text((x,y+150))
        self.render_updrade_text(
            data["upgrade_text"],
            settings.ANCHOR_SHOP_UPGRADE_TEXT,
            colors["UI Text"],
        )
        self.render_game_stats(
            data["game_stats"], settings.ANCHOR_SHOP_GAME_STATS, colors["UI Text"]
        )

    def render_background(self, index=0):
        bg_image = self.bg_images[index]
        self.menu_background = pg.transform.scale(bg_image, self.display.get_size())
        self.display.blit(self.menu_background, (0, 0))

    def render_title(self, pos):
        title = "PassyBUIRD"
        self.render_line(
            title,
            WHITE,
            pos,
            font=self.renderer.font_custom_small,
            size=80,
            border_width=8,
            pulse=1.05,
        )

    def render_text(self, pos):
        text = [
            "This is the shop. Here you can buy",
            "upgrades for your building.",
        ]
        self.render_lines(
                "\n".join(text),
                colors["UI Text"],
                pos,
                font=self.renderer.titlefont,
                size=40,
                lineheight=45
            )

    def render_upgrade_tiles(self, upgrades, pos):
        """Render upgrade tiles on the screen."""
        start_x, start_y = pos  # Starting position for the grid of tiles
        padding = 10  # Space between tiles

        idx = 0
        for key, upgrade in upgrades.items():
            x = start_x + (idx // 3) * (self.tile_size[0] + padding)
            y = start_y + (idx % 3) * (self.tile_size[1] + padding)

            # Render the upgrade tile
            self.render_upgrade_tile(upgrade, (x, y))
            idx += 1

    def render_upgrade_tile(self, upgrade: Upgrade, pos):
        """Render a single upgrade tile with its cost and state."""
        tile_surf = pg.Surface(self.tile_size)

        # Render the tile image
        tile_image = pg.image.load(IMAGE_PATH / upgrade.image).convert_alpha()
        tile_image = pg.transform.scale(tile_image, size=self.tile_size)

        if not upgrade.available:
            grey_surf = pg.Surface(self.tile_size)
            grey_surf.fill((150, 150, 150, 100))
            grey_surf.blit(tile_image, (0, 0))

        tile_surf.blit(tile_image, (0, 0))
        tile_surf.set_colorkey((0, 0, 0))

        self.render_line(
            f"{upgrade.upgrade_text}",
            pos=(10, 10),
            color=colors["Upgrade text"],
            size=20,
            onto=tile_surf,
        )
        # Draw the cost below the tile
        self.render_line(
            f"€{upgrade.cost}",
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
            size=52,
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

    def render_updrade_text(self, data, pos, color):
        spacing = 50  
        self.render_line(
            "Upgrades", colors["UI Text"], pos, font=self.renderer.titlefont, size=40
        )
        self.render_lines(data["lines"], color=color, pos=(pos[0], pos[1] + spacing+10), lineheight=spacing)

    def render_game_stats(self, data, pos, color):
        self.render_lines(data["lines"], color=color, pos=pos, lineheight=50)

class HighscoreRenderer:
    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer
        self.display = renderer.display
        self.render_line = renderer.render_line
        self.render_lines = renderer.render_lines

        self.tile_size = (160, 133)  # Size for each upgrade tile

        # Load the background image for the upgrade menu
        bg_image = pg.image.load(
            IMAGE_PATH / "backgrounds" / "Highscore.png"
        ).convert()
        self.bg_images = [
            pg.transform.scale(img, self.display.get_size())
            for img in [bg_image]
        ]
    def render(self, data, index=0):
        """Render the Highscore menu including background"""
        # Draw the menu background first
        self.display.blit(self.bg_images[index], (0, 0))
        self.data = data

        x,y = settings.ANCHOR_SHOP_TITLE
        self.render_title((x+400,y))
        self.render_text((x+250,y+100))

    def render_background(self, index=0):
        bg_image = self.bg_images[index]
        self.menu_background = pg.transform.scale(bg_image, self.display.get_size())
        self.display.blit(self.menu_background, (0, 0))

    def render_title(self, pos):
        title = "Highscores"
        self.render_line(
            title,
            WHITE,
            pos,
            font=self.renderer.font_custom_small,
            size=80,
            border_width=8,
            pulse=1.05,
        )

    def render_text(self, pos):
        text = self.data

        self.render_lines(
                "\n".join(text),
                colors["UI Text"],
                pos,
                font=self.renderer.titlefont,
                size=50,
                lineheight=25
            )

class CurvesRenderer:
    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer
        self.screen_coords = renderer.camera.screen_coords
        self.curve_width = 3
        self.size_TI_indicator = 10

        # Load the house image for the indicator
        house = pg.image.load(IMAGE_PATH / "glide.png").convert()
        house.set_colorkey((255, 255, 0))
        self.house = pg.transform.scale(house, (64, 53))

    def render(self, data, paused: bool):
        self.draw_area_between_curves(
            (100, 255, 150),
            data["Minimum Comfort Temperature"]["curve"],
            data["Maximum Comfort Temperature"]["curve"],
            alpha=100,
        )



        self.draw_curve("orange", 
                        data["Maximum Comfort Temperature"]["curve"])
        self.draw_curve("lightblue", data["Minimum Comfort Temperature"]["curve"])
        self.draw_curve("red", data["Indoor Temperature"], width=5, alpha=200)
        self.draw_curve(seasonalcolor(self.renderer.game.hour), data["Outdoor Temperature"], width=6, alpha=150)
        self.draw_curve(colors["Emissions"], data["Carbon Intensity"]["curve"], 
                        width=4, alpha=150)
        self.draw_curve((255,230, 50), data["PV"]["curve"], 
                        width=4, alpha=100)

        self.draw_area_between_curves(
            (255, 220, 30),
            data["PV"]["curve"],
            data["PV"]["base"],
            alpha=150,
        )


        self.draw_date_indicator(data["Date Indicator"])
        self.draw_house_indicator(data["TI Indicator"])
        self.draw_TI_indicator(data["TA Indicator"])

        if paused:
            self.draw_indicator(
                data["Minimum Comfort Temperature"]["indicator"]["pos"],
                colors["QC"],
                data["Minimum Comfort Temperature"]["indicator"]["text"],
            )
            self.draw_indicator(
                data["Maximum Comfort Temperature"]["indicator"]["pos"],
                colors["QH"],
                data["Maximum Comfort Temperature"]["indicator"]["text"],
            )
            self.draw_indicator(
            data["Carbon Intensity"]["indicator"]["pos"],
            GREY,
            data["Carbon Intensity"]["indicator"]["text"],
        )
            self.draw_TA_indicator(data["TA Indicator"])
            self.draw_indicator(data["PV"]["indicator"]["pos"], colors["PV"],
                                data["PV"]["indicator"]["text"])


    def draw_date_indicator(self, data):
        # print(f"{len(data)=}")
        for hour, y, dt in data:
            self.renderer.render_line(
                dt.strftime("%d. %b"),
                WHITE,
                pos=self.screen_coords((hour, 20)),
                centered=False,
                size=30,
                border_width=1,
                font=self.renderer.font_custom_small,
            )

    # curve renderer
    def draw_curve(self, color, curve, width=None, alpha=255):
        width = width or self.curve_width
        color=pg.Color(color)
        color.a = alpha
        if len(curve) < 2:
            return

        screencoords = [self.screen_coords(point) for point in curve]
        # Fast path (no transparency)
        if alpha >= 255:
            pg.draw.lines(
                self.renderer.display,
                color,
                closed=False,
                points=screencoords,
                width=width,
            )
            return

        # Transparent draw
        overlay = pg.Surface(self.renderer.display.get_size(), pg.SRCALPHA)

        pg.draw.lines(
            overlay,
            color,
            closed=False,
            points=screencoords,
            width=width,
        )

        self.renderer.display.blit(overlay, (0, 0))

    def draw_area_between_curves(self, color, curve1, curve2, alpha=80):
        n = min(len(curve1), len(curve2))
        if n < 2:
            return

        if (
            not hasattr(self, "_area_overlay")
            or self._area_overlay.get_size() != self.renderer.display.get_size()
        ):
            self._area_overlay = pg.Surface(
                self.renderer.display.get_size(), pg.SRCALPHA
            )

        self._area_overlay.fill((0, 0, 0, 0))

        s1 = [self.screen_coords(point) for point in curve1[:n]]
        s2 = [self.screen_coords(point) for point in curve2[:n]]
        poly = s1 + list(reversed(s2))

        pg.draw.polygon(self._area_overlay, (*color, alpha), poly)
        self.renderer.display.blit(self._area_overlay, (0, 0))

    def draw_house_indicator(self, data):
        """Draw game objects like players or enemies."""
        x, y = self.screen_coords(data["Position"])
        color = colors.get(data["Color"], "comfort")
        if color == "comfort":
            color = color_interpolation(
                color_indicator(data["Comfort dT"]), GREEN, data["score"] / 100
            )
        size = self.size_TI_indicator * data["Scale"]
        pg.draw.circle(self.renderer.display, color, (x, y), size)
        w, h = self.house.get_size()
        scale = data["Scale"]  # e.g. 50%
        # scaled = pg.transform.scale(self.house, (int(w * scale), int(h * scale)))
        scaled = pg.transform.scale(self.house, (int(w * 1), int(h * 1)))

        draw_pos = (x - scaled.get_width() // 2, y - scaled.get_height() // 2)

        self.renderer.outline(
            scaled,
            loc=draw_pos,
            pixel=max(1, int(scale * 3)),
            color=color,
            onto=self.renderer.display,
        )
        self.renderer.display.blit(scaled, draw_pos)

    def draw_indicator(self, pos, color, text, game_coords=True):
        screenpos = self.screen_coords(pos) if game_coords else pos
        bordercolor = color_interpolation(color, (255, 255, 255), 0.8)
        textcolor = color
        self.renderer.render_line(
            text, textcolor, pos=screenpos, border_color=bordercolor, centered=False
        )

    def draw_TA_indicator(self, data):
        hour, TA = data["TA"]
        textcolor = seasonalcolor(hour)
        self.draw_indicator(
            pos=(hour, TA + 10), color=textcolor, text=f"Outdoor Temp {TA:+2.1f}°C"
        )

    def draw_TI_indicator(self, data):
        hour, TI = data["TI"]
        textcolor = seasonalcolor(hour)
        self.draw_indicator(
            pos=(hour, TI), color=textcolor, text=f"Indoor Temp {TI:+2.1f}°C"
        )


class UIRenderer:
    def __init__(self, renderer: Renderer) -> None:
        self.renderer = renderer
        self.display = renderer.display
        self.render_line = renderer.render_line

    def render(self, ui_data):
        pulse = 1.1 if ui_data["player_activity"] else False
        self.energybalance(ui_data["Energy balance"])

        comfort_data = ui_data["Scores"]["Comfort"]
        comfort_pulse = 1.2 if bool(comfort_data["change"]) else False

        # render remaining days
        self.render_line(
            "Remaining days", pos=settings.POS_REMAINING_HOURS, color=WHITE
        )
        self.render_line(
            ui_data["Remaining days"],
            pos=settings.POS_REMAINING_HOURS_VALUE,
            color=GREEN,
            font=self.renderer.font_custom_small,
        )

        anchor_x, anchor_y = settings.ANCHOR_LEVEL_STATS
        spacing_x = settings.ANCHOR_LEVEL_SPACING_X
        line_x = settings.ANCHOR_LEVEL_LINE_X

        # render player money
        self.render_line("Money", pos=(anchor_y, anchor_x + line_x), color=WHITE)
        self.render_line(
            f"€ {ui_data["Scores"]["Money"]:.0f}",
            color=RED if pulse else (100, 255, 120),
            pos=(anchor_y + 150, anchor_x),
            font=self.renderer.font_custom_small,
            pulse=0.9 / pulse if pulse else False,
        )
        line_x += spacing_x

        self.render_comfort_score(
            score=comfort_data["score"],
            dT=comfort_data["dT"],
            pulse=comfort_pulse,
            pos=(anchor_y, anchor_x + line_x),
        )
        line_x += spacing_x

       

        self.render_line("CO2 emitted ", pos=(anchor_y, anchor_x + line_x), color=WHITE)
        self.render_line(
            f"{int(ui_data["CO2"])} kg",
            pos=(anchor_y + 150, anchor_x + line_x),
            color=GREY,
            pulse=pulse,
            size = 25+int((ui_data["CO2"] if ui_data["CO2"] >= 0 else 0)**0.6),
            font=self.renderer.font_custom_small,
        ) 
        line_x += spacing_x
        self.render_line(
            ui_data["Price"], pos=(anchor_y, anchor_x + line_x), color=colors["Price"]
        )
        line_x += spacing_x
        self.render_line(
            ui_data["Feedin"], pos=(anchor_y, anchor_x + line_x), color=colors["Price"]
        )
        line_x += spacing_x

        self.render_line(
            ui_data["COP"], pos=(anchor_y, anchor_x + line_x), color=colors["UI Text"]
        )
        line_x += spacing_x

        self.render_line(
            ui_data["Power"], pos=(anchor_y, anchor_x + line_x), color=colors["UI Text"]
        )

    def energybalance(self, balance_data):
        """Render energy balance as waterfall diagram."""
        anchor_x, anchor_y = 960, self.renderer.cy
        first = balance_data["first"]
        second = balance_data["second"]
        QH = balance_data["QH"]
        QC = balance_data["QC"]

        width = 10
        # Draw anchor point line (reference point)
        pg.draw.rect(
            self.display, WHITE, pg.Rect(anchor_x, anchor_y, 192, 2)
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

    def render_comfort_score(self, score, dT, pos=(880, 66), pulse=False):
        px, py = pos
        text = "Comfort"
        self.render_line(text, WHITE, pos=pos)
        color = RED

        color = color_interpolation(color, GREEN, score / 100)
        self.render_line(
            f"{score:.1f}%",
            color,
            pos=(px + 150, py),
            pulse=pulse,
            font=self.renderer.font_custom_small,
        )


# test code
def test():
    import pygame as pg
    from pygame.math import Vector2  # For handling positions
    import random
    from camera import Camera2D  # Assuming you have a simple Camera2D implementation
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
