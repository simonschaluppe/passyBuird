# utils.py
import pygame as pg
import math

def color_interpolation(color1, color2, weight):
    colorvector1 = pg.Vector3(color1)
    colorvector2 = pg.Vector3(color2)
    dist = colorvector1.distance_to(colorvector2)
    return tuple(colorvector1.move_towards(colorvector2, weight*dist))

def seasonalcolor(timeofyear=0, winter_color=(60, 84, 153), summer_color=(255, 232, 197)):
    return color_interpolation(winter_color, summer_color, weight=(1-math.cos(2*math.pi*timeofyear/8760)))

def circle_surf(radius, color):
    surf = pg.Surface((radius*2,radius*2))
    pg.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0,0,0))
    return surf

def change_color(surf, old, new):
    new_surf = pg.Surface(surf.get_size())
    new_surf.fill(new)
    surf.set_colorkey(old)
    new_surf.blit(surf, (0,0))
    return new_surf