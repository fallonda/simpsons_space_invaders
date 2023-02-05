from time import time
import pygame, os

# Constants related to overall gameplay. 
# Sizes are made relative to the overall HEIGHT (of the window). 
ASPECT_RATIO = 1.6
HEIGHT = 720
WIDTH = int(HEIGHT * ASPECT_RATIO)
FPS = 60
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
START_TIME = time()
SCREEN_TYPES = ["space", "pepper_trip"]
SMUG_FREQ = 10 # For every 10 scores give smug soundbite.  

# Set up window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Cadets: Lemon Defenders")  # Title of window.
SPACE = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "simpsons_space.jpg")),
    (WIDTH, HEIGHT)
)
PEPPER_LAND = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "pepper_land.png")),
    (WIDTH, HEIGHT)
)