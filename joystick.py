import math
import pygame as pg

class JoystickManager:
    def __init__(self):
        pg.joystick.init()
        self.joysticks = {}
        self.refresh_joysticks()
        
        self.deadzone = 0.5
        self.selected_button = None
        
        # Debouncing variables to prevent rapid-fire scrolling
        self.move_cooldown = 0
        self.COOLDOWN_MAX = 12  # frames to wait before moving again
        self.button_a_pressed = False

    def refresh_joysticks(self):
        self.joysticks = {}
        for i in range(pg.joystick.get_count()):
            joy = pg.joystick.Joystick(i)
            joy.init()
            self.joysticks[joy.get_instance_id()] = joy

    def update_menu(self, buttons: list):
        """
        Handles discrete spatial navigation between buttons.
        Pass in self.handler.buttons from your current screen.
        """
        if pg.joystick.get_count() != len(self.joysticks):
            self.refresh_joysticks()

        if not self.joysticks or not buttons:
            return

        # Ensure a button is always selected if the menu has buttons
        if self.selected_button not in buttons:
            self.selected_button = buttons[0]

        # Reset all highlighting, then highlight the selected one
        for b in buttons:
            b.is_selected = False
        self.selected_button.is_selected = True

        joy = list(self.joysticks.values())[0]  # Read player 1

        # 1. Handle Navigation
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        else:
            dx, dy = self._get_directional_input(joy)
            if dx != 0 or dy != 0:
                next_btn = self._find_next_button(self.selected_button, (dx, dy), buttons)
                if next_btn:
                    self.selected_button = next_btn
                    self.selected_button.is_selected = True
                self.move_cooldown = self.COOLDOWN_MAX

        # 2. Handle Clicking (Button 0 is 'A' / Cross)
        is_pressed = joy.get_button(0) | joy.get_button(1)
        is_disabled = getattr(self.selected_button, "disabled", False)

        if is_pressed and not self.button_a_pressed and not is_disabled:
            # Visually press the button (sets self.pressed = True)
            self.selected_button.press()
            self.button_a_pressed = True
            
        elif not is_pressed and self.button_a_pressed:
            # BUGFIX: Reset the tracker BEFORE calling release!
            # Otherwise, the callback's while-loop blocks this from ever resetting.
            self.button_a_pressed = False  
            
            # Now trigger the callback
            self.selected_button.release()

    def is_heating(self) -> bool:
        """For Level gameplay."""
        for joy in self.joysticks.values():
            if joy.get_numhats() > 0 and joy.get_hat(0)[1] == 1:
                return True
            if joy.get_axis(1) < -self.deadzone:
                return True
        return False

    def is_cooling(self) -> bool:
        """For Level gameplay."""
        for joy in self.joysticks.values():
            if joy.get_numhats() > 0 and joy.get_hat(0)[1] == -1:
                return True
            if joy.get_axis(1) > self.deadzone:
                return True
        return False
    
    def is_speedup(self) -> bool:
        """For Level gameplay."""
        joy = list(self.joysticks.values())[0]  # Read player 1
        dx, dy = self._get_directional_input(joy)
        if dx == 1:
            return True
            print("speedup!")
        return False
    
    def is_speeddown(self) -> bool:
        """For Level gameplay."""
        joy = list(self.joysticks.values())[0]  # Read player 1
        dx, dy = self._get_directional_input(joy)
        if dx == -1:
            return True
            print("speeddown!")
        return False

    # --- Private Helpers ---

    def _get_directional_input(self, joy) -> tuple[int, int]:
        """Returns a normalized vector (dx, dy) based on stick or D-pad."""
        dx, dy = 0, 0
        
        # Check D-Pad (Hats)
        if joy.get_numhats() > 0:
            dx, dy = joy.get_hat(0)
            dy = -dy  # Pygame hats are inverted on Y compared to screen coordinates
            
        # Check Analog Stick (if D-Pad wasn't pressed)
        if dx == 0 and dy == 0:
            axis_x, axis_y = joy.get_axis(0), joy.get_axis(1)
            if axis_x > self.deadzone: dx = 1
            elif axis_x < -self.deadzone: dx = -1
            
            if axis_y > self.deadzone: dy = 1
            elif axis_y < -self.deadzone: dy = -1
            
        return dx, dy

    def _find_next_button(self, current, direction: tuple[int, int], buttons: list):
        """Finds the closest button in the pushed direction using spatial scoring."""
        best_button = None
        min_score = float('inf')
        
        # CHANGED: current.pos -> current.position
        cx, cy = current.position[0], current.position[1]
        dx, dy = direction

        for b in buttons:
            if b == current:
                continue
            
            # CHANGED: b.pos -> b.position
            rel_x = b.position[0] - cx
            rel_y = b.position[1] - cy
            
            # Dot product checks if the button is physically in the direction we pushed
            dot_product = rel_x * dx + rel_y * dy
            
            if dot_product > 0:
                # Euclidean distance
                dist = math.hypot(rel_x, rel_y)
                # Orthogonal distance (penalize buttons that are off to the side)
                ortho = abs(rel_x * dy - rel_y * dx)
                
                # Combine distances (weighting orthogonal distance heavier to prefer straight lines)
                score = dist + (ortho * 2.0)
                
                if score < min_score:
                    min_score = score
                    best_button = b
                    
        return best_button