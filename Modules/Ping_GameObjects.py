import pygame
import math
import random
from .Submodules.Ping_Ball import Ball
from .Submodules.Ping_Paddle import Paddle
from .Submodules.Ping_Obstacles import Obstacle, Goal, Portal, PowerUpBall, Manhole  # Added Manhole for Sewer Level

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
    
    def lerp_color(self, color1, color2, t):
        """Linearly interpolate between two colors."""
        return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))
    
    def draw(self, screen, color):
        """Draw the paddle with retro Sega Genesis style and ultra-smooth gradient."""
        scaled_rect = self.scale_rect(self.rect)
        
        # Define key colors
        light_brown = (205, 175, 149)  # Back side
        base_color = color             # Middle
        green_shade = (30, 180, 30)    # Left paddle front
        red_shade = (180, 30, 30)      # Right paddle front
        
        # Number of gradient sections (more sections = smoother gradient)
        num_sections = 12
        section_width = scaled_rect.width / num_sections
        
        if self.is_left_paddle:
            # Left paddle gradient (light brown → base → green)
            for i in range(num_sections):
                t = i / (num_sections - 1)  # Interpolation factor
                
                # First half: brown to base color
                if i < num_sections // 2:
                    t_adjusted = t * 2  # Adjust t for first half
                    current_color = self.lerp_color(light_brown, base_color, t_adjusted)
                # Second half: base color to green
                else:
                    t_adjusted = (t - 0.5) * 2  # Adjust t for second half
                    current_color = self.lerp_color(base_color, green_shade, t_adjusted)
                
                # Draw section
                section_rect = pygame.Rect(
                    scaled_rect.left + (i * section_width),
                    scaled_rect.top,
                    section_width + 1,  # +1 to prevent gaps
                    scaled_rect.height
                )
                
                # Apply border radius consistently
                if i == 0:  # Left-most section (back)
                    pygame.draw.rect(screen, current_color, section_rect,
                                   border_radius=4,
                                   border_top_right_radius=0,
                                   border_bottom_right_radius=0)
                elif i == num_sections - 1:  # Right-most section (front)
                    pygame.draw.rect(screen, current_color, section_rect,
                                   border_radius=4,
                                   border_top_left_radius=0,
                                   border_bottom_left_radius=0)
                else:  # Middle sections
                    pygame.draw.rect(screen, current_color, section_rect)
        else:
            # Right paddle gradient (brown → base → red)
            for i in range(num_sections):
                t = i / (num_sections - 1)
                
                # First half: brown to base color
                if i < num_sections // 2:
                    t_adjusted = t * 2
                    current_color = self.lerp_color(light_brown, base_color, t_adjusted)
                # Second half: base color to red
                else:
                    t_adjusted = (t - 0.5) * 2
                    current_color = self.lerp_color(base_color, red_shade, t_adjusted)
                
                # Draw section
                section_rect = pygame.Rect(
                    scaled_rect.right - ((i + 1) * section_width),
                    scaled_rect.top,
                    section_width + 1,  # +1 to prevent gaps
                    scaled_rect.height
                )
                
                # Apply border radius consistently
                if i == 0:  # Right-most section (back)
                    pygame.draw.rect(screen, current_color, section_rect,
                                   border_radius=4,
                                   border_top_left_radius=0,
                                   border_bottom_left_radius=0)
                elif i == num_sections - 1:  # Left-most section (front)
                    pygame.draw.rect(screen, current_color, section_rect,
                                   border_radius=4,
                                   border_top_right_radius=0,
                                   border_bottom_right_radius=0)
                else:  # Middle sections
                    pygame.draw.rect(screen, current_color, section_rect)

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
    
    def draw(self, screen, color):
        """Draw the portal as a black rectangle."""
        scaled_rect = self.scale_rect(self.rect)
        pygame.draw.rect(screen, color, scaled_rect)

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
        
    def draw(self, screen, color):
        """Draw the obstacle as a pixelated brick wall."""
        scaled_rect = self.scale_rect(self.rect)
        
        # Create brick and mortar colors with brown tinting
        r, g, b = color
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
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x, y, width, height, is_bottom=True):
        """Initialize a manhole object with arena properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
        self.manhole = Manhole(x, y, width, height, is_bottom)
    
    @property
    def rect(self):
        return self.manhole.horizontal_rect
    
    def update(self, active_manholes):
        """Update manhole state."""
        self.manhole.update(active_manholes)
    
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

class PowerUpBallObject(ArenaObject):
    """Power-up that creates a duplicate ball on collision."""
    def __init__(self, arena_width, arena_height, scoreboard_height, scale_rect, x, y, size=20):
        """Initialize a power-up ball object with arena properties."""
        super().__init__(arena_width, arena_height, scoreboard_height, scale_rect)
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