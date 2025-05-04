import pygame
import math
import random

class Ball:
    def __init__(self, size=20):
        """Initialize a ball object."""
        self.size = size
        self.rect = pygame.Rect(0, 0, size, size)
        self.min_speed = 500  # Minimum ball speed
        self.speed = self.min_speed  # Base ball speed
        self.max_speed = 700  # Maximum ball speed
        self.dx = 1 if random.random() < 0.5 else -1  # Random horizontal direction
        self.dy = 1 if random.random() < 0.5 else -1  # Random vertical direction
        self.velocity_x = self.speed * self.dx  # Actual velocity
        self.velocity_y = self.speed * self.dy  # Actual velocity
    
    def draw(self, screen, color, scale_rect):
        """Draw the ball as a circle."""
        scaled_rect = scale_rect(self.rect)
        pygame.draw.circle(screen, color, scaled_rect.center, scaled_rect.width // 2)
    
    def move(self, delta_time):
        """Move the ball based on its velocity and time delta."""
        self.rect.x += self.velocity_x * delta_time
        self.rect.y += self.velocity_y * delta_time

    def reset_position(self, arena_width, arena_height, scoreboard_height):
        """Reset ball to center position with minimum speed."""
        self.rect.x = (arena_width - self.size) // 2
        # Center within the playable area below the scoreboard
        playable_height = arena_height - scoreboard_height
        self.rect.y = scoreboard_height + (playable_height - self.size) // 2
        # Randomize initial vertical direction
        self.dy = 1 if random.random() < 0.5 else -1
        # Reset to minimum speed
        self.speed = self.min_speed
        self.velocity_x = self.speed * self.dx
        self.velocity_y = self.speed * self.dy

    def handle_paddle_collision(self, paddle):
        """Handle collision with a paddle using mask-based collision."""
        if not self.rect.colliderect(paddle.rect):
            return False
            
        # Create offset for mask collision check
        offset_x = self.rect.x - paddle.rect.x
        offset_y = self.rect.y - paddle.rect.y
        
        # Create a temporary mask for the ball
        ball_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(ball_surface, (255, 255, 255, 255),
                         (self.size//2, self.size//2), self.size//2)
        ball_mask = pygame.mask.from_surface(ball_surface)
        
        # Check for mask collision using the underlying paddle's mask
        if not paddle.paddle.mask.overlap(ball_mask, (offset_x, offset_y)): # Access mask via paddle.paddle
            return False

        # Handle collision response
        buffer = 1 # Small buffer to prevent sticking
        if paddle.is_left_paddle:
            self.rect.left = paddle.rect.right + buffer # Place ball slightly past paddle
            self.dx = 1  # Ensure ball moves right
        else:
            self.rect.right = paddle.rect.left - buffer # Place ball slightly past paddle
            self.dx = -1  # Ensure ball moves left
        
        # Calculate angle based on where ball hits the paddle
        relative_intersect = (self.rect.centery - paddle.rect.top) / paddle.rect.height
        angle = (relative_intersect - 0.5) * 90
        # Adjust ball's vertical velocity based on hit angle
        if paddle.is_left_paddle:
            self.dy = -math.tan(math.radians(angle))
        else:
            self.dy = math.tan(math.radians(angle))
            
        # Calculate new speed ensuring it doesn't go below minimum
        speed = self.speed
        total_velocity = math.sqrt(1 + self.dy * self.dy)  # dx is 1 or -1
        if total_velocity * speed > self.max_speed:
            speed = self.max_speed / total_velocity
        elif total_velocity * speed < self.min_speed:
            speed = self.min_speed / total_velocity
        
        self.velocity_x = speed * self.dx
        self.velocity_y = speed * self.dy
            
        return True
    
    def handle_wall_collision(self, scoreboard_height, arena_height):
        """Handle collision with vertical walls (top and bottom)."""
        collided = False
        
        # Handle top wall collision
        if self.rect.top <= scoreboard_height:
            self.rect.top = scoreboard_height + 5  # Push down more from wall
            self.dy = abs(self.dy)  # Force downward movement
            collided = True
            
        # Handle bottom wall collision
        elif self.rect.bottom >= arena_height:
            self.rect.bottom = arena_height - 5  # Push up more from wall
            self.dy = -abs(self.dy)  # Force upward movement
            collided = True
            
        if collided:
            # Ensure minimum speed after wall collision
            total_velocity = math.sqrt(1 + self.dy * self.dy)
            if total_velocity * self.speed < self.min_speed:
                self.speed = self.min_speed / total_velocity
            self.velocity_y = self.speed * self.dy
            
        return collided
    
    def handle_scoring(self, arena_width):
        """
        Check if ball has scored and return score information.
        For Debug Level: score when ball hits vertical walls
        """
        if self.rect.left <= 0:
            self.rect.x = (arena_width - self.size) // 2  # Reset horizontal position
            return "right"  # Right player scores
        elif self.rect.right >= arena_width:
            self.rect.x = (arena_width - self.size) // 2  # Reset horizontal position
            return "left"  # Left player scores
        return None