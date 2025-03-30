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
        self.scanline_intensity = self.SCANLINE_INTENSITY
        self.glow_intensity = self.GLOW_INTENSITY
        self.vs_blink_speed = self.VS_BLINK_SPEED
        self.score_glow_color = self.SCORE_GLOW_COLOR
        
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
                'SCORE_GLOW_COLOR': self.score_glow_color
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
            result = self.draw_settings_screen(screen, events, None, lambda: "title")
            
            # Draw debug console if active
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)
            
            pygame.display.flip()
            clock.tick(60)
            
            # Handle return to title screen
            if result == "title":
                return result
            
    def draw_settings_screen(self, screen, events, sound_test_fn=None, back_fn=None):
        """Draw the settings screen with all options."""
        # Get fonts at different sizes
        title_font = get_pixel_font(24)
        font = get_pixel_font(20)
        small_font = get_pixel_font(16)
        
        # Clear screen
        screen.fill(self.BLACK)
        
        # Calculate positions
        width, height = screen.get_width(), screen.get_height()
        center_x = width // 2
        
        # Create a surface for scrollable content
        total_height = 950  # Approximate total height of content
        content_surface = pygame.Surface((width, total_height))
        content_surface.fill(self.BLACK)
        
        # Track scroll position (class variable if not exists)
        if not hasattr(self, 'scroll_y'):
            self.scroll_y = 0
            
        # Handle scrolling with mouse wheel
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_y = min(0, max(-total_height + height, self.scroll_y + event.y * 30))
        
        current_y = 50
        spacing = 50
        
        # Title
        title = title_font.render("Settings", True, self.WHITE)
        content_surface.blit(title, (center_x - title.get_width()//2, current_y))
        current_y += spacing * 1.5
        
        button = get_button()
        
        # Resolution settings
        current_res = f"{self.screen_sizes[self.current_size_index][0]}x{self.screen_sizes[self.current_size_index][1]}"
        res_label = font.render("Resolution:", True, self.WHITE)
        content_surface.blit(res_label, (center_x - 200, current_y))
        res_btn_rect = pygame.Rect(center_x - 50, current_y, 200, 30)
        button.draw(content_surface, res_btn_rect, current_res, font,
                   is_hovered=res_btn_rect.collidepoint((pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] + self.scroll_y)))
        current_y += spacing
        
        # Player name
        name_label = font.render("Player Name:", True, self.WHITE)
        content_surface.blit(name_label, (center_x - 200, current_y))
        name_btn_rect = pygame.Rect(center_x - 50, current_y, 200, 30)
        button.draw(content_surface, name_btn_rect, self.player_name, font,
                   is_hovered=name_btn_rect.collidepoint((pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] + self.scroll_y)))
        current_y += spacing
        
        # Shader toggle
        shader_label = font.render("Shader Effects:", True, self.WHITE)
        content_surface.blit(shader_label, (center_x - 200, current_y))
        shader_btn_rect = pygame.Rect(center_x - 50, current_y, 200, 30)
        button.draw(content_surface, shader_btn_rect, "On" if self.shader_enabled else "Off", font,
                   is_hovered=shader_btn_rect.collidepoint((pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] + self.scroll_y)))
        current_y += spacing
        
        # Retro effects settings section
        retro_text = font.render("Retro Effects", True, self.WHITE)
        content_surface.blit(retro_text, (center_x - retro_text.get_width()//2, current_y))
        current_y += spacing
        
        # Retro effects enabled toggle
        effects_label = small_font.render("Enable Effects:", True, self.WHITE)
        content_surface.blit(effects_label, (center_x - 200, current_y))
        effects_btn_rect = pygame.Rect(center_x - 50, current_y, 200, 30)
        button.draw(content_surface, effects_btn_rect, "On" if self.retro_effects_enabled else "Off", font,
                   is_hovered=effects_btn_rect.collidepoint((pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] + self.scroll_y)))
        current_y += spacing * 0.8
        
        # Scanline intensity
        scanline_text = small_font.render(
            f"Scanline Intensity: {self.scanline_intensity}%", True, self.WHITE)
        content_surface.blit(scanline_text, (center_x - scanline_text.get_width()//2, current_y))
        current_y += spacing * 0.8
        
        # Glow intensity
        glow_text = small_font.render(
            f"Glow Intensity: {self.glow_intensity}%", True, self.WHITE)
        content_surface.blit(glow_text, (center_x - glow_text.get_width()//2, current_y))
        current_y += spacing * 1.2
        
        # Draw preview box
        preview_width = min(300, int(width * 0.4))  # Scale preview width with window
        preview_height = 100
        preview_x = center_x - preview_width // 2
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
        
        # Draw control hints
        hint_color = (180, 180, 180)  # Slightly dimmer white
        controls = [
            "Controls:",
            "R - Toggle Retro Effects",
            "← → - Adjust Scanline Intensity",
            "Shift + ← → - Adjust Glow Intensity",
            "Mouse Wheel - Scroll Settings"
        ]
        
        # Create hints surface
        hints_y = current_y
        hints_height = len(controls) * spacing * 0.7 + spacing * 0.8
        hints_surface = pygame.Surface((width, hints_height), pygame.SRCALPHA)
        
        hint_y = 0
        for hint in controls:
            hint_text = small_font.render(hint, True, hint_color)
            hints_surface.blit(hint_text, (center_x - hint_text.get_width()//2, hint_y))
            hint_y += spacing * 0.7
        
        content_surface.blit(hints_surface, (0, hints_y))
        current_y = hints_y + hints_height + spacing * 0.8
        
        # Draw buttons (fixed at bottom of screen)
        button_y = height - 100
        button = get_button()
        
        # Create button rectangles
        save_btn_rect = pygame.Rect(center_x - 150, button_y, 100, 40)
        back_btn_rect = pygame.Rect(center_x + 50, button_y, 100, 40)
        
        # Draw the scrollable content to the screen
        visible_rect = pygame.Rect(0, -self.scroll_y, width, height)
        screen.blit(content_surface, (0, 0), visible_rect)
        
        # Draw buttons using Button instance (on main screen, not content surface)
        button.draw(screen, save_btn_rect, "Save", font,
                   is_hovered=save_btn_rect.collidepoint(pygame.mouse.get_pos()))
        button.draw(screen, back_btn_rect, "Back", font,
                   is_hovered=back_btn_rect.collidepoint(pygame.mouse.get_pos()))
        
        # Handle button actions
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 2, 3):  # Only left, middle, right clicks
                mouse_pos = pygame.mouse.get_pos()
                # Adjust mouse position for scrolling when checking content surface buttons
                scrolled_pos = (mouse_pos[0], mouse_pos[1] + self.scroll_y)
                
                if res_btn_rect.collidepoint(scrolled_pos):
                    # Cycle through available resolutions
                    self.current_size_index = (self.current_size_index + 1) % len(self.screen_sizes)
                    # Force reset scroll position when changing resolution
                    self.scroll_y = 0
                    # Save and apply new resolution immediately
                    new_width, new_height = self.screen_sizes[self.current_size_index]
                    self.update_dimensions(new_width, new_height)
                    pygame.display.set_mode((new_width, new_height))
                elif name_btn_rect.collidepoint(scrolled_pos):
                    # Handle player name change
                    from ..Ping_UI import player_name_screen
                    new_name = player_name_screen(screen, pygame.time.Clock(), width, height)
                    if new_name:
                        self.player_name = new_name
                elif shader_btn_rect.collidepoint(scrolled_pos):
                    # Toggle shader effects
                    self.shader_enabled = not self.shader_enabled
                elif effects_btn_rect.collidepoint(scrolled_pos):
                    # Toggle retro effects
                    self.retro_effects_enabled = not self.retro_effects_enabled
                # These buttons are not on the content surface, so use original mouse pos
                elif save_btn_rect.collidepoint(mouse_pos):
                    if self.save_settings():
                        print("Settings saved successfully")
                        # Apply resolution change immediately if needed
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
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.glow_intensity = max(0, self.glow_intensity - 5)
                    else:
                        self.scanline_intensity = max(0, self.scanline_intensity - 5)
                elif event.key == pygame.K_RIGHT:
                    # Increase values
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.glow_intensity = min(100, self.glow_intensity + 5)
                    else:
                        self.scanline_intensity = min(100, self.scanline_intensity + 5)