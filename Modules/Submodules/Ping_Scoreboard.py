import pygame

class Scoreboard:
    """Handles the scoreboard display in the Ping game."""
    def __init__(self, height, scale_y, colors):
        """Initialize the scoreboard with given parameters."""
        self.height = height
        self.scale_y = scale_y
        self.WHITE = colors['WHITE']
        self.DARK_BLUE = colors['DARK_BLUE']
        self._debug_shown = False  # Track if debug message has been shown

    def draw(self, screen, player_name, score_a, opponent_name, score_b, font, respawn_timer=None):
        """Draw the scoreboard at the top of the arena."""
        scoreboard_height = int(self.height * self.scale_y)
        scoreboard_rect = pygame.Rect(0, 0, screen.get_width(), scoreboard_height)
        
        # Draw scoreboard background
        pygame.draw.rect(screen, self.DARK_BLUE, scoreboard_rect)
        pygame.draw.rect(screen, self.WHITE, scoreboard_rect, 2)
        
        # Show debug message only once
        if not self._debug_shown:
            print(f"Loading scoreboard with players - {player_name} vs {opponent_name}")
            self._debug_shown = True
            
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