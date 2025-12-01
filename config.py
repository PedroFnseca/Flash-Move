SIM_TIME = 3600.0
FRAME_DT = 0.5
SEED = 42

INTERARRIVAL_MEAN = 15.0
MAX_QUEUE_FORGIVE = 20
ORDER_TTL = 600.0

PEAK_ENABLED = True
PEAK_DURATION = 120.0
PEAK_MULTIPLIER = 5

ACCIDENT_PROBABILITY = 0.0008 

NUM_COURIERS = 2
SERVICE_SPEED = 80.0

MAP_SIZE = (1400, 900)
SHOW_TRAILS = True
SHOW_SHADOWS = True
SHOW_PARTICLES = True
BACKGROUND_IMAGE = None
FPS = 60

COLORS = {
    'background': (15, 18, 25),
    'background_light': (25, 30, 40),
    'grid': (35, 40, 50),
    'grid_major': (50, 55, 70),
    'panel_bg': (30, 35, 45, 250),
    'panel_border': (100, 180, 255),
    'text': (240, 245, 255),
    'text_dim': (150, 160, 180),
    'accent': (100, 180, 255),
    'success': (50, 255, 150),
    'warning': (255, 200, 50),
    'danger': (255, 70, 110),
    'courier_idle': (50, 255, 150),
    'courier_to_pickup': (100, 180, 255),
    'courier_to_dropoff': (255, 120, 255),
    'order_new': (255, 220, 100),
    'order_waiting': (255, 160, 70),
    'order_urgent': (255, 70, 110),
    'courier_palette': [
        (50, 255, 150),
        (100, 180, 255),
        (255, 120, 255),
        (255, 220, 100),
        (80, 240, 240),
        (255, 140, 80),
        (200, 120, 255),
        (255, 100, 200),
    ],
    'shadow': (0, 0, 0, 100),
    'glow': (255, 255, 255, 40),
    'trail_alpha': 150,
}

ORDER_COLOR_THRESHOLDS = {
    'new': 30,
    'waiting': 100
}
