import pygame
import random
import time
import threading
from sys import exit
from Modules.Ping_AI import PaddleAI
from Modules.Ping_UI import init_display, settings_screen, player_name_screen, TitleScreen, pause_screen, win_screen
from Modules.Ping_GameObjects import PaddleObject, BallObject

"""
Ping Base Code
This is the base code for the Ping game, which includes the main game loop, event handling, and rendering.
---------
This will serve as our base code skeleton for Ping. It is where all the upper tier modules will interact with each other to run the game.
"""

# Initialize PyGame and the mixer for sound effects
pygame.init()
pygame.mixer.init()

from Modules.Ping_Arena import Arena, DEFAULT_WIDTH, DEFAULT_HEIGHT

# Create arena instance
arena = Arena(DEFAULT_WIDTH, DEFAULT_HEIGHT)

# Create the window using init_display from Ping_UI
screen = init_display(arena.width, arena.height)
WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()

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

def main_game(ai_mode, player_name):
    """Main game loop."""
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
    
    # Score
    score_a = 0
    score_b = 0
    scale_x = WINDOW_WIDTH / arena.width
    scale_y = WINDOW_HEIGHT / arena.height
    font = pygame.font.Font(None, max(12, int(48 * scale_y)))
    
    # Game state flags
    paddle_a_up = False
    paddle_a_down = False
    paddle_b_up = False
    paddle_b_down = False
    ball_frozen = False
    respawn_timer = None
    
    # Initial countdown
    for i in range(3, 0, -1):
        screen.fill(arena.BLACK)
        scale_x = WINDOW_WIDTH / arena.width
        scale_y = WINDOW_HEIGHT / arena.height
        scaled_font = pygame.font.Font(None, max(12, int(48 * scale_y)))
        countdown_text = scaled_font.render(str(i), True, arena.WHITE)
        screen.blit(countdown_text, (WINDOW_WIDTH//2 - countdown_text.get_width()//2,
                                   WINDOW_HEIGHT//2 - countdown_text.get_height()//2))
        pygame.display.flip()
        time.sleep(1)
    
    last_frame_time = time.time()
    accumulated_time = 0
    
    paused = False
    
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
                    menu_result = pause_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)
                    if menu_result == "title":
                        return "title"
                    elif menu_result == "settings":
                        settings_result = settings_screen(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT)
                        # After returning from settings, update game objects for new screen size
                        update_game_objects()
                        if isinstance(settings_result, tuple) and settings_result[0] == "name_change":
                            player_name = settings_result[1]  # Update name immediately
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if paused:  # If already paused, unpause
                        paused = False
                        last_frame_time = time.time()
                        accumulated_time = 0
                    else:  # If not paused, show pause menu
                        paused = True
                        menu_result = pause_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)
                        if menu_result == "title":
                            return "title"
                        elif menu_result == "settings":
                            settings_result = settings_screen(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT)
                            if isinstance(settings_result, tuple) and settings_result[0] == "name_change":
                                player_name = settings_result[1]
                            # After returning from settings, update game objects for new screen size
                            update_game_objects()
                        # Unpause after menu interactions or if escape was pressed in pause menu
                        if menu_result is None or menu_result == "settings":
                            paused = False
                            last_frame_time = time.time()
                            accumulated_time = 0
                        
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
                        paddle_b.rect.y, paddle_b.speed * FRAME_TIME
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

                # Move ball if not frozen
                if not ball_frozen:
                    ball.move(FRAME_TIME)

                    # Handle collisions
                    if ball.handle_wall_collision():
                        play_sound(paddle_sound)

                if ball.handle_paddle_collision(paddle_a) or ball.handle_paddle_collision(paddle_b):
                    play_sound(paddle_sound)

                # Ball collision with obstacle
                if arena.obstacle.handle_collision(ball):
                    play_sound(paddle_sound)
                    # Create new obstacle after collision
                    arena.reset_obstacle()
                
                # Check for scoring
                scored = ball.handle_scoring()
                if scored:
                    if scored == "right":
                        score_b += 1
                    else:
                        score_a += 1
                    play_sound(score_sound)
                    
                    # Check for win condition
                    if score_a >= MAX_SCORE:
                        return win_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, player_name)
                    elif score_b >= MAX_SCORE:
                        return win_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, player_b_name)
                    
                    # Reset ball to center position and start respawn timer
                    ball.reset_position()
                    respawn_timer = 2.0  # 2 second respawn delay
                    accumulated_time = 0  # Reset accumulated time for accurate timing
                    ball_frozen = True
                    last_frame_time = time.time()  # Reset frame time for accurate timing
                    continue  # Skip the rest of this frame's updates
                
                accumulated_time -= FRAME_TIME
            # Cap the accumulated time to prevent spiral of death
            accumulated_time = min(accumulated_time, FRAME_TIME * 4)
        
        # Draw game state
        screen.fill(arena.BLACK)
        
        # Update arena scaling based on window size
        arena.update_scaling(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Draw center line using arena method
        arena.draw_center_line(screen)
        
        # Draw game objects
        paddle_a.draw(screen, arena.WHITE)
        paddle_b.draw(screen, arena.WHITE)
        ball.draw(screen, arena.WHITE)
        
        # Draw obstacle
        arena.obstacle.draw(screen, arena.WHITE)
        
        # Draw scoreboard using arena method with respawn timer
        scaled_font = pygame.font.Font(None, max(12, int(48 * arena.scale_y)))
        arena.draw_scoreboard(screen, player_name, score_a, player_b_name, score_b, scaled_font, respawn_timer)
        
        # Draw pause overlay if paused
        if paused:
            arena.draw_pause_overlay(screen, scaled_font)
        
        pygame.display.flip()

def get_player_name():
    """Prompt the player for their name if not already saved."""
    try:
        with open("player_name.txt", "r") as file:
            player_name = file.read().strip()
            if player_name:
                return player_name
    except FileNotFoundError:
        pass

    player_name = player_name_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)
    with open("player_name.txt", "w") as file:
        file.write(player_name)
    return player_name


if __name__ == "__main__":
    running = True
    while running:
        player_name = get_player_name()
        while True:
            title_screen_instance = TitleScreen()
            game_mode = title_screen_instance.display(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)
            if game_mode == "settings":
                settings_result = settings_screen(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT)
                continue
            elif game_mode is None:
                running = False
                break
            
            game_result = main_game(game_mode, player_name)
            if game_result == "title":
                break  # Go back to title screen
            elif game_result == "settings":
                settings_result = settings_screen(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT)
                if isinstance(settings_result, tuple) and settings_result[0] == "name_change":
                    player_name = settings_result[1]  # Update player name immediately