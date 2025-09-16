import pygame
import random
import math
from .Ping_Ball import Ball
from ..Graphics.Effects.Ping_Particles import WaterSpout

class Bumper:
    def __init__(self, x, y, radius=30):
        """Initialize a pinball bumper."""
        self.x = x
        self.y = y
        self.base_radius = radius
        self.current_radius = radius
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        
        # Animation properties
        self.hit_animation_time = 0
        self.hit_animation_duration = 0.2  # seconds
        self.max_scale = 1.2  # Maximum size during hit animation
        self.flash_intensity = 0
        self.color_transition = 0
        
        # Star properties
        self.star_points = 5
        self.star_inner_radius = radius * 0.3
        self.star_outer_radius = radius * 0.5
        
    def update(self, delta_time=1/60):
        """Update bumper animation state."""
        if self.hit_animation_time > 0:
            self.hit_animation_time = max(0, self.hit_animation_time - delta_time)
            
            # Calculate animation progress (0 to 1)
            progress = self.hit_animation_time / self.hit_animation_duration
            
            # Smooth transition for size and flash
            self.current_radius = self.base_radius * (1 + (self.max_scale - 1) * progress)
            self.flash_intensity = progress
            
            # Update collision rect
            self.rect = pygame.Rect(
                self.x - self.current_radius,
                self.y - self.current_radius,
                self.current_radius * 2,
                self.current_radius * 2
            )
            
    def handle_collision(self, ball):
        """Handle collision with the ball using circular collision detection."""
        # Calculate distance between ball center and bumper center
        ball_center = ball.rect.center
        dx = ball_center[0] - self.x
        dy = ball_center[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check for collision using current radius (which may be larger during animation)
        if distance < self.current_radius + ball.rect.width/2:
            # Start hit animation
            self.hit_animation_time = self.hit_animation_duration
            
            # Calculate normalized direction vector from bumper center to ball
            if distance > 0:  # Avoid division by zero
                dx /= distance
                dy /= distance
            else:
                dx, dy = 1, 0  # Default direction if centers overlap
            
            # Get previous ball direction to determine rotation
            prev_dx = ball.ball.dx
            prev_dy = ball.ball.dy
            
            # Adjust the angle by 1 degree
            angle = math.radians(1)
            
            # Calculate rotation direction based on previous movement to avoid loops
            cross_product = prev_dx * dy - prev_dy * dx
            if cross_product > 0:
                # Rotate clockwise
                new_dx = dx * math.cos(angle) + dy * math.sin(angle)
                new_dy = -dx * math.sin(angle) + dy * math.cos(angle)
            else:
                # Rotate counterclockwise
                new_dx = dx * math.cos(angle) - dy * math.sin(angle)
                new_dy = dx * math.sin(angle) + dy * math.cos(angle)
                
            # Increase ball speed but respect maximum speed limit
            new_speed = min(ball.ball.speed * 1.5, ball.ball.max_speed)
            ball.ball.speed = new_speed
            ball.ball.dx = new_dx
            ball.ball.dy = new_dy
            ball.ball.velocity_x = ball.ball.speed * new_dx
            ball.ball.velocity_y = ball.ball.speed * new_dy
            
            # Move ball outside bumper to prevent sticking
            new_x = self.x + (self.current_radius + ball.rect.width/2 + 1) * dx
            new_y = self.y + (self.current_radius + ball.rect.height/2 + 1) * dy
            ball.rect.center = (new_x, new_y)
            
            return True
        return False
        
    def draw(self, screen, colors, scale_rect):
        """Draw the bumper with visual effects."""
        # Scale the position and size for display
        scaled_rect = scale_rect(self.rect)
        scaled_center = scaled_rect.center
        scaled_radius = scaled_rect.width // 2
        
        # Draw drop shadow
        shadow_offset = 4
        shadow_center = (scaled_center[0] + shadow_offset, scaled_center[1] + shadow_offset)
        pygame.draw.circle(screen, (20, 20, 20), shadow_center, scaled_radius)
        
        # Base colors
        red = (220, 60, 60)
        gold = (255, 215, 0)
        yellow = (255, 255, 0)
        
        # Calculate flash-adjusted colors
        flash_color = (255, 255, 255)
        current_red = tuple(int(c1 + (c2 - c1) * self.flash_intensity)
                          for c1, c2 in zip(red, flash_color))
        current_gold = tuple(int(c1 + (c2 - c1) * self.flash_intensity)
                           for c1, c2 in zip(gold, flash_color))
        current_yellow = tuple(int(c1 + (c2 - c1) * self.flash_intensity)
                             for c1, c2 in zip(yellow, flash_color))
        
        # Draw main circle (red padding)
        pygame.draw.circle(screen, current_red, scaled_center, scaled_radius)
        
        # Draw inner circle (gold center)
        inner_radius = int(scaled_radius * 0.7)
        pygame.draw.circle(screen, current_gold, scaled_center, inner_radius)
        
        # Draw star
        star_points = []
        for i in range(self.star_points * 2):
            angle = (i * math.pi) / self.star_points
            radius = self.star_outer_radius if i % 2 == 0 else self.star_inner_radius
            scaled_radius_star = int(radius * (scaled_rect.width / (self.base_radius * 2))) # Renamed to avoid conflict
            x_star = scaled_center[0] + math.cos(angle) * scaled_radius_star # Renamed to avoid conflict
            y_star = scaled_center[1] + math.sin(angle) * scaled_radius_star # Renamed to avoid conflict
            star_points.append((x_star, y_star))
            
        pygame.draw.polygon(screen, current_yellow, star_points)

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
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
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
        pygame.draw.rect(screen, colors['WHITE'], scaled_rect)

    def handle_collision(self, ball, sound_manager=None):
        """
        Handle collision between obstacle and ball.
        Args:
            ball: The ball object that collided
            sound_manager: Optional SoundManager instance to play collision sounds
        """
        if ball.rect.colliderect(self.rect):
            # Play wall break sound if sound manager is provided
            if sound_manager:
                sound_manager.play_sfx('wall_break')

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

    def draw(self, screen, colors, scale_rect):
        """Draw the portal with a sewer-themed brick archway style."""
        scaled_rect = scale_rect(self.rect)

        # Define sewer-specific colors (use defaults if not found in 'colors')
        brick_dark = colors.get('BRICK_DARK', (60, 60, 60))
        brick_light = colors.get('BRICK_LIGHT', (75, 75, 75))
        mortar = colors.get('BRICK_MORTAR', (45, 45, 45))
        # Using a slightly contrasting but still dark glow
        portal_glow = colors.get('PORTAL_GLOW', (40, 20, 60)) # Dark purple/indigo glow
        vegetation = colors.get('VEGETATION_COLOR', (40, 80, 40))

        # 1. Draw the dark inner portal area (the void)
        # Make inner area slightly smaller than the collision rect for the frame
        inner_offset = 4 # Pixel width of the frame
        inner_rect = scaled_rect.inflate(-inner_offset * 2, -inner_offset * 2)
        pygame.draw.rect(screen, (10, 10, 10), inner_rect) # Very dark inside

        # 2. Draw the brick frame around the portal
        # Simplified brick pattern for clarity
        brick_size = inner_offset # Use offset as brick size

        # Top border bricks
        for x_brick in range(scaled_rect.left, scaled_rect.right, brick_size * 2): # Renamed x to x_brick
            pygame.draw.rect(screen, brick_dark, (x_brick, scaled_rect.top, brick_size, brick_size))
            pygame.draw.rect(screen, brick_light, (x_brick + brick_size, scaled_rect.top, brick_size, brick_size))
            pygame.draw.line(screen, mortar, (x_brick, scaled_rect.top), (x_brick, scaled_rect.top + brick_size)) # Vertical mortar
            pygame.draw.line(screen, mortar, (x_brick + brick_size, scaled_rect.top), (x_brick + brick_size, scaled_rect.top + brick_size))
            pygame.draw.line(screen, mortar, (x_brick, scaled_rect.top + brick_size), (x_brick + brick_size * 2, scaled_rect.top + brick_size)) # Horizontal mortar below

        # Bottom border bricks
        for x_brick in range(scaled_rect.left, scaled_rect.right, brick_size * 2): # Renamed x to x_brick
            pygame.draw.rect(screen, brick_light, (x_brick, scaled_rect.bottom - brick_size, brick_size, brick_size))
            pygame.draw.rect(screen, brick_dark, (x_brick + brick_size, scaled_rect.bottom - brick_size, brick_size, brick_size))
            pygame.draw.line(screen, mortar, (x_brick, scaled_rect.bottom - brick_size), (x_brick, scaled_rect.bottom)) # Vertical mortar
            pygame.draw.line(screen, mortar, (x_brick + brick_size, scaled_rect.bottom - brick_size), (x_brick + brick_size, scaled_rect.bottom))
            pygame.draw.line(screen, mortar, (x_brick, scaled_rect.bottom - brick_size), (x_brick + brick_size * 2, scaled_rect.bottom - brick_size)) # Horizontal mortar above

        # Left border bricks
        for y_brick in range(scaled_rect.top + brick_size, scaled_rect.bottom - brick_size, brick_size * 2): # Renamed y to y_brick, Avoid corners
            pygame.draw.rect(screen, brick_light, (scaled_rect.left, y_brick, brick_size, brick_size))
            pygame.draw.rect(screen, brick_dark, (scaled_rect.left, y_brick + brick_size, brick_size, brick_size))
            pygame.draw.line(screen, mortar, (scaled_rect.left, y_brick), (scaled_rect.left + brick_size, y_brick)) # Horizontal mortar
            pygame.draw.line(screen, mortar, (scaled_rect.left, y_brick + brick_size), (scaled_rect.left + brick_size, y_brick + brick_size))
            pygame.draw.line(screen, mortar, (scaled_rect.left + brick_size, y_brick), (scaled_rect.left + brick_size, y_brick + brick_size * 2)) # Vertical mortar right

        # Right border bricks
        for y_brick in range(scaled_rect.top + brick_size, scaled_rect.bottom - brick_size, brick_size * 2): # Renamed y to y_brick, Avoid corners
            pygame.draw.rect(screen, brick_dark, (scaled_rect.right - brick_size, y_brick, brick_size, brick_size))
            pygame.draw.rect(screen, brick_light, (scaled_rect.right - brick_size, y_brick + brick_size, brick_size, brick_size))
            pygame.draw.line(screen, mortar, (scaled_rect.right - brick_size, y_brick), (scaled_rect.right, y_brick)) # Horizontal mortar
            pygame.draw.line(screen, mortar, (scaled_rect.right - brick_size, y_brick + brick_size), (scaled_rect.right, y_brick + brick_size))
            pygame.draw.line(screen, mortar, (scaled_rect.right - brick_size, y_brick), (scaled_rect.right - brick_size, y_brick + brick_size * 2)) # Vertical mortar left


        # 3. Add subtle glow effect inside the portal void
        # Create a surface with alpha for transparency
        glow_surface = pygame.Surface(inner_rect.size, pygame.SRCALPHA)
        # Fill with glow color and low alpha (e.g., 60 out of 255)
        glow_surface.fill((*portal_glow, 60))
        screen.blit(glow_surface, inner_rect.topleft)

        # 4. Optional: Add a hint of vegetation/slime dripping down
        if random.random() < 0.1: # Low chance to draw slime
             slime_start_x = random.randint(inner_rect.left, inner_rect.right)
             slime_end_y = inner_rect.top + random.randint(5, 15) # Short drip
             pygame.draw.line(screen, vegetation, (slime_start_x, inner_rect.top), (slime_start_x, slime_end_y), 2)


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
    def __init__(self, x, y, width, height, is_bottom=True, properties=None):
        """Initialize a static manhole obstacle with two parts, using optional properties."""
        if properties is None:
            properties = {} # Ensure properties is a dict

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
        self.horizontal_rect = pygame.Rect(x - width // 2, y - height // 2, width, height)

        # Position vertical slab underneath horizontal
        vertical_y = y + height if is_bottom else y - self.spout_height
        self.vertical_rect = pygame.Rect(x, vertical_y, width, self.spout_height)

        # Store initial position for hole and cover resting place
        self.initial_y = y

        # Animation parameters for cover flying off
        self.cover_fly_distance = height * 2.5 # How far the cover flies vertically
        self.cover_drift_distance = width * 0.5 # How far the cover drifts horizontally

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

        # Timing variables for spouting behavior (in seconds) - Use properties or defaults
        self.spout_timer = 0
        # Get interval range from properties, default to 5-20 seconds
        self.min_interval_sec = properties.get('spout_min_interval_sec', 5)
        self.max_interval_sec = properties.get('spout_max_interval_sec', 20)
        self.next_spout_time = random.uniform(self.min_interval_sec, self.max_interval_sec)

        # Get duration from properties, default to 1 second
        self.spout_duration_sec = properties.get('spout_duration_sec', 1.0)


    def update(self, active_manholes, delta_time=1/60):
        """Update manhole state and handle spouting mechanics."""
        # Use delta_time for all timing calculations

        if self.is_spouting:
            self.spout_timer += delta_time
            # Check against duration in seconds
            if self.spout_timer >= self.spout_duration_sec:
                # End spouting
                self.is_spouting = False
                self.spout_timer = 0
                # Set next spout time using the interval properties (horizontal_rect.y no longer moved)
                self.next_spout_time = random.uniform(self.min_interval_sec, self.max_interval_sec)
        else:
            self.spout_timer += delta_time
            # Check against next spout time in seconds
            if self.spout_timer >= self.next_spout_time:
                # Only start spouting if less than 2 manholes are active
                if len(active_manholes) < 2:
                    self.is_spouting = True
                    self.spout_timer = 0 # Reset timer for duration tracking
                    # Cover position is now handled dynamically in draw()
                    # Duration is already set by self.spout_duration_sec

        # Update particle system when spouting
        if self.is_spouting:
            self.water_spout.update(delta_time)

    def handle_collision(self, ball):
        """Handle collision with the ball."""
        # Only check collision if spouting (static obstacle with optional collision)
        if not self.is_spouting:
            return False

        # Check collision with the stationary hole area when spouting
        hole_rect = pygame.Rect(self.x, self.initial_y, self.width, self.height)
        if ball.rect.colliderect(hole_rect):
            # Apply upward/downward force and speed boost
            ball.ball.dy = -1 if self.is_bottom else 1
            ball.ball.speed *= 1.5
            ball.ball.velocity_y = ball.ball.speed * ball.ball.dy
            # Prevent sticking (optional, might not be needed if force is strong)
            if self.is_bottom:
                ball.rect.bottom = hole_rect.top
            else:
                ball.rect.top = hole_rect.bottom
            return True
        return False

    def draw(self, screen, colors, scale_rect):
        """Draw the manhole parts and water particles based on state."""
        # Calculate the scaled rectangle for the stationary hole position
        hole_logic_rect = pygame.Rect(self.x, self.initial_y, self.width, self.height)
        scaled_hole_rect = scale_rect(hole_logic_rect)
        hole_radius = scaled_hole_rect.width // 2
        hole_center = scaled_hole_rect.center

        # Always draw the dark hole (top-down circle)
        hole_color = (20, 20, 20)
        shadow_offset = 4

        # Draw hole shadow (slightly offset circle)
        shadow_center = (hole_center[0], hole_center[1] + shadow_offset)
        pygame.draw.circle(screen, (10, 10, 10), shadow_center, hole_radius)

        # Draw main hole
        pygame.draw.circle(screen, hole_color, hole_center, hole_radius)

        # Determine cover position and draw
        cover_center = hole_center
        cover_radius = hole_radius

        if self.is_spouting:
            # Draw water particles originating from the hole center
            self.water_spout.draw(screen, scale_rect) # Assuming WaterSpout uses its own coords

            # Animate the cover flying off
            progress = min(1.0, self.spout_timer / self.spout_duration_sec)

            # Scale the base distances once
            scaled_fly_distance = scale_rect(pygame.Rect(0, 0, 0, self.cover_fly_distance)).height
            scaled_drift_distance = scale_rect(pygame.Rect(0, 0, self.cover_drift_distance, 0)).width

            # Vertical displacement (up for bottom, down for top) using scaled distance
            fly_offset_y = -progress * scaled_fly_distance if self.is_bottom else progress * scaled_fly_distance
            # Horizontal drift (simple sine wave for wobble) using scaled distance
            fly_offset_x = progress * scaled_drift_distance * math.sin(progress * math.pi * 4) # Faster wobble

            # Calculate animated cover center using calculated offsets and convert to integers
            cover_center_x = hole_center[0] + fly_offset_x
            cover_center_y = hole_center[1] + fly_offset_y
            cover_center = (int(cover_center_x), int(cover_center_y))

            # Draw the flying cover
            self._draw_pixelated_cover(screen, colors, cover_center, cover_radius)
        else:
            # Draw the cover in its normal position over the hole
            self._draw_pixelated_cover(screen, colors, cover_center, cover_radius)

    def _draw_pixelated_cover(self, screen, colors, center, radius):
        """Draw a pixelated top-down manhole cover (circle) with distinct sections."""
        center_x, center_y = int(center[0]), int(center[1])
        radius = int(radius)
        shadow_offset = 4

        # Draw drop shadow
        shadow_center_cover = (center_x, center_y + shadow_offset) # Renamed to avoid conflict
        pygame.draw.circle(screen, (20, 20, 20), shadow_center_cover, radius)

        # Draw outer border (dark outline) - slightly thicker
        pygame.draw.circle(screen, (30, 30, 30), center, radius)

        # Draw main cover surface (slightly smaller radius)
        main_radius = max(1, radius - 2)
        pygame.draw.circle(screen, colors['MANHOLE_OUTER'], center, main_radius)

        # Draw inner section (smaller radius)
        inner_radius_main = max(1, main_radius - 4)
        pygame.draw.circle(screen, colors['MANHOLE_INNER'], center, inner_radius_main)

        # Draw concentric circles pattern (using radii relative to inner_radius_main)
        detail_color = colors['MANHOLE_DETAIL']
        ring_thickness = 2 # Make rings slightly thicker

        # Outer ring
        outer_ring_radius = int(inner_radius_main * 0.8)
        if outer_ring_radius >= ring_thickness // 2:
             pygame.draw.circle(screen, detail_color, center, outer_ring_radius, ring_thickness)

        # Middle ring
        middle_ring_radius = int(outer_ring_radius * 0.7)
        if middle_ring_radius >= ring_thickness // 2:
            pygame.draw.circle(screen, detail_color, center, middle_ring_radius, ring_thickness)

        # Inner ring
        inner_ring_radius = int(middle_ring_radius * 0.6)
        if inner_ring_radius >= ring_thickness // 2:
            pygame.draw.circle(screen, detail_color, center, inner_ring_radius, ring_thickness)

        # Draw square notches around the innermost circle (if it exists)
        if inner_ring_radius >= ring_thickness // 2:
            num_notches = 8
            notch_size = max(2, radius // 10) # Scale notch size
            # Place notches just outside the inner ring radius
            notch_distance = inner_ring_radius + notch_size // 2 + 1

            for i in range(num_notches):
                angle_notch = (i / num_notches) * 2 * math.pi # Renamed angle to angle_notch
                # Calculate center position of the notch
                notch_center_x = center_x + math.cos(angle_notch) * notch_distance
                notch_center_y = center_y + math.sin(angle_notch) * notch_distance

                # Calculate top-left corner for the rect
                notch_x = notch_center_x - notch_size // 2
                notch_y = notch_center_y - notch_size // 2

                pygame.draw.rect(screen, detail_color,
                                 (int(notch_x), int(notch_y), notch_size, notch_size))

class PowerUpBall:
    def __init__(self, x, y, size=20):
        """Initialize a ball-shaped power up."""
        self.rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.size = size
        self.spawn_timer = 0
        self.active = False  # Start inactive to prevent immediate collision
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
            shadow_center_powerup = (center[0] + self.shadow_offset, center[1] + self.shadow_offset) # Renamed
            pygame.draw.circle(screen, (20, 20, 20), shadow_center_powerup, radius)  # Dark shadow

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
            print(f"PowerUpBall collision detected! Creating new ball...")
            # Create new raw ball with same properties
            new_ball = Ball(ball.ball.size)
            # Start new ball offset from power-up location to avoid immediate collision
            new_ball.rect.x = self.rect.x + 30  # Offset to avoid overlapping with original ball
            new_ball.rect.y = self.rect.y + 30
            new_ball.dx = ball.ball.dx
            new_ball.dy = ball.ball.dy
            new_ball.speed = ball.ball.speed
            new_ball.velocity_x = ball.ball.velocity_x
            new_ball.velocity_y = ball.ball.velocity_y
            print(f"New ball created at ({new_ball.rect.x}, {new_ball.rect.y}) with velocity ({new_ball.velocity_x}, {new_ball.velocity_y})")

            # Deactivate power up
            self.active = False
            # Reset spawn timer
            self.spawn_timer = 0
            return new_ball # Return the raw Ball instance
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
            x_pos = random.randint(margin + paddle_margin, arena_width - self.size - margin - paddle_margin) # Renamed x
            y_pos = random.randint(scoreboard_height + margin, arena_height - self.size - margin) # Renamed y

            # Create temporary rect for collision checking
            test_rect = pygame.Rect(x_pos, y_pos, self.size, self.size)

            # Check for collisions with obstacles and paddle zones
            valid_position = True

            # Check paddle movement areas
            if test_rect.colliderect(left_paddle_zone) or test_rect.colliderect(right_paddle_zone):
                valid_position = False
                continue

            # Check other obstacles
            if obstacles:
                for obstacle_item in obstacles: # Renamed obstacle
                    # Add margin around obstacles
                    expanded_rect = obstacle_item.rect.inflate(margin * 2, margin * 2)
                    if test_rect.colliderect(expanded_rect):
                        valid_position = False
                        break

            if valid_position:
                return x_pos, y_pos

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
import pygame
import math
import random
from .Ping_Ball import Ball # Assuming Ball class is needed
# Potentially need Font access later: from Modules.Submodules.Ping_Fonts import FontManager

class RouletteSpinner:
    """
    A complex obstacle that captures the ball, spins, holds it for a duration
    based on the hit segment, displays a timer, and releases it.
    """
    def __init__(self, x, y, radius=100, num_segments=38, spin_speed_deg_s=90): # Increased radius, set segments=38
        """Initialize the Roulette Spinner."""
        self.x = x
        self.y = y
        self.radius = radius
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2) # For potential spatial checks

        # Roulette properties
        # Filter out '0' and '00' from the standard sequence
        standard_numbers = [
            '0', '28', '9', '26', '30', '11', '7', '20', '32', '17', '5', '22', '34', '15', '3',
            '24', '36', '13', '1', '00', '27', '10', '25', '29', '12', '8', '19', '31', '18', '6',
            '21', '33', '16', '4', '23', '35', '14', '2'
        ]
        self.segment_numbers = [num for num in standard_numbers if num not in ('0', '00')]

        # Update num_segments based on the filtered list
        self.num_segments = len(self.segment_numbers)
        if self.num_segments > 0:
             self.segment_angle = 360 / self.num_segments
        else:
             self.segment_angle = 0 # Avoid division by zero if list is empty

        # Standard Roulette Colors (0/00 Green, alternating Red/Black)
        roulette_colors = {
            # '0': (0, 150, 0), '00': (0, 150, 0), # Zeros removed
            '1': (200, 0, 0), '2': (30, 30, 30), '3': (200, 0, 0), '4': (30, 30, 30), '5': (200, 0, 0),
            '6': (30, 30, 30), '7': (200, 0, 0), '8': (30, 30, 30), '9': (200, 0, 0), '10': (30, 30, 30),
            '11': (30, 30, 30), '12': (200, 0, 0), '13': (30, 30, 30), '14': (200, 0, 0), '15': (30, 30, 30),
            '16': (200, 0, 0), '17': (30, 30, 30), '18': (200, 0, 0), '19': (200, 0, 0), '20': (30, 30, 30),
            '21': (200, 0, 0), '22': (30, 30, 30), '23': (200, 0, 0), '24': (30, 30, 30), '25': (200, 0, 0),
            '26': (30, 30, 30), '27': (200, 0, 0), '28': (30, 30, 30), '29': (30, 30, 30), '30': (200, 0, 0),
            '31': (30, 30, 30), '32': (200, 0, 0), '33': (30, 30, 30), '34': (200, 0, 0), '35': (30, 30, 30),
            '36': (200, 0, 0)
        }
        # Map numbers to colors based on the *filtered* sequence
        self.segment_colors = [roulette_colors[num] for num in self.segment_numbers]


        self.current_angle = 0  # Degrees
        self.spin_speed = spin_speed_deg_s # Degrees per second

        # State variables
        self.captured_ball = None
        self.is_spinning = False
        self.hold_timer = 0.0  # Seconds remaining
        self.max_hold_duration = 7.0 # Seconds - Max possible hold
        self.target_hold_duration = 0.0 # Seconds - Duration for current capture

        # Ball animation parameters
        self.ball_orbit_radius_factor = 0.5 # Ball orbits at 50% of the spinner radius
        self.ball_orbit_speed_factor = 2.0 # Ball orbits twice as fast as the spinner rotates

        # Graphics / Timer Display
        self.timer_font = None
        self.number_font = None
        self.timer_font_size = max(15, int(radius * 0.3)) # Scale font size with radius
        self.number_font_size = max(10, int(radius * 0.15)) # Smaller font for numbers

        try:
            if not pygame.font.get_init():
                pygame.font.init()
            self.timer_font = pygame.font.SysFont(None, self.timer_font_size)
            self.number_font = pygame.font.SysFont(None, self.number_font_size)
        except Exception as e:
            print(f"Warning: Could not load default system font for RouletteSpinner: {e}")
            class DummyFont:
                def render(self, *args, **kwargs):
                    surf = pygame.Surface((1,1), pygame.SRCALPHA); surf.fill((0,0,0,0)); return surf
            self.timer_font = self.timer_font or DummyFont()
            self.number_font = self.number_font or DummyFont()


        self.shadow_offset = 4

    def update(self, delta_time):
        """Update spinner state: rotation, timer, ball position."""
        if self.is_spinning:
            # Update rotation
            self.current_angle = (self.current_angle + self.spin_speed * delta_time) % 360

            # Update timer
            if self.hold_timer > 0:
                self.hold_timer -= delta_time
                # Update captured ball position to orbit the center
                if self.captured_ball:
                    # Ensure ball object and its rect exist
                    if hasattr(self.captured_ball, 'rect'):
                        # Calculate orbital angle (faster than spinner)
                        orbit_angle_rad = math.radians(self.current_angle * self.ball_orbit_speed_factor)
                        # Calculate orbital radius
                        orbit_radius = self.radius * self.ball_orbit_radius_factor
                        # Calculate ball position relative to center
                        ball_x = self.x + orbit_radius * math.cos(orbit_angle_rad)
                        ball_y = self.y - orbit_radius * math.sin(orbit_angle_rad) # Pygame y-axis inverted
                        # Update ball position
                        self.captured_ball.rect.center = (int(ball_x), int(ball_y))

                    # Ensure ball physics remain stopped
                    if hasattr(self.captured_ball, 'ball'):
                        self.captured_ball.ball.velocity_x = 0
                        self.captured_ball.ball.velocity_y = 0
                        self.captured_ball.ball.speed = 0

            # Check for release
            if self.hold_timer <= 0:
                self.release_ball()

    def handle_collision(self, ball, sound_manager=None):
        """Detect collision, capture ball, and initiate spinning."""
        if self.is_spinning or not hasattr(ball, 'rect') or not hasattr(ball, 'ball'): # Don't capture if already spinning or invalid ball
            return False

        # Circular collision detection
        ball_center = ball.rect.center
        dx_roulette = ball_center[0] - self.x # Renamed dx
        dy_roulette = ball_center[1] - self.y # Renamed dy
        distance_sq = dx_roulette*dx_roulette + dy_roulette*dy_roulette
        # Ensure ball has width attribute for radius calculation
        ball_radius_check = ball.rect.width / 2 if hasattr(ball.rect, 'width') else 0 # Renamed ball_radius
        radii_sum_sq = (self.radius + ball_radius_check) ** 2

        if distance_sq < radii_sum_sq:
            # --- Collision detected ---
            self.captured_ball = ball
            self.is_spinning = True

            # Stop the ball's movement immediately
            ball.ball.velocity_x = 0
            ball.ball.velocity_y = 0
            ball.ball.speed = 0
            ball.rect.center = (self.x, self.y) # Snap to center

            # Determine hit segment
            # Angle of impact (0 degrees is right, increases counter-clockwise)
            impact_angle = math.degrees(math.atan2(-dy_roulette, dx_roulette)) % 360 # Pygame y-axis is inverted

            # Adjust impact angle by current spinner rotation to find relative hit angle
            relative_impact_angle = (impact_angle - self.current_angle) % 360

            # Determine which segment was hit (0 to num_segments - 1)
            # Ensure num_segments is not zero to avoid division error
            hit_segment_index = 0
            if self.num_segments > 0:
                 hit_segment_index = int(relative_impact_angle // self.segment_angle)


            # Calculate hold duration based on segment index (example: linear mapping)
            # Segment 0 = shortest duration, Segment N-1 = longest
            # Handle potential division by zero if num_segments is 1
            if self.num_segments > 1:
                 self.target_hold_duration = (hit_segment_index / (self.num_segments - 1)) * self.max_hold_duration
            elif self.num_segments == 1:
                 self.target_hold_duration = self.max_hold_duration / 2 # Or some default
            else: # num_segments is 0 or less, should not happen with init logic
                 self.target_hold_duration = 0


            self.hold_timer = self.target_hold_duration

            # Optional: Add sound effect trigger here
            # if sound_manager: sound_manager.play_sfx('roulette_capture')

            return True # Collision handled

        return False # No collision

    def release_ball(self):
        """Release the captured ball with velocity based on current angle."""
        if not self.captured_ball or not hasattr(self.captured_ball, 'ball') or not hasattr(self.captured_ball, 'rect'):
            return

        # Calculate release angle (opposite to the segment facing 'up' - adjust as needed)
        # Let's release it based on the current rotation angle directly for simplicity
        release_rad = math.radians(self.current_angle)

        # Calculate direction vector
        release_dx = math.cos(release_rad)
        release_dy = -math.sin(release_rad) # Pygame y-axis is inverted

        # Restore ball's speed (use its original max speed or a fixed release speed)
        # Ensure max_speed attribute exists, otherwise use a default
        release_speed = getattr(self.captured_ball.ball, 'max_speed', 500) # Default 500 if not found
        self.captured_ball.ball.speed = release_speed
        self.captured_ball.ball.dx = release_dx
        self.captured_ball.ball.dy = release_dy
        self.captured_ball.ball.velocity_x = release_speed * release_dx
        self.captured_ball.ball.velocity_y = release_speed * release_dy

        # Move ball slightly outside the spinner radius to prevent immediate re-collision
        ball_radius_release = self.captured_ball.rect.width / 2 if hasattr(self.captured_ball.rect, 'width') else 0 # Renamed
        offset_release = self.radius + ball_radius_release + 1 # Renamed offset
        self.captured_ball.rect.centerx = self.x + offset_release * release_dx
        self.captured_ball.rect.centery = self.y + offset_release * release_dy

        # Reset state
        self.captured_ball = None
        self.is_spinning = False
        self.hold_timer = 0.0
        self.target_hold_duration = 0.0

        # Optional: Add sound effect trigger here
        # if sound_manager: sound_manager.play_sfx('roulette_release')


    def draw(self, screen, colors, scale_rect):
        """Draw the updated roulette spinner graphics."""
        # Scale the core properties
        scaled_logic_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        scaled_display_rect = scale_rect(scaled_logic_rect)
        scaled_center = scaled_display_rect.center
        scaled_radius_draw = scaled_display_rect.width // 2 # Renamed scaled_radius

        if scaled_radius_draw <= 1: return # Avoid drawing if too small

        # Define radii for different parts relative to the main scaled radius
        outer_ring_radius = scaled_radius_draw
        inner_wheel_radius = int(outer_ring_radius * 0.75)
        center_gradient_radius = int(inner_wheel_radius * 0.6)
        center_eye_gold_radius = int(center_gradient_radius * 0.5)
        center_eye_black_radius = int(center_eye_gold_radius * 0.4)

        # Colors (use defaults if not in theme)
        color_white = colors.get('WHITE', (255, 255, 255))
        color_black = colors.get('BLACK', (0, 0, 0))
        color_yellow = colors.get('YELLOW', (255, 215, 0)) # Using goldish yellow
        color_light_blue = colors.get('LIGHT_BLUE', (173, 216, 230))
        color_gold = colors.get('GOLD', (255, 215, 0))
        shadow_color = (20, 20, 20, 150) # Added alpha for slight transparency

        # 1. Draw Shadow (using a surface for potential alpha blending)
        shadow_center_roulette = (scaled_center[0] + self.shadow_offset, scaled_center[1] + self.shadow_offset) # Renamed
        shadow_surface = pygame.Surface((scaled_radius_draw*2 + self.shadow_offset*2, scaled_radius_draw*2 + self.shadow_offset*2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, shadow_color, (scaled_radius_draw + self.shadow_offset, scaled_radius_draw + self.shadow_offset), scaled_radius_draw)
        screen.blit(shadow_surface, (scaled_center[0] - scaled_radius_draw, scaled_center[1] - scaled_radius_draw))


        # 2. Draw Outer Ring Segments and Numbers
        if self.num_segments > 0 and self.number_font:
            text_color = color_white # Numbers are typically white
            number_distance_factor = 0.88 # How far out the numbers are (0.0 center, 1.0 edge)

            for i in range(self.num_segments):
                segment_color = self.segment_colors[i]
                segment_num_str = self.segment_numbers[i]

                # Calculate angles for the segment polygon
                start_angle_deg = self.current_angle + i * self.segment_angle
                end_angle_deg = start_angle_deg + self.segment_angle
                start_angle_rad = math.radians(-start_angle_deg) # Negate for Pygame coord system
                end_angle_rad = math.radians(-end_angle_deg)

                # Draw segment polygon
                point_list = [scaled_center]
                num_arc_points = 5 # Fewer points needed for smaller segments
                for j in range(num_arc_points + 1):
                    angle_poly = start_angle_rad + (end_angle_rad - start_angle_rad) * j / num_arc_points # Renamed angle
                    x_poly = scaled_center[0] + outer_ring_radius * math.cos(angle_poly) # Renamed x
                    y_poly = scaled_center[1] + outer_ring_radius * math.sin(angle_poly) # Renamed y
                    point_list.append((int(x_poly), int(y_poly)))
                pygame.draw.polygon(screen, segment_color, point_list)

                # Calculate position for the number (mid-angle, near outer edge)
                mid_angle_deg = start_angle_deg + self.segment_angle / 2
                mid_angle_rad = math.radians(-mid_angle_deg) # Negate for Pygame
                num_radius = outer_ring_radius * number_distance_factor
                num_x = scaled_center[0] + num_radius * math.cos(mid_angle_rad)
                num_y = scaled_center[1] + num_radius * math.sin(mid_angle_rad)

                # Render and blit the number (upright)
                try:
                    num_surf = self.number_font.render(segment_num_str, True, text_color)
                    num_rect = num_surf.get_rect(center=(int(num_x), int(num_y)))
                    screen.blit(num_surf, num_rect)
                except Exception as e:
                    print(f"Error rendering segment number: {e}") # Handle font errors

        # 3. Draw Inner Yellow Wheel
        if inner_wheel_radius > 0:
            pygame.draw.circle(screen, color_yellow, scaled_center, inner_wheel_radius)

            # Draw black dividing lines on inner wheel
            for i in range(self.num_segments):
                line_angle_deg = self.current_angle + i * self.segment_angle
                line_angle_rad = math.radians(-line_angle_deg) # Negate for Pygame
                start_point = (scaled_center[0] + center_gradient_radius * math.cos(line_angle_rad), # Start from edge of blue center
                               scaled_center[1] + center_gradient_radius * math.sin(line_angle_rad))
                end_x = scaled_center[0] + inner_wheel_radius * math.cos(line_angle_rad)
                end_y = scaled_center[1] + inner_wheel_radius * math.sin(line_angle_rad)
                end_point = (int(end_x), int(end_y))
                pygame.draw.line(screen, color_black, start_point, end_point, max(1, scaled_radius_draw // 50)) # Thin lines

        # 4. Draw Center Gradient (Approximation) and Eye
        if center_gradient_radius > 0:
            # Simple light blue circle for gradient base
            pygame.draw.circle(screen, color_light_blue, scaled_center, center_gradient_radius)
            # Gold Eye part
            if center_eye_gold_radius > 0:
                pygame.draw.circle(screen, color_gold, scaled_center, center_eye_gold_radius)
                # Black center Eye part
                if center_eye_black_radius > 0:
                    pygame.draw.circle(screen, color_black, scaled_center, center_eye_black_radius)

        # 5. Draw Outer Border (thin white line)
        pygame.draw.circle(screen, color_white, scaled_center, outer_ring_radius, max(1, scaled_radius_draw // 40))

        # 6. Draw Timer if spinning and font is available (Draw last to be on top)
        if self.is_spinning and self.timer_font:
            display_time = max(0, self.hold_timer)
            timer_text = f"{display_time:.1f}"
            try:
                text_surface = self.timer_font.render(timer_text, True, color_white)
                # Add black outline/shadow for better visibility
                outline_offset_timer = max(1, self.timer_font_size // 15) # Renamed outline_offset
                text_surface_shadow = self.timer_font.render(timer_text, True, color_black)
                shadow_pos = (scaled_center[0] - text_surface.get_width() // 2 + outline_offset_timer,
                              scaled_center[1] - text_surface.get_height() // 2 + outline_offset_timer)
                screen.blit(text_surface_shadow, shadow_pos)

                # Blit main text
                text_rect = text_surface.get_rect(center=scaled_center)
                screen.blit(text_surface, text_rect)
            except Exception as e:
                 print(f"Error rendering timer text: {e}")


        # Note: The captured ball itself is positioned in update().
        # The main game loop should ideally skip drawing the ball if it's captured by the spinner.
# --- Piston Obstacle Class ---

class PistonObstacle:
    def __init__(self, x, y, width=20, height=30, properties=None):
        """Initialize a Piston obstacle."""
        if properties is None:
            properties = {}

        self.x = x # Logical center X
        self.y = y # Logical center Y (of the base)
        self.width = width
        self.height = height # Total logical height (base + head)

        # Animation state (similar to background version)
        self.state = 'down' # 'down', 'up', 'steaming'
        self.timer = random.uniform(0.0, properties.get('up_interval', 6.0)) # Random start time
        self.up_interval = properties.get('up_interval', random.uniform(4.0, 8.0))
        self.up_duration = properties.get('up_duration', 0.5)
        self.steam_duration = properties.get('steam_duration', 0.3)
        self.steam_particles = [] # List to hold active steam particles

        # Calculate base and head heights based on total height
        self.base_height_ratio = 0.4
        self.head_height_ratio = 0.6
        self.base_height = self.height * self.base_height_ratio
        self.head_height = self.height * self.head_height_ratio

        # Define the base rectangle (centered horizontally, bottom aligned with self.y)
        self.base_rect_logic = pygame.Rect(
            self.x - self.width / 2,
            self.y - self.base_height / 2, # Centered vertically around self.y for base
            self.width,
            self.base_height
        )
        # The head rect position will be calculated dynamically during drawing/update

        # Collision Rect (using the base for now, could be dynamic later)
        self.rect = self.base_rect_logic.copy()


    def update(self, delta_time):
        """Update piston animation state and steam particles."""
        self.timer += delta_time

        # --- Piston State Machine ---
        if self.state == 'down':
            if self.timer >= self.up_interval:
                self.state = 'up'
                self.timer = 0.0
        elif self.state == 'up':
            if self.timer >= self.up_duration:
                self.state = 'steaming'
                self.timer = 0.0
                # Add steam particles when reaching the top
                # Need scale here - assuming scale=1 for particle velocity for now
                # A better approach would pass scale or scale_rect to update/draw
                scale_piston = 1.0 # Placeholder - Ideally get from compiler/renderer
                scaled_width_piston = self.width * scale_piston # Use current scale
                steam_radius_base = scaled_width_piston * 0.8
                base_rect_top_scaled = self.base_rect_logic.top * scale_piston # Approximate scaled pos

                for _ in range(15): # Number of steam particles
                    self.steam_particles.append({
                        'pos': [self.x * scale_piston, base_rect_top_scaled], # Start at approx scaled top center
                        'vel': [random.uniform(-20*scale_piston, 20*scale_piston), random.uniform(-40*scale_piston, -10*scale_piston)], # Upward velocity
                        'radius': random.uniform(steam_radius_base * 0.5, steam_radius_base),
                        'lifetime': random.uniform(0.2, 0.5),
                        'timer': 0.0
                    })
        elif self.state == 'steaming':
            if self.timer >= self.steam_duration:
                self.state = 'down'
                self.timer = 0.0 # Reset timer for 'down' interval

        # --- Update Steam Particles ---
        active_steam_particles = []
        for particle in self.steam_particles:
            particle['timer'] += delta_time
            if particle['timer'] < particle['lifetime']:
                particle['pos'][0] += particle['vel'][0] * delta_time
                particle['pos'][1] += particle['vel'][1] * delta_time
                active_steam_particles.append(particle)
        self.steam_particles = active_steam_particles


    def handle_collision(self, ball, sound_manager=None):
        """Handle collision with the piston (treat as solid obstacle)."""
        # Determine the current collision rectangle based on state
        current_head_height = 0
        if self.state == 'up' or self.state == 'steaming':
            progress_piston = 1.0 if self.state == 'steaming' else min(1.0, self.timer / self.up_duration) # Renamed progress
            current_head_height = self.head_height * progress_piston

        # Combine base and head rects for collision
        # Head rect is positioned above the base rect
        head_rect_logic = pygame.Rect(
            self.base_rect_logic.left,
            self.base_rect_logic.top - current_head_height,
            self.width,
            current_head_height
        )
        # Use the union of base and potentially extended head for collision
        collision_rect_logic = self.base_rect_logic.union(head_rect_logic)

        if ball.rect.colliderect(collision_rect_logic):
            # Play sound if available
            if sound_manager:
                sound_manager.play_sfx('wall') # Or a specific piston sound

            # Basic bounce logic (same as Obstacle)
            collision_left_piston = abs(ball.rect.right - collision_rect_logic.left) # Renamed
            collision_right_piston = abs(ball.rect.left - collision_rect_logic.right) # Renamed
            collision_top_piston = abs(ball.rect.bottom - collision_rect_logic.top) # Renamed
            collision_bottom_piston = abs(ball.rect.top - collision_rect_logic.bottom) # Renamed

            min_collision_piston = min(collision_left_piston, collision_right_piston, collision_top_piston, collision_bottom_piston) # Renamed

            if min_collision_piston in (collision_left_piston, collision_right_piston):
                ball.ball.dx *= -1
                ball.ball.velocity_x = ball.ball.speed * ball.ball.dx
            else:
                ball.ball.dy *= -1
                ball.ball.velocity_y = ball.ball.speed * ball.ball.dy

            # Prevent sticking
            if min_collision_piston == collision_left_piston: ball.rect.right = collision_rect_logic.left
            elif min_collision_piston == collision_right_piston: ball.rect.left = collision_rect_logic.right
            elif min_collision_piston == collision_top_piston: ball.rect.bottom = collision_rect_logic.top
            else: ball.rect.top = collision_rect_logic.bottom

            return True
        return False

    def draw(self, screen, colors, scale_rect):
        """Draw the piston based on its current state."""
        # Get scaled dimensions and positions
        scaled_base_rect = scale_rect(self.base_rect_logic)
        scaled_width_draw = scaled_base_rect.width # Renamed scaled_width
        scaled_base_height = scaled_base_rect.height
        scaled_head_height_max = scale_rect(pygame.Rect(0,0,0,self.head_height)).height

        # Colors from theme or defaults
        piston_base_col = colors.get('PISTON_METAL_BASE', (90, 90, 100))
        piston_shadow_col = colors.get('PISTON_METAL_SHADOW', (60, 60, 70))
        piston_highlight_col = colors.get('PISTON_METAL_HIGHLIGHT', (130, 130, 140))
        steam_core_col = colors.get('STEAM_COLOR_CORE', (230, 230, 230, 200))
        steam_fade_col = colors.get('STEAM_COLOR_FADE', (180, 180, 180, 100))

        # --- Draw Piston Base ---
        shadow_offset_piston = max(1, int(1 * (scaled_width_draw / self.width if self.width else 1))) # Renamed, added check for self.width
        pygame.draw.rect(screen, piston_base_col, scaled_base_rect, border_radius=int(2*(scaled_width_draw / self.width if self.width else 1)))
        # Base Shading
        shadow_rect_piston = scaled_base_rect.move(shadow_offset_piston, shadow_offset_piston) # Renamed
        shadow_rect_piston.width -= shadow_offset_piston
        shadow_rect_piston.height -= shadow_offset_piston
        pygame.draw.rect(screen, piston_shadow_col, shadow_rect_piston, border_radius=int(1.5*(scaled_width_draw / self.width if self.width else 1)))
        # Base Highlight
        highlight_rect_piston = scaled_base_rect.move(-shadow_offset_piston, -shadow_offset_piston) # Renamed
        highlight_rect_piston.width = scaled_base_rect.width
        highlight_rect_piston.height = scaled_base_rect.height
        pygame.draw.rect(screen, piston_highlight_col, highlight_rect_piston, width=shadow_offset_piston, border_top_left_radius=int(2*(scaled_width_draw / self.width if self.width else 1)), border_bottom_left_radius=int(2*(scaled_width_draw / self.width if self.width else 1)), border_top_right_radius=int(2*(scaled_width_draw / self.width if self.width else 1)))

        # --- Calculate and Draw Piston Head ---
        current_scaled_head_height = 0
        head_y_offset_scaled = 0

        if self.state == 'up' or self.state == 'steaming':
            progress_draw = 1.0 if self.state == 'steaming' else min(1.0, self.timer / self.up_duration) # Renamed progress
            current_scaled_head_height = scaled_head_height_max * progress_draw
            head_y_offset_scaled = -current_scaled_head_height # Move upwards

        # Draw head if it has height
        if current_scaled_head_height > 0:
            scaled_head_rect = pygame.Rect(scaled_base_rect.left, scaled_base_rect.top + head_y_offset_scaled,
                                            scaled_width_draw, current_scaled_head_height)
            pygame.draw.rect(screen, piston_base_col, scaled_head_rect, border_radius=int(2*(scaled_width_draw / self.width if self.width else 1)))
            # Head Shading/Highlight
            head_shadow_rect = scaled_head_rect.move(shadow_offset_piston, shadow_offset_piston)
            head_shadow_rect.width -= shadow_offset_piston
            head_shadow_rect.height -= shadow_offset_piston
            pygame.draw.rect(screen, piston_shadow_col, head_shadow_rect, border_radius=int(1.5*(scaled_width_draw / self.width if self.width else 1)))
            head_highlight_rect = scaled_head_rect.move(-shadow_offset_piston, -shadow_offset_piston)
            head_highlight_rect.width = scaled_head_rect.width
            head_highlight_rect.height = scaled_head_rect.height
            pygame.draw.rect(screen, piston_highlight_col, head_highlight_rect, width=shadow_offset_piston, border_top_left_radius=int(2*(scaled_width_draw / self.width if self.width else 1)), border_top_right_radius=int(2*(scaled_width_draw / self.width if self.width else 1)))

        # --- Draw Steam Particles ---
        # Need scale for particle radius calculation
        scale_steam = scaled_width_draw / self.width if self.width else 1.0 # Estimate scale safely, Renamed scale
        for particle in self.steam_particles:
            alpha_ratio = 1.0 - (particle['timer'] / particle['lifetime'])
            current_radius_steam = int(particle['radius'] * alpha_ratio * scale_steam) # Scale radius here, Renamed current_radius
            if current_radius_steam >= 1:
                 center_pos_steam = (int(particle['pos'][0]), int(particle['pos'][1])) # Position is already scaled approx, Renamed center_pos
                 # Draw outer fade circle
                 fade_radius = current_radius_steam
                 fade_color = (steam_fade_col[0], steam_fade_col[1], steam_fade_col[2], int(steam_fade_col[3] * alpha_ratio * 0.8))
                 pygame.draw.circle(screen, fade_color, center_pos_steam, fade_radius)
                 # Draw inner core circle
                 core_radius = max(1, int(current_radius_steam * 0.6))
                 core_color = (steam_core_col[0], steam_core_col[1], steam_core_col[2], int(steam_core_col[3] * alpha_ratio))
                 pygame.draw.circle(screen, core_color, center_pos_steam, core_radius)


# --- Tesla Coil Obstacle Class ---

class TeslaCoilObstacle:
    def __init__(self, x, y, base_radius=15, top_radius=8, height=40, properties=None):
        """Initialize a Tesla Coil obstacle."""
        if properties is None:
            properties = {}

        self.x = x # Logical center X
        self.y = y # Logical center Y (of the whole object)
        self.base_radius_logic = base_radius
        self.top_radius_logic = top_radius
        self.height_logic = height

        # Animation state
        self.timer = random.uniform(0.0, properties.get('spark_interval', 2.75)) # Random start time
        self.spark_interval = properties.get('spark_interval', random.uniform(1.5, 4.0))
        self.spark_duration = properties.get('spark_duration', 0.15)
        self.sparking = False
        self.spark_points = [] # List of lists (branches)

        # Define collision rect (approximated by the base sphere for simplicity)
        self.rect = pygame.Rect(
            self.x - self.base_radius_logic,
            self.y + self.height_logic / 2 - self.base_radius_logic, # Y pos of base center
            self.base_radius_logic * 2,
            self.base_radius_logic * 2
        )

    def update(self, delta_time, scale=1.0): # Pass scale for spark generation
        """Update tesla coil animation state."""
        self.timer += delta_time

        # Handle sparking state
        if self.sparking:
            if self.timer >= self.spark_duration:
                self.sparking = False
                self.timer = 0.0 # Reset timer for interval
                self.spark_points = []
        else:
            if self.timer >= self.spark_interval:
                self.sparking = True
                self.timer = 0.0 # Reset timer for duration
                # Generate spark points (needs scaled positions)
                self.spark_points = []
                num_branches = random.randint(1, 3)
                scaled_height_tesla = self.height_logic * scale # Renamed scaled_height
                spark_length_max = scaled_height_tesla * 1.5
                # Calculate scaled top center Y
                top_center_y_scaled = (self.y - self.height_logic / 2) * scale
                scaled_center_x_tesla = self.x * scale # Scaled X center, Renamed scaled_center_x

                for _ in range(num_branches):
                    # Start sparks from scaled top center X, Y
                    branch = [(scaled_center_x_tesla, top_center_y_scaled)]
                    num_segments_spark = random.randint(4, 7) # Renamed num_segments
                    current_pos_spark = list(branch[0]) # Renamed current_pos
                    current_angle_spark = random.uniform(-math.pi/3, math.pi/3) # Renamed current_angle

                    for i in range(num_segments_spark):
                        current_angle_spark += random.uniform(-math.pi/3, math.pi/3)
                        length_spark = random.uniform(spark_length_max * 0.05, spark_length_max * 0.25) # Renamed length
                        end_x_spark = current_pos_spark[0] + length_spark * math.sin(current_angle_spark) # Renamed end_x
                        end_y_spark = current_pos_spark[1] - length_spark * math.cos(current_angle_spark) # Move upwards, Renamed end_y
                        current_pos_spark = [end_x_spark, end_y_spark]
                        branch.append(tuple(current_pos_spark))
                    self.spark_points.append(branch)


    def handle_collision(self, ball, sound_manager=None):
        """Handle collision with the tesla coil (treat as solid obstacle)."""
        # Use the base rect for collision detection
        if ball.rect.colliderect(self.rect):
             # Play sound if available
            if sound_manager:
                sound_manager.play_sfx('wall') # Or a specific zap sound

            # Basic bounce logic
            collision_left_tesla = abs(ball.rect.right - self.rect.left) # Renamed
            collision_right_tesla = abs(ball.rect.left - self.rect.right) # Renamed
            collision_top_tesla = abs(ball.rect.bottom - self.rect.top) # Renamed
            collision_bottom_tesla = abs(ball.rect.top - self.rect.bottom) # Renamed

            min_collision_tesla = min(collision_left_tesla, collision_right_tesla, collision_top_tesla, collision_bottom_tesla) # Renamed

            if min_collision_tesla in (collision_left_tesla, collision_right_tesla):
                ball.ball.dx *= -1
                ball.ball.velocity_x = ball.ball.speed * ball.ball.dx
            else:
                ball.ball.dy *= -1
                ball.ball.velocity_y = ball.ball.speed * ball.ball.dy

            # Prevent sticking
            if min_collision_tesla == collision_left_tesla: ball.rect.right = self.rect.left
            elif min_collision_tesla == collision_right_tesla: ball.rect.left = self.rect.right
            elif min_collision_tesla == collision_top_tesla: ball.rect.bottom = self.rect.top
            else: ball.rect.top = self.rect.bottom

            return True
        return False


    def draw(self, screen, colors, scale_rect):
        """Draw the tesla coil and sparks."""
        # Scale core dimensions
        scaled_center_x_draw, scaled_center_y_draw = scale_rect(pygame.Rect(self.x, self.y, 0, 0)).center # Renamed
        scaled_base_radius_draw = scale_rect(pygame.Rect(0,0, self.base_radius_logic, 0)).width # Renamed
        scaled_top_radius_draw = scale_rect(pygame.Rect(0,0, self.top_radius_logic, 0)).width # Renamed
        scaled_height_draw = scale_rect(pygame.Rect(0,0,0, self.height_logic)).height # Renamed
        scale_draw = scaled_height_draw / self.height_logic if self.height_logic else 1.0 # Estimate scale, Renamed scale

        # Calculate scaled vertical positions
        base_center_y_scaled = scaled_center_y_draw + scaled_height_draw / 2 # Bottom center of base sphere
        top_center_y_scaled_draw = scaled_center_y_draw - scaled_height_draw / 2 # Top center of top sphere, Renamed

        # Colors
        tesla_base_col = colors.get('TESLA_COIL_BASE', (60, 50, 80))
        tesla_highlight_col = colors.get('TESLA_COIL_HIGHLIGHT', (90, 80, 110))
        spark_core_col = colors.get('TESLA_SPARK_CORE', (255, 255, 255))
        spark_glow_col = colors.get('TESLA_SPARK_GLOW', (200, 200, 255, 150))

        # Draw base sphere
        if scaled_base_radius_draw > 0:
            pygame.draw.circle(screen, tesla_base_col, (scaled_center_x_draw, base_center_y_scaled), scaled_base_radius_draw)
            highlight_offset_tesla = scaled_base_radius_draw * 0.3 # Renamed
            pygame.draw.circle(screen, tesla_highlight_col, (scaled_center_x_draw - highlight_offset_tesla, base_center_y_scaled - highlight_offset_tesla), int(scaled_base_radius_draw * 0.5))

        # Draw connecting shaft
        if scaled_top_radius_draw > 0 and scaled_height_draw > 0:
            shaft_rect_scaled = pygame.Rect(scaled_center_x_draw - scaled_top_radius_draw, top_center_y_scaled_draw,
                                            scaled_top_radius_draw * 2, scaled_height_draw)
            pygame.draw.rect(screen, tesla_base_col, shaft_rect_scaled)
            pygame.draw.line(screen, tesla_highlight_col, shaft_rect_scaled.topleft, shaft_rect_scaled.bottomleft, max(1, int(scale_draw))) # Left highlight

        # Draw top sphere
        if scaled_top_radius_draw > 0:
            pygame.draw.circle(screen, tesla_base_col, (scaled_center_x_draw, top_center_y_scaled_draw), scaled_top_radius_draw)
            top_highlight_offset = scaled_top_radius_draw * 0.3
            pygame.draw.circle(screen, tesla_highlight_col, (scaled_center_x_draw - top_highlight_offset, top_center_y_scaled_draw - top_highlight_offset), int(scaled_top_radius_draw * 0.5))

        # Draw sparks if active
        if self.sparking and self.spark_points:
            spark_core_thickness = max(1, int(1.5 * scale_draw))
            spark_glow_thickness = max(2, int(4 * scale_draw))

            # Use a temporary surface for glow
            # Ensure surface size matches screen to avoid coordinate issues
            screen_width, screen_height = screen.get_size()
            glow_surf_tesla = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA) # Renamed
            glow_surf_tesla.fill((0,0,0,0))

            for branch in self.spark_points:
                 if len(branch) > 1:
                     # Draw glow on temp surface (using already scaled points from update)
                     pygame.draw.lines(glow_surf_tesla, spark_glow_col, False, branch, spark_glow_thickness)
                     # Draw core spark on main surface
                     pygame.draw.lines(screen, spark_core_col, False, branch, spark_core_thickness)

            # Blit the glow surface
            screen.blit(glow_surf_tesla, (0,0))
class GhostObstacle:
    MAX_GHOSTS_ON_SCREEN = 4
    active_ghost_count = 0
    ghost_possessing_ball = None

    def __init__(self, x, y, width, height, arena_rect, game_ball_instance, properties=None):
        """Initialize a Ghost obstacle."""
        if properties is None:
            properties = {}

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        self.arena_rect = arena_rect # To keep ghost within bounds
        self.game_ball = game_ball_instance # Reference to the main game ball

        self.color = (200, 200, 255, 150) # Semi-transparent white/blue
        self.possessed_color = (255, 100, 100, 200) # Reddish when possessing
        self.current_color = self.color

        # Body shape components
        self.body_components = []
        num_components = random.randint(2, 4) # Main body + 1-3 smaller blobs
        for i in range(num_components):
            if i == 0: # Main component
                offset_x_factor = 0.0
                offset_y_factor = 0.0
                size_x_factor = 1.0
                size_y_factor = 0.8 # Original body height factor relative to scaled_rect.height
            else: # Smaller blobs
                offset_x_factor = random.uniform(-0.25, 0.25)
                offset_y_factor = random.uniform(-0.25, 0.25)
                size_x_factor = random.uniform(0.3, 0.6)
                size_y_factor = random.uniform(0.3, 0.7) # Relative to scaled_rect.height
            self.body_components.append({
                'offset_x_factor': offset_x_factor,
                'offset_y_factor': offset_y_factor,
                'size_x_factor': size_x_factor,
                'size_y_factor': size_y_factor,
            })

        self.state = "APPEARING" # Possible states: APPEARING, FLOATING, RUSHING, POSSESSING, FADING_OUT
        self.state_timer = 0.0
        self.visible = False # Start invisible, then fade in

        # Timers and durations
        self.appear_duration = 1.0 # seconds
        self.float_duration = random.uniform(5.0, 10.0)
        self.possess_duration = 3.0
        self.fade_out_duration = 1.0

        # Movement
        self.float_speed = properties.get('float_speed', 50) # pixels per second
        self.rush_speed = properties.get('rush_speed', 300) # pixels per second
        self.avoid_light_speed = properties.get('avoid_light_speed', 75) # Speed to move away from light
        self.avoid_radial_weight = properties.get('avoid_radial_weight', 0.3)
        self.avoid_tangential_weight = properties.get('avoid_tangential_weight', 0.7)
        self.velocity_x = 0
        self.velocity_y = 0
        self._last_chosen_tangent_idx = random.choice([0, 1]) # 0 for first tangent, 1 for second
        self._set_random_float_direction()

        # Possession
        self.possessed_ball_original_dx = 0
        self.possessed_ball_original_dy = 0
        self.possessed_ball_original_speed = 0
        
        # Shadow
        self.shadow_offset = 4

        self.alpha = 0 # For fade in/out
        self.is_controlled_externally = False
        self._initial_fade_alpha = 0 # For smooth fading from current alpha

        # Bobbing animation
        self.bob_timer = random.uniform(0, 2 * math.pi)
        self.bob_amplitude_factor = 0.05 # Percentage of height
        self.bob_speed = 2.5 # Radians per second

        self._generate_face_features() # Add this line to generate face features

        if GhostObstacle.active_ghost_count < GhostObstacle.MAX_GHOSTS_ON_SCREEN:
            GhostObstacle.active_ghost_count += 1
            self.is_active_instance = True
        else:
            self.is_active_instance = False # This instance won't do anything if max is reached
            self.state = "INACTIVE" # A state to signify it shouldn't run update/draw logic

    def _generate_face_features(self):
        """Generates random facial features for the ghost."""
        self.face_features = {}

        # Eye Types
        eye_types = ['normal', 'wide', 'squint', 'uneven_size', 'uneven_y', 'offset_x',
                     'angry_slant', 'sad_droop', 'surprised_round']
        self.face_features['eye_type'] = random.choice(eye_types)

        # Pupil Types
        pupil_types = ['dot', 'slit_vertical', 'none'] # 'slit_horizontal' could be added
        self.face_features['pupil_type'] = random.choice(pupil_types)
        self.face_features['pupil_scale_factor'] = random.uniform(0.3, 0.6) # Relative to eye radius

        # Eyebrow Types
        eyebrow_types = ['flat', 'angled_in', 'angled_out', 'raised_center', 'none']
        self.face_features['eyebrow_type'] = random.choice(eyebrow_types)
        self.face_features['eyebrow_length_factor'] = random.uniform(0.8, 1.2) # Relative to eye width
        self.face_features['eyebrow_thickness_factor'] = random.uniform(0.1, 0.25) # Relative to eye height
        self.face_features['eyebrow_y_offset_factor'] = random.uniform(0.3, 0.6) # Upwards from eye center, relative to eye height

        # Base parameters for eyes (can be overridden by type)
        self.face_features['left_eye_scale_x'] = 1.0
        self.face_features['left_eye_scale_y'] = 1.0
        self.face_features['right_eye_scale_x'] = 1.0
        self.face_features['right_eye_scale_y'] = 1.0
        self.face_features['left_eye_offset_y'] = 0  # Factor of eye radius
        self.face_features['right_eye_offset_y'] = 0 # Factor of eye radius
        self.face_features['left_eye_offset_x_factor'] = 0  # Relative to default position
        self.face_features['right_eye_offset_x_factor'] = 0 # Relative to default position
        self.face_features['eye_angle_deg'] = 0 # For slanted eyes

        eye_type = self.face_features['eye_type']
        if eye_type == 'wide':
            self.face_features['left_eye_scale_x'] = 1.2
            self.face_features['left_eye_scale_y'] = 1.2
            self.face_features['right_eye_scale_x'] = 1.2
            self.face_features['right_eye_scale_y'] = 1.2
        elif eye_type == 'squint':
            self.face_features['left_eye_scale_y'] = 0.5
            self.face_features['right_eye_scale_y'] = 0.5
            self.face_features['left_eye_scale_x'] = 1.1
            self.face_features['right_eye_scale_x'] = 1.1
        elif eye_type == 'uneven_size':
            self.face_features['left_eye_scale_x'] = random.uniform(0.7, 1.3)
            self.face_features['left_eye_scale_y'] = random.uniform(0.7, 1.3)
            self.face_features['right_eye_scale_x'] = random.uniform(0.7, 1.3)
            self.face_features['right_eye_scale_y'] = random.uniform(0.7, 1.3)
        elif eye_type == 'uneven_y':
            self.face_features['left_eye_offset_y'] = random.uniform(-0.1, 0.1)
            self.face_features['right_eye_offset_y'] = random.uniform(-0.1, 0.1)
        elif eye_type == 'offset_x':
            self.face_features['left_eye_offset_x_factor'] = random.uniform(-0.3, 0.3)
            self.face_features['right_eye_offset_x_factor'] = random.uniform(-0.3, 0.3)
        elif eye_type == 'angry_slant':
            self.face_features['eye_angle_deg'] = 15 # Slanted downwards towards center
            self.face_features['left_eye_scale_y'] = 0.8
            self.face_features['right_eye_scale_y'] = 0.8
        elif eye_type == 'sad_droop':
            self.face_features['eye_angle_deg'] = -15 # Slanted upwards towards center (drooping outwards)
            self.face_features['left_eye_scale_y'] = 0.9
            self.face_features['right_eye_scale_y'] = 0.9
        elif eye_type == 'surprised_round':
            self.face_features['left_eye_scale_x'] = 1.3
            self.face_features['left_eye_scale_y'] = 1.3
            self.face_features['right_eye_scale_x'] = 1.3
            self.face_features['right_eye_scale_y'] = 1.3
            self.face_features['pupil_scale_factor'] = random.uniform(0.2, 0.4) # Smaller pupils for surprise

        # Mouth Types
        mouth_types = ['smile', 'frown', 'neutral_line', 'o_shape', 'wavy_line', 'no_mouth', 'smirk',
                       'jagged_line', 'open_circle_surprise']
        self.face_features['mouth_type'] = random.choice(mouth_types)
        self.face_features['mouth_offset_y_factor'] = random.uniform(-0.1, 0.1)  # Factor of body height
        self.face_features['mouth_offset_x_factor'] = random.uniform(-0.1, 0.1) # Factor of body width
        self.face_features['mouth_width_factor'] = random.uniform(0.2, 0.5)  # Factor of body width
        self.face_features['mouth_height_factor'] = random.uniform(0.05, 0.2) # Factor of body height for arcs/o_shape (increased max for surprise)
        if self.face_features['mouth_type'] == 'open_circle_surprise':
            self.face_features['mouth_width_factor'] = random.uniform(0.25, 0.4)
            self.face_features['mouth_height_factor'] = self.face_features['mouth_width_factor'] # Make it circular

    def _set_random_float_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.velocity_x = math.cos(angle) * self.float_speed
        self.velocity_y = math.sin(angle) * self.float_speed

    def _get_direction_to_ball(self):
        if not self.game_ball:
            return 0, 0
        
        ball_center_x, ball_center_y = self.game_ball.rect.center
        dx = ball_center_x - self.rect.centerx
        dy = ball_center_y - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance == 0:
            return random.uniform(-1, 1), random.uniform(-1, 1) # Avoid division by zero, move randomly
        
        return dx / distance, dy / distance

    def update(self, delta_time, game_ball_instance, candles=None, pickles_list=None, scale_factor=1.0, scale_rect_func=None):
        if not self.is_active_instance or self.state == "INACTIVE" or self.is_controlled_externally:
            # If controlled externally (e.g., by Pickles), ghost doesn't update its own logic.
            # Its position will be set by the external controller.
            return

        self.state_timer += delta_time
        self.game_ball = game_ball_instance # Keep game_ball reference updated

        is_avoiding_light = False
        if self.state in ["APPEARING", "FLOATING", "RUSHING"] and candles and scale_rect_func and scale_factor > 0:
            ghost_screen_rect = scale_rect_func(self.rect)
            if ghost_screen_rect and ghost_screen_rect.width > 0 and ghost_screen_rect.height > 0:
                for candle_obj_wrapper in candles:
                    if candle_obj_wrapper and hasattr(candle_obj_wrapper, 'get_light_properties'):
                        light_props = candle_obj_wrapper.get_light_properties(scale_factor)
                        light_x, light_y = light_props['x'], light_props['y']
                        light_radius, light_intensity = light_props['radius'], light_props['intensity']

                        if light_intensity > 0.1 and light_radius > 0:
                            dx_light = ghost_screen_rect.centerx - light_x
                            dy_light = ghost_screen_rect.centery - light_y
                            distance_sq_light = dx_light*dx_light + dy_light*dy_light
                            effective_ghost_radius = ghost_screen_rect.width / 2
                            
                            # Critical exposure distance: if ghost center is within, say, 30% of light radius or very close to light source
                            critical_distance_sq = (light_radius * 0.3)**2
                            # Also consider if ghost is almost on top of the light source, even if radius is small
                            very_close_distance_sq = (effective_ghost_radius * 0.5)**2

                            if distance_sq_light < critical_distance_sq or distance_sq_light < very_close_distance_sq:
                                if self.state != "FADING_OUT": # Avoid re-triggering if already fading
                                    self._initial_fade_alpha = self.alpha # Store current alpha for smooth fade
                                    self.state = "FADING_OUT"
                                    self.state_timer = 0.0
                                    if GhostObstacle.ghost_possessing_ball == self: # Unpossess if critically hit by light
                                        self._unpossess_ball(force_fade_from_current_alpha=True) # Force fade from current alpha
                                return # Ghost is fading, no further updates this frame for avoidance/movement

                            if distance_sq_light < (light_radius + effective_ghost_radius)**2 and distance_sq_light > 0.001:
                                is_avoiding_light = True
                                dist_light = math.sqrt(distance_sq_light)
                                # dx_light, dy_light points from light to ghost. This is the radial direction for avoidance.
                                radial_dx = dx_light / dist_light
                                radial_dy = dy_light / dist_light

                                # Calculate tangential vectors (normalized)
                                tangent1_dx = -radial_dy
                                tangent1_dy = radial_dx
                                tangent2_dx = radial_dy
                                tangent2_dy = -radial_dx
                                
                                tangents = [(tangent1_dx, tangent1_dy), (tangent2_dx, tangent2_dy)]
                                chosen_tangent_dx, chosen_tangent_dy = 0, 0 # Initialize

                                if self.state == "FLOATING" or self.state == "APPEARING":
                                    # Alternate choice for tangential direction
                                    chosen_idx = 1 - self._last_chosen_tangent_idx
                                    chosen_tangent_dx, chosen_tangent_dy = tangents[chosen_idx]
                                    self._last_chosen_tangent_idx = chosen_idx
                                elif self.state == "RUSHING":
                                    ball_dir_x, ball_dir_y = self._get_direction_to_ball()
                                    # If no ball or ghost is at ball (ball_dir is (0,0) if no ball), or ball_dir is random (if ghost on ball),
                                    # fallback to alternating. The random case from _get_direction_to_ball (dist==0) will result in a random tangent choice here.
                                    if ball_dir_x == 0 and ball_dir_y == 0: # If no ball (so dir is 0,0), fallback to alternating tangent
                                        chosen_idx = 1 - self._last_chosen_tangent_idx
                                        chosen_tangent_dx, chosen_tangent_dy = tangents[chosen_idx]
                                        self._last_chosen_tangent_idx = chosen_idx
                                    else:
                                        dot1 = ball_dir_x * tangent1_dx + ball_dir_y * tangent1_dy
                                        dot2 = ball_dir_x * tangent2_dx + ball_dir_y * tangent2_dy
                                        if dot1 >= dot2: # Prefer tangent1 if more aligned or equally aligned
                                            chosen_tangent_dx, chosen_tangent_dy = tangent1_dx, tangent1_dy
                                        else:
                                            chosen_tangent_dx, chosen_tangent_dy = tangent2_dx, tangent2_dy
                                else:
                                    # Fallback for any other unexpected state (e.g. POSSESSING, FADING_OUT, though light avoidance shouldn't trigger there)
                                    chosen_idx = 1 - self._last_chosen_tangent_idx
                                    chosen_tangent_dx, chosen_tangent_dy = tangents[chosen_idx]
                                    self._last_chosen_tangent_idx = chosen_idx

                                # Weighted combination of radial and tangential avoidance
                                combined_vx = (radial_dx * self.avoid_radial_weight) + \
                                              (chosen_tangent_dx * self.avoid_tangential_weight)
                                combined_vy = (radial_dy * self.avoid_radial_weight) + \
                                              (chosen_tangent_dy * self.avoid_tangential_weight)

                                norm_combined = math.hypot(combined_vx, combined_vy)

                                if norm_combined > 0.0001: # Use a small epsilon
                                    final_avoid_dx = combined_vx / norm_combined
                                    final_avoid_dy = combined_vy / norm_combined
                                else:
                                    # Fallback if combined vector is zero
                                    if self.avoid_radial_weight > 0.0001:
                                        final_avoid_dx = radial_dx
                                        final_avoid_dy = radial_dy
                                    elif self.avoid_tangential_weight > 0.0001:
                                        final_avoid_dx = chosen_tangent_dx
                                        final_avoid_dy = chosen_tangent_dy
                                    else: # If both weights are zero, default to moving radially
                                        final_avoid_dx = radial_dx
                                        final_avoid_dy = radial_dy
                                
                                self.velocity_x = final_avoid_dx * self.avoid_light_speed
                                self.velocity_y = final_avoid_dy * self.avoid_light_speed
                                # Do not transition to FADING_OUT here, just avoid.
                                # If multiple lights, it will react to the first one detected in the loop.
                                break # React to one light source at a time
                if is_avoiding_light and GhostObstacle.ghost_possessing_ball == self: # Should not happen if in these states
                    GhostObstacle.ghost_possessing_ball = None


        is_avoiding_pickles = False
        if not is_avoiding_light and pickles_list and (self.state == "APPEARING" or self.state == "FLOATING" or self.state == "RUSHING"):
            for pickles_instance in pickles_list:
                if hasattr(pickles_instance, 'state') and pickles_instance.state == "chasing":
                    avoidance_radius_sq = (150)**2
                    if not (hasattr(pickles_instance, 'rect') and hasattr(self.rect, 'centerx') and hasattr(self.rect, 'centery') and hasattr(pickles_instance.rect, 'centerx') and hasattr(pickles_instance.rect, 'centery')):
                        continue
                    dx_to_pickles = pickles_instance.rect.centerx - self.rect.centerx
                    dy_to_pickles = pickles_instance.rect.centery - self.rect.centery
                    dist_sq = dx_to_pickles**2 + dy_to_pickles**2
                    if dist_sq < avoidance_radius_sq and dist_sq > 0.001:
                        is_avoiding_pickles = True
                        dist = math.sqrt(dist_sq)
                        self.velocity_x = -dx_to_pickles / dist * self.float_speed
                        self.velocity_y = -dy_to_pickles / dist * self.float_speed
                        break

        if self.state == "APPEARING":
            self.alpha = min(255, int((self.state_timer / self.appear_duration) * 150))
            self.current_color = (self.color[0], self.color[1], self.color[2], self.alpha)
            # Ghost does not move in APPEARING state, velocity set here will be used upon transitioning to FLOATING
            if self.state_timer >= self.appear_duration:
                self.visible = True
                self.alpha = 150
                self.current_color = self.color
                self.state = "FLOATING"
                self.state_timer = 0.0
                self.float_duration = random.uniform(5.0, 10.0)
                self.bob_timer = random.uniform(0, 2 * math.pi) # Reset bob timer for fresh float
                if not is_avoiding_light and not is_avoiding_pickles:
                    self._set_random_float_direction()
                # If avoiding, velocity is already set

        elif self.state == "FLOATING":
            self.bob_timer = (self.bob_timer + self.bob_speed * delta_time) % (2 * math.pi)
            # Velocity is set if avoiding light/Pickles, or by _set_random_float_direction if not.
            self.rect.x += self.velocity_x * delta_time
            self.rect.y += self.velocity_y * delta_time

            bounce = False
            if self.rect.left < self.arena_rect.left:
                self.rect.left = self.arena_rect.left
                self.velocity_x *= -1
                bounce = True
            if self.rect.right > self.arena_rect.right:
                self.rect.right = self.arena_rect.right
                self.velocity_x *= -1
                bounce = True
            if self.rect.top < self.arena_rect.top:
                self.rect.top = self.arena_rect.top
                self.velocity_y *= -1
                bounce = True
            if self.rect.bottom > self.arena_rect.bottom:
                self.rect.bottom = self.arena_rect.bottom
                self.velocity_y *= -1
                bounce = True
            
            if bounce and not (is_avoiding_light or is_avoiding_pickles): # If bounced and not avoiding, pick new random direction
                 self._set_random_float_direction()

            self.rect.clamp_ip(self.arena_rect)

            if self.state_timer >= self.float_duration:
                if is_avoiding_light or is_avoiding_pickles:
                    self.state_timer = 0.0 # Continue avoiding in FLOATING state
                    if not is_avoiding_light and is_avoiding_pickles: # if only avoiding pickles, re-evaluate random dir if pickles gone
                         pass # velocity already set for pickles
                    elif not is_avoiding_light and not is_avoiding_pickles : # if no longer avoiding anything
                         self._set_random_float_direction()

                else: # Not avoiding anything, time to rush
                    self.state = "RUSHING"
                    self.state_timer = 0.0

        elif self.state == "RUSHING":
            if not is_avoiding_light and not is_avoiding_pickles:
                if not self.game_ball:
                    self.state = "FLOATING"
                    self.state_timer = 0.0
                    self._set_random_float_direction()
                    return
                dir_x, dir_y = self._get_direction_to_ball()
                self.velocity_x = dir_x * self.rush_speed
                self.velocity_y = dir_y * self.rush_speed
            # If avoiding, velocity is already set.
            
            self.rect.x += self.velocity_x * delta_time
            self.rect.y += self.velocity_y * delta_time
            self.rect.clamp_ip(self.arena_rect)

            if not (is_avoiding_light or is_avoiding_pickles) and self.game_ball and self.rect.colliderect(self.game_ball.rect):
                if GhostObstacle.ghost_possessing_ball is None or GhostObstacle.ghost_possessing_ball == self:
                    self.state = "POSSESSING"
                    self.state_timer = 0.0
                    GhostObstacle.ghost_possessing_ball = self
                    self.current_color = self.possessed_color
                    self.alpha = self.possessed_color[3]
                    self.possessed_ball_original_dx = self.game_ball.ball.dx
                    self.possessed_ball_original_dy = self.game_ball.ball.dy
                    self.possessed_ball_original_speed = self.game_ball.ball.speed
                    possess_angle = random.uniform(0, 2 * math.pi)
                    self.game_ball.ball.dx = math.cos(possess_angle)
                    self.game_ball.ball.dy = math.sin(possess_angle)
                    self.game_ball.ball.velocity_x = self.game_ball.ball.dx * self.game_ball.ball.speed
                    self.game_ball.ball.velocity_y = self.game_ball.ball.dy * self.game_ball.ball.speed
                else:
                    self.state = "FLOATING"
                    self.state_timer = 0.0
                    self._set_random_float_direction()
            elif self.state_timer > 5.0 and not (is_avoiding_light or is_avoiding_pickles) : # Timeout for rushing if not possessing
                self.state = "FLOATING"
                self.state_timer = 0.0
                self._set_random_float_direction()


        elif self.state == "POSSESSING":
            if not self.game_ball:
                self._unpossess_ball()
                return

            self.rect.center = self.game_ball.rect.center

            if candles and self.game_ball and scale_rect_func:
                ball_screen_rect = scale_rect_func(self.game_ball.rect)
                for candle_obj_wrapper in candles:
                    if hasattr(candle_obj_wrapper, 'get_light_properties'):
                        light_props = candle_obj_wrapper.get_light_properties(scale_factor)
                        light_x = light_props['x']
                        light_y = light_props['y']
                        light_radius = light_props['radius']
                        light_intensity = light_props['intensity']

                        if light_intensity > 0.1 and light_radius > 0:
                            dx = ball_screen_rect.centerx - light_x
                            dy = ball_screen_rect.centery - light_y
                            distance_sq = dx*dx + dy*dy
                            sum_radii_sq = (ball_screen_rect.width / 2 + light_radius)**2
                            
                            if distance_sq < sum_radii_sq:
                                self._unpossess_ball()
                                return

            if self.state_timer >= self.possess_duration and self.state == "POSSESSING":
                self._unpossess_ball()
        
        elif self.state == "FADING_OUT":
            # Use _initial_fade_alpha if it was set (e.g. by critical light exposure), otherwise use possessed_color alpha
            start_alpha = self._initial_fade_alpha if self._initial_fade_alpha > 0 else self.possessed_color[3]
            self.alpha = max(0, int(start_alpha * (1 - (self.state_timer / self.fade_out_duration))))
            
            # Determine base color for fading (usually the non-possessed color unless it was possessing then hit by light)
            base_fade_color = self.color
            # If it was possessing and forced to fade by light, it might briefly show possessed color fading
            # However, _unpossess_ball already transitions to FADING_OUT and resets color logic.
            # So, self.color should be the primary base for fading unless specifically handled in _unpossess_ball.

            self.current_color = (base_fade_color[0], base_fade_color[1], base_fade_color[2], self.alpha)

            if self.state_timer >= self.fade_out_duration:
                self._initial_fade_alpha = 0 # Reset for next potential fade
                self.visible = False
                self.state = "INACTIVE"
                GhostObstacle.active_ghost_count -=1
                if GhostObstacle.ghost_possessing_ball == self:
                    GhostObstacle.ghost_possessing_ball = None
                self.is_active_instance = False

    def _unpossess_ball(self, force_fade_from_current_alpha=False):
        if self.game_ball and GhostObstacle.ghost_possessing_ball == self:
            # Ball continues with its current (randomized by possession) trajectory
            pass

        GhostObstacle.ghost_possessing_ball = None
        
        if self.state != "FADING_OUT": # Avoid resetting timer if already fading
            self.state = "FADING_OUT"
            self.state_timer = 0.0
        
        if force_fade_from_current_alpha:
            self._initial_fade_alpha = self.alpha # Start fading from current alpha
        else:
            # Default behavior: if unpossessing normally (e.g. timer up), fade from possessed color's alpha
            self._initial_fade_alpha = self.possessed_color[3]
        
        self.current_color = self.color # Revert to normal base color for fading visual

    def force_fade_out_in_light(self):
        """
        Forces the ghost to start fading out, typically when an external
        controller (like Pickles) determines it has been exposed to light.
        """
        if self.state == "FADING_OUT" or self.state == "INACTIVE":
            return # Already fading or inactive

        self.state = "FADING_OUT"
        self.state_timer = 0.0
        self._initial_fade_alpha = self.alpha # Start fading from current alpha
        self.current_color = self.color # Ensure it fades using the normal ghost color

        if GhostObstacle.ghost_possessing_ball == self:
            GhostObstacle.ghost_possessing_ball = None
            # If it was possessing a ball, the ball should resume its normal behavior.
            # This might require restoring its original dx, dy, speed if that's not handled elsewhere.
            # For now, just releasing possession.

        self.is_controlled_externally = False # Allow its own update logic to handle fading animation
    def draw(self, screen, colors, scale_rect):
        if not self.is_active_instance or not self.visible or self.state == "INACTIVE":
            return

        scaled_rect = scale_rect(self.rect)

        # Calculate bounding box for all components to size temp_surface correctly
        all_component_rects_relative = []
        if not self.body_components: # Should always have components from __init__
             # Fallback if something went wrong with body_components initialization
            temp_surface = pygame.Surface(scaled_rect.size, pygame.SRCALPHA)
            temp_surface.fill((0,0,0,0))
            pygame.draw.ellipse(temp_surface, self.current_color, pygame.Rect(0,0,scaled_rect.width, scaled_rect.height*0.8))
            screen.blit(temp_surface, scaled_rect.topleft)
            return

        for comp in self.body_components:
            comp_w = scaled_rect.width * comp['size_x_factor']
            comp_h = scaled_rect.height * comp['size_y_factor']

            center_offset_x = scaled_rect.width * comp['offset_x_factor']
            center_offset_y = scaled_rect.height * comp['offset_y_factor']
            
            comp_abs_center_x = scaled_rect.width / 2 + center_offset_x
            comp_abs_center_y = scaled_rect.height / 2 + center_offset_y
            
            current_comp_rect = pygame.Rect(
                comp_abs_center_x - comp_w / 2,
                comp_abs_center_y - comp_h / 2,
                comp_w,
                comp_h
            )
            all_component_rects_relative.append(current_comp_rect)

        overall_bounds_rel = all_component_rects_relative[0].copy()
        for r_idx in range(1, len(all_component_rects_relative)):
            overall_bounds_rel.union_ip(all_component_rects_relative[r_idx])
        
        min_x_rel = overall_bounds_rel.left
        min_y_rel = overall_bounds_rel.top
        temp_surface_width = overall_bounds_rel.width
        temp_surface_height = overall_bounds_rel.height

        temp_surface_width = max(1, int(temp_surface_width))
        temp_surface_height = max(1, int(temp_surface_height))

        temp_surface = pygame.Surface((temp_surface_width, temp_surface_height), pygame.SRCALPHA)
        temp_surface.fill((0,0,0,0))

        for comp_rect_rel in all_component_rects_relative:
            rect_on_temp = comp_rect_rel.move(-min_x_rel, -min_y_rel)
            if rect_on_temp.width > 0 and rect_on_temp.height > 0:
                 pygame.draw.ellipse(temp_surface, self.current_color, rect_on_temp)
        
        # --- Draw Face Features ---
        # Face features are drawn relative to the main component (index 0)
        main_comp_rect_rel = all_component_rects_relative[0]
        main_comp_rect_on_temp = main_comp_rect_rel.move(-min_x_rel, -min_y_rel)

        face_color = (0, 0, 0, self.alpha) # Black for features, alpha matches ghost
        pupil_color = (20, 20, 20, self.alpha) # Dark grey for pupils
        
        face_ref_center_x = main_comp_rect_on_temp.centerx
        face_ref_center_y = main_comp_rect_on_temp.centery
        face_ref_width = main_comp_rect_on_temp.width
        face_ref_height = main_comp_rect_on_temp.height

        base_eye_radius = max(2, int(face_ref_width * 0.12)) # Slightly larger eyes relative to main blob
        default_eye_y_pos = int(face_ref_center_y - face_ref_height * 0.1) # Eyes slightly above center of main blob
        default_eye_x_offset = int(face_ref_width * 0.22) # Eyes closer to edge of main blob

        # Left Eye
        left_eye_radius_x_base = int(base_eye_radius * self.face_features['left_eye_scale_x'])
        left_eye_radius_y_base = int(base_eye_radius * self.face_features['left_eye_scale_y'])
        left_eye_center_x_on_temp = face_ref_center_x - default_eye_x_offset + int(default_eye_x_offset * self.face_features['left_eye_offset_x_factor'])
        left_eye_center_y_on_temp = default_eye_y_pos + int(base_eye_radius * self.face_features['left_eye_offset_y'])

        # Right Eye
        right_eye_radius_x_base = int(base_eye_radius * self.face_features['right_eye_scale_x'])
        right_eye_radius_y_base = int(base_eye_radius * self.face_features['right_eye_scale_y'])
        right_eye_center_x_on_temp = face_ref_center_x + default_eye_x_offset + int(default_eye_x_offset * self.face_features['right_eye_offset_x_factor'])
        right_eye_center_y_on_temp = default_eye_y_pos + int(base_eye_radius * self.face_features['right_eye_offset_y'])

        eye_angle_rad = math.radians(self.face_features['eye_angle_deg'])

        # Helper to draw eye (ellipse and pupil)
        def draw_eye_and_pupil(eye_center_x, eye_center_y, radius_x, radius_y, angle_rad, is_left_eye):
            if radius_x <= 0 or radius_y <= 0:
                return

            # For slanted eyes, we might draw a polygon or use rotated blit. Simple ellipse for now.
            # For simplicity, angle is not directly applied to pygame.draw.ellipse.
            # Instead, specific eye types like 'angry_slant' will adjust points if using polygons.
            # Here, we'll use the angle for eyebrow placement primarily.
            
            # Draw Eye Outline/Shape
            eye_rect_temp = pygame.Rect(eye_center_x - radius_x, eye_center_y - radius_y, radius_x * 2, radius_y * 2)
            
            if self.face_features['eye_type'] == 'angry_slant':
                 # Draw as a slightly squashed, upward-pointing trapezoid/polygon for slant
                top_y = eye_center_y - radius_y
                bottom_y = eye_center_y + radius_y * 0.7 # Squashed bottom
                outer_x_offset = radius_x * 0.3 if is_left_eye else -radius_x * 0.3
                inner_x_offset = -radius_x * 0.2 if is_left_eye else radius_x * 0.2
                
                points = [
                    (eye_center_x - radius_x + outer_x_offset, bottom_y),
                    (eye_center_x - radius_x * 0.8 + inner_x_offset, top_y),
                    (eye_center_x + radius_x * 0.8 + inner_x_offset, top_y),
                    (eye_center_x + radius_x + outer_x_offset, bottom_y)
                ]
                pygame.draw.polygon(temp_surface, face_color, points)
            elif self.face_features['eye_type'] == 'sad_droop':
                # Draw as a downward-curving arc or a modified ellipse
                # Simple ellipse for now, droop effect from eyebrows mainly
                pygame.draw.ellipse(temp_surface, face_color, eye_rect_temp)
            else: # Normal, wide, squint, uneven, offset_x, surprised_round
                pygame.draw.ellipse(temp_surface, face_color, eye_rect_temp)


            # Draw Pupil
            pupil_type = self.face_features['pupil_type']
            if pupil_type != 'none':
                pupil_scale = self.face_features['pupil_scale_factor']
                pupil_radius_x = max(1, int(radius_x * pupil_scale))
                pupil_radius_y = max(1, int(radius_y * pupil_scale))

                if pupil_type == 'dot':
                    pygame.draw.ellipse(temp_surface, pupil_color,
                                        (eye_center_x - pupil_radius_x,
                                         eye_center_y - pupil_radius_y,
                                         pupil_radius_x * 2, pupil_radius_y * 2))
                elif pupil_type == 'slit_vertical':
                    pupil_width = max(1, int(radius_x * pupil_scale * 0.5)) # Thinner slit
                    pupil_height = max(1, int(radius_y * pupil_scale * 1.2)) # Taller slit
                    pygame.draw.rect(temp_surface, pupil_color,
                                     (eye_center_x - pupil_width // 2,
                                      eye_center_y - pupil_height // 2,
                                      pupil_width, pupil_height))
        
        draw_eye_and_pupil(left_eye_center_x_on_temp, left_eye_center_y_on_temp, left_eye_radius_x_base, left_eye_radius_y_base, -eye_angle_rad, True)
        draw_eye_and_pupil(right_eye_center_x_on_temp, right_eye_center_y_on_temp, right_eye_radius_x_base, right_eye_radius_y_base, eye_angle_rad, False)

        # Draw Eyebrows
        eyebrow_type = self.face_features['eyebrow_type']
        if eyebrow_type != 'none':
            eyebrow_len_factor = self.face_features['eyebrow_length_factor']
            eyebrow_thick_factor = self.face_features['eyebrow_thickness_factor']
            eyebrow_y_offset = self.face_features['eyebrow_y_offset_factor']

            def draw_eyebrow(eye_center_x, eye_radius_x, eye_radius_y, eye_top_y, is_left):
                length = int(eye_radius_x * 2 * eyebrow_len_factor) # Based on full eye width
                thickness = max(1, int(eye_radius_y * eyebrow_thick_factor))
                
                # Base Y position: above the eye's visual top
                base_y = eye_top_y - (eye_radius_y * eyebrow_y_offset) - thickness / 2
                
                start_x, end_x = 0, 0
                start_y, end_y = base_y, base_y
                angle_offset = 0

                if eyebrow_type == 'flat':
                    start_x = eye_center_x - length // 2
                    end_x = eye_center_x + length // 2
                elif eyebrow_type == 'angled_in': # Slanting down towards nose
                    angle_offset = 15 if is_left else -15
                elif eyebrow_type == 'angled_out': # Slanting up towards sides
                    angle_offset = -15 if is_left else 15
                elif eyebrow_type == 'raised_center': # Like a small arch
                     # Draw as two short lines meeting at a raised center point
                    mid_x = eye_center_x
                    mid_y_raised = base_y - thickness * 1.5
                    p1 = (eye_center_x - length // 2, base_y)
                    p2 = (mid_x, mid_y_raised)
                    p3 = (eye_center_x + length // 2, base_y)
                    pygame.draw.line(temp_surface, face_color, p1, p2, thickness)
                    pygame.draw.line(temp_surface, face_color, p2, p3, thickness)
                    return # Handled custom drawing

                if eyebrow_type != 'flat': # Apply angle for angled_in/out
                    rad = math.radians(angle_offset)
                    half_len_x = (length / 2) * math.cos(rad)
                    half_len_y = (length / 2) * math.sin(rad)
                    start_x = eye_center_x - half_len_x
                    start_y = base_y - half_len_y
                    end_x = eye_center_x + half_len_x
                    end_y = base_y + half_len_y
                
                pygame.draw.line(temp_surface, face_color, (start_x, start_y), (end_x, end_y), thickness)

            # Calculate eye top for eyebrow reference (approximate)
            left_eye_visual_top_y = left_eye_center_y_on_temp - left_eye_radius_y_base
            right_eye_visual_top_y = right_eye_center_y_on_temp - right_eye_radius_y_base
            
            draw_eyebrow(left_eye_center_x_on_temp, left_eye_radius_x_base, left_eye_radius_y_base, left_eye_visual_top_y, True)
            draw_eyebrow(right_eye_center_x_on_temp, right_eye_radius_x_base, right_eye_radius_y_base, right_eye_visual_top_y, False)


        # Mouth
        mouth_type = self.face_features['mouth_type']
        if mouth_type != 'no_mouth':
            mouth_width = int(face_ref_width * self.face_features['mouth_width_factor'])
            mouth_height = int(face_ref_height * self.face_features['mouth_height_factor'])
            mouth_center_x_on_temp = face_ref_center_x + int(face_ref_width * self.face_features['mouth_offset_x_factor'])
            mouth_y_base_on_temp = int(face_ref_center_y + face_ref_height * 0.2) # Below eyes
            mouth_center_y_on_temp = mouth_y_base_on_temp + int(face_ref_height * self.face_features['mouth_offset_y_factor'])
            
            line_thickness = max(1, int(face_ref_width * 0.025))

            if mouth_type == 'smile':
                rect = pygame.Rect(mouth_center_x_on_temp - mouth_width // 2, mouth_center_y_on_temp - mouth_height // 2, mouth_width, mouth_height)
                if rect.width > 0 and rect.height > 0: pygame.draw.arc(temp_surface, face_color, rect, math.pi, 2 * math.pi, line_thickness)
            elif mouth_type == 'frown':
                rect = pygame.Rect(mouth_center_x_on_temp - mouth_width // 2, mouth_center_y_on_temp, mouth_width, mouth_height)
                if rect.width > 0 and rect.height > 0: pygame.draw.arc(temp_surface, face_color, rect, 0, math.pi, line_thickness)
            elif mouth_type == 'neutral_line':
                start_pos = (mouth_center_x_on_temp - mouth_width // 2, mouth_center_y_on_temp)
                end_pos = (mouth_center_x_on_temp + mouth_width // 2, mouth_center_y_on_temp)
                pygame.draw.line(temp_surface, face_color, start_pos, end_pos, line_thickness)
            elif mouth_type == 'o_shape': # Original O shape
                rect = pygame.Rect(mouth_center_x_on_temp - mouth_width // 2, mouth_center_y_on_temp - mouth_height // 2, mouth_width, mouth_height)
                if rect.width > 0 and rect.height > 0: pygame.draw.ellipse(temp_surface, face_color, rect, line_thickness)
            elif mouth_type == 'wavy_line':
                points = []
                num_segments_mouth = 3
                segment_width = mouth_width / num_segments_mouth if num_segments_mouth > 0 else mouth_width
                for i_seg in range(num_segments_mouth + 1):
                    px = mouth_center_x_on_temp - mouth_width // 2 + i_seg * segment_width
                    py_offset = math.sin(i_seg * math.pi * 2) * (mouth_height / 2) # More waves
                    py = mouth_center_y_on_temp + py_offset
                    points.append((px, py))
                if len(points) > 1: pygame.draw.lines(temp_surface, face_color, False, points, line_thickness)
            elif mouth_type == 'smirk':
                half_mouth_width = mouth_width // 2
                rect_left = pygame.Rect(mouth_center_x_on_temp - half_mouth_width, mouth_center_y_on_temp - mouth_height // 2, half_mouth_width, mouth_height)
                if rect_left.width > 0 and rect_left.height > 0: pygame.draw.arc(temp_surface, face_color, rect_left, math.pi * 1.1, math.pi * 1.9, line_thickness)
                pygame.draw.line(temp_surface, face_color,
                                 (mouth_center_x_on_temp, mouth_center_y_on_temp + mouth_height * 0.1),
                                 (mouth_center_x_on_temp + half_mouth_width, mouth_center_y_on_temp + mouth_height*0.2), line_thickness)
            elif mouth_type == 'jagged_line':
                points = []
                num_teeth = 5
                tooth_width = mouth_width / num_teeth if num_teeth > 0 else mouth_width
                for i_tooth in range(num_teeth + 1):
                    px = mouth_center_x_on_temp - mouth_width // 2 + i_tooth * tooth_width
                    py_offset = (mouth_height / 2) if i_tooth % 2 == 0 else -(mouth_height / 2)
                    py = mouth_center_y_on_temp + py_offset
                    points.append((px, py))
                if len(points) > 1: pygame.draw.lines(temp_surface, face_color, False, points, line_thickness)
            elif mouth_type == 'open_circle_surprise':
                # mouth_height_factor is already set to be same as width_factor for circle
                rect = pygame.Rect(mouth_center_x_on_temp - mouth_width // 2,
                                   mouth_center_y_on_temp - mouth_height // 2,
                                   mouth_width, mouth_height)
                if rect.width > 0 and rect.height > 0: pygame.draw.ellipse(temp_surface, face_color, rect) # Filled ellipse


        # Blit the temp_surface containing the composite ghost body and face
        bob_offset = 0
        if self.state == "FLOATING": # Only bob when floating
            bob_offset = math.sin(self.bob_timer) * (scaled_rect.height * self.bob_amplitude_factor)
        
        blit_x = scaled_rect.left + min_x_rel
        blit_y = scaled_rect.top + min_y_rel + bob_offset
        screen.blit(temp_surface, (blit_x, blit_y))

    def handle_collision(self, ball_instance):
        # Collision is primarily handled in the RUSHING state's update method.
        # This method could be used for other types of interactions if needed.
        if not self.is_active_instance or self.state == "INACTIVE":
            return False
            
        if self.state == "RUSHING" and self.rect.colliderect(ball_instance.rect):
            # The logic for possession is in update() to ensure it happens during the ghost's turn.
            # Returning True here would indicate a generic collision, but possession is specific.
            return True # Indicates a collision occurred, main game might react (e.g. sound)
        return False

    @classmethod
    def reset_class_vars(cls):
        cls.active_ghost_count = 0
        cls.ghost_possessing_ball = None

    def is_done(self):
        """Checks if the ghost is inactive and can be removed."""
        return self.state == "INACTIVE"
