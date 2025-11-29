SIM_TIME = 3600.0
FRAME_DT = 0.5
SEED = 42

INTERARRIVAL_MEAN = 30.0
MAX_QUEUE_FORGIVE = 30
ORDER_TTL = 600.0

NUM_COURIERS = 2
SERVICE_SPEED = 80.0

MAP_SIZE = (1400, 900)
SHOW_TRAILS = True
SHOW_SHADOWS = True
SHOW_PARTICLES = True
BACKGROUND_IMAGE = None
FPS = 60

COLORS = {
    'background': (25, 28, 35),
    'background_light': (35, 38, 45),
    'grid': (45, 48, 55),
    'grid_major': (55, 58, 65),
    'panel_bg': (40, 43, 50, 240),
    'panel_border': (70, 150, 255),
    'text': (230, 235, 245),
    'text_dim': (160, 165, 175),
    'accent': (70, 150, 255),
    'success': (80, 250, 120),
    'warning': (255, 200, 60),
    'danger': (255, 80, 100),
    'courier_idle': (80, 250, 120),
    'courier_to_pickup': (70, 150, 255),
    'courier_to_dropoff': (255, 100, 255),
    'order_new': (255, 200, 60),
    'order_waiting': (255, 140, 60),
    'order_urgent': (255, 80, 100),
    'courier_palette': [
        (80, 250, 120),
        (70, 150, 255),
        (255, 100, 255),
        (255, 200, 60),
        (60, 230, 230),
        (255, 120, 60),
        (180, 100, 255),
        (255, 80, 200),
    ],
    'shadow': (0, 0, 0, 80),
    'glow': (255, 255, 255, 30),
    'trail_alpha': 120,
}

ORDER_COLOR_THRESHOLDS = {
    'new': 30,
    'waiting': 100
}
