import pygame
import time
import random
import math
from .Ping_Fonts import get_pixel_font
from .Ping_Button import get_button

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (150, 150, 150)

def random_color():
    """Generate a random bright color."""
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

class Ball:
    def __init__(self, pos=None):
        self.ball_speed = 7
        self.ball_radius = 10
        self.ball_color = random_color()  # Start with random color
        self.ball_pos = list(pos) if pos else [10, 10]
        self.ball_vel = [0, 0]  # Initialize velocity
        self.randomize_direction()  # Set initial direction
    
    def randomize_direction(self):
        """Generate a random direction while maintaining constant speed."""
        angle = random.uniform(0, 2 * math.pi)
        self.ball_vel = [
            self.ball_speed * math.cos(angle),
            self.ball_speed * math.sin(angle)
        ]
    
    def randomize_color(self):
        """Change to a random color."""
        self.ball_color = random_color()
    
    def update(self):
        """Update ball position."""
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
    
    def draw(self, screen):
        """Draw the ball."""
        pygame.draw.circle(screen, self.ball_color,
                         (int(self.ball_pos[0]), int(self.ball_pos[1])),
                         self.ball_radius)
    
    def get_rect(self):
        """Get ball's collision rectangle."""
        return pygame.Rect(self.ball_pos[0] - self.ball_radius,
                         self.ball_pos[1] - self.ball_radius,
                         self.ball_radius * 2, self.ball_radius * 2)

class MainMenu:
    def __init__(self, sound_manager):
        self.options = ["1P Game", "2P Game", "Settings", "Quit"]
        self.selected_option = 0
        self.button = get_button() # Get the button renderer instance
        # Sound setup
        self.sound_manager = sound_manager # Use the passed instance
        # Title color randomization
        self.title_chars = "PING"
        self.title_char_colors = [random_color() for _ in self.title_chars]
        self.last_color_change_time = time.time()
        self.color_change_interval = 3.0 # seconds
        # Start playing main menu music
        self.sound_manager.play_music('main_theme') # Use new method

    def handle_input(self, events, width, height):
        """Handles user input for menu navigation and selection."""
        # --- Start: Calculation copied from draw method ---
        scale_y = height / 600 # Base height for scaling calculations
        scale_x = width / 800
        scale = min(scale_x, scale_y)

        # Title calculations needed to determine options area
        title_font_size = max(24, int(72 * scale))
        title_font = get_pixel_font(title_font_size)
        # Simplified title height estimation for layout (actual rendering done in draw)
        title_char_height = title_font.render("P", True, WHITE).get_height()
        title_y = height // 5
        title_bottom = title_y + (title_char_height // 2)

        # Options layout calculations
        option_font_size = max(12, int(28 * scale_y))
        # option_font = get_pixel_font(option_font_size) # Font needed only for drawing
        button_height = max(40, int(50 * scale_y))
        button_width = max(200, int(width * 0.3))
        options_area_top = title_bottom + 30 # Add some space below title
        options_area_height = height - options_area_top
        num_options = len(self.options)
        total_options_height = num_options * button_height + (num_options - 1) * 15
        start_y = options_area_top + (options_area_height - total_options_height) // 2
        # --- End: Calculation copied from draw method ---

        mouse_pos = pygame.mouse.get_pos() # Get mouse position once

        action = None

        for event in events:
            if event.type == pygame.QUIT:
                return "quit" # Signal quit immediately
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Action based on keyboard selection
                    action = self.options[self.selected_option].lower().replace(" ", "_")
                    if action == "1p_game":
                        self.sound_manager.stop_music() # Use new method
                        return True # AI mode
                    if action == "2p_game":
                        self.sound_manager.stop_music() # Use new method
                        return False # Player vs Player
                    if action == "settings":
                        self.sound_manager.stop_music() # Use new method
                        return "settings"
                    if action == "quit":
                        self.sound_manager.stop_music() # Use new method
                        return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
                for i, option in enumerate(self.options):
                    # Calculate button rect
                    button_rect = pygame.Rect(
                        width // 2 - button_width // 2,
                        start_y + i * (button_height + 15),
                        button_width,
                        button_height
                    )
                    # Check collision using the mouse position from the event
                    if button_rect.collidepoint(event.pos):
                        # Action based on clicked button
                        self.selected_option = i # Update selection to the clicked item
                        action = option.lower().replace(" ", "_")
                        if action == "1p_game":
                            self.sound_manager.stop_music() # Use new method
                            return True # AI mode
                        if action == "2p_game":
                            self.sound_manager.stop_music() # Use new method
                            return False # Player vs Player
                        if action == "settings":
                            self.sound_manager.stop_music() # Use new method
                            return "settings"
                        if action == "quit":
                            self.sound_manager.stop_music() # Use new method
                            return "quit"
                        break # Found the clicked button, no need to check others

        # Check for mouse hover *outside* the event loop using the latest mouse_pos
        # This ensures hover effect updates every frame, not just on events
        for i, option in enumerate(self.options):
            button_rect = pygame.Rect(
                width // 2 - button_width // 2,
                start_y + i * (button_height + 15),
                button_width,
                button_height
            )
            if button_rect.collidepoint(mouse_pos):
                self.selected_option = i # Update selection based on hover
                break # Stop checking once hover is found

        return None # No action taken this frame

    def draw(self, screen, width, height):
        """Draws the main menu."""
        scale_y = height / 600 # Base height for scaling calculations
        scale_x = width / 800
        scale = min(scale_x, scale_y)

        # Title
        title_font_size = max(24, int(72 * scale))
        title_font = get_pixel_font(title_font_size)

        # Check if it's time to change colors
        current_time = time.time()
        if current_time - self.last_color_change_time > self.color_change_interval:
            self.title_char_colors = [random_color() for _ in self.title_chars]
            self.last_color_change_time = current_time

        # Render each character individually
        char_surfaces = []
        total_width = 0
        char_spacing = int(title_font_size * 0.1) # Add small spacing between chars

        for i, char in enumerate(self.title_chars):
            char_surface = title_font.render(char, True, self.title_char_colors[i])
            char_surfaces.append(char_surface)
            total_width += char_surface.get_width() + char_spacing
        
        total_width -= char_spacing # Remove spacing after the last char

        # Calculate starting x position to center the whole title
        start_x = width // 2 - total_width // 2
        title_y = height // 5 # Use the adjusted higher position

        # Blit each character
        current_x = start_x
        for surface in char_surfaces:
            screen.blit(surface, (current_x, title_y - surface.get_height() // 2)) # Center vertically
            current_x += surface.get_width() + char_spacing

        # Options
        option_font_size = max(12, int(28 * scale_y))
        option_font = get_pixel_font(option_font_size)
        button_height = max(40, int(50 * scale_y))
        button_width = max(200, int(width * 0.3))
        # Use the first character's surface to estimate title bottom for options positioning
        title_bottom = title_y + (char_surfaces[0].get_height() // 2 if char_surfaces else 0)
        options_area_top = title_bottom + 30 # Add some space below title
        options_area_height = height - options_area_top
        num_options = len(self.options)
        total_options_height = num_options * button_height + (num_options - 1) * 15
        start_y = options_area_top + (options_area_height - total_options_height) // 2

        mouse_pos = pygame.mouse.get_pos() # Get current mouse position for hover effect

        for i, option in enumerate(self.options):
            button_rect = pygame.Rect(
                width // 2 - button_width // 2,
                start_y + i * (button_height + 15),
                button_width,
                button_height
            )
            is_selected = (i == self.selected_option)
            # Use the current mouse_pos for hover detection during drawing
            is_hovered = button_rect.collidepoint(mouse_pos)

            self.button.draw(screen, button_rect, option, option_font, is_selected or is_hovered)

    def display(self, screen, clock, width, height, debug_console=None):
        """Main loop for displaying and handling the menu (kept for compatibility but logic moved)."""
        print("Warning: MainMenu.display() called directly. Logic should be in TitleScreen.")
        while True:
            events = pygame.event.get()
            action = self.handle_input(events, width, height)
            if action is not None: # If an action occurred (selection or quit)
                # Stop all music if starting a game or quitting
                if action is True or action is False or action == "quit":  # True = 1P game, False = 2P game
                    self.sound_manager.stop_music() # Use new method
                return action

            clock.tick(60)