import pygame
from sys import exit

class SettingsScreen:
    """A class to handle the settings screen functionality and game settings."""
    
    # Class level variables for window dimensions and player name
    WINDOW_WIDTH = 800  # Default value
    WINDOW_HEIGHT = 600  # Default value
    PLAYER_NAME = "Player"  # Default value
    
    def __init__(self):
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.screen_sizes = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
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
            f.write(f"WINDOW_WIDTH={cls.WINDOW_WIDTH}\n")
            f.write(f"WINDOW_HEIGHT={cls.WINDOW_HEIGHT}\n")
            f.write(f"PLAYER_NAME={cls.PLAYER_NAME}")
    
    def display(self, screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT, in_game=False):
        """Display the settings screen with volume control and screen size options."""
        # Scale font size based on both dimensions
        scale_y = WINDOW_HEIGHT / 600  # Base height scale
        scale_x = WINDOW_WIDTH / 800   # Base width scale
        scale = min(scale_x, scale_y)  # Use the smaller scale to ensure text fits
        
        # Calculate base button dimensions
        button_width = 240  # Width of standard buttons
        
        # Calculate and adjust option font size
        font_size = max(12, int(36 * scale))
        option_font = pygame.font.Font(None, font_size)
        
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
            option_font = pygame.font.Font(None, font_size)
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
            back_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 180, 240, 40)
            change_name_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 120, 240, 40)
            volume_up_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 - 30, 100, 40)
            volume_down_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 30, 100, 40)
            # Calculate proper height for dropdown
            option_height = 35
            total_options = len(self.screen_sizes)
            dropdown_height = total_options * option_height + 10  # Add padding
            size_rect_height = 40 if not dropdown_open else dropdown_height
            size_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 50, 240, size_rect_height)

            for event in pygame.event.get():
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
                                    back_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 180, 240, 40)
                                    volume_up_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 - 30, 100, 40)
                                    volume_down_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 30, 100, 40)
                                    size_rect_height = 40 if not dropdown_open else 120
                                    size_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 50, 240, size_rect_height)
                                    pygame.display.flip()
                                    pygame.time.wait(100)
                                    option_font = pygame.font.Font(None, 36)
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
                        elif change_name_rect.collidepoint(mouse_pos):
                            from Modules.Ping_UI import player_name_screen
                            new_name = player_name_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)
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

            self._draw_screen(screen, dropdown_open, current_size_index, volume,
                            WINDOW_WIDTH, WINDOW_HEIGHT, option_font, volume_up_rect,
                            volume_down_rect, back_rect, size_rect, change_name_rect)

            pygame.display.flip()
            clock.tick(60)

    def _draw_screen(self, screen, dropdown_open, current_size_index, volume,
                    WINDOW_WIDTH, WINDOW_HEIGHT, option_font, volume_up_rect,
                    volume_down_rect, back_rect, size_rect, change_name_rect):
        """Helper method to handle screen drawing logic."""
        screen.fill(self.BLACK)
        mouse_pos = pygame.mouse.get_pos()
        hover_color = (100, 100, 100)
        
        if volume_up_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, volume_up_rect)
        pygame.draw.rect(screen, self.WHITE, volume_up_rect, 2)
        
        if volume_down_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, volume_down_rect)
        pygame.draw.rect(screen, self.WHITE, volume_down_rect, 2)
        
        if back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, back_rect)
        pygame.draw.rect(screen, self.WHITE, size_rect, 2)
        if not dropdown_open:
            pygame.draw.rect(screen, self.WHITE, back_rect, 2)

        title_text = option_font.render("Settings", True, self.WHITE)
        volume_text = option_font.render(f"Volume: {int(volume * 100)}%", True, self.WHITE)
        volume_up_text = option_font.render("+", True, self.WHITE)
        volume_down_text = option_font.render("-", True, self.WHITE)
        back_text = option_font.render("Back", True, self.WHITE)
        size_label = option_font.render("Screen Size:", True, self.WHITE)
        change_name_text = option_font.render("Change Name", True, self.WHITE)

        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))
        screen.blit(volume_text, (WINDOW_WIDTH//2 - volume_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        screen.blit(volume_up_text, (WINDOW_WIDTH//2 + 90, WINDOW_HEIGHT//2 - 20))
        screen.blit(volume_down_text, (WINDOW_WIDTH//2 - 90, WINDOW_HEIGHT//2 - 20))

        # Draw change name button
        if change_name_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, change_name_rect)
        pygame.draw.rect(screen, self.WHITE, change_name_rect, 2)
        screen.blit(change_name_text, (WINDOW_WIDTH//2 - change_name_text.get_width()//2, WINDOW_HEIGHT//2 + 130))

        if not dropdown_open:
            screen.blit(back_text, (WINDOW_WIDTH//2 - back_text.get_width()//2, WINDOW_HEIGHT//2 + 190))
        screen.blit(size_label, (WINDOW_WIDTH//2 - size_label.get_width()//2, WINDOW_HEIGHT//2 + 20))

        if dropdown_open:
            self._draw_dropdown(screen, current_size_index, WINDOW_WIDTH, WINDOW_HEIGHT, option_font, title_text, size_label, size_rect)
        else:
            current_size = self.screen_sizes[current_size_index]
            # Render size and arrow separately for better control
            size_text = option_font.render(f"{current_size[0]}x{current_size[1]}", True, self.WHITE)
            arrow_text = option_font.render("▼", True, self.WHITE)
            
            current_size = self.screen_sizes[current_size_index]
            size_text = option_font.render(f"{current_size[0]}x{current_size[1]} ▼", True, self.WHITE)
            text_x = WINDOW_WIDTH//2 - size_text.get_width()//2
            text_y = WINDOW_HEIGHT//2 + 60
            screen.blit(size_text, (text_x, text_y))

    def _draw_dropdown(self, screen, current_size_index, WINDOW_WIDTH, WINDOW_HEIGHT, option_font, title_text, size_label, size_rect):
        """Helper method to handle dropdown menu drawing."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))
        screen.blit(size_label, (WINDOW_WIDTH//2 - size_label.get_width()//2, WINDOW_HEIGHT//2 + 20))
        pygame.draw.rect(screen, self.WHITE, size_rect, 2)

        # Draw dropdown background to fit all options
        option_height = 35
        total_options = len(self.screen_sizes)
        dropdown_height = (total_options * option_height)  # Remove extra padding
        dropdown_background = pygame.Surface((236, dropdown_height))
        dropdown_background.fill((40, 40, 40))
        dropdown_y = WINDOW_HEIGHT//2 + 52
        screen.blit(dropdown_background, (WINDOW_WIDTH//2 - 118, dropdown_y))
        
        mouse_pos = pygame.mouse.get_pos()
        hover_color = (100, 100, 100)
        
        # Draw each option
        for i, size in enumerate(self.screen_sizes):
            option_y = dropdown_y + (i * option_height) + 5  # Add 5px padding from top
            option_rect = pygame.Rect(WINDOW_WIDTH//2 - 118, option_y, 236, 30)
            
            # Highlight selected option or hovered option
            if i == current_size_index:
                pygame.draw.rect(screen, (80, 80, 80), option_rect)
            elif option_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, hover_color, option_rect)
            
            # Draw option border
            pygame.draw.rect(screen, self.WHITE, option_rect, 1)
            
            # Draw option text
            size_option_text = option_font.render(f"{size[0]}x{size[1]}", True, self.WHITE)
            text_x = WINDOW_WIDTH//2 - size_option_text.get_width()//2
            text_y = option_y + (option_height - size_option_text.get_height())//2
            screen.blit(size_option_text, (text_x, text_y))
        
        # Draw close arrow at the bottom of dropdown
        arrow_y = dropdown_y + dropdown_height + 15  # Increased padding to 15px
        arrow_rect = pygame.Rect(WINDOW_WIDTH//2 - 118, arrow_y, 236, 30)
        
        # Draw arrow background and border
        if arrow_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, arrow_rect)
        pygame.draw.rect(screen, self.WHITE, arrow_rect, 1)
        
        # Draw the arrow text
        arrow_text = option_font.render("^", True, self.WHITE)
        arrow_x = WINDOW_WIDTH//2 - arrow_text.get_width()//2
        arrow_text_y = arrow_y + (30 - arrow_text.get_height())//2  # Center vertically in rect
        screen.blit(arrow_text, (arrow_x, arrow_text_y))