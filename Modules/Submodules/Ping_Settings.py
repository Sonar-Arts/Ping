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

    @classmethod
    def get_sound_debug_enabled(cls):
        """Get current sound debug enabled state from settings."""
        # Default to False if not found or error occurs
        default_value = False
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                              if '=' in line and not line.strip().startswith('#'))
                # Read as string 'true'/'false' and convert to boolean
                return settings.get('SOUND_DEBUG_ENABLED', str(default_value)).lower() == 'true'
        except Exception as e:
            print(f"Error loading sound debug setting: {e}")
            return default_value

    @classmethod
    def update_sound_debug_enabled(cls, enabled):
        """Update sound debug enabled state in settings file."""
        try:
            current_settings = {}
            try: # Read existing settings first to preserve others
                with open("Game Parameters/settings.txt", "r") as f:
                    current_settings = dict(line.strip().split('=') for line in f
                                         if '=' in line and not line.strip().startswith('#'))
            except FileNotFoundError:
                 print("Settings file not found, creating new one.")
            except Exception as e:
                 print(f"Error reading existing settings: {e}")
                 # Continue anyway, will overwrite if necessary

            current_settings['SOUND_DEBUG_ENABLED'] = str(enabled).lower() # Save as 'true' or 'false'

            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating sound debug setting: {e}")
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

    # Updated signature: removed paddle_sound, score_sound, added sound_manager
    def display(self, screen, clock, sound_manager, WINDOW_WIDTH, WINDOW_HEIGHT, in_game=False, debug_console=None):
        # Store debug_console reference
        self.debug_console = debug_console
        """Display the settings screen and handle its events."""
        # sound_manager is now passed directly as an argument

        # Apply initial volumes (already loaded in __init__ or _load_settings)

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
            # Removed sound_test_fn and updated back_fn logic
            back_target = "back_to_pause" if in_game else "title"
            # Pass sound_manager to draw_settings_screen
            result = self.draw_settings_screen(screen, events, lambda: back_target, sound_manager)

            # Draw debug console if active
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)

            # Handle return action (could be "title" or "back_to_pause")
            if result == "title" or result == "back_to_pause":
                # Return tuple for back_to_pause to include new dimensions
                if result == "back_to_pause":
                    new_width, new_height = self.screen_sizes[self.current_size_index]
                    return (result, new_width, new_height)
                else: # Returning to title screen
                    # Return name change info if applicable
                    if hasattr(self, '_name_changed') and self._name_changed:
                        del self._name_changed # Reset flag
                        # Return dimensions as well if they changed
                        new_width, new_height = self.screen_sizes[self.current_size_index]
                        # Check against original dimensions (assuming WINDOW_WIDTH/HEIGHT hold them)
                        if new_width != WINDOW_WIDTH or new_height != WINDOW_HEIGHT:
                             return ("name_change_and_resize", self.player_name, new_width, new_height)
                        else:
                             return ("name_change", self.player_name)
                    # Return dimensions if changed from title screen
                    elif not in_game:
                        new_width, new_height = self.screen_sizes[self.current_size_index]
                        if new_width != WINDOW_WIDTH or new_height != WINDOW_HEIGHT:
                            return (new_width, new_height)
                        else:
                             # If nothing changed, just return "title"
                             return "title"
                    else: # Should not happen if in_game is true and result is "title"
                        return "title"

    def _check_button_hover(self, rect, mouse_pos):
        """Helper function to check button hover with proper scroll offset and title area adjustment"""
        title_area_height = 60  # Match the title area height used in draw_settings_screen

        # Adjust mouse position for scroll and title area
        adjusted_y = mouse_pos[1] - self.scroll_y - title_area_height
        # Check collision using adjusted y
        return rect.collidepoint(mouse_pos[0], adjusted_y)

    # Updated signature: removed sound_test_fn
    def draw_settings_screen(self, screen, events, back_fn=None, sound_manager=None):
        """Draw the settings screen with all options."""
        # Clear screen and reset states
        screen.fill(self.BLACK)
        # pygame.event.clear([pygame.MOUSEMOTION]) # Clearing events here might miss clicks

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
                    # Calculate the absolute screen rect of the dropdown area
                    # Need the absolute rect of the button first
                    res_btn_rect_abs = pygame.Rect(right_column_x - button_width//2,
                                                   20 + self.scroll_y + title_area_height, # 20 is initial current_y for res button
                                                   button_width, 35)
                    dropdown_area_abs = pygame.Rect(
                        res_btn_rect_abs.x,
                        res_btn_rect_abs.bottom,
                        res_btn_rect_abs.width,
                        self.dropdown_item_height * len(self.screen_sizes)
                    )
                    # Combine button and dropdown area for hover check
                    full_dropdown_area_abs = res_btn_rect_abs.union(dropdown_area_abs)

                    if full_dropdown_area_abs.collidepoint(mouse_pos):
                        continue # Skip scrolling if mouse is over dropdown

                scroll_amount = event.y * 30
                # Adjust max_scroll calculation
                max_scroll = -(total_height - (height - title_area_height - 80)) # Subtract title and button area heights
                self.scroll_y = min(0, max(max_scroll, self.scroll_y + scroll_amount))
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

        # Adjust content surface start position
        current_y = 20  # Reduced spacing since title is now separate
        button = get_button()

        # --- Draw Content onto content_surface ---

        # Resolution settings section
        self.resolution_section_height = spacing  # Default height
        res_label = font.render("Resolution:", True, self.WHITE)
        content_surface.blit(res_label, (left_column_x - res_label.get_width()//2, current_y))

        # Current resolution button
        current_res = f"{self.screen_sizes[self.current_size_index][0]}x{self.screen_sizes[self.current_size_index][1]}"
        res_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 35)
        # Use relative mouse pos for hover check on content surface
        mouse_pos_rel = list(pygame.mouse.get_pos())
        mouse_pos_rel[1] -= (title_area_height + self.scroll_y) # Adjust for title and scroll
        is_hovered = res_btn_rect.collidepoint(mouse_pos_rel)

        # Draw the resolution button
        button.draw(content_surface, res_btn_rect, current_res, font, is_hovered=is_hovered)

        # Draw dropdown triangle
        triangle_size = 6
        triangle_margin = 10
        triangle_x = res_btn_rect.right - triangle_margin - triangle_size
        triangle_y = res_btn_rect.centery - triangle_size // 2
        is_open = hasattr(self, 'show_resolutions') and self.show_resolutions
        if is_open:
            triangle_points = [(triangle_x, triangle_y + triangle_size), (triangle_x + triangle_size, triangle_y + triangle_size), (triangle_x + triangle_size // 2, triangle_y)]
        else:
            triangle_points = [(triangle_x, triangle_y), (triangle_x + triangle_size, triangle_y), (triangle_x + triangle_size // 2, triangle_y + triangle_size)]
        pygame.draw.polygon(content_surface, self.WHITE, triangle_points)

        # Handle resolution dropdown drawing
        if hasattr(self, 'show_resolutions') and self.show_resolutions:
            dropdown_height = len(self.screen_sizes) * self.dropdown_item_height
            self.resolution_section_height = spacing + dropdown_height # Adjust height dynamically
            dropdown_bg = pygame.Rect(res_btn_rect.x, res_btn_rect.bottom, res_btn_rect.width, dropdown_height)
            pygame.draw.rect(content_surface, (30, 30, 50), dropdown_bg)
            pygame.draw.rect(content_surface, (80, 80, 100), dropdown_bg, 1)

            for i, (w, h) in enumerate(self.screen_sizes):
                option_rect = pygame.Rect(res_btn_rect.x, res_btn_rect.bottom + i * self.dropdown_item_height, res_btn_rect.width, self.dropdown_item_height)
                option_text = f"{w}x{h}"
                is_option_hovered = option_rect.collidepoint(mouse_pos_rel) # Use relative mouse pos

                option_inner = pygame.Rect(option_rect.x + 2, option_rect.y + 2, option_rect.width - 4, option_rect.height - 4)
                bg_color = (80, 40, 60) if is_option_hovered else (60, 30, 50)
                pygame.draw.rect(content_surface, bg_color, option_inner)
                pygame.draw.rect(content_surface, (100, 60, 80), option_inner, 1)
                pygame.draw.rect(content_surface, (100, 100, 140), option_rect, 1)

                small_font = get_pixel_font(16)
                text_surf = small_font.render(option_text, True, self.WHITE)
                text_rect = text_surf.get_rect(center=option_inner.center)
                content_surface.blit(text_surf, text_rect)
        else:
             self.resolution_section_height = spacing # Reset height if closed


        # Add spacing based on resolution dropdown state
        current_y += self.resolution_section_height

        # Player name
        name_label = font.render("Player Name:", True, self.WHITE)
        content_surface.blit(name_label, (left_column_x - name_label.get_width()//2, current_y))
        name_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        button.draw(content_surface, name_btn_rect, self.player_name, font,
                   is_hovered=name_btn_rect.collidepoint(mouse_pos_rel)) # Use relative mouse pos
        current_y += spacing

        # Draw section separator
        pygame.draw.line(content_surface, self.WHITE, (width//4, current_y), (width * 3//4, current_y), 1)
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
        vol_btn_width = button_width // 4
        display_width = vol_btn_width * 2
        padding = 5
        minus_x = right_column_x - (vol_btn_width + display_width + vol_btn_width + padding * 2) // 2
        display_x = minus_x + vol_btn_width + padding
        plus_x = display_x + display_width + padding
        master_vol_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        master_vol_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        master_vol_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        master_minus_hover = master_vol_minus_rect.collidepoint(mouse_pos_rel)
        master_plus_hover = master_vol_plus_rect.collidepoint(mouse_pos_rel)
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
        effects_minus_hover = effects_vol_minus_rect.collidepoint(mouse_pos_rel)
        effects_plus_hover = effects_vol_plus_rect.collidepoint(mouse_pos_rel)
        button.draw(content_surface, effects_vol_minus_rect, "-", font, is_hovered=effects_minus_hover)
        button.draw(content_surface, effects_vol_display_rect, f"{self.effects_volume}%", font, is_hovered=False)
        button.draw(content_surface, effects_vol_plus_rect, "+", font, is_hovered=effects_plus_hover)
        current_y += spacing * 0.8

        # Music volume with +/- buttons
        music_label = small_font.render("Music Volume:", True, self.WHITE)
        content_surface.blit(music_label, (left_column_x - music_label.get_width()//2, current_y))
        music_vol_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        music_vol_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        music_vol_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        music_minus_hover = music_vol_minus_rect.collidepoint(mouse_pos_rel)
        music_plus_hover = music_vol_plus_rect.collidepoint(mouse_pos_rel)
        button.draw(content_surface, music_vol_minus_rect, "-", font, is_hovered=music_minus_hover)
        button.draw(content_surface, music_vol_display_rect, f"{self.music_volume}%", font, is_hovered=False)
        button.draw(content_surface, music_vol_plus_rect, "+", font, is_hovered=music_plus_hover)
        current_y += spacing * 1.2

        # Score effect intensity with +/- buttons
        score_effect_label = small_font.render("Score Effect Intensity:", True, self.WHITE)
        content_surface.blit(score_effect_label, (left_column_x - score_effect_label.get_width()//2, current_y))
        score_effect_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        score_effect_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        score_effect_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        score_effect_minus_hover = score_effect_minus_rect.collidepoint(mouse_pos_rel)
        score_effect_plus_hover = score_effect_plus_rect.collidepoint(mouse_pos_rel)
        button.draw(content_surface, score_effect_minus_rect, "-", font, is_hovered=score_effect_minus_hover)
        button.draw(content_surface, score_effect_display_rect, f"{self.score_effect_intensity}%", font, is_hovered=False)
        button.draw(content_surface, score_effect_plus_rect, "+", font, is_hovered=score_effect_plus_hover)
        current_y += spacing

        # Draw section separator for UI Effects
        pygame.draw.line(content_surface, self.WHITE, (width//4, current_y), (width * 3//4, current_y), 1)
        current_y += spacing * 0.5

        # UI effects settings section header
        effects_text = font.render("Additional UI Effects", True, self.WHITE)
        content_surface.blit(effects_text, (width//2 - effects_text.get_width()//2, current_y))
        current_y += spacing * 1.5

        # Draw preview box right after the section header
        preview_width = min(300, int(width * 0.4))
        preview_height = 100
        preview_x = width//2 - preview_width // 2
        preview_rect = pygame.Rect(preview_x, current_y, preview_width, preview_height)
        preview_surf = pygame.Surface((preview_width + 20, preview_height + 20), pygame.SRCALPHA)
        inner_rect = pygame.Rect(10, 10, preview_width, preview_height)
        pygame.draw.rect(preview_surf, (0, 0, 60), inner_rect)
        pygame.draw.rect(preview_surf, self.WHITE, inner_rect, 2)
        preview_text = font.render("PREVIEW", True, self.WHITE)
        preview_score = font.render("88", True, self.WHITE)
        if self.retro_effects_enabled:
            scanline_surface = pygame.Surface((preview_width, preview_height), pygame.SRCALPHA)
            for y in range(0, preview_height, 4):
                alpha = self.scanline_intensity
                pygame.draw.line(scanline_surface, (0, 0, 0, alpha), (0, y), (preview_width, y))
            preview_surf.blit(scanline_surface, (10, 10))
            glow_alpha = int(self.glow_intensity * 2.55)
            glow_color = tuple(map(int, self.score_glow_color.split(','))) + (glow_alpha,)
            pygame.draw.rect(preview_surf, glow_color, preview_surf.get_rect(), border_radius=10)
        preview_surf.blit(preview_text, (10 + (preview_width - preview_text.get_width()) // 2, 30))
        preview_surf.blit(preview_score, (10 + (preview_width - preview_score.get_width()) // 2, 70))
        content_surface.blit(preview_surf, (preview_x - 10, current_y - 10))
        current_y += preview_height + spacing * 1.5

        # UI effects enabled toggle
        effects_label = small_font.render("Enable Additional UI Effects:", True, self.WHITE)
        content_surface.blit(effects_label, (left_column_x - effects_label.get_width()//2, current_y))
        effects_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        button.draw(content_surface, effects_btn_rect, "On" if self.retro_effects_enabled else "Off", font,
                   is_hovered=effects_btn_rect.collidepoint(mouse_pos_rel))
        current_y += spacing

        # Create rectangles for intensity controls
        scanline_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        scanline_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        scanline_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        glow_minus_rect = pygame.Rect(minus_x, current_y + spacing * 0.8, vol_btn_width, 30)
        glow_display_rect = pygame.Rect(display_x, current_y + spacing * 0.8, display_width, 30)
        glow_plus_rect = pygame.Rect(plus_x, current_y + spacing * 0.8, vol_btn_width, 30)

        if self.retro_effects_enabled:
            # Scanline intensity
            scanline_label = small_font.render("Scanline Intensity:", True, self.WHITE)
            content_surface.blit(scanline_label, (left_column_x - scanline_label.get_width()//2, current_y))
            scanline_minus_hover = scanline_minus_rect.collidepoint(mouse_pos_rel)
            scanline_plus_hover = scanline_plus_rect.collidepoint(mouse_pos_rel)
            button.draw(content_surface, scanline_minus_rect, "-", font, is_hovered=scanline_minus_hover)
            button.draw(content_surface, scanline_display_rect, f"{self.scanline_intensity}%", font, is_hovered=False)
            button.draw(content_surface, scanline_plus_rect, "+", font, is_hovered=scanline_plus_hover)
            current_y += spacing * 0.8

            # Glow intensity
            glow_label = small_font.render("Glow Intensity:", True, self.WHITE)
            content_surface.blit(glow_label, (left_column_x - glow_label.get_width()//2, current_y))
            glow_minus_hover = glow_minus_rect.collidepoint(mouse_pos_rel)
            glow_plus_hover = glow_plus_rect.collidepoint(mouse_pos_rel)
            button.draw(content_surface, glow_minus_rect, "-", font, is_hovered=glow_minus_hover)
            button.draw(content_surface, glow_display_rect, f"{self.glow_intensity}%", font, is_hovered=False)
            button.draw(content_surface, glow_plus_rect, "+", font, is_hovered=glow_plus_hover)
            current_y += spacing * 1.2

        # Draw section separator before hints
        pygame.draw.line(content_surface, self.WHITE, (width//4, current_y), (width * 3//4, current_y), 1)
        current_y += spacing * 0.5

        # Draw control hints
        hint_color = (180, 180, 180)
        controls = [
            "Controls:", "R - Toggle Retro Effects", "← → - Adjust Scanline Intensity",
            "Shift + ← → - Adjust Glow Intensity", "Ctrl + ← → - Adjust Master Volume",
            "Alt + ← → - Adjust Effects Volume", "M/Shift+M - Decrease/Increase Music Volume",
            "Ctrl+Shift + ← → - Adjust Score Effect", "Mouse Wheel - Scroll Settings"
        ]
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

        # --- Blit Content onto Screen ---
        # Draw scrollable content with offset for title area
        visible_rect = pygame.Rect(0, -self.scroll_y, width, height - title_area_height - 80) # Subtract button area height
        screen.blit(content_surface, (0, title_area_height), visible_rect)

        # Draw title area (fixed)
        screen.blit(title_area, (0, 0))

        # Reset scroll when content is shorter than window
        if total_height <= height - title_area_height - 80: # Adjust check for button area
            self.scroll_y = 0

        # --- Draw Fixed Bottom Button Area ---
        button_area_height = 80
        button_area_surface = self._create_brick_pattern(width, button_area_height)
        screen.blit(button_area_surface, (0, height - button_area_height))

        # Draw buttons over the brick pattern (fixed position)
        button_y = height - 60
        save_btn_rect = pygame.Rect(width//2 - 150, button_y, 100, 40)
        back_btn_rect = pygame.Rect(width//2 + 50, button_y, 100, 40)
        mouse_pos_abs = pygame.mouse.get_pos() # Use absolute mouse pos for fixed buttons
        button.draw(screen, save_btn_rect, "Save", font, is_hovered=save_btn_rect.collidepoint(mouse_pos_abs))
        button.draw(screen, back_btn_rect, "Back", font, is_hovered=back_btn_rect.collidepoint(mouse_pos_abs))

        # --- Handle Events ---
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos_abs = event.pos # Use event position for clicks

                # Check fixed buttons first
                if save_btn_rect.collidepoint(mouse_pos_abs):
                    success = self.save_settings()
                    if success:
                        print("Settings saved successfully")
                        if sound_manager:
                            sound_manager._load_volume_settings() # Reload settings in sound manager
                        # Check if resolution changed
                        current_width, current_height = self.screen_sizes[self.current_size_index]
                        if current_width != width or current_height != height:
                             # Signal resolution change requires going back
                             if back_fn: return back_fn() # Use back_fn to return correctly
                        # No resolution change, continue in settings
                    else:
                        print("Error saving settings")
                    continue # Prevent further click processing

                elif back_btn_rect.collidepoint(mouse_pos_abs) and back_fn:
                    # Before returning, check if name changed
                    # Use the class method to get the currently saved name
                    if self.player_name != SettingsScreen.get_player_name():
                        self._name_changed = True # Set flag
                    return back_fn() # Use the provided back function
                    continue # Prevent further click processing

                # --- Handle clicks on scrollable content ---
                mouse_pos_rel = list(mouse_pos_abs)
                mouse_pos_rel[1] -= (title_area_height + self.scroll_y) # Adjust for title and scroll

                # Check resolution dropdown button/options
                # Need to check dropdown options *before* other buttons if dropdown is open
                dropdown_handled = False
                if hasattr(self, 'show_resolutions') and self.show_resolutions:
                    # Check each option in the dropdown
                    for i, (w, h) in enumerate(self.screen_sizes):
                        option_rect = pygame.Rect(res_btn_rect.x, res_btn_rect.bottom + i * self.dropdown_item_height, res_btn_rect.width, self.dropdown_item_height)
                        if option_rect.collidepoint(mouse_pos_rel):
                            self.current_size_index = i
                            self.show_resolutions = False
                            new_width, new_height = self.screen_sizes[i]
                            if hasattr(self, 'debug_console') and self.debug_console and self.debug_console.debug_settings:
                                print(f"[DEBUG] Selected resolution: {new_width}x{new_height}")
                            # Don't update dimensions/display here, let save/back handle it
                            dropdown_handled = True
                            break
                    # If click was inside dropdown bg but not on an option, just close it
                    dropdown_bg_rect = pygame.Rect(res_btn_rect.x, res_btn_rect.bottom, res_btn_rect.width, len(self.screen_sizes) * self.dropdown_item_height)
                    if not dropdown_handled and dropdown_bg_rect.collidepoint(mouse_pos_rel):
                         self.show_resolutions = False
                         dropdown_handled = True # Prevent other clicks if click was in dropdown bg

                # If dropdown wasn't handled, check other buttons
                if not dropdown_handled:
                    if res_btn_rect.collidepoint(mouse_pos_rel):
                        self.show_resolutions = not getattr(self, 'show_resolutions', False)
                    elif name_btn_rect.collidepoint(mouse_pos_rel):
                        from ..Ping_UI import player_name_screen # Local import
                        # Pass debug console if available
                        new_name = player_name_screen(screen, pygame.time.Clock(), width, height, self.debug_console)
                        if new_name:
                            self.player_name = new_name
                    elif master_vol_minus_rect.collidepoint(mouse_pos_rel):
                        self.master_volume = max(0, self.master_volume - 5)
                        if sound_manager: sound_manager.set_master_volume(self.master_volume)
                    elif master_vol_plus_rect.collidepoint(mouse_pos_rel):
                        self.master_volume = min(100, self.master_volume + 5)
                        if sound_manager: sound_manager.set_master_volume(self.master_volume)
                    elif effects_vol_minus_rect.collidepoint(mouse_pos_rel):
                        self.effects_volume = max(0, self.effects_volume - 5)
                        if sound_manager:
                            sound_manager.set_sfx_volume(self.effects_volume) # Corrected method name
                            sound_manager.play_sfx('paddle') # Play preview
                    elif effects_vol_plus_rect.collidepoint(mouse_pos_rel):
                        self.effects_volume = min(100, self.effects_volume + 5)
                        if sound_manager:
                            sound_manager.set_sfx_volume(self.effects_volume) # Corrected method name
                            sound_manager.play_sfx('paddle') # Play preview
                    elif music_vol_minus_rect.collidepoint(mouse_pos_rel):
                        self.music_volume = max(0, self.music_volume - 5)
                        if sound_manager: sound_manager.set_music_volume(self.music_volume)
                    elif music_vol_plus_rect.collidepoint(mouse_pos_rel):
                        self.music_volume = min(100, self.music_volume + 5)
                        if sound_manager: sound_manager.set_music_volume(self.music_volume)
                    elif score_effect_minus_rect.collidepoint(mouse_pos_rel):
                        self.score_effect_intensity = max(0, self.score_effect_intensity - 5)
                    elif score_effect_plus_rect.collidepoint(mouse_pos_rel):
                        self.score_effect_intensity = min(100, self.score_effect_intensity + 5)
                    elif effects_btn_rect.collidepoint(mouse_pos_rel):
                        self.retro_effects_enabled = not self.retro_effects_enabled
                    # Intensity controls only clickable if effects enabled
                    elif self.retro_effects_enabled:
                        if scanline_minus_rect.collidepoint(mouse_pos_rel):
                            self.scanline_intensity = max(0, self.scanline_intensity - 5)
                        elif scanline_plus_rect.collidepoint(mouse_pos_rel):
                            self.scanline_intensity = min(100, self.scanline_intensity + 5)
                        elif glow_minus_rect.collidepoint(mouse_pos_rel):
                            self.glow_intensity = max(0, self.glow_intensity - 5)
                        elif glow_plus_rect.collidepoint(mouse_pos_rel):
                            self.glow_intensity = min(100, self.glow_intensity + 5)
                    else: # Clicked outside any interactive element
                         self.show_resolutions = False # Close dropdown if open

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and back_fn:
                    # Check for name change before returning via escape
                    if self.player_name != SettingsScreen.get_player_name():
                        self._name_changed = True
                    return back_fn()
                elif event.key == pygame.K_r:
                    self.retro_effects_enabled = not self.retro_effects_enabled
                elif event.key == pygame.K_LEFT:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT: self.score_effect_intensity = max(0, self.score_effect_intensity - 5)
                    elif mods & pygame.KMOD_CTRL:
                        self.master_volume = max(0, self.master_volume - 5)
                        if sound_manager: sound_manager.set_master_volume(self.master_volume)
                    elif mods & pygame.KMOD_ALT:
                        self.effects_volume = max(0, self.effects_volume - 5)
                        if sound_manager:
                            sound_manager.set_sfx_volume(self.effects_volume) # Corrected method name
                            sound_manager.play_sfx('paddle') # Play preview
                    elif mods & pygame.KMOD_SHIFT: self.glow_intensity = max(0, self.glow_intensity - 5)
                    else: self.scanline_intensity = max(0, self.scanline_intensity - 5)
                elif event.key == pygame.K_RIGHT:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT: self.score_effect_intensity = min(100, self.score_effect_intensity + 5)
                    elif mods & pygame.KMOD_CTRL:
                        self.master_volume = min(100, self.master_volume + 5)
                        if sound_manager: sound_manager.set_master_volume(self.master_volume)
                    elif mods & pygame.KMOD_ALT:
                        self.effects_volume = min(100, self.effects_volume + 5)
                        if sound_manager:
                            sound_manager.set_sfx_volume(self.effects_volume) # Corrected method name
                            sound_manager.play_sfx('paddle') # Play preview
                    elif mods & pygame.KMOD_SHIFT: self.glow_intensity = min(100, self.glow_intensity + 5)
                    else: self.scanline_intensity = min(100, self.scanline_intensity + 5)
                elif event.key == pygame.K_m:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.music_volume = min(100, self.music_volume + 5)
                        if sound_manager: sound_manager.set_music_volume(self.music_volume)
                    else:
                        self.music_volume = max(0, self.music_volume - 5)
                        if sound_manager: sound_manager.set_music_volume(self.music_volume)

        return None # Continue showing settings screen