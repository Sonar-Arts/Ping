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
    
    def __init__(self):
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.screen_sizes = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
        
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
        """Display the settings screen and handle its events."""
        # Get reference to sound_manager from ping_base
        from ping_base import sound_manager
        
        # Apply initial master volume
        sound_manager.set_master_volume(self.master_volume)
        
        while True:
            events = pygame.event.get()
            
            if debug_console:
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == 96:  # backtick key
                        debug_console.update([event])
                        continue
                if debug_console.visible:
                    if debug_console.handle_event(event):
                        continue
            
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
        """Helper function to check button hover with proper scroll offset"""
        return rect.collidepoint(mouse_pos[0], mouse_pos[1] - self.scroll_y)

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
        total_height = 950  # Approximate total height of content
        content_surface = pygame.Surface((width, total_height))
        content_surface.fill(self.BLACK)
        
        # Handle scrolling with mouse wheel and clear any queued mouse motion events
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                scroll_amount = event.y * 30
                self.scroll_y = min(0, max(-total_height + height, self.scroll_y + scroll_amount))
        
        current_y = 50
        spacing = 50
        
        # Center title with underline
        title = title_font.render("Settings", True, self.WHITE)
        title_x = width//2 - title.get_width()//2
        content_surface.blit(title, (title_x, current_y))
        
        # Draw underline
        pygame.draw.line(content_surface, self.WHITE,
                        (title_x, current_y + title.get_height() + 5),
                        (title_x + title.get_width(), current_y + title.get_height() + 5), 2)
        current_y += spacing * 2.5

        button = get_button()
        
        # Resolution settings
        current_res = f"{self.screen_sizes[self.current_size_index][0]}x{self.screen_sizes[self.current_size_index][1]}"
        res_label = font.render("Resolution:", True, self.WHITE)
        content_surface.blit(res_label, (left_column_x - res_label.get_width()//2, current_y))
        res_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        mouse_pos = pygame.mouse.get_pos()
        button.draw(content_surface, res_btn_rect, current_res, font,
                    is_hovered=self._check_button_hover(res_btn_rect, mouse_pos))
        current_y += spacing

        # Player name
        name_label = font.render("Player Name:", True, self.WHITE)
        content_surface.blit(name_label, (left_column_x - name_label.get_width()//2, current_y))
        name_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        mouse_pos = pygame.mouse.get_pos()
        button.draw(content_surface, name_btn_rect, self.player_name, font,
                     is_hovered=self._check_button_hover(name_btn_rect, mouse_pos))
        current_y += spacing

        # Shader toggle
        shader_label = font.render("Shader Effects:", True, self.WHITE)
        content_surface.blit(shader_label, (left_column_x - shader_label.get_width()//2, current_y))
        shader_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        mouse_pos = pygame.mouse.get_pos()
        button.draw(content_surface, shader_btn_rect, "On" if self.shader_enabled else "Off", font,
                    is_hovered=self._check_button_hover(shader_btn_rect, mouse_pos))
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
        
        # Draw section separator for Retro Effects
        pygame.draw.line(content_surface, self.WHITE,
                        (width//4, current_y),
                        (width * 3//4, current_y), 1)
        current_y += spacing * 0.5

        # Retro effects settings section header
        retro_text = font.render("Retro Effects", True, self.WHITE)
        content_surface.blit(retro_text, (width//2 - retro_text.get_width()//2, current_y))
        current_y += spacing * 1.5
        
        # Retro effects enabled toggle
        effects_label = small_font.render("Enable Effects:", True, self.WHITE)
        content_surface.blit(effects_label, (left_column_x - effects_label.get_width()//2, current_y))
        effects_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        # Draw effects toggle button
        mouse_pos = pygame.mouse.get_pos()
        button.draw(content_surface, effects_btn_rect, "On" if self.retro_effects_enabled else "Off", font,
                   is_hovered=self._check_button_hover(effects_btn_rect, mouse_pos))
        current_y += spacing * 0.8
        
        # Scanline intensity with +/- buttons
        scanline_label = small_font.render("Scanline Intensity:", True, self.WHITE)
        content_surface.blit(scanline_label, (left_column_x - scanline_label.get_width()//2, current_y))
        
        # Scanline intensity controls
        scanline_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        scanline_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        scanline_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
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
        
        # Glow intensity controls
        glow_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        glow_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        glow_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        mouse_pos = pygame.mouse.get_pos()
        button.draw(content_surface, glow_minus_rect, "-", font,
                   is_hovered=self._check_button_hover(glow_minus_rect, mouse_pos))
        button.draw(content_surface, glow_display_rect, f"{self.glow_intensity}%", font,
                   is_hovered=False)
        button.draw(content_surface, glow_plus_rect, "+", font,
                   is_hovered=self._check_button_hover(glow_plus_rect, mouse_pos))
        current_y += spacing * 1.2
        
        # Draw preview box
        preview_width = min(300, int(width * 0.4))  # Scale preview width with window
        preview_height = 100
        preview_x = width//2 - preview_width // 2
        preview_y = current_y
        preview_rect = pygame.Rect(preview_x, preview_y, preview_width, preview_height)
        
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
            
            # Draw glow
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
        
        # Blit preview surface to content surface
        content_surface.blit(preview_surf, (preview_x - 10, preview_y - 10))
        
        current_y = preview_y + preview_height + spacing
        
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
        
        # Draw buttons (fixed at bottom of screen)
        button_y = height - 100
        button = get_button()
        
        # Create button rectangles
        save_btn_rect = pygame.Rect(width//2 - 150, button_y, 100, 40)
        back_btn_rect = pygame.Rect(width//2 + 50, button_y, 100, 40)
        
        # Apply scroll offset and draw the scrollable content
        visible_rect = pygame.Rect(0, -self.scroll_y, width, height)
        screen.blit(content_surface, (0, 0), visible_rect)
        
        # Reset scroll when content is shorter than window
        if total_height <= height:
            self.scroll_y = 0
        
        # Draw fixed buttons using Button instance (no scroll adjustment needed)
        mouse_pos = pygame.mouse.get_pos()
        button.draw(screen, save_btn_rect, "Save", font,
                   is_hovered=save_btn_rect.collidepoint(mouse_pos))
        button.draw(screen, back_btn_rect, "Back", font,
                   is_hovered=back_btn_rect.collidepoint(mouse_pos))
        
        # Handle button actions
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 2, 3):  # Only left, middle, right clicks
                mouse_pos = pygame.mouse.get_pos()
                # Use helper function for button collision checks
                if self._check_button_hover(res_btn_rect, mouse_pos):
                    # Cycle through available resolutions
                    self.current_size_index = (self.current_size_index + 1) % len(self.screen_sizes)
                    # Force reset scroll position when changing resolution
                    self.scroll_y = 0  # Reset scroll position to top
                    # Save and apply new resolution immediately
                    new_width, new_height = self.screen_sizes[self.current_size_index]
                    self.update_dimensions(new_width, new_height)
                    pygame.display.set_mode((new_width, new_height))
                elif self._check_button_hover(name_btn_rect, mouse_pos):
                    # Handle player name change
                    from ..Ping_UI import player_name_screen
                    new_name = player_name_screen(screen, pygame.time.Clock(), width, height)
                    if new_name:
                        self.player_name = new_name
                elif self._check_button_hover(shader_btn_rect, mouse_pos):
                    # Toggle shader effects
                    self.shader_enabled = not self.shader_enabled
                # Handle +/- button clicks for volume controls
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