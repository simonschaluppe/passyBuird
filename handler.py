
import pygame as pg

class Button:
    def __init__(self, pos, callback, text="", size=(150, 40) ):
        self.position = pos
        self.size = size
        self.text = text
        self.callback = callback
        self.hovered = False
    
    def press(self):
        self.callback()

    def is_hovering(self, mouse_pos):
        """Check if the mouse is over the button."""
        x, y = self.position
        w, h = self.size
        self.hovered = x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h
        return self.hovered

class InputHandler(object):
    def __init__(self):
        self.keypress_bindings = {}
        self.keyrelease_bindings = {}
        self.continuous_keypress_bindings = {}
        self.mousebutton_bindings = {}
        self.continuous_mousebutton_bindings = {}

        self.buttons = []

    def register_button(self, button):
        """Register a button to be checked for clicks."""
        self.buttons.append(button)

    def bind_keypress(self, key, action):
        self.keypress_bindings[key] = action

    def bind_keyrelease(self, key, action):
        self.keyrelease_bindings[key] = action

    def bind_continuous_keypress(self, key, action):
        self.continuous_keypress_bindings[key] = action

    def bind_mousebutton(self, button, action):
        self.mousebutton_bindings[button] = action    
        
    def bind_continuous_mousebutton(self, button, action):
        self.continuous_mousebutton_bindings[button] = action

    def bind_WASD_movement(self, mover, speed:float, turnspeed:float):
        self.bind_continuous_keypress(pg.K_w, lambda: mover.move_in_direction(speed))
        self.bind_continuous_keypress(pg.K_s, lambda: mover.move_in_direction(-speed))
        self.bind_continuous_keypress(pg.K_a, lambda: mover.turn(angle=turnspeed))
        self.bind_continuous_keypress(pg.K_d, lambda: mover.turn(angle=-turnspeed))

    def bind_camera(self, camera):
        self.bind_mousebutton(4, lambda: camera.zoom(1.1))
        self.bind_mousebutton(5, lambda: camera.zoom(0.9))
        self.bind_continuous_keypress(pg.K_UP, lambda: camera.move((0,10)))
        self.bind_continuous_keypress(pg.K_DOWN, lambda: camera.move((0,-10)))
        self.bind_continuous_keypress(pg.K_LEFT, lambda: camera.move((-10,0)))
        self.bind_continuous_keypress(pg.K_RIGHT, lambda: camera.move((10,0)))
        self.bind_keypress(pg.K_r, camera.reset)

    def handle_mouse(self):
        mousepos = pg.mouse.get_pos()
        for button in self.buttons:
            if button.is_hovering(mousepos) and pg.mouse.get_pressed()[0]:
                button.press()

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key in self.keypress_bindings:
                print(f"key pressed: {event.key} > calling {self.keypress_bindings[event.key].__name__}")
                self.keypress_bindings[event.key]()
        elif event.type == pg.KEYUP:
            if event.key in self.keyrelease_bindings:
                print(f"key released: {event.key} > calling {self.keyrelease_bindings[event.key].__name__}")
                self.keyrelease_bindings[event.key]()
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button in self.mousebutton_bindings:
                self.mousebutton_bindings[event.button]()
        
    def handle_continuous_keypresses(self):
        keys = pg.key.get_pressed()
        for key, action in self.continuous_keypress_bindings.items():
            if keys[key]:
                action()

    def handle_continuous_mousebuttons(self):
        buttons = pg.mouse.get_pressed()
        for button, action in self.continuous_mousebutton_bindings.items():
            if buttons[button]:
                action()

    def update(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            self.handle_event(event)
        self.handle_mouse()
        self.handle_continuous_keypresses()
        self.handle_continuous_mousebuttons()
        return True
