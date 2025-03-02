import pygame
from Modules.Ping_GameObjects import ObstacleObject
from Modules.Submodules.Ping_Levels import DebugLevel

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
        
        # Set colors
        self.WHITE = params['colors']['WHITE']
        self.BLACK = params['colors']['BLACK']
        self.DARK_BROWN = params['colors']['DARK_BROWN']
        
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
            pygame.draw.rect(screen, self.WHITE, (
                (self.width//2 - 5) * self.scale + self.offset_x,
                box_y * self.scale + self.offset_y,
                box_width,
                box_height
            ))
    
    def draw_scoreboard(self, screen, player_name, score_a, opponent_name, score_b, font, respawn_timer=None):
        """Draw the scoreboard at the top of the arena."""
        scoreboard_height = int(self.scoreboard_height * self.scale_y)
        scoreboard_rect = pygame.Rect(0, 0, screen.get_width(), scoreboard_height)
        
        # Draw scoreboard background
        pygame.draw.rect(screen, self.DARK_BROWN, scoreboard_rect)
        pygame.draw.rect(screen, self.WHITE, scoreboard_rect, 2)
        
        # Draw scores
        score_text = font.render(f"{player_name}: {score_a}  {opponent_name}: {score_b}", True, self.WHITE)
        screen.blit(score_text, (screen.get_width()//2 - score_text.get_width()//2, scoreboard_height//4))

        # Draw respawn timer in center of arena if active
        if respawn_timer is not None and respawn_timer > 0:
            # Create timer box
            timer_width = 80
            timer_height = 40
            timer_rect = pygame.Rect(
                screen.get_width()//2 - timer_width//2,
                screen.get_height()//2 - timer_height//2,
                timer_width,
                timer_height
            )
            # Draw red box with white border
            pygame.draw.rect(screen, (255, 0, 0), timer_rect)
            pygame.draw.rect(screen, self.WHITE, timer_rect, 2)
            
            # Draw timer text in white
            timer_text = font.render(f"{int(respawn_timer)}", True, self.WHITE)
            screen.blit(timer_text, (
                screen.get_width()//2 - timer_text.get_width()//2,
                screen.get_height()//2 - timer_text.get_height()//2
            ))
    
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
        overlay.fill(self.BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        pause_text = font.render("Paused", True, self.WHITE)
        screen.blit(pause_text, (
            screen.get_width()//2 - pause_text.get_width()//2,
            screen.get_height()//2 - pause_text.get_height()//2
        ))

    def draw(self, screen, game_objects, font, player_name, score_a, opponent_name, score_b, respawn_timer=None, paused=False):
        """Draw the complete game state."""
        # Fill background
        screen.fill(self.BLACK)
        
        # Draw center line
        self.draw_center_line(screen)
        
        # Draw game objects
        for obj in game_objects:
            obj.draw(screen, self.WHITE)
        
        # Draw obstacle
        self.obstacle.draw(screen, self.WHITE)
        
        # Draw scoreboard
        self.draw_scoreboard(screen, player_name, score_a, opponent_name, score_b, font, respawn_timer)
        
        # Draw pause overlay if paused
        if paused:
            self.draw_pause_overlay(screen, font)