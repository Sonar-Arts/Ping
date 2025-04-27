"""
Module for handling game graphics, specifically level backgrounds.
"""

import pygame
import random
import math
import pygame # Ensure pygame is imported if not already

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

    # Offset update is handled within the compiler instance state

# --- Populate Background Definitions ---
# Add backgrounds to the dictionary *after* their functions are defined.
AVAILABLE_BACKGROUNDS["sewer"] = draw_sewer_background
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