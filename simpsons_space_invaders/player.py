"""Contains the generic character class,
and all things related to the player. 
"""
# External
import pygame
import os
from random import randint
from time import time
# Internal
import settings as s
from utils import Text

# Constants related to player
PLAYER_VEL = 6
ANGLE_INCREMENT = 2
SPACESHIP_WIDTH = s.HEIGHT // 14
SPACESHIP_HEIGHT = s.HEIGHT // 14

class Character(pygame.sprite.Sprite):
    """Generic class for all characters (player and enemies)."""

    def __init__(self, image: str, x_start, y_start, width, height, health):
        pygame.sprite.Sprite.__init__(self)
        # underlying rect behind the image.
        self.rect = pygame.Rect(x_start, y_start, width, height)
        self.image = pygame.transform.scale(pygame.image.load(image), (width, height))
        self.health = health
        self.x_center = self.rect.x + (width // 2) # The centre of the rect. 
        self.y_center = self.rect.y + (height // 2) # The centre of the rect. 

    def deplete_health(self, damage_taken: int):
        """Depletes the health attribute by an amount `damage_taken`."""
        self.health -= damage_taken

    def change_image(self, new_image):
        """Update the image of the character
        
        E.g. When the player or enemy is hit, you will want them to show blood,
        or explode. 

        Parameters
        ----------
        new_image : path
        """
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", new_image)),
            (self.rect.width, self.rect.height),
        )

    def explosion_image(self, width, height):
        """Draw out single frame of explosion."""
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "explosion.png")), (width, height)
        )
        self.explosion_rect = self.image.get_rect(center=self.rect.center)

    def rotate_image_randomly(self):
        """Rotate the enemy image to random angle"""
        self.image = pygame.transform.rotate(self.image, randint(0, 359))

    def mark_time(self):
        """Create a timestamp as an attribute."""
        self.timestamp = time()

class Player(Character):
    """Class for the player spaceship"""
    def __init__(self, *args):
        Character.__init__(
            self,
            os.path.join("assets", "spaceship_yellow.png"),
            s.WIDTH // 2,
            s.HEIGHT // 2,
            SPACESHIP_WIDTH,
            SPACESHIP_HEIGHT,
            100,
        )
        self.player_angle = 0
        self.player_deg = 0
        self.health_icon_rect = pygame.Rect(s.WIDTH * 0.15625,
                                            s.HEIGHT * 0.934,
                                            s.HEIGHT // 24,
                                            s.HEIGHT // 24)
        self.health_icon = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "health_icon.png")),
            (self.health_icon_rect.width, self.health_icon_rect.height),
        )
        self.lemon_power_active = False
        self.pepper_power_active = False
        self.cola_power_active = False
        self.pop_rock_power_active = False
        self.cola_bomb_power_active = False
        self.pop_rock_rect = pygame.Rect(s.WIDTH * 0.59375,
                                         s.HEIGHT * 0.934,
                                         s.HEIGHT // 23,
                                         s.HEIGHT // 19)
        self.pop_rock_image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "pop_rock.png")),
            (self.pop_rock_rect.width, self.pop_rock_rect.height),
        )
        self.cola_rect = pygame.Rect(s.WIDTH * 0.625,
                                     s.HEIGHT * 0.934,
                                     s.HEIGHT * 25,
                                     37.5)
        self.cola_image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "cola.png")),
            (self.cola_rect.width, self.cola_rect.height),
        )
        self.armed_text = Text(
            "stencil", 25, "ARMED", s.RED, s.WIDTH * 0.59125, s.HEIGHT * 0.906
        )

    def set_player_angle(self, keys_pressed) -> int:
        """Calculate the angle of the player image.
        Can be a pos or neg integer. 
        """
        if keys_pressed[pygame.K_LEFT]:
            self.player_angle += ANGLE_INCREMENT
        if keys_pressed[pygame.K_RIGHT]:
            self.player_angle -= ANGLE_INCREMENT

    def get_degrees(self) -> int:
        """Convert the player angle figure to actual correct degrees"""
        if self.player_angle >= 0:
            if self.player_angle >= 360:
                self.player_deg = self.player_angle - 360
            else:
                self.player_deg = self.player_angle
        else:  # if player_angle is neg
            if self.player_angle <= -360:
                self.player_deg = self.player_angle + 360
            else:
                self.player_deg = self.player_angle
            self.player_deg = self.player_deg + 360  # Convert it to positive.
        self.player_deg = 360 - self.player_deg  # mirror flip the value to be correct.

    def rotate_player(self):
        """Rotate the rect and image to the new player_angle"""
        self.rotated_image = pygame.transform.rotate(self.image, self.player_angle)
        new_rect = self.rotated_image.get_rect(
            center=self.image.get_rect(center=(self.x_center, self.y_center)).center
        )
        self.rect = new_rect

    def handle_movement(self, keys_pressed):
        """Move the player around the screen."""
        if keys_pressed[pygame.K_a] and self.rect.x - PLAYER_VEL > 0:  # LEFT
            self.rect.x -= PLAYER_VEL
        if (
            keys_pressed[pygame.K_d] and self.rect.x + PLAYER_VEL + self.rect.width < s.WIDTH
        ):  # RIGHT
            self.rect.x += PLAYER_VEL
        if keys_pressed[pygame.K_w] and self.rect.y - PLAYER_VEL > 0:  # UP
            self.rect.y -= PLAYER_VEL
        if (
            keys_pressed[pygame.K_s] and self.rect.y + PLAYER_VEL + self.rect.height < s.HEIGHT
        ):  # DOWN
            self.rect.y += PLAYER_VEL
        self.x_center = self.rect.x + (self.rect.width // 2)  # Update centre position.
        self.y_center = self.rect.y + (self.rect.height // 2)

    def rotate_180(self):
        """Rotate about 180 degrees if button pressed"""
        self.player_angle += 180

    def point_up(self):
        """Point player up"""
        self.player_angle = 0

    def draw_health_icon(self, surface_to_blit):
        """Draw the health icon."""
        surface_to_blit.blit(self.health_icon, self.health_icon_rect)

    def set_lemon_power(self, bool: bool):
        """Turn on or off lemon power."""
        self.lemon_power_active = bool
        if self.lemon_power_active == True:
            self.lemon_power_last_on_at = time()

    def set_pepper_power(self, bool: bool):
        """Turn on or off the pepper power."""
        self.pepper_power_active = bool
        if self.pepper_power_active == True:
            self.pepper_power_last_on_at = time()

    def set_cola_or_pop_rock_power(self, powerup_type, bool: bool):
        """Boolean if a cola or pop_rock powerup has been collected."""
        if powerup_type == "cola":
            self.cola_power_active = bool
        elif powerup_type == "pop_rock":
            self.pop_rock_power_active = bool
        else:
            raise ValueError("powerup_type invalid, has to be 'cola' or 'pop_rock'")
        if self.cola_power_active and self.pop_rock_power_active:
            self.cola_bomb_power_active = True
        else:
            self.cola_bomb_power_active = False

    def reset_cola_bomb_values(self):
        """Reset all values relating to the cola bomb back to false after throwing."""
        self.cola_power_active = False
        self.pop_rock_power_active = False
        self.cola_bomb_power_active = False

    def draw_cola_or_pop_rock(self):
        """Draw the icons for the collected items"""
        if self.cola_power_active:
            s.WIN.blit(self.cola_image, self.cola_rect)
        if self.pop_rock_power_active:
            s.WIN.blit(self.pop_rock_image, self.pop_rock_rect)
        if self.cola_bomb_power_active:
            self.armed_text.draw_text(s.WIN)