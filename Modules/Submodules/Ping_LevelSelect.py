import pygame
from .Ping_Levels import DebugLevel, SewerLevel  # Added Sewer Level import
from .Ping_Fonts import get_font_manager
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
        
        # Get font manager and calculate font size
        font_manager = get_font_manager()
        option_font_size = max(12, int(48 * scale))
        option_font = font_manager.get_font('menu', option_font_size)
        
        # Test render the longest text to ensure it fits
        test_text = option_font.render("Debug Level", True, WHITE)
        while test_text.get_width() > button_width - 20 and option_font_size > 12:  # 20px padding
            option_font_size -= 1
            option_font = font_manager.get_font('menu', option_font_size)
            test_text = option_font.render("Debug Level", True, WHITE)
        
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
                    # Move the handle_event check inside the event loop
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
            
            hover_color = (100, 100, 100)
            mouse_pos = pygame.mouse.get_pos()
            
            # Get button renderer
            button = get_button()
            
            # Draw stylish menu buttons
            button.draw(screen, debug_rect, "Debug Level", option_font,
                       is_hovered=debug_rect.collidepoint(mouse_pos))
            button.draw(screen, back_rect, "Back", option_font,
                       is_hovered=back_rect.collidepoint(mouse_pos))
            # Draw all buttons
            for rect, text in [
                (debug_rect, "Debug Level"),
                (sewer_rect, "Sewer Level"),
                (back_rect, "Back")
            ]:
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, hover_color, rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
                
                text_surface = option_font.render(text, True, WHITE)
                screen.blit(text_surface, (rect.centerx - text_surface.get_width()//2,
                                         rect.centery - text_surface.get_height()//2))
            
            # Draw debug console if provided
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)