
DEBUG_MODE = False

SCREEN_RESOLUTION = (1280, 720)

FONT = "custom"
GAME_ZOOM = (20, 20)  # x, y

GODMODE = False
TEMP_WARNING_THRESHOLD = 0.2  # Kelvin lower than setpoint until warning shown
MONEY_WARNING_THRESHOLD = 200  # €
GAME_SPEED = 12  # sim hours / second

BUILDING_PATH = "building_bad.xlsx"
BACKGROUND_FOLDER = "bg_pixelart"  # "backgrounds"

UI_ANCHOR = (100, 250)
ANCHOR_SHOP_UPGRADE_TEXT = (48, 320)
ANCHOR_SHOP_UPGRADE_BUTTONS = (48, 320)
ANCHOR_SHOP_GAME_STATS = (880, -20)
ANCHOR_LEVEL_STATS = (20, 20)
ANCHOR_LEVEL_SPACING_X = 40 
ANCHOR_LEVEL_LINE_X = 0 
POS_REMAINING_HOURS = (500, 50)
POS_REMAINING_HOURS_VALUE = (700, 50)

BUTTON_BORDER_COLOR = (0,0,0)
BUTTON_SIZE = {
    "Start New Game": (250, 60),
    "Retry": (250, 60),
    "Continue": (250, 60),
    "Go to Shop": (150, 60),
    "Start Level": (150, 60),
    "150x60": (150, 60),
    "170x60": (200, 60),
}

SCREEN_ANCHORS = {  # width #height
    "top left": (0.2, 0.07),
    "top right": (0.8, 0.07),
    "bottom left": (0.08, 0.88),
    "bottom center": (0.42, 0.88),
    "bottom right": (0.74, 0.88),
    "popup left": (0.12, 0.78),
    "popup right": (0.70, 0.78),
}
