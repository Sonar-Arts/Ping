"""
Module for handling game graphics, specifically level backgrounds.
"""

import pygame
import random
import math
import pygame # Ensure pygame is imported if not already

import os # Needed for path manipulation

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


import time # Import time for blinking animation

import math # Ensure math is imported for angles

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
    # border_thickness_ratio = 0.04 # Removed wood border
    # border_thickness_logic = arena_width * border_thickness_ratio # Removed wood border
    inner_x_start_logic = 0 # Start from edge
    inner_y_start_logic = scoreboard_height # Start from scoreboard
    inner_width_logic = arena_width # Use full width
    inner_height_logic = arena_height - scoreboard_height # Use full height below scoreboard
    # inner_rect_logic = pygame.Rect(inner_x_start_logic, inner_y_start_logic, inner_width_logic, inner_height_logic) # Not directly used
    inner_center_x_logic = inner_x_start_logic + inner_width_logic / 2

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

    # --- Draw Base Background and Retro Details ---
    full_area_rect_logic = pygame.Rect(0, scoreboard_height, arena_width, arena_height - scoreboard_height)
    scaled_full_area_rect = scale_rect_func(full_area_rect_logic)
    pygame.draw.rect(surface, base_color, scaled_full_area_rect)

    # Add subtle grid lines for more retro detail
    grid_spacing_logic = 50 # Logical pixels between grid lines
    scaled_grid_spacing = max(1, int(grid_spacing_logic * scale))
    grid_color = (base_color[0]+10, base_color[1]+10, base_color[2]+15, 50) # Slightly lighter, semi-transparent

    # Vertical lines
    for x in range(scaled_full_area_rect.left, scaled_full_area_rect.right, scaled_grid_spacing):
        pygame.draw.line(surface, grid_color, (x, scaled_full_area_rect.top), (x, scaled_full_area_rect.bottom), 1)
    # Horizontal lines
    for y in range(scaled_full_area_rect.top, scaled_full_area_rect.bottom, scaled_grid_spacing):
        pygame.draw.line(surface, grid_color, (scaled_full_area_rect.left, y), (scaled_full_area_rect.right, y), 1)


    # --- Draw Wooden Border --- (Removed)
    # top_border_rect = scale_rect_func(pygame.Rect(0, scoreboard_height, arena_width, border_thickness_logic))
    # pygame.draw.rect(surface, wood_border_color, top_border_rect)
    # bottom_border_rect = scale_rect_func(pygame.Rect(0, arena_height - border_thickness_logic, arena_width, border_thickness_logic))
    # pygame.draw.rect(surface, wood_border_color, bottom_border_rect)
    # left_border_rect = scale_rect_func(pygame.Rect(0, scoreboard_height + border_thickness_logic, border_thickness_logic, arena_height - scoreboard_height - 2 * border_thickness_logic))
    # pygame.draw.rect(surface, wood_border_color, left_border_rect)
    # right_border_rect = scale_rect_func(pygame.Rect(arena_width - border_thickness_logic, scoreboard_height + border_thickness_logic, border_thickness_logic, arena_height - scoreboard_height - 2 * border_thickness_logic))
    # pygame.draw.rect(surface, wood_border_color, right_border_rect)

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
    shadow_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
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
            lighting_overlay = pygame.Surface(scaled_full_area_rect.size, pygame.SRCALPHA)
            lighting_overlay.fill((0, 0, 0, overlay_alpha))
            surface.blit(lighting_overlay, scaled_full_area_rect.topleft)

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

# Dictionary mapping background identifiers to their color themes
BACKGROUND_COLOR_THEMES = {
    "casino": CASINO_COLORS,
    "sewer": SEWER_COLORS,
    # Add themes for other backgrounds here
}

# --- Background Definitions ---

# Dictionary mapping background identifiers to their drawing functions.
AVAILABLE_BACKGROUNDS = {} # Initialize first

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

    # Get background details directly from the compiler instance attribute
    background_details = compiler_instance.background_details # Direct access
    if not background_details:
        print("Warning: No background_details found in compiler instance for sewer background.")
        # Attempt to use defaults if details are missing entirely
        background_details = {
             'brick_width': 50, 'brick_height': 25, 'river_width_ratio': 0.25,
             'manhole_brick_padding': 5, 'crack_frequency': 0.05,
             'vegetation_frequency': 0.02, 'river_animation_speed': 1
        }
        print("Warning: Using default sewer background details.")
        # Do not return here, proceed with defaults

    # Get level dimensions directly from compiler instance
    arena_width = compiler_instance.width
    arena_height = compiler_instance.height

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
    scaled_river_y_start = scoreboard_height * scale + offset_y
    scaled_river_height = (arena_height - scoreboard_height) * scale

    # --- Draw Brick Pattern ---
    # (Brick drawing logic remains largely the same, using extracted variables)
    for y_logic in range(scoreboard_height, arena_height, brick_h):
        row_offset = (y_logic // brick_h) % 2 * (brick_w // 2)  # Staggered pattern
        for x_logic in range(0, arena_width, brick_w):
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
            pygame.draw.rect(surface, brick_color, scaled_brick_rect)
            pygame.draw.rect(surface, mortar_color, scaled_brick_rect, 1)  # Mortar outline

            # Vegetation drawing (removed crack generation from here)
            if not is_near_manhole:
                veg_freq = details.get('vegetation_frequency', 0.02)
                veg_color = colors.get('VEGETATION_COLOR', (0, 80, 0)) # Keep vegetation color from theme
                # if random.random() < veg_freq: # Keep vegetation random for now
                #      # Ensure scaled rect has positive dimensions before random range
                #     if scaled_brick_rect.width > 5 and scaled_brick_rect.height > 5:
                #         veg_x = scaled_brick_rect.left + random.randint(0, scaled_brick_rect.width - 5)
                #         veg_y = scaled_brick_rect.top + random.randint(0, scaled_brick_rect.height - 5)
                #         # Scale veg size too, ensure minimum size of 1
                #         veg_w = max(1, int(5 * scale))
                #         veg_h = max(1, int(5 * scale))
                #         pygame.draw.rect(surface, veg_color, (veg_x, veg_y, veg_w, veg_h))

                # if random.random() < veg_freq:
                #      # Ensure scaled rect has positive dimensions before random range
                #     if scaled_brick_rect.width > 5 and scaled_brick_rect.height > 5:
                #         veg_x = scaled_brick_rect.left + random.randint(0, scaled_brick_rect.width - 5)
                #         veg_y = scaled_brick_rect.top + random.randint(0, scaled_brick_rect.height - 5)
                #         # Scale veg size too, ensure minimum size of 1
                #         veg_w = max(1, int(5 * scale))
                #         veg_h = max(1, int(5 * scale))
                #         pygame.draw.rect(surface, veg_color, (veg_x, veg_y, veg_w, veg_h))

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

                # Draw the connected line segments (zig-zag)
                pygame.draw.lines(surface, crack_color, False, scaled_points, 1) # False for non-closed polyline

    # --- Draw Sewer River ---
    river_rect = pygame.Rect(scaled_river_x_start, scaled_river_y_start, scaled_river_width, scaled_river_height)
    # Use blue shades for the river (can still use theme colors here)
    # Define murky sludge colors inspired by the image
    sludge_base_color = colors.get('SLUDGE_BASE', (60, 65, 45))
    # Define mid and highlight with alpha for transparency
    sludge_mid_color_rgb = colors.get('SLUDGE_MID', (80, 85, 60))
    sludge_highlight_color_rgb = colors.get('SLUDGE_HIGHLIGHT', (100, 105, 75))

    # Draw the base river rectangle first
    pygame.draw.rect(surface, sludge_base_color, river_rect)

    # --- Animate Sludge Flow ---
    # Ensure valid dimensions for drawing and calculations
    if scaled_river_width > 0 and scaled_river_height > 0:
        anim_speed = details.get('river_animation_speed', 0.5) # Use speed from details, default 0.5
        # Define speed in pixels per second (doubled speed)
        pixels_per_second = anim_speed * scale * 50 # Doubled speed factor

        # Get dt from compiler_instance
        dt = getattr(compiler_instance, 'dt', 1/60.0) # Default to 1/60

        # --- Update Scroll Offset ---
        current_offset = river_animation_offset # Get current offset
        offset_change = pixels_per_second * dt
        texture_height = scaled_river_height # Use river height for looping

        if texture_height > 0:
            new_offset = (current_offset + offset_change) % texture_height
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
            # If not, it might indicate an issue with texture generation or scaling.
            # For now, we proceed, but ideally, they should match.
            if tex_h != int(texture_height):
                 # print(f"Warning: Sludge texture height ({tex_h}) differs from river height ({int(texture_height)}).")
                 # Optionally resize texture here, but it's better to generate it correctly.
                 pass # Proceeding with potentially mismatched texture

            # Calculate the integer offset for blitting
            blit_offset = int(new_offset)

            # Define the area on the main surface where the river is drawn
            target_area = pygame.Rect(scaled_river_x_start, scaled_river_y_start, scaled_river_width, scaled_river_height)

            # Blit the first instance of the texture
            # Source rect starts from the top of the texture
            # Destination y is offset by the negative scroll amount
            src_rect1 = pygame.Rect(0, 0, scaled_river_width, tex_h)
            dest_y1 = scaled_river_y_start - blit_offset
            surface.blit(sludge_texture, (scaled_river_x_start, dest_y1), area=src_rect1, special_flags=pygame.BLEND_RGBA_ADD) # Use additive blend if desired, or remove flag

            # Blit the second instance of the texture, positioned above the first
            # Destination y is offset by texture height minus the scroll amount
            dest_y2 = scaled_river_y_start - blit_offset + tex_h
            surface.blit(sludge_texture, (scaled_river_x_start, dest_y2), area=src_rect1, special_flags=pygame.BLEND_RGBA_ADD) # Use additive blend if desired, or remove flag

            # --- Clipping --- (Optional but recommended)
            # To ensure the sludge only draws within the river_rect bounds,
            # set a clipping rectangle before blitting and reset it after.
            # original_clip = surface.get_clip()
            # surface.set_clip(river_rect)
            # surface.blit(sludge_texture, ...) # Blit 1
            # surface.blit(sludge_texture, ...) # Blit 2
            # surface.set_clip(original_clip)
            # Note: The current blit operations might implicitly handle clipping if
            # the target coordinates are outside the surface, but explicit clipping is safer.

        elif not sludge_texture:
            # Optionally draw a placeholder if texture isn't ready yet
            # pygame.draw.rect(surface, (255, 0, 255), river_rect) # Magenta placeholder
            pass # Or just draw nothing

    # --- Apply Lighting Overlay ---
    if has_lighting:
        max_darkness_alpha = 200
        overlay_alpha = int(max_darkness_alpha * (1 - (lighting_level / 100.0)))
        overlay_alpha = max(0, min(255, overlay_alpha))

        if overlay_alpha > 0:
            game_area_rect = scale_rect_func(pygame.Rect(0, 0, arena_width, arena_height)) # Define game_area_rect
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
AVAILABLE_BACKGROUNDS["casino"] = draw_casino_background # Add the new background
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