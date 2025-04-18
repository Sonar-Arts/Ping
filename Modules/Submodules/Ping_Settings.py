import pygame
from sys import exit
from .Ping_Fonts import get_pixel_font
from .Ping_Button import get_button

class SettingsScreen:
    """A class to handle the settings screen functionality and game settings."""
    
    # Class level variables
    WINDOW_WIDTH = 800  # Default value
    WINDOW_HEIGHT = 600  # Default value
    PLAYER_NAME = "Player"  # Default value
    SHADER_ENABLED = True  # Default value
    RETRO_EFFECTS_ENABLED = True  # Default value
    SCANLINE_INTENSITY = 40  # Default value
    GLOW_INTENSITY = 80  # Default value
    VS_BLINK_SPEED = 5.0  # Default value
    SCORE_GLOW_COLOR = "180,180,255"  # Default value
    MASTER_VOLUME = 100  # Default value
    EFFECTS_VOLUME = 100  # Default value
    MUSIC_VOLUME = 100  # Default value
    SCORE_EFFECT_INTENSITY = 50  # Default value
    WIN_SCORES = 10  # Default value for scores needed to win
    
    @classmethod
    def get_dimensions(cls):
        """Get current window dimensions."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                              if '=' in line and not line.strip().startswith('#'))
                width = int(settings.get('WINDOW_WIDTH', cls.WINDOW_WIDTH))
                height = int(settings.get('WINDOW_HEIGHT', cls.WINDOW_HEIGHT))
                return width, height
        except Exception as e:
            print(f"Error loading dimensions: {e}")
            return cls.WINDOW_WIDTH, cls.WINDOW_HEIGHT

    @classmethod
    def update_dimensions(cls, width, height):
        """Update window dimensions in settings file."""
        try:
            current_settings = {}
            try:
                with open("Game Parameters/settings.txt", "r") as f:
                    current_settings = dict(line.strip().split('=') for line in f
                                         if '=' in line and not line.strip().startswith('#'))
            except:
                pass
            
            current_settings['WINDOW_WIDTH'] = width
            current_settings['WINDOW_HEIGHT'] = height
            
            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating dimensions: {e}")
            return False

    @classmethod
    def get_player_name(cls):
        """Get current player name from settings."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                              if '=' in line and not line.strip().startswith('#'))
                return settings.get('PLAYER_NAME', cls.PLAYER_NAME)
        except Exception as e:
            print(f"Error loading player name: {e}")
            return cls.PLAYER_NAME

    @classmethod
    def update_player_name(cls, name):
        """Update player name in settings file."""
        try:
            current_settings = {}
            try:
                with open("Game Parameters/settings.txt", "r") as f:
                    current_settings = dict(line.strip().split('=') for line in f
                                         if '=' in line and not line.strip().startswith('#'))
            except:
                pass
            
            current_settings['PLAYER_NAME'] = name
            
            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating player name: {e}")
            return False
    @classmethod
    def get_shader_enabled(cls):
        """Get current shader enabled state from settings."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                              if '=' in line and not line.strip().startswith('#'))
                return settings.get('SHADER_ENABLED', 'true').lower() == 'true'
        except Exception as e:
            print(f"Error loading shader setting: {e}")
            return cls.SHADER_ENABLED
            
    @classmethod
    def update_shader_enabled(cls, enabled):
        """Update shader enabled state in settings file."""
        try:
            current_settings = {}
            with open("Game Parameters/settings.txt", "r") as f:
                current_settings = dict(line.strip().split('=') for line in f
                                   if '=' in line and not line.strip().startswith('#'))
            current_settings['SHADER_ENABLED'] = str(enabled).lower()
            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating shader setting: {e}")
            return False

    @classmethod
    def get_win_scores(cls):
        """Get current win scores setting."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                           if '=' in line and not line.strip().startswith('#'))
                return int(settings.get('WIN_SCORES', cls.WIN_SCORES))
        except Exception as e:
            print(f"Error loading win scores: {e}")
            return cls.WIN_SCORES

    @classmethod
    def update_win_scores(cls, scores):
        """Update win scores in settings file."""
        try:
            current_settings = {}
            with open("Game Parameters/settings.txt", "r") as f:
                current_settings = dict(line.strip().split('=') for line in f
                                   if '=' in line and not line.strip().startswith('#'))
            current_settings['WIN_SCORES'] = scores
            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating win scores: {e}")
            return False
    
    def __init__(self):
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.screen_sizes = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
        self.dropdown_item_height = 25  # Height for dropdown menu items
        
        # Initialize settings with defaults
        self.current_size_index = 0
        self.player_name = self.PLAYER_NAME
        self.shader_enabled = self.SHADER_ENABLED
        self.retro_effects_enabled = self.RETRO_EFFECTS_ENABLED
        self.scroll_y = 0  # Initialize scroll position
        self.scanline_intensity = self.SCANLINE_INTENSITY
        self.glow_intensity = self.GLOW_INTENSITY
        self.vs_blink_speed = self.VS_BLINK_SPEED
        self.score_glow_color = self.SCORE_GLOW_COLOR
        self.master_volume = self.MASTER_VOLUME
        self.effects_volume = self.EFFECTS_VOLUME
        self.music_volume = self.MUSIC_VOLUME
        self.score_effect_intensity = self.SCORE_EFFECT_INTENSITY
        
        self._load_settings()
    
    def _create_brick_pattern(self, width, height):
        """Create a brick pattern background surface."""
        surface = pygame.Surface((width, height))
        brick_width = 30  # Smaller bricks
        brick_height = 15
        brick_color = (40, 40, 40)  # Darker gray for bricks
        brick_outline = (70, 70, 70)  # Outline color
        brick_highlight = (50, 50, 50)  # Slightly lighter for top edge

        # Draw brick pattern
        for y in range(0, height, brick_height):
            offset = brick_width // 2 if (y // brick_height) % 2 == 1 else 0
            for x in range(-offset, width + brick_width, brick_width):
                # Main brick rectangle
                brick_rect = pygame.Rect(x, y, brick_width - 1, brick_height - 1)
                # Draw main brick
                pygame.draw.rect(surface, brick_color, brick_rect)
                # Draw outline
                pygame.draw.rect(surface, brick_outline, brick_rect, 1)
                # Draw highlight on top edge
                pygame.draw.line(surface, brick_highlight,
                               (brick_rect.left, brick_rect.top),
                               (brick_rect.right, brick_rect.top))
        return surface

    def _load_settings(self):
        """Load settings from the settings file."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = {}
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=')
                        settings[key] = value
                
                width = int(settings.get('WINDOW_WIDTH', self.WINDOW_WIDTH))
                height = int(settings.get('WINDOW_HEIGHT', self.WINDOW_HEIGHT))
                
                # Find matching resolution index
                for i, (w, h) in enumerate(self.screen_sizes):
                    if w == width and h == height:
                        self.current_size_index = i
                        break
                
                self.player_name = settings.get('PLAYER_NAME', self.PLAYER_NAME)
                self.shader_enabled = settings.get('SHADER_ENABLED', 'true').lower() == 'true'
                self.retro_effects_enabled = settings.get('RETRO_EFFECTS_ENABLED', 'true').lower() == 'true'
                self.scanline_intensity = int(settings.get('SCANLINE_INTENSITY', self.SCANLINE_INTENSITY))
                self.glow_intensity = int(settings.get('GLOW_INTENSITY', self.GLOW_INTENSITY))
                self.vs_blink_speed = float(settings.get('VS_BLINK_SPEED', self.VS_BLINK_SPEED))
                self.score_glow_color = settings.get('SCORE_GLOW_COLOR', self.SCORE_GLOW_COLOR)
                self.master_volume = int(settings.get('MASTER_VOLUME', self.MASTER_VOLUME))
                self.effects_volume = int(settings.get('EFFECTS_VOLUME', self.EFFECTS_VOLUME))
                self.music_volume = int(settings.get('MUSIC_VOLUME', self.MUSIC_VOLUME))
                self.score_effect_intensity = int(settings.get('SCORE_EFFECT_INTENSITY', self.SCORE_EFFECT_INTENSITY))
                
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save current settings to file."""
        try:
            width, height = self.screen_sizes[self.current_size_index]
            settings = {
                'WINDOW_WIDTH': width,
                'WINDOW_HEIGHT': height,
                'PLAYER_NAME': self.player_name,
                'SHADER_ENABLED': str(self.shader_enabled).lower(),
                'RETRO_EFFECTS_ENABLED': str(self.retro_effects_enabled).lower(),
                'SCANLINE_INTENSITY': self.scanline_intensity,
                'GLOW_INTENSITY': self.glow_intensity,
                'VS_BLINK_SPEED': self.vs_blink_speed,
                'SCORE_GLOW_COLOR': self.score_glow_color,
                'MASTER_VOLUME': self.master_volume,
                'EFFECTS_VOLUME': self.effects_volume,
                'MUSIC_VOLUME': self.music_volume,
                'SCORE_EFFECT_INTENSITY': self.score_effect_intensity
            }
            
            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    def display(self, screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT, in_game=False, debug_console=None):
        # Store debug_console reference
        self.debug_console = debug_console
        """Display the settings screen and handle its events."""
        # Get reference to sound_manager from ping_base
        from ping_base import sound_manager
        
        # Apply initial master volume
        sound_manager.set_master_volume(self.master_volume)
        
        while True:
            events = pygame.event.get()
            
            if debug_console:
                # Check for backtick key to toggle console visibility
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == 96:  # backtick key
                        debug_console.update([event])
                        break

                # Handle other events if console is visible
                if debug_console.visible:
                    # Create a copy of events to modify
                    remaining_events = []
                    for event in events:
                        # Skip the backtick event since it's already handled
                        if event.type == pygame.KEYDOWN and event.key == 96:
                            continue
                        # If event is handled by console, don't add it to remaining events
                        if not debug_console.handle_event(event):
                            remaining_events.append(event)
                    events = remaining_events
            
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    
            # Draw settings and handle events
            result = self.draw_settings_screen(screen, events, None, lambda: "title", sound_manager)
            
            # Draw debug console if active
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)
            
            pygame.display.flip()
            clock.tick(60)
            
            # Handle return to title screen
            if result == "title":
                return result
    
    def _check_button_hover(self, rect, mouse_pos):
        """Helper function to check button hover with proper scroll offset and title area adjustment"""
        title_area_height = 60  # Match the title area height used in draw_settings_screen
        
        # Calculate dropdown offset if open and button is below dropdown
        dropdown_offset = 0
        if hasattr(self, 'show_resolutions') and self.show_resolutions:
            res_button_bottom = 20 + 35  # Initial y + button height
            if rect.y > res_button_bottom:
                dropdown_offset = len(self.screen_sizes) * self.dropdown_item_height
        
        # Adjust mouse position for scroll, title area, and dropdown if needed
        adjusted_y = mouse_pos[1] - self.scroll_y - title_area_height + dropdown_offset
        return rect.collidepoint(mouse_pos[0], adjusted_y)

    def draw_settings_screen(self, screen, events, sound_test_fn=None, back_fn=None, sound_manager=None):
        """Draw the settings screen with all options."""
        # Clear screen and reset states
        screen.fill(self.BLACK)
        pygame.event.clear([pygame.MOUSEMOTION])  # Clear lingering mouse events
        
        # Get fonts and button instance
        title_font = get_pixel_font(24)
        font = get_pixel_font(20)
        small_font = get_pixel_font(16)
        button = get_button()
        
        # Calculate positions and layout dimensions
        width, height = screen.get_width(), screen.get_height()
        left_column_x = width // 4  # Left column at 1/4 width
        right_column_x = (width * 3) // 4  # Right column at 3/4 width
        button_width = min(200, width // 4)  # Limit button width
        
        # Create a surface for scrollable content
        total_height = 1600  # Height for scrollable content
        content_surface = pygame.Surface((width, total_height))
        content_surface.fill(self.BLACK)
        
        # Initialize positions
        current_y = 50
        spacing = 50
        title_area_height = 60  # Smaller title area
        
        # Handle scrolling with mouse wheel (but not when over dropdown)
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                # Don't scroll if mouse is over resolution dropdown
                if hasattr(self, 'show_resolutions') and self.show_resolutions:
                    real_y = current_y
                    # Create rectangle for entire dropdown area including button
                    dropdown_area = pygame.Rect(
                        right_column_x - button_width//2,
                        real_y + self.scroll_y + title_area_height,
                        button_width,
                        self.dropdown_item_height * (len(self.screen_sizes) + 1)  # +1 for button
                    )
                    if dropdown_area.collidepoint(mouse_pos):
                        continue
                
                scroll_amount = event.y * 30
                self.scroll_y = min(0, max(-total_height + height, self.scroll_y + scroll_amount))
                # Only print scroll debug if settings debug is enabled
                if hasattr(self, 'debug_console') and self.debug_console and self.debug_console.debug_settings:
                    print(f"[DEBUG] Scrolling: {self.scroll_y}")
        
        # Create title area with brick pattern
        title_area = self._create_brick_pattern(width, title_area_height)
        
        # Draw title in brick area
        title = title_font.render("Settings", True, self.WHITE)
        title_x = width//2 - title.get_width()//2
        title_y = (title_area_height - title.get_height()) // 2
        title_area.blit(title, (title_x, title_y))
        
        # Draw title area at top
        screen.blit(title_area, (0, 0))
        
        # Adjust content surface start position
        current_y = 20  # Reduced spacing since title is now separate
        button = get_button()
        
        # Resolution settings section
        self.resolution_section_height = spacing  # Default height
        res_label = font.render("Resolution:", True, self.WHITE)
        content_surface.blit(res_label, (left_column_x - res_label.get_width()//2, current_y))

        # Current resolution button
        current_res = f"{self.screen_sizes[self.current_size_index][0]}x{self.screen_sizes[self.current_size_index][1]}"
        res_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 35)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self._check_button_hover(res_btn_rect, mouse_pos)
        
        # Draw the resolution button (original style)
        # Draw the main button
        button.draw(content_surface, res_btn_rect, current_res, font, is_hovered=is_hovered)
        
        # Draw a small triangle that points up when open and down when closed
        triangle_size = 6
        triangle_margin = 10
        triangle_x = res_btn_rect.right - triangle_margin - triangle_size
        triangle_y = res_btn_rect.centery - triangle_size // 2
        
        is_open = hasattr(self, 'show_resolutions') and self.show_resolutions
        if is_open:
            # Pointing upward when open
            triangle_points = [
                (triangle_x, triangle_y + triangle_size),
                (triangle_x + triangle_size, triangle_y + triangle_size),
                (triangle_x + triangle_size // 2, triangle_y)
            ]
        else:
            # Pointing downward when closed
            triangle_points = [
                (triangle_x, triangle_y),
                (triangle_x + triangle_size, triangle_y),
                (triangle_x + triangle_size // 2, triangle_y + triangle_size)
            ]
        pygame.draw.polygon(content_surface, self.WHITE, triangle_points)
        
        # Handle resolution dropdown
        if hasattr(self, 'show_resolutions') and self.show_resolutions:
            # Draw resolution options
            dropdown_height = len(self.screen_sizes) * self.dropdown_item_height
            self.resolution_section_height = spacing + dropdown_height
            # Draw dropdown background
            dropdown_bg = pygame.Rect(res_btn_rect.x, res_btn_rect.bottom,
                                res_btn_rect.width, dropdown_height)
            pygame.draw.rect(content_surface, (30, 30, 50), dropdown_bg)
            pygame.draw.rect(content_surface, (80, 80, 100), dropdown_bg, 1)
            
            # Draw options
            for i, (w, h) in enumerate(self.screen_sizes):
                # Calculate option rect with scroll position taken into account
                real_y = res_btn_rect.bottom + i * self.dropdown_item_height
                option_rect = pygame.Rect(res_btn_rect.x, real_y,
                                        res_btn_rect.width, self.dropdown_item_height)
                option_text = f"{w}x{h}"
                
                # Create hover detection rect that accounts for scroll
                hover_rect = pygame.Rect(option_rect)
                hover_rect.y = real_y + self.scroll_y + title_area_height
                is_option_hovered = hover_rect.collidepoint(mouse_pos)
                
                # Draw option background (purplish-red for options only)
                option_inner = pygame.Rect(option_rect.x + 2, option_rect.y + 2,
                                        option_rect.width - 4, option_rect.height - 4)
                bg_color = (80, 40, 60) if is_option_hovered else (60, 30, 50)
                pygame.draw.rect(content_surface, bg_color, option_inner)
                pygame.draw.rect(content_surface, (100, 60, 80), option_inner, 1)
                pygame.draw.rect(content_surface, (100, 100, 140), option_rect, 1)
                
                # Draw option text with smaller font for dropdown items
                small_font = get_pixel_font(16)  # Smaller font for dropdown options
                text_surf = small_font.render(option_text, True, self.WHITE)
                text_rect = text_surf.get_rect()
                text_rect.center = option_inner.center
                content_surface.blit(text_surf, text_rect)

        # Handle resolution selection
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click only
                # Handle resolution button and options
                if self._check_button_hover(res_btn_rect, mouse_pos):
                    # Toggle dropdown
                    if not hasattr(self, 'show_resolutions'):
                        self.show_resolutions = False
                    self.show_resolutions = not self.show_resolutions
                    if hasattr(self, 'debug_console') and self.debug_console and self.debug_console.debug_settings:
                        print("[DEBUG] Resolution dropdown clicked")
                elif hasattr(self, 'show_resolutions') and self.show_resolutions:
                    # Check each option in the dropdown
                    for i, _ in enumerate(self.screen_sizes):
                        real_y = res_btn_rect.bottom + i * self.dropdown_item_height
                        click_rect = pygame.Rect(res_btn_rect.x, real_y + self.scroll_y + title_area_height,
                                              res_btn_rect.width, self.dropdown_item_height)
                        if click_rect.collidepoint(mouse_pos):
                            self.current_size_index = i
                            self.show_resolutions = False
                            width, height = self.screen_sizes[i]
                            if hasattr(self, 'debug_console') and self.debug_console and self.debug_console.debug_settings:
                                print(f"[DEBUG] Selected resolution: {width}x{height}")
                            self.update_dimensions(width, height)
                            pygame.display.set_mode((width, height))
                            self.resolution_section_height = spacing
                            return None  # Prevent other button clicks
                else:
                    self.show_resolutions = False  # Close when clicking outside

        # Add spacing based on resolution dropdown state
        current_y += self.resolution_section_height if hasattr(self, 'resolution_section_height') else spacing

        # Player name
        name_label = font.render("Player Name:", True, self.WHITE)
        content_surface.blit(name_label, (left_column_x - name_label.get_width()//2, current_y))
        name_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        mouse_pos = pygame.mouse.get_pos()
        # Update button position if dropdown is open
        if hasattr(self, 'show_resolutions') and self.show_resolutions:
            name_btn_rect.y += len(self.screen_sizes) * self.dropdown_item_height
        button.draw(content_surface, name_btn_rect, self.player_name, font,
                   is_hovered=self._check_button_hover(name_btn_rect, mouse_pos))
        current_y += spacing

        # Draw section separator
        pygame.draw.line(content_surface, self.WHITE,
                        (width//4, current_y),
                        (width * 3//4, current_y), 1)
        current_y += spacing * 0.5

        # Volume controls section header
        volume_text = font.render("Volume Controls", True, self.WHITE)
        content_surface.blit(volume_text, (width//2 - volume_text.get_width()//2, current_y))
        current_y += spacing * 1.5

        # Add extra spacing after section headers
        current_y += spacing * 0.5

        # Master volume with +/- buttons
        master_label = small_font.render("Master Volume:", True, self.WHITE)
        content_surface.blit(master_label, (left_column_x - master_label.get_width()//2, current_y))
        
        # Create three parts: minus button, display, plus button
        # Calculate button widths and positions
        vol_btn_width = button_width // 4
        display_width = vol_btn_width * 2
        padding = 5  # Add padding between buttons
        
        # Position the buttons with padding
        minus_x = right_column_x - (vol_btn_width + display_width + vol_btn_width + padding * 2) // 2
        display_x = minus_x + vol_btn_width + padding
        plus_x = display_x + display_width + padding
        
        master_vol_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        master_vol_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        master_vol_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        
        # Draw and handle the master volume controls
        mouse_pos = pygame.mouse.get_pos()
        master_minus_hover = self._check_button_hover(master_vol_minus_rect, mouse_pos)
        master_plus_hover = self._check_button_hover(master_vol_plus_rect, mouse_pos)
        
        # Handle volume button clicks
        if any(event.type == pygame.MOUSEBUTTONDOWN for event in events):
            if master_minus_hover and self.master_volume > 0:
                self.master_volume = max(0, self.master_volume - 5)
                if sound_manager:
                    sound_manager.set_master_volume(self.master_volume)
            elif master_plus_hover and self.master_volume < 100:
                self.master_volume = min(100, self.master_volume + 5)
                if sound_manager:
                    sound_manager.set_master_volume(self.master_volume)
        
        button.draw(content_surface, master_vol_minus_rect, "-", font, is_hovered=master_minus_hover)
        button.draw(content_surface, master_vol_display_rect, f"{self.master_volume}%", font, is_hovered=False)
        button.draw(content_surface, master_vol_plus_rect, "+", font, is_hovered=master_plus_hover)
        current_y += spacing

        # Effects volume with +/- buttons
        effects_label = small_font.render("Effects Volume:", True, self.WHITE)
        content_surface.blit(effects_label, (left_column_x - effects_label.get_width()//2, current_y))
        effects_vol_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        effects_vol_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        effects_vol_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        mouse_pos = pygame.mouse.get_pos()
        button.draw(content_surface, effects_vol_minus_rect, "-", font,
                   is_hovered=self._check_button_hover(effects_vol_minus_rect, mouse_pos))
        button.draw(content_surface, effects_vol_display_rect, f"{self.effects_volume}%", font,
                   is_hovered=False)
        button.draw(content_surface, effects_vol_plus_rect, "+", font,
                   is_hovered=self._check_button_hover(effects_vol_plus_rect, mouse_pos))
        current_y += spacing * 0.8

        # Music volume with +/- buttons
        music_label = small_font.render("Music Volume:", True, self.WHITE)
        content_surface.blit(music_label, (left_column_x - music_label.get_width()//2, current_y))
        music_vol_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        music_vol_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        music_vol_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        mouse_pos = pygame.mouse.get_pos()
        button.draw(content_surface, music_vol_minus_rect, "-", font,
                   is_hovered=self._check_button_hover(music_vol_minus_rect, mouse_pos))
        button.draw(content_surface, music_vol_display_rect, f"{self.music_volume}%", font,
                   is_hovered=False)
        button.draw(content_surface, music_vol_plus_rect, "+", font,
                   is_hovered=self._check_button_hover(music_vol_plus_rect, mouse_pos))
        current_y += spacing * 1.2

        # Score effect intensity with +/- buttons
        score_effect_label = small_font.render("Score Effect Intensity:", True, self.WHITE)
        content_surface.blit(score_effect_label, (left_column_x - score_effect_label.get_width()//2, current_y))
        score_effect_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        score_effect_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        score_effect_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        mouse_pos = pygame.mouse.get_pos()
        button.draw(content_surface, score_effect_minus_rect, "-", font,
                   is_hovered=self._check_button_hover(score_effect_minus_rect, mouse_pos))
        button.draw(content_surface, score_effect_display_rect, f"{self.score_effect_intensity}%", font,
                   is_hovered=False)
        button.draw(content_surface, score_effect_plus_rect, "+", font,
                   is_hovered=self._check_button_hover(score_effect_plus_rect, mouse_pos))
        current_y += spacing
        

        # Draw section separator for UI Effects
        pygame.draw.line(content_surface, self.WHITE,
                        (width//4, current_y),
                        (width * 3//4, current_y), 1)
        current_y += spacing * 0.5

        # UI effects settings section header
        effects_text = font.render("Additional UI Effects", True, self.WHITE)
        content_surface.blit(effects_text, (width//2 - effects_text.get_width()//2, current_y))
        current_y += spacing * 1.5

        # Draw preview box right after the section header
        preview_width = min(300, int(width * 0.4))  # Scale preview width with window
        preview_height = 100
        preview_x = width//2 - preview_width // 2
        preview_rect = pygame.Rect(preview_x, current_y, preview_width, preview_height)
        
        # Create preview surface
        preview_surf = pygame.Surface((preview_width + 20, preview_height + 20), pygame.SRCALPHA)
        inner_rect = pygame.Rect(10, 10, preview_width, preview_height)
        
        # Draw preview background
        pygame.draw.rect(preview_surf, (0, 0, 60), inner_rect)
        pygame.draw.rect(preview_surf, self.WHITE, inner_rect, 2)
        
        # Add preview text
        preview_text = font.render("PREVIEW", True, self.WHITE)
        preview_score = font.render("88", True, self.WHITE)
        
        # Draw with current effect settings
        if self.retro_effects_enabled:
            # Draw scanlines on preview surface
            scanline_surface = pygame.Surface((preview_width, preview_height), pygame.SRCALPHA)
            for y in range(0, preview_height, 4):
                alpha = self.scanline_intensity
                pygame.draw.line(scanline_surface, (0, 0, 0, alpha),
                               (0, y), (preview_width, y))
            preview_surf.blit(scanline_surface, (10, 10))
            
            # Draw glow effect in preview
            glow_alpha = int(self.glow_intensity * 2.55)  # Convert percentage to alpha (0-255)
            glow_color = tuple(map(int, self.score_glow_color.split(','))) + (glow_alpha,)
            pygame.draw.rect(preview_surf, glow_color, preview_surf.get_rect(), border_radius=10)
        
        # Draw preview content
        preview_surf.blit(preview_text,
                          (10 + (preview_width - preview_text.get_width()) // 2,
                           30))
        preview_surf.blit(preview_score,
                          (10 + (preview_width - preview_score.get_width()) // 2,
                           70))
        
        content_surface.blit(preview_surf, (preview_x - 10, current_y - 10))
        current_y += preview_height + spacing * 1.5

        # UI effects enabled toggle
        effects_label = small_font.render("Enable Additional UI Effects:", True, self.WHITE)
        content_surface.blit(effects_label, (left_column_x - effects_label.get_width()//2, current_y))
        effects_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)

        # Draw effects toggle button
        mouse_pos = pygame.mouse.get_pos()
        button.draw(content_surface, effects_btn_rect, "On" if self.retro_effects_enabled else "Off", font,
                   is_hovered=self._check_button_hover(effects_btn_rect, mouse_pos))
        current_y += spacing

        # Create rectangles for intensity controls (but only draw them if effects are enabled)
        scanline_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        scanline_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        scanline_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        
        glow_minus_rect = pygame.Rect(minus_x, current_y + spacing * 0.8, vol_btn_width, 30)
        glow_display_rect = pygame.Rect(display_x, current_y + spacing * 0.8, display_width, 30)
        glow_plus_rect = pygame.Rect(plus_x, current_y + spacing * 0.8, vol_btn_width, 30)

        if self.retro_effects_enabled:
            # Scanline intensity with +/- buttons
            scanline_label = small_font.render("Scanline Intensity:", True, self.WHITE)
            content_surface.blit(scanline_label, (left_column_x - scanline_label.get_width()//2, current_y))
            
            # Draw scanline controls
            mouse_pos = pygame.mouse.get_pos()
            button.draw(content_surface, scanline_minus_rect, "-", font,
                       is_hovered=self._check_button_hover(scanline_minus_rect, mouse_pos))
            button.draw(content_surface, scanline_display_rect, f"{self.scanline_intensity}%", font,
                       is_hovered=False)
            button.draw(content_surface, scanline_plus_rect, "+", font,
                       is_hovered=self._check_button_hover(scanline_plus_rect, mouse_pos))
            current_y += spacing * 0.8
            
            # Glow intensity with +/- buttons
            glow_label = small_font.render("Glow Intensity:", True, self.WHITE)
            content_surface.blit(glow_label, (left_column_x - glow_label.get_width()//2, current_y))
            
            # Draw glow controls
            mouse_pos = pygame.mouse.get_pos()
            button.draw(content_surface, glow_minus_rect, "-", font,
                       is_hovered=self._check_button_hover(glow_minus_rect, mouse_pos))
            button.draw(content_surface, glow_display_rect, f"{self.glow_intensity}%", font,
                       is_hovered=False)
            button.draw(content_surface, glow_plus_rect, "+", font,
                       is_hovered=self._check_button_hover(glow_plus_rect, mouse_pos))
            current_y += spacing * 1.2
        
        # Draw glow effect in preview if enabled
        if self.retro_effects_enabled:
            glow_alpha = int(self.glow_intensity * 2.55)  # Convert percentage to alpha (0-255)
            glow_color = tuple(map(int, self.score_glow_color.split(','))) + (glow_alpha,)
            pygame.draw.rect(preview_surf, glow_color, preview_surf.get_rect(), border_radius=10)
        
        # Removed vertical separator line for cleaner UI
        
        # Draw section separator before hints
        pygame.draw.line(content_surface, self.WHITE,
                        (width//4, current_y),
                        (width * 3//4, current_y), 1)
        current_y += spacing * 0.5
        
        # Draw control hints
        hint_color = (180, 180, 180)  # Slightly dimmer white
        controls = [
            "Controls:",
            "R - Toggle Retro Effects",
            "← → - Adjust Scanline Intensity",
            "Shift + ← → - Adjust Glow Intensity",
            "Ctrl + ← → - Adjust Master Volume",
            "Alt + ← → - Adjust Effects Volume",
            "M/Shift+M - Decrease/Increase Music Volume",
            "Ctrl+Shift + ← → - Adjust Score Effect",
            "Mouse Wheel - Scroll Settings"
        ]
        
        # Create hints surface
        hints_y = current_y
        hints_height = len(controls) * spacing * 0.7 + spacing * 0.8
        hints_surface = pygame.Surface((width, hints_height), pygame.SRCALPHA)
        
        hint_y = 0
        for hint in controls:
            hint_text = small_font.render(hint, True, hint_color)
            hints_surface.blit(hint_text, (width//2 - hint_text.get_width()//2, hint_y))
            hint_y += spacing * 0.7
        
        content_surface.blit(hints_surface, (0, hints_y))
        current_y = hints_y + hints_height + spacing * 0.8
        
        # Draw scrollable content first
        # Draw scrollable content with offset for title area
        visible_rect = pygame.Rect(0, -self.scroll_y, width, height - title_area_height)
        screen.blit(content_surface, (0, title_area_height), visible_rect)
        
        # Reset scroll when content is shorter than window
        if total_height <= height:
            self.scroll_y = 0

        # Create brick pattern background for button area
        button_area_height = 80  # Reduced height of brick area
        button_area_surface = pygame.Surface((width, button_area_height))
        brick_width = 30  # Smaller bricks
        brick_height = 15
        brick_color = (40, 40, 40)  # Darker gray for bricks
        brick_outline = (70, 70, 70)  # Outline color
        brick_highlight = (50, 50, 50)  # Slightly lighter for top edge

        # Draw brick pattern
        for y in range(0, button_area_height, brick_height):
            offset = brick_width // 2 if (y // brick_height) % 2 == 1 else 0
            for x in range(-offset, width + brick_width, brick_width):
                # Main brick rectangle
                brick_rect = pygame.Rect(x, y, brick_width - 1, brick_height - 1)
                # Draw main brick
                pygame.draw.rect(button_area_surface, brick_color, brick_rect)
                # Draw outline
                pygame.draw.rect(button_area_surface, brick_outline, brick_rect, 1)
                # Draw highlight on top edge
                pygame.draw.line(button_area_surface, brick_highlight,
                               (brick_rect.left, brick_rect.top),
                               (brick_rect.right, brick_rect.top))

        # Draw button area background
        screen.blit(button_area_surface, (0, height - button_area_height))

        # Draw buttons over the brick pattern
        button_y = height - 60  # Moved buttons up slightly to fit smaller area
        button = get_button()
        
        # Create button rectangles
        save_btn_rect = pygame.Rect(width//2 - 150, button_y, 100, 40)
        back_btn_rect = pygame.Rect(width//2 + 50, button_y, 100, 40)
        
        # Draw fixed buttons using Button instance
        mouse_pos = pygame.mouse.get_pos()
        button.draw(screen, save_btn_rect, "Save", font,
                   is_hovered=save_btn_rect.collidepoint(mouse_pos))
        button.draw(screen, back_btn_rect, "Back", font,
                   is_hovered=back_btn_rect.collidepoint(mouse_pos))
        
        # Handle button actions
        # Handle non-resolution button clicks
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Only left click
                mouse_pos = pygame.mouse.get_pos()
                # Skip other button processing if a resolution option was clicked
                if (hasattr(self, 'show_resolutions') and self.show_resolutions and
                    mouse_pos[1] >= res_btn_rect.bottom and
                    mouse_pos[1] <= res_btn_rect.bottom + len(self.screen_sizes) * self.dropdown_item_height):
                    continue

                # Handle buttons below the resolution section
                if hasattr(self, 'show_resolutions') and self.show_resolutions:
                    # Adjust mouse position for dropdown offset
                    mouse_pos = list(mouse_pos)
                    mouse_pos[1] += len(self.screen_sizes) * self.dropdown_item_height

                # Handle player name button
                if self._check_button_hover(name_btn_rect, mouse_pos):
                    from ..Ping_UI import player_name_screen
                    new_name = player_name_screen(screen, pygame.time.Clock(), width, height)
                    if new_name:
                        self.player_name = new_name
                
                # Handle other button clicks with adjusted position
                elif self._check_button_hover(master_vol_minus_rect, mouse_pos):
                    self.master_volume = max(0, self.master_volume - 5)
                elif self._check_button_hover(master_vol_plus_rect, mouse_pos):
                    self.master_volume = min(100, self.master_volume + 5)
                elif self._check_button_hover(effects_vol_minus_rect, mouse_pos):
                    self.effects_volume = max(0, self.effects_volume - 5)
                elif self._check_button_hover(effects_vol_plus_rect, mouse_pos):
                    self.effects_volume = min(100, self.effects_volume + 5)
                elif self._check_button_hover(music_vol_minus_rect, mouse_pos):
                    self.music_volume = max(0, self.music_volume - 5)
                elif self._check_button_hover(music_vol_plus_rect, mouse_pos):
                    self.music_volume = min(100, self.music_volume + 5)
                elif self._check_button_hover(score_effect_minus_rect, mouse_pos):
                    self.score_effect_intensity = max(0, self.score_effect_intensity - 5)
                elif self._check_button_hover(score_effect_plus_rect, mouse_pos):
                    self.score_effect_intensity = min(100, self.score_effect_intensity + 5)
                elif self._check_button_hover(scanline_minus_rect, mouse_pos):
                    self.scanline_intensity = max(0, self.scanline_intensity - 5)
                elif self._check_button_hover(scanline_plus_rect, mouse_pos):
                    self.scanline_intensity = min(100, self.scanline_intensity + 5)
                elif self._check_button_hover(glow_minus_rect, mouse_pos):
                    self.glow_intensity = max(0, self.glow_intensity - 5)
                elif self._check_button_hover(glow_plus_rect, mouse_pos):
                    self.glow_intensity = min(100, self.glow_intensity + 5)
                elif self._check_button_hover(effects_btn_rect, mouse_pos):
                    # Toggle retro effects
                    self.retro_effects_enabled = not self.retro_effects_enabled
                # Fixed buttons at bottom of screen (no scroll adjustment needed)
                elif save_btn_rect.collidepoint(mouse_pos):
                    # Handle save button click
                    if self.save_settings():
                        print("Settings saved successfully")
                        # Check if resolution changed
                        if width != self.screen_sizes[self.current_size_index][0] or \
                           height != self.screen_sizes[self.current_size_index][1]:
                            return "title"  # Return to title to apply new resolution
                    else:
                        print("Error saving settings")
                elif back_btn_rect.collidepoint(mouse_pos) and back_fn:
                    return back_fn()
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and back_fn:
                    return back_fn()
                elif event.key == pygame.K_r:
                    # Toggle retro effects
                    self.retro_effects_enabled = not self.retro_effects_enabled
                elif event.key == pygame.K_LEFT:
                    # Decrease values
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT:
                        self.score_effect_intensity = max(0, self.score_effect_intensity - 5)
                    elif mods & pygame.KMOD_CTRL:
                        self.master_volume = max(0, self.master_volume - 5)
                    elif mods & pygame.KMOD_ALT:
                        self.effects_volume = max(0, self.effects_volume - 5)
                    elif mods & pygame.KMOD_SHIFT:
                        self.glow_intensity = max(0, self.glow_intensity - 5)
                    else:
                        self.scanline_intensity = max(0, self.scanline_intensity - 5)
                elif event.key == pygame.K_RIGHT:
                    # Increase values
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT:
                        self.score_effect_intensity = min(100, self.score_effect_intensity + 5)
                    elif mods & pygame.KMOD_CTRL:
                        self.master_volume = min(100, self.master_volume + 5)
                    elif mods & pygame.KMOD_ALT:
                        self.effects_volume = min(100, self.effects_volume + 5)
                    elif mods & pygame.KMOD_SHIFT:
                        self.glow_intensity = min(100, self.glow_intensity + 5)
                    else:
                        self.scanline_intensity = min(100, self.scanline_intensity + 5)
                elif event.key == pygame.K_m:
                    # Music volume control
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.music_volume = min(100, self.music_volume + 5)
                    else:
                        self.music_volume = max(0, self.music_volume - 5)