import pygame
import time
import math
from constants import WIDTH, HEIGHT, BIRD_SCALE, BLOCK_SIZE  # Added BLOCK_SIZE import
from assets import get_bird_start

class Bird:
    def __init__(self, rect, btype, mass, spritesheet, sling_center, boost_sound):
        raw = spritesheet.subsurface(rect)
        size = (int(rect.width * BIRD_SCALE), int(rect.height * BIRD_SCALE))
        self.image = pygame.transform.scale(raw, size)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.type = btype
        self.mass = mass
        self.sling_center = sling_center
        self.boost_sound = boost_sound
        self.collided_blocks = set()
        self.ability_used = False  # Track if special ability has been used
        self.explosion_radius = 100  # For black bird explosion
        self.explosion_time = 0  # For explosion animation timing
        self.exploded = False  # Track if explosion has happened
        self.split_birds = []  # For blue bird's split ability
        self.reset()

    def reset(self):
        self.x, self.y = get_bird_start(self.sling_center[0], self.sling_center[1], self.rect)
        self.init_x, self.init_y = self.x, self.y
        self.rect.topleft = (self.x, self.y)
        self.vx = self.vy = 0
        self.gravity = 0.5
        self.dragging = False
        self.launched = False
        self.launch_time = 0
        self.ability_used = False
        self.boost_effect_time = 0  # For visual effect timing
        self.exploded = False
        self.explosion_time = 0
        self.split_birds = []
        self.collided_blocks.clear()

    def handle_event(self, event, launch_sound, spritesheet):
        # Bird abilities when clicked after launch
        if self.launched and event.type == pygame.MOUSEBUTTONDOWN and not self.collided_blocks and not self.ability_used:
            # Yellow bird - boost speed
            if self.type == 'yellow':
                self.vx *= 10
                self.vy *= 10
                self.boost_sound.play()
                self.boost_effect_time = time.time()
                self.ability_used = True
                print("Yellow bird BOOST activated!")
                return
                
            # Blue bird - split into three
            elif self.type == 'blue':
                self.ability_used = True
                self.boost_sound.play()  # Reuse boost sound for now
                
                # Create two new blue birds above and below
                bird_above = Bird(pygame.Rect(200, 215, 64, 64), 'blue', self.mass/2, spritesheet, self.sling_center, self.boost_sound)
                bird_below = Bird(pygame.Rect(200, 215, 64, 64), 'blue', self.mass/2, spritesheet, self.sling_center, self.boost_sound)
                
                # Position birds
                bird_above.x, bird_above.y = self.x, self.y - 40
                bird_below.x, bird_below.y = self.x, self.y + 40
                
                # Match velocity
                bird_above.vx, bird_above.vy = self.vx, self.vy
                bird_below.vx, bird_below.vy = self.vx, self.vy
                
                # Mark as launched
                bird_above.launched = True
                bird_below.launched = True
                bird_above.launch_time = time.time()
                bird_below.launch_time = time.time()
                bird_above.ability_used = True
                bird_below.ability_used = True
                
                # Add to split birds list
                self.split_birds = [bird_above, bird_below]
                
                print("Blue bird SPLIT activated!")
                return
                
            # Black bird - explode
            elif self.type == 'black':
                self.ability_used = True
                self.exploded = True
                self.explosion_time = time.time()
                self.boost_sound.play()  # Replace with explosion sound when available
                print("Black bird EXPLOSION activated!")
                return
        
        if self.launched:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = event.pos
            dx = mx - self.init_x
            dy = my - self.init_y
            dist = math.hypot(dx, dy)
            if dist > 100:
                dx *= 100 / dist
                dy *= 100 / dist
            self.x = self.init_x + dx
            self.y = self.init_y + dy
            self.rect.topleft = (self.x, self.y)
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            self.launched = True
            self.launch_time = time.time()
            mx, my = pygame.mouse.get_pos()
            self.vx = (self.init_x - mx) * 0.2
            self.vy = (self.init_y - my) * 0.2
            # Play launch sound when bird is launched
            launch_sound.play()

    def update(self):
        # Update split birds if they exist
        for bird in self.split_birds:
            bird.update()
        
        if not self.launched:
            return
            
        # If black bird exploded, handle explosion effects
        if self.exploded:
            # Animation timing - keeping explosion visible for 0.3 seconds
            if time.time() - self.explosion_time > 0.3:
                return  # Stop updating after explosion animation finishes
            return
            
        # Normal physics update
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        # Floor bounce
        if self.y + self.rect.height > HEIGHT:
            self.y = HEIGHT - self.rect.height
            self.vy *= -0.3
            self.vx *= 0.9
        # Wall bounce
        if self.x < 0 or self.x + self.rect.width > WIDTH:
            self.vx *= -0.5
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        # Draw split birds
        for bird in self.split_birds:
            bird.draw(surface)
            
        # If black bird exploded, draw explosion
        if self.exploded:
            # Draw explosion animation
            explosion_alpha = 255 * (1 - min(1, (time.time() - self.explosion_time) / 0.3))
            explosion_surface = pygame.Surface((self.explosion_radius*2, self.explosion_radius*2), pygame.SRCALPHA)
            
            # Yellow/orange gradient for explosion
            pygame.draw.circle(explosion_surface, (255, 165, 0, int(explosion_alpha)), 
                              (self.explosion_radius, self.explosion_radius), self.explosion_radius)
            pygame.draw.circle(explosion_surface, (255, 255, 0, int(explosion_alpha*0.8)), 
                              (self.explosion_radius, self.explosion_radius), self.explosion_radius * 0.7)
            
            # Draw explosion centered on bird
            surface.blit(explosion_surface, 
                        (self.x + self.rect.width/2 - self.explosion_radius, 
                         self.y + self.rect.height/2 - self.explosion_radius))
            return
            
        # Draw the bird normally
        surface.blit(self.image, (self.x, self.y))

    def should_despawn(self):
        # For exploded black bird, despawn after explosion animation
        if self.exploded:
            return time.time() - self.explosion_time > 0.3
        
        # Regular despawn timing for other birds
        return self.launched and (time.time() - self.launch_time) > 1.5
        
    def check_explosion_damage(self, blocks):
        """Check if explosion affects any blocks and apply damage"""
        if not self.exploded:
            return 0
            
        total_damage = 0
        blocks_to_remove = []
        
        # Get center of bird
        center_x = self.x + self.rect.width/2
        center_y = self.y + self.rect.height/2
        
        for block in blocks:
            # Get center of block - using block's size attributes instead of global constant
            block_center_x = block.x + block.rect.width/2
            block_center_y = block.y + block.rect.height/2
            
            # Calculate distance
            dx = center_x - block_center_x
            dy = center_y - block_center_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If within explosion radius, apply damage
            if distance < self.explosion_radius:
                # Closer blocks get more damage
                damage_factor = 1 - (distance / self.explosion_radius)
                damage = block.health * damage_factor * 2  # Powerful explosion
                
                print(f"Explosion damaged {block.type} block by {damage} (distance: {distance:.1f})")
                
                # Apply damage
                block.health -= damage
                total_damage += damage
                
                # Check if block is destroyed
                if block.health <= 0:
                    blocks_to_remove.append(block)
        
        return total_damage

    def draw_trajectory(self, surface):
        if not self.dragging:
            return
            
        # Trajectory preview
        mx, my = pygame.mouse.get_pos()
        dx = (self.init_x - mx) * 0.2
        dy = (self.init_y - my) * 0.2
        for i in range(10):
            t = 0.3 + 1.5 * i
            x = self.init_x + dx * t
            y = self.init_y + dy * t + 0.5 * self.gravity * t * t
            r = max(2, int(8 * (1 - i/10)))
            cx, cy = int(x + self.rect.width/2), int(y + self.rect.height/2)
            pygame.draw.circle(surface, (255,255,255), (cx, cy), r)
            pygame.draw.circle(surface, (0,0,0), (cx, cy), r, 1)