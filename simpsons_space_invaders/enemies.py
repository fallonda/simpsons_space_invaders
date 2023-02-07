from simpsons_space_invaders.player import Character
import simpsons_space_invaders.settings as s
from time import time
import random, os
from math import hypot, ceil, floor


ENEMY_WIDTH = s.HEIGHT // 14
ENEMY_HEIGHT = s.HEIGHT // 9
ENEMY_CLASH_DAMAGE = 20
SPLATTER_TIME = 1.2  # Time in sec to keep splattered enemies on screen.

class Enemy(Character):
    """class for generic enemies"""

    def __init__(self, *args, enemy_vel:float = 1.0):
        Character.__init__(self, *args)
        self.enemy_vel = enemy_vel
        
    def move_towards(self, chase_x, chase_y):
        """Move towards the player.

        Parameters
        ----------
        chase_x : float
            The x position of the player to be chased. 
        chase_y : float
            The y position of the player to be chased. 
        """
        self.x_diff = (chase_x - self.rect.centerx)
        self.y_diff = (chase_y - self.rect.centery)
        # Calculate hypotenuse distance, and divide by it to get normalised unit vector. 
        self.direct_distance = hypot(self.x_diff, self.y_diff)
        self.x_move = self.x_diff/self.direct_distance * self.enemy_vel
        self.y_move = self.y_diff/self.direct_distance * self.enemy_vel
        # Round positive floats up and negative floats down. 
        if self.x_move > 0:
            self.x_move = ceil(self.x_move)
        elif self.x_move < 0:
            self.x_move = floor(self.x_move)
        if self.y_move > 0:
            self.y_move = ceil(self.y_move)
        elif self.y_move < 0:
            self.y_move = floor(self.y_move)
        # Move it
        self.rect.centerx += self.x_move
        self.rect.centery += self.y_move

    def kill_and_splat(self, new_image, rotate_randomly: bool):
        self.kill()
        self.change_image(new_image)
        if rotate_randomly:
            self.rotate_image_randomly()
        self.mark_time()

    def set_hit_by(self, bullet_type):
        """Record what bullet type last hit the enemy,
        so know what splat image to use"""
        self.hit_by = bullet_type
        

class EnemyDropper():
    """Drops enemies in from edge of screen,
    and keeps track of frequency."""        
    def __init__(
        self,
        enemy_freq:float = 2.5,
        enemy_vel:float = 1.0,
    ):
        self.enemy_freq = enemy_freq
        self.previous_time = s.START_TIME
        self.enemy_vel = enemy_vel
        self.top_counter = 70 # For increasing difficulty. 
    
    def random_enemy_start(self) -> tuple:
        """Return a random start position for releasing enemy."""
        left_margin = (-ENEMY_WIDTH, random.randrange(0, s.HEIGHT * 3 // 4))
        right_margin = (s.WIDTH, random.randrange(0, s.HEIGHT * 3 // 4))
        top_margin = (random.randrange(0, (s.WIDTH - ENEMY_WIDTH)), -ENEMY_HEIGHT)
        return random.choice([left_margin, right_margin, top_margin])
    
    def drop_enemy(self, group):
        """Drop a new enemy onto the screen."""
        time_since_last_added = time() - self.previous_time
        if time_since_last_added >= self.enemy_freq:
            enemy_start_pos = self.random_enemy_start()
            new_enemy = Enemy(
                os.path.join("assets", "kang_transparent.png"),
                enemy_start_pos[0], # width start point
                enemy_start_pos[1], # height start point
                ENEMY_WIDTH,
                ENEMY_HEIGHT,
                3,  # enemy health.
                enemy_vel = self.enemy_vel,
            )
            group.add(new_enemy)  
            self.previous_time = time()
        
    def increase_difficulty(self, score):
        """Increase the frequency of enemy drops as score increases."""
        if (score >= 10) & (score < 20):
            self.enemy_freq = 2
            self.enemy_vel = 1.1
        elif (score >= 20) & (score < 30):
            self.enemy_freq = 1.5
        elif (score >= 30) & (score < 50):
            self.enemy_freq = 1
        elif (score >= 50) & (score < 70):
            self.enemy_vel = 1.2
        elif score >= 70:
            # Slowly increase freq and speed for every 10 scored above 70.
            score_from_top = score - self.top_counter
            if score_from_top >= 10:
                self.top_counter += 10
                self.enemy_vel += 0.02
                self.enemy_freq -= 0.02
                
            
                
    
            




    
    
