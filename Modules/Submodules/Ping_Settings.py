import pygame
import math
import random
import time
from sys import exit
from .Ping_Fonts import get_pixel_font
from .Ping_Button import get_button

class RetroAnimatedBackground:
    """Ultra-creative animated retro background for settings menu."""
    
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
        self._init_terminal_windows()
        self._init_geometric_shapes()
        self._init_title_easter_eggs()
        
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
                'speed': random.uniform(50, 150),
                'spawn_rate': random.uniform(0.1, 0.3)
            })
    
    def _init_terminal_windows(self):
        """Initialize floating terminal windows."""
        self.terminal_windows = []
        for _ in range(3):
            self.terminal_windows.append({
                'x': random.uniform(50, self.width - 200),
                'y': random.uniform(50, self.height - 150),
                'width': random.uniform(180, 250),
                'height': random.uniform(100, 180),
                'drift_speed': random.uniform(5, 15),
                'drift_direction': random.uniform(0, math.pi * 2),
                'text_lines': [f"> {chr(random.randint(65, 90))}{chr(random.randint(65, 90))}{random.randint(100, 999)}"
                              for _ in range(random.randint(4, 8))],
                'cursor_blink': 0,
                'alpha': random.uniform(0.3, 0.7)
            })
    
    def _init_geometric_shapes(self):
        """Initialize rotating wireframe shapes."""
        self.geometric_shapes = []
        for _ in range(4):
            self.geometric_shapes.append({
                'x': random.uniform(100, self.width - 100),
                'y': random.uniform(100, self.height - 100),
                'rotation': 0,
                'rotation_speed': random.uniform(30, 60),
                'size': random.uniform(30, 60),
                'shape_type': random.choice(['cube', 'pyramid', 'diamond']),
                'color': random.choice([self.NEON_CYAN, self.HOT_PINK, self.LIME_GREEN]),
                'pulse_phase': random.uniform(0, math.pi * 2)
            })
    
    def _init_title_easter_eggs(self):
        """Initialize subtle 'PING' title appearances."""
        self.title_effects = {
            'particle_constellation': {
                'last_spawn': 0,
                'interval': random.uniform(45, 90),  # 45-90 seconds
                'active': False,
                'formation_particles': [],
                'formation_timer': 0,
                'formation_duration': 8.0,
                'letter_positions': self._calculate_ping_positions()
            },
            'circuit_spell': {
                'last_spawn': 0,
                'interval': random.uniform(60, 120),  # 1-2 minutes
                'active': False,
                'target_nodes': [],
                'spell_timer': 0,
                'spell_duration': 6.0
            },
            'data_stream_message': {
                'last_spawn': 0,
                'interval': random.uniform(30, 75),  # 30-75 seconds
                'active': False,
                'message_streams': [],
                'message_timer': 0,
                'message_duration': 10.0
            }
        }
    
    def _calculate_ping_positions(self):
        """Calculate positions for PING letters formation."""
        letter_width = 30
        letter_spacing = 40
        total_width = 4 * letter_width + 3 * letter_spacing
        start_x = (self.width - total_width) // 2
        center_y = self.height // 2
        
        # Define simple letter patterns (5x7 grid for each letter)
        patterns = {
            'P': [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2),(0,3),(0,4),(0,5),(0,6)],
            'I': [(0,0),(1,0),(2,0),(1,1),(1,2),(1,3),(1,4),(1,5),(0,6),(1,6),(2,6)],
            'N': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,2),(2,1),(3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(3,6)],
            'G': [(1,0),(2,0),(0,1),(0,2),(0,3),(0,4),(0,5),(1,6),(2,6),(3,6),(3,3),(3,4),(3,5),(2,3)]
        }
        
        positions = {}
        letters = ['P', 'I', 'N', 'G']
        for i, letter in enumerate(letters):
            letter_x = start_x + i * (letter_width + letter_spacing)
            positions[letter] = []
            for x_offset, y_offset in patterns[letter]:
                positions[letter].append((
                    letter_x + x_offset * 4,
                    center_y - 14 + y_offset * 4
                ))
        
        return positions
    
    def update(self, dt, mouse_pos=None):
        """Update all animation components."""
        current_time = time.time() - self.start_time
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['lifetime'] += dt
            
            # Mouse interaction
            if mouse_pos:
                dx = mouse_pos[0] - particle['x']
                dy = mouse_pos[1] - particle['y']
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < 100:
                    force = (100 - distance) / 100 * 30
                    particle['vx'] += (dx / distance) * force * dt
                    particle['vy'] += (dy / distance) * force * dt
            
            # Wrap around screen
            if particle['x'] < 0: particle['x'] = self.width
            if particle['x'] > self.width: particle['x'] = 0
            if particle['y'] < 0: particle['y'] = self.height
            if particle['y'] > self.height: particle['y'] = 0
        
        # Update sonar waves
        current_time_sonar = time.time()
        if current_time_sonar - self.last_sonar_spawn > self.sonar_spawn_interval:
            self.sonar_waves.append({
                'x': random.randint(100, self.width - 100),
                'y': random.randint(100, self.height - 100),
                'radius': 0,
                'max_radius': random.uniform(150, 300),
                'color': random.choice([self.NEON_CYAN, self.ELECTRIC_BLUE, self.LIME_GREEN]),
                'birth_time': current_time_sonar
            })
            self.last_sonar_spawn = current_time_sonar
            self.sonar_spawn_interval = random.uniform(2, 5)
        
        # Update existing sonar waves
        self.sonar_waves = [wave for wave in self.sonar_waves 
                           if current_time_sonar - wave['birth_time'] < 4]
        for wave in self.sonar_waves:
            age = current_time_sonar - wave['birth_time']
            wave['radius'] = (age / 4) * wave['max_radius']
        
        # Update data streams
        for stream in self.data_streams:
            for drop in stream['drops']:
                drop['y'] += stream['speed'] * dt
                if drop['y'] > self.height:
                    drop['y'] = -20
                    drop['char'] = chr(random.randint(33, 126))
                    drop['brightness'] = random.uniform(0.3, 1.0)
        
        # Update terminal windows
        for window in self.terminal_windows:
            window['x'] += math.cos(window['drift_direction']) * window['drift_speed'] * dt
            window['y'] += math.sin(window['drift_direction']) * window['drift_speed'] * dt
            window['cursor_blink'] += dt * 2
            
            # Bounce off edges
            if window['x'] < 0 or window['x'] + window['width'] > self.width:
                window['drift_direction'] = math.pi - window['drift_direction']
            if window['y'] < 0 or window['y'] + window['height'] > self.height:
                window['drift_direction'] = -window['drift_direction']
        
        # Update geometric shapes
        for shape in self.geometric_shapes:
            shape['rotation'] += shape['rotation_speed'] * dt
            shape['pulse_phase'] += dt * 3
        
        # Update title easter eggs
        self._update_title_effects(dt, current_time)
    
    def draw(self, surface):
        """Draw all background elements."""
        current_time = time.time() - self.start_time
        
        # Fill with deep space background
        surface.fill(self.DEEP_PURPLE)
        
        # Draw circuit grid
        self._draw_circuit_grid(surface, current_time)
        
        # Draw sonar waves
        self._draw_sonar_waves(surface)
        
        # Draw particles
        self._draw_particles(surface, current_time)
        
        # Draw data streams
        self._draw_data_streams(surface)
        
        # Draw terminal windows
        self._draw_terminal_windows(surface)
        
        # Draw geometric shapes
        self._draw_geometric_shapes(surface, current_time)
        
        # Draw title easter eggs
        self._draw_title_effects(surface, current_time)
    
    def _draw_circuit_grid(self, surface, current_time):
        """Draw the animated circuit board."""
        # Draw paths
        for path in self.circuit_paths:
            pulse = math.sin(current_time * 2 + path['pulse_offset']) * 0.5 + 0.5
            alpha = int(pulse * 100 + 50)
            color = (*self.ELECTRIC_BLUE, alpha)
            
            start_pos = (int(path['start']['x']), int(path['start']['y']))
            end_pos = (int(path['end']['x']), int(path['end']['y']))
            
            # Create temporary surface for alpha blending
            temp_surf = pygame.Surface((abs(end_pos[0] - start_pos[0]) + 4, 
                                      abs(end_pos[1] - start_pos[1]) + 4), pygame.SRCALPHA)
            relative_start = (2, 2)
            relative_end = (end_pos[0] - start_pos[0] + 2, end_pos[1] - start_pos[1] + 2)
            
            pygame.draw.line(temp_surf, color[:3], relative_start, relative_end, 2)
            temp_surf.set_alpha(alpha)
            surface.blit(temp_surf, (min(start_pos[0], end_pos[0]) - 2, 
                                   min(start_pos[1], end_pos[1]) - 2))
        
        # Draw nodes
        for node in self.circuit_nodes:
            pulse = math.sin(current_time * node['pulse_speed'] + node['pulse_phase']) * 0.5 + 0.5
            radius = int(pulse * 4 + 2)
            brightness = int(node['brightness'] * 255)
            color = (brightness, brightness, 255)
            
            pygame.draw.circle(surface, color, (int(node['x']), int(node['y'])), radius)
            pygame.draw.circle(surface, self.NEON_CYAN, (int(node['x']), int(node['y'])), radius, 1)
    
    def _draw_sonar_waves(self, surface):
        """Draw expanding sonar rings."""
        for wave in self.sonar_waves:
            if wave['radius'] > 0:
                age_factor = wave['radius'] / wave['max_radius']
                alpha = int((1 - age_factor) * 150)
                
                if alpha > 0:
                    temp_surf = pygame.Surface((wave['max_radius'] * 2 + 10, 
                                              wave['max_radius'] * 2 + 10), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surf, (*wave['color'], alpha), 
                                     (int(wave['max_radius'] + 5), int(wave['max_radius'] + 5)), 
                                     int(wave['radius']), 2)
                    temp_surf.set_alpha(alpha)
                    surface.blit(temp_surf, (wave['x'] - wave['max_radius'] - 5, 
                                           wave['y'] - wave['max_radius'] - 5))
    
    def _draw_particles(self, surface, current_time):
        """Draw floating digital particles."""
        for particle in self.particles:
            # Color cycling
            color_shift = math.sin(current_time * 2 + particle['color_phase']) * 0.5 + 0.5
            r = int(self.HOT_PINK[0] * color_shift + self.NEON_CYAN[0] * (1 - color_shift))
            g = int(self.HOT_PINK[1] * color_shift + self.NEON_CYAN[1] * (1 - color_shift))
            b = int(self.HOT_PINK[2] * color_shift + self.NEON_CYAN[2] * (1 - color_shift))
            
            # Blinking effect
            blink = math.sin(current_time * 4 + particle['blink_phase']) * 0.3 + 0.7
            alpha = int(blink * 255)
            
            # Draw particle with glow
            glow_radius = int(particle['size'] + 2)
            temp_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            # Outer glow
            pygame.draw.circle(temp_surf, (r//3, g//3, b//3, alpha//3), 
                             (glow_radius, glow_radius), glow_radius)
            # Inner particle
            pygame.draw.circle(temp_surf, (r, g, b, alpha), 
                             (glow_radius, glow_radius), int(particle['size']))
            
            surface.blit(temp_surf, (particle['x'] - glow_radius, particle['y'] - glow_radius))
    
    def _draw_data_streams(self, surface):
        """Draw matrix-style data rain."""
        font = get_pixel_font(12)
        
        for stream in self.data_streams:
            for i, drop in enumerate(stream['drops']):
                brightness = int(drop['brightness'] * 255)
                # Fade effect for trail
                trail_factor = 1.0 - (i / len(stream['drops'])) * 0.7
                color = (0, int(brightness * trail_factor), 0)
                
                try:
                    char_surface = font.render(drop['char'], True, color)
                    surface.blit(char_surface, (stream['x'], int(drop['y'])))
                except pygame.error:
                    pass  # Skip problematic characters
    
    def _draw_terminal_windows(self, surface):
        """Draw floating retro terminal windows."""
        font = get_pixel_font(10)
        
        for window in self.terminal_windows:
            # Window background
            temp_surf = pygame.Surface((int(window['width']), int(window['height'])), pygame.SRCALPHA)
            pygame.draw.rect(temp_surf, (0, 50, 0, int(window['alpha'] * 100)), 
                           (0, 0, int(window['width']), int(window['height'])))
            pygame.draw.rect(temp_surf, self.MATRIX_GREEN, 
                           (0, 0, int(window['width']), int(window['height'])), 2)
            
            # Window title bar
            pygame.draw.rect(temp_surf, (0, 80, 0, int(window['alpha'] * 150)), 
                           (2, 2, int(window['width']) - 4, 20))
            
            # Terminal text
            y_offset = 25
            for line in window['text_lines']:
                if y_offset < window['height'] - 15:
                    try:
                        text_surf = font.render(line, True, self.MATRIX_GREEN)
                        temp_surf.blit(text_surf, (5, y_offset))
                        y_offset += 12
                    except pygame.error:
                        pass
            
            # Blinking cursor
            if math.sin(window['cursor_blink']) > 0:
                cursor_rect = pygame.Rect(5 + len(window['text_lines'][-1]) * 6, 
                                        y_offset - 12, 8, 10)
                pygame.draw.rect(temp_surf, self.MATRIX_GREEN, cursor_rect)
            
            surface.blit(temp_surf, (int(window['x']), int(window['y'])))
    
    def _draw_geometric_shapes(self, surface, current_time):
        """Draw rotating wireframe geometric shapes."""
        for shape in self.geometric_shapes:
            pulse = math.sin(current_time * 2 + shape['pulse_phase']) * 0.3 + 0.7
            size = int(shape['size'] * pulse)
            
            # Simplified wireframe drawing
            center_x, center_y = int(shape['x']), int(shape['y'])
            rotation = math.radians(shape['rotation'])
            
            if shape['shape_type'] == 'cube':
                # Draw a rotating square with 3D effect
                points = []
                for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
                    x = center_x + math.cos(angle + rotation) * size
                    y = center_y + math.sin(angle + rotation) * size
                    points.append((int(x), int(y)))
                
                if len(points) >= 3:
                    pygame.draw.polygon(surface, shape['color'], points, 2)
                    
                # 3D effect - second square offset
                offset_points = []
                for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
                    x = center_x + math.cos(angle + rotation) * size * 0.7 + 10
                    y = center_y + math.sin(angle + rotation) * size * 0.7 - 10
                    offset_points.append((int(x), int(y)))
                
                if len(offset_points) >= 3 and len(points) >= 3:
                    pygame.draw.polygon(surface, shape['color'], offset_points, 1)
                    # Connect corners
                    for i in range(4):
                        pygame.draw.line(surface, shape['color'], points[i], offset_points[i], 1)
            
            elif shape['shape_type'] == 'diamond':
                points = []
                for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
                    x = center_x + math.cos(angle + rotation) * size
                    y = center_y + math.sin(angle + rotation) * size * 0.6
                    points.append((int(x), int(y)))
                
                if len(points) >= 3:
                    pygame.draw.polygon(surface, shape['color'], points, 2)
    
    def _update_title_effects(self, dt, current_time):
        """Update all title easter egg effects."""
        # Update particle constellation effect
        constellation = self.title_effects['particle_constellation']
        if not constellation['active']:
            if current_time - constellation['last_spawn'] > constellation['interval']:
                constellation['active'] = True
                constellation['formation_timer'] = 0
                constellation['last_spawn'] = current_time
                constellation['interval'] = random.uniform(45, 90)
                self._spawn_ping_constellation()
        else:
            constellation['formation_timer'] += dt
            if constellation['formation_timer'] > constellation['formation_duration']:
                constellation['active'] = False
                constellation['formation_particles'] = []
        
        # Update constellation particles
        for particle in constellation['formation_particles']:
            # Move towards target position
            target_x, target_y = particle['target_pos']
            dx = target_x - particle['x']
            dy = target_y - particle['y']
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 2:
                speed = 50 * dt
                particle['x'] += (dx / distance) * speed
                particle['y'] += (dy / distance) * speed
            
            particle['brightness'] = min(1.0, particle['brightness'] + dt * 2)
        
        # Update circuit spelling effect
        circuit_spell = self.title_effects['circuit_spell']
        if not circuit_spell['active']:
            if current_time - circuit_spell['last_spawn'] > circuit_spell['interval']:
                circuit_spell['active'] = True
                circuit_spell['spell_timer'] = 0
                circuit_spell['last_spawn'] = current_time
                circuit_spell['interval'] = random.uniform(60, 120)
                self._select_ping_circuit_nodes()
        else:
            circuit_spell['spell_timer'] += dt
            if circuit_spell['spell_timer'] > circuit_spell['spell_duration']:
                circuit_spell['active'] = False
                circuit_spell['target_nodes'] = []
        
        # Update data stream message effect
        data_message = self.title_effects['data_stream_message']
        if not data_message['active']:
            if current_time - data_message['last_spawn'] > data_message['interval']:
                data_message['active'] = True
                data_message['message_timer'] = 0
                data_message['last_spawn'] = current_time
                data_message['interval'] = random.uniform(30, 75)
                self._spawn_ping_data_streams()
        else:
            data_message['message_timer'] += dt
            if data_message['message_timer'] > data_message['message_duration']:
                data_message['active'] = False
                data_message['message_streams'] = []
        
        # Update message streams
        for stream in data_message['message_streams']:
            stream['y'] += stream['speed'] * dt
            if stream['y'] > self.height + 50:
                stream['y'] = -50
                stream['chars'] = list("PING"[stream['letter_index']] * 8)
    
    def _spawn_ping_constellation(self):
        """Spawn particles that will form PING constellation."""
        constellation = self.title_effects['particle_constellation']
        constellation['formation_particles'] = []
        
        letters = ['P', 'I', 'N', 'G']
        for letter in letters:
            positions = constellation['letter_positions'][letter]
            for target_pos in positions:
                # Start particles from random positions
                start_x = random.uniform(0, self.width)
                start_y = random.uniform(0, self.height)
                
                constellation['formation_particles'].append({
                    'x': start_x,
                    'y': start_y,
                    'target_pos': target_pos,
                    'brightness': 0.0,
                    'color': random.choice([self.NEON_CYAN, self.HOT_PINK, self.LIME_GREEN])
                })
    
    def _select_ping_circuit_nodes(self):
        """Select circuit nodes to spell PING."""
        circuit_spell = self.title_effects['circuit_spell']
        circuit_spell['target_nodes'] = []
        
        # Find nodes that roughly match PING positions
        letter_positions = self.title_effects['particle_constellation']['letter_positions']
        for letter in ['P', 'I', 'N', 'G']:
            target_positions = letter_positions[letter]
            for target_pos in target_positions[:5]:  # Limit to 5 positions per letter
                # Find closest circuit node
                closest_node = None
                min_distance = float('inf')
                
                for node in self.circuit_nodes:
                    distance = math.sqrt((node['x'] - target_pos[0])**2 + (node['y'] - target_pos[1])**2)
                    if distance < min_distance and distance < 100:  # Within reasonable range
                        min_distance = distance
                        closest_node = node
                
                if closest_node:
                    circuit_spell['target_nodes'].append(closest_node)
    
    def _spawn_ping_data_streams(self):
        """Spawn data streams that spell PING."""
        data_message = self.title_effects['data_stream_message']
        data_message['message_streams'] = []
        
        letters = ['P', 'I', 'N', 'G']
        for i, letter in enumerate(letters):
            # Create streams at specific x positions
            x_pos = self.width // 5 * (i + 1)
            data_message['message_streams'].append({
                'x': x_pos,
                'y': random.uniform(-200, -50),
                'speed': random.uniform(30, 60),
                'chars': list(letter * 8),  # Repeat letter
                'letter_index': i,
                'color': random.choice([self.MATRIX_GREEN, self.NEON_CYAN, self.LIME_GREEN])
            })
    
    def _draw_title_effects(self, surface, current_time):
        """Draw all title easter egg effects."""
        # Draw particle constellation
        constellation = self.title_effects['particle_constellation']
        if constellation['active']:
            for particle in constellation['formation_particles']:
                if particle['brightness'] > 0.1:
                    alpha = int(particle['brightness'] * 255)
                    temp_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
                    pygame.draw.circle(temp_surf, (*particle['color'], alpha), (4, 4), 3)
                    pygame.draw.circle(temp_surf, (255, 255, 255, alpha//2), (4, 4), 2)
                    surface.blit(temp_surf, (particle['x'] - 4, particle['y'] - 4))
        
        # Draw circuit spelling effect
        circuit_spell = self.title_effects['circuit_spell']
        if circuit_spell['active']:
            spell_progress = circuit_spell['spell_timer'] / circuit_spell['spell_duration']
            pulse_intensity = math.sin(current_time * 8) * 0.5 + 0.5
            
            for node in circuit_spell['target_nodes']:
                # Enhanced glow for selected nodes
                radius = int(6 + pulse_intensity * 4)
                alpha = int((1 - spell_progress * 0.3) * 255)
                temp_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (255, 255, 0, alpha), (radius, radius), radius)
                pygame.draw.circle(temp_surf, (255, 255, 255, alpha), (radius, radius), radius//2)
                surface.blit(temp_surf, (node['x'] - radius, node['y'] - radius))
        
        # Draw data stream message
        data_message = self.title_effects['data_stream_message']
        if data_message['active']:
            font = get_pixel_font(16)
            for stream in data_message['message_streams']:
                for i, char in enumerate(stream['chars']):
                    char_y = stream['y'] + i * 20
                    if 0 <= char_y <= self.height:
                        # Enhanced fade effect matching the regular data streams
                        trail_factor = 1.0 - (i / len(stream['chars'])) * 0.7
                        
                        # Additional fade based on distance from top of screen
                        position_fade = 1.0
                        if char_y < 100:  # Fade in when appearing
                            position_fade = char_y / 100
                        elif char_y > self.height - 100:  # Fade out when leaving
                            position_fade = (self.height - char_y) / 100
                        
                        # Combine both fade effects
                        final_fade = trail_factor * position_fade
                        brightness = int(final_fade * 255)
                        
                        # Apply brightness to color components (similar to regular streams)
                        r, g, b = stream['color']
                        faded_color = (
                            int(r * final_fade),
                            int(g * final_fade), 
                            int(b * final_fade)
                        )
                        
                        try:
                            char_surface = font.render(char, True, faded_color)
                            surface.blit(char_surface, (stream['x'], char_y))
                        except pygame.error:
                            pass

class SettingsScreen:
    """A class to handle the settings screen functionality and game settings."""

    # Class level variables
    WINDOW_WIDTH = 800  # Default value
    WINDOW_HEIGHT = 600  # Default value
    PLAYER_NAME = "Player"  # Default value
    PLAYER_B_NAME = "Player B"  # Default value for 2P mode
    SHADER_ENABLED = True  # Default value
    RETRO_EFFECTS_ENABLED = True  # Default value
    SCANLINE_INTENSITY = 40  # Default value
    GLOW_INTENSITY = 80  # Default value
    VS_BLINK_SPEED = 5.0  # Default value
    SCORE_GLOW_COLOR = "180,180,255"  # Default value
    MASTER_VOLUME = 100  # Default value
    EFFECTS_VOLUME = 100  # Default value
    MUSIC_VOLUME = 100  # Default value
    SCORE_EFFECT_INTENSITY = 50  # Default value
    WIN_SCORES = 10  # Default value for scores needed to win
    DISPLAY_MODE_DEFAULT = "Windowed" # Default display mode

    @classmethod
    def get_dimensions(cls):
        """Get current window dimensions."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                              if '=' in line and not line.strip().startswith('#'))
                width = int(settings.get('WINDOW_WIDTH', cls.WINDOW_WIDTH))
                height = int(settings.get('WINDOW_HEIGHT', cls.WINDOW_HEIGHT))
                return width, height
        except Exception as e:
            print(f"Error loading dimensions: {e}")
            return cls.WINDOW_WIDTH, cls.WINDOW_HEIGHT

    @classmethod
    def update_dimensions(cls, width, height):
        """Update window dimensions in settings file."""
        try:
            current_settings = {}
            try:
                with open("Game Parameters/settings.txt", "r") as f:
                    current_settings = dict(line.strip().split('=') for line in f
                                         if '=' in line and not line.strip().startswith('#'))
            except:
                pass

            current_settings['WINDOW_WIDTH'] = width
            current_settings['WINDOW_HEIGHT'] = height

            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating dimensions: {e}")
            return False

    @classmethod
    def get_player_name(cls):
        """Get current player name from settings."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                              if '=' in line and not line.strip().startswith('#'))
                return settings.get('PLAYER_NAME', cls.PLAYER_NAME)
        except Exception as e:
            print(f"Error loading player name: {e}")
            return cls.PLAYER_NAME

    @classmethod
    def update_player_name(cls, name):
        """Update player name in settings file."""
        try:
            current_settings = {}
            try:
                with open("Game Parameters/settings.txt", "r") as f:
                    current_settings = dict(line.strip().split('=') for line in f
                                         if '=' in line and not line.strip().startswith('#'))
            except:
                pass

            current_settings['PLAYER_NAME'] = name

            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating player name: {e}")
            return False
    @classmethod
    def get_shader_enabled(cls):
        """Get current shader enabled state from settings."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                              if '=' in line and not line.strip().startswith('#'))
                return settings.get('SHADER_ENABLED', 'true').lower() == 'true'
        except Exception as e:
            print(f"Error loading shader setting: {e}")
            return cls.SHADER_ENABLED

    @classmethod
    def update_shader_enabled(cls, enabled):
        """Update shader enabled state in settings file."""
        try:
            current_settings = {}
            with open("Game Parameters/settings.txt", "r") as f:
                current_settings = dict(line.strip().split('=') for line in f
                                   if '=' in line and not line.strip().startswith('#'))
            current_settings['SHADER_ENABLED'] = str(enabled).lower()
            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating shader setting: {e}")
            return False

    @classmethod
    def get_win_scores(cls):
        """Get current win scores setting."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                           if '=' in line and not line.strip().startswith('#'))
                return int(settings.get('WIN_SCORES', cls.WIN_SCORES))
        except Exception as e:
            print(f"Error loading win scores: {e}")
            return cls.WIN_SCORES

    @classmethod
    def update_win_scores(cls, scores):
        """Update win scores in settings file."""
        try:
            current_settings = {}
            with open("Game Parameters/settings.txt", "r") as f:
                current_settings = dict(line.strip().split('=') for line in f
                                   if '=' in line and not line.strip().startswith('#'))
            current_settings['WIN_SCORES'] = scores
            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating win scores: {e}")
            return False

    @classmethod
    def get_sound_debug_enabled(cls):
        """Get current sound debug enabled state from settings."""
        # Default to False if not found or error occurs
        default_value = False
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = dict(line.strip().split('=') for line in f
                              if '=' in line and not line.strip().startswith('#'))
                # Read as string 'true'/'false' and convert to boolean
                return settings.get('SOUND_DEBUG_ENABLED', str(default_value)).lower() == 'true'
        except Exception as e:
            print(f"Error loading sound debug setting: {e}")
            return default_value

    @classmethod
    def update_sound_debug_enabled(cls, enabled):
        """Update sound debug enabled state in settings file."""
        try:
            current_settings = {}
            try: # Read existing settings first to preserve others
                with open("Game Parameters/settings.txt", "r") as f:
                    current_settings = dict(line.strip().split('=') for line in f
                                         if '=' in line and not line.strip().startswith('#'))
            except FileNotFoundError:
                 print("Settings file not found, creating new one.")
            except Exception as e:
                 print(f"Error reading existing settings: {e}")
                 # Continue anyway, will overwrite if necessary

            current_settings['SOUND_DEBUG_ENABLED'] = str(enabled).lower() # Save as 'true' or 'false'

            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in current_settings.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error updating sound debug setting: {e}")
            return False

    def __init__(self):
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        # Initialize animated background (will be properly sized in display method)
        self.animated_background = None
        self.last_update_time = time.time()
        self.screen_sizes = [
            (640, 480), (800, 600), (1024, 768), (1280, 720), (1280, 1024),
            (1366, 768), (1440, 900), (1600, 900), (1680, 1050), (1920, 1080),
            (2560, 1440), (3440, 1440)
        ]
        self.screen_sizes.sort() # Ensure they are sorted
        self.dropdown_item_height = 25  # Height for dropdown menu items
        self.dropdown_scroll_offset = 0 # For scrolling resolution options
        self.dropdown_max_visible_items = 5 # Max items visible in dropdown

        self.display_modes = ["Windowed", "Borderless", "Fullscreen"]
        self.current_display_mode = self.DISPLAY_MODE_DEFAULT
        self.original_loaded_display_mode = self.DISPLAY_MODE_DEFAULT
        # Find default index for original_loaded_size_index
        default_w, default_h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        self.original_loaded_size_index = 0
        for i, (w, h) in enumerate(self.screen_sizes):
            if w == default_w and h == default_h:
                self.original_loaded_size_index = i
                break
        
        self._display_settings_changed_on_save = False
        self.show_display_modes = False # For the new display mode dropdown


        # Initialize settings with defaults
        self.current_size_index = self.original_loaded_size_index # Start with default/loaded
        self.player_name = self.PLAYER_NAME
        self.player_b_name = self.PLAYER_B_NAME
        self.shader_enabled = self.SHADER_ENABLED
        self.retro_effects_enabled = self.RETRO_EFFECTS_ENABLED
        self.scroll_y = 0  # Initialize scroll position
        self.scanline_intensity = self.SCANLINE_INTENSITY
        self.glow_intensity = self.GLOW_INTENSITY
        self.vs_blink_speed = self.VS_BLINK_SPEED
        self.score_glow_color = self.SCORE_GLOW_COLOR
        self.master_volume = self.MASTER_VOLUME
        self.effects_volume = self.EFFECTS_VOLUME
        self.music_volume = self.MUSIC_VOLUME
        self.score_effect_intensity = self.SCORE_EFFECT_INTENSITY

        self._load_settings()

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

    def _load_settings(self):
        """Load settings from the settings file."""
        try:
            with open("Game Parameters/settings.txt", "r") as f:
                settings = {}
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=')
                        settings[key] = value

                width = int(settings.get('WINDOW_WIDTH', self.WINDOW_WIDTH))
                height = int(settings.get('WINDOW_HEIGHT', self.WINDOW_HEIGHT))

                # Find matching resolution index
                for i, (w_s, h_s) in enumerate(self.screen_sizes): # Renamed w,h to avoid conflict
                    if w_s == width and h_s == height:
                        self.current_size_index = i
                        break
                self.original_loaded_size_index = self.current_size_index

                self.current_display_mode = settings.get('DISPLAY_MODE', self.DISPLAY_MODE_DEFAULT)
                self.original_loaded_display_mode = self.current_display_mode

                self.player_name = settings.get('PLAYER_NAME', self.PLAYER_NAME)
                self.player_b_name = settings.get('PLAYER_B_NAME', self.PLAYER_B_NAME)
                self.shader_enabled = settings.get('SHADER_ENABLED', 'true').lower() == 'true'
                self.retro_effects_enabled = settings.get('RETRO_EFFECTS_ENABLED', 'true').lower() == 'true'
                self.scanline_intensity = int(settings.get('SCANLINE_INTENSITY', self.SCANLINE_INTENSITY))
                self.glow_intensity = int(settings.get('GLOW_INTENSITY', self.GLOW_INTENSITY))
                self.vs_blink_speed = float(settings.get('VS_BLINK_SPEED', self.VS_BLINK_SPEED))
                self.score_glow_color = settings.get('SCORE_GLOW_COLOR', self.SCORE_GLOW_COLOR)
                self.master_volume = int(settings.get('MASTER_VOLUME', self.MASTER_VOLUME))
                self.effects_volume = int(settings.get('EFFECTS_VOLUME', self.EFFECTS_VOLUME))
                self.music_volume = int(settings.get('MUSIC_VOLUME', self.MUSIC_VOLUME))
                self.score_effect_intensity = int(settings.get('SCORE_EFFECT_INTENSITY', self.SCORE_EFFECT_INTENSITY))

        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save current settings to file."""
        try:
            if self.current_display_mode == "Borderless":
                desktop_info = pygame.display.Info()
                width_to_save = desktop_info.current_w
                height_to_save = desktop_info.current_h
            else:
                width_to_save, height_to_save = self.screen_sizes[self.current_size_index]
            
            settings_dict = {
                'WINDOW_WIDTH': width_to_save,
                'WINDOW_HEIGHT': height_to_save,
                'DISPLAY_MODE': self.current_display_mode,
                'PLAYER_NAME': self.player_name,
                'PLAYER_B_NAME': self.player_b_name,
                'SHADER_ENABLED': str(self.shader_enabled).lower(),
                'RETRO_EFFECTS_ENABLED': str(self.retro_effects_enabled).lower(),
                'SCANLINE_INTENSITY': self.scanline_intensity,
                'GLOW_INTENSITY': self.glow_intensity,
                'VS_BLINK_SPEED': self.vs_blink_speed,
                'SCORE_GLOW_COLOR': self.score_glow_color,
                'MASTER_VOLUME': self.master_volume,
                'EFFECTS_VOLUME': self.effects_volume,
                'MUSIC_VOLUME': self.music_volume,
                'SCORE_EFFECT_INTENSITY': self.score_effect_intensity
            }

            with open("Game Parameters/settings.txt", "w") as f:
                for key, value in settings_dict.items():
                    f.write(f"{key}={value}\n")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    # Updated signature: removed paddle_sound, score_sound, added sound_manager
    def display(self, screen, clock, sound_manager, WINDOW_WIDTH, WINDOW_HEIGHT, in_game=False, debug_console=None):
        # Store debug_console reference
        self.debug_console = debug_console
        """Display the settings screen and handle its events."""
        # sound_manager is now passed directly as an argument

        # Play settings menu music
        sound_manager.play_music('PSettingsMenuMusicTemp')

        # Initialize animated background if not already done
        if self.animated_background is None:
            self.animated_background = RetroAnimatedBackground(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Apply initial volumes (already loaded in __init__ or _load_settings)

        while True:
            events = pygame.event.get()

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

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Update animated background
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.last_update_time = current_time
            
            mouse_pos = pygame.mouse.get_pos()
            self.animated_background.update(dt, mouse_pos)
            
            # Draw animated background
            self.animated_background.draw(screen)

            # Draw settings and handle events
            # Removed sound_test_fn and updated back_fn logic
            back_target = "back_to_pause" if in_game else "title"
            # Pass sound_manager to draw_settings_screen
            result = self.draw_settings_screen(screen, events, lambda: back_target, sound_manager)

            # Draw debug console if active
            if debug_console:
                debug_console.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

            pygame.display.flip()
            clock.tick(60)

            # Handle return action (could be "title" or "back_to_pause")
            if result == "title" or result == "back_to_pause":
                # Determine the width, height, and mode to be potentially returned.
                # This should reflect the current UI selection that was just saved or is active.
                returned_mode = self.current_display_mode
                if returned_mode == "Borderless":
                    # If borderless is selected, the W/H to return for application
                    # should be the desktop's W/H.
                    desktop_info = pygame.display.Info()
                    returned_width = desktop_info.current_w
                    returned_height = desktop_info.current_h
                else:
                    # For Windowed/Fullscreen, use the resolution from the UI selection.
                    returned_width, returned_height = self.screen_sizes[self.current_size_index]

                name_changed_flag = hasattr(self, '_name_changed') and self._name_changed

                if self._display_settings_changed_on_save:
                    self._display_settings_changed_on_save = False # Reset flag
                    if name_changed_flag:
                        if hasattr(self, '_name_changed'): del self._name_changed
                        return ("display_and_name_change", returned_width, returned_height, returned_mode, self.player_name)
                    else:
                        return ("display_change", returned_width, returned_height, returned_mode)
                elif name_changed_flag:
                    if hasattr(self, '_name_changed'): del self._name_changed
                    # Name change is signalled, main menu will handle saving it if user confirms.
                    # If display settings were also changed in UI but not saved, they are discarded here.
                    return ("name_change", self.player_name)
                elif result == "back_to_pause":
                    # No save, or save with no display changes. Discard UI display changes.
                    return (result, WINDOW_WIDTH, WINDOW_HEIGHT) # Return active game dimensions
                else: # result == "title", no save or save with no display changes
                    return "title" # Discard UI display changes

    def _check_button_hover(self, rect, mouse_pos):
        """Helper function to check button hover with proper scroll offset and title area adjustment"""
        title_area_height = 60  # Match the title area height used in draw_settings_screen

        # Adjust mouse position for scroll and title area
        adjusted_y = mouse_pos[1] - self.scroll_y - title_area_height
        # Check collision using adjusted y
        return rect.collidepoint(mouse_pos[0], adjusted_y)

    # Updated signature: removed sound_test_fn
    def draw_settings_screen(self, screen, events, back_fn=None, sound_manager=None):
        """Draw the settings screen with all options."""
        # Note: Background is now drawn by animated background in display method
        # pygame.event.clear([pygame.MOUSEMOTION]) # Clearing events here might miss clicks

        # Get fonts and button instance
        title_font = get_pixel_font(24)
        font = get_pixel_font(20)
        small_font = get_pixel_font(16)
        button = get_button()

        # Calculate positions and layout dimensions
        width, height = screen.get_width(), screen.get_height()
        left_column_x = width // 4  # Left column at 1/4 width
        right_column_x = (width * 3) // 4  # Right column at 3/4 width
        button_width = min(200, width // 4)  # Limit button width

        # Create a surface for scrollable content with subtle transparency
        total_height = 1800  # Further Increased height for potential display mode dropdown
        content_surface = pygame.Surface((width, total_height), pygame.SRCALPHA)
        # Add very subtle dark overlay for text readability while keeping background visible
        content_surface.fill((0, 0, 0, 40))

        # Initialize positions
        current_y = 50
        spacing = 50
        title_area_height = 60  # Smaller title area

        # Handle scrolling with mouse wheel (but not when over dropdown)
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                # Handle scrolling for resolution dropdown or main content
                # Check if mouse is over an open dropdown first (resolution or display mode)
                
                # Resolution Dropdown Scroll Check
                is_over_res_dropdown = False
                if hasattr(self, 'show_resolutions') and self.show_resolutions:
                    # Calculate the absolute screen rect of the resolution button
                    # Initial current_y for display mode button is 20, then spacing, then res button
                    # So, res_btn_y_on_surface = 20 (initial) + spacing (for display_mode)
                    res_btn_y_on_surface = 20 + spacing
                    res_btn_rect_abs = pygame.Rect(
                        right_column_x - button_width // 2,
                        res_btn_y_on_surface + self.scroll_y + title_area_height,
                        button_width, 35
                    )
                    num_visible_dd_items = min(len(self.screen_sizes), self.dropdown_max_visible_items)
                    actual_visible_dropdown_height = num_visible_dd_items * self.dropdown_item_height
                    dropdown_area_abs = pygame.Rect(
                        res_btn_rect_abs.x, res_btn_rect_abs.bottom,
                        res_btn_rect_abs.width, actual_visible_dropdown_height
                    )
                    full_dropdown_area_abs = res_btn_rect_abs.union(dropdown_area_abs)
                    if full_dropdown_area_abs.collidepoint(mouse_pos):
                        is_over_res_dropdown = True
                        scroll_direction = event.y
                        max_scroll_dd = len(self.screen_sizes) - num_visible_dd_items
                        if max_scroll_dd > 0:
                            self.dropdown_scroll_offset -= scroll_direction
                            self.dropdown_scroll_offset = max(0, min(self.dropdown_scroll_offset, max_scroll_dd))
                        if hasattr(self, 'debug_console') and self.debug_console and self.debug_console.debug_settings:
                            print(f"[DEBUG] Resolution Dropdown scroll offset: {self.dropdown_scroll_offset}")
                        continue

                # Display Mode Dropdown Scroll Check (no scroll needed as it's short)
                # but we need to prevent main scroll if mouse is over it.
                is_over_dm_dropdown = False
                if hasattr(self, 'show_display_modes') and self.show_display_modes:
                    dm_btn_y_on_surface = 20 # Initial current_y for display_mode button
                    dm_btn_rect_abs = pygame.Rect(
                        right_column_x - button_width // 2,
                        dm_btn_y_on_surface + self.scroll_y + title_area_height,
                        button_width, 35
                    )
                    dm_dropdown_height = len(self.display_modes) * self.dropdown_item_height
                    dm_dropdown_area_abs = pygame.Rect(
                        dm_btn_rect_abs.x, dm_btn_rect_abs.bottom,
                        dm_btn_rect_abs.width, dm_dropdown_height
                    )
                    full_dm_dropdown_area_abs = dm_btn_rect_abs.union(dm_dropdown_area_abs)
                    if full_dm_dropdown_area_abs.collidepoint(mouse_pos):
                        is_over_dm_dropdown = True
                        continue # Prevent main page scrolling if over display mode dropdown

                # If not scrolling any dropdown, scroll main content
                if not is_over_res_dropdown and not is_over_dm_dropdown:
                    scroll_amount = event.y * 30
                # Adjust max_scroll calculation
                max_scroll = -(total_height - (height - title_area_height - 80)) # Subtract title and button area heights
                self.scroll_y = min(0, max(max_scroll, self.scroll_y + scroll_amount))
                # Only print scroll debug if settings debug is enabled
                if hasattr(self, 'debug_console') and self.debug_console and self.debug_console.debug_settings:
                    print(f"[DEBUG] Scrolling: {self.scroll_y}")

        # Create title area with semi-transparent overlay
        title_area = pygame.Surface((width, title_area_height), pygame.SRCALPHA)
        # Add semi-transparent dark overlay for readability
        pygame.draw.rect(title_area, (0, 0, 0, 120), (0, 0, width, title_area_height))
        # Add subtle gradient effect
        for i in range(title_area_height):
            alpha = int((title_area_height - i) / title_area_height * 60)
            pygame.draw.line(title_area, (25, 0, 51, alpha), (0, i), (width, i))

        # Draw title with glow effect
        title = title_font.render("Settings", True, self.WHITE)
        title_x = width//2 - title.get_width()//2
        title_y = (title_area_height - title.get_height()) // 2
        
        # Draw glow effect for title
        glow_color = (0, 255, 255, 100)  # Cyan glow
        glow_offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for offset_x, offset_y in glow_offsets:
            glow_title = title_font.render("Settings", True, glow_color[:3])
            glow_title.set_alpha(glow_color[3])
            title_area.blit(glow_title, (title_x + offset_x, title_y + offset_y))
        
        # Draw main title
        title_area.blit(title, (title_x, title_y))

        # Adjust content surface start position
        current_y = 20  # Reduced spacing since title is now separate
        button = get_button()

        # --- Draw Content onto content_surface ---
        
        # Calculate mouse_pos_rel once for all scrollable items
        mouse_pos_rel = list(pygame.mouse.get_pos())
        mouse_pos_rel[1] -= (title_area_height + self.scroll_y) # Adjust for title and scroll

        # Display Mode settings section
        self.display_mode_section_height = spacing # Default height
        display_mode_label = font.render("Display Mode:", True, self.WHITE)
        
        # Add text background for readability
        label_rect = display_mode_label.get_rect()
        label_rect.center = (left_column_x, current_y + label_rect.height//2)
        background_rect = label_rect.inflate(20, 8)
        pygame.draw.rect(content_surface, (0, 0, 0, 150), background_rect)
        pygame.draw.rect(content_surface, (0, 255, 255, 100), background_rect, 2)
        
        content_surface.blit(display_mode_label, (left_column_x - display_mode_label.get_width()//2, current_y))
        
        display_mode_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 35)
        is_dm_btn_hovered = display_mode_btn_rect.collidepoint(mouse_pos_rel)
        button.draw(content_surface, display_mode_btn_rect, self.current_display_mode, font, is_hovered=is_dm_btn_hovered)

        # Draw display mode dropdown triangle
        dm_triangle_size = 6
        dm_triangle_margin = 10
        dm_triangle_x = display_mode_btn_rect.right - dm_triangle_margin - dm_triangle_size
        dm_triangle_y = display_mode_btn_rect.centery - dm_triangle_size // 2
        is_dm_open = hasattr(self, 'show_display_modes') and self.show_display_modes
        if is_dm_open:
            dm_triangle_points = [(dm_triangle_x, dm_triangle_y + dm_triangle_size), (dm_triangle_x + dm_triangle_size, dm_triangle_y + dm_triangle_size), (dm_triangle_x + dm_triangle_size // 2, dm_triangle_y)]
        else:
            dm_triangle_points = [(dm_triangle_x, dm_triangle_y), (dm_triangle_x + dm_triangle_size, dm_triangle_y), (dm_triangle_x + dm_triangle_size // 2, dm_triangle_y + dm_triangle_size)]
        pygame.draw.polygon(content_surface, self.WHITE, dm_triangle_points)

        # Handle display mode dropdown drawing
        if hasattr(self, 'show_display_modes') and self.show_display_modes:
            dm_dropdown_height = len(self.display_modes) * self.dropdown_item_height
            self.display_mode_section_height = spacing + dm_dropdown_height
            dm_dropdown_bg = pygame.Rect(display_mode_btn_rect.x, display_mode_btn_rect.bottom, display_mode_btn_rect.width, dm_dropdown_height)
            pygame.draw.rect(content_surface, (30, 30, 50), dm_dropdown_bg)
            pygame.draw.rect(content_surface, (80, 80, 100), dm_dropdown_bg, 1)

            for i, mode_text in enumerate(self.display_modes):
                dm_option_rect = pygame.Rect(display_mode_btn_rect.x, display_mode_btn_rect.bottom + i * self.dropdown_item_height, display_mode_btn_rect.width, self.dropdown_item_height)
                is_dm_option_hovered = dm_option_rect.collidepoint(mouse_pos_rel)
                
                dm_option_inner = pygame.Rect(dm_option_rect.x + 2, dm_option_rect.y + 2, dm_option_rect.width - 4, dm_option_rect.height - 4)
                dm_bg_color = (80, 40, 60) if is_dm_option_hovered else (60, 30, 50)
                pygame.draw.rect(content_surface, dm_bg_color, dm_option_inner)
                pygame.draw.rect(content_surface, (100, 60, 80), dm_option_inner, 1)
                pygame.draw.rect(content_surface, (100, 100, 140), dm_option_rect, 1)

                dm_text_surf = small_font.render(mode_text, True, self.WHITE)
                dm_text_rect = dm_text_surf.get_rect(center=dm_option_inner.center)
                content_surface.blit(dm_text_surf, dm_text_rect)
        else:
            self.display_mode_section_height = spacing
        
        current_y += self.display_mode_section_height


        # Resolution settings section
        self.resolution_section_height = spacing  # Default height
        res_label = font.render("Resolution:", True, self.WHITE)
        
        # Add text background for readability
        label_rect = res_label.get_rect()
        label_rect.center = (left_column_x, current_y + label_rect.height//2)
        background_rect = label_rect.inflate(20, 8)
        pygame.draw.rect(content_surface, (0, 0, 0, 150), background_rect)
        pygame.draw.rect(content_surface, (0, 255, 255, 100), background_rect, 2)
        
        content_surface.blit(res_label, (left_column_x - res_label.get_width()//2, current_y))

        # Current resolution button
        if self.current_display_mode == "Borderless":
            try:
                desktop_info = pygame.display.Info()
                current_res = f"{desktop_info.current_w}x{desktop_info.current_h}"
            except pygame.error:
                # Fallback if display info fails during drawing, though unlikely in settings.
                # save_settings and runtime will still prioritize actual desktop info.
                _w, _h = self.screen_sizes[self.current_size_index]
                current_res = f"{_w}x{_h}"
        else:
            _w, _h = self.screen_sizes[self.current_size_index]
            current_res = f"{_w}x{_h}"
        res_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 35)
        
        # mouse_pos_rel is already calculated above before display mode section
        
        is_res_btn_hovered = res_btn_rect.collidepoint(mouse_pos_rel)

        # Draw the resolution button
        button.draw(content_surface, res_btn_rect, current_res, font, is_hovered=is_res_btn_hovered)

        # Draw dropdown triangle
        triangle_size = 6
        triangle_margin = 10
        triangle_x = res_btn_rect.right - triangle_margin - triangle_size
        triangle_y = res_btn_rect.centery - triangle_size // 2
        is_open = hasattr(self, 'show_resolutions') and self.show_resolutions
        if is_open:
            triangle_points = [(triangle_x, triangle_y + triangle_size), (triangle_x + triangle_size, triangle_y + triangle_size), (triangle_x + triangle_size // 2, triangle_y)]
        else:
            triangle_points = [(triangle_x, triangle_y), (triangle_x + triangle_size, triangle_y), (triangle_x + triangle_size // 2, triangle_y + triangle_size)]
        pygame.draw.polygon(content_surface, self.WHITE, triangle_points)

        # Handle resolution dropdown drawing
        if hasattr(self, 'show_resolutions') and self.show_resolutions:
            num_total_options = len(self.screen_sizes)
            num_visible_options = min(num_total_options, self.dropdown_max_visible_items)
            actual_dropdown_height = num_visible_options * self.dropdown_item_height

            self.resolution_section_height = spacing + actual_dropdown_height # Adjust height dynamically
            dropdown_bg = pygame.Rect(res_btn_rect.x, res_btn_rect.bottom, res_btn_rect.width, actual_dropdown_height)
            pygame.draw.rect(content_surface, (30, 30, 50), dropdown_bg)
            pygame.draw.rect(content_surface, (80, 80, 100), dropdown_bg, 1)

            # Ensure scroll_offset is valid
            max_offset = max(0, num_total_options - num_visible_options)
            self.dropdown_scroll_offset = max(0, min(self.dropdown_scroll_offset, max_offset))

            for i_visible in range(num_visible_options):
                actual_option_index = self.dropdown_scroll_offset + i_visible
                if actual_option_index >= num_total_options:
                    break
                
                w, h = self.screen_sizes[actual_option_index]
                option_rect = pygame.Rect(
                    res_btn_rect.x,
                    res_btn_rect.bottom + i_visible * self.dropdown_item_height,
                    res_btn_rect.width,
                    self.dropdown_item_height
                )
                option_text = f"{w}x{h}"
                is_option_hovered = option_rect.collidepoint(mouse_pos_rel)

                option_inner = pygame.Rect(option_rect.x + 2, option_rect.y + 2, option_rect.width - 4, option_rect.height - 4)
                bg_color = (80, 40, 60) if is_option_hovered else (60, 30, 50)
                pygame.draw.rect(content_surface, bg_color, option_inner)
                pygame.draw.rect(content_surface, (100, 60, 80), option_inner, 1)
                pygame.draw.rect(content_surface, (100, 100, 140), option_rect, 1)

                small_font = get_pixel_font(16)
                text_surf = small_font.render(option_text, True, self.WHITE)
                text_rect = text_surf.get_rect(center=option_inner.center)
                content_surface.blit(text_surf, text_rect)
        else:
             self.resolution_section_height = spacing # Reset height if closed


        # Add spacing based on resolution dropdown state
        current_y += self.resolution_section_height

        # Player name
        name_label = font.render("Player Name:", True, self.WHITE)
        
        # Add text background for readability
        label_rect = name_label.get_rect()
        label_rect.center = (left_column_x, current_y + label_rect.height//2)
        background_rect = label_rect.inflate(20, 8)
        pygame.draw.rect(content_surface, (0, 0, 0, 150), background_rect)
        pygame.draw.rect(content_surface, (0, 255, 255, 100), background_rect, 2)
        
        content_surface.blit(name_label, (left_column_x - name_label.get_width()//2, current_y))
        name_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        button.draw(content_surface, name_btn_rect, self.player_name, font,
                   is_hovered=name_btn_rect.collidepoint(mouse_pos_rel)) # Use relative mouse pos
        current_y += spacing

        # Player B name (2P mode)
        name_b_label = font.render("Player B Name:", True, self.WHITE)
        
        # Add text background for readability
        label_rect = name_b_label.get_rect()
        label_rect.center = (left_column_x, current_y + label_rect.height//2)
        background_rect = label_rect.inflate(20, 8)
        pygame.draw.rect(content_surface, (0, 0, 0, 150), background_rect)
        pygame.draw.rect(content_surface, (0, 255, 255, 100), background_rect, 2)
        
        content_surface.blit(name_b_label, (left_column_x - name_b_label.get_width()//2, current_y))
        name_b_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        button.draw(content_surface, name_b_btn_rect, self.player_b_name, font,
                   is_hovered=name_b_btn_rect.collidepoint(mouse_pos_rel))
        current_y += spacing

        # Draw section separator
        pygame.draw.line(content_surface, self.WHITE, (width//4, current_y), (width * 3//4, current_y), 1)
        current_y += spacing * 0.5

        # Volume controls section header
        volume_text = font.render("Volume Controls", True, self.WHITE)
        
        # Add text background for section header
        header_rect = volume_text.get_rect()
        header_rect.center = (width//2, current_y + header_rect.height//2)
        background_rect = header_rect.inflate(30, 12)
        pygame.draw.rect(content_surface, (0, 0, 0, 180), background_rect)
        pygame.draw.rect(content_surface, (255, 20, 147, 120), background_rect, 3)  # Hot pink border
        
        content_surface.blit(volume_text, (width//2 - volume_text.get_width()//2, current_y))
        current_y += spacing * 1.5

        # Add extra spacing after section headers
        current_y += spacing * 0.5

        # Master volume with +/- buttons
        master_label = small_font.render("Master Volume:", True, self.WHITE)
        
        # Add text background for readability
        label_rect = master_label.get_rect()
        label_rect.center = (left_column_x, current_y + label_rect.height//2)
        background_rect = label_rect.inflate(16, 6)
        pygame.draw.rect(content_surface, (0, 0, 0, 130), background_rect)
        pygame.draw.rect(content_surface, (0, 200, 0, 80), background_rect, 1)  # Green border
        
        content_surface.blit(master_label, (left_column_x - master_label.get_width()//2, current_y))
        vol_btn_width = button_width // 4
        display_width = vol_btn_width * 2
        padding = 5
        minus_x = right_column_x - (vol_btn_width + display_width + vol_btn_width + padding * 2) // 2
        display_x = minus_x + vol_btn_width + padding
        plus_x = display_x + display_width + padding
        master_vol_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        master_vol_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        master_vol_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        master_minus_hover = master_vol_minus_rect.collidepoint(mouse_pos_rel)
        master_plus_hover = master_vol_plus_rect.collidepoint(mouse_pos_rel)
        button.draw(content_surface, master_vol_minus_rect, "-", font, is_hovered=master_minus_hover)
        button.draw(content_surface, master_vol_display_rect, f"{self.master_volume}%", font, is_hovered=False)
        button.draw(content_surface, master_vol_plus_rect, "+", font, is_hovered=master_plus_hover)
        current_y += spacing

        # Effects volume with +/- buttons
        effects_label = small_font.render("Effects Volume:", True, self.WHITE)
        
        # Add text background for readability
        label_rect = effects_label.get_rect()
        label_rect.center = (left_column_x, current_y + label_rect.height//2)
        background_rect = label_rect.inflate(16, 6)
        pygame.draw.rect(content_surface, (0, 0, 0, 130), background_rect)
        pygame.draw.rect(content_surface, (0, 200, 0, 80), background_rect, 1)  # Green border
        
        content_surface.blit(effects_label, (left_column_x - effects_label.get_width()//2, current_y))
        effects_vol_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        effects_vol_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        effects_vol_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        effects_minus_hover = effects_vol_minus_rect.collidepoint(mouse_pos_rel)
        effects_plus_hover = effects_vol_plus_rect.collidepoint(mouse_pos_rel)
        button.draw(content_surface, effects_vol_minus_rect, "-", font, is_hovered=effects_minus_hover)
        button.draw(content_surface, effects_vol_display_rect, f"{self.effects_volume}%", font, is_hovered=False)
        button.draw(content_surface, effects_vol_plus_rect, "+", font, is_hovered=effects_plus_hover)
        current_y += spacing * 0.8

        # Music volume with +/- buttons
        music_label = small_font.render("Music Volume:", True, self.WHITE)
        
        # Add text background for readability
        label_rect = music_label.get_rect()
        label_rect.center = (left_column_x, current_y + label_rect.height//2)
        background_rect = label_rect.inflate(16, 6)
        pygame.draw.rect(content_surface, (0, 0, 0, 130), background_rect)
        pygame.draw.rect(content_surface, (0, 200, 0, 80), background_rect, 1)  # Green border
        
        content_surface.blit(music_label, (left_column_x - music_label.get_width()//2, current_y))
        music_vol_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        music_vol_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        music_vol_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        music_minus_hover = music_vol_minus_rect.collidepoint(mouse_pos_rel)
        music_plus_hover = music_vol_plus_rect.collidepoint(mouse_pos_rel)
        button.draw(content_surface, music_vol_minus_rect, "-", font, is_hovered=music_minus_hover)
        button.draw(content_surface, music_vol_display_rect, f"{self.music_volume}%", font, is_hovered=False)
        button.draw(content_surface, music_vol_plus_rect, "+", font, is_hovered=music_plus_hover)
        current_y += spacing * 1.2

        # Score effect intensity with +/- buttons
        score_effect_label = small_font.render("Score Effect Intensity:", True, self.WHITE)
        
        # Add text background for readability
        label_rect = score_effect_label.get_rect()
        label_rect.center = (left_column_x, current_y + label_rect.height//2)
        background_rect = label_rect.inflate(16, 6)
        pygame.draw.rect(content_surface, (0, 0, 0, 130), background_rect)
        pygame.draw.rect(content_surface, (0, 200, 0, 80), background_rect, 1)  # Green border
        
        content_surface.blit(score_effect_label, (left_column_x - score_effect_label.get_width()//2, current_y))
        score_effect_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        score_effect_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        score_effect_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        score_effect_minus_hover = score_effect_minus_rect.collidepoint(mouse_pos_rel)
        score_effect_plus_hover = score_effect_plus_rect.collidepoint(mouse_pos_rel)
        button.draw(content_surface, score_effect_minus_rect, "-", font, is_hovered=score_effect_minus_hover)
        button.draw(content_surface, score_effect_display_rect, f"{self.score_effect_intensity}%", font, is_hovered=False)
        button.draw(content_surface, score_effect_plus_rect, "+", font, is_hovered=score_effect_plus_hover)
        current_y += spacing

        # Draw section separator for UI Effects
        pygame.draw.line(content_surface, self.WHITE, (width//4, current_y), (width * 3//4, current_y), 1)
        current_y += spacing * 0.5

        # UI effects settings section header
        effects_text = font.render("Additional UI Effects", True, self.WHITE)
        
        # Add text background for section header
        header_rect = effects_text.get_rect()
        header_rect.center = (width//2, current_y + header_rect.height//2)
        background_rect = header_rect.inflate(30, 12)
        pygame.draw.rect(content_surface, (0, 0, 0, 180), background_rect)
        pygame.draw.rect(content_surface, (0, 255, 0, 120), background_rect, 3)  # Lime green border
        
        content_surface.blit(effects_text, (width//2 - effects_text.get_width()//2, current_y))
        current_y += spacing * 1.5

        # Draw preview box right after the section header
        preview_width = min(300, int(width * 0.4))
        preview_height = 100
        preview_x = width//2 - preview_width // 2
        preview_rect = pygame.Rect(preview_x, current_y, preview_width, preview_height)
        preview_surf = pygame.Surface((preview_width + 20, preview_height + 20), pygame.SRCALPHA)
        inner_rect = pygame.Rect(10, 10, preview_width, preview_height)
        pygame.draw.rect(preview_surf, (0, 0, 60), inner_rect)
        pygame.draw.rect(preview_surf, self.WHITE, inner_rect, 2)
        preview_text = font.render("PREVIEW", True, self.WHITE)
        preview_score = font.render("88", True, self.WHITE)
        if self.retro_effects_enabled:
            scanline_surface = pygame.Surface((preview_width, preview_height), pygame.SRCALPHA)
            for y in range(0, preview_height, 4):
                alpha = self.scanline_intensity
                pygame.draw.line(scanline_surface, (0, 0, 0, alpha), (0, y), (preview_width, y))
            preview_surf.blit(scanline_surface, (10, 10))
            glow_alpha = int(self.glow_intensity * 2.55)
            glow_color = tuple(map(int, self.score_glow_color.split(','))) + (glow_alpha,)
            pygame.draw.rect(preview_surf, glow_color, preview_surf.get_rect(), border_radius=10)
        preview_surf.blit(preview_text, (10 + (preview_width - preview_text.get_width()) // 2, 30))
        preview_surf.blit(preview_score, (10 + (preview_width - preview_score.get_width()) // 2, 70))
        content_surface.blit(preview_surf, (preview_x - 10, current_y - 10))
        current_y += preview_height + spacing * 1.5

        # UI effects enabled toggle
        effects_label = small_font.render("Enable Additional UI Effects:", True, self.WHITE)
        
        # Add text background for readability
        label_rect = effects_label.get_rect()
        label_rect.center = (left_column_x, current_y + label_rect.height//2)
        background_rect = label_rect.inflate(16, 6)
        pygame.draw.rect(content_surface, (0, 0, 0, 130), background_rect)
        pygame.draw.rect(content_surface, (0, 255, 255, 80), background_rect, 1)  # Cyan border
        
        content_surface.blit(effects_label, (left_column_x - effects_label.get_width()//2, current_y))
        effects_btn_rect = pygame.Rect(right_column_x - button_width//2, current_y, button_width, 30)
        button.draw(content_surface, effects_btn_rect, "On" if self.retro_effects_enabled else "Off", font,
                   is_hovered=effects_btn_rect.collidepoint(mouse_pos_rel))
        current_y += spacing

        # Create rectangles for intensity controls
        scanline_minus_rect = pygame.Rect(minus_x, current_y, vol_btn_width, 30)
        scanline_display_rect = pygame.Rect(display_x, current_y, display_width, 30)
        scanline_plus_rect = pygame.Rect(plus_x, current_y, vol_btn_width, 30)
        glow_minus_rect = pygame.Rect(minus_x, current_y + spacing * 0.8, vol_btn_width, 30)
        glow_display_rect = pygame.Rect(display_x, current_y + spacing * 0.8, display_width, 30)
        glow_plus_rect = pygame.Rect(plus_x, current_y + spacing * 0.8, vol_btn_width, 30)

        if self.retro_effects_enabled:
            # Scanline intensity
            scanline_label = small_font.render("Scanline Intensity:", True, self.WHITE)
            
            # Add text background for readability
            label_rect = scanline_label.get_rect()
            label_rect.center = (left_column_x, current_y + label_rect.height//2)
            background_rect = label_rect.inflate(16, 6)
            pygame.draw.rect(content_surface, (0, 0, 0, 130), background_rect)
            pygame.draw.rect(content_surface, (255, 20, 147, 80), background_rect, 1)  # Hot pink border
            
            content_surface.blit(scanline_label, (left_column_x - scanline_label.get_width()//2, current_y))
            scanline_minus_hover = scanline_minus_rect.collidepoint(mouse_pos_rel)
            scanline_plus_hover = scanline_plus_rect.collidepoint(mouse_pos_rel)
            button.draw(content_surface, scanline_minus_rect, "-", font, is_hovered=scanline_minus_hover)
            button.draw(content_surface, scanline_display_rect, f"{self.scanline_intensity}%", font, is_hovered=False)
            button.draw(content_surface, scanline_plus_rect, "+", font, is_hovered=scanline_plus_hover)
            current_y += spacing * 0.8

            # Glow intensity
            glow_label = small_font.render("Glow Intensity:", True, self.WHITE)
            
            # Add text background for readability
            label_rect = glow_label.get_rect()
            label_rect.center = (left_column_x, current_y + label_rect.height//2)
            background_rect = label_rect.inflate(16, 6)
            pygame.draw.rect(content_surface, (0, 0, 0, 130), background_rect)
            pygame.draw.rect(content_surface, (255, 20, 147, 80), background_rect, 1)  # Hot pink border
            
            content_surface.blit(glow_label, (left_column_x - glow_label.get_width()//2, current_y))
            glow_minus_hover = glow_minus_rect.collidepoint(mouse_pos_rel)
            glow_plus_hover = glow_plus_rect.collidepoint(mouse_pos_rel)
            button.draw(content_surface, glow_minus_rect, "-", font, is_hovered=glow_minus_hover)
            button.draw(content_surface, glow_display_rect, f"{self.glow_intensity}%", font, is_hovered=False)
            button.draw(content_surface, glow_plus_rect, "+", font, is_hovered=glow_plus_hover)
            current_y += spacing * 1.2

        # Draw section separator before hints
        pygame.draw.line(content_surface, self.WHITE, (width//4, current_y), (width * 3//4, current_y), 1)
        current_y += spacing * 0.5

        # Draw control hints
        hint_color = (180, 180, 180)
        controls = [
            "Controls:", "R - Toggle Retro Effects", "← → - Adjust Scanline Intensity",
            "Shift + ← → - Adjust Glow Intensity", "Ctrl + ← → - Adjust Master Volume",
            "Alt + ← → - Adjust Effects Volume", "M/Shift+M - Decrease/Increase Music Volume",
            "Ctrl+Shift + ← → - Adjust Score Effect", "Mouse Wheel - Scroll Settings"
        ]
        hints_y = current_y
        hints_height = len(controls) * spacing * 0.7 + spacing * 0.8
        hints_surface = pygame.Surface((width, hints_height), pygame.SRCALPHA)
        
        # Add background for hints area
        pygame.draw.rect(hints_surface, (0, 0, 0, 100), (0, 0, width, hints_height))
        pygame.draw.rect(hints_surface, (128, 128, 128, 80), (0, 0, width, hints_height), 2)
        
        hint_y = 10
        for i, hint in enumerate(controls):
            hint_text = small_font.render(hint, True, hint_color)
            
            # Add individual text backgrounds for better readability
            if i == 0:  # "Controls:" header
                text_rect = hint_text.get_rect()
                text_rect.center = (width//2, hint_y + text_rect.height//2)
                background_rect = text_rect.inflate(20, 4)
                pygame.draw.rect(hints_surface, (0, 0, 0, 150), background_rect)
                pygame.draw.rect(hints_surface, (255, 255, 255, 120), background_rect, 1)
            
            hints_surface.blit(hint_text, (width//2 - hint_text.get_width()//2, hint_y))
            hint_y += spacing * 0.7
        content_surface.blit(hints_surface, (0, hints_y))
        current_y = hints_y + hints_height + spacing * 0.8

        # --- Blit Content onto Screen ---
        # Draw scrollable content with offset for title area
        visible_rect = pygame.Rect(0, -self.scroll_y, width, height - title_area_height - 80) # Subtract button area height
        screen.blit(content_surface, (0, title_area_height), visible_rect)

        # Draw title area (fixed)
        screen.blit(title_area, (0, 0))

        # Reset scroll when content is shorter than window
        if total_height <= height - title_area_height - 80: # Adjust check for button area
            self.scroll_y = 0

        # --- Draw Fixed Bottom Button Area ---
        button_area_height = 80
        button_area_surface = pygame.Surface((width, button_area_height), pygame.SRCALPHA)
        # Add semi-transparent dark overlay for readability
        pygame.draw.rect(button_area_surface, (0, 0, 0, 120), (0, 0, width, button_area_height))
        # Add subtle gradient effect (inverted from title)
        for i in range(button_area_height):
            alpha = int(i / button_area_height * 60)
            pygame.draw.line(button_area_surface, (25, 0, 51, alpha), (0, i), (width, i))
        screen.blit(button_area_surface, (0, height - button_area_height))

        # Draw buttons over the brick pattern (fixed position)
        button_y = height - 60
        save_btn_rect = pygame.Rect(width//2 - 150, button_y, 100, 40)
        back_btn_rect = pygame.Rect(width//2 + 50, button_y, 100, 40)
        mouse_pos_abs = pygame.mouse.get_pos() # Use absolute mouse pos for fixed buttons
        button.draw(screen, save_btn_rect, "Save", font, is_hovered=save_btn_rect.collidepoint(mouse_pos_abs))
        button.draw(screen, back_btn_rect, "Back", font, is_hovered=back_btn_rect.collidepoint(mouse_pos_abs))

        # --- Handle Events ---
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos_abs = event.pos # Use event position for clicks

                # Check fixed buttons first
                if save_btn_rect.collidepoint(mouse_pos_abs):
                    success = self.save_settings()
                    if success:
                        print("Settings saved successfully")
                        if sound_manager:
                            sound_manager._load_volume_settings()

                        newly_saved_width, newly_saved_height = self.screen_sizes[self.current_size_index]
                        newly_saved_mode = self.current_display_mode

                        resolution_changed = self.current_size_index != self.original_loaded_size_index
                        mode_changed = newly_saved_mode != self.original_loaded_display_mode
                        
                        self._display_settings_changed_on_save = resolution_changed or mode_changed

                        if self._display_settings_changed_on_save:
                            # Update original loaded values to reflect the save for subsequent comparisons
                            self.original_loaded_display_mode = newly_saved_mode
                            self.original_loaded_size_index = self.current_size_index
                            if hasattr(self, 'debug_console') and self.debug_console and self.debug_console.debug_settings:
                                print(f"[DEBUG] Display settings changed and saved. Mode: {newly_saved_mode}, Res: {newly_saved_width}x{newly_saved_height}")
                            if back_fn: return back_fn() # Trigger display update via main loop
                        # No display-related changes, continue in settings
                    else:
                        print("Error saving settings")
                    continue # Prevent further click processing

                elif back_btn_rect.collidepoint(mouse_pos_abs) and back_fn:
                    # Before returning, check if name changed
                    # Use the class method to get the currently saved name
                    if self.player_name != SettingsScreen.get_player_name():
                        self._name_changed = True # Set flag
                    return back_fn() # Use the provided back function
                    continue # Prevent further click processing

                # --- Handle clicks on scrollable content ---
                mouse_pos_rel = list(mouse_pos_abs)
                mouse_pos_rel[1] -= (title_area_height + self.scroll_y) # Adjust for title and scroll

                # Check resolution dropdown button/options OR Display Mode dropdown
                res_dropdown_handled = False
                if hasattr(self, 'show_resolutions') and self.show_resolutions:
                    num_total_res_options = len(self.screen_sizes)
                    num_visible_res_options_drawn = min(num_total_res_options, self.dropdown_max_visible_items)
                    actual_res_dropdown_height_drawn = num_visible_res_options_drawn * self.dropdown_item_height

                    for i_visible in range(num_visible_res_options_drawn):
                        actual_option_index = self.dropdown_scroll_offset + i_visible
                        if actual_option_index >= num_total_res_options: break
                        option_rect = pygame.Rect(res_btn_rect.x, res_btn_rect.bottom + i_visible * self.dropdown_item_height, res_btn_rect.width, self.dropdown_item_height)
                        if option_rect.collidepoint(mouse_pos_rel):
                            self.current_size_index = actual_option_index
                            self.show_resolutions = False
                            self.dropdown_scroll_offset = 0
                            if hasattr(self, 'debug_console') and self.debug_console and self.debug_console.debug_settings: print(f"[DEBUG] Selected resolution index: {actual_option_index}")
                            res_dropdown_handled = True
                            break
                    dropdown_bg_rect_drawn = pygame.Rect(res_btn_rect.x, res_btn_rect.bottom, res_btn_rect.width, actual_res_dropdown_height_drawn)
                    if not res_dropdown_handled and dropdown_bg_rect_drawn.collidepoint(mouse_pos_rel):
                         self.show_resolutions = False
                         self.dropdown_scroll_offset = 0
                         res_dropdown_handled = True
                
                dm_dropdown_handled = False
                if hasattr(self, 'show_display_modes') and self.show_display_modes:
                    dm_dropdown_height = len(self.display_modes) * self.dropdown_item_height
                    for i, mode_text in enumerate(self.display_modes):
                        dm_option_rect = pygame.Rect(display_mode_btn_rect.x, display_mode_btn_rect.bottom + i * self.dropdown_item_height, display_mode_btn_rect.width, self.dropdown_item_height)
                        if dm_option_rect.collidepoint(mouse_pos_rel):
                            self.current_display_mode = mode_text
                            self.show_display_modes = False
                            if hasattr(self, 'debug_console') and self.debug_console and self.debug_console.debug_settings: print(f"[DEBUG] Selected display mode: {mode_text}")
                            dm_dropdown_handled = True
                            break
                    dm_dropdown_bg_rect = pygame.Rect(display_mode_btn_rect.x, display_mode_btn_rect.bottom, display_mode_btn_rect.width, dm_dropdown_height)
                    if not dm_dropdown_handled and dm_dropdown_bg_rect.collidepoint(mouse_pos_rel):
                        self.show_display_modes = False
                        dm_dropdown_handled = True
                
                # If no dropdown handled the click, check other buttons
                if not res_dropdown_handled and not dm_dropdown_handled:
                    if display_mode_btn_rect.collidepoint(mouse_pos_rel):
                        self.show_display_modes = not getattr(self, 'show_display_modes', False)
                        if self.show_display_modes: self.show_resolutions = False # Close other dropdown
                    elif res_btn_rect.collidepoint(mouse_pos_rel):
                        self.show_resolutions = not getattr(self, 'show_resolutions', False)
                        if self.show_resolutions: self.show_display_modes = False # Close other dropdown
                        if not self.show_resolutions: self.dropdown_scroll_offset = 0
                    elif name_btn_rect.collidepoint(mouse_pos_rel):
                        from ..Ping_UI import player_name_screen # Local import
                        # Pass debug console if available
                        new_name = player_name_screen(screen, pygame.time.Clock(), width, height, self.debug_console)
                        if new_name:
                            self.player_name = new_name
                    elif name_b_btn_rect.collidepoint(mouse_pos_rel):
                        from ..Ping_UI import player_name_screen
                        new_name = player_name_screen(screen, pygame.time.Clock(), width, height, self.debug_console)
                        if new_name:
                            self.player_b_name = new_name
                    elif master_vol_minus_rect.collidepoint(mouse_pos_rel):
                        self.master_volume = max(0, self.master_volume - 5)
                        if sound_manager: sound_manager.set_master_volume(self.master_volume)
                    elif master_vol_plus_rect.collidepoint(mouse_pos_rel):
                        self.master_volume = min(100, self.master_volume + 5)
                        if sound_manager: sound_manager.set_master_volume(self.master_volume)
                    elif effects_vol_minus_rect.collidepoint(mouse_pos_rel):
                        self.effects_volume = max(0, self.effects_volume - 5)
                        if sound_manager:
                            sound_manager.set_sfx_volume(self.effects_volume) # Corrected method name
                            sound_manager.play_sfx('paddle') # Play preview
                    elif effects_vol_plus_rect.collidepoint(mouse_pos_rel):
                        self.effects_volume = min(100, self.effects_volume + 5)
                        if sound_manager:
                            sound_manager.set_sfx_volume(self.effects_volume) # Corrected method name
                            sound_manager.play_sfx('paddle') # Play preview
                    elif music_vol_minus_rect.collidepoint(mouse_pos_rel):
                        self.music_volume = max(0, self.music_volume - 5)
                        if sound_manager: sound_manager.set_music_volume(self.music_volume)
                    elif music_vol_plus_rect.collidepoint(mouse_pos_rel):
                        self.music_volume = min(100, self.music_volume + 5)
                        if sound_manager: sound_manager.set_music_volume(self.music_volume)
                    elif score_effect_minus_rect.collidepoint(mouse_pos_rel):
                        self.score_effect_intensity = max(0, self.score_effect_intensity - 5)
                    elif score_effect_plus_rect.collidepoint(mouse_pos_rel):
                        self.score_effect_intensity = min(100, self.score_effect_intensity + 5)
                    elif effects_btn_rect.collidepoint(mouse_pos_rel):
                        self.retro_effects_enabled = not self.retro_effects_enabled
                    # Intensity controls only clickable if effects enabled
                    elif self.retro_effects_enabled:
                        if scanline_minus_rect.collidepoint(mouse_pos_rel):
                            self.scanline_intensity = max(0, self.scanline_intensity - 5)
                        elif scanline_plus_rect.collidepoint(mouse_pos_rel):
                            self.scanline_intensity = min(100, self.scanline_intensity + 5)
                        elif glow_minus_rect.collidepoint(mouse_pos_rel):
                            self.glow_intensity = max(0, self.glow_intensity - 5)
                        elif glow_plus_rect.collidepoint(mouse_pos_rel):
                            self.glow_intensity = min(100, self.glow_intensity + 5)
                    else: # Clicked outside any interactive element on the scrollable surface
                         # Close any open dropdown if click was outside them
                         clicked_outside_all_buttons = True # Assume true initially
                         # Check if click was on any button (add all relevant rects here)
                         # For simplicity, just closing dropdowns if no button was hit by this point.
                         
                         if self.show_resolutions:
                            self.show_resolutions = False
                            self.dropdown_scroll_offset = 0
                         if self.show_display_modes:
                            self.show_display_modes = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and back_fn:
                    # Check for name change before returning via escape
                    if self.player_name != SettingsScreen.get_player_name():
                        self._name_changed = True
                    return back_fn()
                elif event.key == pygame.K_r:
                    self.retro_effects_enabled = not self.retro_effects_enabled
                elif event.key == pygame.K_LEFT:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT: self.score_effect_intensity = max(0, self.score_effect_intensity - 5)
                    elif mods & pygame.KMOD_CTRL:
                        self.master_volume = max(0, self.master_volume - 5)
                        if sound_manager: sound_manager.set_master_volume(self.master_volume)
                    elif mods & pygame.KMOD_ALT:
                        self.effects_volume = max(0, self.effects_volume - 5)
                        if sound_manager:
                            sound_manager.set_sfx_volume(self.effects_volume) # Corrected method name
                            sound_manager.play_sfx('paddle') # Play preview
                    elif mods & pygame.KMOD_SHIFT: self.glow_intensity = max(0, self.glow_intensity - 5)
                    else: self.scanline_intensity = max(0, self.scanline_intensity - 5)
                elif event.key == pygame.K_RIGHT:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT: self.score_effect_intensity = min(100, self.score_effect_intensity + 5)
                    elif mods & pygame.KMOD_CTRL:
                        self.master_volume = min(100, self.master_volume + 5)
                        if sound_manager: sound_manager.set_master_volume(self.master_volume)
                    elif mods & pygame.KMOD_ALT:
                        self.effects_volume = min(100, self.effects_volume + 5)
                        if sound_manager:
                            sound_manager.set_sfx_volume(self.effects_volume) # Corrected method name
                            sound_manager.play_sfx('paddle') # Play preview
                    elif mods & pygame.KMOD_SHIFT: self.glow_intensity = min(100, self.glow_intensity + 5)
                    else: self.scanline_intensity = min(100, self.scanline_intensity + 5)
                elif event.key == pygame.K_m:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.music_volume = min(100, self.music_volume + 5)
                        if sound_manager: sound_manager.set_music_volume(self.music_volume)
                    else:
                        self.music_volume = max(0, self.music_volume - 5)
                        if sound_manager: sound_manager.set_music_volume(self.music_volume)

        return None # Continue showing settings screen