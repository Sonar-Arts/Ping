import pygame
import random
import time
import threading
from sys import exit
from Ping_AI import PaddleAI
from Ping_UI import init_display, settings_screen, player_name_screen, title_screen, pause_menu

"""
Pong Game
---------
This is an implementation of the classic Pong game using PyGame.
The game includes a title screen with options to play against another player or an AI.
"""

# Initialize PyGame and the mixer for sound effects
pygame.init()
pygame.mixer.init()

# Standard arena size
ARENA_WIDTH = 800
ARENA_HEIGHT = 600

# Screen size variable (can be changed, but game logic uses arena size)
screen_size = (ARENA_WIDTH, ARENA_HEIGHT)
WINDOW_WIDTH, WINDOW_HEIGHT = screen_size

# Scale factors for rendering
scale_x = 1.0
scale_y = 1.0
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 120
BALL_SIZE = 20
FRAME_TIME = 1.0 / 60.0  # Target 60 FPS
MAX_FRAME_TIME = FRAME_TIME * 4  # Cap for frame time to prevent spiral of death
BALL_SPEED = 300  # Reduced from 400 for better gameplay
PADDLE_SPEED = 300  # Reduced from 400 for better control

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create the window with SCALED flag to maintain aspect ratio
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("Pong")
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
    # Use arena height for boundaries instead of window height
    if up and paddle.top > 50:  # Keep 50px space for scoreboard
        new_y = paddle.y - paddle_movement
        # Don't let paddle go above scoreboard
        paddle.y = max(50, new_y)
    if down and paddle.bottom < ARENA_HEIGHT:
        new_y = paddle.y + paddle_movement
        # Don't let paddle go below arena height
        paddle.y = min(new_y, ARENA_HEIGHT - PADDLE_HEIGHT)

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
    paddle_ai = PaddleAI(ARENA_HEIGHT) if ai_mode else None
    def update_game_objects():
        """Update game object positions based on standard arena size"""
        nonlocal paddle_a, paddle_b, ball
        # Fixed positions based on standard arena size
        paddle_a.x = 50  # Left paddle 50px from left
        paddle_a.y = (ARENA_HEIGHT//2) - (PADDLE_HEIGHT//2)  # Vertically centered
        paddle_b.x = ARENA_WIDTH - 70  # Right paddle 70px from right
        paddle_b.y = (ARENA_HEIGHT//2) - (PADDLE_HEIGHT//2)  # Vertically centered
        ball.x = (ARENA_WIDTH//2) - (BALL_SIZE//2)  # Horizontally centered
        ball.y = (ARENA_HEIGHT//2) - (BALL_SIZE//2)  # Vertically centered

    # Game objects using standard arena dimensions
    paddle_a = pygame.Rect(50, ARENA_HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_b = pygame.Rect(ARENA_WIDTH - 70, ARENA_HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(ARENA_WIDTH//2 - BALL_SIZE//2, ARENA_HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
    
    ball_dx = BALL_SPEED
    ball_dy = -BALL_SPEED
    
    # Obstacle class
    class Obstacle:
        def __init__(self):
            # Calculate middle third boundaries
            third_width = ARENA_WIDTH // 3
            min_x = third_width
            max_x = third_width * 2
            
            # Random position within middle third
            self.width = 20
            self.height = 60
            self.x = random.randint(min_x, max_x - self.width)
            self.y = random.randint(50, ARENA_HEIGHT - self.height)  # 50px from top for scoreboard
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            
        def draw(self, screen, scale_x, scale_y):
            """Draw the obstacle with proper scaling"""
            scaled_rect = pygame.Rect(
                self.rect.x * scale_x,
                self.rect.y * scale_y,
                self.width * scale_x,
                self.height * scale_y
            )
            pygame.draw.rect(screen, WHITE, scaled_rect)
    
    # Score
    score_a = 0
    score_b = 0
    font = pygame.font.Font(None, 48)
    
    # Create initial obstacle
    obstacle = Obstacle()
    
    # Movement flags
    paddle_a_up = False
    paddle_a_down = False
    paddle_b_up = False
    paddle_b_down = False
    
    # Countdown
    for i in range(3, 0, -1):
        screen.fill(BLACK)
        countdown_text = font.render(str(i), True, WHITE)
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
                    # Use AI to move paddle
                    paddle_b.y = paddle_ai.move_paddle(ball.centery, paddle_b.y, paddle_movement)
                else:
                    move_paddle(paddle_b, paddle_b_up, paddle_b_down)
                
                # Ball collision with top, bottom, and scoreboard using arena dimensions
                if ball.top <= 50 or ball.bottom >= ARENA_HEIGHT:
                    ball_dy *= -1
                
                # Ball collision with paddles
                if ball.colliderect(paddle_a) or ball.colliderect(paddle_b):
                    ball_dx *= -1
                    play_sound(paddle_sound)

                # Ball collision with obstacle
                if ball.colliderect(obstacle.rect):
                    ball_dx *= -1
                    play_sound(paddle_sound)
                    # Create new obstacle after collision
                    obstacle = Obstacle()
                
                # Score points using arena dimensions
                if ball.left <= 0:
                    score_b += 1
                    play_sound(score_sound)
                    ball.center = (ARENA_WIDTH//2, ARENA_HEIGHT//2)
                    ball_dx *= -1
                elif ball.right >= ARENA_WIDTH:
                    score_a += 1
                    play_sound(score_sound)
                    ball.center = (ARENA_WIDTH//2, ARENA_HEIGHT//2)
                    ball_dx *= -1
                
                accumulated_time -= FRAME_TIME
            # Cap the accumulated time to prevent spiral of death
            accumulated_time = min(accumulated_time, FRAME_TIME * 4)
        
        # Draw game state
        screen.fill(BLACK)
        
        # Calculate scale factors based on current window size vs arena size
        scale_x = WINDOW_WIDTH / ARENA_WIDTH
        scale_y = WINDOW_HEIGHT / ARENA_HEIGHT

        # Draw center line boxes with scaling
        box_width = 10 * scale_x
        box_height = 20 * scale_y
        box_spacing = 10 * scale_y
        num_boxes = int(ARENA_HEIGHT // (20 + 10))  # Use arena height for consistent number of boxes
        for i in range(num_boxes):
            box_y = i * (box_height + box_spacing)
            pygame.draw.rect(screen, WHITE, (
                WINDOW_WIDTH//2 - box_width//2,
                box_y,
                box_width,
                box_height
            ))
        
        # Draw game objects with scaling
        scaled_paddle_a = pygame.Rect(
            paddle_a.x * scale_x,
            paddle_a.y * scale_y,
            PADDLE_WIDTH * scale_x,
            PADDLE_HEIGHT * scale_y
        )
        scaled_paddle_b = pygame.Rect(
            paddle_b.x * scale_x,
            paddle_b.y * scale_y,
            PADDLE_WIDTH * scale_x,
            PADDLE_HEIGHT * scale_y
        )
        scaled_ball = pygame.Rect(
            ball.x * scale_x,
            ball.y * scale_y,
            BALL_SIZE * scale_x,
            BALL_SIZE * scale_y
        )
        
        pygame.draw.rect(screen, WHITE, scaled_paddle_a)
        pygame.draw.rect(screen, WHITE, scaled_paddle_b)
        pygame.draw.rect(screen, WHITE, scaled_ball)
        
        # Draw obstacle
        obstacle.draw(screen, scale_x, scale_y)
        
        # Draw scoreboard background
        scoreboard_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 50)
        dark_brown = (101, 67, 33)
        pygame.draw.rect(screen, dark_brown, scoreboard_rect)
        pygame.draw.rect(screen, WHITE, scoreboard_rect, 2)
        
        # Draw score on top of the scoreboard background
        score_text = font.render(f"{player_name}: {score_a}  {player_b_name}: {score_b}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 15))
        
        # If game is paused, draw semi-transparent overlay and pause text
        if paused:
            # Create semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(128)  # 50% transparency
            screen.blit(overlay, (0, 0))
            
            # Draw pause text
            pause_text = font.render("Paused", True, WHITE)
            screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2 - pause_text.get_height()//2))
        
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
            if isinstance(game_mode, tuple) and game_mode[0] == "settings":
                # Handle name change from settings
                player_name = game_mode[1]
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