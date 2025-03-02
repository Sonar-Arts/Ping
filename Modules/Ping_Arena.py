import pygame
from Modules.Ping_GameObjects import ObstacleObject

# Default arena dimensions that can be imported
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

class Arena:
    """Represents the game arena where the Ping game takes place."""
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        """Initialize the arena with standard dimensions."""
        self.width = width
        self.height = height
        self.scoreboard_height = 50
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.DARK_BROWN = (101, 67, 33)
        
        # Calculate scaling factors
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Center line properties
        self.center_line_box_width = 5
        self.center_line_box_height = 10
        self.center_line_box_spacing = 10
        
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
        """Get the initial paddle positions relative to arena dimensions."""
        return {
            'left_x': 50,  # Left paddle 50px from left
            'right_x': self.width - 70,  # Right paddle 70px from right
            'y': (self.height - 120) // 2  # Vertically centered (120 is paddle height)
        }
    
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