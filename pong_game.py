import pygame
import random
import time
import threading
from sys import exit

"""
Pong Game
---------
This is an implementation of the classic Pong game using PyGame.
The game includes a title screen with options to play against another player or an AI.
"""

# Initialize PyGame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 120
BALL_SIZE = 20
FRAME_RATE = 60
FRAME_TIME = 1.0 / FRAME_RATE
BALL_SPEED = 400
PADDLE_SPEED = 400

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Load sounds
paddle_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/Paddle.wav")
score_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/Score.wav")

# Set volume to 75%
paddle_sound.set_volume(0.5)
score_sound.set_volume(0.5)

def random_color():
    """Generate a random color."""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def title_screen():
    """Display the title screen with game options."""
    title_font = pygame.font.Font(None, 74)
    option_font = pygame.font.Font(None, 48)
    
    title_letters = list("Ping")
    title_colors = [WHITE] * len(title_letters)
    last_color_change = time.time()
    
    # Create rectangles for clickable areas
    pvp_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, 300, 50)
    ai_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50, 300, 50)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if pvp_rect.collidepoint(mouse_pos):
                    return False  # PvP mode
                elif ai_rect.collidepoint(mouse_pos):
                    return True   # AI mode

        screen.fill(BLACK)
        
        # Update colors every 3 seconds
        current_time = time.time()
        if current_time - last_color_change >= 3:
            title_colors = [random_color() for _ in title_letters]
            last_color_change = current_time
        
        # Render title
        x_offset = -90
        for letter, color in zip(title_letters, title_colors):
            text = title_font.render(letter, True, color)
            screen.blit(text, (WINDOW_WIDTH//2 + x_offset, WINDOW_HEIGHT//4))
            x_offset += 60
        
        # Render options
        pygame.draw.rect(screen, WHITE, pvp_rect, 2)
        pygame.draw.rect(screen, WHITE, ai_rect, 2)
        
        pvp_text = option_font.render("1. Player vs Player", True, WHITE)
        ai_text = option_font.render("2. Player vs AI", True, WHITE)
        
        screen.blit(pvp_text, (WINDOW_WIDTH//2 - pvp_text.get_width()//2, WINDOW_HEIGHT//2 - 20))
        screen.blit(ai_text, (WINDOW_WIDTH//2 - ai_text.get_width()//2, WINDOW_HEIGHT//2 + 60))
        
        pygame.display.flip()
        clock.tick(60)

def play_sound(sound):
    """Play sound asynchronously."""
    threading.Thread(target=sound.play).start()

def main_game(ai_mode):
    """Main game loop."""
    # Game objects
    paddle_a = pygame.Rect(50, WINDOW_HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    paddle_b = pygame.Rect(WINDOW_WIDTH - 70, WINDOW_HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WINDOW_WIDTH//2 - BALL_SIZE//2, WINDOW_HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
    
    ball_dx = BALL_SPEED
    ball_dy = -BALL_SPEED
    
    # Score
    score_a = 0
    score_b = 0
    font = pygame.font.Font(None, 48)
    
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
        
        while accumulated_time >= FRAME_TIME:
            # Move ball
            ball.x += ball_dx * FRAME_TIME
            ball.y += ball_dy * FRAME_TIME
            
            # Move paddles
            paddle_movement = PADDLE_SPEED * FRAME_TIME
            if paddle_a_up and paddle_a.top > 0:
                paddle_a.y -= paddle_movement
            if paddle_a_down and paddle_a.bottom < WINDOW_HEIGHT:
                paddle_a.y += paddle_movement
                
            if ai_mode:
                # AI movement with hesitation
                if random.random() > 0.1:  # 90% chance to move
                    if ball.centery > paddle_b.centery and paddle_b.bottom < WINDOW_HEIGHT:
                        paddle_b.y += paddle_movement
                    elif ball.centery < paddle_b.centery and paddle_b.top > 0:
                        paddle_b.y -= paddle_movement
            else:
                if paddle_b_up and paddle_b.top > 0:
                    paddle_b.y -= paddle_movement
                if paddle_b_down and paddle_b.bottom < WINDOW_HEIGHT:
                    paddle_b.y += paddle_movement
            
            # Ball collision with top and bottom
            if ball.top <= 0 or ball.bottom >= WINDOW_HEIGHT:
                ball_dy *= -1
            
            # Ball collision with paddles
            if ball.colliderect(paddle_a) or ball.colliderect(paddle_b):
                ball_dx *= -1
                play_sound(paddle_sound)
            
            # Score points
            if ball.left <= 0:
                score_b += 1
                play_sound(score_sound)
                ball.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
                ball_dx *= -1
            elif ball.right >= WINDOW_WIDTH:
                score_a += 1
                play_sound(score_sound)
                ball.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
                ball_dx *= -1
            
            accumulated_time -= FRAME_TIME
        
        # Draw everything
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, paddle_a)
        pygame.draw.rect(screen, WHITE, paddle_b)
        pygame.draw.rect(screen, WHITE, ball)
        
        # Draw score
        score_text = font.render(f"Player A: {score_a}  Player B: {score_b}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 20))
        
        pygame.display.flip()
        clock.tick(FRAME_RATE)

if __name__ == "__main__":
    ai_mode = title_screen()
    main_game(ai_mode)