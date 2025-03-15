import pygame
from sys import exit

class PauseMenu:
    def __init__(self):
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.HOVER_COLOR = (100, 100, 100)
        
    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
        """Display the pause menu with options to resume, go to title screen, or settings."""
        scale_y = WINDOW_HEIGHT / 600  # Base height scale
        scale_x = WINDOW_WIDTH / 800   # Base width scale
        scale = min(scale_x, scale_y)  # Use the smaller scale to ensure text fits
        
        # Calculate font size based on both dimensions and button size
        button_width = min(300, WINDOW_WIDTH // 3)
        font_size = max(12, int(48 * scale))  # Base size of 48, scaled with window
        option_font = pygame.font.Font(None, font_size)
        
        # Test render the longest text to ensure it fits
        test_text = option_font.render("Back to Title", True, self.WHITE)
        while test_text.get_width() > button_width - 20 and font_size > 12:  # 20px padding
            font_size -= 1
            option_font = pygame.font.Font(None, font_size)
            test_text = option_font.render("Back to Title", True, self.WHITE)
        
        # Create rects for buttons
        button_spacing = int(60 * scale_y)  # Vertical space between buttons
        first_button_y = WINDOW_HEIGHT//2 - button_spacing
        
        resume_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, first_button_y, 300, 50)
        title_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, first_button_y + button_spacing, 300, 50)
        settings_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, first_button_y + 2 * button_spacing, 300, 50)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if resume_rect.collidepoint(mouse_pos):
                        return "resume"
                    elif title_rect.collidepoint(mouse_pos):
                        return "title"
                    elif settings_rect.collidepoint(mouse_pos):
                        return "settings"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "resume"

            screen.fill(self.BLACK)

            mouse_pos = pygame.mouse.get_pos()
            
            # Draw pause title
            pause_text = option_font.render("PAUSED", True, self.WHITE)
            screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, first_button_y - 60))

            # Draw resume button
            if resume_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.HOVER_COLOR, resume_rect)
            pygame.draw.rect(screen, self.WHITE, resume_rect, 2)

            # Draw title button
            if title_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.HOVER_COLOR, title_rect)
            pygame.draw.rect(screen, self.WHITE, title_rect, 2)
            
            # Draw settings button
            if settings_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.HOVER_COLOR, settings_rect)
            pygame.draw.rect(screen, self.WHITE, settings_rect, 2)

            # Render button texts
            resume_text = option_font.render("Resume", True, self.WHITE)
            title_text = option_font.render("Back to Title", True, self.WHITE)
            settings_text = option_font.render("Settings", True, self.WHITE)

            # Position texts in buttons
            button_text_y_offset = 10  # Vertical offset to center text in button
            screen.blit(resume_text, (WINDOW_WIDTH//2 - resume_text.get_width()//2, first_button_y + button_text_y_offset))
            screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, first_button_y + button_spacing + button_text_y_offset))
            screen.blit(settings_text, (WINDOW_WIDTH//2 - settings_text.get_width()//2, first_button_y + 2 * button_spacing + button_text_y_offset))

            pygame.display.flip()
            clock.tick(60)