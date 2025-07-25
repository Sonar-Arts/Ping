import pygame
import time
import random
import math # Added for lightning bolt generation
from sys import exit
from .Submodules.Ping_Settings import SettingsScreen
from .Submodules.Ping_Fonts import get_pixel_font

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40) # For clouds base
MID_GREY = (60, 60, 60) # For cloud detail
LIGHT_GREY = (100, 100, 100) # For city placeholder
RUIN_GREY_DARK = (50, 55, 60) # Darker city color
RUIN_GREY_LIGHT = (70, 75, 80) # Lighter city color
YELLOW = (255, 255, 0) # For lightning
LIGHTNING_GLOW = (200, 200, 255, 100) # Pale blue glow

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
        self.lightning_duration = 0.15 # Slightly longer flash
        self.lightning_active = False
        self.lightning_bolt = [] # Store points for the bolt
        self.lightning_glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.lightning_cooldown = random.uniform(2, 5) # Time between lightning strikes

        # Generate ruined city background
        self.city_surface = self._create_ruined_city(width, height)

        # Initialize clouds
        num_clouds = 10 # Fewer, but more detailed clouds
        for _ in range(num_clouds):
            self.add_cloud(initial=True)

    def _create_ruined_city(self, width, height):
        """Creates a surface with a more detailed, pixelated ruined city skyline."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((20, 20, 30, 255)) # Dark blue/grey sky base (ensure full alpha)

        pixel_size = 4 # Size of each 'pixel' block
        building_bottom = height

        # Enhanced color palette with more variety and depth
        BUILDING_COLORS = [
            (45, 50, 55), (55, 60, 65), (60, 65, 70),  # Dark buildings
            (70, 75, 80), (75, 80, 85), (80, 85, 90),  # Medium buildings
            (85, 90, 95), (65, 70, 85), (55, 65, 75)   # Lighter and tinted buildings
        ]
        
        # Enhanced window colors with more variety
        WINDOW_COLOR_UNLIT = (25, 25, 30)
        WINDOW_COLOR_LIT_WARM = (220, 200, 140)    # Warm yellow light
        WINDOW_COLOR_LIT_COOL = (140, 180, 220)    # Cool blue light
        WINDOW_COLOR_LIT_RED = (200, 120, 100)     # Emergency/red light
        WINDOW_COLOR_FLICKERING = (180, 160, 100)  # Dim/flickering light

        # Ensure skyline calculations are snapped to pixel grid
        skyline_height_base = round(height * 0.4 / pixel_size) * pixel_size
        skyline_height_variation = round(height * 0.2 / pixel_size) * pixel_size

        x = 0
        while x < width:
            # Create more architectural variety with different building types
            building_type = random.choice(['residential', 'office', 'industrial', 'mixed'])
            
            # Building dimensions based on type for more realistic architecture
            if building_type == 'residential':
                building_width = random.randrange(pixel_size * 10, pixel_size * 18 + 1, pixel_size)
                height_multiplier = random.uniform(0.8, 1.2)  # Medium height variation
            elif building_type == 'office':
                building_width = random.randrange(pixel_size * 12, pixel_size * 22 + 1, pixel_size)
                height_multiplier = random.uniform(1.1, 1.8)  # Taller buildings
            elif building_type == 'industrial':
                building_width = random.randrange(pixel_size * 15, pixel_size * 28 + 1, pixel_size)
                height_multiplier = random.uniform(0.6, 0.9)  # Wider, shorter buildings
            else:  # mixed
                building_width = random.randrange(pixel_size * 8, pixel_size * 20 + 1, pixel_size)
                height_multiplier = random.uniform(0.9, 1.4)
            
            building_height = int((skyline_height_base + random.randrange(-skyline_height_variation, skyline_height_variation // 2 + 1, pixel_size)) * height_multiplier)
            building_height = max(pixel_size * 6, building_height) # Slightly higher minimum
            building_top = building_bottom - building_height

            # Define the building's core rectangle (snapped to grid)
            building_rect = pygame.Rect(x, building_top, building_width, building_height)
            
            # Choose base color based on building type for more realistic variety
            if building_type == 'residential':
                base_color = random.choice([(55, 65, 70), (65, 70, 85), (60, 65, 70), (70, 75, 80)])
            elif building_type == 'office':
                base_color = random.choice([(70, 75, 80), (75, 80, 85), (80, 85, 90), (85, 90, 95)])
            elif building_type == 'industrial':
                base_color = random.choice([(45, 50, 55), (55, 60, 65), (50, 55, 60), (60, 65, 70)])
            else:  # mixed
                base_color = random.choice(BUILDING_COLORS)
            
            # Calculate distance-based darkening for depth (buildings further back are darker)
            distance_factor = min(1.0, x / (width * 0.7))  # Buildings get darker toward the back
            depth_modifier = int(distance_factor * 15)  # Up to 15 units darker
            base_color = (
                max(30, base_color[0] - depth_modifier),
                max(30, base_color[1] - depth_modifier), 
                max(30, base_color[2] - depth_modifier)
            )

            # --- Draw Building using Pixel Blocks with subtle gradient ---
            for px in range(building_rect.left, building_rect.right, pixel_size):
                for py in range(building_rect.top, building_rect.bottom, pixel_size):
                    # Add subtle vertical gradient (darker at bottom)
                    height_factor = (py - building_rect.top) / building_height
                    gradient_modifier = int(height_factor * 8)  # Up to 8 units darker at bottom
                    
                    # Add slight random color variation for texture
                    tex_color_mod = random.randint(-3, 3)
                    tex_color = (
                        max(0, min(255, base_color[0] + tex_color_mod - gradient_modifier)),
                        max(0, min(255, base_color[1] + tex_color_mod - gradient_modifier)),
                        max(0, min(255, base_color[2] + tex_color_mod - gradient_modifier))
                    )
                    pygame.draw.rect(surface, tex_color, (px, py, pixel_size, pixel_size))

            # --- Add Jagged/Detailed Top ---
            top_variation_range = pixel_size * 4
            for px in range(building_rect.left, building_rect.right, pixel_size):
                # Chance to add extra blocks above or remove blocks below
                top_mod = random.randrange(-top_variation_range, top_variation_range + 1, pixel_size)
                mod_y_start = building_rect.top + top_mod
                mod_y_end = building_rect.top

                if top_mod > 0: # Add blocks above
                    for py in range(mod_y_start, mod_y_end, -pixel_size):
                         pygame.draw.rect(surface, base_color, (px, py, pixel_size, pixel_size))
                elif top_mod < 0: # Remove blocks (draw sky color)
                     for py in range(mod_y_start, mod_y_end, pixel_size):
                          pygame.draw.rect(surface, (20, 20, 30, 255), (px, py, pixel_size, pixel_size))

            # --- Add Architectural Windows Based on Building Type ---
            # Adjust window patterns and lighting based on building type
            if building_type == 'residential':
                window_chance = 0.55  # Moderate window density
                window_spacing_x = pixel_size * 4  # Wider spacing for residential
                window_spacing_y = pixel_size * 5  # Taller spacing between floors
                light_chance_total = 0.06  # 6% total lit windows - more subtle
            elif building_type == 'office':
                window_chance = 0.75  # High window density for office buildings
                window_spacing_x = pixel_size * 3  # Closer spacing
                window_spacing_y = pixel_size * 4  # Regular floor spacing
                light_chance_total = 0.08  # 8% lit windows - late workers
            elif building_type == 'industrial':
                window_chance = 0.35  # Lower window density
                window_spacing_x = pixel_size * 5  # Wider industrial windows
                window_spacing_y = pixel_size * 6  # Taller industrial spaces
                light_chance_total = 0.04  # 4% lit windows - minimal lighting
            else:  # mixed
                window_chance = 0.60
                window_spacing_x = pixel_size * 3
                window_spacing_y = pixel_size * 4
                light_chance_total = 0.07  # 7% lit windows
            
            for wx in range(building_rect.left + pixel_size, building_rect.right - pixel_size * 2, window_spacing_x):
                for wy in range(building_rect.top + pixel_size * 2, building_rect.bottom - pixel_size * 3, window_spacing_y):
                    if random.random() < window_chance:
                        # Much more subtle lighting - reduced frequency across all types
                        light_chance = random.random()
                        if light_chance < light_chance_total:
                            # Distribute the reduced lighting across different types
                            relative_chance = light_chance / light_chance_total
                            if relative_chance < 0.6:  # 60% of lit windows are warm
                                win_color = WINDOW_COLOR_LIT_WARM
                            elif relative_chance < 0.85:  # 25% cool light
                                win_color = WINDOW_COLOR_LIT_COOL
                            elif relative_chance < 0.95:  # 10% red light  
                                win_color = WINDOW_COLOR_LIT_RED
                            else:  # 5% flickering
                                win_color = WINDOW_COLOR_FLICKERING
                        else:
                            win_color = WINDOW_COLOR_UNLIT
                        
                        # Draw windows with architectural variety
                        if building_type == 'office':
                            # Larger office windows
                            pygame.draw.rect(surface, win_color, (wx, wy, pixel_size * 2, pixel_size * 3))
                        elif building_type == 'industrial':
                            # Wide industrial windows
                            pygame.draw.rect(surface, win_color, (wx, wy, pixel_size * 3, pixel_size * 2))
                        else:
                            # Standard residential/mixed windows
                            pygame.draw.rect(surface, win_color, (wx, wy, pixel_size * 2, pixel_size * 2))
                        
                        # Add subtle window frame only for lit windows
                        if win_color != WINDOW_COLOR_UNLIT:
                            frame_color = (max(0, win_color[0] - 50), max(0, win_color[1] - 50), max(0, win_color[2] - 50))
                            # Very subtle frame
                            pygame.draw.rect(surface, frame_color, (wx - pixel_size//4, wy - pixel_size//4, 
                                           (pixel_size * 3 if building_type == 'industrial' else pixel_size * 2) + pixel_size//2, 
                                           (pixel_size * 3 if building_type == 'office' else pixel_size * 2) + pixel_size//2), pixel_size//4)

            # --- Add Building-Type Specific Rooftop Details ---
            rooftop_chance = random.random()
            rooftop_frequency = 0.30 if building_type == 'office' else 0.25 if building_type == 'industrial' else 0.20
            
            if rooftop_chance < rooftop_frequency:
                feature_x = random.randrange(building_rect.left + pixel_size * 2, building_rect.right - pixel_size * 3, pixel_size)
                
                # Building-type specific rooftop features
                if building_type == 'residential':
                    if rooftop_chance < 0.08:  # Chimney for residential
                        chimney_width = pixel_size * 2
                        chimney_height = pixel_size * 4
                        chimney_color = (65, 55, 50)  # Brick-like color
                        for cx in range(feature_x, feature_x + chimney_width, pixel_size):
                            for cy in range(building_rect.top - chimney_height, building_rect.top, pixel_size):
                                pygame.draw.rect(surface, chimney_color, (cx, cy, pixel_size, pixel_size))
                        # Chimney cap
                        cap_color = (75, 65, 60)
                        pygame.draw.rect(surface, cap_color, (feature_x - pixel_size//2, building_rect.top - chimney_height - pixel_size//2, chimney_width + pixel_size, pixel_size))
                    
                    elif rooftop_chance < 0.15:  # Small residential antenna
                        antenna_height = pixel_size * 5
                        antenna_color = (45, 45, 45)
                        for ay in range(building_rect.top - antenna_height, building_rect.top, pixel_size):
                            pygame.draw.rect(surface, antenna_color, (feature_x, ay, pixel_size, pixel_size))
                        # Simple crossbeam
                        pygame.draw.rect(surface, antenna_color, (feature_x - pixel_size, building_rect.top - antenna_height // 2, pixel_size * 3, pixel_size))
                
                elif building_type == 'office':
                    if rooftop_chance < 0.10:  # HVAC system for office
                        hvac_width = pixel_size * 5
                        hvac_height = pixel_size * 3
                        hvac_color = (60, 65, 70)
                        for hx in range(feature_x, feature_x + hvac_width, pixel_size):
                            for hy in range(building_rect.top - hvac_height, building_rect.top, pixel_size):
                                pygame.draw.rect(surface, hvac_color, (hx, hy, pixel_size, pixel_size))
                        # HVAC vents
                        vent_color = (50, 55, 60)
                        for vx in range(feature_x + pixel_size, feature_x + hvac_width - pixel_size, pixel_size * 2):
                            pygame.draw.rect(surface, vent_color, (vx, building_rect.top - pixel_size, pixel_size, pixel_size))
                    
                    elif rooftop_chance < 0.20:  # Communication array
                        array_height = pixel_size * 8
                        array_color = (55, 60, 65)
                        # Main support
                        for ay in range(building_rect.top - array_height, building_rect.top, pixel_size):
                            pygame.draw.rect(surface, array_color, (feature_x, ay, pixel_size, pixel_size))
                        # Multiple dishes
                        for dish_y in range(building_rect.top - array_height + pixel_size, building_rect.top - pixel_size, pixel_size * 3):
                            pygame.draw.rect(surface, array_color, (feature_x - pixel_size, dish_y, pixel_size * 3, pixel_size))
                
                elif building_type == 'industrial':
                    if rooftop_chance < 0.12:  # Industrial smokestack
                        stack_width = pixel_size * 2
                        stack_height = pixel_size * 8
                        stack_color = (45, 50, 55)
                        for sx in range(feature_x, feature_x + stack_width, pixel_size):
                            for sy in range(building_rect.top - stack_height, building_rect.top, pixel_size):
                                pygame.draw.rect(surface, stack_color, (sx, sy, pixel_size, pixel_size))
                        # Stack top/cap
                        cap_color = (55, 60, 65)
                        pygame.draw.rect(surface, cap_color, (feature_x - pixel_size//2, building_rect.top - stack_height - pixel_size, stack_width + pixel_size, pixel_size))
                    
                    elif rooftop_chance < 0.20:  # Industrial cooling unit
                        cooling_width = pixel_size * 6
                        cooling_height = pixel_size * 2
                        cooling_color = (50, 55, 60)
                        for cx in range(feature_x, feature_x + cooling_width, pixel_size):
                            for cy in range(building_rect.top - cooling_height, building_rect.top, pixel_size):
                                pygame.draw.rect(surface, cooling_color, (cx, cy, pixel_size, pixel_size))
                        # Cooling fins
                        fin_color = (40, 45, 50)
                        for fx in range(feature_x, feature_x + cooling_width, pixel_size * 2):
                            pygame.draw.rect(surface, fin_color, (fx, building_rect.top - cooling_height - pixel_size//2, pixel_size, pixel_size//2))
                
                else:  # mixed - water tower or general antenna
                    if rooftop_chance < 0.10:  # Water tower
                        tower_width = pixel_size * 3
                        tower_height = pixel_size * 6
                        tower_color = (60, 65, 70)
                        # Draw water tower base
                        for tx in range(feature_x, feature_x + tower_width, pixel_size):
                            for ty in range(building_rect.top - tower_height, building_rect.top - pixel_size * 2, pixel_size):
                                pygame.draw.rect(surface, tower_color, (tx, ty, pixel_size, pixel_size))
                        # Draw water tower tank (top part)
                        tank_color = (70, 75, 80)
                        for tx in range(feature_x - pixel_size//2, feature_x + tower_width + pixel_size//2, pixel_size):
                            for ty in range(building_rect.top - tower_height - pixel_size * 2, building_rect.top - tower_height, pixel_size):
                                pygame.draw.rect(surface, tank_color, (tx, ty, pixel_size, pixel_size))

            # --- Apply Enhanced Damage (Remove larger chunks with better patterns) ---
            damage_intensity = random.choice([0, 1, 2, 3, 4])  # More variation in damage
            if damage_intensity > 0:
                damage_zone_height = building_height * 0.7 # Apply damage to more of the building
                damage_zone_top = building_rect.top

                for _ in range(damage_intensity):
                    # More varied chunk sizes based on damage type
                    if random.random() < 0.3:  # Large blast damage
                        chunk_w = random.randrange(pixel_size * 6, pixel_size * 12 + 1, pixel_size)
                        chunk_h = random.randrange(pixel_size * 6, pixel_size * 12 + 1, pixel_size)
                    else:  # Small debris damage
                        chunk_w = random.randrange(pixel_size * 2, pixel_size * 6 + 1, pixel_size)
                        chunk_h = random.randrange(pixel_size * 2, pixel_size * 6 + 1, pixel_size)

                    # Enhanced positioning with more realistic damage patterns
                    max_y = damage_zone_top + damage_zone_height - chunk_h
                    
                    # Create more realistic damage clustering
                    if random.random() < 0.4:  # 40% chance for top damage (explosions from above)
                        chunk_y = random.triangular(damage_zone_top, damage_zone_top + damage_zone_height * 0.3, damage_zone_top)
                    else:  # Random damage throughout
                        chunk_y = random.uniform(damage_zone_top, max_y)
                    chunk_y = round(chunk_y / pixel_size) * pixel_size

                    # Enhanced edge bias for more realistic structural damage
                    max_x = building_rect.right - chunk_w
                    edge_bias = random.random()
                    if edge_bias < 0.4:  # Left edge bias
                        chunk_x = random.triangular(building_rect.left, building_rect.left + building_width * 0.3, building_rect.left)
                    elif edge_bias < 0.8:  # Right edge bias  
                        chunk_x = random.triangular(building_rect.right - building_width * 0.3, max_x, max_x)
                    else:  # Center damage
                        chunk_x = random.uniform(building_rect.left + building_width * 0.2, building_rect.right - building_width * 0.2 - chunk_w)
                    chunk_x = round(chunk_x / pixel_size) * pixel_size

                    # Ensure chunk is within building bounds
                    chunk_x = max(building_rect.left, min(chunk_x, building_rect.right - chunk_w))
                    chunk_y = max(damage_zone_top, min(chunk_y, damage_zone_top + damage_zone_height - chunk_h))

                    # Draw sky color to 'remove' the chunk
                    damage_rect = pygame.Rect(chunk_x, chunk_y, chunk_w, chunk_h)
                    pygame.draw.rect(surface, (20, 20, 30, 255), damage_rect)
                    
                    # Add debris/rubble effect around damage
                    if random.random() < 0.6:  # 60% chance for debris
                        debris_color = (max(15, base_color[0] - 20), max(15, base_color[1] - 20), max(15, base_color[2] - 20))
                        debris_x = chunk_x + random.randrange(-pixel_size, chunk_w + pixel_size, pixel_size)
                        debris_y = min(building_rect.bottom - pixel_size, chunk_y + chunk_h)
                        if building_rect.left <= debris_x < building_rect.right:
                            pygame.draw.rect(surface, debris_color, (debris_x, debris_y, pixel_size, pixel_size))


            # Move to next building position (ensure some gap/overlap, snapped)
            x += building_width + random.randrange(-pixel_size * 2, pixel_size * 4 + 1, pixel_size)

        return surface

    def add_cloud(self, initial=True):
        num_puffs = random.randint(3, 7) # Number of ellipses per cloud
        
        # Ensure new clouds start completely off-screen to prevent edge sticking
        if initial:
            base_x = random.randint(-150, self.width)
        else:
            # For replacement clouds, start them well off-screen right
            base_x = self.width + random.randint(100, 200)  # Larger buffer to prevent edge sticking
            
        base_y = random.randint(0, int(self.height * 0.5)) # Clouds in upper 50%
        speed = random.uniform(30, 80) # Increased speed range to ensure reliable movement
        base_color = (random.randint(30, 50), random.randint(30, 50), random.randint(35, 55)) # Darker greys base
        detail_color = (base_color[0]+15, base_color[1]+15, base_color[2]+15) # Slightly lighter detail

        cloud_puffs = []
        min_puff_x = base_x # Track the leftmost point for reset logic
        max_puff_right = base_x # Track the rightmost point for reset logic

        for i in range(num_puffs):
            # Make puffs more blocky/pixelated - use larger steps for size
            puff_w = random.randrange(40, 101, 8) # Widths in steps of 8
            puff_h = random.randrange(32, 71, 8) # Heights in steps of 8
            # Offset puffs relative to the base_x, base_y, snap offsets
            offset_x = random.randrange(-32, 33, 8) * i // 2
            offset_y = random.randrange(-24, 25, 8)
            # Ensure coordinates are integers for rects
            puff_x = int(base_x + offset_x)
            puff_y = int(base_y + offset_y)
            puff_rect = pygame.Rect(puff_x, puff_y, puff_w, puff_h)
            cloud_puffs.append({
                'rect': puff_rect,
                'color': random.choice([base_color, detail_color]) # Mix colors for texture
            })
            min_puff_x = min(min_puff_x, puff_rect.left)
            max_puff_right = max(max_puff_right, puff_rect.right)

        self.clouds.append({
            'puffs': cloud_puffs,
            'speed': speed,
            'base_x': base_x, # Store original base_x for reset calculation
            'base_y': base_y,
            # Use min/max calculated coords for more accurate reset logic
            'min_x': min_puff_x,
            'max_right': max_puff_right,
            'min_left': min_puff_x  # Add this for consistency with update method
        })

    def _generate_lightning_bolt(self, start_pos, end_y):
        """Generates a list of points for a pixelated lightning bolt."""
        points = [start_pos]
        current_pos = list(start_pos)
        # Increased deviation for a more jagged look, step size for pixelation
        max_deviation = 30
        segment_length = random.randrange(8, 25, 4) # Vertical segment length (pixelated steps)
        pixel_size = 4 # Controls the blockiness

        while current_pos[1] < end_y:
            # Calculate next y position with pixel steps
            next_y = current_pos[1] + segment_length
            next_y = min(end_y, next_y) # Don't go past the target end_y

            # Calculate next x position with deviation and pixel steps
            deviation = random.randrange(-max_deviation, max_deviation + 1, pixel_size)
            next_x = current_pos[0] + deviation
            # Clamp x within screen bounds slightly, aligned to pixel grid
            next_x = max(pixel_size, min(self.width - pixel_size, next_x))
            next_x = round(next_x / pixel_size) * pixel_size

            points.append((next_x, next_y))
            current_pos = [next_x, next_y]
            segment_length = random.randrange(8, 25, 4) # New length for next segment

            # Chance to fork (less frequent for cleaner look maybe)
            if random.random() < 0.10 and len(points) > 2:
                 # Forks also generate pixelated bolts
                 fork_end_y = end_y + random.randint(-30, 60)
                 fork_points = self._generate_lightning_bolt(current_pos, fork_end_y)
                 points.append(None) # Separator
                 points.extend(fork_points[1:])

        return points

    def update(self, dt):
        # Move clouds
        clouds_to_reset = []
        for i, cloud in enumerate(self.clouds):
            # Force integer pixel movement to ensure clouds always move
            raw_dx = cloud['speed'] * dt
            dx = max(1, int(raw_dx + 0.5))  # Round to nearest integer, minimum 1 pixel
            
            cloud['base_x'] -= dx
            current_max_right = -float('inf') 
            current_min_left = float('inf')
            
            for puff in cloud['puffs']:
                puff['rect'].x -= dx
                current_max_right = max(current_max_right, puff['rect'].right)
                current_min_left = min(current_min_left, puff['rect'].left)

            # Update the stored boundaries for the cloud
            cloud['max_right'] = current_max_right
            cloud['min_left'] = current_min_left

            # Reset cloud if completely off-screen (with generous buffer)
            if current_max_right < -50:
                clouds_to_reset.append(i)

        # Remove and re-add clouds that went off-screen
        for i in sorted(clouds_to_reset, reverse=True):
            if i < len(self.clouds):
                self.clouds.pop(i)
                self.add_cloud(initial=False)

        # Lightning logic (mostly unchanged, relies on updated _generate_lightning_bolt and draw)
        if self.lightning_active:
            self.lightning_timer -= dt
            if self.lightning_timer <= 0:
                self.lightning_active = False
                self.lightning_bolt = [] # Clear the bolt path
                self.lightning_glow_surface.fill((0, 0, 0, 0)) # Clear glow
        else:
            self.lightning_cooldown -= dt
            if self.lightning_cooldown <= 0:
                self.lightning_active = True
                self.lightning_timer = self.lightning_duration
                self.lightning_bolt = []

                if self.clouds:
                    strike_cloud = random.choice(self.clouds)
                    # Find the lowest, central point of the chosen cloud more accurately
                    origin_x = 0
                    origin_y = 0
                    lowest_y = 0
                    puff_centers_x = []
                    for puff in strike_cloud['puffs']:
                        lowest_y = max(lowest_y, puff['rect'].bottom)
                        puff_centers_x.append(puff['rect'].centerx)
                    # Use average center x of puffs for origin x
                    if puff_centers_x:
                        origin_x = sum(puff_centers_x) / len(puff_centers_x)
                    origin_y = lowest_y # Start from the bottom of the lowest puff
                    start_pos = (int(origin_x), int(origin_y)) # Ensure integer coords

                    target_y = self.height
                    city_hit_y = self.city_surface.get_height() * 0.7
                    if start_pos[1] < city_hit_y:
                        target_y = random.randint(int(city_hit_y), self.height)

                    self.lightning_bolt = self._generate_lightning_bolt(start_pos, target_y)

                else: # Fallback
                     start_pos = (random.randint(0, self.width), random.randint(0, int(self.height * 0.5)))
                     self.lightning_bolt = self._generate_lightning_bolt(start_pos, self.height)

                self.lightning_cooldown = random.uniform(3, 8)

                # Prepare glow effect (unchanged)
                if self.lightning_bolt:
                    valid_points = [p for p in self.lightning_bolt if p]
                    if valid_points:
                        avg_x = sum(p[0] for p in valid_points) / len(valid_points)
                        avg_y = sum(p[1] for p in valid_points) / len(valid_points)
                        glow_radius = random.randint(150, 300)
                        glow_center = (int(avg_x), int(avg_y))
                        # Draw radial gradient for glow (simplified)
                        max_alpha = 150
                        self.lightning_glow_surface.fill((0, 0, 0, 0)) # Clear previous glow before drawing new one
                        for r in range(glow_radius, 0, -5):
                            alpha = int(max_alpha * (1 - r / glow_radius)**2) # Use squared falloff for better look
                            current_glow_color = LIGHTNING_GLOW[:3] + (alpha,)
                            pygame.draw.circle(self.lightning_glow_surface, current_glow_color, glow_center, r)

    def draw(self, screen):
        # Draw city background first
        screen.blit(self.city_surface, (0, 0))

        # Draw clouds (using rects for pixelated look)
        pixel_size = 8 # Increased pixel size for more noticeable pixelation
        for cloud in self.clouds:
            for puff in cloud['puffs']:
                # --- Draw Pixelated Round Puff ---
                puff_rect = puff['rect']
                puff_color = puff['color']
                center_x = puff_rect.centerx
                center_y = puff_rect.centery
                radius_x = puff_rect.width / 2
                radius_y = puff_rect.height / 2

                # Iterate through the bounding box of the puff in pixel_size steps
                for x in range(puff_rect.left, puff_rect.right, pixel_size):
                    for y in range(puff_rect.top, puff_rect.bottom, pixel_size):
                        # Calculate the center of the current pixel block
                        pixel_center_x = x + pixel_size / 2
                        pixel_center_y = y + pixel_size / 2

                        # Check if the pixel center is within the ellipse defined by the puff's rect
                        # Ellipse equation: ((px - cx)/rx)^2 + ((py - cy)/ry)^2 <= 1
                        norm_x = (pixel_center_x - center_x) / radius_x if radius_x > 0 else 0
                        norm_y = (pixel_center_y - center_y) / radius_y if radius_y > 0 else 0

                        if norm_x**2 + norm_y**2 <= 1:
                            # Draw the pixel block
                            pygame.draw.rect(screen, puff_color, (x, y, pixel_size, pixel_size))
                # --- End Pixelated Round Puff ---

        # Draw lightning flash (glow + pixelated bolt)
        if self.lightning_active:
            screen.blit(self.lightning_glow_surface, (0, 0))

            # Draw the lightning bolt using pixel-sized rects or thick lines
            pixel_size = 4 # Size of the 'pixels' for the bolt
            if len(self.lightning_bolt) > 1:
                start_point = self.lightning_bolt[0]
                for i in range(1, len(self.lightning_bolt)):
                    end_point = self.lightning_bolt[i]
                    if start_point and end_point:
                        dx = end_point[0] - start_point[0]
                        dy = end_point[1] - start_point[1]
                        distance = max(abs(dx), abs(dy))
                        if distance == 0: distance = 1 # Avoid division by zero

                        for j in range(0, int(distance), pixel_size // 2): # Step along the line
                            t = j / distance
                            x = start_point[0] + t * dx
                            y = start_point[1] + t * dy
                            # Center the rect on the interpolated point
                            px = int(x - pixel_size / 2)
                            py = int(y - pixel_size / 2)
                            # Snap to grid
                            px = round(px / pixel_size) * pixel_size
                            py = round(py / pixel_size) * pixel_size

                            # Draw white core rect
                            pygame.draw.rect(screen, WHITE, (px, py, pixel_size, pixel_size))

                    start_point = end_point # Move to next segment

from .Submodules.Ping_MainMenu import MainMenu
from .Submodules.Ping_QuickPlayMenu import QuickPlayMenu
from .Submodules.Ping_Pause import PauseMenu
from .Submodules.Ping_LevelSelect import LevelSelect
from .Submodules.Ping_Fonts import get_pixel_font
from .Submodules.Ping_Button import get_button

def init_display(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, flags=0):
    """Initialize the display with the given dimensions and flags."""
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE | flags)
    pygame.display.set_caption("Ping")
    return screen

# Added sound_manager parameter, removed paddle_sound, score_sound
def settings_screen(screen, clock, sound_manager, WINDOW_WIDTH, WINDOW_HEIGHT, in_game=False, debug_console=None):
    """Display the settings screen."""
    settings = SettingsScreen()
    # Pass sound_manager to the display method (will require updating SettingsScreen.display)
    return settings.display(screen, clock, sound_manager, WINDOW_WIDTH, WINDOW_HEIGHT, in_game, debug_console)

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
        self.quick_play_menu = QuickPlayMenu(sound_manager) # Add Quick Play menu
        self.background = None
        self.current_menu = "main"  # Track current menu state

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
                # Update the console first to handle toggle key press, etc.
                processed_by_console = debug_console.update(events)

                # Now check visibility for other potential console-specific logic (if any)
                if debug_console.visible:
                    # If the console processed an event (like Enter for command),
                    # we might want to prevent the menu from processing it too.
                    # Currently, update() returns True if it handled the toggle,
                    # but doesn't indicate other event consumption.
                    # For now, we'll assume the menu can still process events.
                    pass

            # Filter out events potentially consumed by the console if needed
            # (Requires debug_console.update to return more info or modify events list)
            # Example: events = [e for e in events if not processed_by_console]

            # Handle input based on current menu
            if self.current_menu == "main":
                menu_action = self.menu.handle_input(events, WINDOW_WIDTH, WINDOW_HEIGHT)
                
                if menu_action == "quit":
                    pygame.quit()
                    exit()
                elif menu_action == "quick_play":
                    self.current_menu = "quick_play"
                elif menu_action == "campaign":
                    # Campaign does nothing for now, just stay on main menu
                    pass
                elif menu_action is not None:  # Settings or other actions
                    return menu_action
            
            elif self.current_menu == "quick_play":
                quick_play_action = self.quick_play_menu.handle_input(events, WINDOW_WIDTH, WINDOW_HEIGHT)
                
                if quick_play_action == "back":
                    self.current_menu = "main"
                elif quick_play_action is not None:  # True for 1P, False for 2P
                    self.menu.sound_manager.stop_music()  # Stop music when starting game
                    return quick_play_action

            # Draw appropriate background and menu
            if self.current_menu == "main":
                self.background.update(dt)
                self.background.draw(screen)
                self.menu.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)
            elif self.current_menu == "quick_play":
                self.quick_play_menu.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

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