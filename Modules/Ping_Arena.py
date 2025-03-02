import pygame
from Modules.Ping_GameObjects import ObstacleObject
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
        
        # Initialize scoreboard
        self.scoreboard = Scoreboard(
            height=self.scoreboard_height,
            scale_y=1.0,  # Will be updated when scaling changes
            colors={
                'WHITE': self.colors['WHITE'],
                'DARK_BROWN': self.colors['DARK_BROWN']
            }
        )
        
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
        
        # Initialize obstacle
        self.obstacle = self.create_obstacle()
    
    def create_obstacle(self):
        """Create a new obstacle in the arena."""
        return ObstacleObject(
            arena_width=self.width,
            arena_height=self.height,
            scoreboard_height=self.scoreboard_height,
            scale_rect=self.scale_rect
        )
    
    def reset_obstacle(self):
        """Create a new obstacle after collision."""
        self.obstacle = self.create_obstacle()
    
    def update_scaling(self, window_width, window_height):
        """Update scaling factors based on window dimensions."""
        self.scale_x = window_width / self.width
        self.scale_y = window_height / self.height
        self.scale = min(self.scale_x, self.scale_y)
        
        # Calculate centering offsets
        self.offset_x = (window_width - (self.width * self.scale)) / 2
        self.offset_y = (window_height - (self.height * self.scale)) / 2
        
        # Update scoreboard scaling
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

    def draw(self, screen, game_objects, font, player_name, score_a, opponent_name, score_b, respawn_timer=None, paused=False):
        """Draw the complete game state."""
        # Fill background
        screen.fill(self.colors['BLACK'])
        
        # Draw center line
        self.draw_center_line(screen)
        
        # Draw game objects
        for obj in game_objects:
            obj.draw(screen, self.colors['WHITE'])
        
        # Draw obstacle
        self.obstacle.draw(screen, self.colors['WHITE'])
        
        # Draw scoreboard
        self.draw_scoreboard(screen, player_name, score_a, opponent_name, score_b, font, respawn_timer)
        
        # Draw pause overlay if paused
        if paused:
            self.draw_pause_overlay(screen, font)