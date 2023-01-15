# Sounds taken from https://www.wavsource.com/.
# Images taken from google.

# Packages and modules
from numpy import sqrt
import pygame, os, random, time
from math import sin, cos, radians

pygame.init()

# Set parent directory.
os.chdir("/home/pi/repos/simpsons_space_invaders")

# Constants
ASPECT_RATIO = 1.6
HEIGHT = 720
WIDTH = int(HEIGHT * ASPECT_RATIO)
FPS = 60
VEL = 6
BULLET_VEL = 20
DEFAULT_BULLET_DAMAGE = 1
BULLET_SIZE = 8
ANGLE_INCREMENT = 2
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ENEMY_VEL = 1
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 50, 50
START_TIME = time.time()
ENEMY_FREQ = 2.5  # time in sec to add enemies to the screen.
ENEMY_WIDTH, ENEMY_HEIGHT = 50, 80
ENEMY_CLASH_DAMAGE = 20
SPLATTER_TIME = 2.0  # Time in sec to keep splattered enemies on screen.
POWERUP_DROP_SPEED = 2  # Falling speed of powerups.
LEMON_DROP_FREQ = random.randint(20, 40)  # Also changes in function!
POWERUP_TYPES = ["lemon", "beer", "donut", "pepper", "cola", "pop_rock"]
SCREEN_TYPES = ["space", "pepper_trip"]
LEMON_POWER_DUR = 10
POWERUP_VOL = 0.5
LEMON_BULLET_DAMAGE = 3
LEMON_BULLET_SIZE = 20
BULLET_TYPES = ["default", "player", "lemon", "cola_bomb", "pepper"]
SMUG_FREQ = 7
HEALTH_POWERUP_TYPES = ["beer", "donut"]
HEALTH_POWERUP_AMOUNT = 20
HEALTH_DROP_FREQ = random.randint(20, 40)  # Also changes in function!
PEPPER_DROP_FREQ = random.randint(60, 80)  # Also changes in function!
PEPPER_POWER_DUR = 10
PEPPER_BULLET_SIZE = 20
PEPPER_BULLET_DAMAGE = 1
LAST_COLA_OR_POP_DROPPED = "pop_rock"
COLA_POP_FREQ = random.randint(30, 45)  # Also changes in function!
COLA_BOMB_THROW_SPEED = 5
COLA_BOMB_EXPLOSION_SPEED = 7

# Set up window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Cadets: Lemon Defenders")  # Title of window.
SPACE = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "simpsons_space.jpg")), (WIDTH, HEIGHT)
)
PEPPER_LAND = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "pepper_land.png")), (WIDTH, HEIGHT)
)

# Classes
class Character(pygame.sprite.Sprite):
    """class for all characters"""

    def __init__(self, image: str, x_start, y_start, width, height, health):
        pygame.sprite.Sprite.__init__(self)
        # underlying rect behind the image.
        self.rect = pygame.Rect(x_start, y_start, width, height)
        self.image = pygame.transform.scale(pygame.image.load(image), (width, height))
        self.health = health
        self.x_center = self.rect.x + (width // 2)
        self.y_center = self.rect.y + (height // 2)

    def deplete_health(self, damage_taken):
        self.health -= damage_taken

    def change_image(self, new_image):
        """Update the image of the enemy"""
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", new_image)),
            (self.rect.width, self.rect.height),
        )

    def explosion_image(self, width, height):
        """Draw out single frame of explosion"""
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "explosion.png")), (width, height)
        )
        self.explosion_rect = self.image.get_rect(center=self.rect.center)

    def rotate_image_randomly(self):
        """Rotate the enemy image to random angle"""
        self.image = pygame.transform.rotate(self.image, random.randint(0, 359))

    def mark_time(self):
        "Create a timestamp as an attribute"
        self.timestamp = time.time()


class Player(Character):
    def __init__(self, *args):
        Character.__init__(self, *args)
        self.player_angle = 0
        self.player_deg = 0
        self.health_icon_rect = pygame.Rect(WIDTH * 0.15625, HEIGHT * 0.934, 30, 30)
        self.health_icon = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "health_icon.png")),
            (self.health_icon_rect.width, self.health_icon_rect.height),
        )
        self.lemon_power_active = False
        self.pepper_power_active = False
        self.cola_power_active = False
        self.pop_rock_power_active = False
        self.cola_bomb_power_active = False
        self.pop_rock_rect = pygame.Rect(WIDTH * 0.59375, HEIGHT * 0.934, 31, 37.5)
        self.pop_rock_image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "pop_rock.png")),
            (self.pop_rock_rect.width, self.pop_rock_rect.height),
        )
        self.cola_rect = pygame.Rect(WIDTH * 0.625, HEIGHT * 0.934, 25, 37.5)
        self.cola_image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "cola.png")),
            (self.cola_rect.width, self.cola_rect.height),
        )
        self.armed_text = Text(
            "stencil", 25, "ARMED", RED, WIDTH * 0.59125, HEIGHT * 0.906
        )

    def set_player_angle(self, keys_pressed) -> int:
        """Calculate the angle of the player image.
        Can be a pos or neg integer"""
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
        """Move the player around the screen"""
        if keys_pressed[pygame.K_a] and self.rect.x - VEL > 0:  # LEFT
            self.rect.x -= VEL
        if (
            keys_pressed[pygame.K_d] and self.rect.x + VEL + self.rect.width < WIDTH
        ):  # RIGHT
            self.rect.x += VEL
        if keys_pressed[pygame.K_w] and self.rect.y - VEL > 0:  # UP
            self.rect.y -= VEL
        if (
            keys_pressed[pygame.K_s] and self.rect.y + VEL + self.rect.height < HEIGHT
        ):  # DOWN
            self.rect.y += VEL
        self.x_center = self.rect.x + (self.rect.width // 2)  # Update centre position.
        self.y_center = self.rect.y + (self.rect.height // 2)

    def rotate_180(self):
        """Rotate about 180 degrees if button pressed"""
        self.player_angle += 180

    def point_up(self):
        """Point player up"""
        self.player_angle = 0

    def draw_health_icon(self, surface_to_blit):
        """Draw the health icon"""
        surface_to_blit.blit(self.health_icon, self.health_icon_rect)

    def set_lemon_power(self, bool: bool):
        """Turn on or off lemon power"""
        self.lemon_power_active = bool
        if self.lemon_power_active == True:
            self.lemon_power_last_on_at = time.time()

    def set_pepper_power(self, bool: bool):
        """Turn on or off the pepper power"""
        self.pepper_power_active = bool
        if self.pepper_power_active == True:
            self.pepper_power_last_on_at = time.time()

    def set_cola_or_pop_rock_power(self, powerup_type, bool: bool):
        """Boolean if a cola or pop_rock powerup has been collected"""
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
        """Reset all values relating to the cola bomb back to false"""
        self.cola_power_active = False
        self.pop_rock_power_active = False
        self.cola_bomb_power_active = False

    def draw_cola_or_pop_rock(self):
        """Draw the icons for the collected items"""
        if self.cola_power_active:
            WIN.blit(self.cola_image, self.cola_rect)
        if self.pop_rock_power_active:
            WIN.blit(self.pop_rock_image, self.pop_rock_rect)
        if self.cola_bomb_power_active:
            self.armed_text.draw_text(WIN)


class Enemy(Character):
    """class for generic enemies"""

    def __init__(self, *args):
        Character.__init__(self, *args)

    def move_towards(self, chase_x, chase_y):
        """Chase the player"""
        x_diff = chase_x - self.rect.centerx
        y_diff = chase_y - self.rect.centery
        if x_diff < -1:
            self.rect.x -= ENEMY_VEL  # Move x by 1 and it's sign.
        elif x_diff > 1:
            self.rect.x += ENEMY_VEL  # Move x by 1 and it's sign.
        else:
            self.rect.x = self.rect.x  # Don't move if diff is zero.
        if y_diff < -1:
            self.rect.y -= ENEMY_VEL
        elif y_diff > 1:
            self.rect.y += ENEMY_VEL
        else:
            self.rect.y = self.rect.y

    def kill_and_splat(self, new_image, rotate_randomly: bool):
        self.kill()
        self.change_image(new_image)
        if rotate_randomly:
            self.rotate_image_randomly()
        self.mark_time()

    def set_hit_by(self, bullet_type):
        """Record what bullet type last hit the enemy"""
        if bullet_type in BULLET_TYPES:
            self.hit_by = bullet_type
        else:
            raise ValueError(f"{bullet_type} not allowed in list: {BULLET_TYPES}")


class Bullet(pygame.sprite.Sprite):
    """Bullets can have an image, size, speed, direction, damage"""

    def __init__(
        self,
        x_start,
        y_start,
        width,
        height,
        damage,
        angle_at_firing,
        bullet_type,
        image,
    ):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(
            x_start - (width / 2), y_start - (height / 2), width, height
        )
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", image)), (width, height)
        )
        self.damage = damage
        self.angle_at_firing = angle_at_firing
        if bullet_type in BULLET_TYPES:
            self.bullet_type = bullet_type
        else:
            raise ValueError(f"{bullet_type} not allowed in list: {BULLET_TYPES}")

    def move_bullet(self, bullet_speed):
        self.rect.x += sin(radians(self.angle_at_firing)) * bullet_speed
        self.rect.y -= cos(radians(self.angle_at_firing)) * bullet_speed

    def draw_bullet(self, colour):
        """Draw the bullet rect"""
        pygame.draw.rect(WIN, colour, self.rect)


class Text:
    def __init__(self, font, size, text, colour, x, y):
        self.font_path = pygame.font.match_font(font)
        self.font = pygame.font.Font(self.font_path, size)
        self.text = self.font.render(text, True, colour, None)
        self.rect = self.text.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update_text(self, new_text, colour):
        self.text = self.font.render(new_text, True, colour, None)

    def draw_text(self, surface_to_blit):
        """Draw the text to a surface"""
        surface_to_blit.blit(self.text, self.rect)


class Powerup(pygame.sprite.Sprite):
    """Generic class for power-up items"""

    def __init__(self, width, height, image, powerup_type):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(
            random.randint(0, (WIDTH - width)),  # x start
            0 - height,  # y start
            width,
            height,
        )
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", image)), (width, height)
        )
        if powerup_type in POWERUP_TYPES:
            self.powerup_type = powerup_type
        else:
            raise ValueError(
                f"'{powerup_type}' is not in allowed list: {POWERUP_TYPES}"
            )

    def move_downwards(self):
        """Move the powerup down the screen"""
        self.rect.y += POWERUP_DROP_SPEED


class ColaBomb(pygame.sprite.Sprite):
    """Cola Bomb that explodes all enemies"""

    x_start, y_start = 1430, 850

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(
            self.x_start, self.y_start, 40, 40
        )  # Starting point down by homer.
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "cola_bomb.png")),
            (self.rect.width, self.rect.height),
        )
        self.slope = (self.y_start - (HEIGHT / 2)) / (self.x_start - (WIDTH / 2))
        self.explode = False
        self.exploding = False

    def move(self):
        """Movement for throwing the cola bomb, aims it to centre of screen"""
        if self.explode == False and self.exploding == False:
            self.rect.x -= COLA_BOMB_THROW_SPEED
            self.rect.y -= COLA_BOMB_THROW_SPEED * self.slope
            if (self.rect.x <= WIDTH / 2) and (self.rect.y <= HEIGHT / 2):
                self.explode = True

    def draw_explosion(self):
        """Draw each frame of the explosion"""
        if self.explode == True:  # First frame
            self.rect.center = (WIDTH / 2, HEIGHT / 2)
            self.rect.width, self.rect.height = 10, 10
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("assets", "explosion.png")),
                (self.rect.width, self.rect.height),
            )
            self.explode = False
            self.exploding = True
            play_sound("explosion", 0.5, fadeout_ms=4000, fadeout=True)
        if self.exploding:  # Subsequent frames to grow the explosion
            self.rect.width += COLA_BOMB_EXPLOSION_SPEED
            self.rect.height += COLA_BOMB_EXPLOSION_SPEED
            self.rect.center = (WIDTH / 2, HEIGHT / 2)
            self.image = pygame.transform.scale(
                pygame.image.load(os.path.join("assets", "explosion.png")),
                (self.rect.width, self.rect.height),
            )
            if self.rect.width >= 400:
                self.kill()
                kill_all_enemies("cola_bomb")


# Groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemies_killed_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()
colabomb_group = pygame.sprite.Group()

# ----------
# Functions
# ----------
# Drop lemons
time_last_lemon_drop_added = START_TIME  # Initialise time zero


def add_lemon_powerup(previous_time):
    """Add a powerup to fall down screen"""
    time_since_last_lemon_added = time.time() - previous_time
    global LEMON_DROP_FREQ
    if time_since_last_lemon_added >= LEMON_DROP_FREQ:
        new_lemon_drop = Powerup(40, 25, "lemon.png", "lemon")
        powerup_group.add(new_lemon_drop)
        LEMON_DROP_FREQ = random.randint(20, 40)  # Generate new random interval
        global time_last_lemon_drop_added  # Update time of last lemon drop
        time_last_lemon_drop_added = time.time()


# Drop health powerup
time_last_health_powerup_added = START_TIME


def add_health_powerup(previous_time):
    """Add a donut or beer as a health powerup"""
    time_since_last_health_added = time.time() - previous_time
    global HEALTH_DROP_FREQ
    if time_since_last_health_added >= HEALTH_DROP_FREQ:
        rand_choice = random.choice(HEALTH_POWERUP_TYPES)
        if rand_choice == "beer":
            new_health_drop = Powerup(50, 50, "beer.png", "beer")
        elif rand_choice == "donut":
            new_health_drop = Powerup(40, 40, "donut.png", "donut")
        else:
            raise ValueError(f"health_powerup_type not valid.")
        HEALTH_DROP_FREQ = random.randint(20, 40)  # Generate new random interval
        powerup_group.add(new_health_drop)
        global time_last_health_powerup_added
        time_last_health_powerup_added = time.time()


# Drop pepper
time_last_pepper_added = START_TIME


def add_pepper(previous_time):
    """Add a chili pepper that will flip the background"""
    time_since_last_pepper_added = time.time() - previous_time
    global PEPPER_DROP_FREQ
    if time_since_last_pepper_added >= PEPPER_DROP_FREQ:
        new_pepper_drop = Powerup(20, 40, "pepper.png", "pepper")
        powerup_group.add(new_pepper_drop)
        PEPPER_DROP_FREQ = random.randint(60, 80)
        global time_last_pepper_added
        time_last_pepper_added = time.time()


# Drop cola and pop rocks
time_last_cola_or_pop_added = START_TIME


def add_cola_or_pop(previous_time):
    """Add either cola or pop rocks in alternating fashion"""
    time_since_last_cola_or_pop_added = time.time() - previous_time
    global COLA_POP_FREQ
    global LAST_COLA_OR_POP_DROPPED
    if time_since_last_cola_or_pop_added >= COLA_POP_FREQ:
        if LAST_COLA_OR_POP_DROPPED == "pop_rock":
            new_cola_or_pop_drop = Powerup(25, 37.5, "cola.png", "cola")
            LAST_COLA_OR_POP_DROPPED = "cola"
        else:
            new_cola_or_pop_drop = Powerup(31, 37.5, "pop_rock.png", "pop_rock")
            LAST_COLA_OR_POP_DROPPED = "pop_rock"
        powerup_group.add(new_cola_or_pop_drop)
        COLA_POP_FREQ = random.randint(30, 45)
        global time_last_cola_or_pop_added
        time_last_cola_or_pop_added = time.time()


# Release enemies
time_last_enemy_added = START_TIME


def add_enemy(previous_time):
    """Add an enemy to the screen given a time frequency in seconds"""
    time_since_last_enemy_added = time.time() - previous_time
    enemy_start_pos = random_enemy_start()
    if time_since_last_enemy_added >= ENEMY_FREQ:
        new_enemy = Enemy(
            os.path.join("assets", "kang_transparent.png"),
            enemy_start_pos[0],
            enemy_start_pos[1],
            ENEMY_WIDTH,
            ENEMY_HEIGHT,
            3,  # enemy health.
        )
        enemy_group.add(new_enemy)
        global time_last_enemy_added  # Update the time_last_enemy_added.
        time_last_enemy_added = time.time()


def random_enemy_start():
    left_margin = (-ENEMY_WIDTH, random.randrange(0, HEIGHT * 3 / 4))
    right_margin = (WIDTH, random.randrange(0, HEIGHT * 3 / 4))
    top_margin = (random.randrange(0, (WIDTH - ENEMY_WIDTH)), -ENEMY_HEIGHT)
    return random.choice([left_margin, right_margin, top_margin])


def play_sound(folder, volume, fadeout_ms=None, fadeout: bool = False):
    """Play random sound from folder"""
    path = os.path.join("assets", "sounds", folder)
    list_of_sounds = os.listdir(path)
    sound = pygame.mixer.Sound(os.path.join(path, random.choice(list_of_sounds)))
    sound.set_volume(volume)  # Between 0.0 and 1.0.
    sound.play()
    if fadeout:
        sound.fadeout(fadeout_ms)


def kill_all_enemies(bullet_type):
    """Wipe out all enemies on screen (e.g. with colabomb)"""
    for enemy in enemy_group:
        enemy.set_hit_by(bullet_type)
        enemy.health = 0


# Main game function
def main():
    clock = pygame.time.Clock()
    global ENEMY_VEL, ENEMY_FREQ, LEMON_DROP_FREQ, HEALTH_DROP_FREQ
    player = Player(
        os.path.join("assets", "spaceship_yellow.png"),
        WIDTH // 2,
        HEIGHT // 2,
        SPACESHIP_WIDTH,
        SPACESHIP_HEIGHT,
        100,
    )
    score = 0
    score_text = Text(
        "arial_bold", 30, f"Score: {score}", WHITE, WIDTH * 0.025, HEIGHT * 0.94
    )
    player_health_text = Text(
        "arial_bold", 30, f"{player.health}%", WHITE, WIDTH * 0.178, HEIGHT * 0.94
    )
    played_smug_sound = False

    # Game loop
    running = True
    while running:
        clock.tick(FPS)
        # Handling
        for event in pygame.event.get():

            # Check for window close.
            if event.type == pygame.QUIT:
                running = False

            # Bullet events (make a new bullet)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.get_degrees()
                    if player.lemon_power_active:  # Lemon bullet
                        bullet = Bullet(
                            player.x_center,
                            player.y_center,
                            LEMON_BULLET_SIZE,
                            LEMON_BULLET_SIZE,
                            LEMON_BULLET_DAMAGE,
                            player.player_deg,
                            "lemon",
                            "lemon.png",
                        )
                        play_sound("shooting", 0.1, 200, True)
                        bullet_group.add(bullet)
                    elif player.pepper_power_active:  # pepper bullet
                        bullet1 = Bullet(
                            player.x_center,
                            player.y_center,
                            PEPPER_BULLET_SIZE,
                            PEPPER_BULLET_SIZE,
                            PEPPER_BULLET_DAMAGE,
                            player.player_deg - 10,
                            "pepper",
                            "pepper_fire.png",
                        )
                        bullet2 = Bullet(
                            player.x_center,
                            player.y_center,
                            PEPPER_BULLET_SIZE,
                            PEPPER_BULLET_SIZE,
                            PEPPER_BULLET_DAMAGE,
                            player.player_deg,
                            "pepper",
                            "pepper_fire.png",
                        )
                        bullet3 = Bullet(
                            player.x_center,
                            player.y_center,
                            PEPPER_BULLET_SIZE,
                            PEPPER_BULLET_SIZE,
                            PEPPER_BULLET_DAMAGE,
                            player.player_deg + 10,
                            "pepper",
                            "pepper_fire.png",
                        )
                        bullet_group.add([bullet1, bullet2, bullet3])
                        play_sound("shooting_fire", 0.2)
                    else:  # normal bullet
                        bullet = Bullet(
                            player.x_center,
                            player.y_center,
                            BULLET_SIZE,
                            BULLET_SIZE,
                            DEFAULT_BULLET_DAMAGE,
                            player.player_deg,
                            "default",
                            "default_bullet.png",
                        )
                        play_sound("shooting", 0.1, 200, True)
                        bullet_group.add(bullet)

                if event.key == pygame.K_RETURN:
                    if player.cola_bomb_power_active:
                        colabomb_group.add(ColaBomb())
                        play_sound("throw_colabomb", 0.8)
                        player.reset_cola_bomb_values()

                # Rotate player by 180 deg
                if event.key == pygame.K_DOWN:
                    player.rotate_180()
                if event.key == pygame.K_UP:
                    player.point_up()

        # Spaceship movement
        keys_pressed = pygame.key.get_pressed()  # Check what keys are being pressed.
        player.handle_movement(keys_pressed)
        player.set_player_angle(keys_pressed)
        player.rotate_player()

        # enemy movement
        for enemy in enemy_group:
            enemy.move_towards(player.x_center, player.y_center)
        for bullet in bullet_group:
            bullet.move_bullet(BULLET_VEL)
            # Remove bullets that go off-screen.
            if (
                bullet.rect.x < 0
                or bullet.rect.x > WIDTH
                or bullet.rect.y < 0
                or bullet.rect.y > HEIGHT
            ):
                bullet.kill()

        # Bullet hitting enemies
        for enemy in enemy_group:
            # Remove the bullets if they hit an enemy
            for bullet in bullet_group:
                if pygame.sprite.collide_rect(bullet, enemy):
                    bullet.kill()  # Remove the bullet if it hit an enemy
                    enemy.deplete_health(bullet.damage)  # Deplete health of hit enemy.
                    enemy.set_hit_by(bullet.bullet_type)
            # Check if enemies hit player
            if pygame.sprite.collide_rect(enemy, player):
                enemy.health = 0
                enemy.set_hit_by("player")
                player.deplete_health(ENEMY_CLASH_DAMAGE)
                play_sound("player_hit", 0.4)
                score -= 1
            # Change the enemy after all bullet hits.
            if enemy.health == 2:
                enemy.change_image("kang_one_hit.png")
            elif enemy.health == 1:
                enemy.change_image("kang_two_hits.png")
            elif enemy.health <= 0:
                if enemy.hit_by == "lemon":
                    enemy.kill_and_splat("kang_lemon_face.png", rotate_randomly=False)
                elif enemy.hit_by in ["default", "player"]:
                    enemy.kill_and_splat("kang_splatted.png", rotate_randomly=True)
                elif enemy.hit_by == "pepper":
                    enemy.kill_and_splat("kang_on_fire.png", rotate_randomly=False)
                elif enemy.hit_by == "cola_bomb":
                    enemy.kill_and_splat("explosion.png", rotate_randomly=True)
                else:
                    raise ValueError(f"enemy.hit_by value '{enemy.hit_by}' not valid.")
                enemies_killed_group.add(enemy)  # Transfer enemy to killed group.
                play_sound("kang_kill", 0.3)
                score += 1

        # Remove splattered enemies
        for enemy in enemies_killed_group:
            if (time.time() - enemy.timestamp) >= SPLATTER_TIME:
                enemy.kill()

        # powerup drop movement
        for powerup in powerup_group:
            powerup.move_downwards()
            # remove powerups when they hit the bottom of the screen
            if powerup.rect.bottom >= HEIGHT:
                powerup.kill()
            # Check if collected by player
            if pygame.sprite.collide_rect(powerup, player):
                if powerup.powerup_type == "lemon":
                    play_sound("powerup", POWERUP_VOL)
                    player.set_lemon_power(True)
                elif powerup.powerup_type == "donut":
                    play_sound("donut", POWERUP_VOL)
                    player.health += HEALTH_POWERUP_AMOUNT
                elif powerup.powerup_type == "beer":
                    play_sound("beer", POWERUP_VOL)
                    player.health += HEALTH_POWERUP_AMOUNT
                elif powerup.powerup_type == "pepper":
                    play_sound("pepper_trip", POWERUP_VOL)
                    player.set_pepper_power(True)
                elif powerup.powerup_type == "cola":
                    play_sound("powerup", POWERUP_VOL)
                    player.set_cola_or_pop_rock_power("cola", True)
                elif powerup.powerup_type == "pop_rock":
                    play_sound("powerup", POWERUP_VOL)
                    player.set_cola_or_pop_rock_power("pop_rock", True)
                else:
                    raise ValueError(
                        f"powerup.powerup_type '{powerup.powerup_type}', needs to be one of {POWERUP_TYPES}"
                    )
                powerup.kill()  # Remove powerup from screen.

        # Move colabomb
        for colabomb in colabomb_group:
            colabomb.move()
            colabomb.draw_explosion()

        # Turn off expired powerups
        if player.lemon_power_active:
            time_lemon_on = time.time() - player.lemon_power_last_on_at
            lemon_time_remaining = round(LEMON_POWER_DUR - time_lemon_on)
            lemon_text = Text(
                "arial_bold",
                30,
                f"Lemon power remaining: {lemon_time_remaining} s",
                WHITE,
                WIDTH * 0.5,
                HEIGHT * 0.94,
            )
            if (time_lemon_on) >= LEMON_POWER_DUR:
                player.set_lemon_power(False)

        if player.pepper_power_active:
            time_pepper_on = time.time() - player.pepper_power_last_on_at
            pepper_time_remaining = round(PEPPER_POWER_DUR - time_pepper_on)
            pepper_text = Text(
                "arial_bold",
                30,
                f"Pepper trip remaining: {pepper_time_remaining} s",
                WHITE,
                WIDTH * 0.5,
                HEIGHT * 0.97,
            )
            if (time_pepper_on) >= PEPPER_POWER_DUR:
                player.set_pepper_power(False)

        if (
            player.cola_power_active
            or player.pop_rock_power_active
            or player.cola_bomb_power_active
        ):
            player.draw_cola_or_pop_rock()

        # drawing section
        if player.pepper_power_active:
            WIN.blit(PEPPER_LAND, (0, 0))
            pepper_text.draw_text(WIN)
        else:
            WIN.blit(SPACE, (0, 0))
        score_text.update_text(f"Score: {score}", WHITE)
        score_text.draw_text(WIN)
        player_health_text.update_text(f"{player.health}%", WHITE)
        player_health_text.draw_text(WIN)
        if player.lemon_power_active:
            lemon_text.draw_text(WIN)
        player.draw_health_icon(WIN)
        WIN.blit(player.rotated_image, player.rect)
        bullet_group.draw(WIN)
        add_enemy(time_last_enemy_added)
        enemy_group.draw(WIN)
        add_lemon_powerup(time_last_lemon_drop_added)
        add_pepper(time_last_pepper_added)
        add_health_powerup(time_last_health_powerup_added)
        add_cola_or_pop(time_last_cola_or_pop_added)
        player.draw_cola_or_pop_rock()
        colabomb_group.draw(WIN)
        powerup_group.draw(WIN)
        enemies_killed_group.draw(WIN)
        pygame.display.update()

        # Smug winning sound (ensures plays only once every 5 scores)
        if (
            score >= SMUG_FREQ
            and (score % SMUG_FREQ == 0)
            and (player.health > 0)
            and not played_smug_sound
        ):  # Every 5 scores.
            play_sound("player_smug", 1.0)
            played_smug_sound = True
        if score >= SMUG_FREQ and (score % SMUG_FREQ == 1):  # Reset the boolean.
            played_smug_sound = False

        # Update difficulty
        if score >= 10 and score < 20:
            ENEMY_FREQ = 2
            ENEMY_VEL = 1.5
        elif score >= 20 and score < 30:
            ENEMY_FREQ = 1.5
        elif score >= 45 and score < 60:
            ENEMY_FREQ = 1
        elif score >= 60:
            ENEMY_VEL = 1.8

        # Check if player died
        if player.health <= 0:
            play_sound("explosion", 0.5, fadeout_ms=4000, fadeout=True)
            pos_list = list(range(0, 200, 10))

            for dim in pos_list:
                player.explosion_image(dim, dim)
                WIN.blit(player.image, player.explosion_rect)
                pygame.display.update()
                time.sleep(0.1)
            play_sound("player_lose", 1.0)
            time.sleep(7)
            running = False  # End the game.

    pygame.quit()
    print("You quit the game. Thanks for playing!")


# Run
if __name__ == "__main__":
    main()
