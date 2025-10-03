import pygame
from constants import *

def load_assets():
    # Load image assets
    spritesheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()
    block_spritesheet = pygame.image.load(BLOCK_SHEET_PATH).convert_alpha()
    
    background = pygame.image.load(BACKGROUND_PATH).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    
    menu_background = pygame.image.load(LOADING_BACKGROUND).convert()
    menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
    
    # Load sounds
    launch_sound = pygame.mixer.Sound(LAUNCH_SOUND)
    launch_sound.set_volume(0.7)  # Set volume to 70%
    
    # Use launch sound for boost for now
    boost_sound = launch_sound
    
    # Set up background music
    pygame.mixer.music.load(BACKGROUND_SOUND)
    pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
    
    return {
        'spritesheet': spritesheet,
        'block_spritesheet': block_spritesheet,
        'background': background,
        'menu_background': menu_background,
        'launch_sound': launch_sound,
        'boost_sound': boost_sound
    }

# Helper to compute bird spawn position
def get_bird_start(sx, sy, rect):
    x = sx - rect.width // 2
    y = sy - 60 - rect.height // 2
    return x, y