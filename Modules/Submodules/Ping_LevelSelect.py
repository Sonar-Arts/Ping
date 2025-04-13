import pygame
from .Ping_Levels import DebugLevel, SewerLevel  # Added Sewer Level import
from .Ping_Fonts import get_pixel_font
from .Ping_Button import get_button

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class LevelSelect:
    def __init__(self):
        self.scroll_y = 0  # Initialize scroll position for level list
    
    def _create_brick_pattern(self, width, height):
        """Create a brick pattern background surface."""
        surface = pygame.Surface((width, height))
        brick_width = 30  # Smaller bricks
        brick_height = 15
        brick_color = (40, 40, 40)  # Darker gray for bricks
        brick_outline = (70, 70, 70)  # Outline color
        brick_highlight = (50, 50, 50)  # Slightly lighter for top edge

        # Draw brick pattern
        for y in range(0, height, brick_height):
            offset = brick_width // 2 if (y // brick_height) % 2 == 1 else 0
            for x in range(-offset, width + brick_width, brick_width):
                # Main brick rectangle
                brick_rect = pygame.Rect(x, y, brick_width - 1, brick_height - 1)
                # Draw main brick
                pygame.draw.rect(surface, brick_color, brick_rect)
                # Draw outline
                pygame.draw.rect(surface, brick_outline, brick_rect, 1)
                # Draw highlight on top edge
                pygame.draw.line(surface, brick_highlight,
                               (brick_rect.left, brick_rect.top),
                               (brick_rect.right, brick_rect.top))
        return surface
    
    def _check_button_hover(self, rect, mouse_pos, title_area_height):
        """Helper function to check button hover with proper scroll offset and title area"""
        return rect.collidepoint(mouse_pos[0], mouse_pos[1] - self.scroll_y - title_area_height)

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
            # Create a surface for scrollable content
            total_height = 800  # Height for scrollable content
            content_surface = pygame.Surface((WINDOW_WIDTH, total_height))
            content_surface.fill(BLACK)
            
            # Adjust button dimensions and spacing
            button_height = min(40, WINDOW_HEIGHT // 15)  # Reduced button height
            button_spacing = button_height + 10  # Reduced spacing between buttons
            
            # Create title area with brick pattern
            title_area_height = 60  # Smaller title area
            title_area = self._create_brick_pattern(WINDOW_WIDTH, title_area_height)
            
            # Draw title centered in brick area
            title = option_font.render("Select Level", True, WHITE)
            title_x = WINDOW_WIDTH//2 - title.get_width()//2
            title_y = (title_area_height - title.get_height()) // 2
            title_area.blit(title, (title_x, title_y))
            
            # Start positions for content (after title area)
            current_y = 40  # Give more initial space for better appearance
            
            # Create rectangles for level buttons
            debug_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                   current_y,
                                   button_width, button_height)
            current_y += button_spacing
            
            sewer_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2,
                                   current_y,
                                   button_width, button_height)
            current_y += button_spacing * 2  # Extra space before back button
            
            # Back button stays fixed at bottom
            back_button_y = WINDOW_HEIGHT - button_height - 20

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
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click only
                    mouse_pos = event.pos
                    
                    # Adjust mouse position for content area
                    content_mouse_pos = (mouse_pos[0], mouse_pos[1] - title_area_height)
                    
                    # Check buttons with scroll offset for level buttons
                    if self._check_button_hover(debug_rect, content_mouse_pos, title_area_height):
                        return DebugLevel()
                    elif self._check_button_hover(sewer_rect, content_mouse_pos, title_area_height):
                        return SewerLevel()
                    # Back button doesn't need scroll offset since it's fixed
                    elif back_button_y <= mouse_pos[1] <= back_button_y + button_height:
                        if WINDOW_WIDTH//2 - button_width//2 <= mouse_pos[0] <= WINDOW_WIDTH//2 + button_width//2:
                            return "back"
                            
                if event.type == pygame.MOUSEWHEEL:
                    scroll_amount = event.y * 20  # Reduced scroll speed
                    # Adjust scroll bounds to account for title area
                    max_scroll = -(total_height - (WINDOW_HEIGHT - title_area_height))
                    self.scroll_y = min(0, max(max_scroll, self.scroll_y + scroll_amount))

            screen.fill(BLACK)
            
            # Get mouse position for hover effects
            mouse_pos = pygame.mouse.get_pos()
            
            # Get button renderer
            button = get_button()
            
            # Draw level buttons on content surface
            for rect, text in [
                (debug_rect, "Debug Level"),
                (sewer_rect, "Sewer Level")
            ]:
                button.draw(content_surface, rect, text, option_font,
                           is_hovered=self._check_button_hover(rect, mouse_pos, title_area_height))
            
            # Draw scrollable content with offset for title area
            visible_rect = pygame.Rect(0, -self.scroll_y, WINDOW_WIDTH, WINDOW_HEIGHT - title_area_height)
            screen.blit(content_surface, (0, title_area_height), visible_rect)
            
            # Draw title area (fixed position)
            screen.blit(title_area, (0, 0))
            
            # Create and draw back button (fixed at bottom)
            back_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, back_button_y,
                                  button_width, button_height)
            button.draw(screen, back_rect, "Back", option_font,
                       is_hovered=back_rect.collidepoint(mouse_pos))

            # Draw debug console if provided
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)