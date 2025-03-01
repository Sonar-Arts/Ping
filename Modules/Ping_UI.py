import pygame
import time
from sys import exit
from .Submodules.Ping_Settings import SettingsScreen
from .Submodules.Ping_MainMenu import MainMenu

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Default window dimensions
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

def init_display(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    """Initialize the display with the given dimensions."""
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Ping")
    return screen

def settings_screen(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT):
    """Display the settings screen with volume control and screen size options."""
    settings = SettingsScreen()
    return settings.display(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT)

def player_name_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
    """Display the player name input screen."""
    scale_y = WINDOW_HEIGHT / 600  # Use standard height of 600 as base
    font_size = max(12, int(48 * scale_y))
    font = pygame.font.Font(None, font_size)
    input_box = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, 300, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(BLACK)
        txt_surface = font.render(text, True, color)
        width = max(300, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

        prompt_text = font.render("Enter your name:", True, WHITE)
        screen.blit(prompt_text, (WINDOW_WIDTH//2 - prompt_text.get_width()//2, WINDOW_HEIGHT//2 - 100))

        pygame.display.flip()
        clock.tick(30)

class TitleScreen:
    def __init__(self):
        self.menu = MainMenu()

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
        """Display the title screen with game options."""
        return self.menu.display(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)

def win_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, winner_name):
    """Display the win screen with the winner's name."""
    scale_y = WINDOW_HEIGHT / 600
    font_size = max(12, int(74 * scale_y))
    title_font = pygame.font.Font(None, font_size)
    option_font = pygame.font.Font(None, max(12, int(48 * scale_y)))
    
    continue_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50, 300, 50)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_rect.collidepoint(event.pos):
                    return "title"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "title"
        
        screen.fill(BLACK)
        
        # Draw winner text
        winner_text = title_font.render(f"{winner_name} Wins!", True, WHITE)
        screen.blit(winner_text, (WINDOW_WIDTH//2 - winner_text.get_width()//2, WINDOW_HEIGHT//3))
        
        # Draw continue button
        hover_color = (100, 100, 100)
        if continue_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, hover_color, continue_rect)
        pygame.draw.rect(screen, WHITE, continue_rect, 2)
        
        continue_text = option_font.render("Continue", True, WHITE)
        screen.blit(continue_text, (WINDOW_WIDTH//2 - continue_text.get_width()//2, WINDOW_HEIGHT//2 + 60))
        
        pygame.display.flip()
        clock.tick(60)

def pause_menu(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
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

        screen.fill(BLACK)

        hover_color = (100, 100, 100)
        mouse_pos = pygame.mouse.get_pos()
        
        if title_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, title_rect)
        pygame.draw.rect(screen, WHITE, title_rect, 2)
        
        if settings_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, settings_rect)
        pygame.draw.rect(screen, WHITE, settings_rect, 2)

        title_text = option_font.render("Back to Title", True, WHITE)
        settings_text = option_font.render("Settings", True, WHITE)

        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//2 - 20))
        screen.blit(settings_text, (WINDOW_WIDTH//2 - settings_text.get_width()//2, WINDOW_HEIGHT//2 + 60))

        pygame.display.flip()
        clock.tick(60)