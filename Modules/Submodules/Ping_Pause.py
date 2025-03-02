import pygame
from sys import exit

class PauseMenu:
    def __init__(self):
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.HOVER_COLOR = (100, 100, 100)
        
    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
        """Display the pause menu with options to resume, go to title screen, or settings."""
        option_font = pygame.font.Font(None, 48)

        title_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, 300, 50)
        settings_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50, 300, 50)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if title_rect.collidepoint(mouse_pos):
                        return "title"
                    elif settings_rect.collidepoint(mouse_pos):
                        return "settings"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None

            screen.fill(self.BLACK)

            mouse_pos = pygame.mouse.get_pos()
            
            if title_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.HOVER_COLOR, title_rect)
            pygame.draw.rect(screen, self.WHITE, title_rect, 2)
            
            if settings_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, self.HOVER_COLOR, settings_rect)
            pygame.draw.rect(screen, self.WHITE, settings_rect, 2)

            title_text = option_font.render("Back to Title", True, self.WHITE)
            settings_text = option_font.render("Settings", True, self.WHITE)

            screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//2 - 20))
            screen.blit(settings_text, (WINDOW_WIDTH//2 - settings_text.get_width()//2, WINDOW_HEIGHT//2 + 60))

            pygame.display.flip()
            clock.tick(60)