import pygame
import random
import math
from Modules.Submodules.Ping_Ball import Ball
from Modules.Submodules.Ping_Particles import WaterSpout

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
        self.shadow_offset = 4  # Pixels to offset shadow

    def draw(self, screen, colors, scale_rect):
        """Draw the obstacle with a drop shadow effect."""
        # Scale the rectangle for display
        scaled_rect = scale_rect(self.rect)
        
        # Create and draw shadow
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += self.shadow_offset
        shadow_rect.y += self.shadow_offset
        pygame.draw.rect(screen, (20, 20, 20), shadow_rect)  # Dark shadow color
        
        # Draw main obstacle
        pygame.draw.rect(screen, colors['BLACK'], scaled_rect)

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

class Manhole:
    """A static obstacle that can spout to affect ball trajectory."""
    def __init__(self, x, y, width, height, is_bottom=True):
        """Initialize a static manhole obstacle with two parts."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_bottom = is_bottom
        self.is_spouting = False
        
        # Vertical slab is taller for more dramatic water effect
        self.spout_height = height * 6  # Increased height for more dramatic effect
        
        # Define the two parts of the manhole
        # Horizontal slab stays at base position when dormant
        self.horizontal_rect = pygame.Rect(x, y, width, height)
        
        # Position vertical slab underneath horizontal
        vertical_y = y + height if is_bottom else y - self.spout_height
        self.vertical_rect = pygame.Rect(x, vertical_y, width, self.spout_height)
        
        # Calculate position for horizontal slab when pushed (reduced movement)
        ejection_distance = height // 2  # Reduced from full height to half height
        self.spout_position = y - ejection_distance if is_bottom else y + ejection_distance
        
        # Store initial position for resetting
        self.initial_y = y
        
        # Create water spout particle system
        spout_x = x + width // 2  # Center of manhole
        if is_bottom:
            spout_y = y  # Bottom manhole shoots up from top edge
            self.water_spout = WaterSpout(spout_x, spout_y, width, is_bottom=True)
        else:
            spout_y = y + height  # Top manhole shoots down from bottom edge
            self.water_spout = WaterSpout(spout_x, spout_y, width, is_bottom=False)
        
        # Initialize instance variables
        self.is_spouting = False
        
        # Timing variables for spouting behavior (in seconds)
        self.spout_timer = 0
        self.next_spout_time = random.uniform(5, 20)  # Random interval between 5-20 seconds
        self.spout_duration = 60  # Will be reset to 1 second (60 frames) in update

    def update(self, active_manholes, delta_time=1/60):
        """Update manhole state and handle spouting mechanics."""
        frames_per_second = 60
        
        if self.is_spouting:
            self.spout_timer += delta_time
            if self.spout_timer >= self.spout_duration / frames_per_second:
                # End spouting: return horizontal slab to original position
                self.horizontal_rect.y = self.initial_y
                self.is_spouting = False
                self.spout_timer = 0
                # Set next spout time in seconds
                self.next_spout_time = random.uniform(5, 20)
        else:
            self.spout_timer += delta_time
            if self.spout_timer >= self.next_spout_time:
                # Only start spouting if less than 2 manholes are active
                if len(active_manholes) < 2:
                    self.is_spouting = True
                    self.spout_timer = 0
                    # Push horizontal slab up/down
                    self.horizontal_rect.y = self.spout_position
                    # Reset spout duration to 1 second
                    self.spout_duration = frames_per_second

        # Update particle system when spouting
        if self.is_spouting:
            self.water_spout.update(delta_time)

    def handle_collision(self, ball):
        """Handle collision with the ball."""
        # Only check collision if spouting (static obstacle with optional collision)
        if not self.is_spouting:
            return False

        # Only check collision with horizontal slab
        if ball.rect.colliderect(self.horizontal_rect):
            # No bounce - only speed up and force direction
            ball.ball.dy = -1 if self.is_bottom else 1  # Force ball up/down based on position
            ball.ball.speed *= 1.5  # Speed boost
            ball.ball.velocity_y = ball.ball.speed * ball.ball.dy
            return True
        return False

    def draw(self, screen, colors, scale_rect):
        """Draw the manhole parts and water particles based on state."""
        # Create base position for the hole and cover
        base_rect = scale_rect(self.horizontal_rect)
        
        # Create oval effect for perspective (make height 60% of width)
        oval_height = int(base_rect.height * 0.6)
        base_oval = pygame.Rect(
            base_rect.x,
            base_rect.y + (base_rect.height - oval_height) // 2,
            base_rect.width,
            oval_height
        )

        # Always draw the dark hole in the wall first
        # Draw dark hole with pixelated edges
        hole_color = (20, 20, 20)  # Darker color for depth
        shadow_offset = 4
        
        # Draw hole shadow
        shadow_oval = base_oval.copy()
        shadow_oval.y += shadow_offset
        pygame.draw.ellipse(screen, (10, 10, 10), shadow_oval)  # Even darker shadow
        
        # Draw main hole
        pygame.draw.ellipse(screen, hole_color, base_oval)
        
        if self.is_spouting:
            # Draw water particles
            self.water_spout.draw(screen, scale_rect)
            
            # Draw the cover in its ejected position
            cover_rect = base_oval.copy()
            cover_rect.y = scale_rect(pygame.Rect(0, self.spout_position, 1, 1)).y
            
            # Draw the ejected cover with more distinct sections
            self._draw_pixelated_cover(screen, colors, cover_rect)
        else:
            # Draw the cover in its normal position
            self._draw_pixelated_cover(screen, colors, base_oval)
    
    def _draw_pixelated_cover(self, screen, colors, cover_rect):
        """Draw a pixelated manhole cover with distinct sections."""
        # Draw drop shadow
        shadow_rect = cover_rect.copy()
        shadow_rect.y += 4
        pygame.draw.ellipse(screen, (20, 20, 20), shadow_rect)
        
        # Draw outer border (dark outline)
        pygame.draw.ellipse(screen, (30, 30, 30), cover_rect)
        
        # Draw main cover (slightly smaller)
        main_rect = cover_rect.inflate(-4, -3)
        pygame.draw.ellipse(screen, colors['MANHOLE_OUTER'], main_rect)
        
        # Draw inner section
        inner_rect = main_rect.inflate(-8, -6)
        pygame.draw.ellipse(screen, colors['MANHOLE_INNER'], inner_rect)
        
        # Draw concentric circles pattern
        center_x = inner_rect.centerx
        center_y = inner_rect.centery
        
        # Outer ring
        outer_radius = inner_rect.width * 0.4
        pygame.draw.circle(screen, colors['MANHOLE_DETAIL'],
                         (int(center_x), int(center_y)),
                         int(outer_radius), 2)
        
        # Middle ring
        middle_radius = outer_radius * 0.7
        pygame.draw.circle(screen, colors['MANHOLE_DETAIL'],
                         (int(center_x), int(center_y)),
                         int(middle_radius), 2)
        
        # Inner ring
        inner_radius = outer_radius * 0.4
        pygame.draw.circle(screen, colors['MANHOLE_DETAIL'],
                         (int(center_x), int(center_y)),
                         int(inner_radius), 2)
        
        # Draw grip dots in a circular pattern
        num_dots = 8
        dot_radius = 2
        dot_distance = outer_radius * 0.85
        
        for i in range(num_dots):
            angle = (i / num_dots) * 2 * 3.14159
            dot_x = center_x + math.cos(angle) * dot_distance
            dot_y = center_y + math.sin(angle) * dot_distance
            
            pygame.draw.circle(screen, colors['MANHOLE_DETAIL'],
                             (int(dot_x), int(dot_y)),
                             dot_radius)

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
        self.glow_timer = 0
        self.base_color = (0, 255, 0)  # Bright green
        self.glow_speed = 0.05  # Speed of pulsing effect
        self.shadow_offset = 4  # Pixels to offset shadow

    def draw(self, screen, color, scale_rect):
        """Draw the power up with glowing effect, drop shadow, and symmetrical plus symbol if active."""
        if self.active:
            scaled_rect = scale_rect(self.rect)
            center = scaled_rect.center
            radius = scaled_rect.width // 2

            # Draw drop shadow
            shadow_center = (center[0] + self.shadow_offset, center[1] + self.shadow_offset)
            pygame.draw.circle(screen, (20, 20, 20), shadow_center, radius)  # Dark shadow

            # Calculate glow color
            glow_factor = abs(math.sin(self.glow_timer))
            glow_color = (
                int(max(0, min(255, self.base_color[0] * (0.5 + 0.5 * glow_factor)))),
                int(max(0, min(255, self.base_color[1] * (0.5 + 0.5 * glow_factor)))),
                int(max(0, min(255, self.base_color[2] * (0.5 + 0.5 * glow_factor))))
            )

            # Draw the glowing ball
            pygame.draw.circle(screen, glow_color, center, radius)

            # Draw symmetrical red plus symbol
            plus_color = (255, 0, 0)  # Red
            plus_size = radius * 0.6  # Consistent size relative to ball
            plus_thickness = max(2, radius // 6)  # Scaled thickness

            # Calculate plus dimensions
            half_length = plus_size
            half_thickness = plus_thickness // 2

            # Draw horizontal rectangle of plus
            plus_h_rect = pygame.Rect(
                center[0] - half_length,
                center[1] - half_thickness,
                half_length * 2,
                plus_thickness
            )
            pygame.draw.rect(screen, plus_color, plus_h_rect)

            # Draw vertical rectangle of plus
            plus_v_rect = pygame.Rect(
                center[0] - half_thickness,
                center[1] - half_length,
                plus_thickness,
                half_length * 2
            )
            pygame.draw.rect(screen, plus_color, plus_v_rect)

            # Update glow timer
            self.glow_timer += self.glow_speed
    
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