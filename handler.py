import pygame as pg

import settings

import music

class Button:
    def __init__(self, pos, callback, text="", size=settings.BUTTON_SIZE_DEFAULT):
        self.position = pos
        self.size = size
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.disabled = False
        self.is_selected = False

    def release(self):
        self.pressed = False
        self.callback()

    def press(self):
        self.pressed = True

    def is_hovering(self, mouse_pos):
        """Check if the mouse is over the button OR it is selected by the joystick."""
        x, y = self.position
        w, h = self.size
        
        # Check physical mouse collision
        mouse_hover = x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h
        
        # Merge mouse hover and joystick selection
        self.hovered = mouse_hover or self.is_selected
        
        # Ensure it doesn't stay pressed if the user moves off the button
        self.pressed = min(self.pressed, self.hovered)
        
        return self.hovered

class TextInput:
    def __init__(
        self,
        pos,
        size=(250, 40),
        placeholder="",
        text="",
        on_submit=None,
        max_length=32,
    ):
        self.position = pos
        self.size = size
        self.placeholder = placeholder
        self.text = text
        self.on_submit = on_submit  # callback taking (text)
        self.max_length = max_length

        self.hovered = False
        self.active = False
        self.cursor_pos = len(text)
        self._last_blink = 0
        self._cursor_visible = True

    def is_hovering(self, mouse_pos):
        x, y = self.position
        w, h = self.size
        self.hovered = x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h
        return self.hovered

    def focus(self):
        self.active = True
        self._last_blink = pg.time.get_ticks()
        self._cursor_visible = True

    def blur(self):
        self.active = False

    def insert_text(self, s: str):
        if not s:
            return
        if len(self.text) >= self.max_length:
            return
        # trim to not exceed max_length
        allowed = self.max_length - len(self.text)
        s = s[:allowed]
        self.text = self.text[: self.cursor_pos] + s + self.text[self.cursor_pos :]
        self.cursor_pos += len(s)

    def backspace(self):
        if self.cursor_pos > 0:
            self.text = self.text[: self.cursor_pos - 1] + self.text[self.cursor_pos :]
            self.cursor_pos -= 1

    def delete(self):
        if self.cursor_pos < len(self.text):
            self.text = self.text[: self.cursor_pos] + self.text[self.cursor_pos + 1 :]

    def move_cursor_left(self):
        if self.cursor_pos > 0:
            self.cursor_pos -= 1

    def move_cursor_right(self):
        if self.cursor_pos < len(self.text):
            self.cursor_pos += 1

    def move_home(self):
        self.cursor_pos = 0

    def move_end(self):
        self.cursor_pos = len(self.text)

    def submit(self):
        if self.on_submit:
            self.on_submit(self.text)

    def handle_keydown(self, event: pg.event.Event):
        # Returns True if handled (so outer handler doesn’t process it again)
        # if event.key == pg.K_RETURN:
        #     self.submit()
        #     return True
        if event.key == pg.K_BACKSPACE:
            self.backspace()
            return True
        if event.key == pg.K_DELETE:
            self.delete()
            return True
        if event.key == pg.K_LEFT:
            self.move_cursor_left()
            return True
        if event.key == pg.K_RIGHT:
            self.move_cursor_right()
            return True
        if event.key == pg.K_HOME:
            self.move_home()
            return True
        if event.key == pg.K_END:
            self.move_end()
            return True

        # text entry via unicode
        if event.unicode and event.unicode.isprintable():
            self.insert_text(event.unicode)
            return True

        # Simple paste support (Ctrl+V)
        if event.key == pg.K_v and (pg.key.get_mods() & pg.KMOD_CTRL):
            try:
                import pygame.scrap as scrap
                if not scrap.get_init():
                    scrap.init()
                clip = scrap.get("text/plain;charset=utf-8")
                if clip:
                    if isinstance(clip, bytes):
                        clip = clip.decode("utf-8", errors="ignore")
                    self.insert_text(clip)
                    return True
            except Exception:
                pass

        return False

    def update_cursor_blink(self, blink_ms=500):
        now = pg.time.get_ticks()
        if now - self._last_blink >= blink_ms:
            self._cursor_visible = not self._cursor_visible
            self._last_blink = now


class InputHandler(object):
    def __init__(self, music):
        self.keypress_bindings = {}
        self.keyrelease_bindings = {}
        self.continuous_keypress_bindings = {}
        self.mousebutton_bindings = {}
        self.continuous_mousebutton_bindings = {}
        self.joybutton_binds = {}
        self.joycombo_binds = {}
        self.music = music

        self.buttons = []
        self.inputs = []          # NEW
        self.active_input = None

    def register_button(self, button):
        """Register a button to be checked for clicks."""
        self.buttons.append(button)

    def register_input(self, text_input: TextInput):
        self.inputs.append(text_input)

    def focus_input(self, text_input: TextInput | None):
        if self.active_input and self.active_input is not text_input:
            self.active_input.blur()
        self.active_input = text_input
        if self.active_input:
            self.active_input.focus()

    def bind_keypress(self, key, action):
        self.keypress_bindings[key] = action

    def bind_keyrelease(self, key, action):
        self.keyrelease_bindings[key] = action

    def bind_continuous_keypress(self, key, action):
        self.continuous_keypress_bindings[key] = action

    def bind_mousebutton_down(self, button, action):
        """left mousebutton is button 0"""
        self.mousebutton_bindings[button] = action

    def bind_continuous_mousebutton(self, button, action):
        """left mousebutton is button 0"""
        self.continuous_mousebutton_bindings[button] = action
        
    def bind_joybutton(self, button_id: int, callback: callable) -> None:
        """Binds a specific joystick button ID to a callback function."""
        self.joybutton_binds[button_id] = callback

    def bind_joycombo(self, modifier_id: int, button_id: int, callback: callable) -> None:
        """
        Binds a combination of a held modifier button and a newly pressed button to a callback.
        Example: bind_joycombo(4, 7, quit_game) -> Hold LB (4) + Press Start (7)
        """
        self.joycombo_binds[(modifier_id, button_id)] = callback

    def bind_WASD_movement(self, mover, speed: float, turnspeed: float):
        self.bind_continuous_keypress(pg.K_w, lambda: mover.move_in_direction(speed))
        self.bind_continuous_keypress(pg.K_s, lambda: mover.move_in_direction(-speed))
        self.bind_continuous_keypress(pg.K_a, lambda: mover.turn(angle=turnspeed))
        self.bind_continuous_keypress(pg.K_d, lambda: mover.turn(angle=-turnspeed))

    def bind_camera(self, camera):
        self.bind_mousebutton_down(4, lambda: camera.zoom(1.1))
        self.bind_mousebutton_down(5, lambda: camera.zoom(0.9))
        self.bind_continuous_keypress(pg.K_UP, lambda: camera.move((0, 10)))
        self.bind_continuous_keypress(pg.K_DOWN, lambda: camera.move((0, -10)))
        self.bind_continuous_keypress(pg.K_LEFT, lambda: camera.move((-10, 0)))
        self.bind_continuous_keypress(pg.K_RIGHT, lambda: camera.move((10, 0)))
        self.bind_keypress(pg.K_r, camera.reset)

    def handle_mouse_movement(self):
        mousepos = pg.mouse.get_pos()
        for button in self.buttons:
            button.is_hovering(mousepos)
        for ti in self.inputs:
            ti.is_hovering(mousepos)  # just to update hover state

    def handle_mouse_down(self, event):
        if event.button in self.mousebutton_bindings:
            self.mousebutton_bindings[event.button]()

        # Inputs get focus first
        clicked_any_input = False
        for ti in self.inputs:
            if ti.is_hovering(pg.mouse.get_pos()):
                self.focus_input(ti)
                clicked_any_input = True
                break
        if not clicked_any_input:
            # blur active input if clicked outside
            if self.active_input:
                self.active_input.blur()
                self.active_input = None

        # Buttons: press only if clicked
        for button in self.buttons:
            if button.is_hovering(pg.mouse.get_pos()):
                self.music.button(volume=5)
                button.press()

    def handle_mouse_up(self, event):
        if event.button != 1:
            return
        for button in self.buttons:
            if button.is_hovering(pg.mouse.get_pos()):
                button.release()

    def handle_event(self, event: pg.event):
        if event.type == pg.KEYDOWN:
            # If an input is focused, let it consume the event
            if self.active_input:
                handled = self.active_input.handle_keydown(event)
                if handled:
                    return
            # otherwise, global bindings
            if event.key in self.keypress_bindings:
                print(f"key pressed: {event.key} > calling {self.keypress_bindings[event.key].__name__}")
                self.keypress_bindings[event.key]()
        elif event.type == pg.KEYUP:
            if event.key in self.keyrelease_bindings:
                print(f"key released: {event.key} > calling {self.keyrelease_bindings[event.key].__name__}")
                self.keyrelease_bindings[event.key]()
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.handle_mouse_down(event)
        elif event.type == pg.MOUSEBUTTONUP:
            self.handle_mouse_up(event)

        elif event.type == pg.JOYBUTTONDOWN:
            joy = pg.joystick.Joystick(event.instance_id)
            combo_triggered = False
            
            # 1. Check if this button press completes any registered combo
            for (mod_id, btn_id), action in self.joycombo_binds.items():
                if event.button == btn_id and joy.get_button(mod_id):
                    print(f"Combo triggered: {mod_id} + {btn_id} > calling {action.__name__}")
                    action()
                    combo_triggered = True
                    break  # Stop processing once a combo is fired
            
            # 2. If it wasn't a combo, check standard single-button bindings
            if not combo_triggered and event.button in self.joybutton_binds:
                print(f"joy button pressed: {event.button} > calling {self.joybutton_binds[event.button].__name__}")
                self.joybutton_binds[event.button]()

    def handle_continuous_keypresses(self):
        keys = pg.key.get_pressed()
        for key, action in self.continuous_keypress_bindings.items():
            if keys[key]:
                action()

    def handle_continuous_mousebuttons(self):
        buttons = (
            pg.mouse.get_pressed()
        )  # returns tuple of bools, in order of mouse button
        for button, action in self.continuous_mousebutton_bindings.items():
            if buttons[button]:
                action()

    def update(self):
        self.handle_mouse_movement()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            self.handle_event(event)
        self.handle_continuous_keypresses()
        self.handle_continuous_mousebuttons()
        # cursor blink update
        for ti in self.inputs:
            if ti.active:
                ti.update_cursor_blink()
        return True


