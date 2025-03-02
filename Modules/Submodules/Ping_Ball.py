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
        self.dx = 1  # Direction multiplier
        self.dy = -1  # Direction multiplier
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

    def reset_position(self, arena_width, arena_height):
        """Reset ball to center position."""
        self.rect.x = (arena_width - self.size) // 2
        self.rect.y = (arena_height - self.size) // 2
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
        """Handle collision with walls and scoreboard."""
        if self.rect.top <= scoreboard_height or self.rect.bottom >= arena_height:
            self.dy *= -1
            # Ensure minimum speed after wall collision
            total_velocity = math.sqrt(1 + self.dy * self.dy)
            if total_velocity * self.speed < self.min_speed:
                self.speed = self.min_speed / total_velocity
            self.velocity_y = self.speed * self.dy
            return True
        return False
    
    def handle_scoring(self, arena_width):
        """Check if ball has scored and return score information."""
        if self.rect.left <= 0:
            return "right"  # Right player scores
        elif self.rect.right >= arena_width:
            return "left"  # Left player scores
        return None