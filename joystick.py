import pygame as pg

class JoystickManager:
    def __init__(self):
        # Initialize the joystick module
        pg.joystick.init()
        self.joysticks = {}
        self.refresh_joysticks()
        
        # Deadzone prevents cursor drift from slight stick physical offsets
        self.deadzone = 0.2
        self.mouse_speed = 10
        
        # Initialize virtual mouse position
        info = pg.display.Info()
        if info.current_w > 0:
            self.v_mouse_x = info.current_w / 2
            self.v_mouse_y = info.current_h / 2
            pg.mouse.set_pos((int(self.v_mouse_x), int(self.v_mouse_y)))
        else:
            self.v_mouse_x, self.v_mouse_y = pg.mouse.get_pos()
        
        # State tracker to ensure single-click emulation
        self.button_a_pressed = False

    def refresh_joysticks(self):
        """Checks for connected/disconnected controllers."""
        self.joysticks = {}
        for i in range(pg.joystick.get_count()):
            joy = pg.joystick.Joystick(i)
            joy.init()
            self.joysticks[joy.get_instance_id()] = joy

    def update(self):
        """
        Handles navigation by mapping the stick to virtual mouse movement 
        and the 'A' button to left-clicks. Call this once per frame.
        """
        # Basic hotplugging support
        if pg.joystick.get_count() != len(self.joysticks):
            self.refresh_joysticks()

        for joy in self.joysticks.values():
            # 1. Free Cursor Movement (Axis 0 = X-axis, Axis 1 = Y-axis)
            dx = joy.get_axis(0)
            dy = joy.get_axis(1)
            
            if abs(dx) > self.deadzone or abs(dy) > self.deadzone:
                self.v_mouse_x += dx * self.mouse_speed
                self.v_mouse_y += dy * self.mouse_speed
                
                # Clamp cursor to the window boundaries
                info = pg.display.Info()
                self.v_mouse_x = max(0, min(self.v_mouse_x, info.current_w))
                self.v_mouse_y = max(0, min(self.v_mouse_y, info.current_h))
                
                pg.mouse.set_pos((int(self.v_mouse_x), int(self.v_mouse_y)))

            # 2. Emulate Clicking (Button 0 is usually 'A' on Xbox / 'Cross' on PlayStation)
            is_pressed = joy.get_button(0)
            if is_pressed and not self.button_a_pressed:
                # Send mouse-down to Pygame's event queue so your InputHandler catches it
                pg.event.post(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=pg.mouse.get_pos()))
                self.button_a_pressed = True
                
            elif not is_pressed and self.button_a_pressed:
                # Send mouse-up
                pg.event.post(pg.event.Event(pg.MOUSEBUTTONUP, button=1, pos=pg.mouse.get_pos()))
                self.button_a_pressed = False

    def is_heating(self) -> bool:
        """Returns True if D-pad UP or Left Stick is pushed UP."""
        for joy in self.joysticks.values():
            if joy.get_numhats() > 0 and joy.get_hat(0)[1] == 1:
                return True
            if joy.get_axis(1) < -0.5:
                return True
        return False

    def is_cooling(self) -> bool:
        """Returns True if D-pad DOWN or Left Stick is pushed DOWN."""
        for joy in self.joysticks.values():
            if joy.get_numhats() > 0 and joy.get_hat(0)[1] == -1:
                return True
            if joy.get_axis(1) > 0.5:
                return True
        return False