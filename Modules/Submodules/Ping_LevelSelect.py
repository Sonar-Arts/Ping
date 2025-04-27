import pygame
import os # Import os for directory scanning
# Removed import for DebugLevel, SewerLevel
from .Ping_Fonts import get_pixel_font
from .Ping_Button import get_button
from .Ping_Sound import SoundManager

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class LevelSelect:
    def __init__(self, sound_manager):
        self.scroll_y = 0  # Initialize scroll position for level list
        self.sound_manager = sound_manager  # Use the passed instance
        self.levels = [] # List to store level data (instance or path)
        self._load_levels()
    
    def _load_levels(self):
        """Scans for levels (hardcoded and PMF files)."""
        self.levels = []
        # Add hardcoded levels first
        # Removed hardcoded Debug and Sewer levels

        # Scan for PMF files
        level_dir = "Ping_Levels"
        try:
            if os.path.isdir(level_dir):
                for filename in os.listdir(level_dir):
                    if filename.lower().endswith(".pmf"):
                        level_name = os.path.splitext(filename)[0].replace('_', ' ').title() # Nicer name
                        level_path = os.path.join(level_dir, filename).replace('\\', '/') # Use forward slashes for consistency
                        self.levels.append({'name': level_name, 'source': level_path})
        except Exception as e:
            print(f"Error scanning level directory '{level_dir}': {e}")
            # Continue without PMF levels if scanning fails

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
        adjusted_y = mouse_pos[1] - title_area_height - self.scroll_y
        return rect.collidepoint(mouse_pos[0], adjusted_y)

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
        """Display the level select screen with optional debug console."""
        scale_y = WINDOW_HEIGHT / 600  # Base height scale
        scale_x = WINDOW_WIDTH / 800   # Base width scale
        scale = min(scale_x, scale_y)  # Use the smaller scale
        
        button_width = min(300, WINDOW_WIDTH // 3)
        
        # Calculate font size and ensure it fits
        option_font_size = max(12, int(36 * scale))  # Starting with slightly smaller base size
        option_font = get_pixel_font(option_font_size)
        
        # Test all texts to ensure they fit
        test_texts = [level['name'] for level in self.levels] + ["Back"]
        while any(option_font.render(text, True, WHITE).get_width() > button_width - 20
                 for text in test_texts) and option_font_size > 12:
            option_font_size -= 2 # Decrease faster if needed
            option_font = get_pixel_font(option_font_size)
        
        while True:
            # Create a surface for scrollable content
            total_height = 800  # Height for scrollable content
            content_surface = pygame.Surface((WINDOW_WIDTH, total_height))
            content_surface.fill(BLACK)
            
            # Adjust button dimensions and spacing
            button_height = min(40, WINDOW_HEIGHT // 15)  # Reduced button height
            button_spacing = button_height + 15 # Slightly more spacing
            
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
            
            # Store button rects and associated level data
            level_buttons = []
            button_y_pos = current_y # Start position for buttons within the content surface
            for level_data in self.levels:
                rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, button_y_pos, button_width, button_height)
                level_buttons.append({'rect': rect, 'data': level_data})
                button_y_pos += button_spacing

            # Calculate total content height needed based on buttons drawn
            total_content_height = button_y_pos + 40 # Add some padding at the bottom
            # Recreate content surface with correct height
            content_surface = pygame.Surface((WINDOW_WIDTH, total_content_height))
            content_surface.fill(BLACK)

            # Back button stays fixed at bottom
            back_button_y = WINDOW_HEIGHT - button_height - 20
            back_rect = pygame.Rect(WINDOW_WIDTH//2 - button_width//2, back_button_y, button_width, button_height) # Define back_rect here for click check

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
                    
                    # Check level buttons (using adjusted hover check)
                    for button_info in level_buttons:
                        if self._check_button_hover(button_info['rect'], mouse_pos, title_area_height):
                            # self.sound_manager.stop_music() # Removed - Let main_game handle music transition
                            level_source = button_info['data']['source']
                            if isinstance(level_source, str): # It's a PMF path
                                print(f"Selected PMF Level: {level_source}") # Debug print
                                return level_source # Return the path
                            # Removed handling for class-based levels as they are deleted

                    # Check back button (fixed position, no scroll adjustment needed)
                    if back_rect.collidepoint(mouse_pos):
                        # self.sound_manager.stop_music() # Removed - Let title screen handle music
                        return "back"

                if event.type == pygame.MOUSEWHEEL:
                    scroll_amount = event.y * 20  # Reduced scroll speed
                    # Adjust scroll bounds based on dynamic content height
                    scrollable_area_height = WINDOW_HEIGHT - title_area_height
                    # Only allow scrolling if content height exceeds visible area
                    if total_content_height > scrollable_area_height:
                        max_scroll = -(total_content_height - scrollable_area_height)
                    else:
                        max_scroll = 0 # No scrolling needed if content fits
                    self.scroll_y = min(0, max(max_scroll, self.scroll_y + scroll_amount))

            screen.fill(BLACK)
            
            # Get mouse position for hover effects
            mouse_pos = pygame.mouse.get_pos()
            
            # Get button renderer
            button = get_button()
            
            # Draw level buttons onto the dynamically sized content_surface
            for button_info in level_buttons:
                rect = button_info['rect']
                text = button_info['data']['name']
                # Hover check needs the *original* mouse position relative to the screen
                # but the drawing happens on the content_surface at rect's coordinates
                button.draw(content_surface, rect, text, option_font,
                           is_hovered=self._check_button_hover(rect, mouse_pos, title_area_height))

            # Draw scrollable content area onto the main screen
            # The source rect starts at (0, -self.scroll_y) to select the visible part
            visible_content_rect = pygame.Rect(0, -self.scroll_y, WINDOW_WIDTH, WINDOW_HEIGHT - title_area_height)
            screen.blit(content_surface, (0, title_area_height), visible_content_rect)
            
            # Draw title area (fixed position, drawn after content blit)
            screen.blit(title_area, (0, 0))

            # Draw back button (fixed at bottom, drawn after content blit)
            button.draw(screen, back_rect, "Back", option_font,
                        is_hovered=back_rect.collidepoint(mouse_pos)) # Use direct collision check

            # Draw debug console if provided
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)