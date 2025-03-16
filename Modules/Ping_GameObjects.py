import pygame
import math
import random
from .Submodules.Ping_Ball import Ball
from .Submodules.Ping_Paddle import Paddle
from .Submodules.Ping_Obstacles import Obstacle, Goal  # Added Goal for Sewer Level

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
    
    def draw(self, screen, color):
        """Draw the paddle with rounded corners."""
        scaled_rect = self.scale_rect(self.rect)
        pygame.draw.rect(screen, color, scaled_rect, border_radius=7)

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
    
    def handle_wall_collision(self, bounce_walls=False):
        """Handle wall collisions."""
        # First handle vertical walls (top/bottom) - always bounce
        collided = self.ball.handle_wall_collision(self.scoreboard_height, self.arena_height)
        
        # Then handle horizontal walls (left/right) - only bounce if bounce_walls is True
        if bounce_walls:
            if self.rect.left <= 0:
                self.rect.left = 5  # Push further from wall
                self.ball.dx = abs(self.ball.dx)  # Force right direction
                self.ball.velocity_x = self.ball.speed * self.ball.dx
                collided = True
            elif self.rect.right >= self.arena_width:
                self.rect.right = self.arena_width - 5  # Push further from wall
                self.ball.dx = -abs(self.ball.dx)  # Force left direction
                self.ball.velocity_x = self.ball.speed * self.ball.dx
                collided = True
        
        return collided

    def handle_scoring(self, goals=None, bounce_walls=False):
        """
        Check if ball has scored and return score information.
        Uses goal system if goals are provided, otherwise uses traditional edge scoring.
        """
        if goals or bounce_walls:
            return None  # Scoring handled by goals or walls bounce ball
        return self.ball.handle_scoring(self.arena_width)

# Added for Sewer Level implementation
class GoalObject(ArenaObject):
    """Goal object that handles scoring zones behind paddles."""
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, is_left_goal=True):
        """Initialize a goal object with arena properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        
        # Calculate goal dimensions
        width = 20  # Goal depth
        height = 200  # Goal height
        
        # Position goal with specified gaps
        if is_left_goal:
            x = 10  # 10 pixel gap from left wall
        else:
            x = arena_width - width - 10  # 10 pixel gap from right wall
        
        y = (arena_height - height) // 2  # Vertically centered
        
        self.goal = Goal(x, y, width, height, is_left_goal)
    
    @property
    def rect(self):
        return self.goal.rect
    
    def handle_collision(self, ball):
        """Handle collision between goal and ball."""
        return self.goal.handle_collision(ball)

class ObstacleObject(ArenaObject):
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, width=20, height=60):
        """Initialize an obstacle with arena properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        # Calculate middle third boundaries
        third_width = self.arena_width // 3
        min_x = third_width
        max_x = third_width * 2
        
        # Random position within middle third
        x = random.randint(min_x, max_x - width)
        y = random.randint(self.scoreboard_height, self.arena_height - height)
        
        # Create core obstacle
        self.obstacle = Obstacle(x, y, width, height)
    
    @property
    def rect(self):
        return self.obstacle.rect

    def handle_collision(self, ball):
        """Handle collision between obstacle and ball."""
        return self.obstacle.handle_collision(ball)