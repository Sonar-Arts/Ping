import pygame
import random
import time
import math
import os

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLOOD_BLACK = (10, 0, 0)  # Deep blood red background
RED = (255, 0, 0)
DARK_RED = (150, 0, 0)
BRIGHT_RED = (255, 100, 100)
CRIMSON = (220, 20, 60)
BURGUNDY = (128, 0, 32)
BLOOD_RED = (102, 0, 0)
MYSTICAL_RED = (255, 50, 50)  # For the triangle glow

class Ping_Transition:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.duration = 0.3  # 0.3 seconds
        self.start_time = None
        self.is_active = False
        
        # Static effect parameters
        self.static_intensity = 1.0
        self.static_particles = []
        self.generate_static_particles()
        
        # All-seeing eye triangle parameters
        self.eye_center = (width // 2, height // 2)
        self.triangle_size = min(width, height) // 6  # Base triangle size
        self.eye_alpha = 0  # Start hidden
        self.eye_pulse_speed = 6.0  # Slower, more ominous pulsing
        self.triangle_glow_intensity = 0  # For mystical glow effect
        
        # Create surfaces for blending
        self.eye_surface = pygame.Surface((self.triangle_size * 4, self.triangle_size * 4), pygame.SRCALPHA)
        
        # Cryptic elements
        self.glitch_blocks = []
        self.symbol_flashes = []
        self.binary_numbers = ['01001000', '01100101', '01101100', '01110000']  # "Help" in binary
        self.mystical_symbols = ['△', '◯', '☥', '⧨', '⧬']  # Various cryptic symbols
        self.generate_glitch_blocks()
        
        # Static wave clustering
        self.static_wave_phase = 0
        self.wave_speed = 3.0
        
        # Sound effect management
        self.static_sound_played = False
        self.static_sound_channel = None
        self.sound_manager = None
    
    def generate_glitch_blocks(self):
        """Generate random glitch corruption blocks."""
        self.glitch_blocks = []
        num_blocks = random.randint(3, 8)
        
        for _ in range(num_blocks):
            width = random.randint(30, 120)
            height = random.randint(20, 80)
            x = random.randint(0, self.width - width)
            y = random.randint(0, self.height - height)
            intensity = random.uniform(0.3, 0.8)
            flicker_speed = random.uniform(8.0, 20.0)
            
            self.glitch_blocks.append({
                'rect': pygame.Rect(x, y, width, height),
                'intensity': intensity,
                'flicker_speed': flicker_speed,
                'phase_offset': random.uniform(0, 2 * math.pi)
            })
    
    def generate_static_particles(self):
        """Generate random static particles with clustering and color variation."""
        self.static_particles = []
        particle_density = 0.18  # Slightly higher density for more menacing effect
        num_particles = int(self.width * self.height * particle_density / 100)
        
        # Create cluster centers for wave-like static patterns
        cluster_centers = []
        for _ in range(random.randint(3, 6)):
            cluster_centers.append((
                random.randint(0, self.width),
                random.randint(0, self.height)
            ))
        
        for _ in range(num_particles):
            # 70% chance to cluster around centers, 30% random
            if random.random() < 0.7 and cluster_centers:
                center = random.choice(cluster_centers)
                cluster_radius = random.randint(50, 150)
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, cluster_radius)
                x = int(center[0] + distance * math.cos(angle))
                y = int(center[1] + distance * math.sin(angle))
                # Clamp to screen bounds
                x = max(0, min(self.width - 1, x))
                y = max(0, min(self.height - 1, y))
            else:
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
            
            size = random.randint(1, 5)  # Slightly larger particles
            brightness = random.randint(40, 255)  # Darker minimum for more contrast
            flicker_speed = random.uniform(4.0, 18.0)  # Wider range of speeds
            
            # Choose color palette (multiple red variations)
            color_choice = random.choice(['red', 'crimson', 'burgundy', 'blood', 'dark_red'])
            
            self.static_particles.append({
                'x': x,
                'y': y,
                'size': size,
                'base_brightness': brightness,
                'current_brightness': brightness,
                'flicker_speed': flicker_speed,
                'flicker_offset': random.uniform(0, 2 * math.pi),
                'color_type': color_choice,
                'wave_influence': random.uniform(0.5, 1.0)  # How much wave affects this particle
            })
    
    def start_transition(self, sound_manager=None):
        """Start the transition animation with optional sound."""
        self.start_time = time.time()
        self.is_active = True
        self.static_sound_played = False
        self.sound_manager = sound_manager
        
        # Regenerate all cryptic elements for variation
        self.generate_static_particles()
        self.generate_glitch_blocks()
        self.symbol_flashes = []
        self.static_wave_phase = 0
        
        # Start static sound effect if sound_manager is available
        if self.sound_manager and not self.static_sound_played:
            try:
                # Use the sound_manager's play_sfx method to play ArtemisStatic
                self.static_sound_channel = self.sound_manager.play_sfx('ArtemisStatic')
                self.static_sound_played = True
            except Exception as e:
                # If sound fails, continue without it
                print(f"Warning: Could not play ArtemisStatic sound: {e}")
                self.static_sound_played = True
    
    def update(self, dt):
        """Update the transition animation."""
        if not self.is_active:
            return False
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if elapsed >= self.duration:
            self.is_active = False
            # Stop the static sound when transition ends
            if self.static_sound_channel and self.sound_manager:
                try:
                    self.static_sound_channel.stop()
                except:
                    pass  # Channel might already be stopped
            return False
        
        # Calculate progress (0.0 to 1.0)  
        progress = elapsed / self.duration
        
        # Update static intensity with crescendo effect
        if progress < 0.5:
            self.static_intensity = 0.8 + (progress * 0.4)  # Build up
        else:
            self.static_intensity = 1.2 - ((progress - 0.5) * 0.4)  # Decay
        
        # Update static wave phase for clustering effects
        self.static_wave_phase += self.wave_speed * dt
        
        # Update static particles with wave clustering
        for particle in self.static_particles:
            # Base flicker effect
            flicker = math.sin(current_time * particle['flicker_speed'] + particle['flicker_offset'])
            brightness_variation = int(flicker * 60)  # Increased variation
            
            # Add wave influence for clustering effect
            wave_distance = math.sqrt((particle['x'] - self.width/2)**2 + (particle['y'] - self.height/2)**2)
            wave_effect = math.sin(self.static_wave_phase + wave_distance * 0.01) * particle['wave_influence']
            wave_brightness = int(wave_effect * 30)
            
            particle['current_brightness'] = max(0, min(255, 
                particle['base_brightness'] + brightness_variation + wave_brightness))
            
            # More aggressive particle relocation for chaos
            if random.random() < 0.035:  # 3.5% chance per frame
                particle['x'] = random.randint(0, self.width)
                particle['y'] = random.randint(0, self.height)
        
        # Update glitch blocks
        for block in self.glitch_blocks:
            block_flicker = math.sin(current_time * block['flicker_speed'] + block['phase_offset'])
            block['current_intensity'] = block['intensity'] * (0.5 + 0.5 * abs(block_flicker))
        
        # Generate symbol flashes randomly
        if random.random() < 0.08:  # 8% chance per frame for cryptic symbols
            symbol = random.choice(self.mystical_symbols + self.binary_numbers)
            self.symbol_flashes.append({
                'text': symbol,
                'x': random.randint(50, self.width - 50),
                'y': random.randint(50, self.height - 50),
                'alpha': 255,
                'decay_speed': random.uniform(300, 600)  # Alpha decay per second
            })
        
        # Update and remove expired symbol flashes
        self.symbol_flashes = [flash for flash in self.symbol_flashes if flash['alpha'] > 0]
        for flash in self.symbol_flashes:
            flash['alpha'] -= flash['decay_speed'] * dt
            flash['alpha'] = max(0, flash['alpha'])
        
        # All-seeing eye triangle effect - synchronized with static intensity
        if 0.15 <= progress <= 0.85:  # Eye is visible for longer period
            eye_visibility = math.sin((progress - 0.15) / 0.7 * math.pi)  # Sine curve for smooth in/out
            self.eye_alpha = int(eye_visibility * 140)  # Slightly more visible
            self.triangle_glow_intensity = eye_visibility * self.static_intensity  # Sync with static
        else:
            self.eye_alpha = 0
            self.triangle_glow_intensity = 0
        
        return True
    
    def draw_all_seeing_eye(self, surface):
        """Draw the all-seeing eye triangle (Illuminati style) behind the static."""
        if self.eye_alpha <= 0:
            return
        
        # Clear the eye surface
        self.eye_surface.fill((0, 0, 0, 0))
        
        # Triangle center position on surface
        center_x = self.eye_surface.get_width() // 2
        center_y = self.eye_surface.get_height() // 2
        
        # Pulsing effect for the entire triangle
        current_time = time.time()
        pulse = math.sin(current_time * self.eye_pulse_speed) * 0.15 + 1.0  # Pulse between 0.85 and 1.15
        pulsed_size = int(self.triangle_size * pulse)
        
        # Calculate triangle points (equilateral triangle pointing up)
        height = int(pulsed_size * math.sqrt(3) / 2)  # Height of equilateral triangle
        triangle_points = [
            (center_x, center_y - height // 2),  # Top point
            (center_x - pulsed_size // 2, center_y + height // 2),  # Bottom left
            (center_x + pulsed_size // 2, center_y + height // 2)   # Bottom right
        ]
        
        # Draw mystical glow around triangle
        glow_intensity = int(self.triangle_glow_intensity * 100)
        if glow_intensity > 0:
            for i in range(8, 0, -1):  # Multiple glow layers
                glow_alpha = int(glow_intensity * (i / 8) * 0.3)
                glow_color = (MYSTICAL_RED[0], MYSTICAL_RED[1], MYSTICAL_RED[2], glow_alpha)
                
                # Expand triangle points for glow
                glow_offset = i * 3
                glow_points = [
                    (triangle_points[0][0], triangle_points[0][1] - glow_offset),
                    (triangle_points[1][0] - glow_offset, triangle_points[1][1] + glow_offset),
                    (triangle_points[2][0] + glow_offset, triangle_points[2][1] + glow_offset)
                ]
                pygame.draw.polygon(self.eye_surface, glow_color, glow_points)
        
        # Draw main triangle outline (thick mystical border)
        triangle_color = (MYSTICAL_RED[0], MYSTICAL_RED[1], MYSTICAL_RED[2], self.eye_alpha)
        pygame.draw.polygon(self.eye_surface, triangle_color, triangle_points)
        
        # Draw inner triangle fill (darker)
        inner_color = (DARK_RED[0], DARK_RED[1], DARK_RED[2], int(self.eye_alpha * 0.4))
        inner_points = [
            (triangle_points[0][0], triangle_points[0][1] + 8),
            (triangle_points[1][0] + 6, triangle_points[1][1] - 6),
            (triangle_points[2][0] - 6, triangle_points[2][1] - 6)
        ]
        pygame.draw.polygon(self.eye_surface, inner_color, inner_points)
        
        # Calculate eye position inside triangle (centered)
        eye_center_x = center_x
        eye_center_y = center_y + height // 6  # Slightly below geometric center
        eye_radius = max(8, int(pulsed_size * 0.25))  # Eye size relative to triangle
        
        # Draw eye sclera (white/off-white)
        sclera_color = (240, 230, 230, self.eye_alpha)
        pygame.draw.circle(self.eye_surface, sclera_color, (eye_center_x, eye_center_y), eye_radius)
        
        # Draw iris with mystical pattern
        iris_radius = max(5, int(eye_radius * 0.7))
        iris_color = (RED[0], RED[1], RED[2], self.eye_alpha)
        pygame.draw.circle(self.eye_surface, iris_color, (eye_center_x, eye_center_y), iris_radius)
        
        # Draw radiating iris pattern
        for angle in range(0, 360, 30):  # 12 rays
            end_x = eye_center_x + int((iris_radius - 2) * math.cos(math.radians(angle)))
            end_y = eye_center_y + int((iris_radius - 2) * math.sin(math.radians(angle)))
            ray_color = (BRIGHT_RED[0], BRIGHT_RED[1], BRIGHT_RED[2], int(self.eye_alpha * 0.6))
            pygame.draw.line(self.eye_surface, ray_color, (eye_center_x, eye_center_y), (end_x, end_y), 1)
        
        # Draw pupil (black, menacing)
        pupil_radius = max(2, int(iris_radius * 0.4))
        pupil_color = (BLACK[0], BLACK[1], BLACK[2], self.eye_alpha)
        pygame.draw.circle(self.eye_surface, pupil_color, (eye_center_x, eye_center_y), pupil_radius)
        
        # Draw pupil highlight (small red gleam)
        highlight_radius = max(1, pupil_radius // 3)
        highlight_x = eye_center_x - highlight_radius
        highlight_y = eye_center_y - highlight_radius
        highlight_color = (BRIGHT_RED[0], BRIGHT_RED[1], BRIGHT_RED[2], self.eye_alpha)
        pygame.draw.circle(self.eye_surface, highlight_color, (highlight_x, highlight_y), highlight_radius)
        
        # Draw upper and lower eyelids for more realism
        eyelid_color = (CRIMSON[0], CRIMSON[1], CRIMSON[2], int(self.eye_alpha * 0.7))
        # Upper eyelid
        pygame.draw.arc(self.eye_surface, eyelid_color, 
                       (eye_center_x - eye_radius, eye_center_y - eye_radius, 
                        eye_radius * 2, eye_radius * 2), 
                       0, math.pi, 2)
        # Lower eyelid  
        pygame.draw.arc(self.eye_surface, eyelid_color,
                       (eye_center_x - eye_radius, eye_center_y - eye_radius,
                        eye_radius * 2, eye_radius * 2),
                       math.pi, 2 * math.pi, 2)
        
        # Blit all-seeing eye to main surface
        eye_rect = self.eye_surface.get_rect(center=self.eye_center)
        surface.blit(self.eye_surface, eye_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def get_color_for_particle(self, particle, brightness):
        """Get the appropriate color for a static particle based on its type."""
        color_type = particle['color_type']
        
        # Ensure brightness is within valid range
        brightness = max(0, min(255, brightness))
        
        if color_type == 'red':
            return (brightness, 0, 0)
        elif color_type == 'crimson':
            r = max(0, min(255, int(brightness * 0.86)))
            g = max(0, min(255, int(brightness * 0.08)))
            b = max(0, min(255, int(brightness * 0.24)))
            return (r, g, b)
        elif color_type == 'burgundy':
            r = max(0, min(255, int(brightness * 0.5)))
            g = 0
            b = max(0, min(255, int(brightness * 0.125)))
            return (r, g, b)
        elif color_type == 'blood':
            r = max(0, min(255, int(brightness * 0.4)))
            return (r, 0, 0)
        elif color_type == 'dark_red':
            r = max(0, min(255, int(brightness * 0.6)))
            return (r, 0, 0)
        else:
            return (brightness, 0, 0)  # Default to red
    
    def draw(self, surface):
        """Draw the enhanced cryptic transition effect."""
        if not self.is_active:
            return
        
        # Fill screen with deep blood red base instead of black
        surface.fill(BLOOD_BLACK)
        
        # Draw the all-seeing eye triangle first (behind static)
        self.draw_all_seeing_eye(surface)
        
        # Draw enhanced static with color variations
        for particle in self.static_particles:
            brightness = particle['current_brightness']
            intensity = int(brightness * self.static_intensity)
            
            # Get varied color based on particle type
            static_color = self.get_color_for_particle(particle, intensity)
            
            # Draw particle as a small rect for pixelated look
            particle_rect = pygame.Rect(particle['x'], particle['y'], 
                                      particle['size'], particle['size'])
            pygame.draw.rect(surface, static_color, particle_rect)
        
        # Draw glitch corruption blocks
        for block in self.glitch_blocks:
            if hasattr(block, 'current_intensity'):
                block_alpha = int(255 * block['current_intensity'])
                if block_alpha > 10:  # Only draw visible blocks
                    # Create corruption effect with mixed colors (ensure all values are valid)
                    corruption_colors = [
                        (max(0, min(255, int(CRIMSON[0] * block['current_intensity']))), 0, 0),
                        (max(0, min(255, int(BURGUNDY[0] * block['current_intensity']))), 0, max(0, min(255, int(BURGUNDY[2] * block['current_intensity'])))),
                        (max(0, min(255, int(BLOOD_RED[0] * block['current_intensity']))), 0, 0)
                    ]
                    
                    # Fill with random corruption colors in smaller blocks
                    block_rect = block['rect']
                    block_size = 6  # Size of corruption pixels
                    for x in range(block_rect.left, block_rect.right, block_size):
                        for y in range(block_rect.top, block_rect.bottom, block_size):
                            corruption_color = random.choice(corruption_colors)
                            mini_rect = pygame.Rect(x, y, block_size, block_size)
                            pygame.draw.rect(surface, corruption_color, mini_rect)
        
        # Enhanced scan lines with ominous patterns
        for y in range(0, self.height, 3):
            if random.random() < 0.4:  # 40% chance for scan line
                scan_brightness = random.randint(15, 90)
                # Alternate between different red shades (ensure valid color values)
                if y % 6 == 0:
                    scan_color = (scan_brightness, max(0, min(255, int(scan_brightness * 0.1))), 0)
                else:
                    scan_color = (scan_brightness, 0, max(0, min(255, int(scan_brightness * 0.1))))
                pygame.draw.line(surface, scan_color, (0, y), (self.width, y), 1)
        
        # More aggressive vertical interference with geometric patterns
        for x in range(0, self.width, random.randint(15, 45)):
            if random.random() < 0.15:  # 15% chance for vertical line
                line_brightness = random.randint(25, 120)
                line_color = (line_brightness, 0, max(0, min(255, int(line_brightness * 0.2))))
                # Occasionally draw thicker interference
                thickness = random.choice([1, 2, 3])
                pygame.draw.line(surface, line_color, (x, 0), (x, self.height), thickness)
        
        # Draw cryptic symbol flashes
        if self.symbol_flashes:
            font_size = random.randint(16, 32)
            try:
                # Use default pygame font for symbols (create a simple one)
                for flash in self.symbol_flashes:
                    if flash['alpha'] > 0:
                        # Create a simple representation of the symbol
                        symbol_color = (RED[0], RED[1], RED[2], int(flash['alpha']))
                        
                        # Draw different symbols as simple shapes
                        if flash['text'] in self.mystical_symbols:
                            if flash['text'] == '△':  # Triangle
                                symbol_points = [
                                    (flash['x'], flash['y'] - 10),
                                    (flash['x'] - 8, flash['y'] + 8),
                                    (flash['x'] + 8, flash['y'] + 8)
                                ]
                                pygame.draw.polygon(surface, symbol_color, symbol_points, 2)
                            elif flash['text'] == '◯':  # Circle
                                pygame.draw.circle(surface, symbol_color, (flash['x'], flash['y']), 10, 2)
                            else:  # Other symbols as rectangles
                                symbol_rect = pygame.Rect(flash['x'] - 8, flash['y'] - 8, 16, 16)
                                pygame.draw.rect(surface, symbol_color, symbol_rect, 2)
                        else:  # Binary numbers - draw as small rectangles
                            char_width = 4
                            for i, char in enumerate(flash['text']):
                                if char == '1':
                                    char_rect = pygame.Rect(
                                        flash['x'] + i * char_width, flash['y'], 
                                        char_width - 1, 12
                                    )
                                    pygame.draw.rect(surface, symbol_color, char_rect)
            except:
                pass  # Skip symbol drawing if there are font issues
        
        # Add edge vignette effect for claustrophobic feeling
        vignette_intensity = max(0, min(255, int(self.static_intensity * 30)))
        if vignette_intensity > 0:
            # Draw dark edges that pulse inward
            edge_width = int(50 * self.triangle_glow_intensity) if self.triangle_glow_intensity > 0 else 20
            vignette_color = (vignette_intensity, 0, 0)
            
            # Top edge
            pygame.draw.rect(surface, vignette_color, (0, 0, self.width, edge_width))
            # Bottom edge  
            pygame.draw.rect(surface, vignette_color, (0, self.height - edge_width, self.width, edge_width))
            # Left edge
            pygame.draw.rect(surface, vignette_color, (0, 0, edge_width, self.height))
            # Right edge
            pygame.draw.rect(surface, vignette_color, (self.width - edge_width, 0, edge_width, self.height))
    
    def is_finished(self):
        """Check if the transition has finished."""
        return not self.is_active


# Global transition instance
_transition_instance = None

def get_transition(width=800, height=600):
    """Get or create the global transition instance."""
    global _transition_instance
    if _transition_instance is None or _transition_instance.width != width or _transition_instance.height != height:
        _transition_instance = Ping_Transition(width, height)
    return _transition_instance

def play_transition(screen, clock, width, height, sound_manager=None):
    """Play the transition effect and block until complete."""
    transition = get_transition(width, height)
    transition.start_transition(sound_manager)
    
    last_time = time.time()
    
    while transition.is_active:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Handle events to prevent the window from becoming unresponsive
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False  # Signal to quit the game
        
        # Update and draw transition
        transition.update(dt)
        transition.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    return True  # Transition completed successfully