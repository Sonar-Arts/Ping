import pygame
import math
import random
from .Submodules.Ping_Ball import Ball
from .Submodules.Ping_Paddle import Paddle

class ArenaObject:
    """Base class for objects that need arena properties."""
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect):
        self.arena_width = arena_width
        self.arena_height = arena_height
        self.scoreboard_height = scoreboard_height
        self.scale_rect = scale_rect
    
    def draw(self, screen, color):
        """Draw the object with proper scaling."""
        scaled_rect = self.scale_rect(self.rect)
        pygame.draw.rect(screen, color, scaled_rect)

class PaddleObject(ArenaObject):
    def __init__(self, x, y, width, height, arena_width, arena_height, scoreboard_height, scale_rect, is_left_paddle=True):
        """Initialize a paddle object with arena properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        # Initialize core paddle with just paddle properties, not arena properties
        self.paddle = Paddle(x, y, width, height, is_left_paddle)
        self.reset_position()

    @property
    def rect(self):
        return self.paddle.rect

    @property
    def is_left_paddle(self):
        return self.paddle.is_left_paddle

    @property
    def speed(self):
        return self.paddle.speed

    @property
    def moving_up(self):
        return self.paddle.moving_up

    @moving_up.setter
    def moving_up(self, value):
        self.paddle.moving_up = value

    @property
    def moving_down(self):
        return self.paddle.moving_down

    @moving_down.setter
    def moving_down(self, value):
        self.paddle.moving_down = value

    def move(self, delta_time):
        """Move the paddle based on input flags and time delta."""
        self.paddle.move(delta_time, self.scoreboard_height, self.arena_height)
    
    def reset_position(self):
        """Reset paddle to starting position."""
        self.paddle.reset_position(self.arena_width, self.arena_height)

class BallObject(ArenaObject):
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, size=20):
        """Initialize a ball object with arena properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.ball = Ball(size)
        self.reset_position()

    @property
    def rect(self):
        return self.ball.rect

    def draw(self, screen, color):
        """Override draw method to use ball's circular drawing."""
        self.ball.draw(screen, color, self.scale_rect)

    def move(self, delta_time):
        """Move the ball based on its velocity and time delta."""
        self.ball.move(delta_time)

    def reset_position(self):
        """Reset ball to center position."""
        self.ball.reset_position(self.arena_width, self.arena_height)

    def handle_paddle_collision(self, paddle):
        """Handle collision with a paddle."""
        return self.ball.handle_paddle_collision(paddle)
    
    def handle_wall_collision(self):
        """Handle collision with walls and scoreboard."""
        return self.ball.handle_wall_collision(self.scoreboard_height, self.arena_height)
    
    def handle_scoring(self):
        """Check if ball has scored and return score information."""
        return self.ball.handle_scoring(self.arena_width)

class Obstacle(ArenaObject):
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect):
        """Initialize an obstacle with position in the middle third of the arena."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.width = 20
        self.height = 60
        
        # Calculate middle third boundaries
        third_width = self.arena_width // 3
        min_x = third_width
        max_x = third_width * 2
        
        # Random position within middle third
        self.x = random.randint(min_x, max_x - self.width)
        self.y = random.randint(self.scoreboard_height, self.arena_height - self.height)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def handle_collision(self, ball):
        """Handle collision between obstacle and ball."""
        if ball.rect.colliderect(self.rect):
            # Determine collision side and adjust ball direction
            collision_left = abs(ball.rect.right - self.rect.left)
            collision_right = abs(ball.rect.left - self.rect.right)
            collision_top = abs(ball.rect.bottom - self.rect.top)
            collision_bottom = abs(ball.rect.top - self.rect.bottom)
            
            min_collision = min(collision_left, collision_right, collision_top, collision_bottom)
            
            if min_collision in (collision_left, collision_right):
                ball.ball.dx *= -1  # Reverse horizontal direction
                ball.ball.velocity_x = ball.ball.speed * ball.ball.dx
            else:
                ball.ball.dy *= -1  # Reverse vertical direction
                ball.ball.velocity_y = ball.ball.speed * ball.ball.dy
            
            # Ensure ball doesn't get stuck in obstacle
            if min_collision == collision_left:
                ball.rect.right = self.rect.left
            elif min_collision == collision_right:
                ball.rect.left = self.rect.right
            elif min_collision == collision_top:
                ball.rect.bottom = self.rect.top
            else:
                ball.rect.top = self.rect.bottom
                
            return True
        return False