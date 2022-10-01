# Sounds taken from https://www.wavsource.com/.
# Images taken from google. 

# Packages and modules
import pygame, os, random, time
from math import sin, cos, radians
pygame.init()

# Set parent directory. 
os.chdir("C:/Users/df717388/OneDrive - GSK/Documents/pygame/inside/simpsons_space_invaders")

# Constants
WIDTH, HEIGHT = 1600, 1000
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
ENEMY_FREQ = 2.5 # time in sec to add enemies to the screen. 
ENEMY_WIDTH, ENEMY_HEIGHT = 50, 80
ENEMY_CLASH_DAMAGE = 20
SPLATTER_TIME = 2.0 # Time in sec to keep splattered enemies on screen.
POWERUP_DROP_SPEED = 2 # Falling speed of powerups.
LEMON_DROP_FREQ = random.randint(20, 40) # Also changes in function!
POWERUP_TYPES = ["lemon", "beer", "donut"]
LEMON_POWER_DUR = 10
POWERUP_VOL = 0.5
LEMON_BULLET_DAMAGE = 3
LEMON_BULLET_SIZE = 20
BULLET_TYPES = ["default", "player", "lemon", "cola_bomb"]
SMUG_FREQ = 7
HEALTH_POWERUP_TYPES = ["beer", "donut"]
HEALTH_POWERUP_AMOUNT = 20
HEALTH_DROP_FREQ = random.randint(20, 40) # Also changes in function!


# Set up window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game window") # Title of window.
SPACE = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "simpsons_space.jpg")), (WIDTH, HEIGHT)
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
        self.x_center = self.rect.x + (width//2)
        self.y_center = self.rect.y + (height//2)
        
    def deplete_health(self, damage_taken):
        self.health -= damage_taken
        
        
    def change_image(self, new_image):
        """Update the image of the enemy"""
        self.image = (pygame.transform.scale(pygame.image.load(os.path.join("assets", new_image)),
                                                (self.rect.width, self.rect.height)))
        
    def explosion_image(self, width, height):
        """Draw out single frame of explosion"""
        self.image = (pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "explosion.png")),
                                                (width, height)))
        self.explosion_rect = self.image.get_rect(center = self.rect.center)
        
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
        self.health_icon_rect = pygame.Rect(250, 934, 30, 30)
        self.health_icon = (pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "health_icon.png")),
                                                (self.health_icon_rect.width,
                                                 self.health_icon_rect.height)))
        self.lemon_power_active = False
        
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
        else: # if player_angle is neg
            if self.player_angle <= -360: 
                self.player_deg = self.player_angle + 360
            else: 
                self.player_deg = self.player_angle
            self.player_deg = self.player_deg + 360 # Convert it to positive. 
        self.player_deg = 360 - self.player_deg # mirror flip the value to be correct. 

    def rotate_player(self):
        """Rotate the rect and image to the new player_angle"""
        self.rotated_image = pygame.transform.rotate(self.image, self.player_angle) 
        new_rect = self.rotated_image.get_rect(center = self.image.get_rect(
            center = (self.x_center, self.y_center)).center)
        self.rect = new_rect
    
    def handle_movement(self, keys_pressed):
        """Move the player around the screen"""
        if keys_pressed[pygame.K_a] and self.rect.x - VEL > 0: # LEFT
            self.rect.x -= VEL
        if keys_pressed[pygame.K_d] and self.rect.x + VEL + self.rect.width < WIDTH: # RIGHT
            self.rect.x += VEL
        if keys_pressed[pygame.K_w] and self.rect.y - VEL > 0: # UP
            self.rect.y -= VEL
        if keys_pressed[pygame.K_s] and self.rect.y + VEL + self.rect.height < HEIGHT: # DOWN
            self.rect.y += VEL
        self.x_center = self.rect.x + (self.rect.width//2) # Update centre position. 
        self.y_center = self.rect.y + (self.rect.height//2)
        
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
        
        
class Enemy(Character):
    """class for generic enemies"""
    def __init__(self, *args):
        Character.__init__(self, *args)
        
    def move_towards(self, chase_x, chase_y):
        """Chase the player"""
        x_diff = chase_x - self.rect.centerx
        y_diff = chase_y - self.rect.centery
        if x_diff < -1:
            self.rect.x -= ENEMY_VEL # Move x by 1 and it's sign.
        elif x_diff > 1: 
            self.rect.x += ENEMY_VEL # Move x by 1 and it's sign.
        else:
            self.rect.x = self.rect.x # Don't move if diff is zero. 
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
    def __init__(self, x_start, y_start, width, height, damage, angle_at_firing, bullet_type, image) :
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x_start-(width/2), y_start-(height/2), width, height)
        self.image = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", image)),
            (width, height))
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
            random.randint(0,(WIDTH-width)), # x start
            0 - height, # y start
            width, height)
        self.image = pygame.transform.scale(pygame.image.load(os.path.join("assets", image)), (width, height))
        if powerup_type in POWERUP_TYPES:
            self.powerup_type = powerup_type
        else:
            raise ValueError(f"'{powerup_type}' is not in allowed list: {POWERUP_TYPES}")
        
    def move_downwards(self):
        """Move the powerup down the screen"""
        self.rect.y += POWERUP_DROP_SPEED
        


# Groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemies_killed_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()

#----------
# Functions
#----------
# Drop lemons
time_last_lemon_drop_added = START_TIME # Initialise time zero
def add_lemon_powerup(previous_time):
    """Add a powerup to fall down screen"""
    time_since_last_lemon_added = time.time() - previous_time
    global LEMON_DROP_FREQ
    if time_since_last_lemon_added >= LEMON_DROP_FREQ:
        new_lemon_drop = Powerup(40, 25, "lemon.png", "lemon")
        powerup_group.add(new_lemon_drop)
        LEMON_DROP_FREQ = random.randint(20, 40) # Generate new random interval
        global time_last_lemon_drop_added # Update time of last lemon drop
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
            new_health_drop = Powerup(40, 40, "beer.png", "beer")
        elif rand_choice == "donut":
            new_health_drop = Powerup(40, 40, "donut.png", "donut")
        else:
            raise ValueError(f"health_powerup_type not valid.")
        HEALTH_DROP_FREQ = random.randint(20, 40) # Generate new random interval
        powerup_group.add(new_health_drop)
        global time_last_health_powerup_added
        time_last_health_powerup_added = time.time()           

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
            ENEMY_WIDTH, ENEMY_HEIGHT,
            3 # enemy health. 
        )
        enemy_group.add(new_enemy)
        global time_last_enemy_added # Update the time_last_enemy_added.  
        time_last_enemy_added = time.time()
    
def random_enemy_start():
    left_margin = (-ENEMY_WIDTH, random.randrange(0, HEIGHT*3/4))
    right_margin = (WIDTH, random.randrange(0, HEIGHT*3/4))
    top_margin = (random.randrange(0, (WIDTH - ENEMY_WIDTH)), -ENEMY_HEIGHT)
    return random.choice([left_margin, right_margin, top_margin])


def play_sound(folder, volume, fadeout_ms=None, fadeout:bool=False):
    """Play random sound from folder"""
    path = os.path.join("assets", "sounds", folder)
    list_of_sounds = os.listdir(path)
    sound = pygame.mixer.Sound(os.path.join(path, random.choice(list_of_sounds)))
    sound.set_volume(volume) # Between 0.0 and 1.0. 
    sound.play()
    if fadeout:
        sound.fadeout(fadeout_ms)
        
def check_time(start_time) -> float:
    """Give the time elapsed in seconds since the start of the game"""
    return (round(time.time() - start_time, 2))
    
    
# Main game function
def main():
    clock = pygame.time.Clock()
    global ENEMY_VEL, ENEMY_FREQ, LEMON_DROP_FREQ, HEALTH_DROP_FREQ
    player = Player(
        os.path.join("assets", "spaceship_yellow.png"),
        WIDTH//2, HEIGHT//2,
        SPACESHIP_WIDTH, SPACESHIP_HEIGHT, 100
        )
    score = 0
    score_text = Text("arial_bold", 30, f"Score: {score}", WHITE, 40, 940)
    player_health_text = Text("arial_bold", 30, f"{player.health}%", WHITE, 285, 940)
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
                    if player.lemon_power_active: # Lemon bullet
                        bullet = Bullet(player.x_center,
                                        player.y_center,
                                        LEMON_BULLET_SIZE, LEMON_BULLET_SIZE,
                                        LEMON_BULLET_DAMAGE, player.player_deg,
                                        "lemon", "lemon.png"
                                        )
                    else: # normal bullet
                        bullet = Bullet(player.x_center,
                                        player.y_center,
                                        BULLET_SIZE, BULLET_SIZE,
                                        DEFAULT_BULLET_DAMAGE, player.player_deg,
                                        "default", "default_bullet.png"
                                        )
                    play_sound("shooting", 0.1, 200, True)
                    bullet_group.add(bullet)
                    
                # Rotate player by 180 deg
                if event.key == pygame.K_DOWN:
                    player.rotate_180()
                if event.key == pygame.K_UP:
                    player.point_up()
                    
        # Spaceship movement        
        keys_pressed = pygame.key.get_pressed() # Check what keys are being pressed.            
        player.handle_movement(keys_pressed)
        player.set_player_angle(keys_pressed)
        player.rotate_player()
        
        # enemy movement
        for enemy in enemy_group:
            enemy.move_towards(player.x_center, player.y_center)
        for bullet in bullet_group:
            bullet.move_bullet(BULLET_VEL)
            # Remove bullets that go off-screen. 
            if (bullet.rect.x < 0 or bullet.rect.x > WIDTH
                or bullet.rect.y < 0 or bullet.rect.y > HEIGHT):
                bullet.kill()
                
        # Bullet hitting enemies
        for enemy in enemy_group:
            # Remove the bullets if they hit an enemy
            for bullet in bullet_group:
                if pygame.sprite.collide_rect(bullet, enemy):
                    bullet.kill() # Remove the bullet if it hit an enemy
                    enemy.deplete_health(bullet.damage) # Deplete health of hit enemy.
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
                else:
                    raise ValueError(f"enemy.hit_by value '{enemy.hit_by}' not valid.") 
                enemies_killed_group.add(enemy) # Transfer enemy to killed group.
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
                powerup.kill() # Remove powerup from screen. 
        
        # Turn off expired powerups
        if player.lemon_power_active:
            time_lemon_on = time.time() - player.lemon_power_last_on_at
            lemon_time_remaining = round(LEMON_POWER_DUR - time_lemon_on)
            lemon_text = Text("arial_bold", 30,
                              f"Lemon power remaining: {lemon_time_remaining} sec",
                              WHITE, 500, 940)
            if (time_lemon_on) >= LEMON_POWER_DUR:
                player.set_lemon_power(False)
                

            
        # drawing section
        WIN.blit(SPACE, (0, 0)) # Fill the background window.
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
        add_health_powerup(time_last_health_powerup_added)
        powerup_group.draw(WIN)
        enemies_killed_group.draw(WIN)
        pygame.display.update()
        
        # Smug winning sound (ensures plays only once every 5 scores)
        if score >= SMUG_FREQ and (score % SMUG_FREQ == 0) and (player.health > 0) and not played_smug_sound: # Every 5 scores. 
            play_sound("player_smug", 1.0)
            played_smug_sound = True
        if score >= SMUG_FREQ and (score % SMUG_FREQ == 1): # Reset the boolean. 
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
            
            for dim in (pos_list):
                player.explosion_image(dim, dim)
                WIN.blit(player.image, player.explosion_rect)
                pygame.display.update()
                time.sleep(0.1)
            play_sound("player_lose", 1.0)
            time.sleep(7)
            running = False # End the game. 
                      
    pygame.quit()    
    print("You quit the game. Thanks for playing!")


# Run
if __name__ == "__main__":
    main()
