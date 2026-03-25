import random

import pygame as pg

from renderer import Renderer
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
        self.speed = (vx, vy*0.9 - 0.1)


class ParticleManager:
    def __init__(self):
        self.groups = {}
        self.groups["heating"] = []
        self.groups["cooling"] = []
        self.groups["purchase"] = []
        self.groups["success"] = []
        self.groups["other"] = []

    def add(self, list_name, position, velocity, lifetime):
        if list_name not in self.groups:
            raise KeyError(f"{list_name=} not in {__name__}.particleLists")
        p = Particle(
            pos=pg.Vector2(position),
            speed=pg.Vector2(velocity).rotate(random.randint(-30, 30)),
            lifetime=lifetime
        )
        self.groups[list_name].append(p)

    def heat(self, position, velocity):
        self.add("heating", position, velocity, lifetime=50)

    def cool(self, position, velocity):
        self.add("cooling", position, velocity, lifetime=50)

    def purchase(self, position, velocity):
        self.add("purchase", position, velocity, lifetime=50)

    def success(self, position, velocity):
        self.add("success", position, velocity, lifetime=100)


    def update(self):
        for _, container in self.groups.items():
            for i, p in sorted(enumerate(container), reverse=True):
                p.update()
                if p.lifetime <= 0:
                    container.pop(i)
                    continue
                
    def render(self, renderer:Renderer):
        # for _, group in self.groups.items():
        #     for p in group:
        #         p.render(renderer)
        renderer.draw_heat_particles(self.groups["heating"])
        renderer.draw_cool_particles(self.groups["cooling"])
        renderer.draw_purchase_particles(self.groups["purchase"])
        renderer.draw_particles(self.groups["success"], color=(random.randint(100,200), random.randint(200,255), random.randint(100,200)))
        renderer.draw_particles(self.groups["other"], color = (255,255,255))


def test_draw_particles(container, screen):
    """Draw all particles on the screen."""
    for p in container:
        pg.draw.circle(screen, (255, 100, 100), (int(p.pos.x), int(p.pos.y)), 3)


if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((400, 400))
    clock = pg.time.Clock()

    pmanager = ParticleManager()

    running = True
    while running:
        screen.fill((0, 0, 0))  # Clear the screen with black

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            # Emit particles when the mouse is pressed
        if pg.mouse.get_pressed()[0]:
            mouse_pos = pg.mouse.get_pos()  # Get current mouse position
            velocity = (random.uniform(-10, 10), random.uniform(-10, 10))  # Random initial velocity
            pmanager.heat(position=mouse_pos, velocity=velocity)

        # Update and draw particles
        pmanager.update()
        test_draw_particles(pmanager.groups["heating"], screen)

        pg.display.flip()  # Update the display
        clock.tick(60)  # Run at 60 FPS

    pg.quit()
