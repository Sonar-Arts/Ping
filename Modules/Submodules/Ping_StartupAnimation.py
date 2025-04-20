\
import pygame
import time
import math
import sys # For exit()
from .Ping_Fonts import get_pixel_font # Relative import
from .Ping_Sound import SoundManager # Import sound manager

# Constants
SONAR_COLOR = (0, 200, 0) # Green
TEXT_COLOR = (0, 255, 0) # Brighter Green
BACKGROUND_COLOR = (0, 0, 0) # Black
SUB_COLOR = (100, 100, 150) # Greyish blue
SUB_DETAIL_COLOR = (70, 70, 100) # Darker greyish blue for details
SUB_WINDOW_COLOR = (150, 150, 200) # Lighter blue for window

# --- Added Constants ---
SUB_BOB_FREQUENCY = 4 # How fast the sub bobs
SUB_BOB_AMPLITUDE = 2 # How much the sub bobs (in pixels)
NUM_SONAR_RINGS = 7 # Increased number of rings
# --- End Added Constants ---

SUB_APPEAR_DURATION = 0.5
SONAR_BLAST_DURATION = 1.5
TEXT_REVEAL_DURATION = 0.5
TEXT_HOLD_DURATION = 1.0

SONAR_EXPAND_SPEED_FACTOR = 1.2 # How much faster than screen diagonal radius expands

def draw_submarine(screen, x, y, width, height):
    """Draws a more detailed submarine."""
    # Main body (ellipse)
    body_rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
    pygame.draw.ellipse(screen, SUB_COLOR, body_rect)
    pygame.draw.ellipse(screen, SUB_DETAIL_COLOR, body_rect, 1) # Outline

    # Conning tower (rounded rectangle)
    tower_width = width * 0.25
    tower_height = height * 0.6
    tower_rect = pygame.Rect(x - tower_width // 2, y - height // 2 - tower_height + 2, tower_width, tower_height)
    pygame.draw.rect(screen, SUB_COLOR, tower_rect, border_radius=3)
    pygame.draw.rect(screen, SUB_DETAIL_COLOR, tower_rect, 1, border_radius=3) # Outline

    # Periscope
    periscope_width = 4
    periscope_height = 10
    periscope_rect = pygame.Rect(x - periscope_width // 2, tower_rect.top - periscope_height, periscope_width, periscope_height)
    pygame.draw.rect(screen, SUB_DETAIL_COLOR, periscope_rect)

    # Small window/porthole on the body
    window_radius = int(height * 0.15)
    window_center_x = x + int(width * 0.25)
    window_center_y = y
    pygame.draw.circle(screen, SUB_WINDOW_COLOR, (window_center_x, window_center_y), window_radius)
    pygame.draw.circle(screen, SUB_DETAIL_COLOR, (window_center_x, window_center_y), window_radius, 1) # Outline

    # Simple propeller shape at the back
    prop_size = height * 0.4
    prop_x = x - width // 2 - prop_size // 2 + 2
    prop_y = y - prop_size // 2
    # Draw two crossed rectangles for a basic propeller look
    prop_rect1 = pygame.Rect(prop_x, prop_y, prop_size, prop_size * 0.2)
    prop_rect2 = pygame.Rect(prop_x + prop_size // 2 - prop_size * 0.1, prop_y - prop_size * 0.4 + prop_size * 0.2, prop_size * 0.2, prop_size)
    pygame.draw.rect(screen, SUB_DETAIL_COLOR, prop_rect1, border_radius=1)
    pygame.draw.rect(screen, SUB_DETAIL_COLOR, prop_rect2, border_radius=1)

def run_startup_animation(screen, clock, width, height):
    """Runs the Sonar Arts startup animation."""
    # Initialize sound manager
    sound_manager = SoundManager()
    
    start_time = time.time()
    animation_phase = "sub_appear" # sub_appear, sonar_blast, text_reveal, finished
    
    # Add 1 second delay before playing intro music
    time.sleep(1)
    sound_manager.play_music('intro', loops=0, fade_duration=0.1) # Use new method, no loop, quick fade
    sonar_radius = 0
    sub_x, sub_y = width // 2, height // 2
    sub_width, sub_height = 40, 20

    # Scale font size based on height (relative to a baseline like 600px)
    base_height = 600
    scale_factor = height / base_height
    font_size = max(24, int(60 * scale_factor))
    font = get_pixel_font(font_size)
    text_surface = font.render("Sonar Arts", True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(width // 2, height // 2))
    text_alpha = 0

    # Calculate max radius needed (distance to corner)
    max_radius = math.sqrt((width/2)**2 + (height/2)**2)
    sonar_expand_speed = (max_radius * SONAR_EXPAND_SPEED_FACTOR) / SONAR_BLAST_DURATION # pixels per second

    phase_start_time = start_time

    while animation_phase != "finished":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # Use sys.exit
            # Allow skipping animation with Escape or Enter key
            if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                     animation_phase = "finished"
                     break
        if animation_phase == "finished":
            break

        current_time = time.time()
        elapsed_time_total = current_time - start_time
        elapsed_time_phase = current_time - phase_start_time

        # Calculate submarine bobbing offset
        bob_offset = math.sin(elapsed_time_total * SUB_BOB_FREQUENCY) * SUB_BOB_AMPLITUDE
        current_sub_y = sub_y + int(bob_offset) # Apply bobbing

        screen.fill(BACKGROUND_COLOR)

        # --- Animation Logic ---
        if animation_phase == "sub_appear":
            if elapsed_time_phase < SUB_APPEAR_DURATION:
                # Draw sub with bobbing
                draw_submarine(screen, sub_x, current_sub_y, sub_width, sub_height)
            else:
                animation_phase = "sonar_blast"
                phase_start_time = time.time() # Reset timer for next phase
                sonar_radius = 0 # Reset sonar radius

        elif animation_phase == "sonar_blast":
            # Draw sub with bobbing during sonar phase as well
            draw_submarine(screen, sub_x, current_sub_y, sub_width, sub_height)

            sonar_radius = int(elapsed_time_phase * sonar_expand_speed)

            if elapsed_time_phase < SONAR_BLAST_DURATION:
                 # Draw expanding sonar rings
                 # Use the constant for number of rings
                 ring_spacing = int(max_radius / NUM_SONAR_RINGS * 0.6) # Adjusted spacing slightly
                 for i in range(NUM_SONAR_RINGS):
                     r = sonar_radius - i * ring_spacing # Spacing between rings
                     if r > 0:
                         # Calculate brightness/alpha based on how far the ring has expanded
                         # Fade starts slightly before reaching max_radius for smoother effect
                         fade_factor = max(0.0, min(1.0, 1.0 - (r / (max_radius * 0.95))))
                         brightness_factor = 1.0 - fade_factor # Ring is brighter when closer

                         # Ensure brightness doesn't go below a minimum threshold (e.g., 10%)
                         brightness_factor = max(0.1, brightness_factor)

                         current_sonar_color = (
                             max(0, min(int(SONAR_COLOR[0] * brightness_factor), 255)),
                             max(0, min(int(SONAR_COLOR[1] * brightness_factor), 255)),
                             max(0, min(int(SONAR_COLOR[2] * brightness_factor), 255))
                         )
                         # Ensure color components are valid integers
                         current_sonar_color = tuple(int(c) for c in current_sonar_color)

                         # Draw the ring with adjusted brightness
                         pygame.draw.circle(screen, current_sonar_color, (sub_x, sub_y), r, 1) # Draw outline
            else:
                 animation_phase = "text_reveal"
                 phase_start_time = time.time() # Reset timer for text fade

        elif animation_phase == "text_reveal":
             if elapsed_time_phase < TEXT_REVEAL_DURATION:
                 text_alpha = min(255, int(255 * (elapsed_time_phase / TEXT_REVEAL_DURATION)))
             else:
                 text_alpha = 255

             text_surface.set_alpha(text_alpha)
             screen.blit(text_surface, text_rect)

             # Hold the text for a bit
             if elapsed_time_phase > TEXT_REVEAL_DURATION + TEXT_HOLD_DURATION:
                 animation_phase = "finished"


        pygame.display.flip()
        clock.tick(60) # Limit FPS

    # Ensure screen is cleared before returning to avoid visual glitch
    screen.fill(BACKGROUND_COLOR)
    pygame.display.flip()
    # Short pause after clearing to ensure it registers
    time.sleep(0.1)
