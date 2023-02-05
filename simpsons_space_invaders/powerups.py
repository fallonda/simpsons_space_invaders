import pygame, os
from random import randint
import settings as s
from utils import play_sound
from time import time

# Constants related to powerups 
POWERUP_TYPES = ["lemon", "beer", "donut", "pepper", "cola", "pop_rock"]
POWERUP_VOL = 0.5
POWERUP_DROP_SPEED = 2  # Falling speed of powerups.
LEMON_POWER_DUR = 10
HEALTH_POWERUP_AMOUNT = 20
PEPPER_POWER_DUR = 10


class Powerup(pygame.sprite.Sprite):
    """Generic class for power-up items"""
    def __init__(self, width, height, image, powerup_type):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(
            randint(0, (s.WIDTH - width)),  # x start
            0 - height,  # y start
            width,
            height,
        )
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", image)),
            (width, height)
        )
        # Validate powerup_type
        if powerup_type in POWERUP_TYPES:
            self.powerup_type = powerup_type
        else:
            raise ValueError(
                f"'{powerup_type}' is not in allowed list: {POWERUP_TYPES}"
            )
        if powerup_type in ["beer", "donut"]:
            self.add_health = HEALTH_POWERUP_AMOUNT
            
    def move_downwards(self):
        """Move the powerup down the screen"""
        self.rect.y += POWERUP_DROP_SPEED
        
    def play_powerup_sound(self):
        if self.powerup_type in ["lemon", "cola", "pop_rock"]:
            play_sound("powerup", POWERUP_VOL)
        elif self.powerup_type == "beer":
            play_sound("beer", POWERUP_VOL)
        elif self.powerup_type == "donut":
            play_sound("donut", POWERUP_VOL)
        elif self.powerup_type == "pepper":
            play_sound("pepper_trip", POWERUP_VOL)
            

class PowerupDropper():
    """Drops powerups, and records when the next one should be dropped."""
    def __init__(
        self,
        powerup_width,
        powerup_height,
        powerup_image,
        powerup_type, 
        earliest_time:int = 20,
        latest_time:int = 40,
    ):
        self.previous_time = s.START_TIME
        self.earliest_time = earliest_time
        self.latest_time = latest_time
        self.time_for_next_release = randint(self.earliest_time, self.latest_time)
        self.powerup_width = powerup_width
        self.powerup_height = powerup_height
        self.powerup_image = powerup_image
        self.powerup_type = powerup_type
        
    def release(self, group):
        """Check how long in seconds since the last release was."""
        self.time_since_last_release = time() - self.previous_time
        if self.time_since_last_release >= self.time_for_next_release:
            new_powerup = Powerup(
                self.powerup_width,
                self.powerup_height,
                self.powerup_image,
                self.powerup_type, 
            )
            group.add(new_powerup)
            self.previous_time = time() # Reset time of last release. 
            self.time_for_next_release = randint(self.earliest_time, self.latest_time) # Generate new random interval. 

