import pygame
import math
import random
from Ping.Modules.Objects.Ping_Ball import Ball
from Ping.Modules.Objects.Ping_Paddle import Paddle
from Ping.Modules.Objects.Ping_Obstacles import Obstacle, Goal, Portal, PowerUpBall, Manhole, Bumper, GhostObstacle # Added Bumper and GhostObstacle

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
        self.paddle.move(delta_time, self.arena_height) # Removed scoreboard_height

    def draw(self, screen, color):
        """Draw the paddle using its sprite."""
        self.paddle.draw(screen, self.scale_rect)

    def reset_position(self):
        """Reset paddle to starting position."""
        self.paddle.reset_position(self.arena_width, self.arena_height)

class BallObject(ArenaObject):
    # Add optional initial_state parameter
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, size=20, initial_state=None):
        """Initialize a ball object with arena properties and optional initial state."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.ball = Ball(size)
        if initial_state:
            # Apply initial state if provided
            self.ball.rect.x = initial_state['x']
            self.ball.rect.y = initial_state['y']
            self.ball.dx = initial_state['dx']
            self.ball.dy = initial_state['dy']
            self.ball.speed = initial_state['speed']
            self.ball.velocity_x = initial_state['velocity_x']
            self.ball.velocity_y = initial_state['velocity_y']
        else:
            # Reset position only if no initial state is given
            self.reset_position()

    @property
    def rect(self):
        return self.ball.rect

    def draw(self, screen, color):
        """Override draw method to use ball's circular drawing with drop shadow."""
        scaled_rect = self.scale_rect(self.rect)
        
        # Draw drop shadow
        shadow_offset = 4
        shadow_center = (scaled_rect.center[0] + shadow_offset,
                        scaled_rect.center[1] + shadow_offset)
        pygame.draw.circle(screen, (20, 20, 20), shadow_center, scaled_rect.width // 2)
        
        # Draw ball with border
        pygame.draw.circle(screen, (30, 30, 30), scaled_rect.center, scaled_rect.width // 2)  # Border
        pygame.draw.circle(screen, color, scaled_rect.center, (scaled_rect.width - 4) // 2)  # Main ball

    def move(self, delta_time):
        """Move the ball based on its velocity and time delta."""
        self.ball.move(delta_time)

    def reset_position(self):
        """Reset ball to center position."""
        self.ball.reset_position(self.arena_width, self.arena_height) # Removed scoreboard_height

    def handle_paddle_collision(self, paddle):
        """Handle collision with a paddle."""
        return self.ball.handle_paddle_collision(paddle)
    
    def handle_wall_collision(self, bounce_walls=False):
        """Handle wall collisions."""
        # First handle vertical walls (top/bottom) - always bounce
        collided = self.ball.handle_wall_collision(self.arena_height) # Removed scoreboard_height

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
    
    def draw(self, screen, color):
        """Draw the goal as a rusty grate with a subtle glow."""
        scaled_rect = self.scale_rect(self.rect)

        # Define colors
        base_color = (70, 50, 30) # Dark rusty brown
        bar_color = (180, 120, 80) # Lighter rusty color for bars
        highlight_color = (255, 180, 100) # Bright highlight for visibility
        glow_color = (100, 150, 100, 80) # Faint green glow (subtle)

        # Draw the base rectangle (dark background)
        pygame.draw.rect(screen, base_color, scaled_rect)

        # Draw vertical bars for the grate effect
        bar_width = 4 # Scaled width
        bar_spacing = 10 # Scaled spacing
        num_bars = scaled_rect.width // (bar_width + bar_spacing)

        for i in range(num_bars):
            bar_x = scaled_rect.left + bar_spacing + i * (bar_width + bar_spacing)
            bar_rect = pygame.Rect(bar_x, scaled_rect.top, bar_width, scaled_rect.height)
            pygame.draw.rect(screen, bar_color, bar_rect)
            # Add a highlight to the top edge of bars for visibility
            pygame.draw.line(screen, highlight_color, (bar_rect.left, bar_rect.top), (bar_rect.right, bar_rect.top), 1)

        # Add a subtle glow effect behind the bars
        glow_surface = pygame.Surface(scaled_rect.size, pygame.SRCALPHA)
        glow_rect_inner = scaled_rect.inflate(-10, -10) # Smaller inner glow
        # Draw the glow centered within the goal area
        pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect().inflate(-5, -5), border_radius=5)
        screen.blit(glow_surface, scaled_rect.topleft)

        # Draw a border to make it stand out
        pygame.draw.rect(screen, highlight_color, scaled_rect, 2, border_radius=3)

class PortalObject(ArenaObject):
    """Portal object that allows ball teleportation between paired portals."""
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x, y, width, height):
        """Initialize a portal object with arena properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.portal = Portal(x, y, width, height)
        self.target = None
    
    def set_target(self, target_portal):
        """Set the target portal for teleportation."""
        self.portal.set_target(target_portal.portal)
    
    @property
    def rect(self):
        return self.portal.rect
    
    def handle_collision(self, ball):
        """Handle collision between portal and ball."""
        return self.portal.handle_collision(ball)
        
    def update_cooldown(self):
        """Update portal cooldown timer."""
        self.portal.update_cooldown()
    
    # Updated draw method to accept colors dictionary and scale_rect function
    # and delegate drawing to the underlying Portal instance.
    def draw(self, screen, colors, scale_rect):
        """Delegate drawing to the underlying Portal object."""
        # Call the draw method of the actual Portal instance from Ping_Obstacles.py
        self.portal.draw(screen, colors, scale_rect)

class ObstacleObject(ArenaObject):
    # Added x, y, and properties parameters
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x=None, y=None, width=20, height=60, properties=None):
        """Initialize an obstacle with arena properties, position, and optional properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.properties = properties if properties is not None else {} # Store properties

        # Use provided x, y if available, otherwise calculate random position
        if x is None or y is None:
            # Calculate middle third boundaries
            third_width = self.arena_width // 3
            min_x = third_width
            max_x = third_width * 2
            # Random position within middle third
            x = random.randint(min_x, max_x - width)
            y = random.randint(self.scoreboard_height, self.arena_height - height)

        # Create core obstacle, passing position and size
        # Note: Base Obstacle class doesn't currently use properties, but we store them.
        self.obstacle = Obstacle(x, y, width, height)

    @property
    def rect(self):
        return self.obstacle.rect

    def handle_collision(self, ball, sound_manager=None):
        """
        Handle collision between obstacle and ball.
        Args:
            ball: The ball object that collided
            sound_manager: Optional SoundManager instance to play collision sounds
        """
        return self.obstacle.handle_collision(ball, sound_manager)
        
    def draw(self, screen, colors, scale_rect):
        """Draw the obstacle as a pixelated brick wall with drop shadow."""
        scaled_rect = scale_rect(self.rect)

        # Draw drop shadow first
        shadow_offset = 4
        shadow_rect = pygame.Rect(
            scaled_rect.left + shadow_offset,
            scaled_rect.top + shadow_offset,
            scaled_rect.width,
            scaled_rect.height
        )
        pygame.draw.rect(screen, (20, 20, 20), shadow_rect)  # Dark shadow

        # Get base color from colors dict, default to white if not found
        base_color = colors.get('WHITE', (255, 255, 255))
        r, g, b = base_color
        # Mix with brown (139, 69, 19) for brick color
        brick_color = (min(255, (r + 139) // 2), min(255, (g + 69) // 2), min(255, (b + 19) // 2))
        # Darker brown shading
        dark_brick = (max(0, brick_color[0] - 40), max(0, brick_color[1] - 40), max(0, brick_color[2] - 40))
        # Even darker for mortar
        mortar_color = (max(0, brick_color[0] - 60), max(0, brick_color[1] - 60), max(0, brick_color[2] - 60))
        
        # Draw base rectangle (mortar color)
        pygame.draw.rect(screen, mortar_color, scaled_rect)
        
        # Draw brick pattern
        brick_height = 10  # Height of each brick
        brick_rows = scaled_rect.height // brick_height
        
        for row in range(brick_rows):
            # Alternate brick pattern offset for each row
            offset = (10 if row % 2 else 0)
            y = scaled_rect.top + (row * brick_height)
            
            # Draw bricks in this row
            brick_width = 16  # Width of each brick
            x = scaled_rect.left + offset
            while x < scaled_rect.right - 2:
                # Calculate brick width to fit within obstacle
                current_width = min(brick_width, scaled_rect.right - x - 2)
                
                # Brick rectangle with 1px gap for mortar
                brick_rect = pygame.Rect(x, y, current_width - 1, brick_height - 1)
                pygame.draw.rect(screen, brick_color, brick_rect)
                
                # Add shading on right and bottom for 3D effect
                shade_right = pygame.Rect(brick_rect.right - 2, brick_rect.top,
                                        2, brick_rect.height)
                shade_bottom = pygame.Rect(brick_rect.left, brick_rect.bottom - 2,
                                         brick_rect.width, 2)
                pygame.draw.rect(screen, dark_brick, shade_right)
                pygame.draw.rect(screen, dark_brick, shade_bottom)
                
                x += brick_width  # Move to next brick position

class ManHoleObject(ArenaObject):
    """Manhole obstacle that can spout upward and affect ball trajectory."""
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x, y, width, height, is_bottom=True, properties=None):
        """Initialize a manhole object with arena properties, passing properties down."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        # Pass the properties dictionary to the underlying Manhole constructor
        self.manhole = Manhole(x, y, width, height, is_bottom, properties)

    @property
    def rect(self):
        return self.manhole.horizontal_rect
    
    def update(self, active_manholes, delta_time=1/60):
        """Update manhole state and particle effects."""
        self.manhole.update(active_manholes, delta_time)
    
    def handle_collision(self, ball):
        """Handle collision between manhole and ball."""
        return self.manhole.handle_collision(ball)
    
    def draw(self, screen, color):
        """Override draw method to handle both dormant and spouting states."""
        self.manhole.draw(screen, color, self.scale_rect)
    
    @property
    def is_spouting(self):
        """Get the current spouting state."""
        return self.manhole.is_spouting

class BumperObject(ArenaObject):
    """Pinball bumper that repels the ball with increased velocity."""
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x, y, radius=30):
        """Initialize a bumper object with arena properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.bumper = Bumper(x, y, radius)
    
    @property
    def rect(self):
        return self.bumper.rect
    
    def update(self, delta_time):
        """Update bumper animation."""
        self.bumper.update(delta_time)
    
    def handle_collision(self, ball, sound_manager=None):
        """Handle collision between bumper and ball."""
        collision = self.bumper.handle_collision(ball)
        if collision and sound_manager:
            sound_manager.play_sfx('bumper')
        return collision
    
    def draw(self, screen, color):
        """Draw the bumper with its visual effects."""
        # We ignore the color parameter as the bumper uses its own color scheme
        self.bumper.draw(screen, None, self.scale_rect)

class PowerUpBallObject(ArenaObject):
    """Power-up that creates a duplicate ball on collision."""
    # Added properties parameter
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x, y, size=20, properties=None):
        """Initialize a power-up ball object with arena properties and optional properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.properties = properties if properties is not None else {} # Store properties
        # Note: Base PowerUpBall class doesn't currently use properties, but we store them.
        self.power_up = PowerUpBall(x, y, size)
        self.color = (0, 255, 0)  # Green color for visibility

    @property
    def rect(self):
        return self.power_up.rect
    
    def draw(self, screen, color):
        """Override draw method to use power-up's circular drawing."""
        self.power_up.draw(screen, self.color, self.scale_rect)
    
    def handle_collision(self, ball):
        """Handle collision between power-up and ball."""
        return self.power_up.handle_collision(ball)
    
    def update(self, ball_count, arena_width, arena_height, scoreboard_height, obstacles=None):
        """Update power-up state and check for respawn."""
        return self.power_up.update(ball_count, arena_width, arena_height, scoreboard_height, obstacles)
from Ping.Modules.Graphics.ping_graphics import load_sprite_image # Need the sprite loading function

# Existing code...

class CandleObject(ArenaObject):
    """Represents an animated candle object."""
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect_func, x, y, properties=None):
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect_func)
        self.x = x  # Logical x position (center)
        self.y = y  # Logical y position (center of base)
        self.properties = properties if properties is not None else {}

        # Define candle colors (previously in HAUNTED_HOVEL_COLORS)
        self.candle_body_color = self.properties.get('body_color', (150, 140, 100))
        self.candle_wick_color = self.properties.get('wick_color', (30, 30, 20))
        self.flame_core_color = self.properties.get('flame_core_color', (255, 220, 150))
        self.flame_outer_color = self.properties.get('flame_outer_color', (255, 150, 50, 180))
        self.candle_drip_color = self.properties.get('drip_color', (140, 130, 90))

        # Define candle dimensions (logical)
        self.body_width_logic = self.properties.get('body_width', 4)
        self.body_height_logic = self.properties.get('body_height', 8)
        self.wick_height_logic = self.properties.get('wick_height', 2)
        self.flame_base_height_logic = self.properties.get('flame_height', 6)
        self.flame_base_width_logic = self.properties.get('flame_width', 3)

        # Lighting properties
        self.light_radius_logic = self.properties.get('light_radius', 50) # Logical radius of the light
        self.light_intensity_base = self.properties.get('light_intensity', 0.9) # Base intensity (0 to 1)

        # Animation state for gentle pulsing and swaying
        self.pulse_timer = random.uniform(0, 2 * math.pi)  # Random initial phase for pulsing
        self.pulse_speed = random.uniform(1.5, 2.5)       # Speed of the pulse
        self.pulse_magnitude_visual = self.properties.get('pulse_magnitude_visual', 0.15) # e.g., +/- 15% for flame size
        self.pulse_magnitude_light = self.properties.get('pulse_magnitude_light', 0.1)   # e.g., +/- 10% for light intensity/radius
        
        self.current_visual_factor = 1.0 # For flame size
        self.current_light_factor = 1.0  # For light intensity and radius

        self.flame_sway = 0.0
        self.flame_sway_timer = random.uniform(0, 0.5)
        self.flame_sway_interval = random.uniform(0.2, 0.6)
        # flame_sway_amount will be scale-dependent, calculated in update

        # Define a logical rect for the candle base for potential interactions or positioning
        # Centered at self.x, self.y refers to the center of the base of the candle body
        self._rect_logic = pygame.Rect(
            self.x - self.body_width_logic / 2,
            self.y - self.body_height_logic / 2, # y is center of base, so rect top is y - height/2
            self.body_width_logic,
            self.body_height_logic
        )

    @property
    def rect(self):
        # This rect represents the logical base of the candle
        return self._rect_logic

    def update(self, dt, scale):
        """Update candle animation state for pulsing and swaying."""
        # Update pulse timer
        self.pulse_timer += dt * self.pulse_speed
        if self.pulse_timer > 2 * math.pi: # Keep timer within one cycle for precision
            self.pulse_timer -= 2 * math.pi

        # Calculate pulse factor (0 to 1)
        pulse_value = (math.sin(self.pulse_timer) + 1) / 2.0

        # Update current factors based on pulse
        self.current_visual_factor = 1.0 - self.pulse_magnitude_visual + (self.pulse_magnitude_visual * 2.0 * pulse_value)
        self.current_light_factor = 1.0 - self.pulse_magnitude_light + (self.pulse_magnitude_light * 2.0 * pulse_value)
        
        # Clamp factors to avoid issues, e.g., negative sizes/intensity
        self.current_visual_factor = max(0.1, self.current_visual_factor) # Ensure flame doesn't disappear
        self.current_light_factor = max(0.0, self.current_light_factor)   # Light can go to zero

        # Flame sway logic (remains similar)
        flame_sway_amount_scaled = max(1, int(2 * scale)) # Max sway in pixels
        self.flame_sway_timer += dt
        if self.flame_sway_timer >= self.flame_sway_interval:
            self.flame_sway_timer %= self.flame_sway_interval
            self.flame_sway = random.uniform(-flame_sway_amount_scaled, flame_sway_amount_scaled)

    def draw(self, surface, scale): # Removed unused 'colors' and 'scale_rect_func' from signature for now
        """Draw the candle with its flame."""
        # scale_rect_func is available as self.scale_rect from ArenaObject

        scaled_candle_body_w = max(1, int(self.body_width_logic * scale))
        scaled_candle_body_h = max(1, int(self.body_height_logic * scale))
        scaled_wick_h = max(1, int(self.wick_height_logic * scale))
        scaled_flame_base_h = max(1, int(self.flame_base_height_logic * scale))
        scaled_flame_base_w = max(1, int(self.flame_base_width_logic * scale))

        # Get scaled center position for drawing
        # self.x, self.y is the logical center of the candle's base
        # We need to scale this point to screen coordinates
        scaled_pos_obj = self.scale_rect(pygame.Rect(self.x, self.y, 0, 0)) # Create a 0-size rect to scale the point
        scaled_center_x, scaled_center_y = scaled_pos_obj.center # This is the scaled center of the candle base

        # Draw candle body (small rectangle)
        # The body should be drawn such that scaled_center_x, scaled_center_y is its bottom-center or true center.
        # Let's assume self.y is the y-coordinate of the *base* of the candle body.
        # So, the top of the body rect will be above this.
        
        body_rect_top = scaled_center_y - scaled_candle_body_h # Top of the body
        body_rect = pygame.Rect(
            scaled_center_x - scaled_candle_body_w // 2,
            body_rect_top,
            scaled_candle_body_w,
            scaled_candle_body_h
        )

        # Darker base for candle body
        base_offset = max(1, int(1 * scale))
        body_base_rect = pygame.Rect(body_rect.left, body_rect.bottom - base_offset, body_rect.width, base_offset)
        pygame.draw.rect(surface, (self.candle_body_color[0] - 15, self.candle_body_color[1] - 15, self.candle_body_color[2] - 15), body_base_rect)
        pygame.draw.rect(surface, self.candle_body_color, body_rect)  # Main body on top

        # Wax drips
        num_drips = random.randint(1, 3)
        for _ in range(num_drips):
            drip_x_offset_factor = random.choice([-0.5, 0.5]) # Relative to body width
            drip_x_offset = drip_x_offset_factor * scaled_candle_body_w
            drip_start_y = body_rect.top + random.uniform(0.2, 0.6) * body_rect.height
            drip_length = random.uniform(0.1, 0.4) * body_rect.height
            drip_end_y = drip_start_y + drip_length
            drip_width = max(1, scaled_candle_body_w // 3)
            pygame.draw.line(surface, self.candle_drip_color,
                             (body_rect.centerx + drip_x_offset, drip_start_y),
                             (body_rect.centerx + drip_x_offset, drip_end_y), drip_width)

        # Draw wick
        # Wick starts from the center top of the body_rect
        wick_bottom_x = body_rect.centerx
        wick_bottom_y = body_rect.top
        wick_top_y = wick_bottom_y - scaled_wick_h
        pygame.draw.line(surface, self.candle_wick_color, (wick_bottom_x, wick_bottom_y), (wick_bottom_x, wick_top_y), 1)

        # Candle is always on, flame size modulated by current_visual_factor
        current_flame_h = scaled_flame_base_h * self.current_visual_factor
        current_flame_w = scaled_flame_base_w * self.current_visual_factor * 0.8 # Maintain aspect ratio for width modulation
        current_flame_h = max(1, int(current_flame_h)) # Ensure minimum 1 pixel
        current_flame_w = max(1, int(current_flame_w)) # Ensure minimum 1 pixel

        flame_center_x_draw = wick_bottom_x + self.flame_sway # Flame sways around wick top
        
        # Outer flame (larger, more transparent teardrop)
        # Positioned relative to the top of the wick
        outer_flame_rect = pygame.Rect(0, 0, current_flame_w * 1.5, current_flame_h * 1.2)
        outer_flame_rect.midbottom = (flame_center_x_draw, wick_top_y + max(1, int(1 * scale)))
        if outer_flame_rect.width > 0 and outer_flame_rect.height > 0:
            pygame.draw.ellipse(surface, self.flame_outer_color, outer_flame_rect)

        # Core flame (smaller, brighter teardrop)
        core_flame_h = current_flame_h * 0.7
        core_flame_w = current_flame_w * 0.6
        core_flame_rect = pygame.Rect(0, 0, core_flame_w, core_flame_h)
        core_flame_rect.midbottom = (flame_center_x_draw, wick_top_y)
        if core_flame_rect.width > 0 and core_flame_rect.height > 0:
            pygame.draw.ellipse(surface, self.flame_core_color, core_flame_rect)

        # Simple light glow around the candle flame, modulated by visual factor
        glow_radius = scaled_candle_body_h * 2.0 * self.current_visual_factor # Glow relative to body size & pulse
        glow_radius = max(1, int(glow_radius))
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_color_with_alpha = (self.flame_outer_color[0], self.flame_outer_color[1], self.flame_outer_color[2], 30) # Keep glow subtle
        pygame.draw.circle(glow_surf, glow_color_with_alpha, (glow_radius, glow_radius), glow_radius)
        
        # Glow should be centered around the flame area
        glow_center_x = flame_center_x_draw
        glow_center_y = wick_top_y - current_flame_h / 2 # Center of the flame height
        surface.blit(glow_surf, (glow_center_x - glow_radius, glow_center_y - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)

    def get_light_properties(self, scale):
        """
        Returns the properties needed by the lighting system.
        - scaled_center_x: Screen x-coordinate of the light source center.
        - scaled_center_y: Screen y-coordinate of the light source center.
        - scaled_light_radius: Radius of the light effect in screen pixels.
        - current_intensity: Current light intensity (0 to 1), affected by pulsing.
        """
        # Candle is always on for light properties
        # Calculate scaled position of the light source (flame area)
        # Flame is centered around wick_bottom_x, wick_top_y
        # self.x, self.y is logical base center.
        # scaled_pos_obj = self.scale_rect(pygame.Rect(self.x, self.y, 0, 0))
        # scaled_base_center_x, scaled_base_center_y = scaled_pos_obj.center

        # Replicating some calculations from draw to find flame center
        scaled_candle_body_w = max(1, int(self.body_width_logic * scale))
        scaled_candle_body_h = max(1, int(self.body_height_logic * scale))
        scaled_wick_h = max(1, int(self.wick_height_logic * scale))
        
        scaled_pos_obj = self.scale_rect(pygame.Rect(self.x, self.y, 0, 0))
        scaled_center_x_base, scaled_center_y_base = scaled_pos_obj.center
        
        body_rect_top_scaled = scaled_center_y_base - scaled_candle_body_h
        wick_bottom_x_scaled = scaled_center_x_base
        wick_top_y_scaled = body_rect_top_scaled - scaled_wick_h

        # Light source is roughly at the flame's center
        # Flame sways, so consider self.flame_sway
        light_center_x_scaled = wick_bottom_x_scaled + self.flame_sway
        # Flame base is at wick_top_y_scaled. Flame height is modulated by current_visual_factor
        current_flame_h_scaled = max(1, int(self.flame_base_height_logic * scale * self.current_visual_factor))
        light_center_y_scaled = wick_top_y_scaled - (current_flame_h_scaled / 2)

        # Modulate radius and intensity by current_light_factor
        scaled_radius = self.light_radius_logic * scale * self.current_light_factor
        scaled_radius = max(0, scaled_radius) # Ensure radius is not negative

        current_intensity = self.light_intensity_base * self.current_light_factor
        current_intensity = max(0, min(1, current_intensity)) # Clamp to 0-1

        return {
            'x': light_center_x_scaled,
            'y': light_center_y_scaled,
            'radius': scaled_radius,
            'intensity': current_intensity
        }

    def handle_collision(self, ball, sound_manager=None):
        """Candles typically don't have collision effects, but method can be here for interface consistency."""
        return None # No collision effect
class SpriteObject(ArenaObject):
    """Represents a static sprite decoration loaded from the level."""
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x, y, width, height, image_path, properties=None):
        """Initialize a sprite object."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.properties = properties if properties is not None else {} # Store extra properties if needed
        self.image_path = image_path
        # Store logical rect based on PMF data, treating x, y as CENTER coordinates
        # Calculate top-left for pygame.Rect constructor
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)

        # Load the original image first
        original_surface = load_sprite_image(image_path)
        self.surface = None # Initialize surface to None

        if original_surface:
            try:
                # Scale the loaded image to the dimensions defined in the PMF
                # Use smoothscale for better quality, scale for performance
                print(f"DEBUG SpriteObject: Scaling sprite '{image_path}' to ({width}x{height})")
                self.surface = pygame.transform.smoothscale(original_surface, (width, height))
            except Exception as e:
                 print(f"Error scaling sprite image '{image_path}' to ({width}x{height}): {e}")
                 # Optionally, keep the original surface if scaling fails? Or set to None?
                 # Setting to None means it won't draw if scaling fails.
                 self.surface = None
        else:
            print(f"Warning: Failed to load sprite image '{image_path}' for SpriteObject at ({x},{y}). Cannot scale or draw.")
            
        # Note: The self.rect uses the width/height from the PMF/editor.
        # The loaded surface might have different dimensions, but we blit at the defined x, y.

    # Override draw method to use the loaded surface
    def draw(self, screen): # Does not need 'color' argument
        """Draw the sprite if its surface was loaded."""
        # Add a debug log inside the draw method
        # print(f"DEBUG: SpriteObject.draw called for path: {self.image_path}. Surface exists: {self.surface is not None}") # Uncomment if verbose logging needed
        if self.surface:
            # Use the ArenaObject's scale_rect to get the drawing position and handle scaling/offset
            # We scale the position (rect.topleft) but not the surface itself
            scaled_rect = self.scale_rect(self.rect)
            # Adding a print statement here to confirm draw *is attempting* to blit
            print(f"DEBUG: Drawing sprite '{self.image_path}' at {scaled_rect.topleft}")
            screen.blit(self.surface, scaled_rect.topleft)
        # else: # Optionally log when surface is None
            # print(f"DEBUG: Skipping draw for sprite '{self.image_path}' - surface not loaded.") # Uncomment if needed

        # No placeholder drawing here; if load failed, it simply won't draw.

    # Static sprites typically don't need update or collision handling
    def update(self, *args, **kwargs): 
        pass

    def handle_collision(self, *args, **kwargs):
        return None
class GhostObstacleObject(ArenaObject):
    """Ghost obstacle that appears, floats, rushes, and possesses the ball."""
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x, y, width, height, game_ball_instance, properties=None):
        """Initialize a ghost object with arena properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        # Pass the arena_rect directly to the GhostObstacle
        # The arena for the ghost should be the playable area, excluding scoreboard.
        arena_game_rect = pygame.Rect(0, scoreboard_height, arena_width, arena_height - scoreboard_height)
        self.ghost = GhostObstacle(x, y, width, height, arena_game_rect, game_ball_instance, properties)

    @property
    def rect(self):
        return self.ghost.rect

    def update(self, delta_time, game_ball_instance, candles=None, pickles_list=None, scale_factor=1.0, scale_rect_func=None):
        """Update ghost state and behavior."""
        self.ghost.update(delta_time, game_ball_instance, candles, pickles_list, scale_factor, scale_rect_func)

    def draw(self, screen, colors): # colors might be used by the ghost's draw method
        """Draw the ghost."""
        # The GhostObstacle.draw method expects colors and scale_rect.
        # self.scale_rect is inherited from ArenaObject.
        self.ghost.draw(screen, colors, self.scale_rect)

    def handle_collision(self, ball_instance):
        """Handle collision between ghost and ball."""
        # This might not be strictly necessary if all collision logic is in update,
        # but good for interface consistency.
        return self.ghost.handle_collision(ball_instance)

    def is_done(self):
        """Checks if the ghost is inactive and can be removed."""
        return self.ghost.is_done()

    @property
    def is_active_instance(self):
        """Returns if this ghost instance is active (respecting MAX_GHOSTS_ON_SCREEN)."""
        # The GhostObstacle itself manages its active status via is_active_instance
        return self.ghost.is_active_instance
class Pickles(ArenaObject):
    """
    A black cat character named Pickles that can be asleep or chase ghosts.
    """
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x, y, properties=None):
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.properties = properties if properties is not None else {}
        self.initial_x = x
        self.initial_y = y
        self.float_x = float(x) # Internal float position
        self.float_y = float(y) # Internal float position
        
        # Visuals - Placeholder: simple black cat.
        # For a sprite, you would load an image here similar to SpriteObject
        # self.image = load_sprite_image("path/to/pickles_sprite.png") # Example
        # self.image = pygame.transform.scale(self.image, (width, height))
        self.width = self.properties.get('width', 60) # Increased width
        self.height = self.properties.get('height', 40) # Increased height
        self.color = (10, 10, 10) # Very dark grey for black cat

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (round(self.float_x), round(self.float_y))
        
        self.state = "asleep"  # Initial state: "asleep" or "chasing"
        self.speed = self.properties.get('speed', 180) # Pixels per second
        self.activation_radius = self.properties.get('activation_radius', 100) # Radius to wake up

        self.target_ghost = None
        self.target_candle = None
        self.carried_ghost = None
        self.grab_distance = self.properties.get('grab_distance', 30) # pixels
        self.carrying_speed = self.properties.get('carrying_speed', self.speed * 1.75) # Faster when carrying
        
        # Cooldown to prevent immediate re-chasing
        self.action_cooldown_time = 2.0 # seconds
        self.current_action_cooldown = 0.0

    def update(self, delta_time, game_objects, scale_factor=1.0):
        """
        Update Pickles' state and behavior.
        game_objects is a dictionary expected to contain lists of 'balls', 'ghosts', 'candles'.
        """
        balls_list = game_objects.get('balls', [])
        candles_list = game_objects.get('candles', [])

        if self.current_action_cooldown > 0:
            self.current_action_cooldown -= delta_time
            if self.current_action_cooldown <= 0:
                self.current_action_cooldown = 0
                # If chasing and the target ghost is gone
                if self.state == "chasing" and not self.target_ghost:
                    self.go_to_sleep()


        if self.state == "asleep":
            if self.current_action_cooldown <= 0: # Only wake up if not on cooldown
                pickles_center = pygame.math.Vector2(self.float_x, self.float_y) # Use float coords

                for i, ball in enumerate(balls_list): # Use balls_list
                    if not hasattr(ball, 'rect'):
                        continue
                    
                    ball_center = pygame.math.Vector2(ball.rect.centerx, ball.rect.centery)
                    distance = pickles_center.distance_to(ball_center)
                    
                    if distance < self.activation_radius:
                        self.transition_to_chasing(game_objects)
                        break
        
        elif self.state == "chasing":
            # Check if the target ghost still exists or is active
            current_ghosts = game_objects.get('ghosts', [])
            ghost_is_valid = False
            if self.target_ghost:
                if self.target_ghost in current_ghosts:
                    is_active = getattr(self.target_ghost, 'is_active_instance', True) # Default to True if no attribute
                    is_done_method = getattr(self.target_ghost, 'is_done', None)
                    is_done_val = is_done_method() if callable(is_done_method) else False
                    if is_active and not is_done_val:
                        ghost_is_valid = True
            
            if not ghost_is_valid:
                self.target_ghost = None # Clear invalid ghost
                self.go_to_sleep()
                return
 
            # If ghost is valid, proceed.
            if self.target_ghost:
                # Check if Pickles can grab the ghost
                pickles_center_vec = pygame.math.Vector2(self.float_x, self.float_y) # Use float coords
                ghost_center_vec = pygame.math.Vector2(self.target_ghost.rect.centerx, self.target_ghost.rect.centery)
                distance_to_ghost = pickles_center_vec.distance_to(ghost_center_vec)

                if distance_to_ghost < self.grab_distance:
                    self.state = "carrying_ghost"
                    self.carried_ghost = self.target_ghost
                    if hasattr(self.carried_ghost, 'ghost') and hasattr(self.carried_ghost.ghost, 'is_controlled_externally'):
                        self.carried_ghost.ghost.is_controlled_externally = True
                    
                    # Find a candle only AFTER grabbing the ghost
                    self.find_nearest_candle(candles_list)
                    if not self.target_candle: # If no candle found to take the ghost to
                        if hasattr(self.carried_ghost, 'ghost') and hasattr(self.carried_ghost.ghost, 'is_controlled_externally'):
                            self.carried_ghost.ghost.is_controlled_externally = False # Release control
                        self.carried_ghost = None # Drop the ghost
                        self.go_to_sleep() # Pickles gives up for now
                        self.current_action_cooldown = self.action_cooldown_time # Cooldown before trying again
                        return
                    return # Transitioned state to carrying_ghost, process next frame

                # If not grabbing, move directly towards the ghost
                self.move_towards_target(delta_time)
            # If self.target_ghost became None somehow (e.g. external removal not caught by initial check), go to sleep.
            # This case should ideally be covered by the initial ghost_is_valid check.
            # else:
            #     self.go_to_sleep()

        elif self.state == "carrying_ghost":
            if not self.carried_ghost or not self.target_candle:
                if self.carried_ghost and hasattr(self.carried_ghost, 'ghost') and hasattr(self.carried_ghost.ghost, 'is_controlled_externally'):
                    self.carried_ghost.ghost.is_controlled_externally = False
                self.carried_ghost = None # Ensure it's cleared
                self.go_to_sleep()
                return

            # Ensure carried ghost is still valid
            current_ghosts = game_objects.get('ghosts', [])
            ghost_is_valid = False
            if self.carried_ghost in current_ghosts:
                is_active = getattr(self.carried_ghost, 'is_active_instance', True)
                is_done_method = getattr(self.carried_ghost, 'is_done', None)
                is_done_val = is_done_method() if callable(is_done_method) else False
                if is_active and not is_done_val:
                    ghost_is_valid = True
            
            if not ghost_is_valid:
                if self.carried_ghost and hasattr(self.carried_ghost, 'ghost') and hasattr(self.carried_ghost.ghost, 'is_controlled_externally'):
                    self.carried_ghost.ghost.is_controlled_externally = False
                self.carried_ghost = None
                self.go_to_sleep()
                return

            # --- Light Check for Carried Ghost ---
            if self.carried_ghost and hasattr(self.carried_ghost, 'ghost') and candles_list:
                carried_ghost_screen_rect = self.scale_rect(self.carried_ghost.rect)
                if carried_ghost_screen_rect and carried_ghost_screen_rect.width > 0: # Check if rect is valid
                    for candle_obj_wrapper in candles_list:
                        if candle_obj_wrapper and hasattr(candle_obj_wrapper, 'get_light_properties'):
                            light_props = candle_obj_wrapper.get_light_properties(scale_factor)
                            light_x, light_y = light_props['x'], light_props['y']
                            light_radius, light_intensity = light_props['radius'], light_props['intensity']

                            if light_intensity > 0.1 and light_radius > 0:
                                dx_light = carried_ghost_screen_rect.centerx - light_x
                                dy_light = carried_ghost_screen_rect.centery - light_y
                                distance_sq_light = dx_light*dx_light + dy_light*dy_light
                                effective_ghost_radius = carried_ghost_screen_rect.width / 2
                                
                                critical_distance_sq = (light_radius * 0.6)**2 # Increased sensitivity
                                very_close_distance_sq = (effective_ghost_radius * 0.8)**2 # Increased sensitivity

                                if distance_sq_light < critical_distance_sq or distance_sq_light < very_close_distance_sq:
                                    if hasattr(self.carried_ghost.ghost, 'force_fade_out_in_light'):
                                        self.carried_ghost.ghost.force_fade_out_in_light()
                                    # Pickles releases the ghost
                                    self.carried_ghost = None # is_controlled_externally is set False in force_fade_out_in_light
                                    self.go_to_sleep() # Or another state like cooldown
                                    self.current_action_cooldown = self.action_cooldown_time # Apply cooldown
                                    return # Ghost is fading, Pickles' turn is over for this ghost
            
            if not self.carried_ghost: # If ghost was destroyed by light, exit update
                return

            # Move Pickles towards the target candle at carrying speed
            candle_pos_vec = pygame.math.Vector2(self.target_candle.rect.centerx, self.target_candle.rect.centery)
            current_pos_vec = pygame.math.Vector2(self.float_x, self.float_y) # Use float coords
            
            direction_to_candle = candle_pos_vec - current_pos_vec
            distance_to_candle = direction_to_candle.length()

            if distance_to_candle > 0: # Check to avoid division by zero if already at candle
                move_amount_this_frame = self.carrying_speed * delta_time
                if distance_to_candle <= move_amount_this_frame:
                    # Snap to candle
                    self.float_x = candle_pos_vec.x
                    self.float_y = candle_pos_vec.y
                else:
                    direction_normalized = direction_to_candle.normalize()
                    move_vector = direction_normalized * move_amount_this_frame
                    self.float_x += move_vector.x
                    self.float_y += move_vector.y
                
                # Arena bounds check for float coordinates (center based)
                self.float_x = max(self.width / 2, min(self.float_x, self.arena_width - self.width / 2))
                self.float_y = max(self.scoreboard_height + self.height / 2, min(self.float_y, self.arena_height - self.height / 2))
            
            # Make the carried ghost follow Pickles
            # Position ghost slightly in front of Pickles, in direction of candle
            if direction_to_candle.length_squared() > 0: # Use the normalized direction if available
                direction_normalized_for_ghost_pos = direction_to_candle.normalize()
                offset_distance = self.width * 0.6 # Ghost slightly ahead
                # Ghost target position based on Pickles' float position for precision
                ghost_target_pos_float = pygame.math.Vector2(self.float_x, self.float_y) + direction_normalized_for_ghost_pos * offset_distance
                self.carried_ghost.rect.center = (round(ghost_target_pos_float.x), round(ghost_target_pos_float.y))
            else: # Pickles is at the candle (or very close)
                self.carried_ghost.rect.center = (round(self.float_x), round(self.float_y))


            # Check if ghost reached the candle (delivery)
            # Use carried_ghost.rect.center which is already updated based on Pickles' new position
            carried_ghost_center_vec = pygame.math.Vector2(self.carried_ghost.rect.centerx, self.carried_ghost.rect.centery)
            distance_ghost_to_candle_delivery = carried_ghost_center_vec.distance_to(candle_pos_vec)
            
            delivery_threshold = self.properties.get('delivery_threshold', 20) # Renamed for clarity
            if distance_ghost_to_candle_delivery < delivery_threshold:
                # Ghost delivered! Pickles releases the ghost.
                if self.carried_ghost and hasattr(self.carried_ghost, 'ghost') and hasattr(self.carried_ghost.ghost, 'is_controlled_externally'):
                    self.carried_ghost.ghost.is_controlled_externally = False
                # The ghost's own interaction logic with the candle should take over.
                self.carried_ghost = None
                self.go_to_sleep()
                self.current_action_cooldown = self.action_cooldown_time
                return
        
        # Update self.rect from float_x, float_y at the end of the update cycle
        self.rect.center = (round(self.float_x), round(self.float_y))

    def transition_to_chasing(self, game_objects):
        self.state = "chasing"
        self.target_candle = None # Ensure target_candle is None when starting to chase
        self.find_nearest_ghost(game_objects.get('ghosts', []))
        if not self.target_ghost: # Only need a ghost to start chasing
            self.go_to_sleep()

    def go_to_sleep(self):
        if self.carried_ghost and hasattr(self.carried_ghost, 'ghost') and hasattr(self.carried_ghost.ghost, 'is_controlled_externally'):
             self.carried_ghost.ghost.is_controlled_externally = False
        self.carried_ghost = None # Ensure it's cleared if Pickles goes to sleep for any reason while carrying
        self.state = "asleep"
        self.target_ghost = None
        self.target_candle = None
        # Optionally, return to a specific "bed" location or initial position
        # self.float_x = self.initial_x
        # self.float_y = self.initial_y
        # self.rect.center = (round(self.float_x), round(self.float_y))


    def find_nearest_object(self, objects_list):
        nearest_obj = None
        min_dist_sq = float('inf')
        
        if not objects_list:
            return None

        pickles_pos = pygame.math.Vector2(self.float_x, self.float_y) # Use float coords

        for obj in objects_list:
            # Assuming objects have a 'rect' attribute
            if hasattr(obj, 'rect'):
                # For GhostObstacleObject, ensure it's an active instance
                if isinstance(obj, GhostObstacleObject) and not obj.is_active_instance:
                    continue 
                # For CandleObject, it's always "active" for targeting
                
                obj_pos = pygame.math.Vector2(obj.rect.centerx, obj.rect.centery)
                dist_sq = pickles_pos.distance_squared_to(obj_pos)
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    nearest_obj = obj
        return nearest_obj

    def find_nearest_ghost(self, ghosts):
        # Filter for active ghosts if GhostObstacleObject has an 'is_active_instance' property
        active_ghosts = [g for g in ghosts if hasattr(g, 'is_active_instance') and g.is_active_instance]
        if not active_ghosts: # If no active ghosts, check all ghosts (fallback)
            active_ghosts = ghosts

        self.target_ghost = self.find_nearest_object(active_ghosts)


    def find_nearest_candle(self, candles):
        self.target_candle = self.find_nearest_object(candles)

    def move_towards_target(self, delta_time):
        # This method is now only for moving directly towards self.target_ghost
        if not self.target_ghost:
            return
        
        target_pos_vec = pygame.math.Vector2(self.target_ghost.rect.centerx, self.target_ghost.rect.centery)
        current_pos_vec = pygame.math.Vector2(self.float_x, self.float_y)
        
        direction_to_target = target_pos_vec - current_pos_vec
        distance_to_target = direction_to_target.length()
        
        if distance_to_target == 0: # Already at the target
            return

        move_amount_this_frame = self.speed * delta_time

        if distance_to_target <= move_amount_this_frame:
            # Snap to target if closer than one step
            self.float_x = target_pos_vec.x
            self.float_y = target_pos_vec.y
        else:
            # Move towards target
            direction_normalized = direction_to_target.normalize()
            move_vector = direction_normalized * move_amount_this_frame
            self.float_x += move_vector.x
            self.float_y += move_vector.y

        # Arena bounds check for float coordinates (center based)
        # self.rect.width and self.rect.height are used here, assuming they are correctly set.
        # Alternatively, use self.width and self.height directly.
        half_width = self.width / 2
        half_height = self.height / 2
        
        self.float_x = max(half_width, min(self.float_x, self.arena_width - half_width))
        self.float_y = max(self.scoreboard_height + half_height, min(self.float_y, self.arena_height - half_height))
        
        # self.rect.center will be updated at the end of the main update method.


    def draw(self, screen, colors=None):
        # print(f"Pickles.draw() called. State: {self.state}") # Confirm draw method entry. REMOVED TO REDUCE SPAM
        sr = self.scale_rect(self.rect) # Scaled rect for drawing
        # print(f"Pickles.draw(): type(sr)={type(sr)}, sr={sr}, self.rect={self.rect}") # REMOVED TO REDUCE SPAM

        # Define Pickles' detailed color palette
        cat_fur_main = (12, 12, 18)      # Very dark, slightly desaturated blueish-black
        cat_fur_shadow = (5, 5, 8)        # Deeper shadow color
        cat_fur_highlight = (30, 30, 40)  # Subtle cool highlight
        cat_eye_sclera = (240, 245, 230)  # Bright, slightly yellowish-white for eyes
        cat_eye_pupil = (5, 5, 5)          # Deep black pupil
        cat_eye_glint = (255, 255, 255)    # Pure white for eye glint
        cat_inner_ear = (45, 35, 40)      # Dark, desaturated pink/grey for inner ear
        cat_nose_color = (30, 20, 20)      # Small, dark, slightly warm nose
        cat_whisker_color = (180, 180, 190) # Light grey, slightly cool whiskers
        cat_closed_eye_color = (55, 55, 60) # Color for closed eye lines

        if not (hasattr(sr, 'width') and hasattr(sr, 'height') and sr.width > 0 and sr.height > 0):
            # print(f"Pickles.draw(): sr is invalid or zero size: {sr}. Drawing fallback red rect.") # REMOVED TO REDUCE SPAM
            pygame.draw.rect(screen, (255,0,0), pygame.Rect(int(self.rect.x), int(self.rect.y), 5,5))
            return # Stop drawing if sr is bad

        if self.state == "asleep":
            # --- Asleep State (Detailed) ---
            body_w = max(1, int(sr.width * 0.85))
            body_h = max(1, int(sr.height * 0.7))
            body_ellipse_rect = pygame.Rect(int(sr.centerx - body_w / 2), int(sr.centery - body_h / 2 + sr.height * 0.1), body_w, body_h)
            pygame.draw.ellipse(screen, cat_fur_shadow, body_ellipse_rect.move(max(1,int(sr.width*0.01)),max(1,int(sr.width*0.01))))
            pygame.draw.ellipse(screen, cat_fur_main, body_ellipse_rect)

            head_w = max(1, int(sr.width * 0.5))
            head_h = max(1, int(sr.height * 0.45))
            head_ellipse_rect = pygame.Rect(int(sr.centerx - head_w * 0.3), int(sr.centery - head_h * 0.5 - sr.height * 0.05), head_w, head_h)
            pygame.draw.ellipse(screen, cat_fur_shadow, head_ellipse_rect.move(max(1,int(sr.width*0.01)),max(1,int(sr.width*0.01))))
            pygame.draw.ellipse(screen, cat_fur_main, head_ellipse_rect)
            
            eye_y_asleep = int(head_ellipse_rect.centery + head_h * 0.05)
            eye_arc_width = max(1, int(head_w * 0.25))
            eye_arc_height = max(1, int(head_h * 0.2))
            line_thickness = max(1,int(sr.width*0.02))
            
            pygame.draw.arc(screen, cat_closed_eye_color,
                            [int(head_ellipse_rect.centerx - head_w * 0.25 - eye_arc_width/2), int(eye_y_asleep - eye_arc_height/2), eye_arc_width, eye_arc_height],
                            math.pi * 0.2, math.pi * 0.8, line_thickness)
            pygame.draw.arc(screen, cat_closed_eye_color,
                            [int(head_ellipse_rect.centerx + head_w * 0.05 - eye_arc_width/2), int(eye_y_asleep - eye_arc_height/2), eye_arc_width, eye_arc_height],
                            math.pi * 0.2, math.pi * 0.8, line_thickness)

            ear_base_x_l = int(head_ellipse_rect.left + head_w * 0.15)
            ear_top_y_l = int(head_ellipse_rect.top + head_h * 0.1)
            pygame.draw.polygon(screen, cat_fur_main, [
                (ear_base_x_l, ear_top_y_l),
                (int(ear_base_x_l + head_w * 0.15), int(head_ellipse_rect.top + head_h * 0.05)),
                (int(ear_base_x_l + head_w * 0.10), int(ear_top_y_l + head_h * 0.15))
            ])
            ear_base_x_r = int(head_ellipse_rect.right - head_w * 0.15)
            ear_top_y_r = int(head_ellipse_rect.top + head_h * 0.1)
            pygame.draw.polygon(screen, cat_fur_main, [
                (ear_base_x_r, ear_top_y_r),
                (int(ear_base_x_r - head_w * 0.15), int(head_ellipse_rect.top + head_h * 0.05)),
                (int(ear_base_x_r - head_w * 0.10), int(ear_top_y_r + head_h * 0.15))
            ])
            
            tail_points = [
                (int(body_ellipse_rect.right - body_w * 0.2), int(body_ellipse_rect.centery + body_h * 0.2)),
                (int(body_ellipse_rect.right + sr.width * 0.05), int(body_ellipse_rect.centery)),
                (int(body_ellipse_rect.right - body_w * 0.1), int(body_ellipse_rect.centery - body_h * 0.25))
            ]
            if len(tail_points) > 1:
                 pygame.draw.lines(screen, cat_fur_main, False, tail_points, max(2, int(sr.width * 0.05)))

        else: # Awake / Chasing State - Inspired by the image
            body_width = max(1, int(sr.width * 0.65))
            body_height = max(1, int(sr.height * 0.8))
            body_center_x = int(sr.centerx + sr.width * 0.1)
            body_center_y = int(sr.bottom - body_height * 0.5)
            body_rect = pygame.Rect(0, 0, body_width, body_height)
            body_rect.center = (body_center_x, body_center_y)
            
            highlight_body_rect = body_rect.copy()
            highlight_body_rect.width = max(1, int(body_rect.width * 0.5))
            highlight_body_rect.left = body_rect.left
            
            shadow_offset_val = max(1, int(sr.width*0.02))
            pygame.draw.ellipse(screen, cat_fur_shadow, body_rect.move(shadow_offset_val, shadow_offset_val))
            pygame.draw.ellipse(screen, cat_fur_main, body_rect)
            # Removed special_flags from the highlight ellipse; it's not a valid param for draw.ellipse
            # If blending is needed, it would require a separate surface and blit operation.
            pygame.draw.ellipse(screen, cat_fur_highlight, highlight_body_rect)

            neck_width_base = max(1, int(body_width * 0.35))
            neck_width_top = max(1, int(sr.width * 0.28))
            neck_height_factor = 0.4
            
            neck_poly = [
                (int(body_rect.centerx - neck_width_base * 0.4), int(body_rect.top + body_height * 0.1)),
                (int(body_rect.centerx + neck_width_base * 0.6), int(body_rect.top + body_height * 0.15)),
                (int(sr.centerx + neck_width_top * 0.5 - sr.width * 0.05), int(sr.top + sr.height * (0.5 - neck_height_factor*0.5))),
                (int(sr.centerx - neck_width_top * 0.5 - sr.width * 0.05), int(sr.top + sr.height * (0.5 - neck_height_factor*0.55)))
            ]
            pygame.draw.polygon(screen, cat_fur_shadow, [(p[0]+shadow_offset_val//2, p[1]+shadow_offset_val//2) for p in neck_poly])
            pygame.draw.polygon(screen, cat_fur_main, neck_poly)
            
            head_width = max(1, int(sr.width * 0.48))
            head_height = max(1, int(sr.height * 0.42))
            head_center_x = int(sr.centerx - sr.width * 0.08)
            head_center_y = int(sr.top + sr.height * 0.22)
            head_rect = pygame.Rect(0, 0, head_width, head_height)
            head_rect.center = (head_center_x, head_center_y)
            
            highlight_head_rect = head_rect.copy()
            highlight_head_rect.width = max(1, int(head_rect.width * 0.4))
            highlight_head_rect.left = head_rect.left

            pygame.draw.ellipse(screen, cat_fur_shadow, head_rect.move(shadow_offset_val//2, shadow_offset_val//2))
            pygame.draw.ellipse(screen, cat_fur_main, head_rect)
            # Removed special_flags from the highlight ellipse
            pygame.draw.ellipse(screen, cat_fur_highlight, highlight_head_rect)

            ear_height = max(1, int(head_height * 1.1))
            ear_width_base = max(1, int(head_width * 0.4))
            ear_offset_x = int(head_width * 0.25)

            L_ear_tip = (int(head_rect.centerx - ear_offset_x), int(head_rect.top - ear_height * 0.7))
            L_ear_base_outer = (int(head_rect.left + head_width * 0.05), int(head_rect.centery - head_height * 0.3))
            L_ear_base_inner = (int(head_rect.centerx - ear_offset_x + ear_width_base * 0.3), int(head_rect.centery - head_height*0.15))
            pygame.draw.polygon(screen, cat_fur_main, [L_ear_tip, L_ear_base_outer, L_ear_base_inner])
            L_inner_ear_points = [
                (L_ear_tip[0], int(L_ear_tip[1] + ear_height * 0.2)),
                (int(L_ear_base_outer[0] + ear_width_base * 0.15), int(L_ear_base_outer[1] + head_height * 0.05)),
                (int(L_ear_base_inner[0] - ear_width_base * 0.05), int(L_ear_base_inner[1] + head_height * 0.05)) ]
            pygame.draw.polygon(screen, cat_inner_ear, L_inner_ear_points)

            R_ear_tip = (int(head_rect.centerx + ear_offset_x), int(head_rect.top - ear_height * 0.7))
            R_ear_base_outer = (int(head_rect.right - head_width * 0.05), int(head_rect.centery - head_height * 0.3))
            R_ear_base_inner = (int(head_rect.centerx + ear_offset_x - ear_width_base * 0.3), int(head_rect.centery - head_height*0.15))
            pygame.draw.polygon(screen, cat_fur_main, [R_ear_tip, R_ear_base_outer, R_ear_base_inner])
            R_inner_ear_points = [
                (R_ear_tip[0], int(R_ear_tip[1] + ear_height * 0.2)),
                (int(R_ear_base_outer[0] - ear_width_base * 0.15), int(R_ear_base_outer[1] + head_height * 0.05)),
                (int(R_ear_base_inner[0] + ear_width_base * 0.05), int(R_ear_base_inner[1] + head_height * 0.05)) ]
            pygame.draw.polygon(screen, cat_inner_ear, R_inner_ear_points)

            eye_radius = max(1, int(head_height * 0.33))
            pupil_radius = max(1, int(eye_radius * 0.45))
            eye_y_pos = int(head_rect.centery + head_height * 0.05)
            L_eye_center_x = int(head_rect.centerx - head_width * 0.22)
            R_eye_center_x = int(head_rect.centerx + head_width * 0.22)
            glint_radius = max(1, int(eye_radius * 0.2))
            glint_offset_x = int(-eye_radius * 0.2)
            glint_offset_y = int(-eye_radius * 0.2)

            pygame.draw.circle(screen, cat_eye_sclera, (L_eye_center_x, eye_y_pos), eye_radius)
            pygame.draw.circle(screen, cat_eye_pupil, (L_eye_center_x, eye_y_pos), pupil_radius)
            pygame.draw.circle(screen, cat_eye_glint, (L_eye_center_x + glint_offset_x, eye_y_pos + glint_offset_y), glint_radius)

            pygame.draw.circle(screen, cat_eye_sclera, (R_eye_center_x, eye_y_pos), eye_radius)
            pygame.draw.circle(screen, cat_eye_pupil, (R_eye_center_x, eye_y_pos), pupil_radius)
            pygame.draw.circle(screen, cat_eye_glint, (R_eye_center_x + glint_offset_x, eye_y_pos + glint_offset_y), glint_radius)

            nose_width = max(1, int(head_width * 0.12))
            nose_height = max(1, int(head_height * 0.08))
            nose_y = int(eye_y_pos + eye_radius * 0.6)
            nose_rect = pygame.Rect(int(head_rect.centerx - nose_width/2), nose_y, nose_width, nose_height)
            pygame.draw.ellipse(screen, cat_nose_color, nose_rect)

            whisker_length = head_width * 0.3
            num_whiskers = 3
            whisker_y_base = int(nose_y + nose_height * 0.5)
            whisker_thickness = max(1, int(sr.width * 0.005)) # Ensure whiskers are at least 1px thick
            
            for i in range(num_whiskers):
                angle_l = math.pi * (0.9 + i * 0.08)
                start_lx = int(head_rect.centerx - head_width * 0.1)
                end_lx = int(start_lx - whisker_length * math.cos(angle_l))
                end_ly = int(whisker_y_base - whisker_length * math.sin(angle_l) * 0.7)
                pygame.draw.line(screen, cat_whisker_color, (start_lx, whisker_y_base), (end_lx, end_ly), whisker_thickness)
                
                angle_r = math.pi * (0.1 - i * 0.08)
                start_rx = int(head_rect.centerx + head_width * 0.1)
                end_rx = int(start_rx + whisker_length * math.cos(angle_r))
                end_ry = int(whisker_y_base - whisker_length * math.sin(angle_r) * 0.7)
                pygame.draw.line(screen, cat_whisker_color, (start_rx, whisker_y_base), (end_rx, end_ry), whisker_thickness)

            tail_segment_len = sr.width * 0.15
            tail_thickness = max(2, int(sr.width * 0.04))
            tail_start_x = int(body_rect.left + body_width * 0.15)
            tail_start_y = int(body_rect.centery + body_height * 0.3)
            tail_points_awake = [
                (tail_start_x, tail_start_y),
                (int(tail_start_x - tail_segment_len * 0.7), int(tail_start_y - tail_segment_len * 0.3)),
                (int(tail_start_x - tail_segment_len * 1.2), int(tail_start_y - tail_segment_len * 0.2)) ]
            if len(tail_points_awake) > 1:
                pygame.draw.lines(screen, cat_fur_main, False, tail_points_awake, tail_thickness)


# Make sure to add Pickles to any relevant lists or import statements if needed elsewhere.
# For example, if there's a factory method or a list of known game object types.