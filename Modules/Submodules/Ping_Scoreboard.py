import pygame
import math
from .Ping_Fonts import get_pixel_font

class Scoreboard:
    """Handles the scoreboard display with retro arcade styling."""
    def __init__(self, height, scale_y, colors):
        """Initialize the scoreboard with given parameters."""
        self.height = height
        self.scale_y = scale_y
        self.WHITE = colors['WHITE']
        self.DARK_BLUE = colors['DARK_BLUE']
        self._debug_shown = False
        self.time_accumulated = 0
        
        # Load style settings
        self.load_settings()
        
        # VS color is always red for visibility
        self.VS_COLOR = (255, 100, 100)
        
        # Get pixel font variants
        self.name_font = get_pixel_font(12)    # Smaller for names
        self.score_font = get_pixel_font(24)   # Larger for scores
        self.vs_font = get_pixel_font(14)      # Medium for VS text
    
    def load_settings(self):
        """Load scoreboard style settings from settings file."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f if '=' in line and not line.strip().startswith('#'))
            
            # Load and validate settings with defaults
            self.SCANLINE_ALPHA = int(settings.get('SCANLINE_INTENSITY', '40'))
            self.GLOW_INTENSITY = int(settings.get('GLOW_INTENSITY', '80'))
            self.VS_BLINK_SPEED = float(settings.get('VS_BLINK_SPEED', '5.0'))
            self.GLOW_SPEED = 4.0
            
            # Parse color
            color_str = settings.get('SCORE_GLOW_COLOR', '180,180,255')
            r, g, b = map(int, color_str.split(','))
            self.SCORE_GLOW_COLOR = (r, g, b)
            
            # Check if retro effects are enabled
            self.retro_enabled = settings.get('RETRO_EFFECTS_ENABLED', 'true').lower() == 'true'
            
        except Exception as e:
            print(f"Error loading scoreboard settings, using defaults: {e}")
            # Default values
            self.SCANLINE_ALPHA = 40
            self.GLOW_INTENSITY = 80
            self.VS_BLINK_SPEED = 5.0
            self.GLOW_SPEED = 4.0
            self.SCORE_GLOW_COLOR = (180, 180, 255)
            self.retro_enabled = True

    def draw_scanlines(self, screen, rect):
        """Draw CRT-style scanlines effect."""
        if not self.retro_enabled:
            return
            
        scanline_surf = pygame.Surface((rect.width, 2), pygame.SRCALPHA)
        pygame.draw.line(scanline_surf, (0, 0, 0, self.SCANLINE_ALPHA), (0, 0), (rect.width, 0))
        for y in range(0, rect.height, 4):
            screen.blit(scanline_surf, (rect.x, rect.y + y))

    def draw_segmented_number(self, screen, number, x, y, color, size=40):
        """Draw a number in a retro LED display style."""
        segment_width = size // 2
        segment_height = size
        spacing = segment_width // 4

        if self.retro_enabled:
            # Calculate glow based on settings
            glow = (math.sin(self.time_accumulated * self.GLOW_SPEED) + 1) / 2
            glow_intensity = glow * (self.GLOW_INTENSITY / 100)
            
            # Draw glow effect
            glow_surf = pygame.Surface((segment_width + spacing * 4,
                                      segment_height + spacing * 4), pygame.SRCALPHA)
            r, g, b = self.SCORE_GLOW_COLOR
            glow_color = (r, g, b, int(128 * glow_intensity))
            pygame.draw.rect(glow_surf, glow_color,
                           (0, 0, glow_surf.get_width(), glow_surf.get_height()),
                           border_radius=spacing)
            screen.blit(glow_surf, (x - spacing * 2, y - spacing * 2))

        # Draw box around number
        box_rect = pygame.Rect(x - spacing, y - spacing,
                             segment_width + spacing * 2,
                             segment_height + spacing * 2)
        pygame.draw.rect(screen, self.DARK_BLUE, box_rect)
        pygame.draw.rect(screen, color, box_rect, 2)

        # Draw number with shadow effect
        text = self.score_font.render(str(number), True, color)
        
        if self.retro_enabled:
            # Draw shadow
            shadow_pos = (x + (segment_width - text.get_width()) // 2 + 2,
                        y + (segment_height - text.get_height()) // 2 + 2)
            screen.blit(text, shadow_pos, special_flags=pygame.BLEND_RGBA_SUB)
        
        # Draw main text
        text_pos = (x + (segment_width - text.get_width()) // 2,
                   y + (segment_height - text.get_height()) // 2)
        screen.blit(text, text_pos)

    def draw(self, screen, player_name, score_a, opponent_name, score_b, font, respawn_timer=None):
        """Draw the scoreboard with configurable retro effects."""
        self.time_accumulated += 1/60
        screen_width = screen.get_width()
        scoreboard_height = int(self.height * self.scale_y)
        
        # Draw main background
        scoreboard_rect = pygame.Rect(0, 0, screen_width, scoreboard_height)
        pygame.draw.rect(screen, self.DARK_BLUE, scoreboard_rect)
        
        # Draw scanlines if enabled
        self.draw_scanlines(screen, scoreboard_rect)

        # Draw borders with optional glow
        if self.retro_enabled:
            border_glow = (math.sin(self.time_accumulated * self.GLOW_SPEED) + 1) / 2
            glow_intensity = border_glow * (self.GLOW_INTENSITY / 100)
            
            # Multi-layer glow effect
            for i in range(2):
                glow_rect = pygame.Rect(i, i, screen_width - i*2, scoreboard_height - i*2)
                r, g, b = self.SCORE_GLOW_COLOR
                glow_alpha = int(40 * glow_intensity) >> i
                glow_color = (r, g, b, glow_alpha)
                pygame.draw.rect(screen, glow_color, glow_rect, 1)

        # Draw main border
        pygame.draw.rect(screen, self.WHITE, scoreboard_rect, 2)

        # Calculate positions
        center_x = screen_width // 2
        name_y = 5
        score_y = name_y + 20

        # Draw player names
        for name, x_pos in [(player_name, center_x - 150), (opponent_name, center_x + 150)]:
            text = self.name_font.render(name, True, self.WHITE)
            pos_x = x_pos - text.get_width()//2
            
            if self.retro_enabled:
                # Multi-layer shadow
                shadow_colors = [(20, 20, 40), (30, 30, 60)]
                for i, color in enumerate(shadow_colors):
                    shadow = self.name_font.render(name, True, color)
                    screen.blit(shadow, (pos_x + i + 1, name_y + i + 1))
            
            screen.blit(text, (pos_x, name_y))

        # Draw VS text with optional blinking
        vs_alpha = 255
        if self.retro_enabled:
            vs_alpha = int(abs(math.sin(self.time_accumulated * self.VS_BLINK_SPEED)) * 255)
        vs_text = self.vs_font.render("VS", True, (*self.VS_COLOR, vs_alpha))
        vs_rect = vs_text.get_rect(center=(center_x, name_y + vs_text.get_height()//2))
        screen.blit(vs_text, vs_rect)

        # Draw scores
        self.draw_segmented_number(screen, score_a, center_x - 150, score_y, self.WHITE)
        self.draw_segmented_number(screen, score_b, center_x + 150, score_y, self.WHITE)

        # Draw respawn timer if active
        if respawn_timer is not None and respawn_timer > 0:
            timer_size = 60
            timer_x = center_x - timer_size // 2
            timer_y = screen.get_height() // 2 - timer_size // 2
            
            # Draw timer with intense pulsing if retro enabled
            self.draw_segmented_number(screen, int(respawn_timer),
                                     timer_x, timer_y, (255, 100, 100),
                                     size=timer_size)