import pygame
import random
import math
from Modules.Submodules.Ping_Ball import Ball
from Modules.Submodules.Ping_Particles import WaterSpout

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
            scaled_radius = int(radius * (scaled_rect.width / (self.base_radius * 2)))
            x = scaled_center[0] + math.cos(angle) * scaled_radius
            y = scaled_center[1] + math.sin(angle) * scaled_radius
            star_points.append((x, y))
            
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
        for x in range(scaled_rect.left, scaled_rect.right, brick_size * 2):
            pygame.draw.rect(screen, brick_dark, (x, scaled_rect.top, brick_size, brick_size))
            pygame.draw.rect(screen, brick_light, (x + brick_size, scaled_rect.top, brick_size, brick_size))
            pygame.draw.line(screen, mortar, (x, scaled_rect.top), (x, scaled_rect.top + brick_size)) # Vertical mortar
            pygame.draw.line(screen, mortar, (x + brick_size, scaled_rect.top), (x + brick_size, scaled_rect.top + brick_size))
            pygame.draw.line(screen, mortar, (x, scaled_rect.top + brick_size), (x + brick_size * 2, scaled_rect.top + brick_size)) # Horizontal mortar below

        # Bottom border bricks
        for x in range(scaled_rect.left, scaled_rect.right, brick_size * 2):
            pygame.draw.rect(screen, brick_light, (x, scaled_rect.bottom - brick_size, brick_size, brick_size))
            pygame.draw.rect(screen, brick_dark, (x + brick_size, scaled_rect.bottom - brick_size, brick_size, brick_size))
            pygame.draw.line(screen, mortar, (x, scaled_rect.bottom - brick_size), (x, scaled_rect.bottom)) # Vertical mortar
            pygame.draw.line(screen, mortar, (x + brick_size, scaled_rect.bottom - brick_size), (x + brick_size, scaled_rect.bottom))
            pygame.draw.line(screen, mortar, (x, scaled_rect.bottom - brick_size), (x + brick_size * 2, scaled_rect.bottom - brick_size)) # Horizontal mortar above

        # Left border bricks
        for y in range(scaled_rect.top + brick_size, scaled_rect.bottom - brick_size, brick_size * 2): # Avoid corners
            pygame.draw.rect(screen, brick_light, (scaled_rect.left, y, brick_size, brick_size))
            pygame.draw.rect(screen, brick_dark, (scaled_rect.left, y + brick_size, brick_size, brick_size))
            pygame.draw.line(screen, mortar, (scaled_rect.left, y), (scaled_rect.left + brick_size, y)) # Horizontal mortar
            pygame.draw.line(screen, mortar, (scaled_rect.left, y + brick_size), (scaled_rect.left + brick_size, y + brick_size))
            pygame.draw.line(screen, mortar, (scaled_rect.left + brick_size, y), (scaled_rect.left + brick_size, y + brick_size * 2)) # Vertical mortar right

        # Right border bricks
        for y in range(scaled_rect.top + brick_size, scaled_rect.bottom - brick_size, brick_size * 2): # Avoid corners
            pygame.draw.rect(screen, brick_dark, (scaled_rect.right - brick_size, y, brick_size, brick_size))
            pygame.draw.rect(screen, brick_light, (scaled_rect.right - brick_size, y + brick_size, brick_size, brick_size))
            pygame.draw.line(screen, mortar, (scaled_rect.right - brick_size, y), (scaled_rect.right, y)) # Horizontal mortar
            pygame.draw.line(screen, mortar, (scaled_rect.right - brick_size, y + brick_size), (scaled_rect.right, y + brick_size))
            pygame.draw.line(screen, mortar, (scaled_rect.right - brick_size, y), (scaled_rect.right - brick_size, y + brick_size * 2)) # Vertical mortar left


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
        self.horizontal_rect = pygame.Rect(x, y, width, height)

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
        shadow_center = (center_x, center_y + shadow_offset)
        pygame.draw.circle(screen, (20, 20, 20), shadow_center, radius)

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
                angle = (i / num_notches) * 2 * math.pi
                # Calculate center position of the notch
                notch_center_x = center_x + math.cos(angle) * notch_distance
                notch_center_y = center_y + math.sin(angle) * notch_distance

                # Calculate top-left corner for the rect
                notch_x = notch_center_x - notch_size // 2
                notch_y = notch_center_y - notch_size // 2

                pygame.draw.rect(screen, detail_color,
                                 (int(notch_x), int(notch_y), notch_size, notch_size))

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
            # Create new raw ball with same properties
            new_ball = Ball(ball.ball.size)
            new_ball.rect.x = self.rect.x # Start at power-up location
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
import pygame
import math
import random
from Modules.Submodules.Ping_Ball import Ball # Assuming Ball class is needed
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

    def handle_collision(self, ball):
        """Detect collision, capture ball, and initiate spinning."""
        if self.is_spinning or not hasattr(ball, 'rect') or not hasattr(ball, 'ball'): # Don't capture if already spinning or invalid ball
            return False

        # Circular collision detection
        ball_center = ball.rect.center
        dx = ball_center[0] - self.x
        dy = ball_center[1] - self.y
        distance_sq = dx*dx + dy*dy
        # Ensure ball has width attribute for radius calculation
        ball_radius = ball.rect.width / 2 if hasattr(ball.rect, 'width') else 0
        radii_sum_sq = (self.radius + ball_radius) ** 2

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
            impact_angle = math.degrees(math.atan2(-dy, dx)) % 360 # Pygame y-axis is inverted

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
        ball_radius = self.captured_ball.rect.width / 2 if hasattr(self.captured_ball.rect, 'width') else 0
        offset = self.radius + ball_radius + 1
        self.captured_ball.rect.centerx = self.x + offset * release_dx
        self.captured_ball.rect.centery = self.y + offset * release_dy

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
        scaled_radius = scaled_display_rect.width // 2

        if scaled_radius <= 1: return # Avoid drawing if too small

        # Define radii for different parts relative to the main scaled radius
        outer_ring_radius = scaled_radius
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
        shadow_center = (scaled_center[0] + self.shadow_offset, scaled_center[1] + self.shadow_offset)
        shadow_surface = pygame.Surface((scaled_radius*2 + self.shadow_offset*2, scaled_radius*2 + self.shadow_offset*2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, shadow_color, (scaled_radius + self.shadow_offset, scaled_radius + self.shadow_offset), scaled_radius)
        screen.blit(shadow_surface, (scaled_center[0] - scaled_radius, scaled_center[1] - scaled_radius))


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
                    angle = start_angle_rad + (end_angle_rad - start_angle_rad) * j / num_arc_points
                    x = scaled_center[0] + outer_ring_radius * math.cos(angle)
                    y = scaled_center[1] + outer_ring_radius * math.sin(angle)
                    point_list.append((int(x), int(y)))
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
                pygame.draw.line(screen, color_black, start_point, end_point, max(1, scaled_radius // 50)) # Thin lines

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
        pygame.draw.circle(screen, color_white, scaled_center, outer_ring_radius, max(1, scaled_radius // 40))

        # 6. Draw Timer if spinning and font is available (Draw last to be on top)
        if self.is_spinning and self.timer_font:
            display_time = max(0, self.hold_timer)
            timer_text = f"{display_time:.1f}"
            try:
                text_surface = self.timer_font.render(timer_text, True, color_white)
                # Add black outline/shadow for better visibility
                outline_offset = max(1, self.timer_font_size // 15)
                text_surface_shadow = self.timer_font.render(timer_text, True, color_black)
                shadow_pos = (scaled_center[0] - text_surface.get_width() // 2 + outline_offset,
                              scaled_center[1] - text_surface.get_height() // 2 + outline_offset)
                screen.blit(text_surface_shadow, shadow_pos)

                # Blit main text
                text_rect = text_surface.get_rect(center=scaled_center)
                screen.blit(text_surface, text_rect)
            except Exception as e:
                 print(f"Error rendering timer text: {e}")


        # Note: The captured ball itself is positioned in update().
        # The main game loop should ideally skip drawing the ball if it's captured by the spinner.