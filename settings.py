
SCREEN_RESOLUTION = (1200, 700)

FONT = "Helvetica"
GAME_ZOOM = (20, 20) # x, y
TEMP_WARNING_THRESHOLD = 0.2 # Kelvin lower than setpoint until warning shown
MONEY_WARNING_THRESHOLD = 200 # €
GODMODE = False
GAME_SPEED = 12 # sim hours / second

BUTTON_SIZE = {
    "Start New Game": (250,60),
    "Retry": (250,60),
    "Continue": (250,60),
    "Go to Shop": (150,60),
    "Start Level": (150,60),
    "150x60": (150,60),
}

SCREEN_ANCHORS = {  #width #height
    "top left":     (0.2, 0.07),
    "top right":    (0.8, 0.07),
    "bottom left":  (0.2, 0.9),
    "bottom center":(0.5, 0.9),
    "bottom right": (0.8, 0.9),
    "popup left":   (0.15, 0.8),
    "popup right":  (0.7, 0.8)
}