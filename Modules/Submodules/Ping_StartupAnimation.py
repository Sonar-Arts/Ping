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

SUB_APPEAR_DURATION = 0.5
SONAR_BLAST_DURATION = 1.5
TEXT_REVEAL_DURATION = 0.5
TEXT_HOLD_DURATION = 1.0

SONAR_EXPAND_SPEED_FACTOR = 1.2 # How much faster than screen diagonal radius expands

def draw_submarine(screen, x, y, width, height):
    """Draws a simple placeholder submarine."""
    sub_rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
    pygame.draw.rect(screen, SUB_COLOR, sub_rect)
    # Add a small periscope
    periscope_rect = pygame.Rect(x - 2, y - height // 2 - 10, 4, 10)
    pygame.draw.rect(screen, SUB_COLOR, periscope_rect)

def run_startup_animation(screen, clock, width, height):
    """Runs the Sonar Arts startup animation."""
    # Initialize sound manager
    sound_manager = SoundManager()
    
    start_time = time.time()
    animation_phase = "sub_appear" # sub_appear, sonar_blast, text_reveal, finished
    
    # Add 1 second delay before playing intro music
    time.sleep(1)
    sound_manager.play_intro_music()
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

        screen.fill(BACKGROUND_COLOR)

        # --- Animation Logic ---
        if animation_phase == "sub_appear":
            if elapsed_time_phase < SUB_APPEAR_DURATION:
                draw_submarine(screen, sub_x, sub_y, sub_width, sub_height)
            else:
                animation_phase = "sonar_blast"
                phase_start_time = time.time() # Reset timer for next phase
                sonar_radius = 0 # Reset sonar radius

        elif animation_phase == "sonar_blast":
            sonar_radius = int(elapsed_time_phase * sonar_expand_speed)

            if elapsed_time_phase < SONAR_BLAST_DURATION:
                 # Draw expanding sonar rings
                 num_rings = 5
                 ring_spacing = int(max_radius / num_rings * 0.5) # Adjust spacing based on screen size
                 for i in range(num_rings):
                     r = sonar_radius - i * ring_spacing # Spacing between rings
                     if r > 0:
                         # Add a simple reflection simulation: stop drawing ring segment if it hits edge
                         # This is complex, so we'll stick to full circles for simplicity now.
                         pygame.draw.circle(screen, SONAR_COLOR, (sub_x, sub_y), r, 1) # Draw outline
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
