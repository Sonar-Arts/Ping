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

# Initialize PyGame and the mixer for sound effects
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

def settings_screen():
    """Display the settings screen with volume control and back option."""
    option_font = pygame.font.Font(None, 48)
    volume = paddle_sound.get_volume()  # Get current volume

    # Create rectangles for clickable areas
    back_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 100, 300, 50)
    volume_up_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 - 30, 140, 50)
    volume_down_rect = pygame.Rect(WINDOW_WIDTH//2 - 160, WINDOW_HEIGHT//2 - 30, 140, 50)
    change_name_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 180, 300, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_rect.collidepoint(mouse_pos):
                    return  # Go back to the main menu
                elif volume_up_rect.collidepoint(mouse_pos):
                    volume = min(volume + 0.1, 1.0)  # Increase volume
                    paddle_sound.set_volume(volume)
                    score_sound.set_volume(volume)
                elif volume_down_rect.collidepoint(mouse_pos):
                    volume = max(volume - 0.1, 0.0)  # Decrease volume
                    paddle_sound.set_volume(volume)
                    score_sound.set_volume(volume)
                elif change_name_rect.collidepoint(mouse_pos):
                    new_name = player_name_screen()
                    if new_name:
                        with open("player_name.txt", "w") as file:
                            file.write(new_name)
                        return ("name_change", new_name)

        screen.fill(BLACK)

        # Draw title
        title_text = option_font.render("Settings", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))

        # Draw volume controls
        pygame.draw.rect(screen, WHITE, volume_up_rect, 2)
        pygame.draw.rect(screen, WHITE, volume_down_rect, 2)
        pygame.draw.rect(screen, WHITE, back_rect, 2)
        pygame.draw.rect(screen, WHITE, change_name_rect, 2)

        volume_text = option_font.render(f"Volume: {int(volume * 100)}%", True, WHITE)
        volume_up_text = option_font.render("+", True, WHITE)
        volume_down_text = option_font.render("-", True, WHITE)
        back_text = option_font.render("Back", True, WHITE)
        change_name_text = option_font.render("Change Name", True, WHITE)

        screen.blit(volume_text, (WINDOW_WIDTH//2 - volume_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        screen.blit(volume_up_text, (WINDOW_WIDTH//2 + 90, WINDOW_HEIGHT//2 - 20))
        screen.blit(volume_down_text, (WINDOW_WIDTH//2 - 90, WINDOW_HEIGHT//2 - 20))
        screen.blit(back_text, (WINDOW_WIDTH//2 - back_text.get_width()//2, WINDOW_HEIGHT//2 + 110))
        screen.blit(change_name_text, (WINDOW_WIDTH//2 - change_name_text.get_width()//2, WINDOW_HEIGHT//2 + 190))

        pygame.display.flip()
        clock.tick(60)

# Set volume to 50%
paddle_sound.set_volume(0.5)
score_sound.set_volume(0.5)

def random_color():
    """Generate a random color."""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def player_name_screen():
    """Display the player name input screen."""
    font = pygame.font.Font(None, 48)
    input_box = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, 300, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(BLACK)
        txt_surface = font.render(text, True, color)
        width = max(300, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

        prompt_text = font.render("Enter your name:", True, WHITE)
        screen.blit(prompt_text, (WINDOW_WIDTH//2 - prompt_text.get_width()//2, WINDOW_HEIGHT//2 - 100))

        pygame.display.flip()
        clock.tick(30)

    """Display the settings screen with volume control and back option."""
    option_font = pygame.font.Font(None, 48)
    volume = paddle_sound.get_volume()  # Get current volume

    # Create rectangles for clickable areas
    back_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 100, 300, 50)
    volume_up_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 - 30, 140, 50)
    volume_down_rect = pygame.Rect(WINDOW_WIDTH//2 - 160, WINDOW_HEIGHT//2 - 30, 140, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_rect.collidepoint(mouse_pos):
                    return  # Go back to the main menu
                elif volume_up_rect.collidepoint(mouse_pos):
                    volume = min(volume + 0.1, 1.0)  # Increase volume
                    paddle_sound.set_volume(volume)
                    score_sound.set_volume(volume)
                elif volume_down_rect.collidepoint(mouse_pos):
                    volume = max(volume - 0.1, 0.0)  # Decrease volume
                    paddle_sound.set_volume(volume)
                    score_sound.set_volume(volume)

        screen.fill(BLACK)

        # Draw title
        title_text = option_font.render("Settings", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))

        # Draw volume controls
        pygame.draw.rect(screen, WHITE, volume_up_rect, 2)
        pygame.draw.rect(screen, WHITE, volume_down_rect, 2)
        pygame.draw.rect(screen, WHITE, back_rect, 2)

        volume_text = option_font.render(f"Volume: {int(volume * 100)}%", True, WHITE)
        volume_up_text = option_font.render("+", True, WHITE)
        volume_down_text = option_font.render("-", True, WHITE)
        back_text = option_font.render("Back", True, WHITE)

        screen.blit(volume_text, (WINDOW_WIDTH//2 - volume_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        screen.blit(volume_up_text, (WINDOW_WIDTH//2 + 90, WINDOW_HEIGHT//2 - 20))
        screen.blit(volume_down_text, (WINDOW_WIDTH//2 - 90, WINDOW_HEIGHT//2 - 20))
        screen.blit(back_text, (WINDOW_WIDTH//2 - back_text.get_width()//2, WINDOW_HEIGHT//2 + 110))

        pygame.display.flip()
        clock.tick(60)

def title_screen():
    """Display the title screen with game options."""
    title_font = pygame.font.Font(None, 74)
    option_font = pygame.font.Font(None, 48)
    
    title_letters = list("Ping")
    title_colors = [WHITE] * len(title_letters)
    settings_text = option_font.render("Settings", True, WHITE)
    last_color_change = time.time()
    
    # Create rectangles for clickable areas
    pvp_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, 300, 50)
    ai_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50, 300, 50)
    settings_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 130, 300, 50)

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
                elif settings_rect.collidepoint(mouse_pos):
                    settings_result = settings_screen()  # Open settings screen
                    if isinstance(settings_result, tuple) and settings_result[0] == "name_change":
                        return ("settings", settings_result[1])  # Return settings and new name
                    continue  # Stay in title screen after settings

        screen.fill(BLACK)

        # Update colors every 3 seconds
        current_time = time.time()
        if current_time - last_color_change >= 3:
            title_colors = [random_color() for _ in title_letters]
            last_color_change = current_time

        # Render title
        title_width = sum(title_font.render(letter, True, title_colors[i]).get_width() for i, letter in enumerate(title_letters)) + (len(title_letters) - 1) * 5
        x_offset = (WINDOW_WIDTH - title_width) // 2
        for i, letter in enumerate(title_letters):
            text = title_font.render(letter, True, title_colors[i])
            screen.blit(text, (x_offset, WINDOW_HEIGHT//4))
            x_offset += text.get_width() + 5
        
        # Render options
        pygame.draw.rect(screen, WHITE, pvp_rect, 2)
        pygame.draw.rect(screen, WHITE, ai_rect, 2)
        pygame.draw.rect(screen, WHITE, settings_rect, 2)
        
        pvp_text = option_font.render("Player vs Player", True, WHITE)
        ai_text = option_font.render("Player vs AI", True, WHITE)
        
        screen.blit(pvp_text, (WINDOW_WIDTH//2 - pvp_text.get_width()//2, WINDOW_HEIGHT//2 - 20))
        screen.blit(ai_text, (WINDOW_WIDTH//2 - ai_text.get_width()//2, WINDOW_HEIGHT//2 + 60))
        screen.blit(settings_text, (WINDOW_WIDTH//2 - settings_text.get_width()//2, WINDOW_HEIGHT//2 + 140))

        pygame.display.flip()
        clock.tick(60)

def play_sound(sound):
    """Play sound asynchronously."""
    threading.Thread(target=sound.play).start()

def pause_menu():
    """Display the pause menu with options to go back to the title screen or settings menu."""
    option_font = pygame.font.Font(None, 48)

    # Create rectangles for clickable areas
    title_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, 300, 50)
    settings_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 50, 300, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if title_rect.collidepoint(mouse_pos):
                    return "title"
                elif settings_rect.collidepoint(mouse_pos):
                    return "settings"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # Resume game

        screen.fill(BLACK)

        # Render options
        pygame.draw.rect(screen, WHITE, title_rect, 2)
        pygame.draw.rect(screen, WHITE, settings_rect, 2)

        title_text = option_font.render("Back to Title", True, WHITE)
        settings_text = option_font.render("Settings", True, WHITE)

        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//2 - 20))
        screen.blit(settings_text, (WINDOW_WIDTH//2 - settings_text.get_width()//2, WINDOW_HEIGHT//2 + 60))

        pygame.display.flip()
        clock.tick(60)

def move_paddle(paddle, up, down):
    """Move paddle based on input flags."""
    paddle_movement = PADDLE_SPEED * FRAME_TIME
    if up and paddle.top > 0:
        paddle.y -= paddle_movement
    if down and paddle.bottom < WINDOW_HEIGHT:
        paddle.y += paddle_movement

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
    player_b_name = generate_random_name() if ai_mode else "Player B"
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_result = pause_menu()
                    if menu_result == "title":
                        return "title"
                    elif menu_result == "settings":
                        settings_result = settings_screen()
                        if isinstance(settings_result, tuple) and settings_result[0] == "name_change":
                            player_name = settings_result[1]  # Update name immediately
                        
        while accumulated_time >= FRAME_TIME:
            # Move ball
            ball.x += ball_dx * FRAME_TIME
            ball.y += ball_dy * FRAME_TIME
            
            # Move paddles
            paddle_movement = PADDLE_SPEED * FRAME_TIME
            move_paddle(paddle_a, paddle_a_up, paddle_a_down)
                
            if ai_mode:
                # AI movement with hesitation
                if random.random() > 0.3:  # 70% chance to move
                    if ball.centery > paddle_b.centery and paddle_b.bottom < WINDOW_HEIGHT:
                        paddle_b.y += paddle_movement
                    elif ball.centery < paddle_b.centery and paddle_b.top > 0:
                        paddle_b.y -= paddle_movement
            else:
                move_paddle(paddle_b, paddle_b_up, paddle_b_down)
            
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
        score_text = font.render(f"{player_name}: {score_a}  {player_b_name}: {score_b}", True, WHITE)
        # Display the score at the top center of the screen
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 20))
        
        pygame.display.flip()
        clock.tick(FRAME_RATE)

def get_player_name():
    """Prompt the player for their name if not already saved."""
    try:
        with open("player_name.txt", "r") as file:
            player_name = file.read().strip()
            if player_name:
                return player_name
    except FileNotFoundError:
        pass

    player_name = player_name_screen()
    with open("player_name.txt", "w") as file:
        file.write(player_name)
    return player_name

def settings_screen():
    """Display the settings screen with volume control and back option."""
    option_font = pygame.font.Font(None, 48)
    volume = paddle_sound.get_volume()  # Get current volume

    # Create rectangles for clickable areas
    back_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 100, 300, 50)
    volume_up_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 - 30, 140, 50)
    volume_down_rect = pygame.Rect(WINDOW_WIDTH//2 - 160, WINDOW_HEIGHT//2 - 30, 140, 50)
    change_name_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 180, 300, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_rect.collidepoint(mouse_pos):
                    return None
                elif volume_up_rect.collidepoint(mouse_pos):
                    volume = min(volume + 0.1, 1.0)  # Increase volume
                    paddle_sound.set_volume(volume)
                    score_sound.set_volume(volume)
                elif volume_down_rect.collidepoint(mouse_pos):
                    volume = max(volume - 0.1, 0.0)  # Decrease volume
                    paddle_sound.set_volume(volume)
                    score_sound.set_volume(volume)
                elif change_name_rect.collidepoint(mouse_pos):
                    new_name = player_name_screen()
                    with open("player_name.txt", "w") as file:
                        file.write(new_name)
                    return ("name_change", new_name)

        screen.fill(BLACK)
        # Draw title
        title_text = option_font.render("Settings", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))

        # Draw volume controls
        pygame.draw.rect(screen, WHITE, volume_up_rect, 2)
        pygame.draw.rect(screen, WHITE, volume_down_rect, 2)
        pygame.draw.rect(screen, WHITE, back_rect, 2)
        pygame.draw.rect(screen, WHITE, change_name_rect, 2)

        volume_text = option_font.render(f"Volume: {int(volume * 100)}%", True, WHITE)
        volume_up_text = option_font.render("+", True, WHITE)
        volume_down_text = option_font.render("-", True, WHITE)
        back_text = option_font.render("Back", True, WHITE)
        change_name_text = option_font.render("Change Name", True, WHITE)

        screen.blit(volume_text, (WINDOW_WIDTH//2 - volume_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        screen.blit(volume_up_text, (WINDOW_WIDTH//2 + 90, WINDOW_HEIGHT//2 - 20))
        screen.blit(volume_down_text, (WINDOW_WIDTH//2 - 90, WINDOW_HEIGHT//2 - 20))
        screen.blit(back_text, (WINDOW_WIDTH//2 - back_text.get_width()//2, WINDOW_HEIGHT//2 + 110))
        screen.blit(change_name_text, (WINDOW_WIDTH//2 - change_name_text.get_width()//2, WINDOW_HEIGHT//2 + 190))
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    running = True
    while running:
        player_name = get_player_name()
        while True:
            game_mode = title_screen()
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
                settings_result = settings_screen()
                if isinstance(settings_result, tuple) and settings_result[0] == "name_change":
                    player_name = settings_result[1]  # Update player name immediately