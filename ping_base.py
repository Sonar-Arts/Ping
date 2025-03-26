import pygame
import random
import time
import threading
from sys import exit
from Modules.Ping_AI import PaddleAI
from Modules.Ping_UI import init_display, settings_screen, player_name_screen, TitleScreen, pause_screen, win_screen, level_select_screen
from Modules.Ping_GameObjects import PaddleObject, BallObject
from Modules.Submodules.Ping_Levels import SewerLevel  # Added for Sewer Level check

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
MAX_SCORE = 10  # Score needed to win the game

pygame.display.set_caption("Ping")
clock = pygame.time.Clock()

# Load sounds
paddle_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/Paddle.wav")
score_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/Score.wav")

# Set volume to 50%
paddle_sound.set_volume(0.5)
score_sound.set_volume(0.5)


def play_sound(sound):
    """Play sound asynchronously."""
    threading.Thread(target=sound.play).start()

def generate_random_name():
    """Generate a random name from First_Names.txt and Last_Name.txt."""
    with open("First_Names.txt") as f:
        first_names = f.read().splitlines()
    with open("Last_Name.txt") as f:
        last_names = f.read().splitlines()
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    return f"{first_name} {last_name}"

def main_game(ai_mode, player_name, level, window_width, window_height):
    """Main game loop."""
    global screen
    current_player_name = player_name  # Local variable to track current player name
    
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
    
    # Initialize scoreboard
    arena.initialize_scoreboard()
    
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
    font = pygame.font.Font(None, max(12, int(48 * scale_y)))
    
    # List to track all active balls - don't add the initial ball twice
    balls = []
    balls.append(ball)

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
        screen.fill(arena.colors['BLACK'])
        width, height = settings.get_dimensions()
        scale_x = width / arena.width
        scale_y = height / arena.height
        scaled_font = pygame.font.Font(None, max(12, int(48 * scale_y)))
        countdown_text = scaled_font.render(str(i), True, arena.colors['WHITE'])
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
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
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
                        menu_result = pause_screen(screen, clock, width, height)
                        
                        if menu_result == "resume":
                            # Resume game
                            last_frame_time = time.time()
                            accumulated_time = 0
                            # Reset scoreboard debug flag to show message on resume
                            arena.scoreboard._debug_shown = False
                            paused = False
                        elif menu_result == "title":
                            # Return to title screen
                            return "title"
                        elif menu_result == "settings":
                            # Handle settings screen
                            settings_result = settings_screen(screen, clock, paddle_sound, score_sound, width, height, in_game=True)
                            if isinstance(settings_result, tuple):
                                if settings_result[0] == "back_to_pause":
                                    # Update player name if it has changed
                                    current_player_name = settings.get_player_name()
                                    # Update dimensions and refresh display
                                    settings.update_dimensions(settings_result[1], settings_result[2])
                                    width, height = settings.get_dimensions()
                                    screen = init_display(width, height)
                                    arena.update_scaling(width, height)
                                    # Reset scoreboard debug flag to show message after settings update
                                    arena.scoreboard._debug_shown = False
                                    update_game_objects()
                                    scaled_font = pygame.font.Font(None, max(12, int(48 * arena.scale_y)))
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

                # Update power-up state
                if isinstance(level, SewerLevel):
                    arena.update_power_up(len(balls))

                # Handle all active balls
                scored = None
                balls_to_remove = []
                
                for current_ball in balls:
                    # Move ball if not frozen
                    if not ball_frozen:
                        current_ball.move(FRAME_TIME)

                        # Handle collisions
                        if current_ball.handle_wall_collision():
                            play_sound(paddle_sound)

                    if current_ball.handle_paddle_collision(paddle_a) or current_ball.handle_paddle_collision(paddle_b):
                        play_sound(paddle_sound)

                    # Ball collision with obstacle
                    if arena.obstacle.handle_collision(current_ball):
                        play_sound(paddle_sound)
                        # Create new obstacle after collision
                        arena.reset_obstacle()

                    # Check portal collisions
                    arena.check_portal_collisions(current_ball)
                    
                    # Power-up collision (only for Sewer Level)
                    if isinstance(level, SewerLevel):
                        new_ball = arena.check_power_up_collision(current_ball, len(balls))
                        if new_ball:
                            balls.append(new_ball)
                    
                    # Handle all wall collisions and scoring
                    if isinstance(level, SewerLevel):
                        # Sewer Level: bounce off all walls, score with goals
                        if current_ball.handle_wall_collision(bounce_walls=True):
                            play_sound(paddle_sound)
                        ball_scored = arena.check_goal_collisions(current_ball)
                        if ball_scored:
                            scored = ball_scored
                            balls_to_remove.append(current_ball)
                    else:
                        # Debug Level: bounce off top/bottom, score on sides
                        if current_ball.handle_wall_collision(bounce_walls=False):
                            play_sound(paddle_sound)
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
                    play_sound(score_sound)
                    
                    # Check for win condition
                    if score_a >= MAX_SCORE:
                        width, height = settings.get_dimensions()
                        return win_screen(screen, clock, width, height, current_player_name)
                    elif score_b >= MAX_SCORE:
                        width, height = settings.get_dimensions()
                        return win_screen(screen, clock, width, height, player_b_name)
                    
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
        
        # Update arena scaling based on window size
        width, height = settings.get_dimensions()
        arena.update_scaling(width, height)

        # Create or update scaled font
        scaled_font = pygame.font.Font(None, max(12, int(48 * arena.scale_y)))
        
        # Draw complete game state using arena
        game_objects = [paddle_a, paddle_b] + balls  # Include all active balls
        arena.draw(screen, game_objects, scaled_font, current_player_name, score_a, player_b_name, score_b, respawn_timer, paused)
        
        pygame.display.flip()

def get_player_name():
    """Get the player name from settings or prompt for a new one."""
    global settings
    player_name = settings.get_player_name()
    
    if not player_name or player_name == "Player":
        width, height = settings.get_dimensions()
        player_name = player_name_screen(screen, clock, width, height)
        settings.update_player_name(player_name)
        
    return player_name


if __name__ == "__main__":
    running = True
    while running:
        player_name = get_player_name()
        while True:
            title_screen_instance = TitleScreen()
            width, height = settings.get_dimensions()
            game_mode = title_screen_instance.display(screen, clock, width, height)
            if game_mode == "settings":
                settings_result = settings_screen(screen, clock, paddle_sound, score_sound, width, height, in_game=False)
                if isinstance(settings_result, tuple):
                    if settings_result[0] == "name_change":
                        # Update player name
                        player_name = settings_result[1]
                        settings.update_player_name(player_name)
                    elif len(settings_result) == 2:
                        # Normal settings return from title screen - update dimensions
                        settings.update_dimensions(settings_result[0], settings_result[1])
                        screen = init_display(settings_result[0], settings_result[1])
                continue
            elif game_mode is None:
                running = False
                break
            
            # Show level selection screen
            width, height = settings.get_dimensions()
            level = level_select_screen(screen, clock, width, height)
            if level == "back":
                continue  # Go back to title screen
            
            # Get the most up-to-date player name before starting the game
            current_player_name = settings.get_player_name()
            width, height = settings.get_dimensions()
            game_result = main_game(game_mode, current_player_name, level, width, height)
            if game_result == "title":
                break  # Go back to title screen
            elif game_result == "settings":
                width, height = settings.get_dimensions()
                settings_result = settings_screen(screen, clock, paddle_sound, score_sound, width, height, in_game=False)
                if isinstance(settings_result, tuple):
                    if settings_result[0] == "name_change":
                        player_name = settings_result[1]  # Update player name immediately
                    elif len(settings_result) == 2:
                        settings.update_dimensions(settings_result[0], settings_result[1])
                        screen = init_display(settings_result[0], settings_result[1])
                # After settings, return to title screen
                break