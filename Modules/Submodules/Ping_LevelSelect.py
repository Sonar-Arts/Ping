import pygame
from .Ping_Levels import DebugLevel

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class LevelSelect:
    def __init__(self):
        pass

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
        """Display the level select screen."""
        scale_y = WINDOW_HEIGHT / 600  # Base height scale
        scale_x = WINDOW_WIDTH / 800   # Base width scale
        scale = min(scale_x, scale_y)  # Use the smaller scale to ensure text fits
        
        button_width = min(300, WINDOW_WIDTH // 3)
        
        # Calculate and adjust option font size
        option_font_size = max(12, int(48 * scale))
        option_font = pygame.font.Font(None, option_font_size)
        
        # Test render the longest text to ensure it fits
        test_text = option_font.render("Debug Level", True, WHITE)
        while test_text.get_width() > button_width - 20 and option_font_size > 12:  # 20px padding
            option_font_size -= 1
            option_font = pygame.font.Font(None, option_font_size)
            test_text = option_font.render("Debug Level", True, WHITE)
        
        while True:
            button_height = min(50, WINDOW_HEIGHT // 12)
            button_spacing = button_height + 20
            
            debug_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                 WINDOW_HEIGHT//2 - button_height//2 - button_spacing,
                                 button_width, button_height)
            back_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                WINDOW_HEIGHT//2 - button_height//2 + button_spacing,
                                button_width, button_height)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if debug_rect.collidepoint(mouse_pos):
                        return DebugLevel()
                    elif back_rect.collidepoint(mouse_pos):
                        return "back"

            screen.fill(BLACK)
            
            hover_color = (100, 100, 100)
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw level selection buttons
            if debug_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, hover_color, debug_rect)
            pygame.draw.rect(screen, WHITE, debug_rect, 2)
            
            if back_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, hover_color, back_rect)
            pygame.draw.rect(screen, WHITE, back_rect, 2)
            
            debug_text = option_font.render("Debug Level", True, WHITE)
            back_text = option_font.render("Back", True, WHITE)
            
            screen.blit(debug_text, (debug_rect.centerx - debug_text.get_width()//2, 
                                 debug_rect.centery - debug_text.get_height()//2))
            screen.blit(back_text, (back_rect.centerx - back_text.get_width()//2,
                                back_rect.centery - back_text.get_height()//2))

            pygame.display.flip()
            clock.tick(60)