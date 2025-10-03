import pygame
from constants import SLING_WIDTH, SLING_HEIGHT

class Sling:
    def __init__(self, x, y, path):
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(img, (SLING_WIDTH, SLING_HEIGHT))
        self.x, self.y = x, y
    
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))