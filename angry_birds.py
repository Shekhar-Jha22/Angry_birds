import pygame
import sys
import time
import random
import math
pygame.init()


#constants


WIDTH, HEIGHT = 1280, 720
surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ANGRY BIRDS")
clock = pygame.time.Clock()
SPRITESHEET_PATH = "angry_birds.png"
BLOCK_SHEET_PATH = "download.jpg"
BACKGROUND_PATH = "background3.png"
SLING_PATH = "sling.png"
LOADING_BACKGROUND = "bg.jpg"
BACKGROUND_SOUND = "angry-birds.ogg"
LAUNCH_SOUND = "launch.mp3"
WIN_SOUND = "end.mp3"
GRAVITY_FACTOR = 0.5
MAX_DRAG_DISTANCE = 70
LAUNCH_SPEED_FACTOR = 0.6
spritesheet = pygame.image.load(SPRITESHEET_PATH).convert_alpha()
block_spritesheet = pygame.image.load(BLOCK_SHEET_PATH).convert_alpha()
background = pygame.image.load(BACKGROUND_PATH).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
menu_background = pygame.image.load(LOADING_BACKGROUND).convert()
menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
launch_sound = pygame.mixer.Sound(LAUNCH_SOUND)
launch_sound.set_volume(0.7)
boost_sound = launch_sound
win_sound = pygame.mixer.Sound(WIN_SOUND)
win_sound.set_volume(0.7)
pygame.mixer.music.load(BACKGROUND_SOUND)
pygame.mixer.music.set_volume(0.5)
BUTTONS_SPRITE_PATH = "buttons-image.png"
buttons_sheet = pygame.image.load(BUTTONS_SPRITE_PATH).convert_alpha()
PLAY_BUTTON_RECT = pygame.Rect(960,   35, 240, 140)
PLAY_AGAIN_RECT = pygame.Rect(350, 630,  140, 170)
INSTRUCTIONS_RECT = pygame.Rect(690, 750,  110, 130)
PAUSE = pygame.Rect(WIDTH - 120, 20, 80, 80)
RESTART = pygame.Rect(WIDTH - 220, 20, 80, 80)
LEVEL_QUIT = pygame.Rect(WIDTH - 320, 20, 80, 80)
GAME_QUIT = pygame.Rect(WIDTH - 120, HEIGHT - 100, 100, 50)

LEVEL1_RECT = pygame.Rect(WIDTH//2 - 150, 200, 300, 60)
LEVEL2_RECT = pygame.Rect(WIDTH//2 - 150, 280, 300, 60)
INSTRUCTIONS_MENU_RECT = pygame.Rect(WIDTH//2 - 150, 360, 300, 60)
EXIT_RECT = pygame.Rect(WIDTH//2 - 150, 440, 300, 60)
play_button_img = buttons_sheet.subsurface(PLAY_BUTTON_RECT)
play_again_img = buttons_sheet.subsurface(PLAY_AGAIN_RECT)
instructions_img = buttons_sheet.subsurface(INSTRUCTIONS_RECT)
BIRD_SCALE = 0.75
BLOCK_SIZE = 60
BLOCK_HEALTH = 100
SCORE_BAR_WIDTH = WIDTH // 2 - 60
SCORE_BAR_HEIGHT = 30
SCORE_BAR_MARGIN = 30
FONT = pygame.font.SysFont("Arial", 32)
MENU_FONT = pygame.font.SysFont("Arial", 64)
SCORE_FONT = pygame.font.SysFont("Arial", 24, bold=True)
TURN_FONT = pygame.font.SysFont("Arial", 36, bold=True)
ABILITY_FONT = pygame.font.SysFont("Arial", 36, bold=True)
SLING_WIDTH, SLING_HEIGHT = 100, 170
bird_defs = [
    (pygame.Rect(185, 30, 64, 64), 'red', 60),
    (pygame.Rect(205, 120, 64, 64), 'blue', 30),
    (pygame.Rect(200, 215, 64, 64), 'yellow', 40),
    (pygame.Rect(120, 310, 64, 96), 'black', 60),
]
PYRAMID_OFFSETS = [
    (0, 0), (-60, -60), (60, -60), 
    (-120, -120), (0, -120), (120, -120),
    (-180, -180), (-60, -180), (60, -180), (180, -180)
]
BLOCK_TYPES = {
    'wood': pygame.Rect(8, 9, 38, 38),
    'stone': pygame.Rect(8, 65, 38, 38),
    'ice': pygame.Rect(8, 179, 38, 38),
    'damaged_wood': pygame.Rect(179, 9, 38, 38),
    'damaged_stone': pygame.Rect(179, 65, 38, 38),
    'damaged_ice': pygame.Rect(179, 179, 38, 38),
}
tower_offsets = [(col * BLOCK_SIZE, -row * BLOCK_SIZE) for row in range(5) for col in range(2)]
TOWER_POSITIONS = tower_offsets


def get_bird_start(sx, sy, rect):
    x = sx - rect.width // 2
    y = sy - 60 - rect.height // 2
    return x, y


def get_user_input(prompt):
    pygame.key.start_text_input()
    text = ""
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 10:
                        text += event.unicode
        
        surface.blit(menu_background, (0, 0))
        
        # Main container
        container_width = 600
        container_height = 250  # Increased height for better spacing
        container_rect = pygame.Rect(
            WIDTH//2 - container_width//2,
            HEIGHT//2 - container_height//2,
            container_width,
            container_height
        )
        pygame.draw.rect(surface, (255, 165, 0), container_rect, border_radius=15)
        pygame.draw.rect(surface, (0, 0, 0), container_rect, 3, border_radius=15)

        # Input box positioning
        input_width = 400
        input_height = 50
        input_rect = pygame.Rect(
            WIDTH//2 - input_width//2,
            container_rect.centery + 20,  # Center vertically in container
            input_width,
            input_height
        )
        
        # Input box styling
        pygame.draw.rect(surface, (255, 255, 255), input_rect, border_radius=5)
        pygame.draw.rect(surface, (0, 0, 0), input_rect, 2, border_radius=5)

        # Prompt text positioning
        prompt_text = FONT.render(prompt, True, (255, 255, 255))
        prompt_rect = prompt_text.get_rect(center=(WIDTH//2, container_rect.centery - 40))
        surface.blit(prompt_text, prompt_rect)

        # Input text styling (black text for contrast)
        text_surface = FONT.render(text, True, (0, 0, 0))  # Black text
        text_rect = text_surface.get_rect(
            midleft=(input_rect.left + 15, input_rect.centery)
        )
        surface.blit(text_surface, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    pygame.key.stop_text_input()
    return text if text else "Player"


class Bird:
    def __init__(self, rect, btype, mass, spritesheet, sling_center):
        raw = spritesheet.subsurface(rect)
        size = (int(rect.width * BIRD_SCALE), int(rect.height * BIRD_SCALE))
        self.image = pygame.transform.scale(raw, size)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.type = btype
        self.mass = mass
        self.sling_center = sling_center
        self.reset()
        
        
    def reset(self):
        self.x, self.y = get_bird_start(self.sling_center[0], self.sling_center[1], self.rect)
        self.init_x, self.init_y = self.x, self.y
        self.rect.topleft = (self.x, self.y)
        self.vx = self.vy = 0
        self.gravity = 0.5 * GRAVITY_FACTOR
        self.dragging = False
        self.launched = False
        self.ability_used = False
        self.explosion_radius = 115
        self.explosion_time = 0
        self.exploded = False
        self.split_birds = []
        self.collided_blocks = set()
        self.sling_drawn = False
        
        
    def handle_event(self, event):
        if self.launched and event.type == pygame.MOUSEBUTTONDOWN and not self.collided_blocks and not self.ability_used:
            if self.type == 'yellow':
                self.vx *= 2
                self.vy *= 2
                boost_sound.play()
                self.ability_used = True
                return
            if self.type == 'blue':
                self.ability_used = True
                boost_sound.play()
                bird_above = Bird(pygame.Rect(205, 120, 64, 64), 'blue', self.mass/2, spritesheet, self.sling_center)
                bird_below = Bird(pygame.Rect(205, 120, 64, 64), 'blue', self.mass/2, spritesheet, self.sling_center)
                bird_above.x, bird_above.y = self.x, self.y - 75
                bird_below.x, bird_below.y = self.x, self.y + 75
                bird_above.vx, bird_above.vy = self.vx, self.vy
                bird_below.vx, bird_below.vy = self.vx, self.vy
                bird_above.launched = True
                bird_below.launched = True
                bird_above.ability_used = True
                bird_below.ability_used = True
                self.split_birds = [bird_above, bird_below]
                return
            if self.type == 'black':
                self.ability_used = True
                self.exploded = True
                self.explosion_time = time.time()
                boost_sound.play()
                return
        if self.launched:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.dragging = True
            self.sling_drawn = True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = event.pos
            dx = mx - self.init_x
            dy = my - self.init_y
            dist = math.hypot(dx, dy)
            if dist > MAX_DRAG_DISTANCE:
                dx *= MAX_DRAG_DISTANCE / dist
                dy *= MAX_DRAG_DISTANCE / dist
            self.x = self.init_x + dx
            self.y = self.init_y + dy
            self.rect.topleft = (self.x, self.y)
        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            self.launched = True
            self.sling_drawn = False
            self.launch_time = time.time()
            mx, my = pygame.mouse.get_pos()
            self.vx = (self.init_x - mx) * 0.2 * LAUNCH_SPEED_FACTOR
            self.vy = (self.init_y - my) * 0.2 * LAUNCH_SPEED_FACTOR
            launch_sound.play()
            
            #parabola and collision with ground
    def update(self):
        for b in self.split_birds:
            b.update()
        if not self.launched:
            return
        if self.exploded:
            if time.time() - self.explosion_time > 0.3:
                return
            return
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        if self.y + self.rect.height > HEIGHT:
            self.y = HEIGHT - self.rect.height
            self.vy *= -0.3
            self.vx *= 0.9
        if self.x < 0 or self.x + self.rect.width > WIDTH:
            self.vx *= -0.5
        self.rect.topleft = (self.x, self.y)
        
        
    def draw(self):
        for b in self.split_birds:
            b.draw()
        if self.exploded:
            explosion_alpha = 255 * (1 - min(1, (time.time() - self.explosion_time) / 0.3))
            surface_ex = pygame.Surface((self.explosion_radius*2, self.explosion_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surface_ex, (255, 165, 0, int(explosion_alpha)), (self.explosion_radius, self.explosion_radius), self.explosion_radius)
            pygame.draw.circle(surface_ex, (255, 255, 0, int(explosion_alpha*0.8)), (self.explosion_radius, self.explosion_radius), int(self.explosion_radius*0.7))
            surface.blit(surface_ex, (self.x + self.rect.width/2 - self.explosion_radius, self.y + self.rect.height/2 - self.explosion_radius))
            return
        surface.blit(self.image, (self.x, self.y))
        
        
    def should_despawn(self):
        if self.exploded:
            return time.time() - self.explosion_time > 0.3
        return self.launched and (time.time() - self.launch_time) > 1.5
    
    
    def check_explosion_damage(self, blocks):
        if not self.exploded:
            return 0
        total = 0
        for block in blocks[:]:
            cx = self.x + self.rect.width/2
            cy = self.y + self.rect.height/2
            bx = block.x + BLOCK_SIZE/2
            by = block.y + BLOCK_SIZE/2
            d = math.hypot(cx-bx, cy-by)
            if d < self.explosion_radius:
                dmg = min(block.health, 40)
                block.health -= dmg
                total += dmg
                if block.health <= 0:
                    blocks.remove(block)
        return total
    
    
    
class Sling:
    def __init__(self, x, y, path):
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(img, (SLING_WIDTH, SLING_HEIGHT))
        self.x, self.y = x, y
        
        
    def draw(self):
        surface.blit(self.image, (self.x, self.y))
        
        
    def draw_sling_line(self, bird):
        if bird.dragging or bird.sling_drawn:
            cx = self.x + SLING_WIDTH // 2
            cy = self.y + 25
            bx = bird.x + bird.rect.width // 2
            by = bird.y + bird.rect.height // 2
            pygame.draw.line(surface, (0, 0, 0), (cx - 30, cy), (bx, by), 5)
            pygame.draw.line(surface, (0, 0, 0), (cx + 15, cy), (bx, by), 5)
            
            
            
class Block:
    def __init__(self, x, y, btype, sheet):
        self.type = btype
        self.health = BLOCK_HEALTH
        self.sheet = sheet
        self.x, self.y = x, y
        self.update_image()
        
        
    def update_image(self):
        key = 'damaged_' + self.type if self.health < BLOCK_HEALTH*0.5 else self.type
        sub = self.sheet.subsurface(BLOCK_TYPES[key])
        self.image = pygame.transform.scale(sub, (BLOCK_SIZE, BLOCK_SIZE))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
        
        
    def draw(self):
        self.update_image()
        surface.blit(self.image, (self.x, self.y))
        hp = int(BLOCK_SIZE * (self.health/BLOCK_HEALTH))
        pygame.draw.rect(surface, (255,0,0), (self.x, self.y-10, BLOCK_SIZE,5))
        pygame.draw.rect(surface, (0,255,0), (self.x, self.y-10, hp,5))
        
        
        # collision with block
    def hit(self, bird):
        dmg = bird.mass
        if (bird.type=='black' and self.type=='stone') or (bird.type=='blue' and self.type=='ice') or (bird.type=='yellow' and self.type=='wood'):
            dmg*=2
        dx = (bird.x+self.rect.width/2)-(self.x+BLOCK_SIZE/2)
        dy = (bird.y+self.rect.height/2)-(self.y+BLOCK_SIZE/2)
        if abs(dx)>abs(dy):
            bird.vx=-bird.vx*0.7
        else:
            bird.vy=-bird.vy*0.7
        ap=min(self.health,dmg)
        self.health-=ap
        return ap
    
    
class Player:
    
    def __init__(self, sling_pos, tower_pos, name="Player"):
        self.name = name
        self.sling = Sling(sling_pos[0], sling_pos[1], SLING_PATH)
        cx = sling_pos[0] + SLING_WIDTH//2
        cy = sling_pos[1] + SLING_HEIGHT//2
        self.center=(cx,cy)
        # Use passed tower_pos parameter instead of global tower_offsets
        edge_offset = -200 if sling_pos[0] < WIDTH//2 else 120
        bt = random.choices(['wood', 'stone', 'ice'], weights=[4,3,3], k=len(tower_pos))
        self.blocks = [
            Block(cx + dx+ edge_offset, cy + dy+ 30, btype, block_spritesheet)
            for (dx, dy), btype in zip(tower_pos, bt)
        ]
        
        self.score = 0
        self.winning_score = 1000
        self.birds = [Bird(r,t,m,spritesheet,(cx,cy)) for r,t,m in bird_defs]
        self.next_bird()
        
        
    def next_bird(self):
        if not self.birds:
            self.birds=[Bird(r,t,m,spritesheet,self.center) for r,t,m in bird_defs]
        self.current=self.birds.pop(0)


def generate_pyramid_offsets():
    """Generate tower offsets for a pyramid structure with base 4"""
    offsets = []
    for row in range(4):
        num_blocks = 4 - row
        start_x = - (num_blocks - 1) * BLOCK_SIZE // 2
        for col in range(num_blocks):
            x = start_x + col * BLOCK_SIZE
            y = -row * BLOCK_SIZE
            offsets.append((x, y))
    return offsets



class Game1v1:
    
    def __init__(self):
        
        p1_name = get_user_input("Enter Player 1 Name:")
        p2_name = get_user_input("Enter Player 2 Name:")
        p1=(200,540)
        p2=(WIDTH-200-SLING_WIDTH,540)
        self.players=[Player(p1,TOWER_POSITIONS, p1_name),Player(p2,TOWER_POSITIONS, p2_name)]
        self.turn=0
        self.game_over=False
        self.winner=None
        self.paused = False
        self.pause_button = pygame.Rect(PAUSE)
        self.restart_button = pygame.Rect(RESTART)
        self.quit_button = pygame.Rect(LEVEL_QUIT)
        self.resume_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 60)
        self.game_quit_button = pygame.Rect(GAME_QUIT)
        pygame.mixer.music.play(-1)
        
        
    def draw_buttons(self):
    # Define button parameters
        vertical_position = 20
        horizontal_spacing = 20
        min_button_width = 100  # Minimum width for visual consistency
        text_padding = 20
        
        # Create buttons in reverse order (right-to-left)
        buttons = [
            ("QUIT", (WIDTH - horizontal_spacing, vertical_position)),
            ("RESTART", (0, vertical_position)),
            ("PAUSE" if not self.paused else "PLAY", (0, vertical_position))
        ]
        
        current_x = WIDTH  # Start from right edge
        
        for text, _ in buttons:
            # Render text to calculate size
            text_surf = SCORE_FONT.render(text, True, (0, 0, 0))
            text_width, text_height = text_surf.get_size()
            
            # Calculate button dimensions
            btn_width = max(text_width + text_padding*2, min_button_width)
            btn_height = text_height + text_padding
            
            # Create rect (align right edge first)
            btn_rect = pygame.Rect(0, 0, btn_width, btn_height)
            btn_rect.top = vertical_position
            btn_rect.right = current_x - horizontal_spacing
            
            # Draw button
            pygame.draw.rect(surface, (189, 255, 31), btn_rect)
            pygame.draw.rect(surface, (0, 0, 0), btn_rect, 2)
            
            # Draw text
            text_rect = text_surf.get_rect(center=btn_rect.center)
            surface.blit(text_surf, text_rect)
            
            # Update positions for next button
            current_x = btn_rect.left - horizontal_spacing
            
            # Store references to interactive buttons
            if text == "PAUSE" or text == "PLAY":
                self.pause_button = btn_rect
            elif text == "RESTART":
                self.restart_button = btn_rect
            elif text == "QUIT":
                self.quit_button = btn_rect
                
                
    def draw_score_bars(self):
        for i, p in enumerate(self.players):
            # Calculate text dimensions first
            score_text = f"{p.name}: {p.score}"
            text_surface = SCORE_FONT.render(score_text, True, (255, 255, 255))
            text_width, text_height = text_surface.get_size()
            
            # Set dynamic bar width (minimum 400px, expand for longer text)
            min_bar_width = 400
            bar_width = max(text_width + 40, min_bar_width)
            bar_height = 15
            padding = 5
            
            # Position based on player side
            if i == 0:  # Left player
                x = SCORE_BAR_MARGIN
            else:       # Right player
                x = WIDTH - SCORE_BAR_MARGIN - bar_width
                
            y = 100 # Vertical position
            
            # Calculate progress fill
            fill_width = int(min(p.score, p.winning_score)/p.winning_score * bar_width)
            
            # Draw background container
            container_rect = pygame.Rect(
                x - padding,
                y - padding,
                bar_width + padding*2,
                bar_height + padding*2
            )
            pygame.draw.rect(surface, (255, 165, 0), container_rect)  # Orange background
            pygame.draw.rect(surface, (0, 0, 0), container_rect, 2)   # Black border
            
            # Progress bar background
            pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height))
            
            # Progress fill with color transition
            if p.score > p.winning_score * 0.7:
                prog = (p.score - p.winning_score*0.7)/(p.winning_score*0.3)
                fill_color = (int(255*(1-prog)), 255, int(255*(1-prog)))
            else:
                fill_color = (255, 255, 255)
                
            pygame.draw.rect(surface, fill_color, (x, y, fill_width, bar_height))
            
            # Score text background
            text_bg_rect = pygame.Rect(
                x,
                y + bar_height + padding,
                bar_width,
                text_height + padding*2
            )
            pygame.draw.rect(surface, (255, 165, 0), text_bg_rect)
            pygame.draw.rect(surface, (0, 0, 0), text_bg_rect, 2)
            
            # Center text in background
            text_x = x + (bar_width - text_width) // 2
            text_y = y + bar_height + padding*2
            surface.blit(text_surface, (text_x, text_y))
            
            
            
    def draw_victory_screen(self):
        overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        surface.blit(overlay,(0,0))
        winner_name = self.players[self.winner].name
        text=MENU_FONT.render(f"{winner_name} Wins!", True, (255,255,255))
        rect=text.get_rect(center=(WIDTH//2,HEIGHT//2-100))
        surface.blit(text,rect)
        PLAY_AGAIN_RECT.topleft=(WIDTH//2-PLAY_AGAIN_RECT.width//2,rect.bottom+20)
        surface.blit(play_again_img,PLAY_AGAIN_RECT.topleft)
        return PLAY_AGAIN_RECT
    
    
    
    def draw_pause_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        pause_text = MENU_FONT.render("GAME PAUSED", True, (255, 255, 255))
        surface.blit(pause_text, pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))
        
        pygame.draw.rect(surface, (255, 162, 0), self.resume_button)
        pygame.draw.rect(surface, (0, 0, 0), self.resume_button, 2)
        resume_text = FONT.render("RESUME", True, (0, 0, 0))
        surface.blit(resume_text, resume_text.get_rect(center=self.resume_button.center))
        
        
        
    def run(self):
        last_frame_time = time.time()
        fps_history = []
        win_sound_played = False
        while True:
            current_time = time.time()
            delta_time = current_time - last_frame_time
            last_frame_time = current_time
            
            fps = 1.0 / delta_time if delta_time > 0 else 0
            fps_history.append(fps)
            if len(fps_history) > 30:
                fps_history.pop(0)
            avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0
            
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit(); sys.exit()
                    
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if self.game_over and PLAY_AGAIN_RECT.collidepoint(event.pos):
                        self.__init__()
                        win_sound_played = False
                        break
                    
                    elif self.pause_button.collidepoint(event.pos):
                        self.paused = not self.paused
                        continue
                        
                    elif self.restart_button.collidepoint(event.pos):
                        self.__init__()
                        break
                        
                    elif self.quit_button.collidepoint(event.pos):
                        return
                        
                    elif self.game_quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                        
                    elif self.paused and self.resume_button.collidepoint(event.pos):
                        self.paused = False
                        continue
                        
                if not self.game_over and not self.paused:
                    self.players[self.turn].current.handle_event(event)
                    
            surface.blit(background,(0,0))
            
            for p in self.players:
                p.sling.draw()
                for b in p.blocks:
                    b.draw()
                    
            self.draw_buttons()
            
            if self.game_over:
                if not win_sound_played:
                    pygame.mixer.music.stop()
                    win_sound.play()
                    win_sound_played = True
                self.draw_victory_screen()
                pygame.display.flip()
                clock.tick(60)
                continue
                
            if self.paused:
                self.draw_pause_screen()
                pygame.display.flip()
                clock.tick(60)
                continue
                
            player=self.players[self.turn]
            b=player.current
            player.sling.draw_sling_line(b)
            
            if b.dragging:
                mx,my=pygame.mouse.get_pos()
                dx=(b.init_x-mx)*0.2
                dy=(b.init_y-my)*0.2
                for i in range(10):
                    t=0.3+1.5*i
                    x=b.init_x+dx*t
                    y=b.init_y+dy*t+0.5*b.gravity*t*t
                    r=max(2,int(8*(1-i/10)))
                    r_outline = r + 3
                    cx,cy=int(x+b.rect.width/2),int(y+b.rect.height/2)
                    pygame.draw.circle(surface,(0,0,0),(cx,cy),r_outline)
                    pygame.draw.circle(surface,(255,255,255),(cx,cy),r)
                    
            if b.launched and not b.ability_used and not b.collided_blocks:
                ability_text = ""
                if b.type=='yellow': ability_text = "Click to boost!"
                if b.type=='blue': ability_text = "Click to split!"
                if b.type=='black': ability_text = "Click to detonate!"
                if ability_text:
                    text_surf = ABILITY_FONT.render(ability_text, True, (255, 255, 0))
                    text_rect = text_surf.get_rect(center=(WIDTH//2, 180))
                    bg_rect = text_rect.copy()
                    bg_rect.inflate_ip(30, 15)
                    pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect)
                    pygame.draw.rect(surface, (255, 255, 0), bg_rect, 3)
                    surface.blit(text_surf, text_rect)
                    
            if b.launched:
                b.update()
                b.draw()
                opp=self.players[1-self.turn]
                if b.type=='black' and b.exploded:
                    dmg=b.check_explosion_damage(opp.blocks)
                    if dmg>0: player.score+=dmg
                for blk in opp.blocks[:]:
                    if b.rect.colliderect(blk.rect) and blk not in b.collided_blocks:
                        dmg=blk.hit(b)
                        player.score+=dmg
                        b.collided_blocks.add(blk)
                        if blk.health<=0: opp.blocks.remove(blk)
                for sb in b.split_birds:
                    for blk in opp.blocks[:]:
                        if sb.rect.colliderect(blk.rect) and blk not in sb.collided_blocks:
                            dmg=blk.hit(sb)
                            player.score+=dmg
                            sb.collided_blocks.add(blk)
                            if blk.health<=0: opp.blocks.remove(blk)
                if player.score>=player.winning_score:
                    self.game_over=True
                    self.winner=self.turn
                if not self.game_over and b.should_despawn():
                    self.turn=1-self.turn
                    self.players[self.turn].next_bird()
            else:
                b.draw()
                
            self.draw_score_bars()
            
            turn_text = f"{self.players[self.turn].name}'s Turn"
            # Create background rectangle
            text_bg = pygame.Rect(WIDTH//2 - 175, 5, 300, 50)
            pygame.draw.rect(surface, (255, 165, 0), text_bg, border_radius=5)  # Orange background
            pygame.draw.rect(surface, (0, 0, 0), text_bg, 2, border_radius=5)    # Black border

            # Create text with black outline
            text = TURN_FONT.render(turn_text, True, (0, 0, 0))  # Black outline
            text_white = TURN_FONT.render(turn_text, True, (255, 255, 255))  # White fill

            # Calculate positions
            text_rect = text_white.get_rect(center=(WIDTH//2, 30))

            # Draw outline by blitting black text multiple times
            for offset in [(-1,-1), (1,-1), (-1,1), (1,1), (0,1), (0,-1), (1,0), (-1,0)]:
                surface.blit(text, text_rect.move(offset))

            # Draw main white text
            surface.blit(text_white, text_rect)
            
            pygame.display.flip()
            clock.tick(60)
            
            
            
class Game1v1Level2(Game1v1):
    
    def __init__(self):
        # Initialize parent class UI elements
        super().__init__()
        
        # Override positions and structure
        p1 = (200 + 50, 540)
        p2 = (WIDTH - 200 - SLING_WIDTH - 50, 540)
        pyramid_offsets = generate_pyramid_offsets()
        
        # Recreate players with new configuration
        self.players = [
            Player(p1, pyramid_offsets, self.players[0].name),
            Player(p2, pyramid_offsets, self.players[1].name)
        ]
        
        
def show_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if LEVEL1_RECT.collidepoint(event.pos):
                    Game1v1().run()
                elif LEVEL2_RECT.collidepoint(event.pos):
                    Game1v1Level2().run()
                elif INSTRUCTIONS_MENU_RECT.collidepoint(event.pos):
                    show_instructions()
                elif EXIT_RECT.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        # Draw menu
        surface.blit(menu_background, (0,0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,128))
        surface.blit(overlay, (0,0))

        # Title
        title = MENU_FONT.render("Angry Birds 1v1", True, (255,255,255))
        title_rect = title.get_rect(center=(WIDTH//2, 100))
        surface.blit(title, title_rect)

        # Draw buttons
        button_data = [
            (LEVEL1_RECT, "Level 1: Columns"),
            (LEVEL2_RECT, "Level 2: Pyramid"),
            (INSTRUCTIONS_MENU_RECT, "Instructions"),
            (EXIT_RECT, "Exit Game")
        ]

        for rect, text in button_data:
            # Button background
            pygame.draw.rect(surface, (255, 165, 0), rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 3)
            
            # Button text
            text_surf = FONT.render(text, True, (0,0,0))
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(60)
        
        
        
def show_instructions():
    back = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 50)
    lines = [
        "How to Play Angry Birds 1v1:",
        "Players take turns launching birds at the opponent's tower",
        "Click and drag a bird to aim, release to launch",
        "Red: Standard bird",
        "Black: Click to detonate! (Extra damage to stone)",
        "Blue: Click to split! (Extra damage to ice)",
        "Yellow: Click to boost! (Extra damage to wood)",
        "First to 1000 points wins!"
    ]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and back.collidepoint(event.pos):
                return
        surface.blit(menu_background, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        title = MENU_FONT.render("Instructions", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH//2, 100))
        surface.blit(title, title_rect)
        y = 180
        for line in lines:
            text = FONT.render(line, True, (255, 255, 255))
            rect = text.get_rect(midleft=(WIDTH//2 - 300, y))
            surface.blit(text, rect)
            y += 40
        pygame.draw.rect(surface, (255, 255, 255), back, 2)
        back_label = FONT.render("Back to Menu", True, (255, 255, 255))
        surface.blit(back_label, back_label.get_rect(center=back.center))
        pygame.display.flip()
        clock.tick(60)
        
        
if __name__ == "__main__":
    show_menu()
    Game1v1().run()



