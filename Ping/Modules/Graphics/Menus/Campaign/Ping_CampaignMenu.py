import pygame
import time
import random
import math
from ...UI.Ping_Fonts import get_pixel_font
from ...UI.Ping_Button import get_button
from ....Core.Ping_MapState import get_map_state

# SNES-style gritty retro factory color palette
FACTORY_GRAY = (95, 85, 80)           # Base factory gray
FACTORY_GRAY_LIGHT = (115, 105, 100)  # Highlighted areas
FACTORY_GRAY_DARK = (75, 65, 60)      # Shadow areas
BRONZE_ACCENT = (140, 120, 90)        # Main bronze
BRONZE_LIGHT = (160, 140, 110)        # Bronze highlights
BRONZE_DARK = (100, 85, 65)           # Bronze shadows
DARK_BRONZE = (80, 70, 60)            # Base dark bronze
DARK_BRONZE_SHADOW = (60, 50, 40)     # Deep shadows
RED_ACCENT = (200, 80, 60)            # Warning red
RUST_RED = (160, 70, 50)              # Rust color
RUST_ORANGE = (180, 90, 60)           # Rust variation
DARK_METAL = (55, 50, 48)             # Base dark metal
DARK_METAL_SHADOW = (35, 30, 28)      # Deep metal shadow
FACTORY_LIGHT = (180, 160, 130)       # Warm light
SMOKE_GRAY = (110, 105, 100)          # Steam color
WARNING_RED = (220, 90, 70)           # Bright warning
PIPE_BRONZE = (130, 115, 85)          # Pipe color

# SNES-style retro accent colors
RETRO_ORANGE = (255, 140, 70)         # Bright orange
RETRO_ORANGE_DARK = (200, 110, 50)    # Orange shadow
RETRO_CYAN = (70, 180, 200)           # Cool cyan
RETRO_CYAN_DARK = (50, 140, 160)      # Cyan shadow
RETRO_YELLOW = (255, 220, 80)         # Bright yellow
RETRO_YELLOW_DARK = (200, 170, 60)    # Yellow shadow
RETRO_PURPLE = (160, 100, 180)        # Soft purple
RETRO_PURPLE_DARK = (120, 70, 140)    # Purple shadow
NEON_GREEN = (120, 255, 150)          # Bright green
NEON_GREEN_DARK = (80, 200, 110)      # Green shadow

# Additional SNES-style colors
STEEL_BLUE = (90, 110, 130)           # Steel surfaces
COPPER_BROWN = (150, 90, 70)          # Copper pipes
OIL_BLACK = (25, 20, 18)              # Oil stains
SPARK_YELLOW = (255, 255, 180)        # Electrical sparks
GLOW_WHITE = (240, 240, 255)          # Bright highlights

# Enhanced metallic color palette
STEEL_GRAY = (65, 65, 70)             # Base metallic gray
STEEL_GRAY_DARK = (45, 45, 50)        # Darker steel
STEEL_GRAY_LIGHT = (85, 85, 90)       # Highlighted steel
GUNMETAL = (40, 42, 45)               # Very dark metallic
CHROME = (180, 185, 190)              # Bright metallic highlights
IRON_OXIDE = (70, 60, 55)             # Oxidized metal
TITANIUM = (75, 78, 82)               # Titanium finish
WEATHERED_STEEL = (60, 58, 55)        # Old weathered metal
INDUSTRIAL_BLACK = (30, 32, 35)       # Deep industrial black

# Text colors
TEXT_WHITE = (255, 255, 255)
TEXT_RED = (240, 100, 80)
TEXT_BRONZE = (200, 180, 150)

class IndustrialSteamParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-0.3, 0.3)  # Slight horizontal drift
        self.vel_y = random.uniform(-2.0, -1.2)  # Upward movement with variation
        self.life = random.uniform(3.0, 5.0)
        self.max_life = self.life
        self.pixel_size = random.randint(3, 8)
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)

    def update(self, dt):
        self.x += self.vel_x * dt * 60
        self.y += self.vel_y * dt * 60
        self.life -= dt
        self.rotation += self.rotation_speed * dt
        
        # Steam dissipates and slows down over time
        self.vel_y *= 0.998
        self.vel_x *= 0.995

    def draw(self, screen):
        if self.life > 0:
            alpha_factor = self.life / self.max_life
            alpha = int(alpha_factor * 80)
            if alpha > 5:  # Only draw if visible enough
                # Industrial steam color (more gray-white)
                base_gray = int(180 + alpha_factor * 30)
                color = (base_gray, base_gray, base_gray + 10)
                
                # Variable size based on life (expands as it rises)
                current_size = int(self.pixel_size * (1.5 - alpha_factor * 0.5))
                
                pixel_x = int(self.x - current_size // 2)
                pixel_y = int(self.y - current_size // 2)
                
                # Draw as circle for more realistic steam
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), max(1, current_size // 2))

    def is_alive(self):
        return self.life > 0

class CampaignMenu:
    def __init__(self, sound_manager):
        self.options = ["Start New Run", "Continue Run", "Back to Title"]
        self.selected_option = 0
        self.button = get_button()
        self.sound_manager = sound_manager
        self.map_state = get_map_state()
        
        # Cached background
        self.background_surface = None
        self.background_width = 0
        self.background_height = 0
        
        # Visual effects
        self.steam_particles = []
        self.last_steam_time = 0
        self.steam_spawn_interval = 1.0  # Slower spawn rate
        self.warning_light_timer = 0
        self.warning_light_on = False
        
        # Title animation
        self.title_glow_timer = 0
        self.title_pulse = 1.0
    
    def _add_dither_pattern(self, surface, rect, base_color, dither_color, pattern_type="checkerboard"):
        """Add SNES-style dithering to a surface area."""
        for x in range(rect.x, rect.right, 2):
            for y in range(rect.y, rect.bottom, 2):
                if pattern_type == "checkerboard":
                    if (x + y) % 4 == 0:
                        pygame.draw.rect(surface, dither_color, (x, y, 1, 1))
                elif pattern_type == "scanlines":
                    if y % 2 == 0:
                        pygame.draw.rect(surface, dither_color, (x, y, 1, 1))
                elif pattern_type == "dots":
                    if x % 4 == 0 and y % 4 == 0:
                        pygame.draw.rect(surface, dither_color, (x, y, 2, 2))
    
    def _draw_metal_panel(self, surface, rect, base_color, highlight_color, shadow_color):
        """Draw a detailed metal panel with SNES-style shading."""
        # Base panel
        pygame.draw.rect(surface, base_color, rect)
        
        # Top/left highlights
        pygame.draw.line(surface, highlight_color, (rect.x, rect.y), (rect.right-1, rect.y), 1)
        pygame.draw.line(surface, highlight_color, (rect.x, rect.y), (rect.x, rect.bottom-1), 1)
        
        # Bottom/right shadows
        pygame.draw.line(surface, shadow_color, (rect.x+1, rect.bottom-1), (rect.right-1, rect.bottom-1), 1)
        pygame.draw.line(surface, shadow_color, (rect.right-1, rect.y+1), (rect.right-1, rect.bottom-1), 1)
        
        # Add subtle texture using dithering
        if rect.width > 8 and rect.height > 8:
            inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
            self._add_dither_pattern(surface, inner_rect, base_color, shadow_color, "dots")
    
    def _draw_rivet_detail(self, surface, x, y, size=3):
        """Draw a small rivet detail."""
        # Rivet base
        pygame.draw.circle(surface, STEEL_GRAY_DARK, (x, y), size)
        # Highlight
        pygame.draw.circle(surface, CHROME, (x-1, y-1), max(1, size-1))
        # Shadow
        pygame.draw.circle(surface, INDUSTRIAL_BLACK, (x+1, y+1), max(1, size-2))
    
    def _draw_diamond_plate_pattern(self, surface, rect):
        """Draw industrial diamond plate texture."""
        diamond_size = 8
        for y in range(rect.y, rect.bottom, diamond_size):
            for x in range(rect.x, rect.right, diamond_size):
                # Offset every other row
                offset_x = diamond_size // 2 if ((y - rect.y) // diamond_size) % 2 else 0
                plate_x = x + offset_x
                
                if plate_x + diamond_size <= rect.right:
                    # Diamond shape points
                    diamond_points = [
                        (plate_x + diamond_size//2, y),
                        (plate_x + diamond_size, y + diamond_size//2),
                        (plate_x + diamond_size//2, y + diamond_size),
                        (plate_x, y + diamond_size//2)
                    ]
                    
                    # Draw raised diamond
                    pygame.draw.polygon(surface, STEEL_GRAY_LIGHT, diamond_points)
                    # Add shadow edge
                    pygame.draw.polygon(surface, STEEL_GRAY_DARK, diamond_points, 1)
    
    def _draw_welding_seam(self, surface, start_pos, end_pos):
        """Draw a welding seam detail."""
        # Main seam line
        pygame.draw.line(surface, TITANIUM, start_pos, end_pos, 2)
        # Heat affected zone (subtle discoloration)
        pygame.draw.line(surface, IRON_OXIDE, (start_pos[0], start_pos[1]+1), (end_pos[0], end_pos[1]+1), 1)
        
        # Weld bead details (small dots along the seam)
        seam_length = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
        if seam_length > 20:
            num_beads = int(seam_length // 8)
            for i in range(1, num_beads):
                t = i / num_beads
                bead_x = int(start_pos[0] + t * (end_pos[0] - start_pos[0]))
                bead_y = int(start_pos[1] + t * (end_pos[1] - start_pos[1]))
                pygame.draw.circle(surface, CHROME, (bead_x, bead_y), 1)
    
    def _draw_metal_conduit(self, surface, start_pos, end_pos, thickness=4):
        """Draw a metal conduit pipe."""
        # Main pipe body
        pygame.draw.line(surface, STEEL_GRAY, start_pos, end_pos, thickness)
        # Highlight edge
        pygame.draw.line(surface, STEEL_GRAY_LIGHT, start_pos, end_pos, thickness - 2)
        # Shadow edge
        pygame.draw.line(surface, WEATHERED_STEEL, 
                        (start_pos[0] + 1, start_pos[1] + 1), 
                        (end_pos[0] + 1, end_pos[1] + 1), thickness - 2)
        
        # Pipe joints/connectors
        joint_positions = [start_pos, end_pos]
        for joint_x, joint_y in joint_positions:
            pygame.draw.circle(surface, GUNMETAL, (joint_x, joint_y), thickness)
            pygame.draw.circle(surface, CHROME, (joint_x - 1, joint_y - 1), thickness - 2)
    
    def _draw_ventilation_grille(self, surface, rect):
        """Draw an industrial ventilation grille with metallic detail."""
        # Grille background
        pygame.draw.rect(surface, INDUSTRIAL_BLACK, rect)
        pygame.draw.rect(surface, TITANIUM, rect, 1)
        
        # Industrial grille slats with metallic finish
        slat_spacing = 4
        for y in range(rect.y + 2, rect.bottom - 2, slat_spacing):
            # Main slat
            pygame.draw.line(surface, STEEL_GRAY, (rect.x + 1, y), (rect.right - 1, y), 2)
            # Highlight on top
            pygame.draw.line(surface, CHROME, (rect.x + 1, y - 1), (rect.right - 1, y - 1), 1)
            # Shadow on bottom
            pygame.draw.line(surface, GUNMETAL, (rect.x + 1, y + 1), (rect.right - 1, y + 1), 1)
        
        # Add protective mesh pattern
        for x in range(rect.x + 2, rect.right - 2, 3):
            for y in range(rect.y + 2, rect.bottom - 2, 3):
                if (x + y) % 6 == 0:
                    pygame.draw.rect(surface, WEATHERED_STEEL, (x, y, 1, 1))
    
    def _draw_warning_sticker(self, surface, x, y, width, height, warning_type="DANGER"):
        """Draw a detailed warning sticker."""
        sticker_rect = pygame.Rect(x, y, width, height)
        
        # Sticker background
        pygame.draw.rect(surface, RETRO_YELLOW, sticker_rect)
        pygame.draw.rect(surface, RETRO_YELLOW_DARK, sticker_rect, 2)
        
        # Warning stripes
        stripe_width = 4
        for stripe_x in range(sticker_rect.x + 2, sticker_rect.right - 2, stripe_width * 2):
            stripe_rect = pygame.Rect(stripe_x, sticker_rect.y + 2, stripe_width, sticker_rect.height - 4)
            pygame.draw.rect(surface, RED_ACCENT, stripe_rect)
        
        # Age/wear effect
        if random.random() < 0.3:
            wear_rect = pygame.Rect(x + random.randint(0, width//2), y + random.randint(0, height//2), 
                                  random.randint(3, width//3), random.randint(2, height//3))
            pygame.draw.rect(surface, RUST_ORANGE, wear_rect)

    def _create_factory_background(self, width, height):
        """Create a retro-styled abandoned Pong Ball Manufacturing Facility."""
        surface = pygame.Surface((width, height))
        
        # Create a dark metallic gradient background
        for y in range(height):
            gradient_factor = y / height
            # Darker, more metallic gradient from gunmetal to steel gray dark
            bg_color = (
                int(GUNMETAL[0] + gradient_factor * (STEEL_GRAY_DARK[0] - GUNMETAL[0])),
                int(GUNMETAL[1] + gradient_factor * (STEEL_GRAY_DARK[1] - GUNMETAL[1])),
                int(GUNMETAL[2] + gradient_factor * (STEEL_GRAY_DARK[2] - GUNMETAL[2]))
            )
            pygame.draw.line(surface, bg_color, (0, y), (width, y))
            
            # Add subtle metallic shimmer effect using dithering every few lines
            if y % 8 == 0:
                shimmer_color = (
                    min(255, bg_color[0] + 10),
                    min(255, bg_color[1] + 10),
                    min(255, bg_color[2] + 12)
                )
                for x in range(0, width, 16):
                    if (x + y) % 32 == 0:
                        pygame.draw.rect(surface, shimmer_color, (x, y, 2, 1))
        
        # Industrial steel floor with diamond plate pattern
        floor_height = height // 4
        floor_rect = pygame.Rect(0, height - floor_height, width, floor_height)
        pygame.draw.rect(surface, STEEL_GRAY, floor_rect)
        
        # Diamond plate pattern across the entire floor
        self._draw_diamond_plate_pattern(surface, floor_rect)
        
        # Add metal grating sections
        grating_sections = [
            pygame.Rect(width // 6, height - floor_height + 10, width // 4, 30),
            pygame.Rect(2 * width // 3, height - floor_height + 20, width // 5, 25)
        ]
        
        for grating_rect in grating_sections:
            # Grating background
            pygame.draw.rect(surface, GUNMETAL, grating_rect)
            
            # Cross-hatch pattern
            spacing = 6
            for i in range(grating_rect.x, grating_rect.right, spacing):
                pygame.draw.line(surface, TITANIUM, (i, grating_rect.y), (i, grating_rect.bottom), 1)
            for i in range(grating_rect.y, grating_rect.bottom, spacing):
                pygame.draw.line(surface, TITANIUM, (grating_rect.x, i), (grating_rect.right, i), 1)
            
            # Frame around grating
            pygame.draw.rect(surface, WEATHERED_STEEL, grating_rect, 2)
        
        # Add welding seams across floor sections
        floor_seams = [
            ((0, height - floor_height + floor_height // 3), (width, height - floor_height + floor_height // 3)),
            ((width // 3, height - floor_height), (width // 3, height - floor_height + floor_height // 2)),
            ((2 * width // 3, height - floor_height), (2 * width // 3, height - floor_height + floor_height // 2))
        ]
        
        for seam_start, seam_end in floor_seams:
            self._draw_welding_seam(surface, seam_start, seam_end)
        
        # Organized metal scratches in logical wear areas
        # Scratches near equipment and high-traffic areas
        intentional_scratches = [
            # Near left equipment
            ((width // 8 - 10, height - floor_height + 40), (width // 8 + 25, height - floor_height + 42)),
            ((width // 8 + 5, height - floor_height + 50), (width // 8 + 30, height - floor_height + 48)),
            # Center walkway area
            ((width // 2 - 15, height - floor_height + 25), (width // 2 + 20, height - floor_height + 26)),
            ((width // 2 + 10, height - floor_height + 35), (width // 2 + 35, height - floor_height + 37)),
            # Near right equipment
            ((3 * width // 4 - 5, height - floor_height + 30), (3 * width // 4 + 18, height - floor_height + 28)),
            # Loading area scratches
            ((width // 4, height - 20), (width // 4 + 25, height - 18)),
            ((2 * width // 3, height - 25), (2 * width // 3 + 20, height - 27))
        ]
        
        for (start_x, start_y), (end_x, end_y) in intentional_scratches:
            # Main scratch
            pygame.draw.line(surface, WEATHERED_STEEL, (start_x, start_y), (end_x, end_y), 1)
            # Subtle highlight
            pygame.draw.line(surface, STEEL_GRAY_LIGHT, (start_x, start_y - 1), (end_x, end_y - 1), 1)
        
        # Cleaner oil stains with metallic reflections (reduced and more organized)
        # Place stains in specific areas rather than randomly
        organized_stain_locations = [
            (width // 4, height - floor_height + 20, 12),        # Near left equipment
            (width // 2 + 20, height - floor_height + 35, 15),   # Center-right area
            (3 * width // 4 - 10, height - floor_height + 25, 10), # Right area
            (width // 3, height - 30, 8),                        # Lower center
            (2 * width // 3, height - 15, 14)                    # Lower right
        ]
        
        for stain_x, stain_y, stain_size in organized_stain_locations:
            # Simpler, cleaner oil stain shapes
            pygame.draw.ellipse(surface, OIL_BLACK, (stain_x, stain_y, stain_size, stain_size // 2))
            
            # Subtle rainbow oil slick effect (only on larger stains)
            if stain_size > 10:
                slick_colors = [(40, 25, 60), (25, 45, 30)]  # More subtle rainbow
                for i, slick_color in enumerate(slick_colors):
                    offset = i + 1
                    slick_rect = pygame.Rect(stain_x + offset, stain_y + offset, 
                                           max(2, stain_size - offset * 2), max(1, (stain_size // 2) - offset))
                    pygame.draw.ellipse(surface, slick_color, slick_rect)
            
            # Metallic reflection highlights
            reflection_rect = pygame.Rect(stain_x + 2, stain_y + 1, max(2, stain_size // 4), 1)
            pygame.draw.rect(surface, CHROME, reflection_rect)
        
        # Reduced and organized metallic debris (cleaner floor)
        # Place specific debris in logical locations
        organized_debris = [
            ('bolt', width // 6, height - floor_height + 15),
            ('rivet', width // 3 + 20, height - floor_height + 30),
            ('washer', width // 2 - 15, height - floor_height + 45),
            ('scrap', 2 * width // 3, height - floor_height + 20),
            ('bolt', 3 * width // 4 + 10, height - floor_height + 35),
            ('rivet', width // 8, height - 25),
            ('washer', width // 2 + 30, height - 15),
            ('spring', 3 * width // 4 - 5, height - 40)
        ]
        
        for debris_type, debris_x, debris_y in organized_debris:
            if debris_type == 'bolt':
                # Hex bolt head
                pygame.draw.circle(surface, STEEL_GRAY, (debris_x, debris_y), 2)
                pygame.draw.circle(surface, CHROME, (debris_x - 1, debris_y - 1), 1)
                # Bolt threads
                pygame.draw.rect(surface, TITANIUM, (debris_x - 1, debris_y + 1, 2, 4))
            elif debris_type == 'scrap':
                scrap_points = [(debris_x, debris_y), (debris_x + 4, debris_y), 
                               (debris_x + 3, debris_y + 3), (debris_x - 1, debris_y + 3)]
                pygame.draw.polygon(surface, IRON_OXIDE, scrap_points)
                # Torn edge highlight
                pygame.draw.line(surface, CHROME, (debris_x, debris_y), (debris_x + 2, debris_y), 1)
            elif debris_type == 'rivet':
                pygame.draw.circle(surface, GUNMETAL, (debris_x, debris_y), 2)
                pygame.draw.circle(surface, STEEL_GRAY_LIGHT, (debris_x - 1, debris_y - 1), 1)
            elif debris_type == 'washer':
                pygame.draw.circle(surface, WEATHERED_STEEL, (debris_x, debris_y), 2)
                pygame.draw.circle(surface, GUNMETAL, (debris_x, debris_y), 1)
            else:  # spring
                # Coil spring appearance (smaller)
                for i in range(3):
                    spring_y = debris_y + i
                    pygame.draw.circle(surface, TITANIUM, (debris_x, spring_y), 1)
        
        # Simplified wear patterns in key walkways only
        main_walkway = pygame.Rect(width // 3, height - floor_height + 10, width // 3, floor_height - 20)
        # Subtle polished area from foot traffic
        self._add_dither_pattern(surface, main_walkway, STEEL_GRAY, STEEL_GRAY_LIGHT, "scanlines")
        
        # Minimal metallic sheen in center of walkway
        center_shine = pygame.Rect(main_walkway.x + main_walkway.width // 3, main_walkway.y, 
                                 main_walkway.width // 3, main_walkway.height)
        for i in range(0, center_shine.width, 12):
            shine_x = center_shine.x + i
            if i % 24 == 0:
                pygame.draw.line(surface, CHROME, (shine_x, center_shine.y), (shine_x, center_shine.bottom), 1)
        
        # Stylized pong balls with retro glow effect
        for _ in range(15):
            ball_x = random.randint(20, width - 20)
            ball_y = random.randint(height - floor_height + 10, height - 10)
            ball_size = random.randint(8, 14)
            
            # Retro ball colors with neon accents
            ball_colors = [BRONZE_ACCENT, RETRO_ORANGE, RETRO_CYAN, RETRO_YELLOW]
            ball_color = random.choice(ball_colors)
            
            # Draw ball with glow effect
            for glow_radius in range(ball_size + 4, ball_size - 1, -1):
                alpha = max(0, 100 - (glow_radius - ball_size) * 30)
                glow_color = (*ball_color[:3], alpha)
                # Create temporary surface for alpha blending
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                surface.blit(glow_surface, (ball_x - glow_radius, ball_y - glow_radius), special_flags=pygame.BLEND_ALPHA_SDL2)
            
            # Main ball
            pygame.draw.circle(surface, ball_color, (ball_x, ball_y), ball_size // 2)
            pygame.draw.circle(surface, (255, 255, 255, 100), (ball_x - 2, ball_y - 2), max(1, ball_size // 4))  # Highlight
        
        # === RETRO GEOMETRIC ARCHITECTURE ===
        
        # Left section: Detailed storage units with SNES-style elements
        left_boundary = width // 3
        storage_units = [
            (width // 8, height // 2, 60, 80),
            (width // 5, height // 2.5, 50, 70)
        ]
        
        for i, (unit_x, unit_y, unit_w, unit_h) in enumerate(storage_units):
            unit_rect = pygame.Rect(unit_x - unit_w//2, unit_y - unit_h//2, unit_w, unit_h)
            
            # Main unit body using detailed metal panel
            self._draw_metal_panel(surface, unit_rect, STEEL_GRAY, STEEL_GRAY_LIGHT, STEEL_GRAY_DARK)
            
            # Unit frame/border with industrial look
            pygame.draw.rect(surface, TITANIUM, unit_rect, 3)
            pygame.draw.rect(surface, WEATHERED_STEEL, 
                           pygame.Rect(unit_rect.x + 2, unit_rect.bottom - 2, unit_rect.width - 2, 2))
            
            # Detailed panel divisions with metallic finish
            panel_height = unit_h // 4
            for panel_i in range(1, 4):
                panel_y = unit_rect.y + (panel_height * panel_i)
                panel_rect = pygame.Rect(unit_rect.x + 4, panel_y - 1, unit_rect.width - 8, 2)
                pygame.draw.rect(surface, CHROME, panel_rect)
                pygame.draw.rect(surface, GUNMETAL, 
                               pygame.Rect(panel_rect.x, panel_rect.bottom - 1, panel_rect.width, 1))
                
                # Add welding seams along panel divisions
                seam_start = (unit_rect.x + 2, panel_y)
                seam_end = (unit_rect.right - 2, panel_y)
                self._draw_welding_seam(surface, seam_start, seam_end)
            
            # Ventilation grille on side
            grille_rect = pygame.Rect(unit_rect.right - 12, unit_rect.y + 10, 8, 25)
            self._draw_ventilation_grille(surface, grille_rect)
            
            # Access panel with details
            access_rect = pygame.Rect(unit_rect.x + 5, unit_rect.y + unit_h - 25, unit_w - 10, 20)
            self._draw_metal_panel(surface, access_rect, GUNMETAL, STEEL_GRAY_LIGHT, INDUSTRIAL_BLACK)
            
            # Panel handle with metallic finish
            handle_rect = pygame.Rect(access_rect.right - 8, access_rect.y + 8, 4, 4)
            pygame.draw.rect(surface, TITANIUM, handle_rect)
            pygame.draw.rect(surface, CHROME, pygame.Rect(handle_rect.x, handle_rect.y, 2, 2))
            
            # Add conduit running from unit
            conduit_start = (unit_rect.centerx, unit_rect.bottom)
            conduit_end = (unit_rect.centerx + random.randint(-15, 15), height - floor_height)
            self._draw_metal_conduit(surface, conduit_start, conduit_end, 3)
            
            # Warning stickers
            if i == 0:  # First unit gets warning sticker
                self._draw_warning_sticker(surface, unit_rect.x + 8, unit_rect.y + 35, 20, 12)
            
            # Status indicator lights - enhanced
            light_colors = [NEON_GREEN, RETRO_YELLOW, RED_ACCENT]
            for light_i, base_light_color in enumerate(light_colors):
                light_x = unit_rect.x + 10 + light_i * 15
                light_y = unit_rect.y + 10
                
                # Light housing with industrial metallic finish
                housing_rect = pygame.Rect(light_x - 5, light_y - 5, 10, 10)
                self._draw_metal_panel(surface, housing_rect, GUNMETAL, STEEL_GRAY, INDUSTRIAL_BLACK)
                
                # Light itself with glow
                pygame.draw.circle(surface, base_light_color, (light_x, light_y), 3)
                pygame.draw.circle(surface, GLOW_WHITE, (light_x - 1, light_y - 1), 1)
                
                # Subtle glow effect
                glow_color = (*base_light_color[:3], 50)
                glow_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, glow_color, (6, 6), 6)
                surface.blit(glow_surface, (light_x - 6, light_y - 6), special_flags=pygame.BLEND_ALPHA_SDL2)
            
            # Rivets on corners
            rivet_positions = [(unit_rect.x + 4, unit_rect.y + 4), 
                             (unit_rect.right - 4, unit_rect.y + 4),
                             (unit_rect.x + 4, unit_rect.bottom - 4), 
                             (unit_rect.right - 4, unit_rect.bottom - 4)]
            for rivet_x, rivet_y in rivet_positions:
                self._draw_rivet_detail(surface, rivet_x, rivet_y, 2)
            
            # Replace cable connections with industrial conduit
            # (Already added above with _draw_metal_conduit)
        
        # Center section: Retro manufacturing equipment
        center_x = width // 2
        
        # Main processing unit (industrial metallic design)
        main_unit_rect = pygame.Rect(center_x - 80, height // 2 - 60, 160, 120)
        pygame.draw.rect(surface, GUNMETAL, main_unit_rect)
        pygame.draw.rect(surface, TITANIUM, main_unit_rect, 4)
        
        # Add industrial ribbing to main unit
        for rib_y in range(main_unit_rect.y + 10, main_unit_rect.bottom - 10, 8):
            pygame.draw.line(surface, STEEL_GRAY_LIGHT, 
                           (main_unit_rect.x + 5, rib_y), (main_unit_rect.right - 5, rib_y), 1)
            pygame.draw.line(surface, STEEL_GRAY_DARK, 
                           (main_unit_rect.x + 5, rib_y + 1), (main_unit_rect.right - 5, rib_y + 1), 1)
        
        # Industrial control panels with metallic finish
        panel_width = 30
        panel_colors = [STEEL_GRAY_DARK, GUNMETAL, WEATHERED_STEEL, TITANIUM]
        for i in range(4):
            panel_x = main_unit_rect.x + 10 + i * 35
            panel_rect = pygame.Rect(panel_x, main_unit_rect.y + 15, panel_width, 40)
            
            # Panel body
            self._draw_metal_panel(surface, panel_rect, panel_colors[i], CHROME, INDUSTRIAL_BLACK)
            
            # Control elements (buttons, switches)
            for control_y in range(panel_rect.y + 5, panel_rect.bottom - 5, 8):
                for control_x in range(panel_rect.x + 5, panel_rect.right - 5, 8):
                    if (control_x + control_y) % 16 == 0:
                        pygame.draw.circle(surface, TITANIUM, (control_x + 2, control_y + 2), 2)
                        pygame.draw.circle(surface, CHROME, (control_x + 1, control_y + 1), 1)
                    else:
                        pygame.draw.rect(surface, WEATHERED_STEEL, (control_x, control_y, 3, 3))
        
        # Add heavy-duty mounting bolts around the unit
        bolt_positions = [
            (main_unit_rect.x + 8, main_unit_rect.y + 8),
            (main_unit_rect.right - 8, main_unit_rect.y + 8),
            (main_unit_rect.x + 8, main_unit_rect.bottom - 8),
            (main_unit_rect.right - 8, main_unit_rect.bottom - 8)
        ]
        for bolt_x, bolt_y in bolt_positions:
            self._draw_rivet_detail(surface, bolt_x, bolt_y, 4)
        
        # Industrial metallic conveyor system
        conveyor_y = height - floor_height - 15
        conveyor_segments = [
            (0, left_boundary, STEEL_GRAY),
            (left_boundary, center_x + 80, TITANIUM),
            (center_x + 80, width, WEATHERED_STEEL)
        ]
        
        for start_x, end_x, segment_color in conveyor_segments:
            # Main conveyor track (industrial steel)
            pygame.draw.line(surface, segment_color, (start_x, conveyor_y), (end_x, conveyor_y), 8)
            pygame.draw.line(surface, CHROME, (start_x, conveyor_y - 3), (end_x, conveyor_y - 3), 2)
            pygame.draw.line(surface, INDUSTRIAL_BLACK, (start_x, conveyor_y + 3), (end_x, conveyor_y + 3), 1)
            
            # Industrial support pillars with metallic finish
            for support_x in range(start_x + 40, end_x, 60):
                support_rect = pygame.Rect(support_x - 4, conveyor_y, 8, 20)
                self._draw_metal_panel(surface, support_rect, GUNMETAL, STEEL_GRAY_LIGHT, INDUSTRIAL_BLACK)
                
                # Support bracing
                brace_start = (support_x - 8, conveyor_y + 20)
                brace_end = (support_x + 8, conveyor_y + 20)
                pygame.draw.line(surface, WEATHERED_STEEL, brace_start, brace_end, 3)
                
                # Bolt details on supports
                self._draw_rivet_detail(surface, support_x, conveyor_y + 10, 2)
        
        # Right section: Industrial metallic storage towers
        tower_positions = [(3 * width // 4, height // 2.2), (5 * width // 6, height // 2.5)]
        tower_base_colors = [STEEL_GRAY, GUNMETAL]
        
        for i, (tower_x, tower_y) in enumerate(tower_positions):
            tower_w, tower_h = 40, 100
            tower_rect = pygame.Rect(tower_x - tower_w//2, tower_y - tower_h//2, tower_w, tower_h)
            
            # Main tower with industrial metallic styling
            pygame.draw.rect(surface, tower_base_colors[i], tower_rect)
            pygame.draw.rect(surface, TITANIUM, tower_rect, 3)
            
            # Industrial tank sections with metallic banding
            section_height = tower_h // 5
            for section in range(5):
                section_y = tower_rect.y + section * section_height
                section_rect = pygame.Rect(tower_rect.x + 3, section_y + 2, tower_w - 6, section_height - 4)
                
                # Alternating metallic sections
                section_color = STEEL_GRAY_LIGHT if section % 2 == 0 else WEATHERED_STEEL
                pygame.draw.rect(surface, section_color, section_rect)
                
                # Metallic banding around sections
                band_y = section_y + section_height - 2
                pygame.draw.line(surface, TITANIUM, (tower_rect.x, band_y), (tower_rect.right, band_y), 2)
                pygame.draw.line(surface, CHROME, (tower_rect.x, band_y - 1), (tower_rect.right, band_y - 1), 1)
                
                # Inspection ports and gauges
                if section % 2 == 1:
                    port_rect = pygame.Rect(section_rect.x + 8, section_rect.y + 4, section_rect.width - 16, 4)
                    pygame.draw.rect(surface, INDUSTRIAL_BLACK, port_rect)
                    pygame.draw.rect(surface, CHROME, port_rect, 1)
            
            # Tower top with metallic cap
            cap_rect = pygame.Rect(tower_rect.x - 2, tower_rect.y - 8, tower_w + 4, 8)
            self._draw_metal_panel(surface, cap_rect, TITANIUM, CHROME, WEATHERED_STEEL)
            
            # Vertical support struts on tower sides
            for strut_x in [tower_rect.x + 3, tower_rect.right - 3]:
                pygame.draw.line(surface, WEATHERED_STEEL, 
                               (strut_x, tower_rect.y), (strut_x, tower_rect.bottom), 2)
                # Strut mounting bolts
                for bolt_y in range(tower_rect.y + 10, tower_rect.bottom, 20):
                    self._draw_rivet_detail(surface, strut_x, bolt_y, 1)
        
        # Industrial control terminal (right side)
        terminal_rect = pygame.Rect(width - 100, height // 1.7, 80, 50)
        self._draw_metal_panel(surface, terminal_rect, GUNMETAL, STEEL_GRAY_LIGHT, INDUSTRIAL_BLACK)
        pygame.draw.rect(surface, TITANIUM, terminal_rect, 3)
        
        # Industrial CRT screen with metallic housing
        screen_rect = pygame.Rect(terminal_rect.x + 8, terminal_rect.y + 8, 45, 30)
        # Screen housing
        screen_housing = pygame.Rect(screen_rect.x - 2, screen_rect.y - 2, screen_rect.width + 4, screen_rect.height + 4)
        pygame.draw.rect(surface, INDUSTRIAL_BLACK, screen_housing)
        pygame.draw.rect(surface, CHROME, screen_housing, 1)
        
        # CRT screen surface
        pygame.draw.rect(surface, (15, 35, 25), screen_rect)
        pygame.draw.rect(surface, NEON_GREEN, screen_rect, 2)
        
        # Enhanced scanlines with phosphor glow effect
        for scan_y in range(screen_rect.y + 2, screen_rect.bottom - 2, 3):
            pygame.draw.line(surface, NEON_GREEN, (screen_rect.x + 2, scan_y), (screen_rect.right - 2, scan_y), 1)
            # Phosphor fade
            fade_color = (40, 80, 50)
            pygame.draw.line(surface, fade_color, (screen_rect.x + 2, scan_y + 1), (screen_rect.right - 2, scan_y + 1), 1)
        
        # Industrial control buttons with metallic housings
        button_colors = [RED_ACCENT, RETRO_YELLOW, NEON_GREEN]
        for i, btn_color in enumerate(button_colors):
            btn_x = terminal_rect.x + 60 + (i * 8)
            btn_y = terminal_rect.y + 15 + (i * 12)
            
            # Button housing
            housing_rect = pygame.Rect(btn_x - 5, btn_y - 5, 10, 10)
            self._draw_metal_panel(surface, housing_rect, WEATHERED_STEEL, STEEL_GRAY_LIGHT, INDUSTRIAL_BLACK)
            
            # Button itself
            pygame.draw.circle(surface, btn_color, (btn_x, btn_y), 3)
            pygame.draw.circle(surface, CHROME, (btn_x - 1, btn_y - 1), 1)
        
        # Add control panel mounting screws
        screw_positions = [(terminal_rect.x + 5, terminal_rect.y + 5), 
                          (terminal_rect.right - 5, terminal_rect.y + 5),
                          (terminal_rect.x + 5, terminal_rect.bottom - 5), 
                          (terminal_rect.right - 5, terminal_rect.bottom - 5)]
        for screw_x, screw_y in screw_positions:
            self._draw_rivet_detail(surface, screw_x, screw_y, 1)
        
        # === RETRO ATMOSPHERIC ELEMENTS ===
        
        # Clean geometric warning signs
        warning_positions = [(width // 4, height // 3), (3 * width // 4, height // 3.5)]
        for i, (sign_x, sign_y) in enumerate(warning_positions):
            # Retro diamond-shaped warning sign
            diamond_size = 25
            diamond_points = [
                (sign_x, sign_y - diamond_size),
                (sign_x + diamond_size, sign_y),
                (sign_x, sign_y + diamond_size),
                (sign_x - diamond_size, sign_y)
            ]
            
            sign_color = WARNING_RED if i == 0 else RETRO_YELLOW
            pygame.draw.polygon(surface, sign_color, diamond_points)
            pygame.draw.polygon(surface, (255, 255, 255), diamond_points, 3)
            
            # Retro warning symbol (exclamation)
            pygame.draw.circle(surface, DARK_METAL, (sign_x, sign_y - 8), 2)
            pygame.draw.rect(surface, DARK_METAL, (sign_x - 1, sign_y - 3, 2, 8))
        
        # Industrial metallic ceiling structure
        ceiling_y = height // 6
        # Main structural I-beam with industrial detailing
        beam_rect = pygame.Rect(0, ceiling_y - 4, width, 8)
        self._draw_metal_panel(surface, beam_rect, STEEL_GRAY, CHROME, INDUSTRIAL_BLACK)
        
        # I-beam flanges (top and bottom)
        top_flange = pygame.Rect(0, ceiling_y - 6, width, 2)
        bottom_flange = pygame.Rect(0, ceiling_y + 4, width, 2)
        pygame.draw.rect(surface, TITANIUM, top_flange)
        pygame.draw.rect(surface, TITANIUM, bottom_flange)
        
        # Welding seams along the beam
        self._draw_welding_seam(surface, (0, ceiling_y - 6), (width, ceiling_y - 6))
        self._draw_welding_seam(surface, (0, ceiling_y + 6), (width, ceiling_y + 6))
        
        # Industrial support struts with metallic finish
        strut_spacing = width // 6
        for strut_x in range(strut_spacing, width, strut_spacing):
            # Heavy steel angle supports
            strut_thickness = 6
            
            # Left support strut
            left_start = (strut_x, ceiling_y)
            left_end = (strut_x - 30, ceiling_y + 40)
            self._draw_metal_conduit(surface, left_start, left_end, strut_thickness)
            
            # Right support strut
            right_start = (strut_x, ceiling_y)
            right_end = (strut_x + 30, ceiling_y + 40)
            self._draw_metal_conduit(surface, right_start, right_end, strut_thickness)
            
            # Connection plate at junction
            plate_rect = pygame.Rect(strut_x - 8, ceiling_y - 4, 16, 8)
            self._draw_metal_panel(surface, plate_rect, GUNMETAL, STEEL_GRAY_LIGHT, INDUSTRIAL_BLACK)
            
            # Mounting bolts
            self._draw_rivet_detail(surface, strut_x - 4, ceiling_y, 2)
            self._draw_rivet_detail(surface, strut_x + 4, ceiling_y, 2)
        
        # Industrial fluorescent lighting fixtures
        light_positions = [width // 4, width // 2, 3 * width // 4]
        industrial_light_colors = [(200, 210, 255), (180, 200, 245), (190, 205, 250)]  # Cool blue-white industrial lighting
        
        for i, light_x in enumerate(light_positions):
            # Industrial light fixture housing with metallic finish
            fixture_rect = pygame.Rect(light_x - 20, ceiling_y - 12, 40, 20)
            self._draw_metal_panel(surface, fixture_rect, GUNMETAL, STEEL_GRAY_LIGHT, INDUSTRIAL_BLACK)
            
            # Fluorescent tube housing
            tube_rect = pygame.Rect(light_x - 18, ceiling_y - 6, 36, 8)
            pygame.draw.rect(surface, WEATHERED_STEEL, tube_rect)
            pygame.draw.rect(surface, CHROME, tube_rect, 1)
            
            # Fluorescent tube itself
            tube_light_rect = pygame.Rect(light_x - 16, ceiling_y - 4, 32, 4)
            pygame.draw.rect(surface, industrial_light_colors[i], tube_light_rect)
            
            # Fixture mounting hardware
            self._draw_rivet_detail(surface, light_x - 15, ceiling_y - 10, 1)
            self._draw_rivet_detail(surface, light_x + 15, ceiling_y - 10, 1)
            
            # Industrial light beam effect (cooler, more realistic)
            beam_width = 70
            beam_height = 90
            beam_points = [
                (light_x - beam_width//6, ceiling_y + 8),
                (light_x + beam_width//6, ceiling_y + 8),
                (light_x + beam_width//3, ceiling_y + beam_height),
                (light_x - beam_width//3, ceiling_y + beam_height)
            ]
            
            # Create cooler industrial light beam
            beam_surface = pygame.Surface((beam_width, beam_height), pygame.SRCALPHA)
            # Much dimmer, cooler light
            beam_color = (*[int(c * 0.3) for c in industrial_light_colors[i]], 20)
            pygame.draw.polygon(beam_surface, beam_color, [(p[0] - (light_x - beam_width//2), p[1] - ceiling_y - 8) for p in beam_points])
            surface.blit(beam_surface, (light_x - beam_width//2, ceiling_y + 8), special_flags=pygame.BLEND_ALPHA_SDL2)
            
            # Add electrical conduit running to each fixture
            conduit_start = (light_x, ceiling_y - 12)
            conduit_end = (light_x + random.randint(-10, 10), ceiling_y - 30)
            self._draw_metal_conduit(surface, conduit_start, conduit_end, 2)

        return surface

    def _spawn_steam(self, width, height):
        """Spawn industrial steam particles from equipment vents."""
        current_time = time.time()
        if current_time - self.last_steam_time > self.steam_spawn_interval:
            # Spawn more particles for industrial atmosphere
            if len(self.steam_particles) < 12:  # Allow more particles for industrial feel
                # Enhanced spawn locations including ventilation grilles
                spawn_locations = [
                    (width // 2, height // 2 - 60),  # Main processing unit
                    (width // 8, height // 2 - 40),  # Left storage unit
                    (width // 5, height // 2.5 - 35),  # Second storage unit
                    (3 * width // 4, height // 2.2 - 50),  # Right tower 1
                    (5 * width // 6, height // 2.5 - 50),  # Right tower 2
                    (width - 90, height // 1.7 - 25)  # Control terminal
                ]
                
                # Spawn 1-3 particles per interval for more active atmosphere
                num_spawn = random.randint(1, 3)
                for _ in range(num_spawn):
                    if len(self.steam_particles) < 12:
                        # Randomly choose a spawn location
                        spawn_x, spawn_y = random.choice(spawn_locations)
                        # Add more variation to spawn position
                        spawn_x += random.randint(-15, 15)
                        spawn_y += random.randint(-8, 8)
                        
                        self.steam_particles.append(IndustrialSteamParticle(spawn_x, spawn_y))
            
            self.last_steam_time = current_time

    def handle_input(self, events, width, height):
        """Handle user input for menu navigation and selection."""
        # Calculate layout (similar to MainMenu)
        scale_y = height / 600
        scale_x = width / 800
        scale = min(scale_x, scale_y)

        title_font_size = max(24, int(56 * scale))
        title_font = get_pixel_font(title_font_size)
        title_surface = title_font.render("SELECT YOUR DESTINY", True, TEXT_WHITE)
        title_y = height // 6
        title_bottom = title_y + title_surface.get_height()

        option_font_size = max(12, int(24 * scale_y))
        button_height = max(40, int(50 * scale_y))
        button_width = max(250, int(width * 0.35))
        options_area_top = title_bottom + 80
        options_area_height = height - options_area_top - height // 8
        num_options = len(self.options)
        total_options_height = num_options * button_height + (num_options - 1) * 20
        start_y = options_area_top + (options_area_height - total_options_height) // 2

        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    action = self.options[self.selected_option].lower().replace(" ", "_")
                    if action == "start_new_run":
                        # Initialize new map tree run
                        self.map_state.initialize_new_run()
                        return "start_new_run"
                    elif action == "continue_run":
                        # Continue existing run or start new if none exists
                        if self.map_state.has_existing_run():
                            self.map_state.continue_existing_run()
                        else:
                            self.map_state.initialize_new_run()
                        return "continue_run"
                    elif action == "back_to_title":
                        return "back"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, option in enumerate(self.options):
                    button_rect = pygame.Rect(
                        width // 2 - button_width // 2,
                        start_y + i * (button_height + 20),
                        button_width,
                        button_height
                    )
                    if button_rect.collidepoint(event.pos):
                        self.selected_option = i
                        action = option.lower().replace(" ", "_")
                        if action == "start_new_run":
                            # Initialize new map tree run
                            self.map_state.initialize_new_run()
                            return "start_new_run"
                        elif action == "continue_run":
                            # Continue existing run or start new if none exists
                            if self.map_state.has_existing_run():
                                self.map_state.continue_existing_run()
                            else:
                                self.map_state.initialize_new_run()
                            return "continue_run"
                        elif action == "back_to_title":
                            return "back"

        # Check for mouse hover
        for i, option in enumerate(self.options):
            button_rect = pygame.Rect(
                width // 2 - button_width // 2,
                start_y + i * (button_height + 20),
                button_width,
                button_height
            )
            if button_rect.collidepoint(mouse_pos):
                self.selected_option = i
                break

        return None

    def draw(self, screen, width, height):
        """Draw the campaign menu."""
        # Cache background if needed
        if (self.background_surface is None or 
            self.background_width != width or 
            self.background_height != height):
            self.background_surface = self._create_factory_background(width, height)
            self.background_width = width
            self.background_height = height
        
        # Draw cached background
        screen.blit(self.background_surface, (0, 0))
        
        # Update visual effects (reduced frequency)
        self.warning_light_timer += 1/60
        if self.warning_light_timer > 2.0:  # Slower toggle
            self.warning_light_on = not self.warning_light_on
            self.warning_light_timer = 0
        
        # Update title animation (reduced intensity)
        self.title_glow_timer += 1/60
        self.title_pulse = 1.0 + 0.05 * math.sin(self.title_glow_timer)
        
        # Spawn and update steam particles (reduced)
        self._spawn_steam(width, height)
        dt = 1/60
        for particle in self.steam_particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.steam_particles.remove(particle)
        
        # Draw steam particles
        for particle in self.steam_particles:
            particle.draw(screen)
        
        # Simple warning light effect
        if self.warning_light_on:
            sign_positions = [(width // 4, height // 3), (3 * width // 4, height // 2.5)]
            for sign_x, sign_y in sign_positions:
                # Simple colored rectangle instead of complex glow
                light_rect = pygame.Rect(int(sign_x - 35), int(sign_y - 20), 70, 40)
                pygame.draw.rect(screen, RED_ACCENT, light_rect, 2)

        # Calculate layout
        scale_y = height / 600
        scale_x = width / 800
        scale = min(scale_x, scale_y)

        # Draw title with shadow effect
        title_font_size = max(24, int(56 * scale))
        title_font = get_pixel_font(title_font_size)
        
        title_text = "SELECT YOUR DESTINY"
        # Simple pulsing color
        red_intensity = int(220 * self.title_pulse)
        title_color = (red_intensity, 80, 70)
        
        title_x = width // 2
        title_y = height // 6
        
        # Draw shadow first (offset by 3 pixels down and right)
        shadow_offset = 3
        shadow_color = (25, 20, 18)  # Dark shadow using OIL_BLACK
        shadow_surface = title_font.render(title_text, True, shadow_color)
        shadow_x = title_x - shadow_surface.get_width() // 2 + shadow_offset
        shadow_y = title_y + shadow_offset
        screen.blit(shadow_surface, (shadow_x, shadow_y))
        
        # Draw main title text
        title_surface = title_font.render(title_text, True, title_color)
        main_title_x = title_x - title_surface.get_width() // 2
        screen.blit(title_surface, (main_title_x, title_y))

        # Draw menu options
        option_font_size = max(12, int(24 * scale_y))
        option_font = get_pixel_font(option_font_size)
        button_height = max(40, int(50 * scale_y))
        button_width = max(250, int(width * 0.35))
        
        title_bottom = title_y + title_surface.get_height()
        options_area_top = title_bottom + 80
        options_area_height = height - options_area_top - height // 8
        num_options = len(self.options)
        total_options_height = num_options * button_height + (num_options - 1) * 20
        start_y = options_area_top + (options_area_height - total_options_height) // 2

        mouse_pos = pygame.mouse.get_pos()

        for i, option in enumerate(self.options):
            button_rect = pygame.Rect(
                width // 2 - button_width // 2,
                start_y + i * (button_height + 20),
                button_width,
                button_height
            )
            is_selected = (i == self.selected_option)
            is_hovered = button_rect.collidepoint(mouse_pos)

            # Custom factory-themed button drawing
            self._draw_factory_button(screen, button_rect, option, option_font, is_selected or is_hovered)

    def _draw_factory_button(self, screen, rect, text, font, is_highlighted):
        """Draw a factory-themed button."""
        # Button base
        base_color = BRONZE_ACCENT if is_highlighted else DARK_BRONZE
        shadow_color = DARK_METAL
        
        # Draw shadow
        shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=4)
        
        # Draw main button
        pygame.draw.rect(screen, base_color, rect, border_radius=4)
        
        # Draw border/frame
        border_color = RED_ACCENT if is_highlighted else PIPE_BRONZE
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=4)
        
        # Add metallic highlight
        highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 3)
        highlight_color = (
            min(255, base_color[0] + 30),
            min(255, base_color[1] + 30),
            min(255, base_color[2] + 30)
        )
        pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=2)
        
        # Draw text
        text_color = TEXT_RED if is_highlighted else TEXT_BRONZE
        text_surface = font.render(text, True, text_color)
        text_pos = (
            rect.centerx - text_surface.get_width() // 2,
            rect.centery - text_surface.get_height() // 2
        )
        screen.blit(text_surface, text_pos)

    def display(self, screen, clock, width, height, debug_console=None):
        """Main loop for displaying and handling the campaign menu."""
        while True:
            events = pygame.event.get()
            action = self.handle_input(events, width, height)
            
            if action is not None:
                return action

            self.draw(screen, width, height)
            
            if debug_console and debug_console.visible:
                debug_console.draw(screen, width, height)

            pygame.display.flip()
            clock.tick(60)