import pygame
from .Ping_Levels import DebugLevel, SewerLevel  # Added Sewer Level import
from .Ping_Fonts import get_pixel_font
from .Ping_Button import get_button

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class LevelSelect:
    def __init__(self):
        pass

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
        """Display the level select screen with optional debug console."""
        scale_y = WINDOW_HEIGHT / 600  # Base height scale
        scale_x = WINDOW_WIDTH / 800   # Base width scale
        scale = min(scale_x, scale_y)  # Use the smaller scale to ensure text fits
        
        button_width = min(300, WINDOW_WIDTH // 3)
        
        # Calculate font size and ensure it fits
        option_font_size = max(12, int(36 * scale))  # Starting with slightly smaller base size
        option_font = get_pixel_font(option_font_size)
        
        # Test all texts to ensure they fit
        test_texts = ["Debug Level", "Sewer Level", "Back"]
        while any(option_font.render(text, True, WHITE).get_width() > button_width - 20 
                 for text in test_texts) and option_font_size > 12:
            option_font_size -= 1
            option_font = get_pixel_font(option_font_size)
        
        while True:
            button_height = min(50, WINDOW_HEIGHT // 12)
            button_spacing = button_height + 20
            
            # Create rectangles for all buttons
            debug_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                  WINDOW_HEIGHT//2 - button_height//2 - button_spacing*2,
                                  button_width, button_height)
            sewer_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                  WINDOW_HEIGHT//2 - button_height//2,
                                  button_width, button_height)
            back_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                 WINDOW_HEIGHT//2 - button_height//2 + button_spacing*2,
                                 button_width, button_height)

            # Get events
            events = pygame.event.get()
            
            # Handle debug console if provided
            if debug_console:
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == 96:  # Backtick
                        debug_console.update([event])
                        continue
                    if debug_console.visible:
                        if debug_console.handle_event(event):
                            continue

            # Process remaining events
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if debug_rect.collidepoint(mouse_pos):
                        return DebugLevel()
                    elif sewer_rect.collidepoint(mouse_pos):
                        return SewerLevel()
                    elif back_rect.collidepoint(mouse_pos):
                        return "back"

            screen.fill(BLACK)
            
            # Get mouse position for hover effects
            mouse_pos = pygame.mouse.get_pos()
            
            # Get button renderer
            button = get_button()
            
            # Draw title
            title = option_font.render("Select Level", True, WHITE)
            screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2,
                              WINDOW_HEIGHT//4 - title.get_height()//2))
            
            # Draw all buttons with consistent styling
            for rect, text in [
                (debug_rect, "Debug Level"),
                (sewer_rect, "Sewer Level"),
                (back_rect, "Back")
            ]:
                button.draw(screen, rect, text, option_font,
                          is_hovered=rect.collidepoint(mouse_pos))

            # Draw debug console if provided
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)