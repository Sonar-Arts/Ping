"""
Module for handling game graphics, specifically level backgrounds.
"""

import pygame
import random
import math
import pygame # Ensure pygame is imported if not already

import os # Needed for path manipulation
import time # Import time for blinking animation

# Global cache for loaded sprite images
# Key: relative path (e.g., "MySprite.png"), Value: pygame.Surface
sprite_cache = {}
SPRITE_BASE_PATH = "Ping Assets/Images/Sprites/" # Base path for sprites

def load_sprite_image(relative_path):
    """
    Loads a sprite image, caches it, and handles transparency.

    Args:
        relative_path (str): The filename of the sprite relative to SPRITE_BASE_PATH.

    Returns:
        pygame.Surface or None: The loaded sprite surface with alpha, or None if loading fails.
    """
    if relative_path in sprite_cache:
        return sprite_cache[relative_path]

    full_path = os.path.join(SPRITE_BASE_PATH, relative_path)

    try:
        # Ensure the sprite directory exists before trying to load from it.
        # This is mainly a check; loading will still fail if the *file* is missing.
        if not os.path.isdir(SPRITE_BASE_PATH):
             print(f"Warning: Sprite base directory not found: {SPRITE_BASE_PATH}")
             return None

        if not os.path.exists(full_path):
            print(f"Warning: Sprite image file not found: {full_path}")
            return None

        image = pygame.image.load(full_path)
        image = image.convert_alpha() # Optimize for drawing with transparency
        sprite_cache[relative_path] = image
        print(f"Loaded and cached sprite: {relative_path}") # Debug print
        return image
    except pygame.error as e:
        print(f"Error loading sprite '{full_path}': {e}")
        return None
    except FileNotFoundError: # Should be caught by os.path.exists, but just in case
        print(f"Error: Sprite file not found (FileNotFoundError): {full_path}")
        return None
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred loading sprite '{full_path}': {e}")
        return None
# --- Texture Generation Function ---

def generate_sludge_texture(width, height, scale, colors):
    """
    Generates a single tileable sludge texture surface.
    This function is designed to be called potentially in a separate thread.

    Args:
        width (int): The desired width of the texture surface.
        height (int): The desired height of the texture surface.
        scale (float): The current game scale factor.
        colors (dict): Dictionary containing color definitions (SLUDGE_MID, SLUDGE_HIGHLIGHT).

    Returns:
        pygame.Surface: A Pygame surface containing the generated sludge pattern,
                      with transparency. Returns None if width or height is invalid.
    """
    if width <= 0 or height <= 0:
        return None # Invalid dimensions

    # Ensure dimensions are integers
    tex_width = int(width)
    tex_height = int(height)

    # Create the surface for the texture
    sludge_texture = pygame.Surface((tex_width, tex_height), pygame.SRCALPHA)
    sludge_texture.fill((0, 0, 0, 0)) # Fill with fully transparent

    # Define colors (extract from passed dictionary - slightly darker defaults for murkier look)
    sludge_mid_color_rgb = colors.get('SLUDGE_MID', (70, 75, 50)) # Darker mid
    sludge_highlight_color_rgb = colors.get('SLUDGE_HIGHLIGHT', (90, 95, 65)) # Darker highlight

    # Determine base size and number of blobs based on scale and area
    blob_base_radius = max(1, int(10 * scale)) # Base size of sludge blobs
    # Calculate number of vertical steps needed to cover the texture height
    # Draw slightly more to ensure coverage when wrapping/seeding
    num_vertical_steps = int(tex_height / (blob_base_radius * 0.5)) + 5

    for i in range(num_vertical_steps):
        # Calculate base y position for this 'row' of blobs
        y_base_logical = (i * blob_base_radius * 0.5)
        # Use modulo for seeding consistency across texture generation calls if needed,
        # but here we just need a consistent pattern within *this* texture.
        y_seed_pos = y_base_logical % tex_height

        # Calculate how many blobs to draw horizontally
        num_blobs_per_row = int(tex_width / (blob_base_radius * 1.5)) + 1

        for j in range(num_blobs_per_row * 2): # Draw double for overlap
            # Seed randomness based on vertical position and horizontal index
            # Ensures the generated texture is consistent if parameters are the same
            random.seed(f"{y_seed_pos:.2f}-{j}")

            # Randomize blob properties
            blob_radius = max(1, int(blob_base_radius * random.uniform(0.6, 1.6)))
            x_pos = random.uniform(0, tex_width)
            y_pos = y_base_logical # Draw relative to the logical y base for this step

            # Choose base color and alpha (reduced alpha range for murkier blend)
            base_color_rgb = random.choice([sludge_mid_color_rgb, sludge_highlight_color_rgb, sludge_mid_color_rgb])
            alpha = random.randint(60, 140) # Lower max alpha
            final_color = (base_color_rgb[0], base_color_rgb[1], base_color_rgb[2], alpha)

            # Draw the blob onto the texture surface
            draw_x = int(x_pos)
            # Wrap the drawing y-position onto the texture surface
            draw_y = int(y_pos % tex_height)
            draw_radius = int(blob_radius)
            if draw_radius > 0:
                pygame.draw.circle(sludge_texture, final_color, (draw_x, draw_y), draw_radius)

    return sludge_texture


# Helper function to generate points along an arc for pixelated look
def get_arc_points(center_x, center_y, radius_x, radius_y, start_angle, end_angle, num_segments):
    """ Calculates points along an elliptical arc segment. Angles in radians. """
    points = []
    # Ensure num_segments is at least 1 to avoid division by zero
    num_segments = max(1, num_segments)
    angle_step = (end_angle - start_angle) / num_segments
    for i in range(num_segments + 1):
        angle = start_angle + i * angle_step
        x = center_x + radius_x * math.cos(angle)
        y = center_y + radius_y * math.sin(angle)
        points.append((x, y))
    return points

def draw_casino_background(surface, compiler_instance):
    """
    Draws a pixelated, dark retro pinball background (v4).
    Features dark base, pixelated curved lanes with borders, corner lights, details.
    Retrieves necessary parameters from the compiler_instance.

    Args:
        surface: The pygame surface to draw onto.
        compiler_instance: The LevelCompiler instance containing level data,
                           colors, scale, offsets, objects, and state.
    """
    # --- Extract parameters ---
    colors = compiler_instance.colors
    scale = compiler_instance.scale
    scale_rect_func = compiler_instance.scale_rect
    scoreboard_height = compiler_instance.scoreboard_height
    arena_width = compiler_instance.width
    arena_height = compiler_instance.height
    dt = getattr(compiler_instance, 'dt', 1/60.0)
    center_x_logic = arena_width / 2

    # --- Get Lighting Properties ---
    level_properties = getattr(compiler_instance, 'level_properties', {})
    has_lighting = level_properties.get('has_lighting', False)
    lighting_level = level_properties.get('lighting_level', 75) # Default 75%

    # --- Define Pixelated Retro Pinball Colors ---
    base_color = colors.get('PINBALL_BASE', (10, 5, 25))          # Even Darker Blue/Purple
    lane_color = colors.get('PINBALL_LANE', (0, 200, 255))        # Bright Cyan
    lane_border_color = colors.get('LANE_BORDER', (5, 5, 5))      # Near Black border
    light_off_color = colors.get('PINBALL_LIGHT_OFF', (25, 15, 50)) # Dimmer Base Color
    wood_border_color = colors.get('WOOD_BORDER', (85, 55, 30))  # Dark Brown
    detail_color = colors.get('PINBALL_DETAIL', (40, 30, 65))    # Subtle detail color
    light_colors = [
        colors.get('PINBALL_LIGHT_1', (255, 255, 100)),  # Soft Yellow
        colors.get('PINBALL_LIGHT_2', (255, 50, 50)),    # Soft Red
        colors.get('PINBALL_LIGHT_3', (100, 255, 255)),  # Soft Cyan
        colors.get('PINBALL_LIGHT_4', (255, 100, 255)),  # Soft Magenta
    ]

    # --- Define Layout Parameters ---
    inner_x_start_logic = 0 # Start from edge
    inner_y_start_logic = 0 # Logical Y for playable area starts at 0
    inner_width_logic = arena_width # Use full logical width
    inner_height_logic = arena_height # Use full logical playable height (compiler_instance.height)
    inner_center_x_logic = inner_x_start_logic + inner_width_logic / 2

    # --- Get the game area rectangle ---
    # Use scale_rect_func to get the position of the game area on screen
    game_area_rect = scale_rect_func(pygame.Rect(0, 0, arena_width, arena_height))

    # --- Draw Base Background and Retro Details ---
    # Draw the base color covering the game area
    pygame.draw.rect(surface, base_color, game_area_rect)

    # Add subtle grid lines for more retro detail
    grid_spacing_logic = 50 # Logical pixels between grid lines
    scaled_grid_spacing = max(1, int(grid_spacing_logic * scale))
    grid_color = (base_color[0]+10, base_color[1]+10, base_color[2]+15, 50) # Slightly lighter, semi-transparent

    # Vertical lines - only within game area
    for x in range(game_area_rect.left, game_area_rect.right, scaled_grid_spacing):
        pygame.draw.line(surface, grid_color, (x, game_area_rect.top), (x, game_area_rect.bottom), 1)
    # Horizontal lines - only within game area
    for y in range(game_area_rect.top, game_area_rect.bottom, scaled_grid_spacing):
        pygame.draw.line(surface, grid_color, (game_area_rect.left, y), (game_area_rect.right, y), 1)

    # --- Initialize/Update Animation State ---
    if 'background_animation_state' not in compiler_instance.__dict__:
         compiler_instance.background_animation_state = {}
    anim_state = compiler_instance.background_animation_state

    num_lights = 8 # 2 per corner
    light_radius_logic = inner_width_logic * 0.008 # Even smaller lights

    # Check if lights need initialization or recalculation due to dimension change
    recalculate_lights = False
    if 'pinball_lights' not in anim_state:
        recalculate_lights = True
        anim_state['pinball_lights'] = [] # Initialize the list
        anim_state['pinball_lights_last_dims'] = (0, 0) # Initialize stored dimensions
    elif anim_state.get('pinball_lights_last_dims') != (arena_width, arena_height):
        recalculate_lights = True
        print(f"Casino BG: Dimensions changed from {anim_state.get('pinball_lights_last_dims')} to {(arena_width, arena_height)}. Recalculating light positions.")

    if recalculate_lights:
        # Store the current dimensions used for calculation
        anim_state['pinball_lights_last_dims'] = (arena_width, arena_height)

        # Define symmetrical positions near the four corners
        corner_offset_x = 0.15 # Relative offset from corner edge
        corner_offset_y = 0.15
        corner_spread = 0.06 # Spread between the two lights in a corner
        relative_light_positions = [
            # Top Left
            (corner_offset_x, corner_offset_y), (corner_offset_x + corner_spread, corner_offset_y + corner_spread),
            # Top Right
            (1.0 - corner_offset_x, corner_offset_y), (1.0 - (corner_offset_x + corner_spread), corner_offset_y + corner_spread),
            # Bottom Left
            (corner_offset_x, 1.0 - corner_offset_y), (corner_offset_x + corner_spread, 1.0 - (corner_offset_y + corner_spread)),
            # Bottom Right
            (1.0 - corner_offset_x, 1.0 - corner_offset_y), (1.0 - (corner_offset_x + corner_spread), 1.0 - (corner_offset_y + corner_spread)),
        ]
        relative_light_positions = relative_light_positions[:num_lights]

        # Clear existing light data if recalculating positions but keeping state
        if len(anim_state['pinball_lights']) == num_lights:
            # Update existing light positions
            for i, (rel_x, rel_y) in enumerate(relative_light_positions):
                abs_x = inner_x_start_logic + inner_width_logic * rel_x
                abs_y = inner_y_start_logic + inner_height_logic * rel_y
                anim_state['pinball_lights'][i]['pos_logic'] = (abs_x, abs_y)
        else:
            # Initialize new light data (if list was empty or wrong size)
            anim_state['pinball_lights'] = [] # Clear completely if size mismatch
            for i, (rel_x, rel_y) in enumerate(relative_light_positions):
                abs_x = inner_x_start_logic + inner_width_logic * rel_x
                abs_y = inner_y_start_logic + inner_height_logic * rel_y
                anim_state['pinball_lights'].append({
                    "id": i, "pos_logic": (abs_x, abs_y),
                    "on": random.choice([True, False, False]),
                    "timer": random.uniform(0, 1.0),
                    "interval": random.uniform(0.8, 2.0),
                    "color_index": random.randint(0, len(light_colors) - 1)
                })

    # Update light timers and states (this happens every frame regardless of recalculation)
    for light in anim_state['pinball_lights']:
        light['timer'] += dt
        if light['timer'] >= light['interval']:
            light['timer'] %= light['interval']
            light['on'] = not light['on']
            if light['on']:
                 light['color_index'] = random.randint(0, len(light_colors) - 1)

    # --- Draw Small Details ---
    detail_radius_logic = inner_width_logic * 0.005
    scaled_detail_radius = max(1, int(detail_radius_logic * scale))
    detail_positions_relative = [
        (0.5, 0.1), (0.5, 0.9), # Center top/bottom
        (0.2, 0.5), (0.8, 0.5), # Mid left/right
        (0.3, 0.2), (0.7, 0.2), # Upper mid
        (0.3, 0.8), (0.7, 0.8), # Lower mid
        # Add more details
        (0.4, 0.3), (0.6, 0.3),
        (0.4, 0.7), (0.6, 0.7),
    ]
    for rel_x, rel_y in detail_positions_relative:
         abs_x = inner_x_start_logic + inner_width_logic * rel_x
         abs_y = inner_y_start_logic + inner_height_logic * rel_y
         scaled_center = scale_rect_func(pygame.Rect(abs_x, abs_y, 0, 0)).center
         pygame.draw.circle(surface, detail_color, scaled_center, scaled_detail_radius)

    # --- Draw Pixelated Curved Lane Guides with Shadows ---
    num_segments = 12 # Increase segments slightly for smoother pixel curve
    lane_thickness_logic = inner_width_logic * 0.018 # Make lanes thicker
    border_thickness_logic_lane = lane_thickness_logic * 1.5 # Border slightly thicker
    shadow_offset_scale = 0.002 # How far to offset the shadow
    shadow_color = (5, 5, 15, 150) # Dark semi-transparent shadow

    # Define arc parameters (smaller and more centered)
    arc_center_y = inner_y_start_logic + inner_height_logic * 0.50 # Center vertically
    arc_radius_x = inner_width_logic * 0.18 # Make curves narrower
    arc_radius_y = inner_height_logic * 0.4 # Make curves shorter

    # Left Curve
    start_angle_left = math.pi * 0.75 # Start higher
    end_angle_left = math.pi * 1.25 # End lower
    center_left_x = inner_center_x_logic - inner_width_logic * 0.10 # Shift center less left

    # Right Curve (Symmetrical)
    start_angle_right = math.pi * 0.25 # Start higher
    end_angle_right = math.pi * -0.25 # End lower (equiv 1.75pi)
    center_right_x = inner_center_x_logic + inner_width_logic * 0.10 # Shift center less right

    # Generate points using helper function
    left_curve_points = get_arc_points(center_left_x, arc_center_y, arc_radius_x, arc_radius_y, start_angle_left, end_angle_left, num_segments)
    right_curve_points = get_arc_points(center_right_x, arc_center_y, arc_radius_x, arc_radius_y, start_angle_right, end_angle_right, num_segments)

    # Scale points
    scaled_left_points = [scale_rect_func(pygame.Rect(p[0], p[1], 0, 0)).center for p in left_curve_points]
    scaled_right_points = [scale_rect_func(pygame.Rect(p[0], p[1], 0, 0)).center for p in right_curve_points]

    # Draw lines (shadow, then border, then main color)
    scaled_border_thickness = max(2, int(border_thickness_logic_lane * scale))
    scaled_lane_thickness = max(1, int(lane_thickness_logic * scale))
    scaled_shadow_thickness = max(3, int(scaled_border_thickness * 1.2)) # Shadow slightly thicker
    scaled_shadow_offset_x = max(1, int(arena_width * shadow_offset_scale * scale))
    scaled_shadow_offset_y = max(1, int(arena_height * shadow_offset_scale * scale))

    # Create a temporary surface for drawing shadows with alpha
    shadow_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    shadow_surface.fill((0,0,0,0)) # Transparent

    if len(scaled_left_points) > 1:
        # Shadow (offset down-right for left curve)
        shadow_points_left = [(p[0] + scaled_shadow_offset_x, p[1] + scaled_shadow_offset_y) for p in scaled_left_points]
        pygame.draw.lines(shadow_surface, shadow_color, False, shadow_points_left, scaled_shadow_thickness)
        # Border
        pygame.draw.lines(surface, lane_border_color, False, scaled_left_points, scaled_border_thickness)
        # Lane
        pygame.draw.lines(surface, lane_color, False, scaled_left_points, scaled_lane_thickness)

    if len(scaled_right_points) > 1:
        # Shadow (offset down-left for right curve)
        shadow_points_right = [(p[0] - scaled_shadow_offset_x, p[1] + scaled_shadow_offset_y) for p in scaled_right_points]
        pygame.draw.lines(shadow_surface, shadow_color, False, shadow_points_right, scaled_shadow_thickness)
        # Border
        pygame.draw.lines(surface, lane_border_color, False, scaled_right_points, scaled_border_thickness)
        # Lane
        pygame.draw.lines(surface, lane_color, False, scaled_right_points, scaled_lane_thickness)

    # Blit the shadow surface onto the main surface
    surface.blit(shadow_surface, (0, 0))

    # --- Draw Animated Lights (Glassy/Shining Effect) ---
    scaled_light_radius = max(1, int(light_radius_logic * scale)) # Base radius
    glass_radius = max(2, int(scaled_light_radius * 1.5)) # Outer glass slightly larger
    inner_light_radius = max(1, int(scaled_light_radius * 0.7)) # Inner light source smaller
    glint_radius = max(1, int(scaled_light_radius * 0.3)) # Small highlight
    glint_offset_x = int(scaled_light_radius * 0.3)
    glint_offset_y = -int(scaled_light_radius * 0.3)
    glint_color = (255, 255, 255, 200) # Bright white glint
    glass_color_off = (light_off_color[0]+10, light_off_color[1]+10, light_off_color[2]+10, 100) # Slightly lighter off glass

    for light in anim_state['pinball_lights']:
        scaled_center = scale_rect_func(pygame.Rect(light['pos_logic'][0], light['pos_logic'][1], 0, 0)).center
        cx, cy = scaled_center

        if light['on']:
            base_on_color = light_colors[light['color_index']]
            # Glassy outer layer (semi-transparent version of base color)
            glass_color_on = (base_on_color[0], base_on_color[1], base_on_color[2], 120)
            pygame.draw.circle(surface, glass_color_on, scaled_center, glass_radius)
            # Inner light source (brighter)
            inner_color = (min(255, base_on_color[0]+50), min(255, base_on_color[1]+50), min(255, base_on_color[2]+50))
            pygame.draw.circle(surface, inner_color, scaled_center, inner_light_radius)
            # Glint
            glint_pos = (cx + glint_offset_x, cy + glint_offset_y)
            pygame.draw.circle(surface, glint_color, glint_pos, glint_radius)
        else:
            # Dim outer glass when off
            pygame.draw.circle(surface, glass_color_off, scaled_center, glass_radius)
            # Very dim inner circle when off
            pygame.draw.circle(surface, light_off_color, scaled_center, inner_light_radius)

    # --- Apply Lighting Overlay ---
    if has_lighting:
        # lighting_level is 0-100. 0 = max darkness, 100 = no darkness overlay.
        # We can map this to an alpha value for a black overlay.
        # Alpha: 0 (fully transparent) to 255 (fully opaque).
        # If lighting_level = 100, alpha = 0.
        # If lighting_level = 0, alpha = ~200 (very dark, but not pitch black).
        # If lighting_level = 50, alpha = ~100.
        max_darkness_alpha = 200 # How dark it gets at lighting_level = 0
        overlay_alpha = int(max_darkness_alpha * (1 - (lighting_level / 100.0)))
        overlay_alpha = max(0, min(255, overlay_alpha)) # Clamp alpha

        if overlay_alpha > 0:
            lighting_overlay = pygame.Surface(game_area_rect.size, pygame.SRCALPHA)
            lighting_overlay.fill((0, 0, 0, overlay_alpha))
            surface.blit(lighting_overlay, game_area_rect.topleft)

# --- Color Theme Definitions ---

# Define the color dictionaries for each background theme
CASINO_COLORS = {
    'PINBALL_BASE': (10, 5, 25),
    'PINBALL_LANE': (0, 200, 255),
    'LANE_BORDER': (5, 5, 5),
    'PINBALL_LIGHT_OFF': (25, 15, 50),
    'WOOD_BORDER': (85, 55, 30), # Kept for potential future use
    'PINBALL_DETAIL': (40, 30, 65),
    'PINBALL_LIGHT_1': (255, 255, 100),
    'PINBALL_LIGHT_2': (255, 50, 50),
    'PINBALL_LIGHT_3': (100, 255, 255),
    'PINBALL_LIGHT_4': (255, 100, 255),
    # Add any other casino-specific colors here
}

SEWER_COLORS = {
    'BRICK_LIGHT': (45, 45, 45),
    'BRICK_DARK': (30, 30, 30),
    'MORTAR': (15, 15, 15),
    'MANHOLE_BRICK_LIGHT': (20, 20, 20), # Using border color for simplicity
    'MANHOLE_BRICK_DARK': (20, 20, 20),  # Using border color for simplicity
    'VEGETATION_COLOR': (0, 80, 0),
    'CRACK_COLOR': (10, 10, 10),
    'SLUDGE_BASE': (60, 65, 45),
    'SLUDGE_MID': (80, 85, 60),
    'SLUDGE_HIGHLIGHT': (100, 105, 75),
    # Add any other sewer-specific colors here
}
FACTORY_COLORS = {
    # Floor/Circuit Colors (Metallic Grate & PCB Theme)
    'GRATE_BASE': (55, 60, 65),          # Medium-dark metallic grey base
    'GRATE_LINE_DARK': (40, 45, 50),     # Darker grey for grate lines
    'GRATE_LINE_LIGHT': (70, 75, 80),    # Lighter grey for grate lines/highlights
    'CIRCUIT_TRACE_MAIN': (160, 160, 155), # Light grey for main traces
    'CIRCUIT_TRACE_SHADOW': (25, 30, 30), # Dark shadow for traces
    'SOLDER_POINT': (218, 165, 32),     # Gold color for solder points
    'SOLDER_POINT_DARK': (184, 134, 11), # Darker gold for shading/bevel
    'SOLDER_POINT_HIGHLIGHT': (240, 190, 60), # Lighter gold for highlight/bevel

    # CRT/Eye Colors
    'CRT_BORDER': (30, 30, 30),           # Dark border for the screen
    'CRT_SCREEN': (0, 0, 0),             # Black screen background
    'EYE_GLOW': (200, 0, 0),            # Bright red glow
    'EYE_PUPIL_BG': (50, 0, 0),           # Dark red background for pupil numbers
    'EYE_NUMBER': (255, 180, 180),      # Light red/pink for numbers

    # Piston/Tesla Colors
    'PISTON_METAL_BASE': (90, 90, 100),   # Base metal color
    'PISTON_METAL_SHADOW': (60, 60, 70),  # Shadow color
    'PISTON_METAL_HIGHLIGHT': (130, 130, 140), # Highlight color
    'STEAM_COLOR_CORE': (230, 230, 230, 200), # Brighter core steam
    'STEAM_COLOR_FADE': (180, 180, 180, 100), # Faded outer steam
    'TESLA_COIL_BASE': (60, 50, 80),      # Darker purple/grey base
    'TESLA_COIL_HIGHLIGHT': (90, 80, 110), # Lighter highlight for coil
    'TESLA_SPARK_CORE': (255, 255, 255),   # Bright white core spark
    'TESLA_SPARK_GLOW': (200, 200, 255, 150), # Light blue glow
}

HAUNTED_HOVEL_COLORS = {
    'FLOOR_WOOD_DARK': (40, 30, 20),        # Dark brown for wood
    'FLOOR_WOOD_LIGHT': (60, 45, 30),       # Lighter brown for wood grain/highlights
    'WALL_STONE_DARK': (50, 50, 60),        # Dark grey-blue for stone walls
    'WALL_STONE_LIGHT': (70, 70, 80),       # Lighter grey-blue for stone highlights
    'COBWEB': (100, 100, 100, 100),         # Semi-transparent grey for cobwebs
    'DUST_MOTE': (120, 120, 100, 80),       # Faint yellowish dust
    'SHADOW': (10, 10, 15, 150),            # Dark, moody shadow color
    'FURNITURE_DARK': (30, 25, 20),         # Very dark for furniture outlines
    'FURNITURE_SHEET': (180, 170, 160, 200), # Off-white for sheets over furniture
    'FURNITURE_SHEET_PATTERN': (170, 160, 150, 200), # Slightly darker for subtle pattern on sheets
    'WINDOW_FRAME': (20, 15, 10),           # Dark frame for boarded/broken windows
    'WINDOW_PANE_MOONLIGHT': (100, 120, 150, 70), # Faint moonlight through a dirty pane
}

# Dictionary mapping background identifiers to their color themes
BACKGROUND_COLOR_THEMES = {
    "casino": CASINO_COLORS,
    "sewer": SEWER_COLORS,
    "factory": FACTORY_COLORS,
    "haunted_hovel": HAUNTED_HOVEL_COLORS,
    # Add themes for other backgrounds here
}

# --- Background Definitions ---

# Dictionary mapping background identifiers to their drawing functions.
AVAILABLE_BACKGROUNDS = {} # Initialize first

def draw_haunted_hovel_background(surface, compiler_instance):
    """
    Draws a pixelated, top-down view of a haunted hovel interior.
    Features detailed elements like wooden floors, cobwebs, and blinking candles.
    """
    # --- Extract parameters ---
    colors = compiler_instance.colors
    scale = compiler_instance.scale
    scale_rect_func = compiler_instance.scale_rect
    arena_width = compiler_instance.width
    arena_height = compiler_instance.height
    dt = getattr(compiler_instance, 'dt', 1/60.0)
    center_x_logic = arena_width / 2
    center_y_logic = arena_height / 2
    wall_thickness_logic = 10 # Moved up for use in cobweb pre-calculation

    # --- Get Lighting Properties ---
    level_properties = getattr(compiler_instance, 'level_properties', {})
    has_lighting = level_properties.get('has_lighting', False)
    lighting_level = level_properties.get('lighting_level', 75) # Default 75%

    # --- Initialize/Update Animation State ---
    # This will now cover furniture drapes, dust motes, and animated chair
    if 'background_animation_state' not in compiler_instance.__dict__:
         compiler_instance.background_animation_state = {}
    anim_state = compiler_instance.background_animation_state

    recalculate_bg_details = False
    current_dims_scale_bg = (arena_width, arena_height, scale)
    last_dims_scale_tuple = anim_state.get('hovel_bg_last_dims_scale')

    if last_dims_scale_tuple is None:
        recalculate_bg_details = True
    else:
        last_w, last_h, last_s = last_dims_scale_tuple
        # Define a small tolerance for scale comparison
        scale_tolerance = 0.0001 # Example tolerance for floating point comparison
        if last_w != arena_width or \
           last_h != arena_height or \
           abs(last_s - scale) > scale_tolerance:
            recalculate_bg_details = True
    
    if recalculate_bg_details:
        anim_state['hovel_bg_last_dims_scale'] = current_dims_scale_bg
        # print(f"Haunted Hovel BG: Dimensions/Scale changed OR first run. Recalculating details.") # Optional debug
        # Initialize/clear drape details storage
        anim_state['hovel_furniture_drapes'] = {} # Store by furniture index or a unique ID
        anim_state['hovel_animated_chair'] = {} # For the moving chair
        anim_state['hovel_bookshelf_details'] = {} # For pre-calculating book details
        anim_state['hovel_bookshelf_details'] = {} # For pre-calculating book details

        # Initialize dust motes (moved here to be part of the same recalculation)
        anim_state['hovel_dust_motes'] = []
        num_motes = 50
        for _ in range(num_motes):
            anim_state['hovel_dust_motes'].append({
                'pos_logic': (random.uniform(0, arena_width), random.uniform(0, arena_height)),
                'size_logic': random.uniform(0.5, 1.5),
                'alpha': random.randint(40, 100)
            })
        
        # Pre-calculate cobweb scaled data
        anim_state['hovel_cobwebs_scaled_data'] = []
        cobweb_points_sets_local = [
            [(wall_thickness_logic, wall_thickness_logic), (wall_thickness_logic + 60, wall_thickness_logic), (wall_thickness_logic, wall_thickness_logic + 60)], # Top-left corner
            # Removed the problematic small cobweb definition that was here
            [(arena_width - wall_thickness_logic, wall_thickness_logic), (arena_width - wall_thickness_logic - 60, wall_thickness_logic), (arena_width - wall_thickness_logic, wall_thickness_logic + 60)], # Top-right corner
            [(wall_thickness_logic, arena_height - wall_thickness_logic), (wall_thickness_logic + 60, arena_height - wall_thickness_logic), (wall_thickness_logic, arena_height - wall_thickness_logic - 60)], # Bottom-left corner
        ]
        for point_set_logic in cobweb_points_sets_local:
            current_scaled_points = [scale_rect_func(pygame.Rect(p[0], p[1], 0, 0)).center for p in point_set_logic]
            if len(current_scaled_points) >= 3:
                current_center_of_web = ((current_scaled_points[0][0] + current_scaled_points[1][0] + current_scaled_points[2][0]) / 3,
                                         (current_scaled_points[0][1] + current_scaled_points[1][1] + current_scaled_points[2][1]) / 3)
                strand_lines_data = []
                for p_s in current_scaled_points:
                    strand_lines_data.append({'start': current_center_of_web, 'end': p_s})
                anim_state['hovel_cobwebs_scaled_data'].append({
                    'polygon_points': current_scaled_points,
                    'strand_lines': strand_lines_data
                })

    # --- Define Haunted Hovel Colors (from theme) ---
    floor_dark = colors.get('FLOOR_WOOD_DARK', (40, 30, 20))
    floor_light = colors.get('FLOOR_WOOD_LIGHT', (60, 45, 30))
    wall_dark = colors.get('WALL_STONE_DARK', (50, 50, 60))
    wall_light = colors.get('WALL_STONE_LIGHT', (70, 70, 80))
    cobweb_color = colors.get('COBWEB', (100, 100, 100, 100))
    shadow_color = colors.get('SHADOW', (10, 10, 15, 150))
    furniture_dark_color = colors.get('FURNITURE_DARK', (30, 25, 20))
    furniture_sheet_color = colors.get('FURNITURE_SHEET', (180, 170, 160, 200))
    furniture_sheet_pattern_color = colors.get('FURNITURE_SHEET_PATTERN', (170, 160, 150, 200))
    window_frame_color = colors.get('WINDOW_FRAME', (20, 15, 10))
    moonlight_color = colors.get('WINDOW_PANE_MOONLIGHT', (100, 120, 150, 70))

    # --- Get the game area rectangle ---
    game_area_rect = scale_rect_func(pygame.Rect(0, 0, arena_width, arena_height))
    # --- Draw Base Floor (Pixelated Wood Planks) ---
    surface.fill(floor_dark, game_area_rect)
    # DEBUG: Draw a small red rectangle to test if any drawing is happening
    test_rect = pygame.Rect(game_area_rect.left + 10, game_area_rect.top + 10, 20, 20)
    surface.fill((255, 0, 0), test_rect)
    plank_width_logic = 20
    scaled_plank_width = max(1, int(plank_width_logic * scale))
    for x_screen in range(game_area_rect.left, game_area_rect.right, scaled_plank_width):
        # Alternate plank color for texture, or add grain lines
        if (x_screen // scaled_plank_width) % 3 == 0: # Every 3rd plank slightly lighter
            pygame.draw.line(surface, floor_light, (x_screen, game_area_rect.top), (x_screen, game_area_rect.bottom), max(1, int(2*scale)))
        else: # Draw thin dark lines for plank separation
             pygame.draw.line(surface, (floor_dark[0]-5, floor_dark[1]-5, floor_dark[2]-5), (x_screen, game_area_rect.top), (x_screen, game_area_rect.bottom), 1)

    # --- Draw Walls (Simple Outlines) ---
    # wall_thickness_logic is already defined earlier
    scaled_wall_thickness = max(1, int(wall_thickness_logic * scale))
    # Top wall
    pygame.draw.rect(surface, wall_dark, scale_rect_func(pygame.Rect(0, 0, arena_width, wall_thickness_logic)))
    # Bottom wall
    pygame.draw.rect(surface, wall_dark, scale_rect_func(pygame.Rect(0, arena_height - wall_thickness_logic, arena_width, wall_thickness_logic)))
    # Left wall
    pygame.draw.rect(surface, wall_dark, scale_rect_func(pygame.Rect(0, 0, wall_thickness_logic, arena_height)))
    # Right wall
    pygame.draw.rect(surface, wall_dark, scale_rect_func(pygame.Rect(arena_width - wall_thickness_logic, 0, wall_thickness_logic, arena_height)))

    # --- Draw Dilapidated Furniture (Covered with Sheets - more specific shapes) ---
    furniture_definitions = [
        {'type': 'bed', 'rect_logic': pygame.Rect(arena_width * 0.65, arena_height * 0.2, arena_width * 0.25, arena_height * 0.35), 'sheeted': True},
        {'type': 'round_table', 'pos_logic': (arena_width * 0.25, arena_height * 0.65), 'radius_logic': arena_width * 0.08, 'sheeted': True},
        {'type': 'grandfather_clock', 'rect_logic': pygame.Rect(arena_width * 0.05, arena_height * 0.25, arena_width * 0.05, arena_height * 0.4), 'sheeted': False}, # Usually not sheeted
        {'type': 'dresser', 'rect_logic': pygame.Rect(arena_width * 0.4, arena_height * 0.8, arena_width * 0.2, arena_height * 0.1), 'sheeted': True},
        {'type': 'rickety_chair', 'base_rect_logic': pygame.Rect(arena_width * 0.15, arena_height * 0.45, arena_width * 0.07, arena_height * 0.1), 'sheeted': False, 'animated': True},
        {'type': 'bookshelf', 'rect_logic': pygame.Rect(arena_width * 0.75, wall_thickness_logic + arena_height * 0.05, arena_width * 0.15, arena_height * 0.25), 'sheeted': False},
        {'type': 'broken_mirror', 'rect_logic': pygame.Rect(arena_width * 0.5, arena_height * 0.12, arena_width * 0.04, arena_height * 0.15), 'sheeted': False},
    ]

    for idx, item_def in enumerate(furniture_definitions): # Added enumerate for unique key
        item_type = item_def['type']
        sheeted = item_def['sheeted']
        furniture_key = f"{item_type}_{idx}" # Unique key for anim_state
        is_animated_chair = item_def.get('animated', False) and item_type == 'rickety_chair'

        if recalculate_bg_details:
            # Pre-calculate random drape parameters if this item has drapes
            if item_type == 'bed' and sheeted:
                anim_state['hovel_furniture_drapes'][furniture_key] = []
                for _ in range(4): # 4 drape lines for bed
                    anim_state['hovel_furniture_drapes'][furniture_key].append({
                        'start_x_factor': random.uniform(0.1, 0.9),
                        'end_x_offset_factor': random.uniform(-0.2, 0.2),
                        'start_y_factor': random.uniform(0.2, 0.8),
                        'end_y_offset_factor': random.uniform(0.05, 0.15)
                    })
            elif item_type == 'round_table' and sheeted:
                anim_state['hovel_furniture_drapes'][furniture_key] = []
                for i in range(6): # 6 drape lines for table
                    anim_state['hovel_furniture_drapes'][furniture_key].append({
                        'angle_offset': random.uniform(-0.1, 0.1),
                        'start_r_factor': random.uniform(0.3, 0.6),
                        'end_r_factor': random.uniform(0.7, 0.95)
                    })
            elif is_animated_chair:
                # Initialize animated chair state
                if furniture_key not in anim_state['hovel_animated_chair']:
                    anim_state['hovel_animated_chair'][furniture_key] = {
                        'base_rect_logic': item_def['base_rect_logic'].copy(), # Store a copy
                        'current_offset_logic': pygame.math.Vector2(0, 0),
                        'target_offset_logic': pygame.math.Vector2(0, 0),
                        'move_timer': random.uniform(2.0, 5.0), # Start with a random delay
                        'move_interval': random.uniform(4.0, 8.0), # How often to consider moving
                        'is_moving': False,
                        'move_duration': random.uniform(0.3, 0.7), # How long a move takes
                        'current_move_time': 0.0,
                        'max_offset_pixels': 3, # Max movement in logical pixels
                    }
            elif item_type == 'bookshelf':
                # Pre-calculate book details only if not already done or if recalculating
                if furniture_key not in anim_state['hovel_bookshelf_details'] or recalculate_bg_details:
                    anim_state['hovel_bookshelf_details'][furniture_key] = {'books': []}
                    shelf_rect_logic = item_def['rect_logic']
                    book_colors_options = [(80,40,30), (40,60,50), (70,70,50), (30,30,60), (50,50,50), (60, 60, 80)] # Added more variety
                    num_shelves_for_calc = 4 # Must match drawing logic
                    
                    for i_shelf in range(num_shelves_for_calc):
                        # Relative Y calculation for books on this shelf, within the shelf's logical rect
                        # These are factors of the shelf's own height for this specific shelf level
                        shelf_level_top_y_factor = (i_shelf + 0.1) / num_shelves_for_calc
                        shelf_level_bottom_y_factor = (i_shelf + 0.9) / num_shelves_for_calc
                        
                        current_x_factor = 0.05 # Start books a bit inset, relative to shelf width
                        while current_x_factor < 0.90: # Leave some space at the end
                            book_width_factor = random.uniform(0.04, 0.12) # Relative to shelf width, slightly wider books
                            # Book height is relative to the height of this specific shelf level
                            book_height_factor = (shelf_level_bottom_y_factor - shelf_level_top_y_factor) * random.uniform(0.85, 0.98) # Slightly vary height
                            
                            # Store relative rect (x,y,w,h are factors of the parent bookshelf rect) and color
                            anim_state['hovel_bookshelf_details'][furniture_key]['books'].append({
                                'rel_x': current_x_factor,
                                'rel_y': shelf_level_top_y_factor + ((shelf_level_bottom_y_factor - shelf_level_top_y_factor) - book_height_factor), # Align to bottom of shelf space
                                'rel_w': book_width_factor,
                                'rel_h': book_height_factor,
                                'color': random.choice(book_colors_options)
                            })
                            current_x_factor += book_width_factor + random.uniform(0.008, 0.02) # Small gap, relative
            elif item_type == 'bookshelf':
                if furniture_key not in anim_state['hovel_bookshelf_details']:
                    anim_state['hovel_bookshelf_details'][furniture_key] = {'books': []}
                    shelf_rect_logic = item_def['rect_logic']
                    book_colors_options = [(80,40,30), (40,60,50), (70,70,50), (30,30,60), (50,50,50)]
                    num_shelves_for_calc = 4 # Must match drawing logic
                    
                    for i in range(num_shelves_for_calc):
                        # Relative Y calculation for books on this shelf
                        # These are factors of the shelf's own height
                        shelf_y_top_factor = (i + 0.1) / num_shelves_for_calc
                        shelf_y_bottom_factor = (i + 0.9) / num_shelves_for_calc
                        
                        current_x_factor = 0.05 # Start books a bit inset, relative to shelf width
                        while current_x_factor < 0.90: # Leave some space at the end
                            book_width_factor = random.uniform(0.03, 0.08) # Relative to shelf width
                            book_height_factor = shelf_y_bottom_factor - shelf_y_top_factor # Full height of available space on this shelf level
                            
                            # Store relative rect and color
                            anim_state['hovel_bookshelf_details'][furniture_key]['books'].append({
                                'rel_x': current_x_factor,
                                'rel_y': shelf_y_top_factor,
                                'rel_w': book_width_factor,
                                'rel_h': book_height_factor,
                                'color': random.choice(book_colors_options)
                            })
                            current_x_factor += book_width_factor + random.uniform(0.005, 0.015) # Small gap, relative

        if item_type == 'bed':
            bed_rect_logic = item_def['rect_logic']
            scaled_bed_rect = scale_rect_func(bed_rect_logic)
            pygame.draw.rect(surface, furniture_dark_color, scaled_bed_rect, border_radius=max(1, int(2*scale)))
            if sheeted:
                sheet_rect = scaled_bed_rect.inflate(-max(1,int(2*scale)), -max(1,int(2*scale)))
                if sheet_rect.width > 0 and sheet_rect.height > 0:
                    pygame.draw.rect(surface, furniture_sheet_color, sheet_rect, border_radius=max(1, int(1*scale)))
                    # Pattern on sheet
                    for r in range(0, sheet_rect.height, max(2,int(4*scale))):
                        pygame.draw.line(surface, furniture_sheet_pattern_color, (sheet_rect.left, sheet_rect.top + r), (sheet_rect.right, sheet_rect.top + r), 1)
                    # Drape lines - use stored random values
                    if furniture_key in anim_state['hovel_furniture_drapes']:
                        for drape_params in anim_state['hovel_furniture_drapes'][furniture_key]:
                            start_x = sheet_rect.left + drape_params['start_x_factor'] * sheet_rect.width
                            end_x = start_x + drape_params['end_x_offset_factor'] * sheet_rect.width
                            start_y = sheet_rect.top + drape_params['start_y_factor'] * sheet_rect.height
                            end_y = start_y + drape_params['end_y_offset_factor'] * sheet_rect.height
                            pygame.draw.line(surface, (furniture_sheet_color[0]-15, furniture_sheet_color[1]-15, furniture_sheet_color[2]-15), (start_x, start_y), (end_x, min(sheet_rect.bottom -1, end_y)), 1)
            # Bed posts
            post_size_logic = 5
            scaled_post_size = max(1, int(post_size_logic * scale))
            posts_logic = [
                (bed_rect_logic.left, bed_rect_logic.top), (bed_rect_logic.right - post_size_logic, bed_rect_logic.top),
                (bed_rect_logic.left, bed_rect_logic.bottom - post_size_logic), (bed_rect_logic.right - post_size_logic, bed_rect_logic.bottom - post_size_logic)
            ]
            for post_l_x, post_l_y in posts_logic:
                scaled_post_rect = scale_rect_func(pygame.Rect(post_l_x, post_l_y, post_size_logic, post_size_logic))
                pygame.draw.rect(surface, furniture_dark_color, scaled_post_rect)

        elif item_type == 'round_table':
            pos_logic = item_def['pos_logic']
            radius_logic = item_def['radius_logic']
            scaled_center = scale_rect_func(pygame.Rect(pos_logic[0], pos_logic[1],0,0)).center
            scaled_radius = max(2, int(radius_logic * scale))
            pygame.draw.circle(surface, furniture_dark_color, scaled_center, scaled_radius)
            if sheeted:
                sheet_radius = max(1, int(scaled_radius * 0.9))
                if sheet_radius > 0:
                    pygame.draw.circle(surface, furniture_sheet_color, scaled_center, sheet_radius)
                    # Pattern on sheet (concentric circles)
                    for r_offset in range(max(1,int(3*scale)), sheet_radius, max(2,int(4*scale))):
                         pygame.draw.circle(surface, furniture_sheet_pattern_color, scaled_center, sheet_radius - r_offset, 1)
                    # Drape lines (radial) - use stored random values
                    if furniture_key in anim_state['hovel_furniture_drapes']:
                        for i, drape_params in enumerate(anim_state['hovel_furniture_drapes'][furniture_key]):
                            angle = (math.pi * 2 / 6) * i + drape_params['angle_offset']
                            start_r = sheet_radius * drape_params['start_r_factor']
                            end_r = sheet_radius * drape_params['end_r_factor']
                            p1 = (scaled_center[0] + start_r * math.cos(angle), scaled_center[1] + start_r * math.sin(angle))
                            p2 = (scaled_center[0] + end_r * math.cos(angle), scaled_center[1] + end_r * math.sin(angle))
                            pygame.draw.line(surface, (furniture_sheet_color[0]-15, furniture_sheet_color[1]-15, furniture_sheet_color[2]-15), p1, p2, 1)

        elif item_type == 'grandfather_clock':
            clock_rect_logic = item_def['rect_logic']
            scaled_clock_rect = scale_rect_func(clock_rect_logic)
            pygame.draw.rect(surface, furniture_dark_color, scaled_clock_rect)
            # Simple face detail
            face_center_x = scaled_clock_rect.centerx
            face_center_y = scaled_clock_rect.top + scaled_clock_rect.width // 2 # Assume square top for face
            face_radius = scaled_clock_rect.width // 3
            if face_radius > 1:
                pygame.draw.circle(surface, floor_light, (face_center_x, face_center_y), face_radius) # Clock face
                pygame.draw.circle(surface, floor_dark, (face_center_x, face_center_y), max(1, face_radius-int(1*scale))) # Inner dark

        elif item_type == 'dresser':
            dresser_rect_logic = item_def['rect_logic']
            scaled_dresser_rect = scale_rect_func(dresser_rect_logic)
            pygame.draw.rect(surface, furniture_dark_color, scaled_dresser_rect, border_radius=max(1, int(1*scale)))
            if sheeted:
                sheet_rect = scaled_dresser_rect.inflate(-max(1,int(1*scale)), -max(1,int(1*scale)))
                if sheet_rect.width > 0 and sheet_rect.height > 0:
                    pygame.draw.rect(surface, furniture_sheet_color, sheet_rect, border_radius=max(1, int(1*scale)))
                    # Pattern on sheet
                    for r in range(0, sheet_rect.height, max(2,int(3*scale))): # Tighter pattern
                        pygame.draw.line(surface, furniture_sheet_pattern_color, (sheet_rect.left, sheet_rect.top + r), (sheet_rect.right, sheet_rect.top + r), 1)
        
        elif is_animated_chair:
            chair_state = anim_state['hovel_animated_chair'].get(furniture_key)
            if chair_state:
                chair_state['move_timer'] -= dt
                if not chair_state['is_moving'] and chair_state['move_timer'] <= 0:
                    chair_state['is_moving'] = True
                    chair_state['current_move_time'] = 0.0
                    # Choose a small random offset
                    offset_x = random.uniform(-chair_state['max_offset_pixels'], chair_state['max_offset_pixels'])
                    offset_y = random.uniform(-chair_state['max_offset_pixels'], chair_state['max_offset_pixels'])
                    chair_state['target_offset_logic'] = pygame.math.Vector2(offset_x, offset_y)
                    chair_state['move_timer'] = chair_state['move_interval'] # Reset timer for next potential move

                if chair_state['is_moving']:
                    chair_state['current_move_time'] += dt
                    progress = min(1.0, chair_state['current_move_time'] / chair_state['move_duration'])
                    # Simple linear interpolation for movement
                    chair_state['current_offset_logic'] = chair_state['target_offset_logic'] * progress
                    
                    if progress >= 1.0:
                        chair_state['is_moving'] = False
                        # Snap to target, then reset target to 0 for next idle phase or make it drift back
                        chair_state['current_offset_logic'] = chair_state['target_offset_logic'].copy()
                        # Option: make it slowly drift back to 0,0 or just stay put until next move
                        # For now, it stays put until the next explicit move.
                        # To make it drift back, you'd set a new target_offset_logic to (0,0)
                        # and a new move_duration for the drift back.

                # Apply offset to base rect
                animated_rect_logic = chair_state['base_rect_logic'].move(chair_state['current_offset_logic'].x, chair_state['current_offset_logic'].y)
                scaled_chair_rect = scale_rect_func(animated_rect_logic)
                chair_main_color = furniture_dark_color
                chair_detail_color = (min(255,chair_main_color[0]+20), min(255,chair_main_color[1]+20), min(255,chair_main_color[2]+20))

                # Seat (main rectangle)
                seat_rect = scaled_chair_rect
                pygame.draw.rect(surface, chair_main_color, seat_rect)
                pygame.draw.rect(surface, chair_detail_color, seat_rect, max(1, int(1*scale))) # Outline

                # Backrest
                back_width = seat_rect.width
                back_height_abs = seat_rect.height * 1.1 # Absolute height for backrest
                back_top_y = seat_rect.top - back_height_abs
                
                # Main backrest panel
                back_panel_rect = pygame.Rect(seat_rect.left, back_top_y, back_width, back_height_abs)
                pygame.draw.rect(surface, chair_main_color, back_panel_rect)
                pygame.draw.rect(surface, chair_detail_color, back_panel_rect, max(1, int(1*scale)))

                # Spindles for backrest (3 vertical spindles)
                num_spindles = 3
                spindle_width_abs = max(1, int(back_width * 0.1)) # Absolute width
                total_spindle_width = num_spindles * spindle_width_abs
                spacing_between_spindles = (back_width - total_spindle_width) / (num_spindles + 1)
                
                for i in range(num_spindles):
                    spindle_x = back_panel_rect.left + spacing_between_spindles * (i + 1) + spindle_width_abs * i
                    spindle_rect = pygame.Rect(spindle_x, back_panel_rect.top + max(1, int(1*scale)), spindle_width_abs, back_panel_rect.height - max(2, int(2*scale)))
                    pygame.draw.rect(surface, chair_detail_color, spindle_rect)
                
                # Top rail of backrest
                top_rail_height = max(1, int(back_height_abs * 0.15))
                top_rail_rect = pygame.Rect(back_panel_rect.left, back_panel_rect.top, back_panel_rect.width, top_rail_height)
                pygame.draw.rect(surface, chair_detail_color, top_rail_rect)


                # Legs (more distinct)
                leg_width_abs = max(1, int(seat_rect.width * 0.12)) # Absolute width
                leg_height_abs = max(1, int(seat_rect.height * 0.5)) # Legs are usually longer than seat height from side, but appear shorter top-down

                # Front legs (drawn slightly "under" the front edge of the seat)
                pygame.draw.rect(surface, chair_main_color, (seat_rect.left + leg_width_abs*0.3, seat_rect.bottom - leg_height_abs*0.7, leg_width_abs, leg_height_abs))
                pygame.draw.rect(surface, chair_main_color, (seat_rect.right - leg_width_abs*1.3, seat_rect.bottom - leg_height_abs*0.7, leg_width_abs, leg_height_abs))
                
                # Back legs (drawn slightly "under" the back edge of the seat, aligned with backrest posts if any)
                pygame.draw.rect(surface, chair_main_color, (seat_rect.left + leg_width_abs*0.3, seat_rect.top + seat_rect.height - leg_height_abs*1.0, leg_width_abs, leg_height_abs))
                pygame.draw.rect(surface, chair_main_color, (seat_rect.right - leg_width_abs*1.3, seat_rect.top + seat_rect.height - leg_height_abs*1.0, leg_width_abs, leg_height_abs))


        elif item_type == 'bookshelf':
            shelf_rect_logic = item_def['rect_logic']
            scaled_shelf_rect = scale_rect_func(shelf_rect_logic)
            # Main frame of the bookshelf
            pygame.draw.rect(surface, furniture_dark_color, scaled_shelf_rect)
            pygame.draw.rect(surface, (furniture_dark_color[0]+10, furniture_dark_color[1]+10, furniture_dark_color[2]+10), scaled_shelf_rect, max(1,int(1*scale))) # Outline

            # Draw shelves
            num_shelves = 4 # Should match pre-calculation
            shelf_thickness_scaled = max(1, int(2*scale)) # Thickness of the shelf plank
            # Calculate available height for shelf content (excluding thickness of planks and top/bottom frame)
            content_height_total = scaled_shelf_rect.height - (num_shelves + 1) * shelf_thickness_scaled
            shelf_content_height_each = content_height_total / num_shelves if num_shelves > 0 else 0
            
            shelf_plank_color = (furniture_dark_color[0]+20, furniture_dark_color[1]+20, furniture_dark_color[2]+20)

            for i_shelf in range(num_shelves):
                # Y position of the top of the shelf plank
                plank_y_pos = scaled_shelf_rect.top + shelf_thickness_scaled * (i_shelf +1) + shelf_content_height_each * i_shelf
                pygame.draw.rect(surface, shelf_plank_color,
                                 (scaled_shelf_rect.left + int(1*scale), plank_y_pos, scaled_shelf_rect.width - int(2*scale), shelf_thickness_scaled))
            
            # Draw pre-calculated books using stored details
            if furniture_key in anim_state['hovel_bookshelf_details']:
                shelf_details_data = anim_state['hovel_bookshelf_details'][furniture_key]
                for book_info in shelf_details_data['books']:
                    # Calculate absolute book position and size based on stored relative factors and current scaled_shelf_rect
                    book_abs_x = scaled_shelf_rect.left + book_info['rel_x'] * scaled_shelf_rect.width
                    book_abs_y = scaled_shelf_rect.top + book_info['rel_y'] * scaled_shelf_rect.height
                    book_abs_w = book_info['rel_w'] * scaled_shelf_rect.width
                    book_abs_h = book_info['rel_h'] * scaled_shelf_rect.height
                    
                    book_abs_w = max(1, book_abs_w) # Ensure min width 1px
                    book_abs_h = max(1, book_abs_h) # Ensure min height 1px

                    current_book_rect = pygame.Rect(book_abs_x, book_abs_y, book_abs_w, book_abs_h)
                    pygame.draw.rect(surface, book_info['color'], current_book_rect)
                    # Add a darker outline to each book for definition
                    outline_color = (max(0, book_info['color'][0]-20), max(0, book_info['color'][1]-20), max(0, book_info['color'][2]-20))
                    pygame.draw.rect(surface, outline_color, current_book_rect, 1)

        elif item_type == 'broken_mirror':
            mirror_rect_logic = item_def['rect_logic']
            scaled_mirror_rect = scale_rect_func(mirror_rect_logic)
            # Frame
            pygame.draw.rect(surface, window_frame_color, scaled_mirror_rect, max(1, int(2*scale)))
            # Glass (slightly reflective, greyish)
            glass_color = (100, 105, 110, 150)
            inner_mirror_rect = scaled_mirror_rect.inflate(-max(1,int(2*scale))*2, -max(1,int(2*scale))*2)
            if inner_mirror_rect.width > 0 and inner_mirror_rect.height > 0:
                 pygame.draw.rect(surface, glass_color, inner_mirror_rect)
                 # Cracks
                 crack_color_mirror = (30,30,30, 200)
                 # Store crack points in animation state if not already set
                 if 'mirror_cracks' not in anim_state:
                     anim_state['mirror_cracks'] = []
                     for _ in range(3): # Generate 3 crack lines
                         start_pt = (random.randint(inner_mirror_rect.left, inner_mirror_rect.right),
                                   random.randint(inner_mirror_rect.top, inner_mirror_rect.bottom))
                         end_pt = (random.randint(inner_mirror_rect.left, inner_mirror_rect.right),
                                 random.randint(inner_mirror_rect.top, inner_mirror_rect.bottom))
                         anim_state['mirror_cracks'].append((start_pt, end_pt))
                 
                 # Draw stored crack lines
                 for start_pt, end_pt in anim_state['mirror_cracks']:
                     pygame.draw.line(surface, crack_color_mirror, start_pt, end_pt, max(1,int(1*scale)))


    # --- Draw Cobwebs (in corners) ---
    # Use pre-calculated scaled data from anim_state
    if 'hovel_cobwebs_scaled_data' in anim_state:
        for cobweb_data in anim_state['hovel_cobwebs_scaled_data']:
            scaled_polygon_points = cobweb_data['polygon_points']
            pygame.draw.polygon(surface, cobweb_color, scaled_polygon_points, 0) # Filled polygon for base
            
            strand_color_r = cobweb_color[0] + 10 if cobweb_color[0] < 245 else 255
            strand_color_g = cobweb_color[1] + 10 if cobweb_color[1] < 245 else 255
            strand_color_b = cobweb_color[2] + 10 if cobweb_color[2] < 245 else 255
            strand_color_a = cobweb_color[3] - 20 if cobweb_color[3] > 20 else cobweb_color[3]
            strand_final_color = (strand_color_r, strand_color_g, strand_color_b, strand_color_a)

            for line_data in cobweb_data['strand_lines']:
                pygame.draw.line(surface, strand_final_color, line_data['start'], line_data['end'], 1)

    # --- Draw some dust motes (optional, for mood) ---
    # Dust mote generation is now handled above, triggered by recalculate_bg_details
    dust_mote_color_base = colors.get('DUST_MOTE', (120, 120, 100, 80))
    for mote in anim_state['hovel_dust_motes']:
        scaled_mote_pos = scale_rect_func(pygame.Rect(mote['pos_logic'][0], mote['pos_logic'][1],0,0)).center
        scaled_mote_size = max(1, int(mote['size_logic'] * scale))
        mote_color = (dust_mote_color_base[0], dust_mote_color_base[1], dust_mote_color_base[2], mote['alpha'])
        pygame.draw.circle(surface, mote_color, scaled_mote_pos, scaled_mote_size)

    # --- Apply Lighting Overlay ---
    if has_lighting:
        max_darkness_alpha = 200
        overlay_alpha = int(max_darkness_alpha * (1 - (lighting_level / 100.0)))
        overlay_alpha = max(0, min(255, overlay_alpha))

        if overlay_alpha > 0:
            lighting_overlay = pygame.Surface(game_area_rect.size, pygame.SRCALPHA)
            lighting_overlay.fill((0, 0, 0, overlay_alpha))
            surface.blit(lighting_overlay, game_area_rect.topleft)


def draw_sewer_background(surface, compiler_instance):
    """
    Draws the detailed sewer background with bricks, river, cracks, etc.
    Retrieves necessary parameters from the compiler_instance.

    Args:
        surface: The pygame surface to draw onto.
        compiler_instance: The LevelCompiler instance containing level data,
                           colors, scale, offsets, objects, and state.
    """
    # --- Extract parameters from compiler_instance ---
    # Access attributes directly from the compiler instance
    colors = compiler_instance.colors
    scale = compiler_instance.scale
    offset_x = compiler_instance.offset_x
    offset_y = compiler_instance.offset_y
    scale_rect_func = compiler_instance.scale_rect
    scoreboard_height = compiler_instance.scoreboard_height
    all_objects = compiler_instance.manholes # Use the specific manholes list from compiler

    # --- Get Lighting Properties ---
    level_properties = getattr(compiler_instance, 'level_properties', {})
    has_lighting = level_properties.get('has_lighting', False)
    lighting_level = level_properties.get('lighting_level', 75) # Default 75%

    # Get background details directly from the compiler instance attribute
    background_details = compiler_instance.background_details # Direct access
    if not background_details:
        # Only show warning once using static flag
        if not hasattr(draw_sewer_background, '_warned_about_details'):
            print("Warning: No background_details found in compiler instance for sewer background.")
            print("Warning: Using default sewer background details.")
            draw_sewer_background._warned_about_details = True
        
        # Use defaults if details are missing entirely
        background_details = {
              'brick_width': 50, 'brick_height': 25, 'river_width_ratio': 0.25,
              'manhole_brick_padding': 5, 'crack_frequency': 0.05,
              'vegetation_frequency': 0.02, 'river_animation_speed': 1
        }
        # Do not return here, proceed with defaults

    # Get level dimensions directly from compiler instance
    arena_width = compiler_instance.width
    arena_height = compiler_instance.height

    # --- Get the game area rectangle ---
    game_area_rect = scale_rect_func(pygame.Rect(0, 0, arena_width, arena_height))

    # --- Draw Base Background Color ---
    # Use a dark base color, e.g., Mortar or Brick Dark, filling only the game area
    base_sewer_color = colors.get('MORTAR', (15, 15, 15))
    surface.fill(base_sewer_color, game_area_rect)

    # Use the already filtered manholes list from the compiler instance
    # IMPORTANT: Assumes ManHoleObject class is imported or accessible where LevelCompiler is defined
    # If not, this might need adjustment based on how object types are stored/checked.
    manholes = [obj for obj in all_objects if obj.__class__.__name__ == 'ManHoleObject']

    # Access and update animation state (assuming it's stored this way)
    if 'background_animation_state' not in compiler_instance.__dict__:
         compiler_instance.background_animation_state = {} # Initialize if needed
    if 'river_offset' not in compiler_instance.background_animation_state:
        compiler_instance.background_animation_state['river_offset'] = 0 # Initialize offset

    river_animation_offset = compiler_instance.background_animation_state['river_offset']

    # --- Use extracted parameters ---
    details = background_details # Use the extracted details

    brick_w = details.get('brick_width', 50) # Use .get with defaults
    brick_h = details.get('brick_height', 25) # Use .get with defaults
    river_width_ratio = details.get('river_width_ratio', 0.25)
    river_width = arena_width * river_width_ratio
    river_x_start = (arena_width - river_width) / 2
    river_x_end = river_x_start + river_width
    manhole_padding = details.get('manhole_brick_padding', 5)

    # Pre-calculate scaled values for efficiency
    scaled_brick_w = brick_w * scale
    scaled_brick_h = brick_h * scale
    scaled_river_x_start = river_x_start * scale + offset_x
    scaled_river_width = river_width * scale
    # River Y starts at the top of the playable area in logical coordinates (Y=0)
    # scale_rect_func will handle adding the scoreboard offset for screen coordinates
    scaled_river_y_start = scale_rect_func(pygame.Rect(0, 0, 0, 0)).top # Get scaled top Y of playable area
    scaled_river_height = arena_height * scale # Use the full playable height

    # --- Draw Brick Pattern ---
    # Iterate through logical Y coordinates of the playable area (0 to arena_height)
    for y_logic in range(0, arena_height, brick_h): # Start Y loop from 0
        row_offset = (y_logic // brick_h) % 2 * (brick_w // 2)  # Staggered pattern
        for x_logic in range(0, arena_width, brick_w):
            # Create rect with logical coordinates relative to playable area top-left (0,0)
            brick_rect_logic = pygame.Rect(x_logic - row_offset, y_logic, brick_w, brick_h)

            # Skip drawing bricks fully covered by the river
            if brick_rect_logic.right > river_x_start and brick_rect_logic.left < river_x_end:
                continue

            # Check if near a manhole
            is_near_manhole = False
            manhole_brick_color_dark = colors.get('MANHOLE_BRICK_DARK', colors.get('BRICK_DARK', (50,50,50))) # More fallbacks
            manhole_brick_color_light = colors.get('MANHOLE_BRICK_LIGHT', colors.get('BRICK_LIGHT', (100,100,100))) # More fallbacks
            for manhole in manholes: # Use the filtered list
                # Inflate the logical manhole rect for checking
                # Ensure manhole.rect exists and is a pygame.Rect
                if hasattr(manhole, 'rect') and isinstance(manhole.rect, pygame.Rect):
                    manhole_rect_padded = manhole.rect.inflate(manhole_padding * 2, manhole_padding * 2)
                    if brick_rect_logic.colliderect(manhole_rect_padded):
                        is_near_manhole = True
                        break
                else:
                     # Log warning if manhole object is malformed
                     # print(f"Warning: Manhole object {manhole} lacks a valid rect attribute.")
                     pass

            # Determine brick color (Hardcoded darker values, solid manhole border)
            manhole_border_color = (20, 20, 20) # Very dark for border
            brick_light_color = (45, 45, 45)    # Darker light brick
            brick_dark_color = (30, 30, 30)     # Darker dark brick
            mortar_color = (15, 15, 15)         # Darker mortar

            if is_near_manhole:
                # Use only the dark manhole border color
                brick_color = manhole_border_color
            else:
                # Use hardcoded darker base brick colors
                brick_color = brick_light_color if (x_logic // brick_w + y_logic // brick_h) % 2 == 0 else brick_dark_color

            # Scale and draw the brick using the provided function
            scaled_brick_rect = scale_rect_func(brick_rect_logic) # Use extracted function
            # Draw directly onto the main surface
            pygame.draw.rect(surface, brick_color, scaled_brick_rect)
            pygame.draw.rect(surface, mortar_color, scaled_brick_rect, 1)  # Mortar outline

            # Vegetation drawing (removed for simplicity)

    # --- Draw Pre-calculated Cracks ---
    crack_color = (10, 10, 10) # Hardcoded dark crack color
    if 'cracks' in details and isinstance(details['cracks'], list):
        for crack_point_list in details['cracks']:
            if len(crack_point_list) >= 2: # Need at least two points to draw lines
                # Scale each point in the list
                scaled_points = []
                for point in crack_point_list:
                    # Scale logical point to screen coordinates
                    scaled_point = scale_rect_func(pygame.Rect(point[0], point[1], 0, 0)).topleft
                    scaled_points.append(scaled_point)

                # Draw the connected line segments (zig-zag) on the temp surface
                # Draw directly onto the main surface
                pygame.draw.lines(surface, crack_color, False, scaled_points, 1)

    # --- Draw Sewer River ---
    # Define the logical rectangle for the river within the playable area
    river_rect_logic = pygame.Rect(river_x_start, 0, river_width, arena_height)
    # Scale the logical rect to get the screen drawing area
    river_rect_scaled = scale_rect_func(river_rect_logic)

    # Use blue shades for the river (can still use theme colors here)
    # Define murky sludge colors inspired by the image
    sludge_base_color = colors.get('SLUDGE_BASE', (60, 65, 45))
    # Define mid and highlight with alpha for transparency
    sludge_mid_color_rgb = colors.get('SLUDGE_MID', (80, 85, 60))
    sludge_highlight_color_rgb = colors.get('SLUDGE_HIGHLIGHT', (100, 105, 75))

    # Draw the base river rectangle first
    # Draw the base river rectangle directly onto the main surface
    pygame.draw.rect(surface, sludge_base_color, river_rect_scaled)

    # --- Animate Sludge Flow ---
    # Ensure valid dimensions for drawing and calculations
    if river_rect_scaled.width > 0 and river_rect_scaled.height > 0:
        anim_speed = details.get('river_animation_speed', 0.5)
        # Define speed in pixels per second
        pixels_per_second = anim_speed * scale * 50 # Speed relative to scaled pixels

        # Get dt from compiler_instance
        dt = getattr(compiler_instance, 'dt', 1/60.0) # Default to 1/60

        # --- Update Scroll Offset ---
        current_offset = river_animation_offset # Get current offset
        offset_change = pixels_per_second * dt
        # Use the scaled river height for looping the texture offset
        texture_loop_height = river_rect_scaled.height

        if texture_loop_height > 0:
            new_offset = (current_offset + offset_change) % texture_loop_height
        else:
            new_offset = 0
        compiler_instance.background_animation_state['river_offset'] = new_offset # Store updated offset

        # --- Retrieve Pre-rendered Texture ---
        # Assume the texture is stored in the compiler instance after being generated
        # by the background thread. Add error handling/default if not found.
        sludge_texture = getattr(compiler_instance, 'sludge_texture', None)

        # --- Draw Scrolling Texture ---
        if sludge_texture and sludge_texture.get_height() > 0:
            tex_h = sludge_texture.get_height()
            # Ensure the texture height matches the expected river height for seamless tiling
            if tex_h != int(river_rect_scaled.height):
                 pass # Proceeding with potentially mismatched texture

            # Calculate the integer offset for blitting
            blit_offset = int(new_offset)

            # Define the area on the main surface where the river is drawn
            # Define the target area on the screen (the scaled river rect)
            target_area = river_rect_scaled

            # Create a temporary surface for the sludge texture with the right size
            sludge_target = pygame.Surface((target_area.width, target_area.height), pygame.SRCALPHA)
            sludge_target.fill((0, 0, 0, 0))  # Clear with transparent

            # Blit the first instance of the texture to the temporary surface
            src_rect1 = pygame.Rect(0, 0, target_area.width, tex_h)
            # Destination Y is offset by the negative scroll amount
            dest_y1 = -blit_offset
            sludge_target.blit(sludge_texture, (0, dest_y1), area=src_rect1, special_flags=pygame.BLEND_RGBA_ADD)

            # Blit the second instance of the texture, positioned below the first (wrapping around)
            dest_y2 = -blit_offset + tex_h
            sludge_target.blit(sludge_texture, (0, dest_y2), area=src_rect1, special_flags=pygame.BLEND_RGBA_ADD)

            # Blit the animated sludge texture directly onto the main surface at the river position
            surface.blit(sludge_target, river_rect_scaled.topleft) # Use river_rect_scaled.topleft
        elif not sludge_texture:
            pass # If no sludge texture is available

    # --- Apply Lighting Overlay ---
    if has_lighting:
        max_darkness_alpha = 200
        overlay_alpha = int(max_darkness_alpha * (1 - (lighting_level / 100.0)))
        overlay_alpha = max(0, min(255, overlay_alpha))

        if overlay_alpha > 0:
            lighting_overlay = pygame.Surface(game_area_rect.size, pygame.SRCALPHA)
            lighting_overlay.fill((0, 0, 0, overlay_alpha))
            surface.blit(lighting_overlay, game_area_rect.topleft)

    # --- No final blit needed as we drew directly onto the surface ---

def draw_factory_background(surface, compiler_instance):
    """
    Draws a symmetrical, top-down mechanical factory background.
    Features a central CRT eye, circuits, pistons, and tesla coils.

    Args:
        surface: The pygame surface to draw onto.
        compiler_instance: The LevelCompiler instance containing level data,
                           colors, scale, offsets, objects, and state.
    """
    # --- Extract parameters ---
    colors = compiler_instance.colors # Should contain FACTORY_COLORS now
    scale = compiler_instance.scale
    scale_rect_func = compiler_instance.scale_rect
    arena_width = compiler_instance.width
    arena_height = compiler_instance.height
    dt = getattr(compiler_instance, 'dt', 1/60.0)
    center_x_logic = arena_width / 2
    center_y_logic = arena_height / 2
    # Access ball objects (assuming they are in compiler_instance.balls or compiler_instance.objects)
    # Let's try 'objects' first, and filter for BallObject later if needed.
    game_objects = getattr(compiler_instance, 'objects', [])

    # --- Get Lighting Properties ---
    level_properties = getattr(compiler_instance, 'level_properties', {})
    has_lighting = level_properties.get('has_lighting', False)
    lighting_level = level_properties.get('lighting_level', 75) # Default 75%

    # --- Define Factory Colors (using the theme) ---
    pcb_base = colors.get('PCB_BASE', (35, 40, 38))
    trace_main = colors.get('CIRCUIT_TRACE_MAIN', (160, 160, 155))
    trace_detail = colors.get('CIRCUIT_TRACE_DETAIL', (120, 120, 115))
    solder_point = colors.get('SOLDER_POINT', (218, 165, 32))
    solder_point_dark = colors.get('SOLDER_POINT_DARK', (184, 134, 11))

    crt_border = colors.get('CRT_BORDER', (30, 30, 30))
    crt_screen = colors.get('CRT_SCREEN', (10, 10, 10))
    eye_glow = colors.get('EYE_GLOW', (200, 0, 0))
    eye_pupil_bg = colors.get('EYE_PUPIL_BG', (50, 0, 0))
    eye_number = colors.get('EYE_NUMBER', (255, 180, 180))

    piston_base_col = colors.get('PISTON_METAL_BASE', (90, 90, 100))
    piston_shadow_col = colors.get('PISTON_METAL_SHADOW', (60, 60, 70))
    piston_highlight_col = colors.get('PISTON_METAL_HIGHLIGHT', (130, 130, 140))
    steam_core_col = colors.get('STEAM_COLOR_CORE', (230, 230, 230, 200))
    steam_fade_col = colors.get('STEAM_COLOR_FADE', (180, 180, 180, 100))

    tesla_base_col = colors.get('TESLA_COIL_BASE', (60, 50, 80))
    tesla_highlight_col = colors.get('TESLA_COIL_HIGHLIGHT', (90, 80, 110))
    spark_core_col = colors.get('TESLA_SPARK_CORE', (255, 255, 255))
    spark_glow_col = colors.get('TESLA_SPARK_GLOW', (200, 200, 255, 150))


    # --- Get the game area rectangle ---
    game_area_rect = scale_rect_func(pygame.Rect(0, 0, arena_width, arena_height))

    # --- Draw Metallic Grate Floor ---
    grate_base_col = colors.get('GRATE_BASE', (55, 60, 65))
    grate_dark_col = colors.get('GRATE_LINE_DARK', (40, 45, 50))
    grate_light_col = colors.get('GRATE_LINE_LIGHT', (70, 75, 80))
    surface.fill(grate_base_col, game_area_rect)

    grate_spacing_logic = 15 # Logical pixels for grate spacing
    scaled_grate_spacing = max(2, int(grate_spacing_logic * scale)) # Ensure minimum 2px spacing

    # Draw horizontal grate lines (alternating dark/light for depth)
    for y in range(game_area_rect.top, game_area_rect.bottom, scaled_grate_spacing):
        pygame.draw.line(surface, grate_dark_col, (game_area_rect.left, y), (game_area_rect.right, y), 1)
        if y + 1 < game_area_rect.bottom: # Draw highlight line below dark line
             pygame.draw.line(surface, grate_light_col, (game_area_rect.left, y + 1), (game_area_rect.right, y + 1), 1)

    # Draw vertical grate lines (alternating dark/light for depth)
    for x in range(game_area_rect.left, game_area_rect.right, scaled_grate_spacing):
        pygame.draw.line(surface, grate_dark_col, (x, game_area_rect.top), (x, game_area_rect.bottom), 1)
        if x + 1 < game_area_rect.right: # Draw highlight line to the right of dark line
             pygame.draw.line(surface, grate_light_col, (x + 1, game_area_rect.top), (x + 1, game_area_rect.bottom), 1)


    # --- Initialize/Update Animation State ---
    if 'background_animation_state' not in compiler_instance.__dict__:
         compiler_instance.background_animation_state = {}
    anim_state = compiler_instance.background_animation_state

    # --- Recalculate Scale-Dependent Geometry & Fonts ---
    # Check if dimensions or scale have changed
    current_dims_scale = (arena_width, arena_height, scale)
    recalculate_geometry = False
    if anim_state.get('factory_last_dims_scale') != current_dims_scale:
        print(f"Factory BG: Dimensions/Scale changed from {anim_state.get('factory_last_dims_scale')} to {current_dims_scale}. Recalculating geometry & fonts.")
        recalculate_geometry = True
        anim_state['factory_last_dims_scale'] = current_dims_scale

        # --- Font Size Recalculation ---
        # (Moved inside the recalculation block)
        crt_width_logic_init = arena_width * 0.3
        crt_height_logic_init = arena_height * 0.25
        crt_rect_scaled_init = scale_rect_func(pygame.Rect(center_x_logic - crt_width_logic_init / 2, center_y_logic - crt_height_logic_init / 2, crt_width_logic_init, crt_height_logic_init))
        inner_screen_rect_init = crt_rect_scaled_init.inflate(-max(2, int(5 * scale))*1.5 * 2, -max(2, int(5 * scale))*1.5* 2)
        eye_radius_x_init = inner_screen_rect_init.width * 0.35
        eye_radius_y_init = inner_screen_rect_init.height * 0.35
        pupil_radius_init = min(eye_radius_x_init, eye_radius_y_init) * 0.6

        font_size_small_init = max(1, int(pupil_radius_init * 0.15))
        font_size_large_init = max(8, int(pupil_radius_init * 1.2))
        try:
            anim_state['factory_small_font'] = pygame.font.Font(None, font_size_small_init)
            anim_state['factory_large_font'] = pygame.font.Font(None, font_size_large_init)
        except Exception as e_font:
            print(f"Warning: Failed to load default font, falling back to SysFont: {e_font}")
            try:
                 anim_state['factory_small_font'] = pygame.font.SysFont("monospace", font_size_small_init)
                 anim_state['factory_large_font'] = pygame.font.SysFont("monospace", font_size_large_init)
            except Exception as e_sysfont:
                 print(f"ERROR: Failed to load ANY font: {e_sysfont}")
                 anim_state['factory_small_font'] = None
                 anim_state['factory_large_font'] = None

        # --- PCB Geometry Recalculation ---
        # (Moved inside the recalculation block)
        anim_state['factory_pcb_geometry'] = {}
        pcb_geo = anim_state['factory_pcb_geometry']

        # Store calculated scaled sizes
        pcb_geo['trace_thickness_main'] = max(1, int(2 * scale))
        pcb_geo['trace_thickness_shadow'] = max(2, int(3 * scale)) # Shadow slightly thicker
        pcb_geo['trace_shadow_offset'] = max(1, int(1 * scale))
        pcb_geo['solder_radius'] = max(2, int(3 * scale))
        pcb_geo['solder_radius_dark'] = max(1, int(1.5 * scale))
        pcb_geo['solder_highlight_offset'] = max(1, int(1 * scale))

        pcb_geo['h_buses'] = []
        pcb_geo['v_buses'] = []
        pcb_geo['solder_points'] = []
        pcb_geo['detail_traces'] = [] # Keep empty

        num_horizontal_buses_init = 8
        num_vertical_buses_init = 10

        # Define the central CRT area again for generation logic
        crt_avoid_width_logic_init = arena_width * 0.35
        crt_avoid_height_logic_init = arena_height * 0.30
        crt_avoid_rect_logic_init = pygame.Rect(
            center_x_logic - crt_avoid_width_logic_init / 2,
            center_y_logic - crt_avoid_height_logic_init / 2,
            crt_avoid_width_logic_init, crt_avoid_height_logic_init
        )

        # Generate horizontal buses (Store logical coords first)
        h_bus_y_coords = []
        num_lines_per_bus = 3
        bus_spacing_logic = 2 * 1.5 # Logical spacing based on trace thickness 2
        for i in range(num_horizontal_buses_init):
            y_logic = (i + 1) * (arena_height / (num_horizontal_buses_init + 1))
            if crt_avoid_rect_logic_init.top < (y_logic - bus_spacing_logic * (num_lines_per_bus / 2)) and \
               crt_avoid_rect_logic_init.bottom > (y_logic + bus_spacing_logic * (num_lines_per_bus / 2)):
                continue
            h_bus_y_coords.append(y_logic)
            start_x = 0
            end_x = arena_width
            for j in range(num_lines_per_bus):
                offset = (j - (num_lines_per_bus - 1) / 2) * bus_spacing_logic
                # Store logical points for scaling later during drawing
                pcb_geo['h_buses'].append(((start_x, y_logic + offset), (end_x, y_logic + offset)))

        # Generate vertical buses (Store logical coords first)
        v_bus_x_coords = []
        for i in range(num_vertical_buses_init):
            x_logic = (i + 1) * (arena_width / (num_vertical_buses_init + 1))
            if crt_avoid_rect_logic_init.left < (x_logic - bus_spacing_logic * (num_lines_per_bus / 2)) and \
               crt_avoid_rect_logic_init.right > (x_logic + bus_spacing_logic * (num_lines_per_bus / 2)):
                continue
            v_bus_x_coords.append(x_logic)
            start_y = 0
            end_y = arena_height
            for j in range(num_lines_per_bus):
                offset = (j - (num_lines_per_bus - 1) / 2) * bus_spacing_logic
                # Store logical points for scaling later during drawing
                pcb_geo['v_buses'].append(((x_logic + offset, start_y), (x_logic + offset, end_y)))

        # Generate solder points (Store logical coords first)
        for y_logic in h_bus_y_coords:
            for x_logic in v_bus_x_coords:
                if not crt_avoid_rect_logic_init.collidepoint(x_logic, y_logic):
                    # Store logical point for scaling later during drawing
                    pcb_geo['solder_points'].append((x_logic, y_logic))

    # --- Draw PCB Elements (Using Calculated Geometry) ---
    if 'factory_pcb_geometry' in anim_state:
        pcb_geo = anim_state['factory_pcb_geometry']
        trace_thickness_main_scaled = pcb_geo['trace_thickness_main']
        trace_thickness_shadow_scaled = pcb_geo['trace_thickness_shadow']
        trace_shadow_offset_scaled = pcb_geo['trace_shadow_offset']
        solder_radius_scaled = pcb_geo['solder_radius']
        solder_radius_dark_scaled = pcb_geo['solder_radius_dark']
        solder_highlight_offset_scaled = pcb_geo['solder_highlight_offset']
        trace_shadow_col = colors.get('CIRCUIT_TRACE_SHADOW', (25, 30, 30))
        solder_highlight_col = colors.get('SOLDER_POINT_HIGHLIGHT', (240, 190, 60))

        # Draw buses with shadows
        for p1_logic, p2_logic in pcb_geo.get('h_buses', []) + pcb_geo.get('v_buses', []):
            p1_scaled = scale_rect_func(pygame.Rect(p1_logic[0], p1_logic[1], 0, 0)).center
            p2_scaled = scale_rect_func(pygame.Rect(p2_logic[0], p2_logic[1], 0, 0)).center
            # Shadow (offset down-right)
            p1_shadow = (p1_scaled[0] + trace_shadow_offset_scaled, p1_scaled[1] + trace_shadow_offset_scaled)
            p2_shadow = (p2_scaled[0] + trace_shadow_offset_scaled, p2_scaled[1] + trace_shadow_offset_scaled)
            pygame.draw.line(surface, trace_shadow_col, p1_shadow, p2_shadow, trace_thickness_shadow_scaled)
            # Main trace
            pygame.draw.line(surface, trace_main, p1_scaled, p2_scaled, trace_thickness_main_scaled)

        # Draw solder points with bevel effect
        for pos_logic in pcb_geo.get('solder_points', []):
            pos_scaled = scale_rect_func(pygame.Rect(pos_logic[0], pos_logic[1], 0, 0)).center
            # Dark base/shadow
            pygame.draw.circle(surface, solder_point_dark, pos_scaled, solder_radius_scaled)
            # Highlight (offset up-left)
            pos_highlight = (pos_scaled[0] - solder_highlight_offset_scaled, pos_scaled[1] - solder_highlight_offset_scaled)
            pygame.draw.circle(surface, solder_highlight_col, pos_highlight, int(solder_radius_scaled * 0.6)) # Smaller highlight circle
            # Main solder color (slightly offset from highlight)
            pos_main = (pos_scaled[0] - solder_highlight_offset_scaled // 2, pos_scaled[1] - solder_highlight_offset_scaled // 2)
            pygame.draw.circle(surface, solder_point, pos_main, int(solder_radius_scaled * 0.8))


    # --- Initialize One-Time Animation States ---
    # (Only run if factory_initialized flag is not set)
    if 'factory_initialized' not in anim_state:
        anim_state['factory_initialized'] = True # Mark as initialized

        # --- Eye State Init ---
        anim_state['factory_eye_blink_timer'] = 0.0
        anim_state['factory_eye_is_open'] = True
        anim_state['factory_eye_blink_duration'] = 0.2
        anim_state['factory_eye_open_interval'] = 5.0 # Set fixed 5 second open interval
        anim_state['factory_pupil_number'] = random.randint(0, 9)
        anim_state['factory_pupil_number_timer'] = 0.0
        anim_state['factory_pupil_number_interval'] = 0.1

        # --- Font Loading ---
        # Calculate font sizes based on a typical pupil radius (needs CRT dimensions first)
        crt_width_logic_init = arena_width * 0.3
        crt_height_logic_init = arena_height * 0.25
        # Estimate scaled CRT rect for font size calculation (might not be perfect if scale changes drastically)
        crt_rect_scaled_init = scale_rect_func(pygame.Rect(center_x_logic - crt_width_logic_init / 2, center_y_logic - crt_height_logic_init / 2, crt_width_logic_init, crt_height_logic_init))
        inner_screen_rect_init = crt_rect_scaled_init.inflate(-max(2, int(5 * scale))*1.5 * 2, -max(2, int(5 * scale))*1.5* 2)
        eye_radius_x_init = inner_screen_rect_init.width * 0.35
        eye_radius_y_init = inner_screen_rect_init.height * 0.35
        pupil_radius_init = min(eye_radius_x_init, eye_radius_y_init) * 0.6

        font_size_small_init = max(1, int(pupil_radius_init * 0.15))
        font_size_large_init = max(8, int(pupil_radius_init * 1.2))
        try:
            # Try loading default font first
            anim_state['factory_small_font'] = pygame.font.Font(None, font_size_small_init)
            anim_state['factory_large_font'] = pygame.font.Font(None, font_size_large_init)
        except Exception as e_font:
            print(f"Warning: Failed to load default font, falling back to SysFont: {e_font}")
            try:
                 # Fallback to monospace system font
                 anim_state['factory_small_font'] = pygame.font.SysFont("monospace", font_size_small_init)
                 anim_state['factory_large_font'] = pygame.font.SysFont("monospace", font_size_large_init)
            except Exception as e_sysfont:
                 print(f"ERROR: Failed to load ANY font: {e_sysfont}")
                 # Store None to prevent errors later, though text won't render
                 anim_state['factory_small_font'] = None
                 anim_state['factory_large_font'] = None


        # --- Piston State Init ---
        anim_state['factory_pistons'] = []
        # Define piston positions symmetrically (example positions)
        piston_y_offset = arena_height * 0.15
        piston_x_offset = arena_width * 0.3
        piston_positions_logic = [
            (piston_x_offset, piston_y_offset), (arena_width - piston_x_offset, piston_y_offset),
            (piston_x_offset, arena_height - piston_y_offset), (arena_width - piston_x_offset, arena_height - piston_y_offset)
        ]
        for i, pos in enumerate(piston_positions_logic):
            anim_state['factory_pistons'].append({
                'id': i, 'pos_logic': pos, 'state': 'down', # 'down', 'up', 'steaming'
                'timer': random.uniform(0.0, 3.0), # Random start time
                'up_interval': random.uniform(4.0, 8.0),
                'up_duration': 0.5,
                'steam_duration': 0.3
            })

        # --- Tesla Coil State Init ---
        anim_state['factory_tesla_coils'] = []
        # Define coil positions symmetrically (example positions)
        coil_y_offset = arena_height * 0.35
        coil_x_offset = arena_width * 0.1
        coil_positions_logic = [
             (coil_x_offset, coil_y_offset), (arena_width - coil_x_offset, coil_y_offset),
             (coil_x_offset, arena_height - coil_y_offset), (arena_width - coil_x_offset, arena_height - coil_y_offset)
        ]
        for i, pos in enumerate(coil_positions_logic):
             anim_state['factory_tesla_coils'].append({
                 'id': i, 'pos_logic': pos,
                 'timer': random.uniform(0.0, 2.0),
                 'spark_interval': random.uniform(1.5, 4.0),
                 'spark_duration': 0.15,
                 'sparking': False,
                 'spark_points': [] # Points for the lightning effect
             })

        # --- Piston/Tesla Position Recalculation (if needed, though less critical than PCB/fonts) ---
        # Example: If piston/tesla positions were relative to arena size, recalculate here.
        # Currently, they seem fixed relative offsets, so maybe not needed unless logic changes.
        # if recalculate_geometry: # Or a separate check if needed
        #    # Recalculate piston_positions_logic, coil_positions_logic based on new arena_width/height
        #    # Update pos_logic in anim_state['factory_pistons'] and anim_state['factory_tesla_coils']
        #    pass # Placeholder

        # End of the initialization block

    # --- Draw Central CRT Screen ---
    crt_width_logic = arena_width * 0.25  # Smaller width
    crt_height_logic = arena_height * 0.2  # Smaller height
    crt_rect_logic = pygame.Rect(
        center_x_logic - crt_width_logic / 2,
        center_y_logic - crt_height_logic / 2,
        crt_width_logic, crt_height_logic
    )
    crt_rect_scaled = scale_rect_func(crt_rect_logic)
    border_thickness_scaled = max(2, int(5 * scale))

    # Draw border and screen
    pygame.draw.rect(surface, crt_border, crt_rect_scaled, border_thickness_scaled, border_radius=int(3*scale))
    inner_screen_rect = crt_rect_scaled.inflate(-border_thickness_scaled*1.5, -border_thickness_scaled*1.5) # Slightly less inflation for effect
    if inner_screen_rect.width > 0 and inner_screen_rect.height > 0:
        # Draw screen background with subtle gradient/scanlines
        screen_surf = pygame.Surface(inner_screen_rect.size, pygame.SRCALPHA)
        screen_surf.fill(crt_screen)
        # Slightly more visible Scanlines
        scanline_alpha = 25 # Increased alpha
        # Use a slightly brighter grey for scanlines on black background
        scanline_color = (25, 25, 25, scanline_alpha)
        for y in range(0, int(inner_screen_rect.height), max(2, int(3 * scale))):
             pygame.draw.line(screen_surf, scanline_color, (0, y), (inner_screen_rect.width, y), 1)
        # Subtle vertical gradient (darker at edges)
        gradient_strength = 15
        for x in range(int(inner_screen_rect.width)):
            alpha = int(gradient_strength * (1 - abs(x - inner_screen_rect.width / 2) / (inner_screen_rect.width / 2)))
            pygame.draw.line(screen_surf, (0,0,0, alpha), (x, 0), (x, inner_screen_rect.height), 1)

        surface.blit(screen_surf, inner_screen_rect.topleft)


    # --- Draw Blinking Eye (with Tracking) ---

    # Create a dedicated surface for the eye, matching the inner screen size
    eye_surface = pygame.Surface(inner_screen_rect.size, pygame.SRCALPHA)
    eye_surface.fill((0, 0, 0, 0)) # Fill with transparent

    # Center of the eye *relative to the eye_surface*
    eye_surface_center = (inner_screen_rect.width // 2, inner_screen_rect.height // 2)

    # Radii based on the eye_surface dimensions
    # Make eye proportional to smaller screen
    eye_radius_x_scaled = inner_screen_rect.width * 0.35
    eye_radius_y_scaled = inner_screen_rect.height * 0.35
    pupil_radius_scaled = min(eye_radius_x_scaled, eye_radius_y_scaled) * 0.4

    # --- Eye Tracking Logic ---
    # Initialize eye tracking state if not exists
    if 'eye_pos' not in anim_state:
        anim_state['eye_pos'] = {'x': eye_surface_center[0], 'y': eye_surface_center[1]}
    
    balls = [obj for obj in game_objects if obj.__class__.__name__ == 'BallObject']
    target_pos = None

    if balls and len(balls) > 0:
        ball = balls[0]  # Track the first ball
        if hasattr(ball, 'rect'):
            # Convert ball position to eye surface space
            ball_x = ball.rect.centerx - inner_screen_rect.left
            ball_y = ball.rect.centery - inner_screen_rect.top
            target_pos = (ball_x, ball_y)

    # Smooth movement interpolation
    current_pos = anim_state['eye_pos']
    
    # Set default target to center if no ball
    target_x = eye_surface_center[0]
    target_y = eye_surface_center[1]
    
    if target_pos:
        # Clamp target position within eye bounds
        max_offset = min(eye_radius_x_scaled, eye_radius_y_scaled) * 0.4
        dx = target_pos[0] - eye_surface_center[0]
        dy = target_pos[1] - eye_surface_center[1]
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            scale = min(max_offset, dist) / dist
            target_x = eye_surface_center[0] + dx * scale
            target_y = eye_surface_center[1] + dy * scale
    
    # Smooth interpolation
    lerp_speed = 10.0 * dt  # Adjust for smoother/faster tracking
    current_pos['x'] += (target_x - current_pos['x']) * lerp_speed
    current_pos['y'] += (target_y - current_pos['y']) * lerp_speed

    # Final pupil position
    pupil_draw_pos_on_surface = (current_pos['x'], current_pos['y'])


    # Update blink timer
    anim_state['factory_eye_blink_timer'] += dt
    if anim_state['factory_eye_is_open']:
        if anim_state['factory_eye_blink_timer'] >= anim_state['factory_eye_open_interval']:
            anim_state['factory_eye_is_open'] = False
            anim_state['factory_eye_blink_timer'] = 0.0
            # Reset interval to the fixed value
            anim_state['factory_eye_open_interval'] = 5.0 # Set fixed 5 second open interval
    else: # Eye is closed (blinking)
        if anim_state['factory_eye_blink_timer'] >= anim_state['factory_eye_blink_duration']:
            anim_state['factory_eye_is_open'] = True
            anim_state['factory_eye_blink_timer'] = 0.0
            # Change the big number when blink finishes
            anim_state['factory_pupil_number'] = random.randint(0, 9)


    if anim_state['factory_eye_is_open']:
        # Draw open eye components onto the eye_surface
        if eye_radius_x_scaled > 0 and eye_radius_y_scaled > 0:
            # Draw outer glow (larger, more transparent) onto eye_surface
            # Enhanced glow effect
            glow_radius_x = eye_radius_x_scaled * 1.8
            glow_radius_y = eye_radius_y_scaled * 1.8
            glow_color = (eye_glow[0], eye_glow[1], eye_glow[2], 80) # More subtle glow
            # Use eye_surface_center for positioning on the eye_surface
            glow_rect_on_surface = pygame.Rect(0, 0, glow_radius_x * 2, glow_radius_y * 2)
            glow_rect_on_surface.center = eye_surface_center
            pygame.draw.ellipse(eye_surface, glow_color, glow_rect_on_surface) # Draw directly on eye_surface

            # Draw main eye ellipse (using eye_surface_center)
            eye_rect_on_surface = pygame.Rect(eye_surface_center[0] - eye_radius_x_scaled, eye_surface_center[1] - eye_radius_y_scaled,
                                              eye_radius_x_scaled * 2, eye_radius_y_scaled * 2)
            pygame.draw.ellipse(eye_surface, eye_glow, eye_rect_on_surface)

            # Inner, slightly darker ring (using eye_surface_center)
            inner_eye_color = (max(0, eye_glow[0]-40), max(0, eye_glow[1]-10), max(0, eye_glow[2]-10))
            inner_radius_x = eye_radius_x_scaled * 0.85
            inner_radius_y = eye_radius_y_scaled * 0.85
            inner_eye_rect_on_surface = pygame.Rect(eye_surface_center[0] - inner_radius_x, eye_surface_center[1] - inner_radius_y,
                                                    inner_radius_x * 2, inner_radius_y * 2)
            pygame.draw.ellipse(eye_surface, inner_eye_color, inner_eye_rect_on_surface, width=max(1, int(2*scale))) # Draw as outline

            # Draw pupil (darker circle with changing numbers) - uses pupil_draw_pos_on_surface
            if pupil_radius_scaled >= 1:
                # Add subtle pulsing to pupil background
                pulse_factor = 0.9 + 0.1 * math.sin(time.time() * 5) # Simple time-based pulse
                current_pupil_radius = int(pupil_radius_scaled * pulse_factor)
                current_pupil_bg = (max(0, eye_pupil_bg[0] + int(10 * pulse_factor) - 5), eye_pupil_bg[1], eye_pupil_bg[2])
                # Use the calculated pupil_draw_pos_on_surface for drawing the pupil
                pygame.draw.circle(eye_surface, current_pupil_bg, pupil_draw_pos_on_surface, current_pupil_radius)

                # Update and draw changing numbers in pupil (around the pupil_draw_pos_on_surface)
                anim_state['factory_pupil_number_timer'] += dt
                if anim_state['factory_pupil_number_timer'] >= anim_state['factory_pupil_number_interval']:
                    anim_state['factory_pupil_number_timer'] = 0.0
                    # Draw small random numbers around the main one - with varied size/alpha
                    num_small_numbers = 25 # Increased number of background digits
                    base_font_size_small = max(1, int(pupil_radius_scaled * 0.2))

                    for _ in range(num_small_numbers):
                        angle = random.uniform(0, 2 * math.pi)
                        dist = random.uniform(current_pupil_radius * 0.2, current_pupil_radius * 0.9) # Use current radius
                        # Use pupil_draw_pos_on_surface for number positioning
                        num_x = pupil_draw_pos_on_surface[0] + dist * math.cos(angle)
                        num_y = pupil_draw_pos_on_surface[1] + dist * math.sin(angle)

                        # Vary size and alpha
                        current_font_size = max(1, base_font_size_small + random.randint(-1, 2))
                        current_alpha = random.randint(100, 220)
                        current_num_color = (eye_number[0], eye_number[1], eye_number[2], current_alpha)

                        small_font = anim_state.get('factory_small_font') # Get pre-loaded font
                        if small_font: # Check if font loaded successfully
                             num_surf = small_font.render(str(random.randint(0,9)), True, current_num_color)
                             # Create a surface with per-pixel alpha for the number
                             num_alpha_surf = pygame.Surface(num_surf.get_size(), pygame.SRCALPHA)
                             num_alpha_surf.blit(num_surf, (0,0))
                             num_alpha_surf.set_alpha(current_alpha) # Apply overall alpha too

                             num_rect = num_alpha_surf.get_rect(center=(int(num_x), int(num_y)))
                             eye_surface.blit(num_alpha_surf, num_rect) # Blit onto eye_surface


                # Draw the large central number
                font_size_large = max(8, int(pupil_radius_scaled * 1.2))
                large_font = anim_state.get('factory_large_font') # Get pre-loaded font
                if large_font: # Check if font loaded successfully
                     num_surf_large = large_font.render(str(anim_state['factory_pupil_number']), True, eye_number)
                     # Use pupil_draw_pos_on_surface for the large number's center
                     num_rect_large = num_surf_large.get_rect(center=pupil_draw_pos_on_surface)
                     eye_surface.blit(num_surf_large, num_rect_large) # Blit onto eye_surface

    else:
        # Draw closed eye (thin horizontal line) onto eye_surface
        # Use eye_surface_center for positioning
        line_y = eye_surface_center[1]
        line_start_x = eye_surface_center[0] - eye_radius_x_scaled
        line_end_x = eye_surface_center[0] + eye_radius_x_scaled
        line_thickness = max(1, int(3 * scale))
        pygame.draw.line(eye_surface, eye_glow, (line_start_x, line_y), (line_end_x, line_y), line_thickness)

    # Finally, blit the complete eye_surface onto the main surface at the inner screen position
    surface.blit(eye_surface, inner_screen_rect.topleft)


    # --- Piston and Tesla Coil drawing removed ---
    # This logic is now handled by PistonObstacle and TeslaCoilObstacle classes
    # in Ping_Obstacles.py

    # --- Apply Lighting Overlay ---
    if has_lighting:
        max_darkness_alpha = 200
        overlay_alpha = int(max_darkness_alpha * (1 - (lighting_level / 100.0)))
        overlay_alpha = max(0, min(255, overlay_alpha))

        if overlay_alpha > 0:
            lighting_overlay = pygame.Surface(game_area_rect.size, pygame.SRCALPHA)
            lighting_overlay.fill((0, 0, 0, overlay_alpha))
            surface.blit(lighting_overlay, game_area_rect.topleft)

# --- Populate Background Definitions ---
# Add backgrounds to the dictionary *after* their functions are defined.
AVAILABLE_BACKGROUNDS["sewer"] = draw_sewer_background
AVAILABLE_BACKGROUNDS["casino"] = draw_casino_background
AVAILABLE_BACKGROUNDS["factory"] = draw_factory_background
AVAILABLE_BACKGROUNDS["haunted_hovel"] = draw_haunted_hovel_background
# Add more backgrounds here in the future, e.g.:
# AVAILABLE_BACKGROUNDS["factory"] = draw_factory_background

# --- Accessor Functions ---

def get_available_backgrounds():
    """Returns a list of identifiers for available backgrounds."""
    return list(AVAILABLE_BACKGROUNDS.keys())

def get_background_draw_function(identifier):
    """
    Returns the drawing function associated with the given background identifier.
    Returns None if the identifier is not found.
    """
    return AVAILABLE_BACKGROUNDS.get(identifier)

def get_background_theme_colors(identifier):
    """
    Returns the color dictionary for the specified background theme.
    Returns an empty dictionary if the identifier is not found or has no theme.
    """
    return BACKGROUND_COLOR_THEMES.get(identifier, {}) # Return theme or empty dict