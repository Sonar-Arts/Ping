import pygame
import time
import random
import math

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

    def display(self, screen, clock, WINDOW_WIDTH, WINDOW_HEIGHT):
        """Display the title screen with game options."""
        scale_y = WINDOW_HEIGHT / 600  # Base height scale
        scale_x = WINDOW_WIDTH / 800   # Base width scale
        scale = min(scale_x, scale_y)  # Use the smaller scale to ensure text fits
        
        # Calculate font sizes based on both dimensions
        button_width = min(300, WINDOW_WIDTH // 3)
        
        # Title font scaling
        title_font_size = max(12, int(74 * scale))
        title_font = pygame.font.Font(None, title_font_size)
        
        # Option font scaling with fit check
        option_font_size = max(12, int(48 * scale))
        option_font = pygame.font.Font(None, option_font_size)
        
        # Test render the longest text to ensure it fits
        test_text = option_font.render("Player vs Player", True, WHITE)
        while test_text.get_width() > button_width - 20 and option_font_size > 12:  # 20px padding
            option_font_size -= 1
            option_font = pygame.font.Font(None, option_font_size)
            test_text = option_font.render("Player vs Player", True, WHITE)
        
        settings_text = option_font.render("Settings", True, WHITE)
        
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
                    mouse_pos = event.pos
                    # Check menu button clicks
                    if pvp_rect.collidepoint(mouse_pos):
                        return False  # PvP mode
                    elif ai_rect.collidepoint(mouse_pos):
                        return True   # AI mode
                    elif settings_rect.collidepoint(mouse_pos):
                        return "settings"
                    # Check for ball clicks
                    for ball in self.balls[:]:  # Use slice to avoid modifying list during iteration
                        if ball.get_rect().collidepoint(mouse_pos):
                            # Set ball clicked flag and handle first click
                            self.ball_clicked = True
                            # Randomize clicked ball's direction and spawn new ball
                            ball.randomize_direction()
                            ball.randomize_color()
                            self.play_pitch_varied_wahahoo()
                            new_ball = Ball(ball.ball_pos[:])  # Create new ball at same position
                            self.balls.append(new_ball)
                            break  # Only handle one ball click per frame

            screen.fill(BLACK)

            # Update title colors
            current_time = time.time()
            if current_time - self.last_color_change >= 3:
                self.title_colors = [random_color() for _ in self.title_letters]
                self.last_color_change = current_time

            # Draw title
            title_width = sum(title_font.render(letter, True, self.title_colors[i]).get_width() 
                            for i, letter in enumerate(self.title_letters)) + (len(self.title_letters) - 1) * 5
            x_offset = (WINDOW_WIDTH - title_width) // 2
            
            for i, letter in enumerate(self.title_letters):
                text = title_font.render(letter, True, self.title_colors[i])
                screen.blit(text, (x_offset, WINDOW_HEIGHT//4))
                x_offset += text.get_width() + 5
            
            hover_color = (100, 100, 100)
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw menu buttons
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

            # Create title collision rect
            title_rect = pygame.Rect(x_offset - title_width, WINDOW_HEIGHT//4,
                                   title_width * 2,
                                   title_font.get_height())

            # Update and handle collisions for all balls
            for ball in self.balls:
                ball.update()
                self.handle_ball_collisions(ball, pvp_rect, ai_rect, settings_rect, title_rect, WINDOW_WIDTH, WINDOW_HEIGHT)
                ball.draw(screen)

            pygame.display.flip()
            clock.tick(60)