import pygame, os
import settings as s
from math import sin, cos, radians
from utils import play_sound

# Constants related to projectiles
BULLET_VEL = 20
DEFAULT_BULLET_DAMAGE = 1
BULLET_SIZE = 8
LEMON_BULLET_DAMAGE = 3
LEMON_BULLET_SIZE = 20
BULLET_TYPES = ["default", "player", "lemon", "cola_bomb", "pepper"]
PEPPER_BULLET_SIZE = 20
PEPPER_BULLET_DAMAGE = 1
COLA_BOMB_THROW_SPEED = 5
COLA_BOMB_EXPLOSION_SPEED = 7


class Bullet(pygame.sprite.Sprite):
    """Bullets can have an image, size, speed, direction, damage"""
    def __init__(
        self,
        x_start,
        y_start,
        angle_at_firing,
        width: int = BULLET_SIZE,
        height: int = BULLET_SIZE,
        damage: int = DEFAULT_BULLET_DAMAGE,
        bullet_type: str = "default",
        image: str = "default_bullet.png",
        play_sound_effect: bool = False,
    ):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(
            x_start - (width / 2),
            y_start - (height / 2),
            width,
            height,
        )
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", image)),
            (width, height)
        )
        self.damage = damage
        self.angle_at_firing = angle_at_firing
        # Validate the bullet_type
        if bullet_type in BULLET_TYPES:
            self.bullet_type = bullet_type
        else:
            raise ValueError(f"{bullet_type} not allowed in list: {BULLET_TYPES}")
        # Play bullet sound at init
        if play_sound_effect:
            play_sound("shooting", 0.1, 200, True)

    def move_bullet(self):
        self.rect.x += sin(radians(self.angle_at_firing)) * BULLET_VEL
        self.rect.y -= cos(radians(self.angle_at_firing)) * BULLET_VEL

    def draw_bullet(self, colour):
        """Draw the bullet rect"""
        pygame.draw.rect(s.WIN, colour, self.rect)
       
class LemonBullet(Bullet):
    """Specific Lemon bullet"""
    def __init__(self, x_start, y_start, angle_at_firing):
        Bullet.__init__(
            self,
            x_start,
            y_start,
            angle_at_firing,
            LEMON_BULLET_SIZE,
            LEMON_BULLET_SIZE,
            LEMON_BULLET_DAMAGE,
            "lemon",
            "lemon.png",
            play_sound_effect=True
        )
        
class PepperBullet(Bullet):
    """Specific bullet when pepper power is active."""
    def __init__(self, x_start, y_start, angle_at_firing):
        Bullet.__init__(
            self,
            x_start,
            y_start,
            angle_at_firing,     
            PEPPER_BULLET_SIZE,
            PEPPER_BULLET_SIZE,
            PEPPER_BULLET_DAMAGE,
            "pepper",
            "pepper_fire.png",
            play_sound_effect=False
        )

class ColaBomb(pygame.sprite.Sprite):
    """Cola Bomb that explodes all enemies"""
    X_START, Y_START = s.WIDTH, s.HEIGHT
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(
            self.X_START, self.Y_START, 40, 40
        )  # Starting point down by homer.
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "cola_bomb.png")),
            (self.rect.width, self.rect.height),
        )
        self.slope = (self.Y_START - (s.HEIGHT / 2)) / (self.X_START - (s.WIDTH / 2))
        play_sound("throw_colabomb", 0.8)
        self.explode = False
        self.exploding = False

    def move(self):
        """Movement for throwing the cola bomb, aims it to centre of screen"""
        if self.explode == False and self.exploding == False:
            self.rect.x -= COLA_BOMB_THROW_SPEED
            self.rect.y -= COLA_BOMB_THROW_SPEED * self.slope
            # When it hits the centre of the screen, explode. 
            if (self.rect.x <= s.WIDTH // 2) and (self.rect.y <= s.HEIGHT // 2):
                self.explode = True

    def draw_explosion(self, group):
        """Draw each frame of the explosion"""
        # First frame
        if self.explode == True:  
            self.rect.center = (s.WIDTH // 2, s.HEIGHT // 2)
            self.rect.width, self.rect.height = 10, 10
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("assets", "explosion.png")),
                (self.rect.width, self.rect.height),
            )
            self.explode = False
            self.exploding = True
            play_sound("explosion", 0.5, fadeout_ms=4000, fadeout=True)
        # Subsequent frames to grow the explosion
        if self.exploding:  
            self.rect.width += COLA_BOMB_EXPLOSION_SPEED
            self.rect.height += COLA_BOMB_EXPLOSION_SPEED
            self.rect.center = (s.WIDTH // 2, s.HEIGHT // 2)
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("assets", "explosion.png")),
                (self.rect.width, self.rect.height),
            )
            # When explosion gets big enough, kill all enemies on screen. 
            if self.rect.width >= 400:
                self.kill() # remove self from cola bomb group. 
                for enemy in group:
                    enemy.set_hit_by("cola_bomb")
                    enemy.health = 0

    
