import pygame
import os # Import os for directory scanning
import math
import random
import time
# Removed import for DebugLevel, SewerLevel
from ..UI.Ping_Fonts import get_pixel_font
from ..UI.Ping_Button import get_button
from ...Audio.Ping_Sound import SoundManager

def get_ping_levels_path():
    """Get the correct path to Ping Assets/Levels directory."""
    # Get the directory of this file (Ping/Modules/Graphics/Menus/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up three levels to get to Ping directory, then into Ping Assets/Levels
    ping_levels_dir = os.path.join(current_dir, "..", "..", "..", "Ping Assets", "Levels")
    return os.path.normpath(ping_levels_dir)

class RetroAnimatedBackground:
    """Ultra-creative animated retro background for level select menu."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.start_time = time.time()
        
        # Color palette
        self.NEON_CYAN = (0, 255, 255)
        self.ELECTRIC_BLUE = (0, 120, 255)
        self.HOT_PINK = (255, 20, 147)
        self.LIME_GREEN = (0, 255, 0)
        self.DEEP_PURPLE = (25, 0, 51)
        self.MATRIX_GREEN = (0, 200, 0)
        
        # Initialize animation components
        self._init_circuit_grid()
        self._init_particles()
        self._init_sonar_waves()
        self._init_data_streams()
        self._init_geometric_shapes()
        
    def _init_circuit_grid(self):
        """Initialize the animated circuit board grid."""
        self.circuit_nodes = []
        self.circuit_paths = []
        self.data_packets = []
        
        # Create grid nodes
        grid_spacing = 80
        for x in range(0, self.width + grid_spacing, grid_spacing):
            for y in range(0, self.height + grid_spacing, grid_spacing):
                if random.random() > 0.3:  # 70% chance for node
                    self.circuit_nodes.append({
                        'x': x, 'y': y,
                        'pulse_phase': random.uniform(0, math.pi * 2),
                        'pulse_speed': random.uniform(2, 4),
                        'brightness': random.uniform(0.3, 1.0)
                    })
        
        # Create paths between nearby nodes
        for i, node_a in enumerate(self.circuit_nodes):
            for j, node_b in enumerate(self.circuit_nodes[i+1:], i+1):
                distance = math.sqrt((node_a['x'] - node_b['x'])**2 + (node_a['y'] - node_b['y'])**2)
                if distance < grid_spacing * 1.5 and random.random() > 0.6:
                    self.circuit_paths.append({
                        'start': node_a, 'end': node_b,
                        'pulse_offset': random.uniform(0, math.pi * 2)
                    })
    
    def _init_particles(self):
        """Initialize floating digital particles."""
        self.particles = []
        for _ in range(150):
            self.particles.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'vx': random.uniform(-20, 20),
                'vy': random.uniform(-15, 15),
                'size': random.uniform(1, 4),
                'color_phase': random.uniform(0, math.pi * 2),
                'blink_phase': random.uniform(0, math.pi * 2),
                'lifetime': random.uniform(0, 10)
            })
    
    def _init_sonar_waves(self):
        """Initialize sonar wave effects."""
        self.sonar_waves = []
        self.last_sonar_spawn = 0
        self.sonar_spawn_interval = random.uniform(2, 4)
    
    def _init_data_streams(self):
        """Initialize matrix-style data rain."""
        self.data_streams = []
        for _ in range(20):
            self.data_streams.append({
                'x': random.randint(0, self.width),
                'drops': [{'y': random.randint(-self.height, 0), 
                         'char': chr(random.randint(33, 126)),
                         'brightness': random.uniform(0.3, 1.0)} 
                         for _ in range(random.randint(5, 15))],
                'speed': random.uniform(30, 80)
            })
    
    def _init_geometric_shapes(self):
        """Initialize floating geometric shapes."""
        self.geometric_shapes = []
        for _ in range(30):
            shape_type = random.choice(['triangle', 'hexagon', 'diamond'])
            self.geometric_shapes.append({
                'type': shape_type,
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'vx': random.uniform(-10, 10),
                'vy': random.uniform(-10, 10),
                'rotation': random.uniform(0, math.pi * 2),
                'rotation_speed': random.uniform(-2, 2),
                'size': random.uniform(10, 30),
                'color_phase': random.uniform(0, math.pi * 2),
                'pulse_phase': random.uniform(0, math.pi * 2)
            })
    
    def update(self, dt):
        """Update all animation components."""
        current_time = time.time() - self.start_time
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['color_phase'] += dt * 2
            particle['blink_phase'] += dt * 4
            particle['lifetime'] += dt
            
            # Wrap around screen
            if particle['x'] < 0: particle['x'] = self.width
            elif particle['x'] > self.width: particle['x'] = 0
            if particle['y'] < 0: particle['y'] = self.height
            elif particle['y'] > self.height: particle['y'] = 0
        
        # Update sonar waves
        if current_time - self.last_sonar_spawn > self.sonar_spawn_interval:
            self.sonar_waves.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'radius': 0,
                'max_radius': random.uniform(100, 200),
                'lifetime': 0
            })
            self.last_sonar_spawn = current_time
            self.sonar_spawn_interval = random.uniform(2, 4)
        
        # Update existing sonar waves
        for wave in self.sonar_waves[:]:
            wave['radius'] += dt * 80
            wave['lifetime'] += dt
            if wave['radius'] > wave['max_radius']:
                self.sonar_waves.remove(wave)
        
        # Update data streams
        for stream in self.data_streams:
            for drop in stream['drops']:
                drop['y'] += stream['speed'] * dt
                if drop['y'] > self.height + 20:
                    drop['y'] = -20
                    drop['char'] = chr(random.randint(33, 126))
                    drop['brightness'] = random.uniform(0.3, 1.0)
        
        # Update geometric shapes
        for shape in self.geometric_shapes:
            shape['x'] += shape['vx'] * dt
            shape['y'] += shape['vy'] * dt
            shape['rotation'] += shape['rotation_speed'] * dt
            shape['color_phase'] += dt
            shape['pulse_phase'] += dt * 3
            
            # Wrap around screen
            if shape['x'] < -50: shape['x'] = self.width + 50
            elif shape['x'] > self.width + 50: shape['x'] = -50
            if shape['y'] < -50: shape['y'] = self.height + 50
            elif shape['y'] > self.height + 50: shape['y'] = -50
    
    def draw(self, screen):
        """Draw the complete animated background."""
        current_time = time.time() - self.start_time
        
        # Fill background with deep purple
        screen.fill(self.DEEP_PURPLE)
        
        # Draw circuit grid
        self._draw_circuit_grid(screen, current_time)
        
        # Draw particles
        self._draw_particles(screen, current_time)
        
        # Draw sonar waves
        self._draw_sonar_waves(screen)
        
        # Draw data streams
        self._draw_data_streams(screen)
        
        # Draw geometric shapes
        self._draw_geometric_shapes(screen, current_time)
    
    def _draw_circuit_grid(self, screen, current_time):
        """Draw the animated circuit board."""
        # Draw paths
        for path in self.circuit_paths:
            pulse = (math.sin(current_time * 2 + path['pulse_offset']) + 1) / 2
            brightness = int(50 + pulse * 100)
            color = (0, brightness, brightness)
            start_pos = (int(path['start']['x']), int(path['start']['y']))
            end_pos = (int(path['end']['x']), int(path['end']['y']))
            pygame.draw.line(screen, color, start_pos, end_pos, 1)
        
        # Draw nodes
        for node in self.circuit_nodes:
            pulse = (math.sin(current_time * node['pulse_speed'] + node['pulse_phase']) + 1) / 2
            brightness = int(node['brightness'] * (100 + pulse * 155))
            color = (0, brightness, brightness)
            pygame.draw.circle(screen, color, (int(node['x']), int(node['y'])), 3)
    
    def _draw_particles(self, screen, current_time):
        """Draw floating particles."""
        for particle in self.particles:
            # Color cycling
            r = int(127 + 127 * math.sin(particle['color_phase']))
            g = int(127 + 127 * math.sin(particle['color_phase'] + 2))
            b = int(127 + 127 * math.sin(particle['color_phase'] + 4))
            
            # Blinking effect
            blink = (math.sin(particle['blink_phase']) + 1) / 2
            alpha = int(blink * 255)
            
            if alpha > 50:  # Only draw if bright enough
                color = (r, g, b)
                pos = (int(particle['x']), int(particle['y']))
                pygame.draw.circle(screen, color, pos, int(particle['size']))
    
    def _draw_sonar_waves(self, screen):
        """Draw sonar wave effects."""
        for wave in self.sonar_waves:
            alpha = max(0, 255 - int(wave['lifetime'] * 100))
            if alpha > 0:
                color = (*self.NEON_CYAN, alpha)
                try:
                    # Create surface for alpha blending
                    surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    pygame.draw.circle(surf, color, (int(wave['x']), int(wave['y'])), int(wave['radius']), 2)
                    screen.blit(surf, (0, 0))
                except:
                    # Fallback without alpha
                    pygame.draw.circle(screen, self.NEON_CYAN, (int(wave['x']), int(wave['y'])), int(wave['radius']), 2)
    
    def _draw_data_streams(self, screen):
        """Draw matrix-style data rain."""
        font = get_pixel_font(12)
        for stream in self.data_streams:
            for i, drop in enumerate(stream['drops']):
                brightness = int(drop['brightness'] * 255)
                if i == 0:  # Head of stream is brighter
                    color = (brightness, 255, brightness)
                else:
                    color = (0, brightness, 0)
                
                try:
                    text_surf = font.render(drop['char'], True, color)
                    screen.blit(text_surf, (stream['x'], int(drop['y'])))
                except:
                    pass  # Skip if character can't be rendered
    
    def _draw_geometric_shapes(self, screen, current_time):
        """Draw floating geometric shapes."""
        for shape in self.geometric_shapes:
            # Color cycling
            r = int(127 + 127 * math.sin(shape['color_phase']))
            g = int(127 + 127 * math.sin(shape['color_phase'] + 2))
            b = int(127 + 127 * math.sin(shape['color_phase'] + 4))
            
            # Pulsing size
            pulse = (math.sin(shape['pulse_phase']) + 1) / 2
            size = shape['size'] * (0.7 + 0.3 * pulse)
            
            color = (r, g, b)
            center = (int(shape['x']), int(shape['y']))
            
            # Draw different shapes
            if shape['type'] == 'triangle':
                self._draw_rotated_triangle(screen, center, size, shape['rotation'], color)
            elif shape['type'] == 'hexagon':
                self._draw_rotated_hexagon(screen, center, size, shape['rotation'], color)
            elif shape['type'] == 'diamond':
                self._draw_rotated_diamond(screen, center, size, shape['rotation'], color)
    
    def _draw_rotated_triangle(self, screen, center, size, rotation, color):
        """Draw a rotated triangle."""
        points = []
        for i in range(3):
            angle = rotation + i * 2 * math.pi / 3
            x = center[0] + size * math.cos(angle)
            y = center[1] + size * math.sin(angle)
            points.append((x, y))
        
        if len(points) >= 3:
            pygame.draw.polygon(screen, color, points, 2)
    
    def _draw_rotated_hexagon(self, screen, center, size, rotation, color):
        """Draw a rotated hexagon."""
        points = []
        for i in range(6):
            angle = rotation + i * math.pi / 3
            x = center[0] + size * math.cos(angle)
            y = center[1] + size * math.sin(angle)
            points.append((x, y))
        
        if len(points) >= 3:
            pygame.draw.polygon(screen, color, points, 2)
    
    def _draw_rotated_diamond(self, screen, center, size, rotation, color):
        """Draw a rotated diamond."""
        points = []
        for i in range(4):
            angle = rotation + i * math.pi / 2
            x = center[0] + size * math.cos(angle)
            y = center[1] + size * math.sin(angle)
            points.append((x, y))
        
        if len(points) >= 3:
            pygame.draw.polygon(screen, color, points, 2)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class LevelSelect:
    def __init__(self, sound_manager):
        self.scroll_y = 0  # Initialize scroll position for level list
        self.sound_manager = sound_manager  # Use the passed instance
        self.levels = [] # List to store level data (instance or path)
        self.background = None
        self.last_update = time.time()
        self._load_levels()
    
    def _load_levels(self):
        """Scans for levels (hardcoded and PMF files)."""
        self.levels = []
        # Add hardcoded levels first
        # Removed hardcoded Debug and Sewer levels

        # Scan for PMF files
        level_dir = get_ping_levels_path()
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

    def initialize_background(self, width, height):
        """Initialize the animated background with current screen dimensions."""
        self.background = RetroAnimatedBackground(width, height)
    
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
            # Initialize background if needed
            if self.background is None:
                self.initialize_background(WINDOW_WIDTH, WINDOW_HEIGHT)

            # Update background animation
            current_time = time.time()
            dt = current_time - self.last_update
            self.last_update = current_time
            self.background.update(dt)

            # Create a transparent surface for scrollable content
            total_height = 800  # Height for scrollable content
            content_surface = pygame.Surface((WINDOW_WIDTH, total_height), pygame.SRCALPHA)
            content_surface.fill((0, 0, 0, 0))  # Transparent fill
            
            # Adjust button dimensions and spacing
            button_height = min(40, WINDOW_HEIGHT // 15)  # Reduced button height
            button_spacing = button_height + 15 # Slightly more spacing
            
            # Title area height
            title_area_height = 60  # Smaller title area
            
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
            content_surface = pygame.Surface((WINDOW_WIDTH, total_content_height), pygame.SRCALPHA)
            content_surface.fill((0, 0, 0, 0))  # Transparent fill

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

            # Draw animated background
            self.background.draw(screen)
            
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
            
            # Draw title with animated background showing through
            title = option_font.render("SELECT LEVEL", True, WHITE)
            title_x = WINDOW_WIDTH//2 - title.get_width()//2
            title_y = title_area_height//2 - title.get_height()//2
            screen.blit(title, (title_x, title_y))

            # Draw back button (fixed at bottom, drawn after content blit)
            button.draw(screen, back_rect, "Back", option_font,
                        is_hovered=back_rect.collidepoint(mouse_pos)) # Use direct collision check

            # Draw debug console if provided
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)