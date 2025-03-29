import pygame
import time
from sys import exit
from .Submodules.Ping_Settings import SettingsScreen
from .Submodules.Ping_MainMenu import MainMenu
from .Submodules.Ping_Pause import PauseMenu
from .Submodules.Ping_LevelSelect import LevelSelect
from .Submodules.Ping_Fonts import get_font_manager
from .Submodules.Ping_Button import get_button  # Add button manager import

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

def settings_screen(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT, in_game=False, debug_console=None):
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
        debug_console: Debug console instance for overlay
    """
    settings = SettingsScreen()
    return settings.display(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT, in_game, debug_console)

def player_name_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
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
    
    # Get font manager and calculate font size
    font_manager = get_font_manager()
    font_size = max(12, int(48 * scale))
    font = font_manager.get_font('text', font_size)
    # Test render with default color
    test_text = font.render("Enter name", True, pygame.Color('lightskyblue3'))
    while test_text.get_width() > input_box_width - 20 and font_size > 12:  # 20px padding
        font_size -= 1
        font = font_manager.get_font('text', font_size)
        test_text = font.render("Enter name", True, pygame.Color('lightskyblue3'))
    active = False
    current_name = SettingsScreen.get_player_name()
    text = current_name

    while True:
        # Get events
        events = pygame.event.get()
        
        # Handle debug console if provided
        if debug_console:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == 96:  # Backtick
                    debug_console.update([event])
                    continue
            if debug_console.visible:
                if debug_console.handle_event(event):
                    continue

        # Process remaining events
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active  # Just toggle active state for visual feedback
                else:
                    active = False
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
        
        # Get button renderer
        button = get_button()

        # Draw prompt text
        prompt_text = font.render("Enter your name:", True, WHITE)
        screen.blit(prompt_text, (WINDOW_WIDTH//2 - prompt_text.get_width()//2, WINDOW_HEIGHT//2 - 100))

        # Adjust input box width based on text
        # Use the box color for text rendering
        box_color = pygame.Color('dodgerblue2') if active else pygame.Color('lightskyblue3')
        txt_surface = font.render(text if text else "Enter name", True, box_color)
        width = max(300, txt_surface.get_width()+20)  # Added more padding
        input_box.w = width

        # Draw input box with custom style
        if active:
            # Draw active input box with glow effect
            glow = pygame.Surface((width + 10, input_box_height + 10), pygame.SRCALPHA)
            glow_color = (30, 144, 255, 100)  # dodgerblue2 RGB values with alpha
            pygame.draw.rect(glow, glow_color, (0, 0, width + 10, input_box_height + 10), border_radius=8)
            screen.blit(glow, (input_box.x - 5, input_box.y - 5))

        # Draw input box background with fixed colors
        box_color = pygame.Color('dodgerblue2') if active else pygame.Color('lightskyblue3')
        bg_color = (40, 40, 60) if active else (30, 30, 40)
        pygame.draw.rect(screen, bg_color, input_box, border_radius=8)
        pygame.draw.rect(screen, box_color, input_box, 2, border_radius=8)
        
        # Draw text centered in box
        screen.blit(txt_surface, (input_box.x + (width - txt_surface.get_width())//2,
                                input_box.y + (input_box_height - txt_surface.get_height())//2))

        # Draw debug console if provided
        if debug_console:
            debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

        pygame.display.flip()
        clock.tick(30)

class TitleScreen:
    def __init__(self):
        self.menu = MainMenu()

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
        """Display the title screen with game options."""
        return self.menu.display(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console)

def win_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, winner_name, debug_console=None):
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
    
    # Get font manager
    font_manager = get_font_manager()
    
    # Calculate and adjust title font size
    title_font_size = max(12, int(74 * scale))
    title_font = font_manager.get_font('title', title_font_size)
    title_text = title_font.render(f"{winner_name} Wins!", True, WHITE)
    while title_text.get_width() > WINDOW_WIDTH - 40 and title_font_size > 12:  # 40px padding
        title_font_size -= 1
        title_font = font_manager.get_font('title', title_font_size)
        title_text = title_font.render(f"{winner_name} Wins!", True, WHITE)
    
    # Calculate and adjust option font size
    option_font_size = max(12, int(48 * scale))
    option_font = font_manager.get_font('menu', option_font_size)
    test_text = option_font.render("Continue", True, WHITE)
    while test_text.get_width() > button_width - 20 and option_font_size > 12:  # 20px padding
        option_font_size -= 1
        option_font = font_manager.get_font('menu', option_font_size)
        test_text = option_font.render("Continue", True, WHITE)
    
    while True:
        # Get events
        events = pygame.event.get()
        
        # Handle debug console if provided
        if debug_console:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == 96:  # Backtick
                    debug_console.update([event])
                    continue
            if debug_console.visible:
                if debug_console.handle_event(event):
                    continue

        # Process remaining events
        for event in events:
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
        
        # Get button renderer
        button = get_button()
        
        # Draw continue button with new style
        button.draw(screen, continue_rect, "Continue", option_font,
                   is_hovered=continue_rect.collidepoint(pygame.mouse.get_pos()))
        
        # Draw debug console if provided
        if debug_console:
            debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)
            
        pygame.display.flip()
        clock.tick(60)

def pause_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
    """Display the pause menu with options to resume, go to title screen, or settings."""
    pause_menu = PauseMenu()
    return pause_menu.display(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console)

def level_select_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
    """Display the level selection screen."""
    level_select = LevelSelect()
    return level_select.display(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console)