import random

import pygame as pg

from renderer import Renderer, colors
import renderer
from utils import color_interpolation, seasonalcolor, circle_surf



class Particle:
    def __init__(self, pos, speed, lifetime, game_coords = True):
        self.pos = pos
        self.speed = speed
        self.lifetime = lifetime
        self.age = lifetime
        self.game_coords = game_coords

    def update(self):
        self.lifetime -= 1
        self.pos += self.speed
        vx, vy = self.speed
        self.speed *=  0.85


class ParticleManager:
    def __init__(self, renderer:Renderer):
        self.groups = {}
        self.groups["heating"] = []
        self.groups["cooling"] = []
        self.groups["purchase"] = []
        self.groups["success"] = []
        self.groups["other"] = []
        self.renderer = renderer

    def add(self, list_name, position, velocity, lifetime):
        if list_name not in self.groups:
            raise KeyError(f"{list_name=} not in {__name__}.particleLists")
        p = Particle(
            pos=pg.Vector2(position),
            speed=velocity,
            lifetime=lifetime
        )
        self.groups[list_name].append(p)

    def heat(self, position, velocity):
        self.add("heating", position, 
                 0.5*pg.Vector2(velocity)+(random.random(),-random.random()), 
                 lifetime=random.randint(15,25))

    def cool(self, position, velocity):
        self.add("cooling", position, 
                 0.5*pg.Vector2(velocity)+(random.random(),random.random()), 
                 lifetime=random.randint(15,25))

    def purchase(self, position, n=5):
        for _ in range(n):
            lifetime = random.randint(10,30)
            self.add("purchase", position,
                 pg.Vector2(0,5).rotate(random.randint(-180, 180)), 
                 lifetime=lifetime)

    def success(self, position, velocity):
        self.add("success", position, pg.Vector2(velocity).rotate(random.randint(-30, 30)), 
                 lifetime=random.randint(15,60))


    def update(self):
        for _, container in self.groups.items():
            for i, p in sorted(enumerate(container), reverse=True):
                p.update()
                if p.lifetime <= 0:
                    container.pop(i)
                    continue

        # particle renderer
    def draw_particles(self, particleList, color, game_coords=False, size=500):
        for p in particleList:
            #self.renderer.glow_effect(pos=p.pos, radius=p.lifetime, color=color, game_coords=game_coords)
            self.renderer.ring_effect(pos=p.pos, radius=size*(p.age-p.lifetime)/p.age, 
                                    color=color_interpolation( renderer.WHITE,color, max(0,-0.1+p.lifetime/p.age)),
                                    width=p.lifetime, game_coords=game_coords)
                
    def render(self):
        # for _, group in self.groups.items():
        #     for p in group:
        #         p.render(renderer)
        
        self.draw_particles(self.groups["heating"], colors["QH"], game_coords=True) 
        self.draw_particles(self.groups["cooling"], colors["QC"], game_coords=True)
        self.draw_particles(self.groups["purchase"], colors["Purchase"], game_coords=False, size=5000)
        self.draw_particles(self.groups["success"], 
                            color=(random.randint(100,200), random.randint(200,255), random.randint(100,200)),
                            size=2000)
        self.draw_particles(self.groups["other"], color = (255,255,255), size=2000)


def test_draw_particles(container, screen):
    """Draw all particles on the screen."""
    for p in container:
        pg.draw.circle(screen, (255, 100, 100), (int(p.pos.x), int(p.pos.y)), 3)



