"""For random utilities used across the project."""

import pygame, os
import random
from datetime import datetime
import pandas as pd

class Text:
    """Draw text on screen."""
    def __init__(self, font, size, text, colour, x, y, set_by="topleft"):
        self.font_path = pygame.font.match_font(font)
        self.font = pygame.font.Font(self.font_path, size)
        self.text = self.font.render(text, True, colour, None)
        self.rect = self.text.get_rect()
        if set_by == "topleft":
            self.rect.x = x
            self.rect.y = y
        elif set_by == "center":
            self.rect.centerx = x
            self.rect.centery = y
        else:
            raise ValueError("set_by can only have the options 'topleft' or 'center'.")
        
    def update_text(self, new_text, colour):
        self.text = self.font.render(new_text, True, colour, None)

    def draw_text(self, surface_to_blit):
        """Draw the text to a surface"""
        surface_to_blit.blit(self.text, self.rect)
        

def play_sound(folder, volume, fadeout_ms=None, fadeout: bool = False):
    """Play random sound from folder"""
    path = os.path.join("assets", "sounds", folder)
    list_of_sounds = os.listdir(path)
    sound = pygame.mixer.Sound(os.path.join(path, random.choice(list_of_sounds)))
    sound.set_volume(volume)  # Between 0.0 and 1.0.
    sound.play()
    if fadeout:
        sound.fadeout(fadeout_ms)
        
class User:
    """Holds username, timestamp and score."""
    def __init__(self):
        self.username = "default"
        
    def add_name(self, username):
        self.username = username
        
    def add_score(self, score):
        self.score = score
        
    def add_timestamp(self):
        self.datetime = str(datetime.now())[0:16]
        
def curate_scores(user:User, current_scores:pd.DataFrame) -> pd.DataFrame:
    """add the new score, and reorder to top 5."""
    current_scores_df = current_scores
    new_score_added = current_scores_df.append({
        "position": 0, # Dummy
        "name": user.username,
        "timestamp": user.datetime,
        "score": user.score,
    }, ignore_index = True)
    scores_sorted = new_score_added.sort_values("score", ascending=False).head(5)
    scores_sorted["position"] = range(1,6)
    scores_sorted["timestamp"] = [str(x) for x in scores_sorted["timestamp"]] # cast as str. 
    return scores_sorted
    
        

