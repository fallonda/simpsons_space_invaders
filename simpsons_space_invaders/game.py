# Sounds taken from https://www.wavsource.com/.
# Images taken from google.

# Packages and modules
import pygame, os
from time import time, sleep
import pygame_menu
from pygame_menu import themes
from datetime import datetime
import pandas as pd

# Internal
from simpsons_space_invaders.player import Player
from simpsons_space_invaders.utils import Text, play_sound, User, curate_scores
import simpsons_space_invaders.settings as s
from simpsons_space_invaders.projectiles import Bullet, LemonBullet, PepperBullet, ColaBomb
from simpsons_space_invaders.powerups import PowerupDropper, LEMON_POWER_DUR, PEPPER_POWER_DUR
from simpsons_space_invaders.enemies import ENEMY_CLASH_DAMAGE, SPLATTER_TIME, EnemyDropper

# pygame setup
pygame.init()

# Groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemies_killed_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()
colabomb_group = pygame.sprite.Group()

# Initialise user
user = User()
current_scores = pd.read_csv("high_scores.txt", sep = "\t")
print(current_scores)

# Main game function
def main():
    # Initialisations
    clock = pygame.time.Clock()
    player = Player()
    score = 0
    played_smug_sound = False
    
    # Text on screen
    score_text = Text(
        "arial_bold", 30, f"Score: {score}", s.WHITE,
        s.WIDTH * 0.025, s.HEIGHT * 0.94
    )
    player_health_text = Text(
        "arial_bold", 30, f"{player.health}%", s.WHITE,
        s.WIDTH * 0.19, s.HEIGHT * 0.94
    )
    paused_text = Text(
        "arial", 70, "PAUSED", s.WHITE,
        s.WIDTH//2,
        s.HEIGHT//2,
        set_by="center",
    )
    # Objects that drop powerups
    lemon_dropper = PowerupDropper(40, 25, "lemon.png", "lemon")
    beer_dropper = PowerupDropper(50, 50, "beer.png", "beer")
    donut_dropper = PowerupDropper(40, 40, "donut.png", "donut")
    pepper_dropper = PowerupDropper(20, 40, "pepper.png", "pepper", 60, 80)
    cola_dropper = PowerupDropper(25, 37.5, "cola.png", "cola", 30, 60)
    pop_dropper = PowerupDropper(31, 37.5, "pop_rock.png", "pop_rock", 30, 60)
    # Object that drops enemies
    enemy_dropper = EnemyDropper()

    # Game loop
    running = True
    paused = False
    while running:
        clock.tick(s.FPS)
        # Handling
        events = pygame.event.get()
        for event in events:
            # Check for window close.
            if event.type == pygame.QUIT:
                running = False
            # pause game    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True
            # unpause game
            while paused:
                for event in pygame.event.get():
                    # Draw paused text on screen. 
                    paused_text.draw_text(s.WIN)
                    # Press escape to unpause. 
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            paused = False
                    # Still allow quit window during pause. 
                    if event.type == pygame.QUIT:
                        running = False
                        paused = False
                    # refresh screen while paused.
                    pygame.display.update()
    
            # Key presses
            if event.type == pygame.KEYDOWN:
                # Firing bullets 
                if event.key == pygame.K_SPACE:
                    player.get_degrees() # Sets the angle of the player. 
                    if player.lemon_power_active:  # Lemon bullet
                        bullet = LemonBullet(
                            player.x_center,
                            player.y_center,
                            player.player_deg,
                        )
                        bullet_group.add(bullet)
                    elif player.pepper_power_active:  # pepper bullet
                        # Need three bullets together (left, centre, right)
                        bullet1 = PepperBullet(
                            player.x_center,
                            player.y_center, 
                            player.player_deg - 10, # Stray left
                        )
                        bullet2 = PepperBullet(
                            player.x_center,
                            player.y_center,
                            player.player_deg, # Stay centre
                        )
                        bullet3 = PepperBullet(
                            player.x_center,
                            player.y_center,
                            player.player_deg + 10, # Stray right
                        )
                        bullet_group.add([bullet1, bullet2, bullet3])
                        play_sound("shooting_fire", 0.2) # Separate so only plays once for the three pepper bullets. 
                    # Fire three lemons if both effects are active. 
                    elif player.lemon_power_active & player.pepper_power_active:
                        lemon1 = LemonBullet(
                            player.x_center,
                            player.y_center,
                            player.player_deg - 10, # Stray left
                        )
                        lemon2 = LemonBullet(
                            player.x_center,
                            player.y_center,
                            player.player_deg, # Stay centre
                        )
                        lemon3 = LemonBullet(
                            player.x_center,
                            player.y_center,
                            player.player_deg + 10, # Stray right
                            play_sound_effect = True # Play 1 shooting sound for the three lemons. 
                        )
                        bullet_group.add([lemon1, lemon2, lemon3])
                    else:  # normal bullet, no effects active. 
                        normal_bullet = Bullet(
                            player.x_center,
                            player.y_center,
                            player.player_deg,
                            play_sound_effect=True
                        )
                        bullet_group.add(normal_bullet)
                        
                # Launch colabomb
                if event.key == pygame.K_RETURN:
                    if player.cola_bomb_power_active:
                        colabomb_group.add(ColaBomb())
                        player.reset_cola_bomb_values()

                # Rotate player by 180 deg or point up. 
                if event.key == pygame.K_DOWN:
                    player.rotate_180()
                if event.key == pygame.K_UP:
                    player.point_up()

        # Spaceship movement
        keys_pressed = pygame.key.get_pressed()  # Check what keys are being pressed.
        player.handle_movement(keys_pressed)
        player.set_player_angle(keys_pressed)
        player.rotate_player()

        # Enemy movement
        for enemy in enemy_group:
            enemy.move_towards(player.x_center, player.y_center)
            
        # Bullet movement
        for bullet in bullet_group:
            bullet.move_bullet()
            # Remove bullets that go off-screen.
            if (
                bullet.rect.x < 0
                or bullet.rect.x > s.WIDTH
                or bullet.rect.y < 0
                or bullet.rect.y > s.HEIGHT
            ):
                bullet.kill()

        # Bullet hitting enemies
        for enemy in enemy_group:
            # Remove the bullets if they hit an enemy
            for bullet in bullet_group:
                if pygame.sprite.collide_rect(bullet, enemy):
                    bullet.kill()  # Remove the bullet if it hit an enemy
                    enemy.deplete_health(bullet.damage) # Deplete health of hit enemy.
                    enemy.set_hit_by(bullet.bullet_type)
            # Check if enemies hit player
            if pygame.sprite.collide_rect(enemy, player):
                enemy.health = 0
                enemy.set_hit_by("player")
                player.deplete_health(ENEMY_CLASH_DAMAGE)
                play_sound("player_hit", 0.4)
                score -= 5
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
            if (time() - enemy.timestamp) >= SPLATTER_TIME:
                enemy.kill()

        # powerup drop movement
        for powerup in powerup_group:
            powerup.move_downwards()
            # remove powerups when they hit the bottom of the screen
            if powerup.rect.bottom >= s.HEIGHT:
                powerup.kill()
            # Check if collected by player
            if pygame.sprite.collide_rect(powerup, player):
                powerup.play_powerup_sound()
                if powerup.powerup_type == "lemon":
                    player.set_lemon_power(True)
                elif powerup.powerup_type == "pepper":
                    player.set_pepper_power(True)
                elif powerup.powerup_type in ["donut", "beer"]:
                    player.health += powerup.add_health
                elif powerup.powerup_type == "cola":
                    player.set_cola_or_pop_rock_power("cola", True)
                elif powerup.powerup_type == "pop_rock":
                    player.set_cola_or_pop_rock_power("pop_rock", True)
                powerup.kill()  # Remove powerup from screen.

        # Move colabomb
        for colabomb in colabomb_group:
            colabomb.move()
            colabomb.draw_explosion(enemy_group)
            

        # Turn off expired powerups
        if player.lemon_power_active:
            time_lemon_on = time() - player.lemon_power_last_on_at
            lemon_time_remaining = round(LEMON_POWER_DUR - time_lemon_on)
            lemon_text = Text(
                "arial_bold",
                30,
                f"Lemon power remaining: {lemon_time_remaining} s",
                s.WHITE,
                s.WIDTH * 0.5,
                s.HEIGHT * 0.94,
            )
            if (time_lemon_on) >= LEMON_POWER_DUR:
                player.set_lemon_power(False)

        if player.pepper_power_active:
            time_pepper_on = time() - player.pepper_power_last_on_at
            pepper_time_remaining = round(PEPPER_POWER_DUR - time_pepper_on)
            pepper_text = Text(
                "arial_bold",
                30,
                f"Pepper trip remaining: {pepper_time_remaining} s",
                s.WHITE,
                s.WIDTH * 0.5,
                s.HEIGHT * 0.97,
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
            s.WIN.blit(s.PEPPER_LAND, (0, 0))
            pepper_text.draw_text(s.WIN)
        else:
            s.WIN.blit(s.SPACE, (0, 0))
        score_text.update_text(f"Score: {score}", s.WHITE)
        score_text.draw_text(s.WIN)
        player_health_text.update_text(f"{player.health}%", s.WHITE)
        player_health_text.draw_text(s.WIN)
        if player.lemon_power_active:
            lemon_text.draw_text(s.WIN)
        if player.pepper_power_active:
            pepper_text.draw_text(s.WIN)
        player.draw_health_icon(s.WIN)
        s.WIN.blit(player.rotated_image, player.rect)
        bullet_group.draw(s.WIN)
        enemy_group.draw(s.WIN)
        
        # Add things if they are ready for next release. 
        enemy_dropper.drop_enemy(enemy_group)
        lemon_dropper.release(powerup_group)
        pepper_dropper.release(powerup_group)
        donut_dropper.release(powerup_group)
        beer_dropper.release(powerup_group)
        cola_dropper.release(powerup_group)
        pop_dropper.release(powerup_group)
        player.draw_cola_or_pop_rock()
        colabomb_group.draw(s.WIN)
        powerup_group.draw(s.WIN)
        enemies_killed_group.draw(s.WIN)
        pygame.display.update()
        
        # Increase difficulty
        enemy_dropper.increase_difficulty(score)
 
        # Smug winning sound
        if (
            score >= s.SMUG_FREQ
            and (score % s.SMUG_FREQ == 0)
            and (player.health > 0)
            and not played_smug_sound
        ):
            play_sound("player_smug", 1.0)
            played_smug_sound = True
        if score >= s.SMUG_FREQ and (score % s.SMUG_FREQ == 1):  # Reset the boolean.
            played_smug_sound = False
            
        # Check if player died
        if player.health <= 0:
            play_sound("explosion", 0.5, fadeout_ms=4000, fadeout=True)
            pos_list = list(range(0, 200, 10))
            for dim in pos_list:
                player.explosion_image(dim, dim)
                s.WIN.blit(player.image, player.explosion_rect)
                pygame.display.update()
                sleep(0.1)
            play_sound("player_lose", 1.0)
            sleep(7)
            running = False  # End the game.
        
    # At the indent of the while loop (when running = False)
    # add the score to user.  
    user.add_score(score)
    user.add_timestamp()
    # Write to scores and reorder top 5
    global current_scores
    current_scores = curate_scores(user, current_scores)
    current_scores.to_csv("high_scores.txt", sep = "\t", index=False)
    pygame.quit()

# Menus
mainmenu = pygame_menu.Menu(
    "Simpsons Space Invaders",
    s.WIDTH, s.HEIGHT,
    theme=themes.THEME_SOLARIZED
)
# Score menu
score_menu = pygame_menu.Menu(
    "High Scores",
    s.WIDTH, s.HEIGHT,
    theme=themes.THEME_SOLARIZED
)
def open_score_menu():
    mainmenu._open(score_menu)
mainmenu.add.text_input('Name: ', default='username', maxchar=12, onreturn=user.add_name)
mainmenu.add.button('Play', main)
mainmenu.add.button("High scores", open_score_menu)
mainmenu.add.button('Quit', pygame_menu.events.EXIT)
score_table = score_menu.add.table(table_id = "score_table", font_size=20)
score_table.default_cell_padding = 20
score_table.default_row_background_color = 'white'
score_table.add_row(["Position", 'Name', 'Time', 'Score'])
for i in range(0,5):
    print(current_scores)
    
    list_line = current_scores.iloc[i, :].to_list()
    print(len(list_line))
    score_table.add_row(current_scores.iloc[1, :].to_list())
 


# Game loop
mainmenu.mainloop(s.WIN)


