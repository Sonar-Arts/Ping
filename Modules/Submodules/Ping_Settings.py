import pygame
from sys import exit
import json
from .Ping_Fonts import get_font_manager
from .Ping_Button import get_button

class SettingsScreen:
    """A class to handle the settings screen functionality and game settings."""
    
    # Class level variables
    WINDOW_WIDTH = 800  # Default value
    WINDOW_HEIGHT = 600  # Default value
    PLAYER_NAME = "Player"  # Default value
    SHADER_ENABLED = True  # Default value
    
    def __init__(self):
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.screen_sizes = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
        self.SHADER_ENABLED = True  # Default value matching class variable
        self._load_settings()

    @classmethod
    def _load_settings(cls):
        """Load settings from the settings file."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = {}
                for line in f:
                    key, value = line.strip().split('=')
                    settings[key] = value
                
                # Update class variables with loaded values
                if 'WINDOW_WIDTH' in settings:
                    cls.WINDOW_WIDTH = int(settings['WINDOW_WIDTH'])
                if 'WINDOW_HEIGHT' in settings:
                    cls.WINDOW_HEIGHT = int(settings['WINDOW_HEIGHT'])
                if 'PLAYER_NAME' in settings:
                    cls.PLAYER_NAME = settings['PLAYER_NAME']
                if 'SHADER_ENABLED' in settings:
                    cls.SHADER_ENABLED = settings['SHADER_ENABLED'].lower() == 'true'
        except (FileNotFoundError, ValueError):
            # If file doesn't exist or is invalid, use defaults
            pass

    @classmethod
    def update_dimensions(cls, width, height):
        """Update window dimensions and save to settings file."""
        cls.WINDOW_WIDTH = width
        cls.WINDOW_HEIGHT = height
        cls._save_settings()

    @classmethod
    def get_dimensions(cls):
        """Get current window dimensions."""
        return cls.WINDOW_WIDTH, cls.WINDOW_HEIGHT

    @classmethod
    def update_player_name(cls, name):
        """Update player name and save to settings file."""
        cls.PLAYER_NAME = name
        cls._save_settings()

    @classmethod
    def get_player_name(cls):
        """Get current player name."""
        return cls.PLAYER_NAME

    @classmethod
    def _save_settings(cls):
        """Save all settings to the settings file."""
        with open("Game Parameters/settings.txt", "w") as f:
            settings = [
                f"WINDOW_WIDTH={cls.WINDOW_WIDTH}",
                f"WINDOW_HEIGHT={cls.WINDOW_HEIGHT}",
                f"PLAYER_NAME={cls.PLAYER_NAME}",
                f"SHADER_ENABLED={str(cls.SHADER_ENABLED).lower()}"
            ]
            f.write("\n".join(settings))

    @classmethod
    def get_shader_enabled(cls):
        """Get shader enabled state."""
        return cls.SHADER_ENABLED

    @classmethod
    def update_shader_enabled(cls, enabled):
        """Update shader enabled state and save to settings."""
        cls.SHADER_ENABLED = enabled
        cls._save_settings()
    
    def display(self, screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT, in_game=False, debug_console=None):
        """Display the settings screen with volume control and screen size options."""
        # Scale font size based on both dimensions
        scale_y = WINDOW_HEIGHT / 600  # Base height scale
        scale_x = WINDOW_WIDTH / 800   # Base width scale
        scale = min(scale_x, scale_y)  # Use the smaller scale to ensure text fits
        
        # Calculate base button dimensions
        button_width = 240  # Width of standard buttons
        
        # Get font manager and calculate font size
        font_manager = get_font_manager()
        font_size = max(12, int(36 * scale))
        option_font = font_manager.get_font('menu', font_size)
        
        # Test render the longest possible text to ensure it fits
        test_texts = [
            "Settings",
            f"Volume: 100%",
            "Screen Size:",
            "1920x1080",
            "Change Name",
            "Back"
        ]
        
        # Adjust font size until all text fits within buttons
        while any(option_font.render(text, True, self.WHITE).get_width() > button_width - 20 for text in test_texts) and font_size > 12:
            font_size -= 1
            option_font = font_manager.get_font('menu', font_size)
        volume = paddle_sound.get_volume()  # Get current volume
        screen_size = (WINDOW_WIDTH, WINDOW_HEIGHT)  # Initialize screen_size with current window size
        try:
            current_size_index = self.screen_sizes.index((WINDOW_WIDTH, WINDOW_HEIGHT))
        except ValueError:
            current_size_index = 0
            screen_size = self.screen_sizes[0]
            WINDOW_WIDTH, WINDOW_HEIGHT = screen_size
            screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

        dropdown_open = False

        while True:
            shader_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 120, 240, 40)
            change_name_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 170, 240, 40)
            back_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 220, 240, 40)
            volume_up_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 - 30, 100, 40)
            volume_down_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 30, 100, 40)
            # Calculate proper height for dropdown
            option_height = 35
            total_options = len(self.screen_sizes)
            dropdown_height = total_options * option_height + 10  # Add padding
            size_rect_height = 40 if not dropdown_open else dropdown_height
            size_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 50, 240, size_rect_height)

            events = pygame.event.get()
            
            # Handle debug console if provided
            if debug_console:
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == 96:  # Backtick
                        debug_console.update([event])
                        continue
                    # Move the handle_event check inside the event loop
                    if debug_console.visible:
                        if debug_console.handle_event(event):
                            continue

            # Process remaining events
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEWHEEL:
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if dropdown_open:
                        # Calculate dropdown dimensions for click detection
                        option_height = 35
                        dropdown_y = WINDOW_HEIGHT//2 + 52
                        dropdown_height = (len(self.screen_sizes) * option_height) + 10
                        
                        # Check if click is on the close arrow
                        arrow_y = dropdown_y + dropdown_height + 5
                        arrow_rect = pygame.Rect(WINDOW_WIDTH//2 - 20, arrow_y, 40, 20)
                        
                        if arrow_rect.collidepoint(mouse_pos):
                            dropdown_open = False
                        elif size_rect.collidepoint(mouse_pos):
                            # Ensure click is within valid option area
                            relative_y = mouse_pos[1] - dropdown_y
                            if 0 <= relative_y < dropdown_height:  # Only within actual options area
                                clicked_index = int(relative_y // option_height)
                                if 0 <= clicked_index < len(self.screen_sizes):
                                    option_y = dropdown_y + (clicked_index * option_height) + 5
                                    option_rect = pygame.Rect(WINDOW_WIDTH//2 - 118,
                                                        option_y,
                                                        236, 30)
                                    if option_rect.collidepoint(mouse_pos):
                                        current_size_index = clicked_index
                                        screen_size = self.screen_sizes[current_size_index]
                                        WINDOW_WIDTH, WINDOW_HEIGHT = screen_size
                                        old_surface = screen.copy()
                                    try:
                                        # Set new screen size
                                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
                                        screen.fill(self.BLACK)
                                        scaled_surface = pygame.transform.scale(old_surface, screen_size)
                                        screen.blit(scaled_surface, (0, 0))
                                    except pygame.error as e:
                                        print(f"Failed to create renderer: {e}")
                                        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
                                        screen.fill(self.BLACK)
                                    # Update UI elements positions and sizes
                                    shader_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 120, 240, 40)
                                    change_name_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 170, 240, 40)
                                    back_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 220, 240, 40)
                                    volume_up_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 - 30, 100, 40)
                                    volume_down_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 30, 100, 40)
                                    size_rect_height = 40 if not dropdown_open else 120
                                    size_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 50, 240, size_rect_height)
                                    pygame.display.flip()
                                    pygame.time.wait(100)
                                    option_font = font_manager.get_font('menu', 36)
                                    dropdown_open = False
                        else:
                            dropdown_open = False
                    else:
                        if back_rect.collidepoint(mouse_pos):
                            # Handle back button differently based on context
                            if in_game:
                                # When in game, return special value for pause menu
                                return ("back_to_pause", WINDOW_WIDTH, WINDOW_HEIGHT)
                            else:
                                # Normal back behavior for title screen
                                return (WINDOW_WIDTH, WINDOW_HEIGHT)
                        elif volume_up_rect.collidepoint(mouse_pos):
                            volume = min(volume + 0.1, 1.0)
                            paddle_sound.set_volume(volume)
                            score_sound.set_volume(volume)
                        elif volume_down_rect.collidepoint(mouse_pos):
                            volume = max(volume - 0.1, 0.0)
                            paddle_sound.set_volume(volume)
                            score_sound.set_volume(volume)
                        elif shader_rect.collidepoint(mouse_pos):
                            # Toggle shader state and save
                            self.__class__.SHADER_ENABLED = not self.__class__.SHADER_ENABLED
                            self.SHADER_ENABLED = self.__class__.SHADER_ENABLED
                            self._save_settings()
                        elif change_name_rect.collidepoint(mouse_pos):
                            from Modules.Ping_UI import player_name_screen
                            new_name = player_name_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console)
                            if new_name:
                                self.PLAYER_NAME = new_name
                                self._save_settings()
                                # First update the player name
                                self.update_player_name(new_name)
                                # Then return to the appropriate screen
                                if in_game:
                                    return ("back_to_pause", WINDOW_WIDTH, WINDOW_HEIGHT)
                                else:
                                    # Return current dimensions instead of name change tuple
                                    return (WINDOW_WIDTH, WINDOW_HEIGHT)
                        elif size_rect.collidepoint(mouse_pos):
                            dropdown_open = True

            # Draw screen elements
            self._draw_screen(screen, dropdown_open, current_size_index, volume,
                            WINDOW_WIDTH, WINDOW_HEIGHT, option_font, volume_up_rect,
                            volume_down_rect, back_rect, size_rect, change_name_rect,
                            shader_rect)
            
            # Draw debug console if provided
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)

    def _draw_screen(self, screen, dropdown_open, current_size_index, volume,
                    WINDOW_WIDTH, WINDOW_HEIGHT, option_font, volume_up_rect,
                    volume_down_rect, back_rect, size_rect, change_name_rect,
                    shader_rect):
        """Helper method to handle screen drawing logic."""
        screen.fill(self.BLACK)
        mouse_pos = pygame.mouse.get_pos()
        
        # Get button renderer
        button = get_button()

        # Render text elements
        title_text = option_font.render("Settings", True, self.WHITE)
        volume_text = option_font.render(f"Volume: {int(volume * 100)}%", True, self.WHITE)
        size_label = option_font.render("Screen Size:", True, self.WHITE)

        # Draw stylish buttons
        button.draw(screen, volume_up_rect, "+", option_font,
                   is_hovered=volume_up_rect.collidepoint(mouse_pos))
        button.draw(screen, volume_down_rect, "-", option_font,
                   is_hovered=volume_down_rect.collidepoint(mouse_pos))

        # Draw size selector with custom appearance
        pygame.draw.rect(screen, self.WHITE, size_rect, 2)

        # Draw shader checkbox with class-level state
        button.draw(screen, shader_rect, "Pixel Shader Effect", option_font,
                    is_hovered=shader_rect.collidepoint(mouse_pos),
                    is_checkbox=True, is_checked=self.__class__.SHADER_ENABLED)

        # Draw change name and back buttons
        button.draw(screen, change_name_rect, "Change Name", option_font,
                   is_hovered=change_name_rect.collidepoint(mouse_pos))
        
        if not dropdown_open:
            button.draw(screen, back_rect, "Back", option_font,
                       is_hovered=back_rect.collidepoint(mouse_pos))

        # Draw text elements
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))
        screen.blit(volume_text, (WINDOW_WIDTH//2 - volume_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        screen.blit(size_label, (WINDOW_WIDTH//2 - size_label.get_width()//2, WINDOW_HEIGHT//2 + 20))

        if dropdown_open:
            # Get button renderer once and pass it to _draw_dropdown
            button = get_button()
            self._draw_dropdown(screen, current_size_index, WINDOW_WIDTH, WINDOW_HEIGHT, option_font, title_text, size_label, size_rect, button)
        else:
            # Draw current screen size with dropdown arrow
            current_size = self.screen_sizes[current_size_index]
            button.draw(screen, size_rect, f"{current_size[0]}x{current_size[1]} ▼", option_font,
                       is_hovered=size_rect.collidepoint(mouse_pos))

    def _draw_dropdown(self, screen, current_size_index, WINDOW_WIDTH, WINDOW_HEIGHT, option_font, title_text, size_label, size_rect, button):
        """Helper method to handle dropdown menu drawing."""
        # Setup dimensions
        option_height = 35
        total_options = len(self.screen_sizes)
        dropdown_height = (total_options * option_height)
        dropdown_y = WINDOW_HEIGHT//2 + 52

        # Create semi-transparent overlay for the entire screen
        screen_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        screen_overlay.fill((0, 0, 0))
        screen_overlay.set_alpha(128)
        screen.blit(screen_overlay, (0, 0))

        # Create dropdown background with extra space for close button
        dropdown_bg = pygame.Surface((240, dropdown_height + 45))
        dropdown_bg.fill((30, 30, 40))
        screen.blit(dropdown_bg, (WINDOW_WIDTH//2 - 120, dropdown_y))
        
        # Re-draw header texts on top
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))
        screen.blit(size_label, (WINDOW_WIDTH//2 - size_label.get_width()//2, WINDOW_HEIGHT//2 + 20))
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Draw each option
        for i, size in enumerate(self.screen_sizes):
            option_y = dropdown_y + (i * option_height) + 5  # Add 5px padding from top
            option_rect = pygame.Rect(WINDOW_WIDTH//2 - 118, option_y, 236, 30)
            
            # Draw option button with appropriate state
            button.draw(screen, option_rect, f"{size[0]}x{size[1]}", option_font,
                       is_hovered=option_rect.collidepoint(mouse_pos) or i == current_size_index)
        
        # Draw close arrow button at the bottom of dropdown
        arrow_y = dropdown_y + dropdown_height + 15  # Increased padding to 15px
        arrow_rect = pygame.Rect(WINDOW_WIDTH//2 - 118, arrow_y, 236, 30)
        button.draw(screen, arrow_rect, "^", option_font,
                   is_hovered=arrow_rect.collidepoint(mouse_pos))