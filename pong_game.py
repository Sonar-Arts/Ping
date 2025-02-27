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

def settings_screen():
    """Display the settings screen with volume control and screen size options."""
    global screen_size, screen, option_font, WINDOW_WIDTH, WINDOW_HEIGHT
    option_font = pygame.font.Font(None, 36)  # Reduced font size for better fit
    volume = paddle_sound.get_volume()  # Get current volume
    screen_sizes = [(800, 600), (1024, 768), (1280, 720),(1920, 1080)]
    try:
        current_size_index = screen_sizes.index((WINDOW_WIDTH, WINDOW_HEIGHT))
    except ValueError:
        # If current size isn't in the list, default to first option
        current_size_index = 0
        screen_size = screen_sizes[0]
        WINDOW_WIDTH, WINDOW_HEIGHT = screen_size
        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

    dropdown_open = False

    while True:
        # Create rectangles for clickable areas - update positions based on current window size
        back_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 180, 240, 40)
        volume_up_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 - 30, 100, 40)
        volume_down_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 30, 100, 40)
        # Make size rect taller when dropdown is open
        size_rect_height = 40 if not dropdown_open else 120  # Reduced height for options
        size_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 50, 240, size_rect_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Ignore mouse wheel events
            if event.type == pygame.MOUSEWHEEL:
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click only
                mouse_pos = pygame.mouse.get_pos()
                # Handle clicks based on dropdown state
                if dropdown_open:
                    if size_rect.collidepoint(mouse_pos):
                        # When dropdown is open, check for size selection
                        mouse_y = mouse_pos[1]
                        # Calculate which option was clicked based on new spacing
                        option_height = 35  # Reduced height for each option
                        first_option_y = WINDOW_HEIGHT//2 + 52  # Starting Y position of first option
                        clicked_index = int((mouse_y - first_option_y) // option_height)
                        
                        # Check if click is within valid option area
                        if 0 <= clicked_index < len(screen_sizes):
                            # Check if click is within the horizontal bounds of the option
                            option_rect = pygame.Rect(WINDOW_WIDTH//2 - 118,
                                                     first_option_y + clicked_index * option_height,
                                                     236, 30)
                            if option_rect.collidepoint(mouse_pos):
                                try:
                                    current_size_index = clicked_index
                                    screen_size = screen_sizes[current_size_index]
                                    # Update window size variables
                                    WINDOW_WIDTH, WINDOW_HEIGHT = screen_size
                                    # Store old surface contents
                                    old_surface = screen.copy()
                                    # Set new display mode with SCALED flag to maintain aspect ratio
                                    screen = pygame.display.set_mode(screen_size, pygame.SCALED | pygame.RESIZABLE)
                                    # Clear the new screen
                                    screen.fill(BLACK)
                                    try:
                                        # Try to scale old content to new size
                                        scaled_surface = pygame.transform.scale(old_surface, screen_size)
                                        screen.blit(scaled_surface, (0, 0))
                                    except pygame.error:
                                        pass  # If scaling fails, continue with blank screen
                                    # Update display
                                    pygame.display.flip()
                                    # Brief pause to let the display settle
                                    pygame.time.wait(100)
                                    # Need to redeclare font after screen mode change
                                    option_font = pygame.font.Font(None, 36)  # Maintain smaller font size
                                    dropdown_open = False
                                    print(f"Selected size: {screen_size}")
                                except pygame.error as e:
                                    print(f"Error resizing screen: {e}")
                    else:
                        # Close dropdown if clicked outside
                        dropdown_open = False
                else:
                    # Handle regular button clicks when dropdown is closed
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
                    elif size_rect.collidepoint(mouse_pos):
                        dropdown_open = True

        screen.fill(BLACK)

        # Draw base UI elements first
        # Check for hover and fill with very opaque gray if hovered
        mouse_pos = pygame.mouse.get_pos()
        hover_color = (100, 100, 100)  # More visible gray
        
        if volume_up_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, volume_up_rect)
        pygame.draw.rect(screen, WHITE, volume_up_rect, 2)
        
        if volume_down_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, volume_down_rect)
        pygame.draw.rect(screen, WHITE, volume_down_rect, 2)
        
        if back_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, back_rect)
        pygame.draw.rect(screen, WHITE, size_rect, 2)
        if not dropdown_open:
            pygame.draw.rect(screen, WHITE, back_rect, 2)
        

        # Prepare all text elements
        title_text = option_font.render("Settings", True, WHITE)
        volume_text = option_font.render(f"Volume: {int(volume * 100)}%", True, WHITE)
        volume_up_text = option_font.render("+", True, WHITE)
        volume_down_text = option_font.render("-", True, WHITE)
        back_text = option_font.render("Back", True, WHITE)
        size_label = option_font.render("Screen Size:", True, WHITE)

        # Draw title and all base UI text
        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))
        screen.blit(volume_text, (WINDOW_WIDTH//2 - volume_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        screen.blit(volume_up_text, (WINDOW_WIDTH//2 + 90, WINDOW_HEIGHT//2 - 20))
        screen.blit(volume_down_text, (WINDOW_WIDTH//2 - 90, WINDOW_HEIGHT//2 - 20))
        if not dropdown_open:
            screen.blit(back_text, (WINDOW_WIDTH//2 - back_text.get_width()//2, WINDOW_HEIGHT//2 + 190))
        screen.blit(size_label, (WINDOW_WIDTH//2 - size_label.get_width()//2, WINDOW_HEIGHT//2 + 20))

        # Draw current size or dropdown
        if dropdown_open:
            # Create semi-transparent overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)  # 50% transparency
            screen.blit(overlay, (0, 0))
            
            # Redraw title and size selector on top of overlay
            screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))
            screen.blit(size_label, (WINDOW_WIDTH//2 - size_label.get_width()//2, WINDOW_HEIGHT//2 + 20))
            pygame.draw.rect(screen, WHITE, size_rect, 2)

            try:
                # Draw dropdown box with dark background
                dropdown_background = pygame.Surface((236, 116))
                dropdown_background.fill((40, 40, 40))
                screen.blit(dropdown_background, (WINDOW_WIDTH//2 - 118, WINDOW_HEIGHT//2 + 52))
                
                # Show all sizes with individual selection boxes
                for i, size in enumerate(screen_sizes):
                    option_rect = pygame.Rect(WINDOW_WIDTH//2 - 118, WINDOW_HEIGHT//2 + 52 + i * 35, 236, 30)
                    pygame.draw.rect(screen, WHITE, option_rect, 1)
                    if i == current_size_index:
                        pygame.draw.rect(screen, (80, 80, 80), option_rect)
                    size_option_text = option_font.render(f"{size[0]}x{size[1]}", True, WHITE)
                    text_x = WINDOW_WIDTH//2 - size_option_text.get_width()//2
                    text_y = WINDOW_HEIGHT//2 + 57 + i * 35
                    screen.blit(size_option_text, (text_x, text_y))
            except pygame.error as e:
                print(f"Error creating dropdown surface: {e}")
                dropdown_open = False
        else:
            # Show current size with arrow indicator
            current_size = screen_sizes[current_size_index]
            size_text = option_font.render(f"{current_size[0]}x{current_size[1]} ▼", True, WHITE)
            text_x = WINDOW_WIDTH//2 - size_text.get_width()//2
            text_y = WINDOW_HEIGHT//2 + 60
            screen.blit(size_text, (text_x, text_y))

        if dropdown_open:
            print("Rendering dropdown options")
            try:
                # Draw dropdown box with dark background for better visibility
                dropdown_background = pygame.Surface((236, 116))  # Reduced width and height
                dropdown_background.fill((40, 40, 40))  # Dark gray background
                screen.blit(dropdown_background, (WINDOW_WIDTH//2 - 118, WINDOW_HEIGHT//2 + 52))
            except pygame.error as e:
                print(f"Error creating dropdown surface: {e}")
                dropdown_open = False
                continue
            
            # Show all sizes with individual selection boxes
            for i, size in enumerate(screen_sizes):
                # Draw selection box for each option with reduced size
                option_rect = pygame.Rect(WINDOW_WIDTH//2 - 118, WINDOW_HEIGHT//2 + 52 + i * 35, 236, 30)
                pygame.draw.rect(screen, WHITE, option_rect, 1)
                
                # Highlight selected size
                if i == current_size_index:
                    pygame.draw.rect(screen, (80, 80, 80), option_rect)  # Darker highlight
                
                # Render size text
                size_option_text = option_font.render(f"{size[0]}x{size[1]}", True, WHITE)
                text_x = WINDOW_WIDTH//2 - size_option_text.get_width()//2
                text_y = WINDOW_HEIGHT//2 + 57 + i * 35  # Reduced spacing between options
                screen.blit(size_option_text, (text_x, text_y))
        else:
            # Show current size with arrow indicator for dropdown
            current_size = screen_sizes[current_size_index]
            size_text = option_font.render(f"{current_size[0]}x{current_size[1]} ▼", True, WHITE)
            text_x = WINDOW_WIDTH//2 - size_text.get_width()//2
            text_y = WINDOW_HEIGHT//2 + 60
            screen.blit(size_text, (text_x, text_y))

        try:
            # Update screen
            pygame.display.flip()
            clock.tick(60)
        except pygame.error as e:
            print(f"Display error: {e}")
            # Try to recover by resetting the display
            try:
                screen = pygame.display.set_mode(screen_size, pygame.SCALED | pygame.RESIZABLE)
                pygame.display.flip()
            except pygame.error:
                # If we can't recover, return to the main menu
                return

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

def title_screen():
    """Display the title screen with game options."""
    title_font = pygame.font.Font(None, 74)
    option_font = pygame.font.Font(None, 48)
    
    title_letters = list("Ping")
    title_colors = [WHITE] * len(title_letters)
    settings_text = option_font.render("Settings", True, WHITE)
    last_color_change = time.time()
    
    while True:
        # Create rectangles for clickable areas with size relative to screen dimensions
        button_width = min(300, WINDOW_WIDTH // 3)  # Scale width with screen, max 300px
        button_height = min(50, WINDOW_HEIGHT // 12)  # Scale height with screen, max 50px
        button_spacing = button_height + 20  # Space between buttons
        
        pvp_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                              WINDOW_HEIGHT//2 - button_height//2 - button_spacing,
                              button_width, button_height)
        ai_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                             WINDOW_HEIGHT//2 - button_height//2,
                             button_width, button_height)
        settings_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                  WINDOW_HEIGHT//2 - button_height//2 + button_spacing,
                                  button_width, button_height)

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
        
        # Render options with hover effect
        hover_color = (100, 100, 100)  # More visible gray
        mouse_pos = pygame.mouse.get_pos()
        
        # PvP button
        if pvp_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, pvp_rect)
        pygame.draw.rect(screen, WHITE, pvp_rect, 2)
        
        # AI button
        if ai_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, ai_rect)
        pygame.draw.rect(screen, WHITE, ai_rect, 2)
        
        # Settings button
        if settings_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, settings_rect)
        pygame.draw.rect(screen, WHITE, settings_rect, 2)
        
        pvp_text = option_font.render("Player vs Player", True, WHITE)
        ai_text = option_font.render("Player vs AI", True, WHITE)
        
        # Center text within the button rectangles
        screen.blit(pvp_text, (pvp_rect.centerx - pvp_text.get_width()//2, pvp_rect.centery - pvp_text.get_height()//2))
        screen.blit(ai_text, (ai_rect.centerx - ai_text.get_width()//2, ai_rect.centery - ai_text.get_height()//2))
        screen.blit(settings_text, (settings_rect.centerx - settings_text.get_width()//2, settings_rect.centery - settings_text.get_height()//2))

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

        # Render options with hover effect
        hover_color = (100, 100, 100)  # More visible gray
        mouse_pos = pygame.mouse.get_pos()
        
        # Title button
        if title_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, title_rect)
        pygame.draw.rect(screen, WHITE, title_rect, 2)
        
        # Settings button
        if settings_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, settings_rect)
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
    player_b_name = generate_random_name() if ai_mode else "Player B"
    """Main game loop."""
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
                    menu_result = pause_menu()
                    if menu_result == "title":
                        return "title"
                    elif menu_result == "settings":
                        settings_result = settings_screen()
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
                        menu_result = pause_menu()
                        if menu_result == "title":
                            return "title"
                        elif menu_result == "settings":
                            settings_result = settings_screen()
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
                    # AI movement with hesitation, using arena boundaries
                    if random.random() > 0.3:  # 70% chance to move
                        if ball.centery > paddle_b.centery and paddle_b.bottom < ARENA_HEIGHT:
                            new_y = paddle_b.y + paddle_movement
                            paddle_b.y = min(new_y, ARENA_HEIGHT - PADDLE_HEIGHT)
                        elif ball.centery < paddle_b.centery and paddle_b.top > 50:  # 50px for scoreboard
                            new_y = paddle_b.y - paddle_movement
                            paddle_b.y = max(50, new_y)
                else:
                    move_paddle(paddle_b, paddle_b_up, paddle_b_down)
                
                # Ball collision with top, bottom, and scoreboard using arena dimensions
                if ball.top <= 50 or ball.bottom >= ARENA_HEIGHT:
                    ball_dy *= -1
                
                # Ball collision with paddles
                if ball.colliderect(paddle_a) or ball.colliderect(paddle_b):
                    ball_dx *= -1
                    play_sound(paddle_sound)
                
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

    player_name = player_name_screen()
    with open("player_name.txt", "w") as file:
        file.write(player_name)
    return player_name


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