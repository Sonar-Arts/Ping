import pygame
import time
from sys import exit
from .Submodules.Ping_Settings import SettingsScreen
from .Submodules.Ping_MainMenu import MainMenu
from .Submodules.Ping_Pause import PauseMenu
from .Submodules.Ping_LevelSelect import LevelSelect

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

def settings_screen(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT, in_game=False):
    """Display the settings screen with volume control and screen size options.
    
    Args:
        screen: The pygame display surface
        clock: The pygame clock object
        paddle_sound: Sound effect for paddle hits
        score_sound: Sound effect for scoring
        WINDOW_WIDTH: Current window width
        WINDOW_HEIGHT: Current window height
        in_game (bool): Whether settings is being accessed from within a game.
                       Controls whether back returns to pause menu or previous screen.
    """
    settings = SettingsScreen()
    return settings.display(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT, in_game)

def player_name_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
    """Display the player name input screen."""
    from .Submodules.Ping_Settings import SettingsScreen
    scale_y = WINDOW_HEIGHT / 600  # Base height scale
    scale_x = WINDOW_WIDTH / 800   # Base width scale
    scale = min(scale_x, scale_y)  # Use the smaller scale to ensure text fits
    
    # Calculate input box dimensions
    input_box_width = min(300, WINDOW_WIDTH // 3)
    input_box_height = min(50, WINDOW_HEIGHT // 12)
    input_box = pygame.Rect(WINDOW_WIDTH//2 - input_box_width//2,
                          WINDOW_HEIGHT//2 - input_box_height//2,
                          input_box_width, input_box_height)
    
    # Calculate font size and ensure it fits
    font_size = max(12, int(48 * scale))
    font = pygame.font.Font(None, font_size)
    test_text = font.render("Enter name", True, color_inactive)
    while test_text.get_width() > input_box_width - 20 and font_size > 12:  # 20px padding
        font_size -= 1
        font = pygame.font.Font(None, font_size)
        test_text = font.render("Enter name", True, color_inactive)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    current_name = SettingsScreen.get_player_name()
    text = current_name

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
                        if text:  # Only save if there's a name entered
                            SettingsScreen.update_player_name(text)
                            return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(BLACK)
        txt_surface = font.render(text if text else "Enter name", True, color)
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
    scale_y = WINDOW_HEIGHT / 600  # Base height scale
    scale_x = WINDOW_WIDTH / 800   # Base width scale
    scale = min(scale_x, scale_y)  # Use the smaller scale to ensure text fits
    
    # Calculate button dimensions
    button_width = min(300, WINDOW_WIDTH // 3)
    button_height = min(50, WINDOW_HEIGHT // 12)
    continue_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                              WINDOW_HEIGHT//2 + 50,
                              button_width, button_height)
    
    # Calculate and adjust title font size
    title_font_size = max(12, int(74 * scale))
    title_font = pygame.font.Font(None, title_font_size)
    title_text = title_font.render(f"{winner_name} Wins!", True, WHITE)
    while title_text.get_width() > WINDOW_WIDTH - 40 and title_font_size > 12:  # 40px padding
        title_font_size -= 1
        title_font = pygame.font.Font(None, title_font_size)
        title_text = title_font.render(f"{winner_name} Wins!", True, WHITE)
    
    # Calculate and adjust option font size
    option_font_size = max(12, int(48 * scale))
    option_font = pygame.font.Font(None, option_font_size)
    test_text = option_font.render("Continue", True, WHITE)
    while test_text.get_width() > button_width - 20 and option_font_size > 12:  # 20px padding
        option_font_size -= 1
        option_font = pygame.font.Font(None, option_font_size)
        test_text = option_font.render("Continue", True, WHITE)
    
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

def pause_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
    """Display the pause menu with options to resume, go to title screen, or settings."""
    pause_menu = PauseMenu()
    return pause_menu.display(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)

def level_select_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
    """Display the level selection screen."""
    level_select = LevelSelect()
    return level_select.display(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)