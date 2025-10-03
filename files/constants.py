import pygame
import os

# Initialize Pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 1280, 720
FONT = pygame.font.SysFont(None, 32)
MENU_FONT = pygame.font.SysFont(None, 64)

# Game constants
BIRD_SCALE = 0.75
BLOCK_SIZE = 60
BLOCK_HEALTH = 100
SCORE_BAR_WIDTH, SCORE_BAR_HEIGHT = 200, 20
SCORE_BAR_MARGIN = 20
SLING_WIDTH, SLING_HEIGHT = 100, 170

# Asset paths
SPRITESHEET_PATH = "angry_birds.png"
BLOCK_SHEET_PATH = "download.jpg"
BACKGROUND_PATH = "background3.png"
SLING_PATH = "sling.png"
LOADING_BACKGROUND = "bg.jpg"
BACKGROUND_SOUND = "angry-birds.ogg"
LAUNCH_SOUND = "launch.mp3"
WIN_SOUND = "end.mp3"

# Bird types: (sprite rect, type, mass)
BIRD_DEFS = [
    (pygame.Rect(185, 30, 64, 64), 'red', 60),
    (pygame.Rect(205, 120, 64, 64), 'black', 60),
    (pygame.Rect(200, 215, 64, 64), 'blue', 30),
    (pygame.Rect(120, 310, 64, 96), 'yellow', 40),
]

# Block sprite regions
BLOCK_TYPES = {
    'wood': pygame.Rect(8, 9, 38, 38),
    'stone': pygame.Rect(8, 65, 38, 38),
    'ice': pygame.Rect(8, 179, 38, 38),
    'damaged_wood': pygame.Rect(179, 9, 38, 38),
    'damaged_stone': pygame.Rect(179, 65, 38, 38),
    'damaged_ice': pygame.Rect(179, 179, 38, 38),
}

# Tower positions relative to sling base
TOWER_OFFSETS = [(col * BLOCK_SIZE, -row * BLOCK_SIZE) for row in range(5) for col in range(2)]

# Base X position for lining up the left tower
BASE_X = 800