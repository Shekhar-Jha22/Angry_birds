import pygame
from constants import BLOCK_SIZE, BLOCK_HEALTH, BLOCK_TYPES

class Block:
    def __init__(self, x, y, btype, sheet):
        self.type = btype
        self.health = BLOCK_HEALTH
        self.sheet = sheet
        self.x, self.y = x, y
        self.update_image()
        # Add debug prints to confirm blocks are created properly
        print(f"Created block: {btype} at {x},{y} with health {self.health}")

    def update_image(self):
        key = 'damaged_' + self.type if self.health < BLOCK_HEALTH * 0.5 else self.type
        sub = self.sheet.subsurface(BLOCK_TYPES[key])
        self.image = pygame.transform.scale(sub, (BLOCK_SIZE, BLOCK_SIZE))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface):
        # Update the image each frame to reflect current health
        self.update_image()
        surface.blit(self.image, (self.x, self.y))
        
        # Optional: Debug visualization to show block health
        health_percent = self.health / BLOCK_HEALTH
        health_width = int(BLOCK_SIZE * health_percent)
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 10, BLOCK_SIZE, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y - 10, health_width, 5))

    def hit(self, bird):
        # Apply damage based on bird type and block type
        damage = bird.mass
        if (bird.type == 'black' and self.type == 'stone') or \
           (bird.type == 'blue' and self.type == 'ice') or \
           (bird.type == 'yellow' and self.type == 'wood'):
            damage *= 2
        
        # Determine collision direction
        dx = (bird.x + bird.rect.width/2) - (self.x + BLOCK_SIZE/2)
        dy = (bird.y + bird.rect.height/2) - (self.y + BLOCK_SIZE/2)
        
        # Bounce the bird
        if abs(dx) > abs(dy):
            bird.vx = -bird.vx * 0.7
        else:
            bird.vy = -bird.vy * 0.7
        
        # Apply damage and print for debugging
        applied = min(self.health, damage)
        self.health -= applied
        print(f"Hit! Block {self.type} took {applied} damage. Health now: {self.health}")
        return applied