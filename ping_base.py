import pygame
import random
import time
import threading
import math
from sys import exit
from Modules.Ping_AI import PaddleAI
from Modules.Ping_UI import init_display, settings_screen, player_name_screen, title_screen, pause_menu

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
BALL_SPEED = 300  # Base ball speed
MAX_BALL_SPEED = 600  # Maximum ball speed after paddle hits
PADDLE_SPEED = 300  # Reduced from 400 for better control

# Helper function to cap ball velocity
def cap_ball_velocity(dx, dy):
    """Cap the ball's velocity to prevent it from moving too fast."""
    speed = math.sqrt(dx * dx + dy * dy)
    if speed > MAX_BALL_SPEED:
        scale = MAX_BALL_SPEED / speed
        return dx * scale, dy * scale
    return dx, dy

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

def move_paddle(paddle, up, down):
    """Move paddle based on input flags."""
    paddle_movement = PADDLE_SPEED * FRAME_TIME
    if up and paddle.top > arena.scoreboard_height:
        new_y = paddle.y - paddle_movement
        # Don't let paddle go above scoreboard
        paddle.y = max(arena.scoreboard_height, new_y)
    if down and paddle.bottom < arena.height:
        new_y = paddle.y + paddle_movement
        # Don't let paddle go below arena height
        paddle.y = min(new_y, arena.height - PADDLE_HEIGHT)

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
        paddle_positions = arena.get_paddle_positions()
        ball_position = arena.get_ball_position(BALL_SIZE)
        
        # Update paddle positions
        paddle_a.x = paddle_positions['left_x']
        paddle_a.y = paddle_positions['y']
        paddle_b.x = paddle_positions['right_x']
        paddle_b.y = paddle_positions['y']
        
        # Update ball position
        ball.x, ball.y = ball_position

    # Create game objects using arena dimensions
    paddle_positions = arena.get_paddle_positions()
    ball_position = arena.get_ball_position(BALL_SIZE)
    
    paddle_a = pygame.Rect(paddle_positions['left_x'], paddle_positions['y'],
                          PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_b = pygame.Rect(paddle_positions['right_x'], paddle_positions['y'],
                          PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(ball_position[0], ball_position[1], BALL_SIZE, BALL_SIZE)
    
    ball_dx = BALL_SPEED
    ball_dy = -BALL_SPEED
    
    # Obstacle class
    class Obstacle:
        def __init__(self):
            # Calculate middle third boundaries
            third_width = arena.width // 3
            min_x = third_width
            max_x = third_width * 2
            
            # Random position within middle third
            self.width = 20
            self.height = 60
            self.x = random.randint(min_x, max_x - self.width)
            self.y = random.randint(arena.scoreboard_height, arena.height - self.height)
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            
        def draw(self, screen, scale, offset_x, offset_y):
            """Draw the obstacle with proper scaling and centering"""
            scaled_rect = pygame.Rect(
                (self.rect.x * scale) + offset_x,
                (self.rect.y * scale) + offset_y,
                self.width * scale,
                self.height * scale
            )
            pygame.draw.rect(screen, arena.WHITE, scaled_rect)
    
    # Score
    score_a = 0
    score_b = 0
    scale_x = WINDOW_WIDTH / arena.width
    scale_y = WINDOW_HEIGHT / arena.height
    font = pygame.font.Font(None, max(12, int(48 * scale_y)))
    
    # Create initial obstacle
    obstacle = Obstacle()
    
    # Movement flags
    paddle_a_up = False
    paddle_a_down = False
    paddle_b_up = False
    paddle_b_down = False
    
    # Countdown
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
                    menu_result = pause_menu(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)
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
                        menu_result = pause_menu(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)
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
                # Move ball
                ball.x += ball_dx * FRAME_TIME
                ball.y += ball_dy * FRAME_TIME
                
                # Move paddles
                paddle_movement = PADDLE_SPEED * FRAME_TIME
                move_paddle(paddle_a, paddle_a_up, paddle_a_down)
                    
                if ai_mode:
                    # Use AI to move paddle with ball trajectory information
                    paddle_b.y = paddle_ai.move_paddle(
                        ball.x, ball.y,  # Current ball position
                        ball_dx, ball_dy,  # Ball velocity
                        paddle_b.y, paddle_movement
                    )
                else:
                    move_paddle(paddle_b, paddle_b_up, paddle_b_down)
                
                # Ball collision with top, bottom, and scoreboard
                if ball.top <= arena.scoreboard_height or ball.bottom >= arena.height:
                    ball_dy *= -1
                
                # Ball collision with paddles
                if ball.colliderect(paddle_a):
                    # Collision with left paddle
                    ball.left = paddle_a.right  # Place ball outside paddle
                    ball_dx = abs(ball_dx)  # Ensure ball moves right
                    
                    # Calculate relative intersection point (0-1) on paddle
                    relative_intersect = (ball.centery - paddle_a.top) / paddle_a.height
                    # Convert to angle (-45 to 45 degrees)
                    angle = (relative_intersect - 0.5) * 90
                    # Adjust ball's vertical velocity based on hit angle
                    new_dy = ball_dx * -math.tan(math.radians(angle))
                    # Cap the ball's velocity
                    ball_dx, ball_dy = cap_ball_velocity(ball_dx, new_dy)
                    
                    play_sound(paddle_sound)
                elif ball.colliderect(paddle_b):
                    # Collision with right paddle
                    ball.right = paddle_b.left  # Place ball outside paddle
                    ball_dx = -abs(ball_dx)  # Ensure ball moves left
                    
                    # Calculate relative intersection point (0-1) on paddle
                    relative_intersect = (ball.centery - paddle_b.top) / paddle_b.height
                    # Convert to angle (-45 to 45 degrees)
                    angle = (relative_intersect - 0.5) * 90
                    # Adjust ball's vertical velocity based on hit angle
                    new_dy = -ball_dx * -math.tan(math.radians(angle))
                    # Cap the ball's velocity
                    ball_dx, ball_dy = cap_ball_velocity(ball_dx, new_dy)
                    
                    play_sound(paddle_sound)

                # Ball collision with obstacle
                if ball.colliderect(obstacle.rect):
                    ball_dx *= -1
                    play_sound(paddle_sound)
                    # Create new obstacle after collision
                    obstacle = Obstacle()
                
                # Score points
                if ball.left <= 0:
                    score_b += 1
                    play_sound(score_sound)
                    ball_pos = arena.get_ball_position(BALL_SIZE)
                    ball.x, ball.y = ball_pos
                    ball_dx *= -1
                elif ball.right >= arena.width:
                    score_a += 1
                    play_sound(score_sound)
                    ball_pos = arena.get_ball_position(BALL_SIZE)
                    ball.x, ball.y = ball_pos
                    ball_dx *= -1
                
                accumulated_time -= FRAME_TIME
            # Cap the accumulated time to prevent spiral of death
            accumulated_time = min(accumulated_time, FRAME_TIME * 4)
        
        # Draw game state
        screen.fill(arena.BLACK)
        
        # Update arena scaling based on window size
        arena.update_scaling(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Draw center line using arena method
        arena.draw_center_line(screen)
        
        # Draw game objects with arena scaling
        scaled_paddle_a = arena.scale_rect(paddle_a)
        scaled_paddle_b = arena.scale_rect(paddle_b)
        scaled_ball = arena.scale_rect(ball)
        
        pygame.draw.rect(screen, arena.WHITE, scaled_paddle_a)
        pygame.draw.rect(screen, arena.WHITE, scaled_paddle_b)
        pygame.draw.rect(screen, arena.WHITE, scaled_ball)
        
        # Draw obstacle using arena scaling
        obstacle.draw(screen, arena.scale, arena.offset_x, arena.offset_y)
        
        # Draw scoreboard using arena method
        scaled_font = pygame.font.Font(None, max(12, int(48 * arena.scale_y)))
        arena.draw_scoreboard(screen, player_name, score_a, player_b_name, score_b, scaled_font)
        
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
            game_mode = title_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT)
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