import pygame
import math
import random

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

class Paddle(ArenaObject):
    def __init__(self, x, y, width, height, arena_width, arena_height, scoreboard_height, scale_rect, is_left_paddle=True):
        """Initialize a paddle object."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.rect = pygame.Rect(x, y, width, height)
        self.is_left_paddle = is_left_paddle
        self.speed = 300  # Standard paddle speed
        self.moving_up = False
        self.moving_down = False
    
    def move(self, delta_time):
        """Move the paddle based on input flags and time delta."""
        movement = self.speed * delta_time
        if self.moving_up and self.rect.top > self.scoreboard_height:
            new_y = self.rect.y - movement
            self.rect.y = max(self.scoreboard_height, new_y)
        if self.moving_down and self.rect.bottom < self.arena_height:
            new_y = self.rect.y + movement
            self.rect.y = min(new_y, self.arena_height - self.rect.height)
    
    def reset_position(self):
        """Reset paddle to starting position."""
        self.rect.y = (self.arena_height - self.rect.height) // 2
        if self.is_left_paddle:
            self.rect.x = 50  # Left paddle 50px from left
        else:
            self.rect.x = self.arena_width - 70  # Right paddle 70px from right

class Ball(ArenaObject):
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, size=20):
        """Initialize a ball object."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.size = size
        self.rect = pygame.Rect(0, 0, size, size)
        self.speed = 300  # Base ball speed
        self.max_speed = 600  # Maximum ball speed
        self.dx = 1  # Direction multiplier
        self.dy = -1  # Direction multiplier
        self.velocity_x = self.speed * self.dx  # Actual velocity
        self.velocity_y = self.speed * self.dy  # Actual velocity
        self.reset_position()
    
    def move(self, delta_time):
        """Move the ball based on its velocity and time delta."""
        self.rect.x += self.velocity_x * delta_time
        self.rect.y += self.velocity_y * delta_time

    def reset_position(self):
        """Reset ball to center position."""
        self.rect.x = (self.arena_width - self.size) // 2
        self.rect.y = (self.arena_height - self.size) // 2
        # Randomize initial vertical direction
        self.dy = 1 if random.random() < 0.5 else -1
        self.velocity_x = self.speed * self.dx
        self.velocity_y = self.speed * self.dy

    def handle_paddle_collision(self, paddle):
        """Handle collision with a paddle."""
        if not self.rect.colliderect(paddle.rect):
            return False
            
        if paddle.is_left_paddle:
            self.rect.left = paddle.rect.right  # Place ball outside paddle
            self.dx = 1  # Ensure ball moves right
        else:
            self.rect.right = paddle.rect.left  # Place ball outside paddle
            self.dx = -1  # Ensure ball moves left
        
        # Calculate angle based on where ball hits the paddle
        relative_intersect = (self.rect.centery - paddle.rect.top) / paddle.rect.height
        angle = (relative_intersect - 0.5) * 90
        # Adjust ball's vertical velocity based on hit angle
        if paddle.is_left_paddle:
            self.dy = -math.tan(math.radians(angle))
        else:
            self.dy = math.tan(math.radians(angle))
            
        # Update velocities based on direction and speed
        speed = self.speed
        total_velocity = math.sqrt(1 + self.dy * self.dy) # dx is 1 or -1
        if total_velocity * speed > self.max_speed:
            speed = self.max_speed / total_velocity
        
        self.velocity_x = speed * self.dx
        self.velocity_y = speed * self.dy
            
        return True
    
    def handle_wall_collision(self):
        """Handle collision with walls and scoreboard."""
        if self.rect.top <= self.scoreboard_height or self.rect.bottom >= self.arena_height:
            self.dy *= -1
            self.velocity_y = self.speed * self.dy
            return True
        return False
    
    def handle_scoring(self):
        """Check if ball has scored and return score information."""
        if self.rect.left <= 0:
            return "right"  # Right player scores
        elif self.rect.right >= self.arena_width:
            return "left"  # Left player scores
        return None

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
                ball.dx *= -1  # Reverse horizontal direction
                ball.velocity_x = ball.speed * ball.dx
            else:
                ball.dy *= -1  # Reverse vertical direction
                ball.velocity_y = ball.speed * ball.dy
            
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