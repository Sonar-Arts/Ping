import pygame
import math
import random
import time
import os
from sys import exit
from ..UI.Ping_Fonts import get_pixel_font
from ..UI.Ping_Button import get_button

class RetroAnimatedBackground:
    """Ultra-creative animated retro background for quick play menu."""
    
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

class QuickPlayMenu:
    def __init__(self, sound_manager):
        self.options = ["1P Game", "2P Game", "Back"]
        self.selected_option = 0
        self.button = get_button()
        self.sound_manager = sound_manager
        self.background = None
        self.last_update = time.time()

    def initialize_background(self, width, height):
        """Initialize the animated background with current screen dimensions."""
        self.background = RetroAnimatedBackground(width, height)

    def handle_input(self, events, width, height):
        """Handles user input for menu navigation and selection."""
        # Calculate scaling for consistent layout
        scale_y = height / 600
        scale_x = width / 800
        scale = min(scale_x, scale_y)

        # Calculate button dimensions and positions
        button_width = int(200 * scale)
        button_height = int(60 * scale)
        button_spacing = int(20 * scale)
        
        total_buttons_height = len(self.options) * button_height + (len(self.options) - 1) * button_spacing
        start_y = (height - total_buttons_height) // 2
        
        # Create button rectangles for mouse interaction
        button_rects = []
        for i in range(len(self.options)):
            button_x = (width - button_width) // 2
            button_y = start_y + i * (button_height + button_spacing)
            button_rects.append(pygame.Rect(button_x, button_y, button_width, button_height))

        # Handle mouse input
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(button_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_option = i
                break

        # Handle events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    return self._get_selection_result()
                elif event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key == pygame.K_BACKQUOTE:
                    return "debug_console"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(event.pos):
                            self.selected_option = i
                            return self._get_selection_result()

        return None

    def _get_selection_result(self):
        """Return the appropriate result based on selected option."""
        if self.selected_option == 0:  # 1P Game
            return True
        elif self.selected_option == 1:  # 2P Game
            return False
        elif self.selected_option == 2:  # Back
            return "back"
        return None

    def draw(self, screen, width, height):
        """Draw the quick play menu."""
        # Initialize background if needed
        if self.background is None:
            self.initialize_background(width, height)

        # Update background animation
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        self.background.update(dt)

        # Draw animated background
        self.background.draw(screen)

        # Calculate scaling
        scale_y = height / 600
        scale_x = width / 800
        scale = min(scale_x, scale_y)

        # Draw title
        title_font_size = max(24, int(48 * scale))
        title_font = get_pixel_font(title_font_size)
        title_text = title_font.render("QUICK PLAY", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(width // 2, int(height * 0.25)))
        screen.blit(title_text, title_rect)

        # Draw buttons
        button_width = int(200 * scale)
        button_height = int(60 * scale)
        button_spacing = int(20 * scale)
        font_size = max(12, int(24 * scale))
        
        total_buttons_height = len(self.options) * button_height + (len(self.options) - 1) * button_spacing
        start_y = (height - total_buttons_height) // 2

        for i, option in enumerate(self.options):
            button_x = (width - button_width) // 2
            button_y = start_y + i * (button_height + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            is_selected = (i == self.selected_option)
            font = get_pixel_font(font_size)
            self.button.draw(screen, button_rect, option, font, is_selected)