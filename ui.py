import pygame as pg

colors = {
    "QV": (200, 0, 100),
    "QT": (250, 0, 0),
    "QS": (200, 200, 0),
    "QH": (255, 0, 0),
    "QC": (0, 0, 255),
}

class UI:
    """Overlays the info retrieved from the callbacks"""
    def __init__(self, 
                 anchorpoint,
                 fontsize=20, 
                 color="black",
                 ):
        self.fontsize = fontsize
        self.color = color
        self.font = pg.font.Font("assets/fonts/cour.ttf", fontsize)
        self.debug_statements = {}
        
        # Anchor points (legacy and new)
        self.anchor_x = anchorpoint[0] # old
        self.anchor_y = anchorpoint[1] # old
        self.anchorpoint = anchorpoint

        self.first = {"QV" : 0, "QT" : 0}
        self.second = {"QS" : 0}

    def debug(self, label:str, call:callable ):
        if callable(call):
            self.debug_statements[label] = call
        else:
            self.debug_statements[label] = lambda: call

    def render_line(self, text, color=None):
        if color is None:
            color = self.color
        return self.font.render(text, True, color)
    
    def update(self, game):
        self.first["QV"] = game.model.QV[game.hour] * 5
        self.first["QT"] = game.model.QT[game.hour] * 5
        self.second["QS"] = game.model.QS[game.hour] * 5
        self.QH = game.model.QH[game.hour] * 5
        self.QC = game.model.QC[game.hour] * 5
    
    # Old methods for backward compatibility
    def draw(self, surf:pg.Surface): # only used in old version of game.py
        current_height = self.anchor_y  - sum(val for val in self.first.values())
        pg.draw.rect(surf, "black", pg.Rect(20, self.anchor_y, 120, 2))
        for label, value in self.first.items():
            current_height += value
            pg.draw.rect(surf, colors[label], pg.Rect(50, current_height, 10, abs(value)))
            surf.blit(self.render_line(f"{label}: {value:.1f}"), (210, current_height))

        current_height = self.anchor_y - sum(val for val in self.first.values())

        for label, value in self.second.items():
            current_height -= value
            pg.draw.rect(surf, colors[label], pg.Rect(60, current_height, 10, value))
            surf.blit(self.render_line(f"{label}: {value:.1f}"), (210, current_height))

        endheight = current_height + self.QH
        pg.draw.rect(surf, colors["QH"], pg.Rect(70, endheight, 10, abs(self.QH)))
        #surf.blit(self.render_line(f"QH: {self.QH:.1f}"), (210, current_height+self.QH))
        endheight = endheight - self.QC
        pg.draw.rect(surf, colors["QC"], pg.Rect(70, endheight, 10, self.QC))
        #surf.blit(self.render_line(f"QC: {self.QC:.1f}"), (210, current_height-self.QC))

    def draw_debug(self, surf:pg.Surface): # only used in old version of game.py
        for i, (label, callback) in enumerate(self.debug_statements.items()):#
            render = self.render_line(label + ": " + str(callback()), "red")
            surf.blit(render, (10,i*self.fontsize))

    # New method for the refactored renderer
    def get_ui_elements(self):
        """Provide data for rendering the UI (new version)."""
        return {
            "anchorpoint": (self.anchor_x, self.anchor_y),
            "debug_statements": self.debug_statements,
            "first": self.first,
            "second": self.second,
            "QH": self.QH,
            "QC": self.QC
        }