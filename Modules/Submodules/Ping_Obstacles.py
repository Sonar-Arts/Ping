import pygame
import random
from Modules.Submodules.Ping_Ball import Ball

# Goals for Sewer Level - Added for new level implementation
class Goal:
    def __init__(self, x, y, width, height, is_left_goal=True):
        """Initialize a goal with given dimensions."""
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.is_left_goal = is_left_goal
        self.rect = pygame.Rect(x, y, width, height)
    
    def handle_collision(self, ball):
        """
        Handle collision with the ball.
        Returns:
        - None: No collision
        - "left": Left player scored
        - "right": Right player scored
        - "bounce": Ball hit non-scoring side
        """
        if not ball.rect.colliderect(self.rect):
            return None
            
        # Get which side of the goal was hit
        collision_left = abs(ball.rect.right - self.rect.left)
        collision_right = abs(ball.rect.left - self.rect.right)
        collision_top = abs(ball.rect.bottom - self.rect.top)
        collision_bottom = abs(ball.rect.top - self.rect.bottom)
        
        min_collision = min(collision_left, collision_right, collision_top, collision_bottom)
        
        # For left goal
        if self.is_left_goal:
            if min_collision == collision_right:  # Ball entered from right side
                return "right"
            # Ball hit other sides, bounce
            if min_collision in (collision_left, collision_right):
                ball.ball.dx *= -1
                ball.ball.velocity_x = ball.ball.speed * ball.ball.dx
            else:
                ball.ball.dy *= -1
                ball.ball.velocity_y = ball.ball.speed * ball.ball.dy
            return "bounce"
        
        # For right goal
        else:
            if min_collision == collision_left:  # Ball entered from left side
                return "left"
            # Ball hit other sides, bounce
            if min_collision in (collision_left, collision_right):
                ball.ball.dx *= -1
                ball.ball.velocity_x = ball.ball.speed * ball.ball.dx
            else:
                ball.ball.dy *= -1
                ball.ball.velocity_y = ball.ball.speed * ball.ball.dy
            return "bounce"

class Obstacle:
    def __init__(self, x, y, width, height):
        """Initialize an obstacle with given dimensions."""
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, width, height)

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

class Portal(Obstacle):
    def __init__(self, x, y, width, height, target_portal=None):
        """Initialize a portal with given dimensions and target portal."""
        super().__init__(x, y, width, height)
        self.target_portal = target_portal
        self.teleport_cooldown = 0
    
    def set_target(self, target_portal):
        """Set the target portal for teleportation."""
        self.target_portal = target_portal
        
    def handle_collision(self, ball):
        """Handle collision by teleporting the ball to the target portal."""
        if self.teleport_cooldown > 0:  # Skip if on cooldown
            return False
            
        if ball.rect.colliderect(self.rect) and self.target_portal:
            # Preserve velocities
            curr_dx = ball.ball.dx
            curr_dy = ball.ball.dy
            curr_speed = ball.ball.speed
            
            # Calculate exit point based on whether portal is on left or right wall
            if self.rect.x == 0:  # Left wall portal
                new_x = self.target_portal.rect.right + ball.rect.width
            else:  # Right wall portal
                new_x = self.target_portal.rect.left - ball.rect.width
                
            # Use relative Y position but ensure ball stays within portal bounds
            rel_y = (ball.rect.centery - self.rect.y) / self.height
            new_y = self.target_portal.rect.y + (rel_y * self.target_portal.height)
            
            # Ensure ball stays within vertical bounds
            new_y = max(self.target_portal.rect.top + ball.rect.height/2,
                      min(new_y, self.target_portal.rect.bottom - ball.rect.height/2))
            
            # Set new position
            ball.rect.centerx = new_x
            ball.rect.centery = new_y
            
            # Maintain velocities
            ball.ball.dx = curr_dx
            ball.ball.dy = curr_dy
            ball.ball.speed = curr_speed
            ball.ball.velocity_x = curr_speed * curr_dx
            ball.ball.velocity_y = curr_speed * curr_dy
            
            # Set cooldown for both portals
            self.teleport_cooldown = 15  # About 0.25 seconds at 60 FPS
            self.target_portal.teleport_cooldown = 15
            
            return True
        return False
        
    def update_cooldown(self):
        """Update teleport cooldown timer."""
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1

class PowerUpBall:
    def __init__(self, x, y, size=20):
        """Initialize a ball-shaped power up."""
        self.rect = pygame.Rect(x, y, size, size)
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.size = size
        self.spawn_timer = 0
        self.active = True
        self.next_spawn_time = random.randint(3, 15) * 60  # 3-15 seconds (at 60 FPS)

    def draw(self, screen, color, scale_rect):
        """Draw the power up as a circle if active."""
        if self.active:
            scaled_rect = scale_rect(self.rect)
            pygame.draw.circle(screen, color, scaled_rect.center, scaled_rect.width // 2)
    
    def handle_collision(self, ball):
        """Handle collision by creating a duplicate ball with same trajectory."""
        if not self.active:
            return False
            
        if ball.rect.colliderect(self.rect):
            # Create new ball with same properties
            new_ball = Ball(ball.ball.size)
            new_ball.rect.x = self.rect.x
            new_ball.rect.y = self.rect.y
            new_ball.dx = ball.ball.dx
            new_ball.dy = ball.ball.dy
            new_ball.speed = ball.ball.speed
            new_ball.velocity_x = ball.ball.velocity_x
            new_ball.velocity_y = ball.ball.velocity_y
            
            # Deactivate power up
            self.active = False
            # Reset spawn timer
            self.spawn_timer = 0
            return new_ball
        return None
    
    def find_valid_position(self, arena_width, arena_height, scoreboard_height, obstacles):
        """Find a valid spawn position that doesn't overlap with obstacles or paddle movement areas."""
        margin = 20  # Minimum distance from walls and obstacles
        max_attempts = 50  # Maximum number of attempts to find valid position
        
        # Define paddle movement areas to avoid
        paddle_margin = 100  # Space to avoid around paddles
        left_paddle_zone = pygame.Rect(0, scoreboard_height, paddle_margin, arena_height - scoreboard_height)
        right_paddle_zone = pygame.Rect(arena_width - paddle_margin, scoreboard_height, paddle_margin, arena_height - scoreboard_height)
        
        for _ in range(max_attempts):
            # Generate random position with margins
            x = random.randint(margin + paddle_margin, arena_width - self.size - margin - paddle_margin)
            y = random.randint(scoreboard_height + margin, arena_height - self.size - margin)
            
            # Create temporary rect for collision checking
            test_rect = pygame.Rect(x, y, self.size, self.size)
            
            # Check for collisions with obstacles and paddle zones
            valid_position = True
            
            # Check paddle movement areas
            if test_rect.colliderect(left_paddle_zone) or test_rect.colliderect(right_paddle_zone):
                valid_position = False
                continue
            
            # Check other obstacles
            if obstacles:
                for obstacle in obstacles:
                    # Add margin around obstacles
                    expanded_rect = obstacle.rect.inflate(margin * 2, margin * 2)
                    if test_rect.colliderect(expanded_rect):
                        valid_position = False
                        break
            
            if valid_position:
                return x, y
                
        # If no valid position found after max attempts, use center position
        return (arena_width - self.size) // 2, (arena_height - self.size) // 2

    def update(self, ball_count, arena_width, arena_height, scoreboard_height, obstacles=None):
        """Update spawn timer and activate power up when ready."""
        if not self.active:
            self.spawn_timer += 1
            if self.spawn_timer >= self.next_spawn_time and ball_count < 10:
                # Find new valid position
                new_x, new_y = self.find_valid_position(
                    arena_width, arena_height, scoreboard_height, obstacles
                )
                self.rect.x = new_x
                self.rect.y = new_y
                
                self.active = True
                self.spawn_timer = 0
                self.next_spawn_time = random.randint(3, 15) * 60  # 3-15 seconds (at 60 FPS)
                return True
        return False