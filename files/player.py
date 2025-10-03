import pygame
import random
from bird import Bird
from block import Block
from sling import Sling
from constants import (
    BIRD_DEFS,
    TOWER_OFFSETS,
    SLING_WIDTH,
    SLING_HEIGHT,
    SLING_PATH,
    BLOCK_HEALTH,
    WIDTH,
    # Just import the constants that actually exist
    # Don't add any new ones
)

class Player:
    def __init__(self, sling_pos, tower_pos, assets):
        self.sling = Sling(sling_pos[0], sling_pos[1], SLING_PATH)
        cx = sling_pos[0] + SLING_WIDTH // 2
        cy = sling_pos[1] + SLING_HEIGHT // 2
        self.center = (cx, cy)
        
        # Store assets reference
        self.assets = assets
        
        # Build tower with different block types
        block_types = random.sample(['wood']*4 + ['ice']*3 + ['stone']*3, len(tower_pos))
        
        # Adjust tower position based on player side
        if sling_pos[0] < WIDTH // 2:  # Left player
            self.blocks = [Block(cx + dx - 200, cy + dy + 30, btype, assets['block_spritesheet'])
                           for (dx, dy), btype in zip(tower_pos, block_types)]
        else:  # Right player
            self.blocks = [Block(cx + dx + 100, cy + dy + 30, btype, assets['block_spritesheet'])
                          for (dx, dy), btype in zip(tower_pos, block_types)]
        
        self.score = 0
        self.max_score = len(self.blocks) * BLOCK_HEALTH
        self.birds = [Bird(r, t, m, assets['spritesheet'], self.center, assets['boost_sound'])
                      for r, t, m in BIRD_DEFS]
        self.next_bird()
    
    def next_bird(self):
        if not self.birds:
            # If we run out of birds, regenerate the birds list
            # Use the assets dictionary that was passed in
            self.birds = [Bird(r, t, m, self.assets['spritesheet'], 
                              self.center, self.assets['boost_sound'])
                          for r, t, m in BIRD_DEFS]
        self.current = self.birds.pop(0)
        
    def draw(self, surface):
        self.sling.draw(surface)
        for block in self.blocks:
            block.draw(surface)