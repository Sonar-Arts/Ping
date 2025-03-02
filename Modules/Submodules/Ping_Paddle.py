import pygame

class Paddle:
    def __init__(self, x, y, width, height, is_left_paddle=True):
        """Initialize a paddle object."""
        self.rect = pygame.Rect(x, y, width, height)
        self.is_left_paddle = is_left_paddle
        self.speed = 300  # Standard paddle speed
        self.moving_up = False
        self.moving_down = False
    
    def move(self, delta_time, scoreboard_height, arena_height):
        """Move the paddle based on input flags and time delta."""
        movement = self.speed * delta_time
        if self.moving_up and self.rect.top > scoreboard_height:
            new_y = self.rect.y - movement
            self.rect.y = max(scoreboard_height, new_y)
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