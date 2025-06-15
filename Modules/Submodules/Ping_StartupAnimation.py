\
import pygame
import time
import math
import sys
import random
from .Ping_Fonts import get_pixel_font
from .Ping_Sound import SoundManager

# Ultra-Creative Animation Constants
BACKGROUND_COLOR = (0, 5, 15)  # Deep ocean blue-black
OCEAN_COLORS = {
    'deep': (0, 20, 40),
    'mid': (0, 40, 80), 
    'surface': (0, 80, 120),
    'light': (40, 120, 160)
}

# Retro Submarine Colors - Classic 1960s submarine aesthetic
SUB_COLORS = {
    'hull_main': (70, 90, 110),        # Steel blue-grey
    'hull_dark': (45, 60, 75),         # Dark steel
    'hull_light': (95, 115, 135),      # Light steel highlight
    'detail': (30, 40, 50),            # Dark detailing
    'window': (60, 120, 180),          # Deep blue windows
    'window_glow': (120, 200, 255),    # Bright window glow
    'light_red': (255, 80, 80),        # Navigation lights
    'light_green': (80, 255, 80),      # Starboard lights
    'light_white': (255, 255, 220),    # Search lights
    'exhaust': (180, 120, 60),         # Engine exhaust
    'propeller': (90, 90, 100),        # Metallic propeller
    'rust': (140, 80, 50),             # Weathered rust
    'brass': (180, 140, 80),           # Brass fittings
    'rivets': (50, 50, 60),            # Rivet details
    'periscope': (60, 60, 70),         # Periscope metal
    'antenna': (100, 100, 110)         # Antenna/radar
}

# Sonar System Colors
SONAR_COLORS = {
    'primary': (0, 255, 150),
    'secondary': (0, 200, 255),
    'echo': (255, 150, 0),
    'interference': (255, 50, 50),
    'harmonic': (150, 0, 255)
}

# Text Effects Colors
TEXT_COLORS = {
    'hologram': (0, 255, 200),
    'glow': (100, 255, 255),
    'core': (255, 255, 255),
    'shadow': (0, 50, 100)
}

# Animation Timing (synchronized with 4-second PIntroMusicTemp.wav)
TOTAL_ANIMATION_DURATION = 4.0  # Matches audio file exactly
SUB_APPEAR_DURATION = 0.3       # Quick submarine appearance
SONAR_BLAST_DURATION = 1.5      # Immediate ping - main effect
TEXT_EMERGE_DURATION = 1.2      # Text emerges from sonar waves
TEXT_HOLD_DURATION = 1.0        # Final dramatic display

# Physics Constants
WATER_DENSITY = 0.8
BUBBLE_RISE_SPEED = 30
DEBRIS_FALL_SPEED = 15
LIGHT_RAY_SPEED = 200

class UltraSubmarine:
    """Ultra-detailed animated submarine with realistic components."""
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bob_phase = 0
        self.propeller_rotation = 0
        self.light_pulse = 0
        self.bubble_timer = 0
        self.engine_heat = 0
        
    def update(self, delta_time, animation_phase):
        """Update submarine animations."""
        self.bob_phase += delta_time * 2
        self.propeller_rotation += delta_time * 15  # Fast rotation
        self.light_pulse += delta_time * 4
        self.bubble_timer += delta_time
        
        # Engine heat based on animation phase
        if animation_phase in ['sonar_charge', 'sonar_blast']:
            self.engine_heat = min(1.0, self.engine_heat + delta_time * 2)
        else:
            self.engine_heat = max(0.0, self.engine_heat - delta_time * 0.5)
    
    def draw(self, screen, particles):
        """Draw ultra-detailed retro submarine with classic 1960s aesthetics."""
        # Calculate bobbing offset
        bob_offset = math.sin(self.bob_phase) * 3
        current_y = self.y + bob_offset
        
        # Main hull with classic submarine shape (more elongated)
        hull_rect = pygame.Rect(self.x - self.width // 2, current_y - self.height // 2, 
                               self.width, self.height)
        
        # Draw main hull with retro gradient shading
        for i in range(self.height):
            if i < self.height // 3:
                shade_color = SUB_COLORS['hull_light']
            elif i < 2 * self.height // 3:
                shade_color = SUB_COLORS['hull_main']
            else:
                shade_color = SUB_COLORS['hull_dark']
            pygame.draw.rect(screen, shade_color, 
                           (hull_rect.x, hull_rect.y + i, hull_rect.width, 1))
        
        # Hull outline with heavy retro detailing
        pygame.draw.rect(screen, SUB_COLORS['detail'], hull_rect, 3)
        
        # Add rivets along the hull (classic submarine detail)
        rivet_spacing = 8
        for x in range(hull_rect.left + rivet_spacing, hull_rect.right, rivet_spacing):
            for y in range(hull_rect.top + 4, hull_rect.bottom - 4, rivet_spacing):
                pygame.draw.circle(screen, SUB_COLORS['rivets'], (x, y), 1)
        
        # Conning tower - more angular and retro
        tower_width = self.width * 0.35
        tower_height = self.height * 0.9
        tower_rect = pygame.Rect(self.x - tower_width // 2, 
                                current_y - self.height // 2 - tower_height + 5,
                                tower_width, tower_height)
        
        # Draw tower with stepped design
        pygame.draw.rect(screen, SUB_COLORS['hull_main'], tower_rect)
        pygame.draw.rect(screen, SUB_COLORS['detail'], tower_rect, 3)
        
        # Add tower rivets
        for y in range(tower_rect.top + 3, tower_rect.bottom - 3, 6):
            pygame.draw.circle(screen, SUB_COLORS['rivets'], (tower_rect.left + 3, y), 1)
            pygame.draw.circle(screen, SUB_COLORS['rivets'], (tower_rect.right - 3, y), 1)
        
        # Classic periscope array (more detailed)
        periscope_data = [
            {'x_offset': -10, 'height': 20, 'color': SUB_COLORS['periscope'], 'width': 3},
            {'x_offset': -3, 'height': 25, 'color': SUB_COLORS['antenna'], 'width': 2},
            {'x_offset': 4, 'height': 18, 'color': SUB_COLORS['periscope'], 'width': 2},
            {'x_offset': 10, 'height': 22, 'color': SUB_COLORS['antenna'], 'width': 2}
        ]
        
        for scope in periscope_data:
            scope_x = self.x + scope['x_offset']
            scope_top = tower_rect.top - scope['height']
            # Main periscope shaft
            pygame.draw.rect(screen, scope['color'], 
                           (scope_x, scope_top, scope['width'], scope['height']))
            # Periscope head
            pygame.draw.rect(screen, SUB_COLORS['brass'], 
                           (scope_x - 1, scope_top - 3, scope['width'] + 2, 3))
            # Blinking navigation light
            if scope['x_offset'] in [-10, 10]:  # Main periscopes get lights
                light_intensity = 0.5 + 0.5 * math.sin(self.light_pulse + scope['x_offset'])
                light_color = SUB_COLORS['light_red'] if scope['x_offset'] < 0 else SUB_COLORS['light_green']
                light_color = tuple(int(c * light_intensity) for c in light_color)
                pygame.draw.circle(screen, light_color, 
                                 (scope_x + scope['width']//2, scope_top - 1), 2)
        
        # Classic submarine portholes (more detailed and retro)
        porthole_positions = [
            {'x_mult': 0.35, 'y_offset': -2, 'size': 8},
            {'x_mult': 0.1, 'y_offset': 2, 'size': 6}, 
            {'x_mult': -0.15, 'y_offset': -1, 'size': 7},
            {'x_mult': -0.35, 'y_offset': 1, 'size': 5}
        ]
        
        for i, port in enumerate(porthole_positions):
            window_x = self.x + int(self.width * port['x_mult'])
            window_y = current_y + port['y_offset']
            window_size = port['size']
            
            # Outer brass ring
            pygame.draw.circle(screen, SUB_COLORS['brass'], 
                             (window_x, window_y), window_size + 2, 2)
            # Inner window with glow
            glow_intensity = 0.7 + 0.3 * math.sin(self.light_pulse + i * 0.7)
            window_color = tuple(int(c * glow_intensity) for c in SUB_COLORS['window'])
            pygame.draw.circle(screen, window_color, (window_x, window_y), window_size)
            # Interior glow
            glow_color = tuple(int(c * glow_intensity * 0.8) for c in SUB_COLORS['window_glow'])
            pygame.draw.circle(screen, glow_color, (window_x, window_y), window_size - 2)
            # Window reflection
            pygame.draw.circle(screen, SUB_COLORS['light_white'], 
                             (window_x - 2, window_y - 2), max(1, window_size // 3))
        
        # Retro propeller system with more detail
        prop_center_x = self.x - self.width // 2 - 10
        prop_center_y = current_y
        
        # Propeller shroud/guard
        shroud_rect = pygame.Rect(prop_center_x - 15, prop_center_y - 12, 30, 24)
        pygame.draw.ellipse(screen, SUB_COLORS['hull_dark'], shroud_rect, 2)
        
        # Spinning propeller blades
        for blade in range(3):  # 3-blade propeller more retro
            angle = self.propeller_rotation + (blade * 2 * math.pi / 3)
            blade_length = 10
            
            # Main blade
            end_x = prop_center_x + math.cos(angle) * blade_length
            end_y = prop_center_y + math.sin(angle) * blade_length
            pygame.draw.line(screen, SUB_COLORS['propeller'], 
                           (prop_center_x, prop_center_y), (end_x, end_y), 4)
            
            # Blade tip detail
            pygame.draw.circle(screen, SUB_COLORS['brass'], (int(end_x), int(end_y)), 2)
        
        # Propeller hub with retro detailing
        pygame.draw.circle(screen, SUB_COLORS['brass'], (prop_center_x, prop_center_y), 6)
        pygame.draw.circle(screen, SUB_COLORS['detail'], (prop_center_x, prop_center_y), 6, 2)
        pygame.draw.circle(screen, SUB_COLORS['rivets'], (prop_center_x, prop_center_y), 3)
        
        # Classic submarine fins/rudders
        # Dorsal fin
        fin_points = [
            (self.x - self.width//3, current_y - self.height//2),
            (self.x - self.width//4, current_y - self.height//2 - 8),
            (self.x + self.width//4, current_y - self.height//2 - 4),
            (self.x + self.width//3, current_y - self.height//2)
        ]
        pygame.draw.polygon(screen, SUB_COLORS['hull_main'], fin_points)
        pygame.draw.polygon(screen, SUB_COLORS['detail'], fin_points, 2)
        
        # Side control surfaces
        for side in [-1, 1]:
            control_y = current_y + side * (self.height//2 + 3)
            control_points = [
                (self.x - self.width//4, control_y),
                (self.x - self.width//6, control_y + side * 5),
                (self.x + self.width//6, control_y + side * 3),
                (self.x + self.width//4, control_y)
            ]
            pygame.draw.polygon(screen, SUB_COLORS['hull_dark'], control_points)
            pygame.draw.polygon(screen, SUB_COLORS['detail'], control_points, 1)
        
        # Engine exhaust with retro heat effect
        if self.engine_heat > 0.1:
            for _ in range(int(self.engine_heat * 8)):
                exhaust_x = prop_center_x - random.randint(8, 20)
                exhaust_y = prop_center_y + random.randint(-4, 4)
                heat_color = tuple(int(c * (0.6 + 0.4 * self.engine_heat)) 
                                 for c in SUB_COLORS['exhaust'])
                pygame.draw.circle(screen, heat_color, (exhaust_x, exhaust_y), 
                                 random.randint(1, 3))
        
        # Weather details and battle damage
        damage_spots = [
            (self.x - 15, current_y + 3), (self.x + 8, current_y - 5),
            (self.x - 5, current_y + 8), (self.x + 20, current_y + 2)
        ]
        for spot_x, spot_y in damage_spots:
            pygame.draw.circle(screen, SUB_COLORS['rust'], (spot_x, spot_y), 
                             random.randint(1, 3))
        
        # Hull number/identification (retro military style)
        hull_number = "SSN-571"  # Classic submarine designation
        if hasattr(pygame.font, 'Font'):
            try:
                small_font = pygame.font.Font(None, 12)
                number_surface = small_font.render(hull_number, True, SUB_COLORS['light_white'])
                screen.blit(number_surface, (self.x - 20, current_y + 8))
            except:
                pass  # Skip if font fails
        
        # Bubble generation from propeller
        if self.bubble_timer > 0.1:
            particles.add_bubble(prop_center_x - 8, prop_center_y + random.randint(-6, 6))
            # Additional bubbles from hull vents
            particles.add_bubble(self.x + random.randint(-10, 10), 
                               current_y + self.height//2 + random.randint(0, 3))
            self.bubble_timer = 0


class UltraParticleSystem:
    """Advanced particle system for underwater effects."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bubbles = []
        self.debris = []
        self.light_rays = []
        self.water_distortion = []
        
    def add_bubble(self, x, y, size=None, velocity=None):
        """Add a bubble particle."""
        bubble = {
            'x': x,
            'y': y,
            'size': size or random.uniform(2, 8),
            'velocity': velocity or random.uniform(20, BUBBLE_RISE_SPEED),
            'wobble': random.uniform(0, math.pi * 2),
            'wobble_speed': random.uniform(2, 5),
            'alpha': random.uniform(0.6, 1.0),
            'life': random.uniform(3, 6)
        }
        self.bubbles.append(bubble)
        
    def add_debris(self, x, y):
        """Add a debris particle."""
        debris = {
            'x': x,
            'y': y,
            'size': random.uniform(1, 4),
            'velocity': random.uniform(5, DEBRIS_FALL_SPEED),
            'rotation': random.uniform(0, math.pi * 2),
            'rotation_speed': random.uniform(-2, 2),
            'alpha': random.uniform(0.3, 0.8),
            'color': random.choice([(100, 80, 60), (80, 70, 50), (60, 50, 40)])
        }
        self.debris.append(debris)
        
    def add_light_ray(self, x, y, angle, length):
        """Add a light ray effect."""
        ray = {
            'x': x,
            'y': y,
            'angle': angle,
            'length': length,
            'width': random.uniform(2, 6),
            'alpha': random.uniform(0.3, 0.7),
            'pulse': random.uniform(0, math.pi * 2),
            'color': random.choice([OCEAN_COLORS['light'], TEXT_COLORS['glow']])
        }
        self.light_rays.append(ray)
        
    def update(self, delta_time):
        """Update all particles."""
        # Update bubbles
        for bubble in self.bubbles[:]:
            bubble['y'] -= bubble['velocity'] * delta_time
            bubble['wobble'] += bubble['wobble_speed'] * delta_time
            bubble['x'] += math.sin(bubble['wobble']) * 0.5
            bubble['life'] -= delta_time
            
            if bubble['y'] < -bubble['size'] or bubble['life'] <= 0:
                self.bubbles.remove(bubble)
                
        # Update debris
        for debris in self.debris[:]:
            debris['y'] += debris['velocity'] * delta_time
            debris['rotation'] += debris['rotation_speed'] * delta_time
            
            if debris['y'] > self.height + debris['size']:
                self.debris.remove(debris)
                
        # Update light rays
        for ray in self.light_rays[:]:
            ray['pulse'] += delta_time * 3
            ray['alpha'] = 0.4 + 0.3 * math.sin(ray['pulse'])
            
    def draw(self, screen):
        """Draw all particles."""
        # Skip light rays to avoid visual artifacts
            
        # Draw debris
        for debris in self.debris:
            debris_surface = pygame.Surface((debris['size'] * 2, debris['size'] * 2), 
                                          pygame.SRCALPHA)
            color_with_alpha = (*debris['color'], int(255 * debris['alpha']))
            pygame.draw.rect(debris_surface, color_with_alpha,
                           (0, 0, debris['size'], debris['size']))
            
            rotated_debris = pygame.transform.rotate(debris_surface, 
                                                   math.degrees(debris['rotation']))
            screen.blit(rotated_debris, (debris['x'], debris['y']))
            
        # Draw bubbles (foreground)
        for bubble in self.bubbles:
            bubble_surface = pygame.Surface((bubble['size'] * 3, bubble['size'] * 3), 
                                          pygame.SRCALPHA)
            
            # Bubble with highlight
            bubble_color = (150, 200, 255, int(255 * bubble['alpha'] * 0.3))
            highlight_color = (255, 255, 255, int(255 * bubble['alpha'] * 0.8))
            
            pygame.draw.circle(bubble_surface, bubble_color, 
                             (bubble['size'], bubble['size']), int(bubble['size']))
            pygame.draw.circle(bubble_surface, highlight_color,
                             (bubble['size'] - 1, bubble['size'] - 1), 
                             max(1, int(bubble['size'] * 0.3)))
            
            screen.blit(bubble_surface, (bubble['x'] - bubble['size'], 
                                       bubble['y'] - bubble['size']))


class UltraSonarSystem:
    """Advanced multi-layered sonar system with interference patterns."""
    
    def __init__(self, center_x, center_y, max_radius):
        self.center_x = center_x
        self.center_y = center_y
        self.max_radius = max_radius
        self.primary_waves = []
        self.echo_waves = []
        self.interference_patterns = []
        self.harmonic_waves = []
        self.charge_level = 0
        
    def charge_sonar(self, delta_time):
        """Charge the sonar system."""
        self.charge_level = min(1.0, self.charge_level + delta_time)
        
        # Add charging effects
        if random.random() < 0.3:
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, 30)
            spark_x = self.center_x + math.cos(angle) * distance
            spark_y = self.center_y + math.sin(angle) * distance
            
            spark = {
                'x': spark_x,
                'y': spark_y,
                'life': 0.2,
                'intensity': random.uniform(0.5, 1.0)
            }
            self.interference_patterns.append(spark)
    
    def fire_sonar_blast(self):
        """Fire the main sonar blast."""
        # Primary wave
        primary = {
            'radius': 0,
            'speed': 300,
            'intensity': 1.0,
            'frequency': 2.0,
            'type': 'primary'
        }
        self.primary_waves.append(primary)
        
        # Multiple harmonic waves
        for i in range(3):
            harmonic = {
                'radius': 0,
                'speed': 250 + i * 30,
                'intensity': 0.7 - i * 0.2,
                'frequency': 3.0 + i,
                'phase_offset': i * 0.5,
                'type': 'harmonic'
            }
            self.harmonic_waves.append(harmonic)
            
        # Echo waves (delayed)
        for i in range(2):
            echo = {
                'radius': 0,
                'speed': 200,
                'intensity': 0.4,
                'delay': 0.5 + i * 0.3,
                'current_delay': 0,
                'active': False,
                'type': 'echo'
            }
            self.echo_waves.append(echo)
    
    def update(self, delta_time):
        """Update all sonar waves."""
        # Update primary waves
        for wave in self.primary_waves[:]:
            wave['radius'] += wave['speed'] * delta_time
            wave['intensity'] = max(0, wave['intensity'] - delta_time * 0.5)
            
            if wave['radius'] > self.max_radius or wave['intensity'] <= 0:
                self.primary_waves.remove(wave)
                
        # Update harmonic waves
        for wave in self.harmonic_waves[:]:
            wave['radius'] += wave['speed'] * delta_time
            wave['intensity'] = max(0, wave['intensity'] - delta_time * 0.3)
            
            if wave['radius'] > self.max_radius or wave['intensity'] <= 0:
                self.harmonic_waves.remove(wave)
                
        # Update echo waves
        for wave in self.echo_waves[:]:
            if not wave['active']:
                wave['current_delay'] += delta_time
                if wave['current_delay'] >= wave['delay']:
                    wave['active'] = True
            else:
                wave['radius'] += wave['speed'] * delta_time
                wave['intensity'] = max(0, wave['intensity'] - delta_time * 0.4)
                
                if wave['radius'] > self.max_radius or wave['intensity'] <= 0:
                    self.echo_waves.remove(wave)
                    
        # Update interference patterns
        for pattern in self.interference_patterns[:]:
            pattern['life'] -= delta_time
            if pattern['life'] <= 0:
                self.interference_patterns.remove(pattern)
    
    def draw(self, screen):
        """Draw all sonar effects."""
        current_time = time.time()
        
        # Draw harmonic waves first
        for wave in self.harmonic_waves:
            if wave['radius'] > 0:
                for ring in range(int(wave['radius'] // 20)):
                    ring_radius = ring * 20
                    if ring_radius <= wave['radius']:
                        alpha = wave['intensity'] * (1.0 - ring_radius / wave['radius'])
                        color = (*SONAR_COLORS['harmonic'], int(255 * alpha))
                        
                        # Create pulsing effect
                        pulse = 0.8 + 0.2 * math.sin(current_time * wave['frequency'] + 
                                                    wave['phase_offset'])
                        ring_size = int(ring_radius * pulse)
                        
                        if ring_size > 0:
                            pygame.draw.circle(screen, color, 
                                             (self.center_x, self.center_y), ring_size, 2)
        
        # Draw primary waves
        for wave in self.primary_waves:
            if wave['radius'] > 0:
                # Multiple rings with interference
                for ring in range(int(wave['radius'] // 30)):
                    ring_radius = ring * 30
                    if ring_radius <= wave['radius']:
                        alpha = wave['intensity'] * (1.0 - ring_radius / wave['radius'])
                        color = (*SONAR_COLORS['primary'], int(255 * alpha))
                        
                        # Interference pattern
                        interference = 1.0 + 0.3 * math.sin(current_time * wave['frequency'] * 2)
                        ring_size = int(ring_radius * interference)
                        
                        if ring_size > 0:
                            pygame.draw.circle(screen, color,
                                             (self.center_x, self.center_y), ring_size, 3)
        
        # Draw echo waves
        for wave in self.echo_waves:
            if wave['active'] and wave['radius'] > 0:
                alpha = wave['intensity'] * 0.6
                color = (*SONAR_COLORS['echo'], int(255 * alpha))
                pygame.draw.circle(screen, color, 
                                 (self.center_x, self.center_y), 
                                 int(wave['radius']), 2)
        
        # Draw charging effects
        for pattern in self.interference_patterns:
            intensity = pattern['intensity'] * (pattern['life'] / 0.2)
            color = (*SONAR_COLORS['interference'], int(255 * intensity))
            pygame.draw.circle(screen, color, 
                             (int(pattern['x']), int(pattern['y'])), 3)


class SonarPulseText:
    """Clean, readable sonar-themed text with wave emergence."""
    
    def __init__(self, text, font, center_x, center_y):
        self.text = text
        self.font = font
        self.center_x = center_x
        self.center_y = center_y
        
        # Pre-render text surfaces for clean rendering
        self.main_surface = font.render(text, True, TEXT_COLORS['hologram'])
        self.glow_surface = font.render(text, True, TEXT_COLORS['glow'])
        self.shadow_surface = font.render(text, True, TEXT_COLORS['shadow'])
        
        # Calculate positioning
        self.text_rect = self.main_surface.get_rect(center=(center_x, center_y))
        
        # Animation state
        self.active = False
        self.emergence_progress = 0.0
        self.scan_wave_radius = 0
        self.text_alpha = 0.0
        
    def update(self, emergence_factor):
        """Update sonar pulse text emergence."""
        self.emergence_progress = emergence_factor
        self.active = (emergence_factor > 0.0)
        
        if not self.active:
            self.scan_wave_radius = 0
            self.text_alpha = 0.0
            return
        
        # Expanding sonar wave from submarine
        self.scan_wave_radius = emergence_factor * 300
        
        # Text appears when sonar wave reaches it
        distance_to_text = math.sqrt(
            (self.center_x - self.center_x)**2 + 
            (self.center_y - self.center_y)**2
        )
        
        if self.scan_wave_radius > distance_to_text:
            # Text discovered - fade in smoothly
            discovery_progress = min(1.0, (self.scan_wave_radius - distance_to_text) / 100)
            self.text_alpha = discovery_progress
        else:
            self.text_alpha = 0.0
    
    def draw_sonar_pulse(self, screen):
        """Render sonar pulse text effect."""
        if not self.active:
            return
        
        # Draw expanding sonar discovery wave
        if self.scan_wave_radius > 10:
            # Main discovery wave
            wave_color = SONAR_COLORS['primary']
            pygame.draw.circle(screen, wave_color, 
                             (self.center_x, self.center_y), 
                             int(self.scan_wave_radius), 3)
            
            # Inner pulse ring
            inner_radius = max(0, self.scan_wave_radius - 30)
            if inner_radius > 0:
                inner_color = tuple(int(c * 0.6) for c in SONAR_COLORS['primary'])
                pygame.draw.circle(screen, inner_color,
                                 (self.center_x, self.center_y),
                                 int(inner_radius), 2)
        
        # Render text when discovered
        if self.text_alpha > 0.0:
            # Calculate final alpha
            final_alpha = max(1, min(255, int(self.text_alpha * 255)))
            
            # Render shadow
            if self.text_alpha > 0.3:
                shadow_alpha = int(final_alpha * 0.4)
                self.shadow_surface.set_alpha(shadow_alpha)
                screen.blit(self.shadow_surface, 
                          (self.text_rect.x + 2, self.text_rect.y + 2))
            
            # Render glow
            if self.text_alpha > 0.2:
                glow_alpha = int(final_alpha * 0.7)
                self.glow_surface.set_alpha(glow_alpha)
                screen.blit(self.glow_surface, 
                          (self.text_rect.x + 1, self.text_rect.y + 1))
            
            # Render main text with sonar glow effect
            self.main_surface.set_alpha(final_alpha)
            screen.blit(self.main_surface, self.text_rect.topleft)
            
            # Add sonar scanning lines across discovered text
            if self.text_alpha > 0.5:
                self._draw_scanning_lines(screen)
    
    def _draw_scanning_lines(self, screen):
        """Draw subtle scanning lines across the text."""
        current_time = time.time()
        
        # Horizontal scanning lines
        for i in range(3):
            line_y = self.text_rect.top + (i + 1) * (self.text_rect.height // 4)
            line_alpha = int(100 * (0.5 + 0.5 * math.sin(current_time * 8 + i)))
            line_color = (*SONAR_COLORS['primary'], line_alpha)
            
            # Create line surface with alpha
            line_surface = pygame.Surface((self.text_rect.width, 1), pygame.SRCALPHA)
            line_surface.fill(line_color)
            screen.blit(line_surface, (self.text_rect.left, line_y))

def run_startup_animation(screen, clock, width, height):
    """Ultra-creative sonar startup animation with cinematic effects."""
    # Initialize sound manager and sync timing with audio
    sound_manager = SoundManager()
    
    # Start immediately to sync with 4-second audio
    sound_manager.play_music('intro_theme', loops=0, fade_duration=0.1)
    
    # Initialize all ultra-creative systems
    center_x, center_y = width // 2, height // 2
    max_radius = math.sqrt((width/2)**2 + (height/2)**2) * 1.2
    
    # Create ultra-submarine
    submarine = UltraSubmarine(center_x, center_y + 50, 80, 40)
    
    # Create particle system
    particles = UltraParticleSystem(width, height)
    
    # Create advanced sonar system
    sonar = UltraSonarSystem(center_x, center_y, max_radius)
    
    # Create sonar pulse text system
    scale_factor = min(width / 800, height / 600)
    font_size = max(32, int(80 * scale_factor))
    font = get_pixel_font(font_size)
    sonar_text = SonarPulseText("Sonar Arts", font, center_x, center_y - 30)
    
    # Animation timing and state
    start_time = time.time()
    last_frame_time = start_time
    animation_phase = "sub_appear"
    phase_start_time = start_time
    
    # Environmental setup - add initial debris only
    for _ in range(15):
        particles.add_debris(
            random.randint(0, width),
            random.randint(-50, 0)
        )
    
    # Main animation loop
    while animation_phase != "finished":
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        
        total_elapsed = current_time - start_time
        phase_elapsed = current_time - phase_start_time
        
        # Handle events (allow skipping)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                    animation_phase = "finished"
                    break
        
        if animation_phase == "finished":
            break
        
        # Phase management with 4-second audio synchronization
        if animation_phase == "sub_appear" and phase_elapsed >= SUB_APPEAR_DURATION:
            animation_phase = "sonar_blast"
            phase_start_time = current_time
            sonar.fire_sonar_blast()  # Immediate ping!
            
        elif animation_phase == "sonar_blast" and phase_elapsed >= SONAR_BLAST_DURATION:
            animation_phase = "text_emerge"
            phase_start_time = current_time
            
        elif animation_phase == "text_emerge" and phase_elapsed >= TEXT_EMERGE_DURATION:
            animation_phase = "text_hold"
            phase_start_time = current_time
            
        elif animation_phase == "text_hold" and phase_elapsed >= TEXT_HOLD_DURATION:
            animation_phase = "finished"
        
        # Create depth-gradient background
        draw_ocean_gradient(screen, width, height, total_elapsed)
        
        # Update all systems
        submarine.update(delta_time, animation_phase)
        particles.update(delta_time)
        sonar.update(delta_time)
        
        # Add dramatic particle effects during sonar blast
        if animation_phase == "sonar_blast":
            # Intense particle generation during the ping
            if random.random() < 0.6:
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(30, 120)
                effect_x = center_x + math.cos(angle) * distance
                effect_y = center_y + math.sin(angle) * distance
                particles.add_bubble(effect_x, effect_y, random.uniform(4, 8), random.uniform(25, 50))
        
        # Text emergence calculation with safe transition handling
        text_emergence = 0.0
        if animation_phase == "text_emerge":
            # Smooth emergence from 0 to 1 over the duration
            text_emergence = min(1.0, max(0.0, phase_elapsed / TEXT_EMERGE_DURATION))
        elif animation_phase == "text_hold":
            # Keep at full emergence during hold phase
            text_emergence = 1.0
        # For all other phases, text_emergence stays 0.0 (no rendering)
            
        sonar_text.update(text_emergence)
        
        # Add environmental particle effects
        if random.random() < 0.1:
            particles.add_debris(random.randint(0, width), -10)
        if random.random() < 0.05:
            particles.add_bubble(
                random.randint(width//4, 3*width//4),
                height + 10,
                random.uniform(4, 12),
                random.uniform(15, 25)
            )
        
        # Interactive mouse effects
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if 0 <= mouse_x < width and 0 <= mouse_y < height:
            # Add particle attraction to mouse
            if random.random() < 0.3:
                particles.add_bubble(
                    mouse_x + random.randint(-20, 20),
                    mouse_y + random.randint(-20, 20),
                    random.uniform(2, 5),
                    random.uniform(10, 30)
                )
        
        # Render everything in proper depth order
        particles.draw(screen)  # Background particles
        submarine.draw(screen, particles)  # Submarine with bubbles
        sonar.draw(screen)  # Sonar effects
        
        # Add cinematic water distortion effect during sonar blast
        if animation_phase in ["sonar_blast", "text_emerge"]:
            add_water_distortion(screen, width, height, total_elapsed)
        
        # Render sonar pulse text system
        sonar_text.draw_sonar_pulse(screen)  # Clean, readable sonar text
        
        pygame.display.flip()
        clock.tick(60)
    
    # Fade out effect
    fade_out_animation(screen, clock, width, height)


def draw_ocean_gradient(screen, width, height, time_elapsed):
    """Draw realistic ocean depth gradient background."""
    # Create vertical gradient from deep ocean to surface
    for y in range(height):
        depth_factor = y / height
        
        # Color mixing based on depth
        if depth_factor < 0.3:
            # Deep ocean
            color = OCEAN_COLORS['deep']
        elif depth_factor < 0.6:
            # Mid ocean
            blend = (depth_factor - 0.3) / 0.3
            color = blend_colors(OCEAN_COLORS['deep'], OCEAN_COLORS['mid'], blend)
        elif depth_factor < 0.8:
            # Upper ocean
            blend = (depth_factor - 0.6) / 0.2
            color = blend_colors(OCEAN_COLORS['mid'], OCEAN_COLORS['surface'], blend)
        else:
            # Near surface
            blend = (depth_factor - 0.8) / 0.2
            color = blend_colors(OCEAN_COLORS['surface'], OCEAN_COLORS['light'], blend)
        
        # Add subtle animation
        wave_effect = 5 * math.sin(time_elapsed * 0.5 + y * 0.01)
        animated_color = tuple(min(255, max(0, int(c + wave_effect))) for c in color)
        
        pygame.draw.line(screen, animated_color, (0, y), (width, y))


def blend_colors(color1, color2, factor):
    """Blend two colors by a factor (0=color1, 1=color2)."""
    return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))


def add_water_distortion(screen, width, height, time_elapsed):
    """Add water distortion ripple effects."""
    # Create subtle ripple effects across the screen
    ripple_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for i in range(0, width, 20):
        for j in range(0, height, 30):
            ripple_intensity = 10 * math.sin(time_elapsed * 3 + i * 0.02 + j * 0.03)
            if abs(ripple_intensity) > 2:
                ripple_color = (100, 150, 200, int(abs(ripple_intensity)))
                pygame.draw.circle(ripple_surface, ripple_color, (i, j), 3)
    
    screen.blit(ripple_surface, (0, 0))


def fade_out_animation(screen, clock, width, height):
    """Cinematic fade out with particle cleanup."""
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill(BACKGROUND_COLOR)
    
    for alpha in range(0, 256, 8):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    
    # Final clear
    screen.fill(BACKGROUND_COLOR)
    pygame.display.flip()
    time.sleep(0.2)
