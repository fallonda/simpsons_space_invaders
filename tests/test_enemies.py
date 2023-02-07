from simpsons_space_invaders.enemies import Enemy, ENEMY_WIDTH, ENEMY_HEIGHT
import os
import simpsons_space_invaders.settings as s

# Create a fake enemy to test the methods
fake_enemy = Enemy(
    os.path.join("assets", "kang_transparent.png"),
    200, # Start the fake enemy in the top left quadrant of the screen.
    200,
    ENEMY_WIDTH,
    ENEMY_HEIGHT,
    3, # health
    enemy_vel = 1.0
)       

class TestEnemy(object):
    def test_move_towards_bottom_right(self):
        # Move the enemy towards the middle-ish of the screen. 
        fake_enemy.move_towards(
            chase_x = 400,
            chase_y = 400,    
        )
        assert fake_enemy.x_move == 1
        assert fake_enemy.y_move == 1
        
    def test_move_towards_bottom_left(self):
        fake_enemy.move_towards(
            chase_x = 100,
            chase_y = 100,    
        )
        assert fake_enemy.x_move == -1
        assert fake_enemy.y_move == -1