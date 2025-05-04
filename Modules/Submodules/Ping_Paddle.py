import pygame
import os

class Paddle:
    def __init__(self, x, y, width, height, is_left_paddle=True):
        """Initialize a paddle object."""
        self.rect = pygame.Rect(x, y, width, height)
        self.is_left_paddle = is_left_paddle
        self.speed = 300  # Standard paddle speed
        self.moving_up = False
        self.moving_down = False
        
        # Load the appropriate sprite based on paddle side
        sprite_path = os.path.join('Ping Assets', 'Images', 'Sprites',
                                 'Protag Paddle.webp' if is_left_paddle else 'Anttag Paddle.webp')
        self.sprite = pygame.image.load(sprite_path).convert_alpha()
        
        # Scale sprite to match paddle dimensions
        self.sprite = pygame.transform.scale(self.sprite, (width, height))
        
        # Create mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.sprite)
    
    def draw(self, screen, scale_rect):
        """Draw the paddle using its sprite."""
        scaled_rect = scale_rect(self.rect)
        # Scale the sprite to match the scaled rect
        scaled_sprite = pygame.transform.scale(self.sprite, (scaled_rect.width, scaled_rect.height))
        screen.blit(scaled_sprite, scaled_rect)
    
    def move(self, delta_time, arena_height): # Removed scoreboard_height
        """Move the paddle based on input flags and time delta."""
        movement = self.speed * delta_time
        if self.moving_up and self.rect.top > 0: # Check against Y=0
            new_y = self.rect.y - movement
            self.rect.y = max(0, new_y) # Use 0 as the minimum Y
        if self.moving_down and self.rect.bottom < arena_height:
            new_y = self.rect.y + movement
            self.rect.y = min(new_y, arena_height - self.rect.height)
    
    def reset_position(self, arena_width, arena_height):
        """Reset paddle to starting position."""
        self.rect.y = (arena_height - self.rect.height) // 2
        if self.is_left_paddle:
            self.rect.x = 50  # Left paddle 50px from left
        else:
            self.rect.x = arena_width - 70  # Right paddle 70px from right