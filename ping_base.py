import pygame
import pygame.sndarray
import random
import time
from Modules.Submodules.Ping_Ball import Ball # Import Ball class for type checking
import threading
import numpy as np
from sys import exit
from Modules.Ping_AI import PaddleAI
from Modules.Ping_UI import init_display, settings_screen, player_name_screen, TitleScreen, pause_screen, win_screen, level_select_screen
from Modules.Ping_GameObjects import PaddleObject, BallObject
from Modules.Submodules.Ping_DBConsole import get_console
# Removed import for DebugLevel and SewerLevel as they no longer exist
from Modules.Submodules.Ping_Fonts import get_pixel_font  # Moved import here
from Modules.Submodules.Ping_StartupAnimation import run_startup_animation  # Import the new animation function
from Modules.Submodules.Ping_LevelIntro import play_level_intro # Import the level intro function

from Modules.Submodules.Ping_Obstacles import RouletteSpinner # Import the RouletteSpinner class
"""
Ping Base Code
This is the base code for the Ping game, which includes the main game loop, event handling, and rendering.
---------
This will serve as our base code skeleton for Ping. It is where all the upper tier modules will interact with each other to run the game.
"""

# Initialize PyGame and the mixer for sound effects
pygame.init()
pygame.mixer.init()

from Modules.Ping_Arena import Arena # Import the old Arena for specific levels
from Modules.Ping_MCompile import LevelCompiler # Import the new compiler for PMF levels
from Modules.Submodules.Ping_Settings import SettingsScreen

# Initialize global debug console (singleton)
debug_console = get_console()
debug_console.log("Game initialized")

class MainGameObject:
    """Container class to hold game state for debug commands."""
    def __init__(self):
        self.arena = None
        self.balls = []

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
PADDLE_WIDTH = 40  # Increased width to better match sprite proportions
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
def main_game(ai_mode, player_name, level, window_width, window_height, debug_console=debug_console):
    # Set the game state reference in the debug console
    debug_console.game_state = MainGameObject()
    """Main game loop."""
    global screen
    current_player_name = player_name  # Local variable to track current player name
    debug_console.log(f"Starting game: Mode={ai_mode}, Player={player_name}")  # Use global debug_console

    # Validate level selection
    if not level:
        sound_manager.stop_music() # Stop music if no level selected
        return "title"

    # Create arena instance with selected level
    # Determine level name for logging (handle both class and path string)
    # Determine how to load the level based on its type
    # Removed check for DebugLevel/SewerLevel as they are deleted.
    # Assuming all levels are now PMF files or handled by LevelCompiler.
    if isinstance(level, str): # Now only check if it's a string (PMF path)
        # Use the LevelCompiler for PMF file paths (strings)
        level_name_for_log = level
        print(f"Loading level compiler for level: {level_name_for_log}...")
        arena = LevelCompiler(level) # Instantiate the LevelCompiler
        # Update arena with current window dimensions
        width, height = settings.get_dimensions()
        arena.update_scaling(width, height)
        print("Level Compiler successfully loaded and scaled")
# Play level music if specified
        # --- Play Level Music ---
        if arena.level_music: # Check if a music path string exists
            try:
                pmf_music_value = arena.level_music
                logical_music_name = None

                # 1. Check if the PMF value is directly a known logical name
                if pmf_music_value in sound_manager._sound_paths['music']:
                    logical_music_name = pmf_music_value
                    print(f"Found logical music name directly in PMF: {logical_music_name}")
                else:
                    # 2. If not a direct logical name, try converting it as a filename/path
                    print(f"PMF value '{pmf_music_value}' not a direct logical name. Attempting path conversion...")
                    # Normalize path separators for the lookup function
                    normalized_path_for_lookup = pmf_music_value.replace("\\", "/")
                    logical_music_name = sound_manager.get_music_name_from_path(normalized_path_for_lookup)

                # 3. Play music if a logical name was found either way
                if logical_music_name:
                    print(f"Attempting to play music: {logical_music_name} (from PMF value: {pmf_music_value})")
                    sound_manager.play_music(logical_music_name)
                    debug_console.log(f"Playing level music: {logical_music_name} (PMF Value: {pmf_music_value})")
                else:
                    # 4. Log warning if no logical name could be determined
                    debug_console.log(f"Warning: Could not determine logical name for music value '{pmf_music_value}' from PMF. Music will not play.")
                    print(f"Warning: Could not determine logical name for music value '{pmf_music_value}' from PMF.")
            except Exception as e:
                # Log error but avoid crashing if music path is problematic but present
                debug_console.log(f"Error processing or playing music '{arena.level_music}': {e}")
        else:
            # Stop music if no level music is defined for this level
            sound_manager.stop_music()
            debug_console.log("No level music defined, stopping music.")
    else:
        # Handle unexpected level type
        print(f"Error: Unexpected level type received: {type(level)}")
        sound_manager.stop_music() # Stop music on error
        return "title" # Or handle error appropriately

    # --- Initialize Game Variables BEFORE Intro ---
    player_b_name = generate_random_name() if ai_mode else "Player B"
    # Initialize AI if in AI mode
    paddle_ai = PaddleAI(arena) if ai_mode else None

    def update_game_objects():
        """Update game object positions based on arena dimensions"""
        nonlocal paddle_a, paddle_b, ball
        # Recreate game objects with new dimensions
        paddle_a = PaddleObject(
            x=60,  # Moved slightly right to account for wider paddle
            y=arena.scoreboard_height + (arena.height - arena.scoreboard_height - PADDLE_HEIGHT) // 2, # Center in playable area
            width=PADDLE_WIDTH,
            height=PADDLE_HEIGHT,
            arena_width=arena.width,
            arena_height=arena.height,
            scoreboard_height=arena.scoreboard_height,
            scale_rect=arena.scale_rect,
            is_left_paddle=True
        )
        paddle_b = PaddleObject(
            x=arena.width - 100,  # Moved slightly left to account for wider paddle
            y=arena.scoreboard_height + (arena.height - arena.scoreboard_height - PADDLE_HEIGHT) // 2, # Center in playable area
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
        x=60,  # Moved slightly right to account for wider paddle
        y=arena.scoreboard_height + (arena.height - arena.scoreboard_height - PADDLE_HEIGHT) // 2, # Center in playable area
        width=PADDLE_WIDTH,
        height=PADDLE_HEIGHT,
        arena_width=arena.width,
        arena_height=arena.height,
        scoreboard_height=arena.scoreboard_height,
        scale_rect=arena.scale_rect,
        is_left_paddle=True
    )
    paddle_b = PaddleObject(
        x=arena.width - 100,  # Moved slightly left to account for wider paddle
        y=arena.scoreboard_height + (arena.height - arena.scoreboard_height - PADDLE_HEIGHT) // 2, # Center in playable area
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
    debug_console.game_state.balls = balls  # Update debug console reference to balls list
    debug_console.game_state.arena = arena  # Update debug console reference to arena

    # --- Level Intro Animation ---
    level_name_for_intro = None
    # Try to get the level name using the new method first
    if hasattr(arena, 'get_level_name'):
        level_name_for_intro = arena.get_level_name()
    else:
        # Fallback for older Arena instances or if method is missing
        level_instance = getattr(arena, 'level_instance', None) # Get original level object if available
        if hasattr(level_instance, 'display_name'):
            level_name_for_intro = level_instance.display_name
        # Removed elif check for non-DebugLevel instances as DebugLevel is removed.
        # Assuming level_instance will have display_name if it's a compiled level.
        # The 'else' block below handles the fallback if display_name isn't available.
        # Need to import re here if it's not already imported globally
        import re
        class_name = level_instance.__class__.__name__
        formatted_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', class_name)
        level_name_for_intro = formatted_name.replace(" Level", " Zone")

    # Play intro if a name was determined
    if level_name_for_intro:
        # Define a function to draw the background during the intro
        # This includes the arena background and static game objects
        def draw_intro_background(target_screen):
            # Ensure game_objects list is up-to-date if balls change during intro (unlikely but safe)
            current_game_objects = [paddle_a, paddle_b] + balls
            arena.draw(target_screen, current_game_objects, font, current_player_name, score_a, player_b_name, score_b, None, False)

        play_level_intro(
            screen=screen,
            clock=clock,
            level_name=level_name_for_intro,
            width=width,
            height=height,
            scale_y=arena.scale_y,
            colors=arena.colors, # Pass the arena's color dict
            draw_background_func=draw_intro_background
        )
    # --- End Level Intro ---

    # Initialize scoreboard (can happen after intro)
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
        outline_px = max(1, int(3 * arena.scale_y)) # Scale outline thickness
        # Render countdown number with outline
        countdown_surf, countdown_rect = _render_text_with_outline(
            countdown_font,
            str(i),
            arena.colors.get('WHITE', (255, 255, 255)), # Use .get() for safety
            outline_color=(0, 0, 0),
            outline_px=outline_px
        )
        # Center the outlined text rect
        countdown_rect.center = (width // 2, height // 2)
        screen.blit(countdown_surf, countdown_rect)
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
                    elif event.key == pygame.K_DOWN:
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
                    elif event.key == pygame.K_DOWN:
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

                # Update power-up state if allowed and powerup exists
                if arena.can_spawn_powerups and arena.power_up:
                    arena.update_power_up(len(balls))

                # Update manhole states if they exist
                if arena.manholes:
                    arena.update_manholes(FRAME_TIME) # Pass frame time for smooth particle animation

                # Update RouletteSpinner state if it exists
                if isinstance(arena.obstacle, RouletteSpinner):
                    arena.obstacle.update(FRAME_TIME)

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

                    # Ball collision with obstacle (check if obstacle exists first)
                    if arena.obstacle:
                        collision_handled = False
                        # Check the type of obstacle to call the correct collision handler
                        if isinstance(arena.obstacle, RouletteSpinner):
                            # RouletteSpinner handles its own logic, doesn't need sound_manager here
                            if arena.obstacle.handle_collision(current_ball):
                                collision_handled = True
                                # RouletteSpinner manages its own state, no reset needed here
                        elif hasattr(arena.obstacle, 'handle_collision'):
                            # Assume other obstacles might use the old signature
                            if arena.obstacle.handle_collision(current_ball, sound_manager):
                                collision_handled = True
                                # Reset only if it's not a RouletteSpinner (assuming old behavior)
                                arena.reset_obstacle()

                    # Check portal collisions
                    arena.check_portal_collisions(current_ball)

                    # Check manhole collisions (applies if manholes exist)
                    if arena.check_manhole_collisions(current_ball):
                        sound_manager.play_sfx('paddle') # Use new method (consider 'manhole_hit' later)

                    # Check bumper collisions if they exist
                    for bumper in arena.bumpers:
                        if bumper.handle_collision(current_ball, sound_manager):
                            sound_manager.play_sfx('bumper')  # Play bumper sound

                    # Power-up collision check (applies if powerups allowed and exist)
                    # Arena.check_power_up_collision returns a raw Ball instance or None
                    new_ball_result = arena.check_power_up_collision(current_ball, len(balls))
                    # Check if the collision result is a raw Ball instance
                    if isinstance(new_ball_result, Ball):
                        # Prepare initial state from the raw Ball instance
                        initial_state = {
                            'x': new_ball_result.rect.x, # Use position from the raw ball
                            'y': new_ball_result.rect.y,
                            'dx': new_ball_result.dx,
                            'dy': new_ball_result.dy,
                            'speed': new_ball_result.speed,
                            'velocity_x': new_ball_result.velocity_x,
                            'velocity_y': new_ball_result.velocity_y
                        }
                        # Wrap the raw Ball instance in a BallObject, passing initial state
                        new_ball_object = BallObject(
                            arena_width=arena.width,
                            arena_height=arena.height,
                            scoreboard_height=arena.scoreboard_height,
                            scale_rect=arena.scale_rect,
                            size=new_ball_result.size, # Use size from the raw ball
                            initial_state=initial_state # Pass the prepared state
                        )
                        balls.append(new_ball_object) # Append the wrapped object
                    # No need for an elif here, as Arena won't return a BallObject anymore

                    # Handle wall collisions and scoring based on arena properties
                    # Use arena.bounce_walls and arena.use_goals flags parsed from PMF/level
                    if current_ball.handle_wall_collision(bounce_walls=arena.bounce_walls):
                         sound_manager.play_sfx('paddle') # Use new method

                    # Check goals only if they are used in this level
                    if arena.use_goals:
                        ball_scored = arena.check_goal_collisions(current_ball)
                        if ball_scored:
                            scored = ball_scored
                            balls_to_remove.append(current_ball)
                    # If goals are not used, check for side scoring (unless walls bounce)
                    elif not arena.bounce_walls:
                         ball_scored = current_ball.handle_scoring() # Original side scoring
                         if ball_scored:
                             scored = ball_scored
                             # If side scoring happens, remove the ball
                             balls_to_remove.append(current_ball)

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
                        sound_manager.stop_music() # Stop music before win screen
                        return win_screen(screen, clock, width, height, current_player_name, debug_console)
                    elif score_b >= win_score:
                        width, height = settings.get_dimensions()
                        sound_manager.stop_music() # Stop music before win screen
                        return win_screen(screen, clock, width, height, player_b_name, debug_console)

                    # Clear all existing balls and create a new single ball
                    balls.clear()
                    new_ball = BallObject(
                        arena_width=arena.width,
                        arena_height=arena.height,
                        scoreboard_height=arena.scoreboard_height,
                        scale_rect=arena.scale_rect,
                        size=BALL_SIZE
                    )
                    new_ball.reset_position()
                    balls = [new_ball]

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