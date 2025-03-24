import pygame
from Modules.Ping_GameObjects import ObstacleObject, GoalObject, PortalObject, PowerUpBallObject, BallObject
from Modules.Submodules.Ping_Levels import DebugLevel
from Modules.Submodules.Ping_Scoreboard import Scoreboard

class Arena:
    """Represents the game arena where the Ping game takes place."""
    def __init__(self, level=None):
        """Initialize the arena with parameters from a level configuration."""
        # Load level parameters (use DebugLevel as default if none provided)
        level = level if level else DebugLevel()
        params = level.get_parameters()
        
        # Set dimensions
        self.width = params['dimensions']['width']
        self.height = params['dimensions']['height']
        self.scoreboard_height = params['dimensions']['scoreboard_height']
        
        # Get colors from level configuration
        self.colors = params['colors']
        
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
        
        # Initialize obstacle, goals, portals and power-ups
        self.obstacle = self.create_obstacle()
        self.goals = []
        self.portals = []
        self.power_up = None

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
    
    def draw(self, screen, game_objects, font, player_name, score_a, opponent_name, score_b, respawn_timer=None, paused=False):
        """Draw the complete game state."""
        # Fill background
        screen.fill(self.colors['BLACK'])
        
        # Draw center line if not disabled (0 width/height)
        if self.center_line_box_width > 0 and self.center_line_box_height > 0:
            self.draw_center_line(screen)
        
        # Draw portals first
        for portal in self.portals:
            portal.draw(screen, self.colors['PORTAL'])

        # Draw goals behind other objects
        for goal in self.goals:
            goal.draw(screen, self.colors['WHITE'])
        
        # Draw game objects
        for obj in game_objects:
            obj.draw(screen, self.colors['WHITE'])
        
        # Draw obstacle
        self.obstacle.draw(screen, self.colors['WHITE'])
        
        # Draw power-up if active
        if self.power_up:
            self.power_up.draw(screen, self.colors['WHITE'])
        
        # Draw scoreboard
        self.draw_scoreboard(screen, player_name, score_a, opponent_name, score_b, font, respawn_timer)
        
        # Draw pause overlay if paused
        if paused:
            self.draw_pause_overlay(screen, font)