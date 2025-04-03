import pygame
import time
from sys import exit
from .Submodules.Ping_Settings import SettingsScreen
from .Submodules.Ping_Fonts import get_pixel_font

class GameCursor:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.visible = True
        self.is_text_select = False
        
        # Create cursor surfaces
        self.normal_cursor = self._create_cursor((255, 255, 255))
        self.text_cursor = self._create_text_cursor()
    
    def _create_cursor(self, color):
        """Create a basic cursor surface."""
        size = 20
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.line(surface, color, (0, 0), (size-5, size-5), 2)
        pygame.draw.line(surface, color, (0, size-5), (size-5, 0), 2)
        return surface
    
    def _create_text_cursor(self):
        """Create a text selection cursor surface."""
        size = 20
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.line(surface, (255, 255, 255), (size//2, 0), (size//2, size), 2)
        return surface
    
    def update(self, mouse_pos, is_text_select=False):
        """Update cursor position and state."""
        self.x, self.y = mouse_pos
        self.is_text_select = is_text_select
    
    def draw(self, screen):
        """Draw the cursor on screen."""
        if self.visible:
            cursor = self.text_cursor if self.is_text_select else self.normal_cursor
            screen.blit(cursor, (self.x - cursor.get_width()//2,
                               self.y - cursor.get_height()//2))

# Global cursor instance
_game_cursor = None

def get_game_cursor():
    """Get the global cursor instance."""
    global _game_cursor
    if _game_cursor is None:
        _game_cursor = GameCursor()
    return _game_cursor
from .Submodules.Ping_MainMenu import MainMenu
from .Submodules.Ping_Pause import PauseMenu
from .Submodules.Ping_LevelSelect import LevelSelect
from .Submodules.Ping_Fonts import get_pixel_font
from .Submodules.Ping_Button import get_button

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
    """Display the settings screen."""
    settings = SettingsScreen()
    return settings.display(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT, in_game, debug_console)

def player_name_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
    """Display the player name input screen."""
    from .Submodules.Ping_Settings import SettingsScreen
    scale_y = WINDOW_HEIGHT / 600
    scale_x = WINDOW_WIDTH / 800
    scale = min(scale_x, scale_y)
    
    # Calculate input box dimensions
    input_box_width = min(300, WINDOW_WIDTH // 3)
    input_box_height = min(50, WINDOW_HEIGHT // 12)
    input_box = pygame.Rect(WINDOW_WIDTH//2 - input_box_width//2,
                          WINDOW_HEIGHT//2 - input_box_height//2,
                          input_box_width, input_box_height)
    
    # Calculate appropriate font size
    font_size = max(12, int(28 * scale))
    font = get_pixel_font(font_size)
    
    # Test render and adjust size if needed
    test_text = font.render("Enter name", True, pygame.Color('lightskyblue3'))
    while test_text.get_width() > input_box_width - 20 and font_size > 12:
        font_size -= 1
        font = get_pixel_font(font_size)
        test_text = font.render("Enter name", True, pygame.Color('lightskyblue3'))
    
    active = False
    current_name = SettingsScreen.get_player_name()
    text = current_name

    while True:
        events = pygame.event.get()
        
        if debug_console:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == 96:
                    debug_console.update([event])
                    continue
            if debug_console.visible:
                if debug_console.handle_event(event):
                    continue

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click only
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if text:
                            SettingsScreen.update_player_name(text)
                            return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(BLACK)
        
        # Draw prompt text
        prompt_text = font.render("Enter your name:", True, WHITE)
        screen.blit(prompt_text, (WINDOW_WIDTH//2 - prompt_text.get_width()//2, WINDOW_HEIGHT//2 - 100))

        # Draw input box with style
        box_color = pygame.Color('dodgerblue2') if active else pygame.Color('lightskyblue3')
        txt_surface = font.render(text if text else "Enter name", True, box_color)
        width = max(300, txt_surface.get_width()+20)
        input_box.w = width

        if active:
            # Draw glow effect
            glow = pygame.Surface((width + 10, input_box_height + 10), pygame.SRCALPHA)
            glow_color = (30, 144, 255, 100)
            pygame.draw.rect(glow, glow_color, (0, 0, width + 10, input_box_height + 10), border_radius=8)
            screen.blit(glow, (input_box.x - 5, input_box.y - 5))

        # Draw input box
        bg_color = (40, 40, 60) if active else (30, 30, 40)
        pygame.draw.rect(screen, bg_color, input_box, border_radius=8)
        pygame.draw.rect(screen, box_color, input_box, 2, border_radius=8)
        
        # Center text in box
        screen.blit(txt_surface, (input_box.x + (width - txt_surface.get_width())//2,
                                input_box.y + (input_box_height - txt_surface.get_height())//2))

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
    scale_y = WINDOW_HEIGHT / 600
    scale_x = WINDOW_WIDTH / 800
    scale = min(scale_x, scale_y)
    
    # Calculate button dimensions
    button_width = min(300, WINDOW_WIDTH // 3)
    button_height = min(50, WINDOW_HEIGHT // 12)
    continue_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                             WINDOW_HEIGHT//2 + 50,
                             button_width, button_height)
    
    # Calculate appropriate font sizes
    title_font_size = max(12, int(48 * scale))
    title_font = get_pixel_font(title_font_size)
    option_font = get_pixel_font(int(24 * scale))
    
    # Test and adjust title font size
    title_text = title_font.render(f"{winner_name} Wins!", True, WHITE)
    while title_text.get_width() > WINDOW_WIDTH - 40 and title_font_size > 12:
        title_font_size -= 1
        title_font = get_pixel_font(title_font_size)
        title_text = title_font.render(f"{winner_name} Wins!", True, WHITE)

    while True:
        events = pygame.event.get()
        
        if debug_console:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == 96:
                    debug_console.update([event])
                    continue
            if debug_console.visible:
                if debug_console.handle_event(event):
                    continue

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click only
                if continue_rect.collidepoint(event.pos):
                    return "title"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "title"
        
        screen.fill(BLACK)
        
        # Draw winner text
        winner_text = title_font.render(f"{winner_name} Wins!", True, WHITE)
        screen.blit(winner_text, (WINDOW_WIDTH//2 - winner_text.get_width()//2, WINDOW_HEIGHT//3))
        
        # Get button renderer and draw continue button
        button = get_button()
        button.draw(screen, continue_rect, "Continue", option_font,
                   is_hovered=continue_rect.collidepoint(pygame.mouse.get_pos()))
        
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