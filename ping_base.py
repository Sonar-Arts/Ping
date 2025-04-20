import pygame
import pygame.sndarray
import random
import time
import threading
import numpy as np
from sys import exit
from Modules.Ping_AI import PaddleAI
from Modules.Ping_UI import init_display, settings_screen, player_name_screen, TitleScreen, pause_screen, win_screen, level_select_screen
from Modules.Ping_GameObjects import PaddleObject, BallObject
from Modules.Submodules.Ping_DBConsole import get_console
from Modules.Submodules.Ping_Levels import SewerLevel  # Added for Sewer Level check
from Modules.Submodules.Ping_Fonts import get_pixel_font  # Moved import here
from Modules.Submodules.Ping_StartupAnimation import run_startup_animation  # Import the new animation function

"""
Ping Base Code
This is the base code for the Ping game, which includes the main game loop, event handling, and rendering.
---------
This will serve as our base code skeleton for Ping. It is where all the upper tier modules will interact with each other to run the game.
"""

# Initialize PyGame and the mixer for sound effects
pygame.init()
pygame.mixer.init()

from Modules.Ping_Arena import Arena
from Modules.Submodules.Ping_Settings import SettingsScreen

# Initialize global debug console (singleton)
debug_console = get_console()
debug_console.log("Game initialized")

def read_settings():
    """Read window dimensions from settings file."""
    try:
        with open("Game Parameters/settings.txt", "r") as f:
            settings = {}
            for line in f:
                key, value = line.strip().split('=')
                settings[key] = int(value)
        return settings['WINDOW_WIDTH'], settings['WINDOW_HEIGHT']
    except (FileNotFoundError, KeyError, ValueError):
        # If file doesn't exist or is invalid, return defaults and create file
        default_width, default_height = 800, 600
        with open("Game Parameters/settings.txt", "w") as f:
            f.write(f"WINDOW_WIDTH={default_width}\nWINDOW_HEIGHT={default_height}")
        return default_width, default_height

# Initialize settings and load initial window dimensions
settings = SettingsScreen()
width, height = settings.get_dimensions()
screen = init_display(width, height)

def update_screen_size(width=None, height=None):
    """Update screen dimensions and reinitialize display."""
    global settings
    if width is None or height is None:
        width, height = settings.get_dimensions()
    # Update the settings (which will also write to file)
    settings.update_dimensions(width, height)
    return init_display(width, height)

# Game constants
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 120
BALL_SIZE = 20
FRAME_TIME = 1.0 / 60.0  # Target 60 FPS
MAX_FRAME_TIME = FRAME_TIME * 4  # Cap for frame time to prevent spiral of death

pygame.display.set_caption("Ping")

# Set window icon
try:
    icon = pygame.image.load("Ping Assets/Images/Icons/Ping Game Icon.png")
    pygame.display.set_icon(icon)
    debug_console.log("Game icon loaded successfully")
except (pygame.error, FileNotFoundError) as e:
    debug_console.log(f"Could not load game icon: {e}")

clock = pygame.time.Clock()

# Initialize sound manager
from Modules.Submodules.Ping_Sound import SoundManager
sound_manager = SoundManager()
# Provide the console with access to the sound manager instance
debug_console.sound_manager = sound_manager

def generate_random_name():
    """Generate a random name from First_Names.txt and Last_Name.txt."""
    try:
        with open("First_Names.txt") as f:
            first_names = f.read().splitlines()
        with open("Last_Name.txt") as f:
            last_names = f.read().splitlines()
        if not first_names or not last_names:
            return "Random Player"
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        return f"{first_name} {last_name}"
    except FileNotFoundError:
        debug_console.log("Error: Name files not found.")
        return "Player X"

def main_game(ai_mode, player_name, level, window_width, window_height, debug_console=debug_console):
    """Main game loop."""
    global screen
    current_player_name = player_name  # Local variable to track current player name
    debug_console.log(f"Starting game: Mode={ai_mode}, Player={player_name}")  # Use global debug_console

    # Validate level selection
    if not level:
        return "title"

    # Create arena instance with selected level
    print(f"Loading arena for level: {level.__class__.__name__}...")
    arena = Arena(level)
    # Update arena with current window dimensions
    width, height = settings.get_dimensions()
    arena.update_scaling(width, height)
    print("Arena successfully loaded and scaled")

    # --- Initialize Game Variables BEFORE Intro ---
    player_b_name = generate_random_name() if ai_mode else "Player B"
    # Initialize AI if in AI mode
    paddle_ai = PaddleAI(arena) if ai_mode else None

    def update_game_objects():
        """Update game object positions based on arena dimensions"""
        nonlocal paddle_a, paddle_b, ball
        # Recreate game objects with new dimensions
        paddle_a = PaddleObject(
            x=50,
            y=(arena.height - PADDLE_HEIGHT) // 2,
            width=PADDLE_WIDTH,
            height=PADDLE_HEIGHT,
            arena_width=arena.width,
            arena_height=arena.height,
            scoreboard_height=arena.scoreboard_height,
            scale_rect=arena.scale_rect,
            is_left_paddle=True
        )
        paddle_b = PaddleObject(
            x=arena.width - 70,
            y=(arena.height - PADDLE_HEIGHT) // 2,
            width=PADDLE_WIDTH,
            height=PADDLE_HEIGHT,
            arena_width=arena.width,
            arena_height=arena.height,
            scoreboard_height=arena.scoreboard_height,
            scale_rect=arena.scale_rect,
            is_left_paddle=False
        )
        ball = BallObject(
            arena_width=arena.width,
            arena_height=arena.height,
            scoreboard_height=arena.scoreboard_height,
            scale_rect=arena.scale_rect,
            size=BALL_SIZE
        )

    # Create game objects with proper params
    paddle_a = PaddleObject(
        x=50,
        y=(arena.height - PADDLE_HEIGHT) // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        arena_width=arena.width,
        arena_height=arena.height,
        scoreboard_height=arena.scoreboard_height,
        scale_rect=arena.scale_rect,
        is_left_paddle=True
    )
    paddle_b = PaddleObject(
        x=arena.width - 70,
        y=(arena.height - PADDLE_HEIGHT) // 2,
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        arena_width=arena.width,
        arena_height=arena.height,
        scoreboard_height=arena.scoreboard_height,
        scale_rect=arena.scale_rect,
        is_left_paddle=False
    )
    ball = BallObject(
        arena_width=arena.width,
        arena_height=arena.height,
        scoreboard_height=arena.scoreboard_height,
        scale_rect=arena.scale_rect,
        size=BALL_SIZE
    )

    # Score and game state
    score_a = 0
    score_b = 0
    width, height = settings.get_dimensions()
    scale_x = width / arena.width
    scale_y = height / arena.height
    font = get_pixel_font(max(12, int(28 * scale_y)))

    # List to track all active balls
    balls = [ball] # Initialize with the first ball

    # --- Sonic-style Level Intro ---
    if isinstance(level, SewerLevel):
        # Define graphic properties
        level_name = "Sewer Zone"
        intro_font_size = max(24, int(60 * arena.scale_y)) # Scale font size
        intro_font = get_pixel_font(intro_font_size)
        text_surface = intro_font.render(level_name, True, (0, 200, 0)) # Green text
        text_rect = text_surface.get_rect()

        # Animation parameters
        slide_speed = width / 1.0 # Pixels per second (adjust for desired speed)
        pause_duration = 1.5 # Seconds to pause on screen

        # Starting position (off-screen left)
        text_rect.center = (-text_rect.width // 2, height // 2)
        start_time = time.time()

        # Slide in
        while text_rect.centerx < width // 2:
            elapsed_time = time.time() - start_time
            text_rect.centerx = -text_rect.width // 2 + int(slide_speed * elapsed_time)

            # Draw background and game objects first
            game_objects = [paddle_a, paddle_b] + balls # Ensure game_objects are defined here
            arena.draw(screen, game_objects, font, current_player_name, score_a, player_b_name, score_b, None, False)
            # Draw level name text on top
            screen.blit(text_surface, text_rect)
            pygame.display.flip()
            clock.tick(60) # Limit FPS

        # Pause on screen
        text_rect.centerx = width // 2 # Ensure it's centered
        # Draw background and game objects first
        game_objects = [paddle_a, paddle_b] + balls # Ensure game_objects are defined here
        arena.draw(screen, game_objects, font, current_player_name, score_a, player_b_name, score_b, None, False)
        # Draw level name text on top
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        time.sleep(pause_duration)

        # Slide out (to the right)
        start_time = time.time()
        start_x = text_rect.centerx
        while text_rect.left < width:
            elapsed_time = time.time() - start_time
            text_rect.centerx = start_x + int(slide_speed * elapsed_time)

            # Draw background and game objects first
            game_objects = [paddle_a, paddle_b] + balls # Ensure game_objects are defined here
            arena.draw(screen, game_objects, font, current_player_name, score_a, player_b_name, score_b, None, False)
            # Draw level name text on top
            screen.blit(text_surface, text_rect)
            pygame.display.flip()
            clock.tick(60)
    # --- End Level Intro ---

    # Initialize scoreboard
    arena.initialize_scoreboard()

    # Game state flags
    paddle_a_up = False
    paddle_a_down = False
    paddle_b_up = False
    paddle_b_down = False
    ball_frozen = False
    respawn_timer = None
    paused = False

    # Initial countdown
    for i in range(3, 0, -1):
        # Draw the initial game state first
        width, height = settings.get_dimensions()
        arena.update_scaling(width, height) # Ensure scaling is correct
        scaled_font = get_pixel_font(max(12, int(28 * arena.scale_y)))
        game_objects = [paddle_a, paddle_b] + balls # Include all active balls
        # Draw arena, scoreboard, paddles, ball (at initial positions)
        arena.draw(screen, game_objects, scaled_font, current_player_name, score_a, player_b_name, score_b, None, False)

        # Draw countdown number on top
        countdown_font_size = max(48, int(100 * arena.scale_y)) # Larger font for countdown
        countdown_font = get_pixel_font(countdown_font_size)
        countdown_text = countdown_font.render(str(i), True, arena.colors['WHITE'])
        screen.blit(countdown_text, (width//2 - countdown_text.get_width()//2,
                                    height//2 - countdown_text.get_height()//2))
        pygame.display.flip()
        time.sleep(1)

    last_frame_time = time.time()

    accumulated_time = 0

    while True:
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        accumulated_time += delta_time

        # Get events and handle debug console first
        events = pygame.event.get()
        if debug_console.update(events):
            continue

        # Handle regular game events
        for event in events:
            # Let the sound manager handle its events first
            sound_manager.handle_event(event) # Process sound events

            if event.type == pygame.QUIT:
                # Shutdown is handled before final pygame.quit() at the end of the script
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resizing
                width, height = event.w, event.h
                screen = init_display(width, height)
                settings.update_dimensions(width, height) # Update settings object and file
                arena.update_scaling(width, height)     # Update arena scaling factors
                update_game_objects()                   # Recreate/reposition game objects
                scaled_font = get_pixel_font(max(12, int(28 * arena.scale_y))) # Update font
                # Reset scoreboard debug flag to show message after resize
                arena.scoreboard._debug_shown = False
                debug_console.log(f"Window resized to {width}x{height}")
                # No need to redraw here, the main loop will handle it
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    paddle_a_up = True
                if event.key == pygame.K_s:
                    paddle_a_down = True
                if not ai_mode:
                    if event.key == pygame.K_UP:
                        paddle_b_up = True
                    if event.key == pygame.K_DOWN:
                        paddle_b_down = True
                if event.key == pygame.K_ESCAPE:
                    paused = True
                    while paused:  # Keep pause menu active until explicitly resumed or exited
                        width, height = SettingsScreen.get_dimensions()
                        # Pass sound_manager to pause_screen
                        menu_result = pause_screen(screen, clock, width, height, sound_manager, debug_console)

                        if menu_result == "resume":
                            # Resume game
                            last_frame_time = time.time()
                            accumulated_time = 0
                            # Reset scoreboard debug flag to show message on resume
                            arena.scoreboard._debug_shown = False
                            paused = False
                        elif menu_result == "title":
                            # Music is stopped within pause_screen now
                            # Return to title screen
                            return "title"
                        elif menu_result == "settings":
                            # Handle settings screen
                            # Added sound_manager argument
                            settings_result = settings_screen(screen, clock, sound_manager, width, height, in_game=True, debug_console=debug_console)
                            if isinstance(settings_result, tuple):
                                if settings_result[0] == "back_to_pause":
                                    # Update player name if it has changed
                                    current_player_name = settings.get_player_name()
                                    # Update dimensions and refresh display
                                    settings.update_dimensions(settings_result[1], settings_result[2])
                                    width, height = settings.get_dimensions()
                                    screen = init_display(width, height)
                                    debug_console.draw(screen, width, height)  # Draw console after init
                                    pygame.display.flip()
                                    arena.update_scaling(width, height)
                                    # Reset scoreboard debug flag to show message after settings update
                                    arena.scoreboard._debug_shown = False
                                    update_game_objects()
                                    scaled_font = get_pixel_font(max(12, int(28 * arena.scale_y)))
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    paddle_a_up = False
                if event.key == pygame.K_s:
                    paddle_a_down = False
                if not ai_mode:
                    if event.key == pygame.K_UP:
                        paddle_b_up = False
                    if event.key == pygame.K_DOWN:
                        paddle_b_down = False

        if not paused:
            while accumulated_time >= FRAME_TIME:
                # Update paddle movement flags
                paddle_a.moving_up = paddle_a_up
                paddle_a.moving_down = paddle_a_down
                paddle_b.moving_up = paddle_b_up
                paddle_b.moving_down = paddle_b_down

                # Move paddles
                paddle_a.move(FRAME_TIME)
                if ai_mode:
                    # Use AI to move paddle with ball trajectory information
                    paddle_b.rect.y = paddle_ai.move_paddle(
                        ball.rect.x, ball.rect.y,  # Current ball position
                        ball.ball.velocity_x, ball.ball.velocity_y,  # Ball velocity
                        paddle_b.rect.y, paddle_b.speed * FRAME_TIME,
                        ball_frozen,  # Pass ball's frozen state
                        all_balls=balls  # Pass all active balls for better prediction
                    )
                    # Make sure paddle stays within bounds
                    paddle_b.rect.y = max(arena.scoreboard_height,
                                        min(paddle_b.rect.y, arena.height - paddle_b.rect.height))
                else:
                    paddle_b.move(FRAME_TIME)

                # Update respawn timer if active
                if respawn_timer is not None:
                    respawn_timer -= FRAME_TIME
                    if respawn_timer <= 0:
                        respawn_timer = None
                        ball_frozen = False

                # Update power-up and manhole states for Sewer Level
                if isinstance(level, SewerLevel):
                    arena.update_power_up(len(balls))
                    arena.update_manholes(FRAME_TIME)  # Pass frame time for smooth particle animation

                # Handle all active balls
                scored = None
                balls_to_remove = []

                for current_ball in balls:
                    # Move ball if not frozen
                    if not ball_frozen:
                        current_ball.move(FRAME_TIME)

                        # Handle collisions
                        if current_ball.handle_wall_collision():
                            sound_manager.play_sfx('paddle') # Use new method

                    if current_ball.handle_paddle_collision(paddle_a) or current_ball.handle_paddle_collision(paddle_b):
                        sound_manager.play_sfx('paddle') # Use new method

                    # Ball collision with obstacle
                    if arena.obstacle.handle_collision(current_ball):
                        sound_manager.play_sfx('paddle') # Use new method (consider 'obstacle_hit' later)
                        # Create new obstacle after collision
                        arena.reset_obstacle()

                    # Check portal collisions
                    arena.check_portal_collisions(current_ball)

                    # Sewer Level specific collisions
                    if isinstance(level, SewerLevel):
                        # Check manhole collisions first as they affect ball trajectory
                        if arena.check_manhole_collisions(current_ball):
                            sound_manager.play_sfx('paddle') # Use new method (consider 'manhole_hit' later)

                        # Power-up collision check
                        new_ball = arena.check_power_up_collision(current_ball, len(balls))
                        if new_ball:
                            balls.append(new_ball)

                    # Handle all wall collisions and scoring
                    if isinstance(level, SewerLevel):
                        # Sewer Level: bounce off all walls, score with goals
                        if current_ball.handle_wall_collision(bounce_walls=True):
                            sound_manager.play_sfx('paddle') # Use new method
                        ball_scored = arena.check_goal_collisions(current_ball)
                        if ball_scored:
                            scored = ball_scored
                            balls_to_remove.append(current_ball)
                    else:
                        # Debug Level: bounce off top/bottom, score on sides
                        if current_ball.handle_wall_collision(bounce_walls=False):
                            sound_manager.play_sfx('paddle') # Use new method
                        ball_scored = current_ball.handle_scoring()
                        if ball_scored:
                            scored = ball_scored

                # Remove scored balls
                for ball_to_remove in balls_to_remove:
                    if ball_to_remove in balls:
                        balls.remove(ball_to_remove)

                # Handle scoring results
                if scored:
                    if scored == "right":
                        score_b += 1
                    else:
                        score_a += 1
                    sound_manager.play_sfx('score') # Use new method

                    # Check for win condition
                    win_score = settings.get_win_scores()
                    if score_a >= win_score:
                        width, height = settings.get_dimensions()
                        return win_screen(screen, clock, width, height, current_player_name, debug_console)
                    elif score_b >= win_score:
                        width, height = settings.get_dimensions()
                        return win_screen(screen, clock, width, height, player_b_name, debug_console)

                    # Reset balls and start AI paddle moving to center
                    if len(balls) == 0:
                        # Create new ball if all balls are gone
                        new_ball = BallObject(
                            arena_width=arena.width,
                            arena_height=arena.height,
                            scoreboard_height=arena.scoreboard_height,
                            scale_rect=arena.scale_rect,
                            size=BALL_SIZE
                        )
                        new_ball.reset_position()
                        balls = [new_ball]
                    else:
                        # Reset remaining balls
                        for b in balls:
                            b.reset_position()

                    if ai_mode:
                        paddle_ai.reset_position()  # Start AI paddle moving to center
                    respawn_timer = 2.0  # 2 second respawn delay
                    accumulated_time = 0  # Reset accumulated time for accurate timing
                    ball_frozen = True
                    last_frame_time = time.time()  # Reset frame time for accurate timing
                    continue  # Skip the rest of this frame's updates

                accumulated_time -= FRAME_TIME
            # Cap the accumulated time to prevent spiral of death
            accumulated_time = min(accumulated_time, FRAME_TIME * 4)

        # Arena scaling is now updated only on VIDEORESIZE event or settings change
        # width, height = settings.get_dimensions() # Removed
        # arena.update_scaling(width, height) # Removed
        # Create or update scaled font
        scaled_font = get_pixel_font(max(12, int(28 * arena.scale_y)))

        # Draw complete game state using arena
        game_objects = [paddle_a, paddle_b] + balls  # Include all active balls
        arena.draw(screen, game_objects, scaled_font, current_player_name, score_a, player_b_name, score_b, respawn_timer, paused)

        # Draw debug console (handles its own visibility)
        debug_console.draw(screen, width, height)

        # Final display update
        pygame.display.flip()

def get_player_name():
    """Get the player name from settings or prompt for a new one."""
    global settings
    player_name = settings.get_player_name()

    if not player_name or player_name == "Player":
        width, height = settings.get_dimensions()
        player_name = player_name_screen(screen, clock, width, height, debug_console)
        settings.update_player_name(player_name)

    return player_name


if __name__ == "__main__":
    # --- RUN STARTUP ANIMATION ---
    # Moved here to run only once on startup
    try:
        current_width, current_height = settings.get_dimensions()
        run_startup_animation(screen, clock, current_width, current_height)
        debug_console.log("Startup animation finished.")
    except Exception as e:
        # Use debug console for logging errors if available
        if 'debug_console' in globals():
            debug_console.log(f"Error during startup animation: {e}")
        else:
            print(f"Error during startup animation: {e}")  # Fallback print
    # --- END STARTUP ANIMATION ---

    running = True
    while running:
        player_name = get_player_name()
        while True:
            # Create and display title screen
            # Pass the global sound_manager instance
            title_screen_instance = TitleScreen(sound_manager)
            width, height = settings.get_dimensions()
            # Corrected call: Use the TitleScreen's method to display the menu
            game_mode = title_screen_instance.display(screen, clock, width, height, debug_console)

            # Handle quit action from title screen
            if game_mode == "quit":
                running = False
                break

            if game_mode == "settings":
                # Added sound_manager argument
                settings_result = settings_screen(screen, clock, sound_manager, width, height, in_game=False, debug_console=debug_console)
                if isinstance(settings_result, tuple):
                    # Handle different return types from settings screen
                    if settings_result[0] == "name_change":
                        # Update player name
                        player_name = settings_result[1]
                        settings.update_player_name(player_name)
                    elif len(settings_result) == 2:
                        # Normal settings return from title screen - update dimensions
                        settings.update_dimensions(settings_result[0], settings_result[1])
                        screen = init_display(settings_result[0], settings_result[1])
                continue
            # Check if game_mode is None (which could happen if the display loop exits unexpectedly)
            # or if it's False (for 2P mode) or True (for 1P mode)
            elif game_mode is None:
                # If game_mode is None, assume user closed window or error occurred
                running = False
                break

            # Show level selection screen only if a game mode was selected (True or False)
            width, height = settings.get_dimensions()
            # Pass sound_manager to level_select_screen
            level = level_select_screen(screen, clock, width, height, sound_manager, debug_console)
            if level == "back":
                continue  # Go back to title screen
            elif level is None: # Handle closing the level select screen
                continue # Go back to title screen implicitly

            # Get the most up-to-date player name before starting the game
            current_player_name = settings.get_player_name()
            width, height = settings.get_dimensions()
            game_result = main_game(game_mode, current_player_name, level, width, height, debug_console)
            if game_result == "title":
                break  # Go back to title screen
            elif game_result == "settings":
                width, height = settings.get_dimensions()
                # Removed sound preview args - update settings_screen function later
                settings_result = settings_screen(screen, clock, width, height, in_game=False, debug_console=debug_console)
                if isinstance(settings_result, tuple):
                    if settings_result[0] == "name_change":
                        player_name = settings_result[1]  # Update player name immediately
                    elif len(settings_result) == 2:
                        settings.update_dimensions(settings_result[0], settings_result[1])
                        screen = init_display(settings_result[0], settings_result[1])
                # After settings, return to title screen
                break
    # Ensure Pygame quits properly if the loop exits
    sound_manager.shutdown() # Clean up sounds before quitting
    pygame.quit()
    exit()