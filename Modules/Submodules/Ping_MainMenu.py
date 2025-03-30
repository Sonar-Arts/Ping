import pygame
import time
import random
import math
from .Ping_Fonts import get_pixel_font
from .Ping_Button import get_button

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def random_color():
    """Generate a random color."""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

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
    def __init__(self):
        self.last_color_change = time.time()
        self.title_letters = list("Ping")
        self.title_colors = [WHITE] * len(self.title_letters)
        self.balls = [Ball()]  # Start with one ball
        self.ball_clicked = False  # Track if ball has been clicked
        
        # Initialize sound
        self.wahahoo_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/wahahoo.wav")
        self.wahahoo_sound.set_volume(0.5)

    def play_pitch_varied_wahahoo(self):
        """Play wahahoo sound at random pitch from predefined set."""
        if self.ball_clicked:  # Only play if ball has been clicked
            # List of distinct pitch speeds for variety
            pitch_speeds = [
                0.25,  # Very low pitch (2 octaves down)
                0.5,   # Low pitch (1 octave down)
                0.75,  # Slightly low pitch
                1.0,   # Normal pitch
                1.5,   # Medium high pitch
                2.0,   # High pitch (1 octave up)
                2.5,   # Very high pitch
                3.0    # Highest pitch
            ]
            speed = random.choice(pitch_speeds)
            self.wahahoo_sound.play(maxtime=int(self.wahahoo_sound.get_length() * 1000 / speed))

    def handle_ball_collisions(self, ball, pvp_rect, ai_rect, settings_rect, title_rect, WINDOW_WIDTH, WINDOW_HEIGHT):
        """Handle all collision checks for a single ball."""
        collision = False
        
        # Screen edge collisions
        if (ball.ball_pos[0] - ball.ball_radius <= 0 or 
            ball.ball_pos[0] + ball.ball_radius >= WINDOW_WIDTH or
            ball.ball_pos[1] - ball.ball_radius <= 0 or 
            ball.ball_pos[1] + ball.ball_radius >= WINDOW_HEIGHT):
            collision = True
        
        # Ball collision rectangle
        ball_rect = ball.get_rect()
        
        # Button collisions
        for button in [pvp_rect, ai_rect, settings_rect]:
            if ball_rect.colliderect(button):
                collision = True
                break
        
        # Title collision
        if ball_rect.colliderect(title_rect):
            collision = True
        
        # If any collision occurred, randomize direction and color
        if collision:
            ball.randomize_direction()
            ball.randomize_color()
            self.play_pitch_varied_wahahoo()

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT, debug_console=None):
        """Display the title screen with game options and handle debug console."""
        scale_y = WINDOW_HEIGHT / 600
        scale_x = WINDOW_WIDTH / 800
        scale = min(scale_x, scale_y)
        
        # Calculate button dimensions
        button_width = min(300, WINDOW_WIDTH // 3)
        
        # Calculate font sizes
        title_font_size = max(12, int(74 * scale))
        title_font = get_pixel_font(title_font_size)
        
        option_font_size = max(12, int(48 * scale))
        option_font = get_pixel_font(option_font_size)
        
        # Test render to ensure text fits
        test_text = option_font.render("Player vs Player", True, WHITE)
        while test_text.get_width() > button_width - 20 and option_font_size > 12:
            option_font_size -= 1
            option_font = get_pixel_font(option_font_size)
            test_text = option_font.render("Player vs Player", True, WHITE)
        
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

            events = pygame.event.get()
            
            if debug_console:
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == 96:
                        debug_console.update([event])
                        continue
                    if debug_console.visible:
                        if debug_console.handle_event(event):
                            continue

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if pvp_rect.collidepoint(mouse_pos):
                        return False  # PvP mode
                    elif ai_rect.collidepoint(mouse_pos):
                        return True   # AI mode
                    elif settings_rect.collidepoint(mouse_pos):
                        return "settings"
                    # Check for ball clicks
                    for ball in self.balls[:]:
                        if ball.get_rect().collidepoint(mouse_pos):
                            self.ball_clicked = True
                            ball.randomize_direction()
                            ball.randomize_color()
                            self.play_pitch_varied_wahahoo()
                            new_ball = Ball(ball.ball_pos[:])
                            self.balls.append(new_ball)
                            break

            screen.fill(BLACK)

            # Update title colors
            current_time = time.time()
            if current_time - self.last_color_change >= 3:
                self.title_colors = [random_color() for _ in self.title_letters]
                self.last_color_change = current_time

            # Draw title with rainbow effect
            title_width = sum(title_font.render(letter, True, self.title_colors[i]).get_width() 
                            for i, letter in enumerate(self.title_letters)) + (len(self.title_letters) - 1) * 5
            x_offset = (WINDOW_WIDTH - title_width) // 2
            
            # Draw each letter with its color
            for i, letter in enumerate(self.title_letters):
                text = title_font.render(letter, True, self.title_colors[i])
                screen.blit(text, (x_offset, WINDOW_HEIGHT//4))
                x_offset += text.get_width() + 5

            # Get button renderer
            button = get_button()
            
            # Draw stylish menu buttons
            mouse_pos = pygame.mouse.get_pos()
            button.draw(screen, pvp_rect, "Player vs Player", option_font,
                       is_hovered=pvp_rect.collidepoint(mouse_pos))
            button.draw(screen, ai_rect, "Player vs AI", option_font,
                       is_hovered=ai_rect.collidepoint(mouse_pos))
            button.draw(screen, settings_rect, "Settings", option_font,
                       is_hovered=settings_rect.collidepoint(mouse_pos))

            # Create title collision rect
            title_rect = pygame.Rect(x_offset - title_width, WINDOW_HEIGHT//4,
                                   title_width * 2,
                                   title_font.get_height())

            # Update and handle collisions for all balls
            for ball in self.balls:
                ball.update()
                self.handle_ball_collisions(ball, pvp_rect, ai_rect, settings_rect, title_rect, WINDOW_WIDTH, WINDOW_HEIGHT)
                ball.draw(screen)

            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)