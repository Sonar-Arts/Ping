import pygame
from sys import exit
from .Ping_Fonts import get_pixel_font
from .Ping_Button import get_button

class PauseMenu:
    def __init__(self, sound_manager):
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.HOVER_COLOR = (100, 100, 100)
        self.sound_manager = sound_manager

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
        """Display the pause menu with options to resume, go to title screen, or settings."""
        scale_y = WINDOW_HEIGHT / 600  # Base height scale
        scale_x = WINDOW_WIDTH / 800   # Base width scale
        scale = min(scale_x, scale_y)  # Use the smaller scale to ensure text fits
        
        # Calculate button width and font size
        button_width = min(300, WINDOW_WIDTH // 3)
        font_size = max(12, int(48 * scale))  # Base size of 48, scaled with window
        option_font = get_pixel_font(font_size)
        
        # Test render the longest text to ensure it fits
        test_text = option_font.render("Back to Title", True, self.WHITE)
        while test_text.get_width() > button_width - 20 and font_size > 12:  # 20px padding
            font_size -= 1
            option_font = get_pixel_font(font_size)
            test_text = option_font.render("Back to Title", True, self.WHITE)
        
        # Create rects for buttons
        button_spacing = int(60 * scale_y)  # Vertical space between buttons
        first_button_y = WINDOW_HEIGHT//2 - button_spacing
        
        resume_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, first_button_y, 300, 50)
        title_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, first_button_y + button_spacing, 300, 50)
        settings_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, first_button_y + 2 * button_spacing, 300, 50)
        while True:
            # Get events
            events = pygame.event.get()
            
            # Handle debug console if provided
            if debug_console:
                # Check for backtick key to toggle console visibility
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == 96:  # backtick key
                        debug_console.update([event])
                        break
                
                # Handle other events if console is visible
                if debug_console.visible:
                    # Create a copy of events to modify
                    remaining_events = []
                    for event in events:
                        # Skip the backtick event since it's already handled
                        if event.type == pygame.KEYDOWN and event.key == 96:
                            continue
                        # If event is handled by console, don't add it to remaining events
                        if not debug_console.handle_event(event):
                            remaining_events.append(event)
                    events = remaining_events

            # Process remaining events
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click only
                    mouse_pos = pygame.mouse.get_pos()
                    if resume_rect.collidepoint(mouse_pos):
                        return "resume"
                    elif title_rect.collidepoint(mouse_pos):
                        self.sound_manager.stop_music() # Use new method to stop music
                        return "title"
                    elif settings_rect.collidepoint(mouse_pos):
                        return "settings"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "resume"

            screen.fill(self.BLACK)

            mouse_pos = pygame.mouse.get_pos()
            
            # Draw pause title
            pause_text = option_font.render("PAUSED", True, self.WHITE)
            screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, first_button_y - 60))

            # Get button renderer
            button = get_button()

            # Draw stylish menu buttons
            button.draw(screen, resume_rect, "Resume", option_font,
                       is_hovered=resume_rect.collidepoint(mouse_pos))
            button.draw(screen, title_rect, "Back to Title", option_font,
                       is_hovered=title_rect.collidepoint(mouse_pos))
            button.draw(screen, settings_rect, "Settings", option_font,
                        is_hovered=settings_rect.collidepoint(mouse_pos))

            # Draw debug console if active
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)