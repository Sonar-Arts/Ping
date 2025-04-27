import pygame
import time
import random
from .Ping_Fonts import get_pixel_font

def _generate_random_color(min_brightness=50):
    """Generates a random RGB color tuple with minimum brightness."""
    while True:
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # Basic brightness check (sum of components)
        if sum(color) >= min_brightness * 3:
            return color

def _create_jagged_polygon(x, y, width, height, jagged_amplitude, jagged_frequency, direction='left'):
    """Creates points for a rectangle with one jagged vertical edge."""
    points = []
    if direction == 'left':
        # Top-left straight edge start
        points.append((x + width, y))
        # Bottom-left straight edge start
        points.append((x + width, y + height))
        # Bottom-right jagged edge start
        points.append((x, y + height))
        # Create jagged points upwards
        num_jags = int(height / jagged_frequency) if jagged_frequency > 0 else 0 # Avoid division by zero
        for i in range(num_jags, 0, -1):
            jag_y = y + i * jagged_frequency
            jag_x_offset = random.uniform(-jagged_amplitude / 2, jagged_amplitude / 2) # More randomness
            jag_x = x + (jagged_amplitude / 2) + jag_x_offset if (i % 2 == 0) else x - (jagged_amplitude / 2) + jag_x_offset
            points.append((max(x - jagged_amplitude, min(x + jagged_amplitude, jag_x)), jag_y)) # Clamp x
        # Top-right jagged edge end (connects near top left)
        points.append((x, y))
    else: # direction == 'right'
        # Top-right straight edge start
        points.append((x, y))
        # Bottom-right straight edge start
        points.append((x, y + height))
        # Bottom-left jagged edge start
        points.append((x + width, y + height))
        # Create jagged points upwards
        num_jags = int(height / jagged_frequency) if jagged_frequency > 0 else 0 # Avoid division by zero
        for i in range(num_jags, 0, -1):
            jag_y = y + i * jagged_frequency
            jag_x_offset = random.uniform(-jagged_amplitude / 2, jagged_amplitude / 2)
            jag_x = x + width - (jagged_amplitude / 2) + jag_x_offset if (i % 2 == 0) else x + width + (jagged_amplitude / 2) + jag_x_offset
            points.append((max(x, min(x + width + jagged_amplitude, jag_x)), jag_y)) # Clamp x
        # Top-left jagged edge end
        points.append((x + width, y))

    return points

def _render_text_with_outline(font, text, text_color, outline_color=(0, 0, 0), outline_px=2):
    """Renders text with a simple outline by blitting offset background copies."""
    # Render the main text
    text_surface = font.render(text, True, text_color).convert_alpha()
    w, h = text_surface.get_size()

    # Create a slightly larger surface to accommodate the outline
    outline_surface = pygame.Surface((w + outline_px * 2, h + outline_px * 2), pygame.SRCALPHA)
    outline_surface.fill((0,0,0,0)) # Transparent background

    # Render the outline text (multiple times for thicker outline)
    outline_text = font.render(text, True, outline_color).convert_alpha()

    # Blit outline copies shifted in 8 directions
    for dx in range(-outline_px, outline_px + 1, outline_px):
         for dy in range(-outline_px, outline_px + 1, outline_px):
             if dx == 0 and dy == 0: # Skip the center position
                 continue
             outline_surface.blit(outline_text, (outline_px + dx, outline_px + dy))

    # Blit the main text on top
    outline_surface.blit(text_surface, (outline_px, outline_px))

    return outline_surface, outline_surface.get_rect()


def play_level_intro(screen, clock, level_name, width, height, scale_y, colors, draw_background_func):
    """
    Plays a 'Sonic-style' sliding level intro animation with jagged edges and randomized colors.
    Text is drawn on top with a black outline.

    Args:
        screen: The main pygame display surface.
        clock: The pygame Clock object.
        level_name: The string name of the level (e.g., "Manhole Mayhem").
        width: Current screen width.
        height: Current screen height.
        scale_y: Vertical scaling factor for UI elements (used for font scaling).
        colors: A dictionary containing color definitions (used for text color 'WHITE').
        draw_background_func: A function to draw the static background (currently unused by this animation).
    """
    game_name = "Ping"
    outline_color = (0, 0, 0) # Black outline

    # --- Animation Parameters ---
    slide_duration = 0.6
    pause_duration = 1.5
    jagged_amplitude = max(5, int(30 * scale_y)) # Ensure minimum amplitude
    jagged_frequency = max(5, int(10 * scale_y)) # Ensure minimum frequency > 0

    # --- Panel Definitions ---
    panel_color1 = _generate_random_color()
    panel_color2 = _generate_random_color()
    panel_color3 = _generate_random_color()

    panel1_height = height * 0.60
    panel2_height = height * 0.25
    panel3_height = height * 0.15

    panel1_y = 0
    panel2_y = panel1_height
    panel3_y = panel1_height + panel2_height

    panel1_start_x = -width
    panel1_end_x = 0
    panel2_start_x = width
    panel2_end_x = 0
    panel3_start_x = -width
    panel3_end_x = 0

    # --- Text Definitions ---
    text_color = colors.get('WHITE', (255, 255, 255))
    level_font_size = max(24, int(60 * scale_y))
    zone_font_size = max(20, int(45 * scale_y))
    game_font_size = max(16, int(30 * scale_y))
    outline_px = max(1, int(2 * scale_y)) # Scale outline thickness, ensure at least 1px

    level_font = get_pixel_font(level_font_size)
    zone_font = get_pixel_font(zone_font_size)
    game_font = get_pixel_font(game_font_size)

    level_words = level_name.upper().split()
    zone_text = ""
    if len(level_words) > 1 and level_words[-1] in ["ZONE", "LEVEL", "AREA"]:
        zone_text = level_words.pop()
    level_text_line = " ".join(level_words)

    # Render text with outline
    level_surf, level_rect = _render_text_with_outline(level_font, level_text_line, text_color, outline_color, outline_px)
    zone_surf, zone_rect = (None, None)
    if zone_text:
        zone_surf, zone_rect = _render_text_with_outline(zone_font, zone_text, text_color, outline_color, outline_px)
    game_surf, game_rect = _render_text_with_outline(game_font, game_name.upper(), text_color, outline_color, outline_px)

    # Text target positions
    level_target_x = width * 0.45
    level_target_y = panel1_height * 0.5
    zone_target_x = width * 0.75
    zone_target_y = level_target_y + level_rect.height * 0.6 # Position relative to level text height
    game_target_x = width * 0.75
    game_target_y = panel1_height + panel2_height + (panel3_height * 0.5)

    # Set initial rect centers based on target positions
    level_rect.center = (level_target_x, level_target_y)
    if zone_rect:
        zone_rect.center = (zone_target_x, zone_target_y)
    game_rect.center = (game_target_x, game_target_y)

    # Text initial off-screen positions (use rect width which includes outline)
    level_start_x = -level_rect.width
    zone_start_x = width + (zone_rect.width if zone_rect else 0)
    game_start_x = width + game_rect.width

    # --- Animation Loop ---
    start_time = time.time()
    stage = "slide_in"

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if stage == "slide_in" and elapsed_time >= slide_duration:
            stage = "pause"
            start_time = current_time
            elapsed_time = 0
        elif stage == "pause" and elapsed_time >= pause_duration:
            stage = "slide_out"
            start_time = current_time
            elapsed_time = 0
        elif stage == "slide_out" and elapsed_time >= slide_duration:
            break

        progress = 0
        if stage == "slide_in":
            progress = min(1.0, elapsed_time / slide_duration)
        elif stage == "slide_out":
            progress = max(0.0, 1.0 - (elapsed_time / slide_duration))
        elif stage == "pause":
            progress = 1.0

        # Interpolate panel positions
        panel1_current_x = panel1_start_x + (panel1_end_x - panel1_start_x) * progress
        panel2_current_x = panel2_start_x + (panel2_end_x - panel2_start_x) * progress
        panel3_current_x = panel3_start_x + (panel3_end_x - panel3_start_x) * progress

        # Interpolate text positions using the original target center coordinates
        level_current_x = level_start_x + (level_target_x - level_start_x) * progress
        zone_current_x = zone_start_x + ((zone_target_x if zone_rect else width) - zone_start_x) * progress
        game_current_x = game_start_x + (game_target_x - game_start_x) * progress

        # --- Drawing ---
        screen.fill((0, 0, 0)) # Clear screen

        # Draw Panels FIRST
        panel1_points = _create_jagged_polygon(panel1_current_x, panel1_y, width, panel1_height, jagged_amplitude, jagged_frequency, direction='right')
        pygame.draw.polygon(screen, panel_color1, panel1_points)

        panel2_points = _create_jagged_polygon(panel2_current_x, panel2_y, width, panel2_height, jagged_amplitude, jagged_frequency, direction='left')
        pygame.draw.polygon(screen, panel_color2, panel2_points)

        panel3_points = _create_jagged_polygon(panel3_current_x, panel3_y, width, panel3_height, jagged_amplitude, jagged_frequency, direction='right')
        pygame.draw.polygon(screen, panel_color3, panel3_points)

        # Draw Text LAST (on top of panels)
        # Update rect center for blitting based on interpolated position
        current_level_rect = level_surf.get_rect(center=(level_current_x, level_target_y))
        screen.blit(level_surf, current_level_rect)

        if zone_surf and zone_rect:
            current_zone_rect = zone_surf.get_rect(center=(zone_current_x, zone_target_y))
            screen.blit(zone_surf, current_zone_rect)

        current_game_rect = game_surf.get_rect(center=(game_current_x, game_target_y))
        screen.blit(game_surf, current_game_rect)

        pygame.display.flip()

    # --- End of Animation ---