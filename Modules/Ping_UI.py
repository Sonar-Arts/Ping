import pygame
import time
import random
from sys import exit
from .Submodules.Ping_Settings import SettingsScreen
from .Submodules.Ping_Fonts import get_pixel_font

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40) # For clouds
LIGHT_GREY = (100, 100, 100) # For city placeholder
YELLOW = (255, 255, 0) # For lightning

# Default window dimensions
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

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

class AnimatedBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clouds = []
        self.lightning_timer = 0
        self.lightning_duration = 0.1 # seconds
        self.lightning_active = False
        self.lightning_pos = (0, 0)
        self.lightning_cooldown = random.uniform(2, 5) # Time between lightning strikes

        # Placeholder for ruined city background (simple gradient or solid color)
        self.city_surface = pygame.Surface((width, height))
        # Simple gradient from dark grey to black
        for y in range(height):
            color_val = int(40 * (1 - y / height))
            pygame.draw.line(self.city_surface, (color_val, color_val, color_val), (0, y), (width, y))
        # Or just a solid color: self.city_surface.fill(LIGHT_GREY)

        # Initialize clouds
        num_clouds = 15
        for _ in range(num_clouds):
            self.add_cloud()

    def add_cloud(self, initial=True):
        cloud_width = random.randint(50, 150)
        cloud_height = random.randint(20, 60)
        # Start clouds off-screen to the right or already on screen if initial
        start_x = self.width + random.randint(50, 200) if not initial else random.randint(-cloud_width, self.width)
        start_y = random.randint(0, int(self.height * 0.6)) # Clouds in upper 60%
        speed = random.uniform(10, 40) # Pixels per second
        self.clouds.append({
            'rect': pygame.Rect(start_x, start_y, cloud_width, cloud_height),
            'speed': speed,
            'color': (random.randint(30, 60), random.randint(30, 60), random.randint(30, 60)) # Darker greys
        })

    def update(self, dt):
        # Move clouds
        for cloud in self.clouds:
            cloud['rect'].x -= cloud['speed'] * dt
            # If cloud moves off-screen left, reset its position to the right
            if cloud['rect'].right < 0:
                cloud['rect'].width = random.randint(50, 150)
                cloud['rect'].height = random.randint(20, 60)
                cloud['rect'].x = self.width + random.randint(50, 200)
                cloud['rect'].y = random.randint(0, int(self.height * 0.6))
                cloud['speed'] = random.uniform(10, 40)

        # Lightning logic
        if self.lightning_active:
            self.lightning_timer -= dt
            if self.lightning_timer <= 0:
                self.lightning_active = False
        else:
            self.lightning_cooldown -= dt
            if self.lightning_cooldown <= 0:
                self.lightning_active = True
                self.lightning_timer = self.lightning_duration
                # Choose a random cloud's position for the lightning origin (approx)
                if self.clouds:
                    strike_cloud = random.choice(self.clouds)
                    self.lightning_pos = (strike_cloud['rect'].centerx, strike_cloud['rect'].bottom)
                else:
                     self.lightning_pos = (random.randint(0, self.width), random.randint(0, int(self.height * 0.6)))
                self.lightning_cooldown = random.uniform(3, 8) # Reset cooldown

    def draw(self, screen):
        # Draw city background
        screen.blit(self.city_surface, (0, 0))

        # Draw clouds
        for cloud in self.clouds:
            pygame.draw.ellipse(screen, cloud['color'], cloud['rect']) # Use ellipse for softer cloud shape

        # Draw lightning flash (simple full screen flash)
        if self.lightning_active:
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Intensity based on remaining time
            intensity = int(200 * (self.lightning_timer / self.lightning_duration))
            flash_surface.fill((255, 255, 200, intensity)) # Yellowish white flash
            screen.blit(flash_surface, (0, 0))
            # Optional: Draw a lightning bolt shape
            # pygame.draw.line(screen, YELLOW, self.lightning_pos, (self.lightning_pos[0] + random.randint(-10, 10), self.height), 3)

from .Submodules.Ping_MainMenu import MainMenu
from .Submodules.Ping_Pause import PauseMenu
from .Submodules.Ping_LevelSelect import LevelSelect
from .Submodules.Ping_Fonts import get_pixel_font
from .Submodules.Ping_Button import get_button

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
    def __init__(self, sound_manager):
        self.menu = MainMenu(sound_manager) # Pass sound_manager to MainMenu
        self.background = None

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
        """Display the title screen with game options."""
        if self.background is None or self.background.width != WINDOW_WIDTH or self.background.height != WINDOW_HEIGHT:
            self.background = AnimatedBackground(WINDOW_WIDTH, WINDOW_HEIGHT)

        last_time = time.time()

        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            events = pygame.event.get()

            if debug_console:
                for event in events:
                     if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKQUOTE:
                         debug_console.toggle_visibility()
                         events.remove(event)
                         break

                if debug_console.visible:
                    processed_by_console = debug_console.update(events)
                    pass

            menu_action = self.menu.handle_input(events, WINDOW_WIDTH, WINDOW_HEIGHT)

            if menu_action == "quit":
                 pygame.quit()
                 exit()
            elif menu_action:
                 return menu_action

            self.background.update(dt)
            self.background.draw(screen)
            self.menu.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            if debug_console and debug_console.visible:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)

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

def pause_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, sound_manager, debug_console=None):
    """Display the pause menu with options to resume, go to title screen, or settings."""
    pause_menu = PauseMenu(sound_manager) # Pass sound_manager
    return pause_menu.display(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console)

def level_select_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, sound_manager, debug_console=None):
    """Display the level selection screen."""
    level_select = LevelSelect(sound_manager) # Pass sound_manager
    return level_select.display(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console)