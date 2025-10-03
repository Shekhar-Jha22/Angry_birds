import pygame
import sys
import time
from constants import WIDTH, HEIGHT, FONT, MENU_FONT, SCORE_BAR_WIDTH, SCORE_BAR_HEIGHT, SCORE_BAR_MARGIN, TOWER_OFFSETS, SLING_WIDTH, BLOCK_HEALTH
from player import Player

class Game1v1:
    def __init__(self, assets):
        # Player 1 left, Player 2 right
        p1_sling = (200, 540)
        p2_sling = (WIDTH - 200 - SLING_WIDTH, 540)
        self.players = [Player(p1_sling, TOWER_OFFSETS, assets), Player(p2_sling, TOWER_OFFSETS, assets)]
        self.turn = 0
        self.winning_score = 1000
        self.game_over = False
        self.winner = None
        self.assets = assets
        
        # Start playing background music
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        
        # Print tower block counts for debugging
        print(f"Player 1 has {len(self.players[0].blocks)} blocks")
        print(f"Player 2 has {len(self.players[1].blocks)} blocks")

    def draw_score_bars(self, surface):
        for i, p in enumerate(self.players):
            x = SCORE_BAR_MARGIN if i == 0 else WIDTH - SCORE_BAR_MARGIN - SCORE_BAR_WIDTH
            y = SCORE_BAR_MARGIN
            pygame.draw.rect(surface, (0,0,0), (x-2, y-2, SCORE_BAR_WIDTH+4, SCORE_BAR_HEIGHT+4))
            pygame.draw.rect(surface, (255,255,255), (x, y, SCORE_BAR_WIDTH, SCORE_BAR_HEIGHT), 2)
            
            # Calculate fill as percentage of winning score instead of max_score
            fill = int((min(p.score, self.winning_score) / self.winning_score) * SCORE_BAR_WIDTH)
            
            # Change color based on how close to winning
            bar_color = (255, 255, 255)
            if p.score > self.winning_score * 0.7:
                # Gradually change to green as score approaches winning score
                progress = (p.score - self.winning_score * 0.7) / (self.winning_score * 0.3)
                bar_color = (255 * (1 - progress), 255, 255 * (1 - progress))
            
            pygame.draw.rect(surface, bar_color, (x, y, fill, SCORE_BAR_HEIGHT))
            txt = FONT.render(f"P{i+1}: {p.score}/{self.winning_score}", True, (255,255,255))
            surface.blit(txt, (x, y + SCORE_BAR_HEIGHT + 5))

    def draw_victory_screen(self, surface):
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark overlay with transparency
        surface.blit(overlay, (0, 0))
        
        # Display victory message
        victory_text = MENU_FONT.render(f"Player {self.winner + 1} Wins!", True, (255, 255, 255))
        victory_rect = victory_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        surface.blit(victory_text, victory_rect)
        
        # Create play again button
        play_again_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 50)
        pygame.draw.rect(surface, (255, 255, 255), play_again_btn, 2)
        play_again_text = FONT.render("Play Again", True, (255, 255, 255))
        surface.blit(play_again_text, play_again_text.get_rect(center=play_again_btn.center))
        
        return play_again_btn
    
    def handle_collision(self, bird, opponent_blocks):
        damage_done = 0
        
        # Process black bird explosion if applicable
        if bird.type == 'black' and bird.exploded:
            explosion_damage = bird.check_explosion_damage(opponent_blocks)
            if explosion_damage > 0:
                damage_done += explosion_damage
                
        # Handle regular collisions
        for blk in list(opponent_blocks):
            # For regular bird collisions
            if bird.rect.colliderect(blk.rect):
                # If not already collided with this block
                if blk not in bird.collided_blocks:
                    # Print debug info
                    print(f"Collision detected between {bird.type} bird and {blk.type} block")
                    
                    # Apply damage and update score
                    dmg = blk.hit(bird)
                    damage_done += dmg
                    
                    # Add to collided blocks to prevent multiple hits
                    bird.collided_blocks.add(blk)
        
        # Also handle collisions for split birds if they exist
        for split_bird in bird.split_birds:
            for blk in list(opponent_blocks):
                if split_bird.rect.colliderect(blk.rect) and blk not in split_bird.collided_blocks:
                    dmg = blk.hit(split_bird)
                    damage_done += dmg
                    split_bird.collided_blocks.add(blk)
                    
        return damage_done
    
    def run(self, surface, clock):
        while True:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle play again button when game is over
                if self.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    play_again_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 50)
                    if play_again_btn.collidepoint(event.pos):
                        # Reset the game
                        self.__init__(self.assets)
                        continue
                
                # Handle bird events only if game is not over
                if not self.game_over:
                    player = self.players[self.turn]
                    player.current.handle_event(event, self.assets['launch_sound'], self.assets['spritesheet'])

            # Draw game background
            surface.blit(self.assets['background'], (0, 0))
            
            # Draw players (slings and towers)
            for p in self.players:
                p.draw(surface)

            # If game is over, show victory screen and continue
            if self.game_over:
                self.draw_victory_screen(surface)
                pygame.display.flip()
                clock.tick(60)
                continue
                
            # Normal gameplay - handle current bird
            player = self.players[self.turn]
            current_bird = player.current
            
            # Draw trajectory if dragging
            current_bird.draw_trajectory(surface)
                    
            # Special instruction for bird abilities based on type
            if current_bird.launched and not current_bird.ability_used and not current_bird.collided_blocks:
                if current_bird.type == 'yellow':
                    tip_text = FONT.render("Click anywhere to boost the yellow bird!", True, (255, 220, 0))
                    surface.blit(tip_text, (WIDTH//2 - tip_text.get_width()//2, 50))
                elif current_bird.type == 'blue':
                    tip_text = FONT.render("Click anywhere to split the blue bird!", True, (0, 191, 255))
                    surface.blit(tip_text, (WIDTH//2 - tip_text.get_width()//2, 50))
                elif current_bird.type == 'black':
                    tip_text = FONT.render("Black bird will explode on impact!", True, (100, 100, 100))
                    surface.blit(tip_text, (WIDTH//2 - tip_text.get_width()//2, 50))
            
            # Update physics and check for bird status
            if current_bird.launched:
                # Update bird position
                current_bird.update()
                
                # Handle collisions with opponent's blocks
                opponent = self.players[1 - self.turn]
                damage_score = self.handle_collision(current_bird, opponent.blocks)
                
                # Add score from damage
                if damage_score > 0:
                    player.score += damage_score
                    damage_text = FONT.render(f"+{damage_score}", True, (255, 255, 0))
                    current_bird.damage_popups.append({
                        'text': damage_text,
                        'pos': current_bird.rect.center,
                        'lifetime': 60
                    })
                    
                    # Play hit sound
                    self.assets['hit_sound'].play()
                
                # Check if bird is out of bounds or stopped
                if (current_bird.rect.left > WIDTH or 
                    current_bird.rect.right < 0 or 
                    current_bird.rect.top > HEIGHT or
                    (current_bird.velocity.length() < 0.5 and 
                     current_bird.rect.bottom >= HEIGHT - 10)):
                    
                    # Wait a moment before changing turn if there's still active animation
                    if not current_bird.split_birds and not (current_bird.type == 'black' and current_bird.exploded):
                        # Switch to next player's turn after a short delay
                        pygame.time.delay(500)
                        self.next_turn()
            
            # Update and draw any split birds
            active_split_birds = False
            for split_bird in list(current_bird.split_birds):
                split_bird.update()
                split_bird.draw(surface)
                
                # Handle collisions with opponent blocks
                damage_score = self.handle_collision(split_bird, opponent.blocks)
                if damage_score > 0:
                    player.score += damage_score
                    self.assets['hit_sound'].play()
                
                # Check if split bird is out of bounds or stopped
                if (split_bird.rect.left > WIDTH or 
                    split_bird.rect.right < 0 or 
                    split_bird.rect.top > HEIGHT or
                    (split_bird.velocity.length() < 0.5 and 
                     split_bird.rect.bottom >= HEIGHT - 10)):
                    current_bird.split_birds.remove(split_bird)
                else:
                    active_split_birds = True
            
            # If no more active split birds and main bird is done, change turn
            if (current_bird.launched and 
                not active_split_birds and 
                (current_bird.rect.left > WIDTH or 
                 current_bird.rect.right < 0 or 
                 current_bird.rect.top > HEIGHT or
                 (current_bird.velocity.length() < 0.5 and 
                  current_bird.rect.bottom >= HEIGHT - 10))):
                
                # For black bird, check if explosion animation is done
                if current_bird.type == 'black' and current_bird.exploded:
                    if time.time() - current_bird.explosion_time > 1.0:  # Wait 1 second after explosion
                        self.next_turn()
                elif not current_bird.split_birds:
                    self.next_turn()
            
            # Draw damage popups
            for player in self.players:
                player.current.update_damage_popups()
                player.current.draw_damage_popups(surface)
            
            # Draw score bars
            self.draw_score_bars(surface)
            
            # Check for win condition
            if not self.game_over:
                for i, player in enumerate(self.players):
                    if player.score >= self.winning_score:
                        self.game_over = True
                        self.winner = i
                        self.assets['victory_sound'].play()
                        break
            
            # Show active player indicator
            active_text = FONT.render(f"Player {self.turn + 1}'s Turn", True, (255, 255, 255))
            surface.blit(active_text, (WIDTH//2 - active_text.get_width()//2, 10))
            
            # Update the display
            pygame.display.flip()
            clock.tick(60)
    
    def next_turn(self):
        # Clean up current player's bird
        current_player = self.players[self.turn]
        current_player.reset_bird()
        
        # Switch turns
        self.turn = 1 - self.turn
        
        # Prepare next player's bird
        next_player = self.players[self.turn]
        next_player.prepare_next_bird()
        
        # Play turn change sound
        self.assets['switch_turn_sound'].play()