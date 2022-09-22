# Sounds taken from https://www.wavsource.com/.
# Images taken from google. 

# Packages and modules
import pygame, os, random, time
from math import sin, cos, radians
pygame.init()

# Set parent directory. 
os.chdir("C:/Users/df717388/OneDrive - GSK/Documents/pygame/simpsons_space")

# Constants
WIDTH, HEIGHT = 1600, 1000
FPS = 60
VEL = 6
BULLET_VEL = 20
BULLET_SIZE = 4
ANGLE_INCREMENT = 2
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ENEMY_VEL = 1
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 50, 50
START_TIME = time.time()
ENEMY_FREQ = 3 # time in sec to add enemies to the screen. 
ENEMY_WIDTH, ENEMY_HEIGHT = 50, 80
ENEMY_CLASH_DAMAGE = 20
SPLATTER_TIME = 2.0 # Time in sec to keep splattered enemies on screen. 

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
        

class Enemy(Character):
    """class for generic enemies"""
    def __init__(self, *args):
        Character.__init__(self, *args)
        
    def move_towards(self, chase_x, chase_y, speed):
        """Chase the player"""
        x_diff = chase_x - self.rect.centerx
        y_diff = chase_y - self.rect.centery
        if x_diff < -1:
            self.rect.x -= speed # Move x by 1 and it's sign.
        elif x_diff > 1: 
            self.rect.x += speed # Move x by 1 and it's sign.
        else:
            self.rect.x = self.rect.x # Don't move if diff is zero. 
        if y_diff < -1:
            self.rect.y -= speed
        elif y_diff > 1:
            self.rect.y += speed
        else:
            self.rect.y = self.rect.y
            
    def kill_and_splat(self, new_image):
        self.kill()
        self.change_image(new_image)
        self.rotate_image_randomly()
        self.mark_time()
        
            
class Bullet(pygame.sprite.Sprite):
    """Bullets can have an image, size, speed, direction, damage"""
    def __init__(self, x_start, y_start, width, height, damage, angle_at_firing, image=None):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x_start, y_start, width, height)
        if image is not None:
            self.image = pygame.transform.scale(
                pygame.image.load(image),
                (width, height))
        self.damage = damage
        self.angle_at_firing = angle_at_firing
        
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
        
        

# Groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemies_killed_group = pygame.sprite.Group()

# Release enemies
time_last_enemy_added = START_TIME
def add_enemy(frequency: float, previous_time) -> float:
    """Add an enemy to the screen given a time frequency in seconds"""
    time_since_last_enemy_added = time.time() - previous_time
    enemy_start_pos = random_enemy_start()
    if time_since_last_enemy_added >= frequency:
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
    
    
# Functions
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
    global ENEMY_VEL, ENEMY_FREQ
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
                    bullet = Bullet(player.x_center,
                                    player.y_center,
                                    BULLET_SIZE, BULLET_SIZE, 1, player.player_deg)
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
            enemy.move_towards(player.x_center, player.y_center, ENEMY_VEL)
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
            # Check if enemies hit player
            if pygame.sprite.collide_rect(player, enemy):
                enemy.health = 0
                player.deplete_health(ENEMY_CLASH_DAMAGE)
                play_sound("player_hit", 0.4)
                score -= 1
            # Change the enemy after all bullet hits.  
            if enemy.health == 2:
                enemy.change_image("kang_one_hit.png")
            elif enemy.health == 1:
                enemy.change_image("kang_two_hits.png")
            elif enemy.health <= 0:
                enemy.kill_and_splat("kang_splatted.png")
                enemies_killed_group.add(enemy) # Transfer enemy to killed group.
                play_sound("kang_kill", 0.3)
                score += 1
            
        
        # Remove splattered enemies
        for enemy in enemies_killed_group:
            if (time.time() - enemy.timestamp) >= SPLATTER_TIME:
                enemy.kill()
         
        # drawing section
        WIN.blit(SPACE, (0, 0)) # Fill the background window.
        score_text.update_text(f"Score: {score}", WHITE)
        score_text.draw_text(WIN)
        player_health_text.update_text(f"{player.health}%", WHITE)
        player_health_text.draw_text(WIN)
        player.draw_health_icon(WIN)
        WIN.blit(player.rotated_image, player.rect)
        for bullet in bullet_group: # Can't use bullet_group.draw() as no image for bullets. 
            bullet.draw_bullet(YELLOW)
        add_enemy(ENEMY_FREQ, time_last_enemy_added)
        enemy_group.draw(WIN)
        enemies_killed_group.draw(WIN)
        pygame.display.update()
        
        # Smug winning sound (ensures plays only once every 5 scores)
        if score >= 5 and (score % 5 == 0) and (player.health > 0) and not played_smug_sound: # Every 5 scores. 
            play_sound("player_smug", 1.0)
            played_smug_sound = True
        if score >= 5 and (score % 5 == 1): # Reset the boolean. 
            played_smug_sound = False    
             
        # Update difficulty 
        if score >= 20:
            ENEMY_FREQ = 2
        elif score >= 40:
            ENEMY_VEL = 2
            
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
