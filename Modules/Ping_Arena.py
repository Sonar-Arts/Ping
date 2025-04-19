import pygame
import random  # Import random for background generation
import math  # Import math for river animation
from Modules.Ping_GameObjects import ObstacleObject, GoalObject, PortalObject, PowerUpBallObject, BallObject, ManHoleObject
from Modules.Submodules.Ping_Levels import DebugLevel, SewerLevel  # Import SewerLevel
from Modules.Submodules.Ping_Scoreboard import Scoreboard

class Arena:
    """Represents the game arena where the Ping game takes place."""
    def __init__(self, level=None):
        """Initialize the arena with parameters from a level configuration."""
        # Load level parameters (use DebugLevel as default if none provided)
        self.level_instance = level if level else DebugLevel()
        params = self.level_instance.get_parameters()
        
        # Set dimensions
        self.width = params['dimensions']['width']
        self.height = params['dimensions']['height']
        self.scoreboard_height = params['dimensions']['scoreboard_height']
        
        # Set up shader handling
        self._shader_warning_shown = False
        self._shader = None
        self._settings = None
        self._shader_instance = None
        try:
            from .Submodules.Ping_Settings import SettingsScreen
            from .Submodules.Ping_Shader import get_shader
            self._settings = SettingsScreen
            self._shader_instance = get_shader()  # Create shader instance once
        except ImportError as e:
            from .Submodules.Ping_DBConsole import get_console
            debug_console = get_console()
            debug_console.log(f"Warning: Shader system unavailable: {e}")
            self._shader_warning_shown = True
        
        # Get colors from level configuration
        self.colors = params['colors']
        
        # Store background details if available
        self.background_details = params.get('background_details', None)
        self.river_animation_offset = 0  # Initialize river animation offset

        # Initialize scoreboard as None
        self.scoreboard = None
        
        # Calculate scaling factors
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Set center line properties
        self.center_line_box_width = params['center_line']['box_width']
        self.center_line_box_height = params['center_line']['box_height']
        self.center_line_box_spacing = params['center_line']['box_spacing']
        
        # Store paddle positions
        self.paddle_positions = params['paddle_positions']
        
        # Initialize obstacle, goals, portals, manholes and power-ups
        self.obstacle = self.create_obstacle()
        self.goals = []
        self.portals = []
        self.manholes = []
        self.power_up = None

        # Create manholes if specified
        if 'manholes' in params:
            manhole_params = params['manholes']
            positions = manhole_params['positions']
            
            # Create the four manholes
            bottom_left = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                    positions['bottom_left']['x'], positions['bottom_left']['y'],
                                    manhole_params['width'], manhole_params['height'], True)
            
            bottom_right = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                     positions['bottom_right']['x'], positions['bottom_right']['y'],
                                     manhole_params['width'], manhole_params['height'], True)
            
            top_left = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                  positions['top_left']['x'], positions['top_left']['y'],
                                  manhole_params['width'], manhole_params['height'], False)
            
            top_right = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                   positions['top_right']['x'], positions['top_right']['y'],
                                   manhole_params['width'], manhole_params['height'], False)
            
            # Add manholes to the list
            self.manholes.extend([bottom_left, bottom_right, top_left, top_right])

        # Create power-up if specified
        if 'power_ups' in params and 'ball_duplicator' in params['power_ups']:
            power_up_config = params['power_ups']['ball_duplicator']
            if power_up_config['active']:
                self.power_up = PowerUpBallObject(
                    self.width,
                    self.height,
                    self.scoreboard_height,
                    self.scale_rect,
                    power_up_config['position']['x'],
                    power_up_config['position']['y'],
                    power_up_config['size']
                )
        
        # Create goals if specified
        if 'goals' in params and params['goals']:
            if params['goals'].get('left'):
                self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=True))
            if params['goals'].get('right'):
                self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=False))
        
        # Create portals if specified
        if 'portals' in params:
            portal_params = params['portals']
            positions = portal_params['positions']
            
            # Create the four portals
            top_left = PortalObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                  positions['top_left']['x'], positions['top_left']['y'],
                                  portal_params['width'], portal_params['height'])
            
            bottom_left = PortalObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                     positions['bottom_left']['x'], positions['bottom_left']['y'],
                                     portal_params['width'], portal_params['height'])
            
            top_right = PortalObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                   positions['top_right']['x'], positions['top_right']['y'],
                                   portal_params['width'], portal_params['height'])
            
            bottom_right = PortalObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                      positions['bottom_right']['x'], positions['bottom_right']['y'],
                                      portal_params['width'], portal_params['height'])
            
            # Link the portals diagonally
            top_left.set_target(bottom_right)
            bottom_right.set_target(top_left)
            bottom_left.set_target(top_right)
            top_right.set_target(bottom_left)
            
            # Add portals to the list
            self.portals.extend([top_left, bottom_left, top_right, bottom_right])
    
    def create_obstacle(self):
        """Create a new obstacle in the arena."""
        return ObstacleObject(
            arena_width=self.width,
            arena_height=self.height,
            scoreboard_height=self.scoreboard_height,
            scale_rect=self.scale_rect
        )
    
    def check_goal_collisions(self, ball):
        """Check for collisions between ball and goals."""
        for goal in self.goals:
            result = goal.handle_collision(ball)
            if result == "left" or result == "right":
                return result
            elif result == "bounce":
                return None
        return None

    def check_portal_collisions(self, ball):
        """Check for collisions between ball and portals."""
        # Update cooldowns for all portals
        for portal in self.portals:
            portal.update_cooldown()
            
        # Check for collisions
        for portal in self.portals:
            if portal.handle_collision(ball):
                return True
        return False

    def update_manholes(self, delta_time=1/60):
        """Update all manhole states."""
        active_manholes = [m for m in self.manholes if m.is_spouting]
        for manhole in self.manholes:
            manhole.update(active_manholes, delta_time)
    
    def check_manhole_collisions(self, ball):
        """Check for collisions between ball and manholes."""
        for manhole in self.manholes:
            if manhole.handle_collision(ball):
                return True
        return False

    def reset_obstacle(self):
        """Create a new obstacle after collision."""
        self.obstacle = self.create_obstacle()
    
    def initialize_scoreboard(self):
        """Initialize the scoreboard after level selection."""
        self.scoreboard = Scoreboard(
            height=self.scoreboard_height,
            scale_y=1.0,  # Will be updated when scaling changes
            colors={
                'WHITE': self.colors['WHITE'],
                'DARK_BLUE': self.colors['DARK_BLUE']
            }
        )
    
    def update_scaling(self, window_width, window_height):
        """Update scaling factors based on window dimensions."""
        self.scale_x = window_width / self.width
        self.scale_y = window_height / self.height
        self.scale = min(self.scale_x, self.scale_y)
        
        # Calculate centering offsets
        self.offset_x = (window_width - (self.width * self.scale)) / 2
        self.offset_y = (window_height - (self.height * self.scale)) / 2
        
        # Update scoreboard scaling if initialized
        if self.scoreboard:
            self.scoreboard.scale_y = self.scale_y
    
    def scale_rect(self, rect):
        """Scale a rectangle according to current scaling factors."""
        return pygame.Rect(
            (rect.x * self.scale) + self.offset_x,
            (rect.y * self.scale) + self.offset_y,
            rect.width * self.scale,
            rect.height * self.scale
        )
    
    def draw_center_line(self, screen):
        """Draw the dashed center line."""
        box_width = self.center_line_box_width * self.scale
        box_height = self.center_line_box_height * self.scale
        box_spacing = self.center_line_box_spacing * self.scale_y
        num_boxes = int(self.height // (self.center_line_box_height + self.center_line_box_spacing))
        
        for i in range(num_boxes):
            box_y = i * (box_height + box_spacing)
            pygame.draw.rect(screen, self.colors['WHITE'], (
                (self.width//2 - 5) * self.scale + self.offset_x,
                box_y * self.scale + self.offset_y,
                box_width,
                box_height
            ))
    
    def draw_scoreboard(self, screen, player_name, score_a, opponent_name, score_b, font, respawn_timer=None):
        """Draw the scoreboard at the top of the arena."""
        if self.scoreboard:
            self.scoreboard.draw(screen, player_name, score_a, opponent_name, score_b, font, respawn_timer)
    
    def get_paddle_positions(self):
        """Get the paddle positions from the loaded level configuration."""
        return self.paddle_positions
    
    def get_ball_position(self, ball_size):
        """Get the initial ball position (centered)."""
        return (
            self.width//2 - ball_size//2,
            self.height//2 - ball_size//2
        )
    
    def draw_pause_overlay(self, screen, font):
        """Draw pause overlay and text."""
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill(self.colors['BLACK'])
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        pause_text = font.render("Paused", True, self.colors['WHITE'])
        screen.blit(pause_text, (
            screen.get_width()//2 - pause_text.get_width()//2,
            screen.get_height()//2 - pause_text.get_height()//2
        ))

    def check_power_up_collision(self, ball, ball_count):
        """Check for collisions between ball and power-up."""
        if self.power_up:
            new_ball = self.power_up.handle_collision(ball)
            if new_ball:
                return BallObject(
                    self.width,
                    self.height,
                    self.scoreboard_height,
                    self.scale_rect,
                    new_ball.size
                )
        return None

    def update_power_up(self, ball_count):
        """Update power-up state and check for respawn."""
        if self.power_up:
            # Pass arena dimensions and obstacles for valid spawn position
            obstacles = [self.obstacle]
            if self.goals:
                obstacles.extend(self.goals)
            if self.portals:
                obstacles.extend(self.portals)
                
            self.power_up.update(
                ball_count,
                self.width,
                self.height,
                self.scoreboard_height,
                obstacles
            )
    
    def _draw_sewer_background(self, surface):
        """Draws the detailed sewer background with bricks, river, cracks, etc."""
        if not self.background_details:
            return  # Only draw if details are provided

        details = self.background_details
        colors = self.colors
        
        brick_w = details['brick_width']
        brick_h = details['brick_height']
        river_width = self.width * details['river_width_ratio']
        river_x_start = (self.width - river_width) / 2
        river_x_end = river_x_start + river_width
        manhole_padding = details['manhole_brick_padding']

        # Pre-calculate scaled values for efficiency
        scaled_brick_w = brick_w * self.scale
        scaled_brick_h = brick_h * self.scale
        scaled_river_x_start = river_x_start * self.scale + self.offset_x
        scaled_river_width = river_width * self.scale
        scaled_river_y_start = self.scoreboard_height * self.scale + self.offset_y
        scaled_river_height = (self.height - self.scoreboard_height) * self.scale
        scaled_manhole_padding = manhole_padding * self.scale

        # --- Draw Brick Pattern --- 
        for y in range(self.scoreboard_height, self.height, brick_h):
            row_offset = (y // brick_h) % 2 * (brick_w // 2)  # Staggered pattern
            for x in range(0, self.width, brick_w):
                brick_rect_logic = pygame.Rect(x - row_offset, y, brick_w, brick_h)
                
                # Skip drawing bricks fully covered by the river
                if brick_rect_logic.right > river_x_start and brick_rect_logic.left < river_x_end:
                    continue

                # Check if near a manhole
                is_near_manhole = False
                manhole_brick_color_dark = colors['MANHOLE_BRICK_DARK']
                manhole_brick_color_light = colors['MANHOLE_BRICK_LIGHT']
                for manhole in self.manholes:
                    manhole_rect_padded = manhole.rect.inflate(manhole_padding * 2, manhole_padding * 2)
                    if brick_rect_logic.colliderect(manhole_rect_padded):
                        is_near_manhole = True
                        break

                # Determine brick color
                if is_near_manhole:
                    brick_color = manhole_brick_color_light if (x // brick_w + y // brick_h) % 2 == 0 else manhole_brick_color_dark
                else:
                    brick_color = colors['BRICK_LIGHT'] if (x // brick_w + y // brick_h) % 2 == 0 else colors['BRICK_DARK']
                
                # Scale and draw the brick
                scaled_brick_rect = self.scale_rect(brick_rect_logic)
                pygame.draw.rect(surface, brick_color, scaled_brick_rect)
                pygame.draw.rect(surface, colors['BRICK_MORTAR'], scaled_brick_rect, 1)  # Mortar outline

                # Add cracks and vegetation (only on normal bricks)
                if not is_near_manhole:
                    if random.random() < details['crack_frequency']:
                        crack_start = (scaled_brick_rect.left + random.randint(2, scaled_brick_rect.width - 3),
                                       scaled_brick_rect.top + random.randint(2, scaled_brick_rect.height - 3))
                        crack_end = (crack_start[0] + random.randint(-5, 5),
                                     crack_start[1] + random.randint(-5, 5))
                        pygame.draw.line(surface, colors['CRACK_COLOR'], crack_start, crack_end, 1)
                    
                    if random.random() < details['vegetation_frequency']:
                        veg_x = scaled_brick_rect.left + random.randint(0, scaled_brick_rect.width - 5)
                        veg_y = scaled_brick_rect.top + random.randint(0, scaled_brick_rect.height - 5)
                        pygame.draw.rect(surface, colors['VEGETATION_COLOR'], (veg_x, veg_y, 5, 5))

        # --- Draw Sewer River --- 
        river_rect = pygame.Rect(scaled_river_x_start, scaled_river_y_start, scaled_river_width, scaled_river_height)
        pygame.draw.rect(surface, colors['RIVER_WATER_DARK'], river_rect)

        # Animate water flow (simple vertical lines)
        num_lines = int(scaled_river_width / 4)  # Density of lines
        line_speed = details['river_animation_speed'] * self.scale
        self.river_animation_offset = (self.river_animation_offset + line_speed) % (scaled_brick_h * 2)  # Loop animation

        for i in range(int(scaled_river_height / scaled_brick_h) + 2):  # Draw enough lines to cover height + offset
            y_base = scaled_river_y_start + (i * scaled_brick_h) - self.river_animation_offset
            
            # Draw darker wave base
            wave_rect_dark = pygame.Rect(scaled_river_x_start, y_base, scaled_river_width, scaled_brick_h * 0.6)
            pygame.draw.rect(surface, colors['RIVER_WATER_LIGHT'], wave_rect_dark)

            # Draw highlight lines
            highlight_y = y_base + scaled_brick_h * 0.2
            if highlight_y > scaled_river_y_start and highlight_y < scaled_river_y_start + scaled_river_height:
                 pygame.draw.line(surface, colors['RIVER_HIGHLIGHT'], 
                                 (scaled_river_x_start, highlight_y), 
                                 (scaled_river_x_start + scaled_river_width, highlight_y), 2)

    def draw(self, screen, game_objects, font, player_name, score_a, opponent_name, score_b, respawn_timer=None, paused=False):
        """Draw the complete game state."""
        # Create intermediate surface for shader processing
        intermediate = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        intermediate.fill(self.colors['BLACK'])  # Default background

        # --- Draw Specific Level Background --- 
        if isinstance(self.level_instance, SewerLevel):
            self._draw_sewer_background(intermediate)
        else:
            # Draw default background elements like center line for other levels
            if self.center_line_box_width > 0 and self.center_line_box_height > 0:
                self.draw_center_line(intermediate)
        
        # Draw portals first (potentially over background elements)
        for portal in self.portals:
            portal.draw(intermediate, self.colors['PORTAL'])

        # Draw manholes behind other objects
        for manhole in self.manholes:
            manhole.draw(intermediate, self.colors)

        # Draw goals behind other objects
        for goal in self.goals:
            goal.draw(intermediate, self.colors['WHITE'])
        
        # Draw game objects
        for obj in game_objects:
            obj.draw(intermediate, self.colors['WHITE'])
        
        # Draw obstacle
        self.obstacle.draw(intermediate, self.colors['WHITE'])
        
        # Draw power-up if active
        if self.power_up:
            self.power_up.draw(intermediate, self.colors['WHITE'])
        
        # Draw scoreboard
        self.draw_scoreboard(intermediate, player_name, score_a, opponent_name, score_b, font, respawn_timer)
        
        # Draw pause overlay if paused
        if paused:
            self.draw_pause_overlay(intermediate, font)

        # Try to apply shader if enabled and available
        if self._settings and self._shader_instance and self._settings.get_shader_enabled():
            try:
                processed = self._shader_instance.apply_to_surface(intermediate)
                screen.blit(processed, (0, 0))
                return
            except Exception as e:
                if not self._shader_warning_shown:
                    from .Submodules.Ping_DBConsole import get_console
                    debug_console = get_console()
                    debug_console.log(f"Warning: Shader processing failed, using fallback rendering: {e}")
                    self._shader_warning_shown = True

        # Fall back to direct rendering if shader is disabled or failed
        screen.blit(intermediate, (0, 0))