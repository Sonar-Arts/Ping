import pygame
import time
import random

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def random_color():
    """Generate a random color."""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class MainMenu:
    def __init__(self):
        self.last_color_change = time.time()
        self.title_letters = list("Ping")
        self.title_colors = [WHITE] * len(self.title_letters)

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
        """Display the title screen with game options."""
        scale_y = WINDOW_HEIGHT / 600  # Use standard height of 600 as base
        title_font = pygame.font.Font(None, max(12, int(74 * scale_y)))
        option_font = pygame.font.Font(None, max(12, int(48 * scale_y)))
        
        settings_text = option_font.render("Settings", True, WHITE)
        
        while True:
            button_width = min(300, WINDOW_WIDTH // 3)
            button_height = min(50, WINDOW_HEIGHT // 12)
            button_spacing = button_height + 20
            
            pvp_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                WINDOW_HEIGHT//2 - button_height//2 - button_spacing,
                                button_width, button_height)
            ai_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                               WINDOW_HEIGHT//2 - button_height//2,
                               button_width, button_height)
            settings_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                    WINDOW_HEIGHT//2 - button_height//2 + button_spacing,
                                    button_width, button_height)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if pvp_rect.collidepoint(mouse_pos):
                        return False  # PvP mode
                    elif ai_rect.collidepoint(mouse_pos):
                        return True   # AI mode
                    elif settings_rect.collidepoint(mouse_pos):
                        return "settings"

            screen.fill(BLACK)

            current_time = time.time()
            if current_time - self.last_color_change >= 3:
                self.title_colors = [random_color() for _ in self.title_letters]
                self.last_color_change = current_time

            title_width = sum(title_font.render(letter, True, self.title_colors[i]).get_width() 
                            for i, letter in enumerate(self.title_letters)) + (len(self.title_letters) - 1) * 5
            x_offset = (WINDOW_WIDTH - title_width) // 2
            for i, letter in enumerate(self.title_letters):
                text = title_font.render(letter, True, self.title_colors[i])
                screen.blit(text, (x_offset, WINDOW_HEIGHT//4))
                x_offset += text.get_width() + 5
            
            hover_color = (100, 100, 100)
            mouse_pos = pygame.mouse.get_pos()
            
            if pvp_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, hover_color, pvp_rect)
            pygame.draw.rect(screen, WHITE, pvp_rect, 2)
            
            if ai_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, hover_color, ai_rect)
            pygame.draw.rect(screen, WHITE, ai_rect, 2)
            
            if settings_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, hover_color, settings_rect)
            pygame.draw.rect(screen, WHITE, settings_rect, 2)
            
            pvp_text = option_font.render("Player vs Player", True, WHITE)
            ai_text = option_font.render("Player vs AI", True, WHITE)
            
            screen.blit(pvp_text, (pvp_rect.centerx - pvp_text.get_width()//2, 
                                 pvp_rect.centery - pvp_text.get_height()//2))
            screen.blit(ai_text, (ai_rect.centerx - ai_text.get_width()//2, 
                               ai_rect.centery - ai_text.get_height()//2))
            screen.blit(settings_text, (settings_rect.centerx - settings_text.get_width()//2, 
                                     settings_rect.centery - settings_text.get_height()//2))

            pygame.display.flip()
            clock.tick(60)