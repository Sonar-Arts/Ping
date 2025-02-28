import pygame
import time
from sys import exit
import random

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def init_display(width, height):
    """Initialize the display with the given dimensions."""
    screen = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("Ping")
    return screen

def random_color():
    """Generate a random color."""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def settings_screen(screen, clock, paddle_sound, score_sound, WINDOW_WIDTH, WINDOW_HEIGHT):
    """Display the settings screen with volume control and screen size options."""
    option_font = pygame.font.Font(None, 36)  # Reduced font size for better fit
    volume = paddle_sound.get_volume()  # Get current volume
    screen_sizes = [(800, 600), (1024, 768), (1280, 720), (1920, 1080)]
    screen_size = (WINDOW_WIDTH, WINDOW_HEIGHT)  # Initialize screen_size with current window size
    try:
        current_size_index = screen_sizes.index((WINDOW_WIDTH, WINDOW_HEIGHT))
    except ValueError:
        current_size_index = 0
        screen_size = screen_sizes[0]
        WINDOW_WIDTH, WINDOW_HEIGHT = screen_size
        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)

    dropdown_open = False

    while True:
        back_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 180, 240, 40)
        volume_up_rect = pygame.Rect(WINDOW_WIDTH//2 + 20, WINDOW_HEIGHT//2 - 30, 100, 40)
        volume_down_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 30, 100, 40)
        size_rect_height = 40 if not dropdown_open else 120
        size_rect = pygame.Rect(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 50, 240, size_rect_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEWHEEL:
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if dropdown_open:
                    if size_rect.collidepoint(mouse_pos):
                        mouse_y = mouse_pos[1]
                        option_height = 35
                        first_option_y = WINDOW_HEIGHT//2 + 52
                        clicked_index = int((mouse_y - first_option_y) // option_height)
                        
                        if 0 <= clicked_index < len(screen_sizes):
                            option_rect = pygame.Rect(WINDOW_WIDTH//2 - 118,
                                                   first_option_y + clicked_index * option_height,
                                                   236, 30)
                            if option_rect.collidepoint(mouse_pos):
                                current_size_index = clicked_index
                                screen_size = screen_sizes[current_size_index]
                                WINDOW_WIDTH, WINDOW_HEIGHT = screen_size
                                old_surface = screen.copy()
                                try:
                                    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
                                    screen.fill(BLACK)
                                    scaled_surface = pygame.transform.scale(old_surface, screen_size)
                                    screen.blit(scaled_surface, (0, 0))
                                except pygame.error as e:
                                    print(f"Failed to create renderer: {e}")
                                    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
                                    screen.fill(BLACK)
                                pygame.display.flip()
                                pygame.time.wait(100)
                                option_font = pygame.font.Font(None, 36)
                                dropdown_open = False
                    else:
                        dropdown_open = False
                else:
                    if back_rect.collidepoint(mouse_pos):
                        return screen_size
                    elif volume_up_rect.collidepoint(mouse_pos):
                        volume = min(volume + 0.1, 1.0)
                        paddle_sound.set_volume(volume)
                        score_sound.set_volume(volume)
                    elif volume_down_rect.collidepoint(mouse_pos):
                        volume = max(volume - 0.1, 0.0)
                        paddle_sound.set_volume(volume)
                        score_sound.set_volume(volume)
                    elif size_rect.collidepoint(mouse_pos):
                        dropdown_open = True

        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        hover_color = (100, 100, 100)
        
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

        title_text = option_font.render("Settings", True, WHITE)
        volume_text = option_font.render(f"Volume: {int(volume * 100)}%", True, WHITE)
        volume_up_text = option_font.render("+", True, WHITE)
        volume_down_text = option_font.render("-", True, WHITE)
        back_text = option_font.render("Back", True, WHITE)
        size_label = option_font.render("Screen Size:", True, WHITE)

        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))
        screen.blit(volume_text, (WINDOW_WIDTH//2 - volume_text.get_width()//2, WINDOW_HEIGHT//2 - 100))
        screen.blit(volume_up_text, (WINDOW_WIDTH//2 + 90, WINDOW_HEIGHT//2 - 20))
        screen.blit(volume_down_text, (WINDOW_WIDTH//2 - 90, WINDOW_HEIGHT//2 - 20))
        if not dropdown_open:
            screen.blit(back_text, (WINDOW_WIDTH//2 - back_text.get_width()//2, WINDOW_HEIGHT//2 + 190))
        screen.blit(size_label, (WINDOW_WIDTH//2 - size_label.get_width()//2, WINDOW_HEIGHT//2 + 20))

        if dropdown_open:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            
            screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//4))
            screen.blit(size_label, (WINDOW_WIDTH//2 - size_label.get_width()//2, WINDOW_HEIGHT//2 + 20))
            pygame.draw.rect(screen, WHITE, size_rect, 2)

            dropdown_background = pygame.Surface((236, 116))
            dropdown_background.fill((40, 40, 40))
            screen.blit(dropdown_background, (WINDOW_WIDTH//2 - 118, WINDOW_HEIGHT//2 + 52))
            
            for i, size in enumerate(screen_sizes):
                option_rect = pygame.Rect(WINDOW_WIDTH//2 - 118, WINDOW_HEIGHT//2 + 52 + i * 35, 236, 30)
                pygame.draw.rect(screen, WHITE, option_rect, 1)
                if i == current_size_index:
                    pygame.draw.rect(screen, (80, 80, 80), option_rect)
                size_option_text = option_font.render(f"{size[0]}x{size[1]}", True, WHITE)
                text_x = WINDOW_WIDTH//2 - size_option_text.get_width()//2
                text_y = WINDOW_HEIGHT//2 + 57 + i * 35
                screen.blit(size_option_text, (text_x, text_y))
        else:
            current_size = screen_sizes[current_size_index]
            size_text = option_font.render(f"{current_size[0]}x{current_size[1]} ▼", True, WHITE)
            text_x = WINDOW_WIDTH//2 - size_text.get_width()//2
            text_y = WINDOW_HEIGHT//2 + 60
            screen.blit(size_text, (text_x, text_y))

        pygame.display.flip()
        clock.tick(60)

def player_name_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
    """Display the player name input screen."""
    font = pygame.font.Font(None, 48)
    input_box = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, 300, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''

    while True:
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

def title_screen(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
    """Display the title screen with game options."""
    title_font = pygame.font.Font(None, 74)
    option_font = pygame.font.Font(None, 48)
    
    title_letters = list("Ping")
    title_colors = [WHITE] * len(title_letters)
    settings_text = option_font.render("Settings", True, WHITE)
    last_color_change = time.time()
    
    while True:
        button_width = min(300, WINDOW_WIDTH // 3)
        button_height = min(50, WINDOW_HEIGHT // 12)
        button_spacing = button_height + 20
        
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
                    return "settings"

        screen.fill(BLACK)

        current_time = time.time()
        if current_time - last_color_change >= 3:
            title_colors = [random_color() for _ in title_letters]
            last_color_change = current_time

        title_width = sum(title_font.render(letter, True, title_colors[i]).get_width() 
                         for i, letter in enumerate(title_letters)) + (len(title_letters) - 1) * 5
        x_offset = (WINDOW_WIDTH - title_width) // 2
        for i, letter in enumerate(title_letters):
            text = title_font.render(letter, True, title_colors[i])
            screen.blit(text, (x_offset, WINDOW_HEIGHT//4))
            x_offset += text.get_width() + 5
        
        hover_color = (100, 100, 100)
        mouse_pos = pygame.mouse.get_pos()
        
        if pvp_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, pvp_rect)
        pygame.draw.rect(screen, WHITE, pvp_rect, 2)
        
        if ai_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, ai_rect)
        pygame.draw.rect(screen, WHITE, ai_rect, 2)
        
        if settings_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, settings_rect)
        pygame.draw.rect(screen, WHITE, settings_rect, 2)
        
        pvp_text = option_font.render("Player vs Player", True, WHITE)
        ai_text = option_font.render("Player vs AI", True, WHITE)
        
        screen.blit(pvp_text, (pvp_rect.centerx - pvp_text.get_width()//2, 
                              pvp_rect.centery - pvp_text.get_height()//2))
        screen.blit(ai_text, (ai_rect.centerx - ai_text.get_width()//2, 
                            ai_rect.centery - ai_text.get_height()//2))
        screen.blit(settings_text, (settings_rect.centerx - settings_text.get_width()//2, 
                                  settings_rect.centery - settings_text.get_height()//2))

        pygame.display.flip()
        clock.tick(60)

def pause_menu(screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
    """Display the pause menu with options to resume, go to title screen, or settings."""
    option_font = pygame.font.Font(None, 48)

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
                    return None

        screen.fill(BLACK)

        hover_color = (100, 100, 100)
        mouse_pos = pygame.mouse.get_pos()
        
        if title_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, title_rect)
        pygame.draw.rect(screen, WHITE, title_rect, 2)
        
        if settings_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, settings_rect)
        pygame.draw.rect(screen, WHITE, settings_rect, 2)

        title_text = option_font.render("Back to Title", True, WHITE)
        settings_text = option_font.render("Settings", True, WHITE)

        screen.blit(title_text, (WINDOW_WIDTH//2 - title_text.get_width()//2, WINDOW_HEIGHT//2 - 20))
        screen.blit(settings_text, (WINDOW_WIDTH//2 - settings_text.get_width()//2, WINDOW_HEIGHT//2 + 60))

        pygame.display.flip()
        clock.tick(60)