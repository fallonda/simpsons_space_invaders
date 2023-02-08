"""For random utilities used across the project."""

import pygame, os
import random

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
        

