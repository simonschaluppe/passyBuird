import pygame as pg

class Curve:
    def __init__(self, color="red", starting_point=None) -> None:
        self.coordinates = []
        if starting_point:
            self.update(starting_point)
        self.color = color
    
    @classmethod
    def from_points(cls, points, *args, **kwargs) -> "Curve":
        new = cls(*args, **kwargs)
        for i, p in enumerate(points):
            new.update((i,p))
        return new
    
    def update(self, point=None):
        if point:
            self.coordinates.append(point)

    def extend(self):
        lastx, lasty = self.coordinates[-1]
        self.coordinates.append((lastx+1, lasty))

    def draw(self, surface, camera):
        if len(self.coordinates) < 2: return
        screencoords = []
        for coord in self.coordinates:
            screencoords.append(camera.screen_coords(coord))
        pg.draw.lines(surface, self.color, closed=False, points=screencoords)

