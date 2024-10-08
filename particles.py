import random
import pygame as pg

class Particle:
    def __init__(self, pos, speed, lifetime):
        self.pos = pos
        self.speed = speed
        self.lifetime = lifetime

    
class ParticleManager:
    def __init__(self):
        self.groups = {}
        self.groups["heating"] = []
        self.groups["cooling"] = []
    
    def add(self, list_name, position, velocity, lifetime):
        if list_name not in self.groups:
            raise KeyError(f"{list_name=} not in {__name__}.particleLists")
        p = Particle(
            pos=pg.Vector2(position), 
            speed=pg.Vector2(velocity).rotate(random.randint(-30,30)),
            lifetime=lifetime
            )
        self.groups[list_name].append(p)

    def heat(self, position, velocity):
        self.add("heating", position, velocity, lifetime=50)

    def cool(self, position, velocity):
        self.add("cooling", position, velocity, lifetime=50)

    def update(self):
        for name, container in self.groups.items():
            for i, p in sorted(enumerate(container), reverse=True):
                p.lifetime -= 1
                if p.lifetime <= 0: 
                    container.pop(i)
                    continue
                #p.speed.scale_to_length(p.lifetime/50)
                p.pos += p.speed
                vx, vy = p.speed
                p.speed = (vx, vy*0.9)


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