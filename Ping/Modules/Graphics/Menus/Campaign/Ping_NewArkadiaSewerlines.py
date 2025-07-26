"""
New Arkadia Sewerlines Campaign Module
Dedicated module for the New Arkadia Sewerlines zone with its own stunning visual background.
"""

import pygame
import math
import time
import random
from typing import Optional, List, Tuple
from ....Core.Ping_MapState import get_map_state, MapStateManager
from ....Core.Ping_MapTree import NodeType, MapNode, MapZone
from ...UI.Ping_Fonts import get_pixel_font
from ...UI.Ping_Button import get_button

# New Arkadia Sewerlines specific color palette
SEWER_BASE_DARK = (15, 25, 20)         # Deep sewer darkness
SEWER_WATER_MURKY = (10, 40, 30)       # Murky sewer water
SEWER_WATER_FLOW = (20, 60, 45)        # Flowing water highlights
SEWER_PIPE_METAL = (75, 80, 85)        # Clean metal pipes
SEWER_PIPE_RUST = (110, 70, 40)        # Rusty pipe details
SEWER_PIPE_CORRODED = (90, 60, 35)     # Heavily corroded sections
SEWER_ALGAE_DARK = (30, 70, 35)        # Dark algae growth
SEWER_ALGAE_BRIGHT = (50, 110, 55)     # Bright algae highlights
SEWER_MOSS_WET = (45, 85, 50)          # Wet moss texture
SEWER_GRIME = (35, 40, 35)             # Accumulated grime
SEWER_CONCRETE_OLD = (60, 65, 60)      # Aged concrete walls
SEWER_SLIME_GREEN = (45, 100, 55)      # Glowing green slime
SEWER_STEAM = (180, 190, 185)          # Steam/mist
SEWER_TOXIC_GREEN = (80, 180, 90)      # Toxic waste glow

# Node colors specific to sewer theme
NODE_ACCESSIBLE_SEWER = (120, 180, 130)    # Clean water available
NODE_COMPLETED_SEWER = (80, 120, 200)      # Purified water
NODE_BLOCKED_SEWER = (80, 80, 80)          # Blocked pipe
NODE_CURRENT_SEWER = (220, 180, 80)        # Current location glow
NODE_SHOP_SEWER = (180, 120, 200)          # Shop/upgrade station
NODE_BOSS_SEWER = (200, 80, 80)            # Boss battle danger

# UI colors
TEXT_SEWER_WHITE = (255, 255, 255)
TEXT_SEWER_GREEN = (120, 255, 130)
TEXT_SEWER_RED = (255, 120, 120)
TEXT_SEWER_YELLOW = (255, 255, 120)

class SewerWaterParticle:
    """Enhanced water particle system for sewer atmosphere."""
    
    def __init__(self, x: float, y: float, particle_type: str = "droplet"):
        self.x = x
        self.y = y
        self.particle_type = particle_type
        
        if particle_type == "droplet":
            self.vel_x = random.uniform(-0.8, 0.8)
            self.vel_y = random.uniform(0.8, 2.5)
            self.life = random.uniform(2.0, 4.0)
            self.size = random.randint(2, 4)
            self.color = SEWER_WATER_FLOW
        elif particle_type == "steam":
            self.vel_x = random.uniform(-0.3, 0.3)
            self.vel_y = random.uniform(-1.5, -0.8)
            self.life = random.uniform(3.0, 6.0)
            self.size = random.randint(4, 8)
            self.color = SEWER_STEAM
        elif particle_type == "bubble":
            self.vel_x = random.uniform(-0.2, 0.2)
            self.vel_y = random.uniform(-0.5, -0.2)
            self.life = random.uniform(4.0, 8.0)
            self.size = random.randint(3, 6)
            self.color = SEWER_WATER_MURKY
            
        self.max_life = self.life
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-30, 30)
        
    def update(self, dt: float):
        self.x += self.vel_x * dt * 60
        self.y += self.vel_y * dt * 60
        self.life -= dt
        self.rotation += self.rotation_speed * dt
        
        # Apply physics based on particle type
        if self.particle_type == "droplet":
            self.vel_y += 0.2 * dt  # Gravity
        elif self.particle_type == "steam":
            self.vel_y *= 0.995  # Steam dissipates
            self.vel_x *= 0.998
        elif self.particle_type == "bubble":
            self.vel_y *= 0.99  # Bubbles slow down
            
    def draw(self, screen: pygame.Surface):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            color = (*self.color, min(255, alpha))
            
            # Create temporary surface for alpha blending
            if self.size > 1:
                temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                
                if self.particle_type == "bubble":
                    # Draw hollow bubble
                    pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size, 1)
                else:
                    # Draw solid particle
                    pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
                    
                screen.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))
            else:
                try:
                    screen.set_at((int(self.x), int(self.y)), color[:3])
                except:
                    pass  # Skip if out of bounds
                
    def is_alive(self) -> bool:
        return self.life > 0

class NewArkadiaSewerlines:
    """New Arkadia Sewerlines zone map tree interface."""
    
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.map_state: MapStateManager = get_map_state()
        
        # Visual effects
        self.water_particles: List[SewerWaterParticle] = []
        self.last_particle_spawn = 0
        self.particle_spawn_interval = 0.2
        
        # Animation timers
        self.water_flow_offset = 0
        self.node_pulse_timer = 0
        self.pipe_steam_timer = 0
        self.algae_sway_timer = 0
        
        # Selection state
        self.selected_node: Optional[str] = None
        self.hovered_node: Optional[str] = None
        
        # Panning state
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.is_panning = False
        self.last_mouse_pos = (0, 0)
        
        # Controls tooltip state
        self.show_controls_tooltip = False
        
        # Background cache
        self.background_surface: Optional[pygame.Surface] = None
        self.background_width = 0
        self.background_height = 0
        
        # Initialize map state if needed
        if not self.map_state.get_current_zone():
            if self.map_state.has_existing_run():
                self.map_state.continue_existing_run()
            else:
                self.map_state.initialize_new_run()
    
    def _create_stunning_sewer_background(self, width: int, height: int) -> pygame.Surface:
        """Create a stunning, detailed sewer background for New Arkadia Sewerlines."""
        surface = pygame.Surface((width, height))
        
        # Base gradient from deep darkness to murky green
        for y in range(height):
            gradient_factor = y / height
            base_color = (
                int(SEWER_BASE_DARK[0] + gradient_factor * (SEWER_CONCRETE_OLD[0] - SEWER_BASE_DARK[0])),
                int(SEWER_BASE_DARK[1] + gradient_factor * (SEWER_CONCRETE_OLD[1] - SEWER_BASE_DARK[1])),
                int(SEWER_BASE_DARK[2] + gradient_factor * (SEWER_CONCRETE_OLD[2] - SEWER_BASE_DARK[2]))
            )
            pygame.draw.line(surface, base_color, (0, y), (width, y))
        
        # Create main sewer tunnels with perspective
        tunnel_sections = [
            # (start_x, start_y, end_x, end_y, width, depth)
            (width * 0.1, height * 0.15, width * 0.9, height * 0.25, 80, "main"),
            (width * 0.05, height * 0.35, width * 0.95, height * 0.45, 100, "main"),
            (width * 0.15, height * 0.6, width * 0.85, height * 0.7, 75, "branch"),
            (width * 0.2, height * 0.8, width * 0.8, height * 0.85, 60, "drain")
        ]
        
        for start_x, start_y, end_x, end_y, tunnel_width, tunnel_type in tunnel_sections:
            # Create tunnel with perspective and depth
            tunnel_center_y = (start_y + end_y) / 2
            
            # Draw tunnel walls with brick texture
            wall_top = tunnel_center_y - tunnel_width / 2
            wall_bottom = tunnel_center_y + tunnel_width / 2
            
            # Tunnel base
            tunnel_rect = pygame.Rect(int(start_x), int(wall_top), int(end_x - start_x), int(tunnel_width))
            pygame.draw.rect(surface, SEWER_CONCRETE_OLD, tunnel_rect)
            
            # Add brick pattern to walls
            brick_width = 25
            brick_height = 12
            for brick_x in range(int(start_x), int(end_x), brick_width):
                for brick_y in range(int(wall_top), int(wall_bottom), brick_height):
                    # Offset every other row
                    offset = (brick_height // 2) if ((brick_y - int(wall_top)) // brick_height) % 2 else 0
                    brick_rect = pygame.Rect(brick_x + offset, brick_y, brick_width - 2, brick_height - 2)
                    
                    # Vary brick colors for realism
                    brick_color = (
                        SEWER_CONCRETE_OLD[0] + random.randint(-10, 10),
                        SEWER_CONCRETE_OLD[1] + random.randint(-10, 10),
                        SEWER_CONCRETE_OLD[2] + random.randint(-10, 10)
                    )
                    pygame.draw.rect(surface, brick_color, brick_rect)
                    
                    # Add mortar lines
                    pygame.draw.rect(surface, SEWER_GRIME, brick_rect, 1)
            
            # Flowing water in tunnel bottom
            water_y = wall_bottom - 15
            water_rect = pygame.Rect(int(start_x), int(water_y), int(end_x - start_x), 15)
            pygame.draw.rect(surface, SEWER_WATER_MURKY, water_rect)
            
            # Animated water flow effect
            flow_offset = int(self.water_flow_offset) % 30
            for i in range(0, int(end_x - start_x), 30):
                highlight_x = int(start_x + i + flow_offset)
                if highlight_x < end_x:
                    highlight_rect = pygame.Rect(highlight_x, int(water_y), 12, 15)
                    pygame.draw.rect(surface, SEWER_WATER_FLOW, highlight_rect)
            
            # Add reflections on water surface
            for reflection_x in range(int(start_x), int(end_x), 40):
                reflection_y = int(water_y) + random.randint(2, 8)
                pygame.draw.line(surface, SEWER_STEAM, 
                               (reflection_x, reflection_y), 
                               (reflection_x + 15, reflection_y), 1)
        
        # Add large intersection pipes
        intersection_pipes = [
            (width * 0.25, height * 0.3, 60, 30, "vertical"),
            (width * 0.6, height * 0.5, 70, 35, "horizontal"),
            (width * 0.4, height * 0.75, 50, 25, "diagonal"),
            (width * 0.75, height * 0.35, 55, 28, "vertical")
        ]
        
        for pipe_x, pipe_y, pipe_w, pipe_h, pipe_orientation in intersection_pipes:
            # Main pipe body with metallic shading
            pipe_rect = pygame.Rect(int(pipe_x - pipe_w/2), int(pipe_y - pipe_h/2), int(pipe_w), int(pipe_h))
            
            # Create metallic gradient
            for i in range(int(pipe_h)):
                shade_factor = i / pipe_h
                pipe_color = (
                    int(SEWER_PIPE_METAL[0] * (0.7 + 0.3 * shade_factor)),
                    int(SEWER_PIPE_METAL[1] * (0.7 + 0.3 * shade_factor)),
                    int(SEWER_PIPE_METAL[2] * (0.7 + 0.3 * shade_factor))
                )
                pygame.draw.line(surface, pipe_color, 
                               (pipe_rect.x, pipe_rect.y + i), 
                               (pipe_rect.right, pipe_rect.y + i))
            
            # Add rust patches
            for _ in range(random.randint(2, 5)):
                rust_x = pipe_rect.x + random.randint(5, pipe_rect.width - 15)
                rust_y = pipe_rect.y + random.randint(5, pipe_rect.height - 10)
                rust_size = random.randint(8, 20)
                pygame.draw.ellipse(surface, SEWER_PIPE_RUST, 
                                  (rust_x, rust_y, rust_size, rust_size // 2))
            
            # Pipe joints and bolts
            joint_positions = [
                (pipe_rect.left, pipe_rect.centery),
                (pipe_rect.right, pipe_rect.centery),
                (pipe_rect.centerx, pipe_rect.top),
                (pipe_rect.centerx, pipe_rect.bottom)
            ]
            
            for joint_x, joint_y in joint_positions:
                # Joint flange
                pygame.draw.circle(surface, SEWER_PIPE_CORRODED, (int(joint_x), int(joint_y)), 12)
                pygame.draw.circle(surface, SEWER_PIPE_METAL, (int(joint_x), int(joint_y)), 8)
                
                # Bolts around joint
                for angle in range(0, 360, 45):
                    bolt_x = joint_x + 6 * math.cos(math.radians(angle))
                    bolt_y = joint_y + 6 * math.sin(math.radians(angle))
                    pygame.draw.circle(surface, SEWER_PIPE_RUST, (int(bolt_x), int(bolt_y)), 2)
        
        # Add stunning algae and overgrowth
        algae_patches = []
        for _ in range(25):
            algae_x = random.randint(0, width)
            algae_y = random.randint(int(height * 0.4), height)  # Lower areas
            algae_size = random.randint(15, 40)
            algae_patches.append((algae_x, algae_y, algae_size))
        
        for algae_x, algae_y, algae_size in algae_patches:
            # Create organic algae shape
            points = []
            num_points = 8
            for i in range(num_points):
                angle = (i / num_points) * 2 * math.pi
                radius_variation = random.uniform(0.7, 1.3)
                point_x = algae_x + (algae_size * radius_variation) * math.cos(angle)
                point_y = algae_y + (algae_size * radius_variation) * math.sin(angle)
                points.append((int(point_x), int(point_y)))
            
            # Draw algae with multiple layers for depth
            pygame.draw.polygon(surface, SEWER_ALGAE_DARK, points)
            
            # Bright highlights for wet appearance
            highlight_points = [(x + random.randint(-3, 3), y + random.randint(-3, 3)) for x, y in points[:5]]
            pygame.draw.polygon(surface, SEWER_ALGAE_BRIGHT, highlight_points)
            
            # Add some glowing toxic elements
            if random.random() < 0.3:
                glow_x = algae_x + random.randint(-algae_size//2, algae_size//2)
                glow_y = algae_y + random.randint(-algae_size//2, algae_size//2)
                glow_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*SEWER_TOXIC_GREEN, 100), (10, 10), 10)
                surface.blit(glow_surface, (glow_x - 10, glow_y - 10), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Add atmospheric grime stains and water damage
        for _ in range(40):
            stain_x = random.randint(0, width)
            stain_y = random.randint(0, height)
            stain_w = random.randint(20, 60)
            stain_h = random.randint(10, 30)
            
            stain_rect = pygame.Rect(stain_x, stain_y, stain_w, stain_h)
            
            # Create streaky stain pattern
            stain_color = (
                SEWER_GRIME[0] + random.randint(-10, 10),
                SEWER_GRIME[1] + random.randint(-10, 10),
                SEWER_GRIME[2] + random.randint(-10, 10)
            )
            pygame.draw.ellipse(surface, stain_color, stain_rect)
            
            # Add vertical streaks for water damage
            if random.random() < 0.4:
                streak_length = random.randint(30, 80)
                pygame.draw.line(surface, stain_color, 
                               (stain_x + stain_w//2, stain_y), 
                               (stain_x + stain_w//2, stain_y + streak_length), 2)
        
        # Add distant tunnel lighting effects
        light_sources = [
            (width * 0.2, height * 0.2),
            (width * 0.7, height * 0.4),
            (width * 0.5, height * 0.6),
            (width * 0.8, height * 0.8)
        ]
        
        for light_x, light_y in light_sources:
            # Create atmospheric light beam
            beam_surface = pygame.Surface((120, 200), pygame.SRCALPHA)
            light_color = (*SEWER_STEAM, 30)
            
            # Draw light cone
            light_points = [
                (60, 0),
                (40, 200),
                (80, 200)
            ]
            pygame.draw.polygon(beam_surface, light_color, light_points)
            
            # Position and blend the light
            surface.blit(beam_surface, (int(light_x - 60), int(light_y)), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        return surface
    
    def _draw_sewer_connection_line(self, surface: pygame.Surface, start_pos: Tuple[int, int], 
                                  end_pos: Tuple[int, int], is_accessible: bool):
        """Draw a detailed sewer pipe connection between nodes."""
        if is_accessible:
            pipe_color = SEWER_PIPE_METAL
            water_color = SEWER_WATER_FLOW
        else:
            pipe_color = SEWER_PIPE_CORRODED
            water_color = SEWER_WATER_MURKY
        
        # Calculate pipe thickness and water flow
        distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
        pipe_thickness = max(8, int(distance / 30))
        
        # Main pipe body
        pygame.draw.line(surface, pipe_color, start_pos, end_pos, pipe_thickness)
        
        # Pipe highlights for metallic appearance
        highlight_color = tuple(min(255, c + 40) for c in pipe_color)
        pygame.draw.line(surface, highlight_color, start_pos, end_pos, pipe_thickness - 4)
        
        # Water flow inside pipe
        pygame.draw.line(surface, water_color, start_pos, end_pos, pipe_thickness - 6)
        
        # Joint connectors at ends with enhanced detail
        for pos in [start_pos, end_pos]:
            # Outer joint ring
            pygame.draw.circle(surface, SEWER_PIPE_RUST, pos, pipe_thickness + 4)
            # Inner joint
            pygame.draw.circle(surface, pipe_color, pos, pipe_thickness)
            # Center connection
            pygame.draw.circle(surface, highlight_color, pos, pipe_thickness - 4)
            
            # Bolts around joint
            for angle in range(0, 360, 60):
                bolt_x = pos[0] + (pipe_thickness + 2) * math.cos(math.radians(angle))
                bolt_y = pos[1] + (pipe_thickness + 2) * math.sin(math.radians(angle))
                pygame.draw.circle(surface, SEWER_PIPE_CORRODED, (int(bolt_x), int(bolt_y)), 2)
    
    def _draw_sewer_node(self, surface: pygame.Surface, node: MapNode, position: Tuple[int, int], 
                        is_current: bool, is_selected: bool, is_hovered: bool):
        """Draw a detailed sewer-themed map node."""
        x, y = position
        
        # Determine node appearance based on state
        if is_current:
            base_color = NODE_CURRENT_SEWER
            size = 30
            glow_radius = 45
        elif node.is_completed:
            base_color = NODE_COMPLETED_SEWER
            size = 25
            glow_radius = 35
        elif node.is_accessible:
            base_color = NODE_ACCESSIBLE_SEWER
            size = 28
            glow_radius = 40
        else:
            base_color = NODE_BLOCKED_SEWER
            size = 22
            glow_radius = 30
        
        # Special styling for different node types
        if node.type == NodeType.SHOP:
            base_color = NODE_SHOP_SEWER
            size += 3
        elif node.type == NodeType.BOSS:
            base_color = NODE_BOSS_SEWER
            size += 5
            glow_radius += 10
        
        # Pulsing effect for current node
        if is_current:
            pulse = 1.0 + 0.4 * math.sin(self.node_pulse_timer * 4)
            size = int(size * pulse)
            glow_radius = int(glow_radius * pulse)
        
        # Selection/hover effects
        if is_selected or is_hovered:
            ring_color = TEXT_SEWER_YELLOW if is_hovered else TEXT_SEWER_WHITE
            # Outer selection ring
            pygame.draw.circle(surface, ring_color, (x, y), size + 12, 4)
            # Inner selection ring
            pygame.draw.circle(surface, ring_color, (x, y), size + 8, 2)
        
        # Atmospheric glow effect
        if node.is_accessible or is_current:
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            glow_color = (*base_color, 60)
            pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (x - glow_radius, y - glow_radius), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Node shadow for depth
        shadow_offset = 4
        shadow_surface = pygame.Surface((size * 2 + 8, size * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, 120), (size + 4, size + 4), size + 2)
        surface.blit(shadow_surface, (x - size - 4, y - size - 4))
        
        # Main node body with metallic appearance
        # Outer ring
        pygame.draw.circle(surface, SEWER_PIPE_RUST, (x, y), size + 2)
        # Main body
        pygame.draw.circle(surface, base_color, (x, y), size)
        # Metallic highlight
        highlight_color = tuple(min(255, c + 80) for c in base_color)
        pygame.draw.circle(surface, highlight_color, (x - size//3, y - size//3), size//2)
        
        # Node type indicators with enhanced graphics
        if node.type == NodeType.SHOP:
            # Enhanced shop symbol
            font = get_pixel_font(20)
            text = font.render("$", True, TEXT_SEWER_WHITE)
            text_rect = text.get_rect(center=(x, y))
            # Add glow behind text
            glow_text = font.render("$", True, (*TEXT_SEWER_YELLOW, 150))
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                surface.blit(glow_text, (text_rect.x + dx, text_rect.y + dy))
            surface.blit(text, text_rect)
            
        elif node.type == NodeType.BOSS:
            # Enhanced boss symbol with danger glow
            font = get_pixel_font(22)
            text = font.render("☠", True, TEXT_SEWER_WHITE)
            text_rect = text.get_rect(center=(x, y))
            # Danger glow
            danger_glow = font.render("☠", True, (*NODE_BOSS_SEWER, 200))
            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                surface.blit(danger_glow, (text_rect.x + dx, text_rect.y + dy))
            surface.blit(text, text_rect)
            
        elif node.is_completed:
            # Enhanced completion checkmark
            font = get_pixel_font(18)
            text = font.render("✓", True, TEXT_SEWER_WHITE)
            text_rect = text.get_rect(center=(x, y))
            # Success glow
            success_glow = font.render("✓", True, (*TEXT_SEWER_GREEN, 180))
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                surface.blit(success_glow, (text_rect.x + dx, text_rect.y + dy))
            surface.blit(text, text_rect)
        
        # Add pipe connections indicators for visual continuity
        if len(node.connections) > 0:
            for i, angle in enumerate([0, 90, 180, 270]):
                if i < len(node.connections):
                    pipe_end_x = x + (size + 8) * math.cos(math.radians(angle))
                    pipe_end_y = y + (size + 8) * math.sin(math.radians(angle))
                    pygame.draw.circle(surface, SEWER_PIPE_METAL, (int(pipe_end_x), int(pipe_end_y)), 3)
    
    def _draw_current_position_indicator(self, surface: pygame.Surface, position: Tuple[int, int]):
        """Draw an enhanced arrow pointing to current position."""
        x, y = position
        
        # Animated floating arrow with glow
        float_offset = 50 + int(15 * math.sin(self.node_pulse_timer * 3))
        arrow_y = y - float_offset
        
        # Arrow glow effect
        glow_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        glow_color = (*TEXT_SEWER_YELLOW, 100)
        pygame.draw.circle(glow_surface, glow_color, (30, 30), 30)
        surface.blit(glow_surface, (x - 30, arrow_y - 30), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Enhanced arrow shape
        arrow_points = [
            (x, arrow_y),
            (x - 12, arrow_y - 20),
            (x - 6, arrow_y - 20),
            (x - 6, arrow_y - 35),
            (x + 6, arrow_y - 35),
            (x + 6, arrow_y - 20),
            (x + 12, arrow_y - 20)
        ]
        
        # Arrow shadow
        shadow_points = [(px + 3, py + 3) for px, py in arrow_points]
        pygame.draw.polygon(surface, (0, 0, 0, 150), shadow_points)
        
        # Main arrow with gradient effect
        pygame.draw.polygon(surface, TEXT_SEWER_YELLOW, arrow_points)
        pygame.draw.polygon(surface, TEXT_SEWER_WHITE, arrow_points, 3)
        
        # Pulsing text
        font = get_pixel_font(12)
        text = font.render("YOU ARE HERE", True, TEXT_SEWER_WHITE)
        text_rect = text.get_rect(center=(x, arrow_y - 50))
        
        # Text glow
        pulse_alpha = int(150 + 105 * math.sin(self.node_pulse_timer * 2))
        text_glow = font.render("YOU ARE HERE", True, (*TEXT_SEWER_YELLOW, pulse_alpha))
        surface.blit(text_glow, (text_rect.x + 1, text_rect.y + 1))
        surface.blit(text, text_rect)
    
    def _spawn_enhanced_particles(self, width: int, height: int):
        """Spawn enhanced particle effects for sewer atmosphere."""
        current_time = time.time()
        if current_time - self.last_particle_spawn > self.particle_spawn_interval:
            if len(self.water_particles) < 30:
                # Varied particle spawn locations
                spawn_locations = [
                    (width * 0.25, height * 0.3, "steam"),     # Pipe intersections
                    (width * 0.6, height * 0.5, "bubble"),    # Water areas
                    (width * 0.4, height * 0.75, "droplet"),  # Ceiling drips
                    (width * 0.75, height * 0.35, "steam"),   # Steam vents
                    (width * 0.2, height * 0.6, "droplet"),   # More drips
                    (width * 0.8, height * 0.7, "bubble")     # Toxic bubbles
                ]
                
                spawn_x, spawn_y, particle_type = random.choice(spawn_locations)
                spawn_x += random.randint(-30, 30)
                spawn_y += random.randint(-20, 20)
                
                self.water_particles.append(SewerWaterParticle(spawn_x, spawn_y, particle_type))
            
            self.last_particle_spawn = current_time
    
    # ... [Include all the other methods from the original MapTreeMenu but adapted for sewer theme]
    
    def get_node_screen_position(self, node: MapNode, width: int, height: int) -> Tuple[int, int]:
        """Convert node logical position to screen coordinates with panning."""
        node_x, node_y = node.position
        screen_x = int((node_x / 800) * width) + self.pan_offset_x
        screen_y = int((node_y / 500) * height) + self.pan_offset_y
        return screen_x, screen_y
    
    def get_node_at_position(self, pos: Tuple[int, int], width: int, height: int) -> Optional[str]:
        """Get the node ID at the given screen position."""
        zone = self.map_state.get_current_zone()
        if not zone:
            return None
        
        mouse_x, mouse_y = pos
        
        for node_id, node in zone.nodes.items():
            node_x, node_y = self.get_node_screen_position(node, width, height)
            distance = math.sqrt((mouse_x - node_x) ** 2 + (mouse_y - node_y) ** 2)
            
            radius = 30 if node_id == zone.current_node_id else 28
            if node.type == NodeType.BOSS:
                radius = 35
            
            if distance <= radius:
                return node_id
        
        return None
    
    def handle_input(self, events: List[pygame.event.Event], width: int, height: int) -> Optional[str]:
        """Handle user input for the sewer map."""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_node = self.get_node_at_position(mouse_pos, width, height)
        
        # Check for controls button hover
        controls_button_rect = pygame.Rect(width - 140, height - 100, 120, 50)
        self.show_controls_tooltip = controls_button_rect.collidepoint(mouse_pos)
        
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back_to_campaign"
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_node:
                        return self._handle_node_selection(self.selected_node)
                # Arrow keys for panning
                elif event.key == pygame.K_LEFT:
                    self.pan_offset_x += 20
                elif event.key == pygame.K_RIGHT:
                    self.pan_offset_x -= 20
                elif event.key == pygame.K_UP:
                    self.pan_offset_y += 20
                elif event.key == pygame.K_DOWN:
                    self.pan_offset_y -= 20
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    clicked_node = self.get_node_at_position(event.pos, width, height)
                    if clicked_node:
                        return self._handle_node_selection(clicked_node)
                    
                    # Check for back button
                    back_button_rect = pygame.Rect(50, height - 100, 200, 50)
                    if back_button_rect.collidepoint(event.pos):
                        return "back_to_title"
                    
                    # Check for controls button
                    controls_button_rect = pygame.Rect(width - 140, height - 100, 120, 50)
                    if controls_button_rect.collidepoint(event.pos):
                        # Controls button clicked, don't start panning
                        pass
                    else:
                        # Start panning with left click if not clicking UI elements
                        self.is_panning = True
                        self.last_mouse_pos = event.pos
                    
                elif event.button == 3:  # Right click for panning
                    self.is_panning = True
                    self.last_mouse_pos = event.pos
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in [1, 3]:  # Stop panning
                    self.is_panning = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_panning:
                    # Calculate pan delta
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.pan_offset_x += dx
                    self.pan_offset_y += dy
                    self.last_mouse_pos = event.pos
            
            elif event.type == pygame.MOUSEWHEEL:
                # Mouse wheel scrolling for panning
                scroll_speed = 20
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    # Horizontal scroll with shift
                    self.pan_offset_x += event.y * scroll_speed
                else:
                    # Vertical scroll
                    self.pan_offset_y += event.y * scroll_speed
        
        return None
    
    def _handle_node_selection(self, node_id: str) -> Optional[str]:
        """Handle node selection with sewer-specific logic."""
        zone = self.map_state.get_current_zone()
        if not zone:
            return None
        
        node = zone.get_node(node_id)
        if not node:
            return None
        
        if not node.is_accessible or node.is_completed:
            return None
        
        if node.type == NodeType.SHOP:
            return "shop_blocked"
        elif node.type in [NodeType.LEVEL, NodeType.START, NodeType.BOSS]:
            self.map_state.move_to_node(node_id)
            return f"start_level:{node.level_file}"
        
        return None
    
    def draw(self, screen: pygame.Surface, width: int, height: int):
        """Draw the complete New Arkadia Sewerlines interface."""
        # Update animations
        dt = 1/60
        self.water_flow_offset += 40 * dt
        self.node_pulse_timer += dt
        self.pipe_steam_timer += dt
        self.algae_sway_timer += dt * 0.5
        
        # Cache stunning background
        if (self.background_surface is None or 
            self.background_width != width or 
            self.background_height != height):
            self.background_surface = self._create_stunning_sewer_background(width, height)
            self.background_width = width
            self.background_height = height
        
        # Draw cached background
        screen.blit(self.background_surface, (0, 0))
        
        # Spawn and update enhanced particles
        self._spawn_enhanced_particles(width, height)
        for particle in self.water_particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.water_particles.remove(particle)
        
        # Draw particles
        for particle in self.water_particles:
            particle.draw(screen)
        
        # Get current zone and draw map elements
        zone = self.map_state.get_current_zone()
        if not zone:
            return
        
        # Draw sewer pipe connections
        for node_id, node in zone.nodes.items():
            start_pos = self.get_node_screen_position(node, width, height)
            
            for connection_id in node.connections:
                connected_node = zone.get_node(connection_id)
                if connected_node:
                    end_pos = self.get_node_screen_position(connected_node, width, height)
                    is_accessible = connected_node.is_accessible
                    self._draw_sewer_connection_line(screen, start_pos, end_pos, is_accessible)
        
        # Draw sewer nodes
        current_node_id = zone.current_node_id
        for node_id, node in zone.nodes.items():
            position = self.get_node_screen_position(node, width, height)
            is_current = (node_id == current_node_id)
            is_selected = (node_id == self.selected_node)
            is_hovered = (node_id == self.hovered_node)
            
            self._draw_sewer_node(screen, node, position, is_current, is_selected, is_hovered)
        
        # Draw current position indicator
        if current_node_id:
            current_node = zone.get_node(current_node_id)
            if current_node:
                current_pos = self.get_node_screen_position(current_node, width, height)
                self._draw_current_position_indicator(screen, current_pos)
        
        # Draw enhanced UI elements
        self._draw_sewer_ui_elements(screen, width, height)
    
    def _draw_sewer_ui_elements(self, screen: pygame.Surface, width: int, height: int):
        """Draw sewer-themed UI elements."""
        # Zone title with sewer styling
        title_font = get_pixel_font(36)
        zone = self.map_state.get_current_zone()
        if zone:
            title_text = zone.name
            
            # Title background panel
            title_surface = title_font.render(title_text, True, TEXT_SEWER_WHITE)
            title_width = title_surface.get_width() + 40
            title_height = title_surface.get_height() + 20
            title_x = width // 2 - title_width // 2
            title_y = 20
            
            # Panel background with sewer styling
            panel_rect = pygame.Rect(title_x, title_y, title_width, title_height)
            pygame.draw.rect(screen, SEWER_PIPE_METAL, panel_rect)
            pygame.draw.rect(screen, SEWER_PIPE_RUST, panel_rect, 3)
            
            # Title text with glow
            text_x = title_x + 20
            text_y = title_y + 10
            
            # Text glow effect
            glow_surface = title_font.render(title_text, True, (*TEXT_SEWER_GREEN, 100))
            for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                screen.blit(glow_surface, (text_x + dx, text_y + dy))
            
            screen.blit(title_surface, (text_x, text_y))
        
        # Enhanced stats panel
        stats = self.map_state.get_player_stats()
        stats_font = get_pixel_font(18)
        
        # Stats background panel - made wider to fit text properly
        stats_panel = pygame.Rect(width - 280, 20, 260, 120)
        pygame.draw.rect(screen, SEWER_CONCRETE_OLD, stats_panel)
        pygame.draw.rect(screen, SEWER_PIPE_RUST, stats_panel, 2)
        
        # Currency with coin icon effect
        currency_text = f"Credits: {stats['currency']}"
        currency_surface = stats_font.render(currency_text, True, TEXT_SEWER_GREEN)
        screen.blit(currency_surface, (width - 270, 35))
        
        # Progress with visual bar
        progress = self.map_state.get_zone_progress()
        completed = progress.get('completed_nodes', 0)
        total = progress.get('total_nodes', 0)
        progress_text = f"Progress: {completed}/{total}"
        progress_surface = stats_font.render(progress_text, True, TEXT_SEWER_WHITE)
        screen.blit(progress_surface, (width - 270, 65))
        
        # Progress bar - adjusted to fit within new panel size
        if total > 0:
            bar_width = 240  # Fit within panel (260 width - 20 padding)
            bar_height = 8
            bar_x = width - 270  # 10 pixels from panel left edge
            bar_y = 90
            
            # Background bar
            pygame.draw.rect(screen, SEWER_GRIME, (bar_x, bar_y, bar_width, bar_height))
            # Progress fill
            fill_width = int((completed / total) * bar_width)
            pygame.draw.rect(screen, TEXT_SEWER_GREEN, (bar_x, bar_y, fill_width, bar_height))
            # Border
            pygame.draw.rect(screen, TEXT_SEWER_WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Levels completed
        levels_text = f"Levels: {stats['levels_completed']}"
        levels_surface = stats_font.render(levels_text, True, TEXT_SEWER_WHITE)
        screen.blit(levels_surface, (width - 270, 110))
        
        # Enhanced back button
        back_button_rect = pygame.Rect(50, height - 100, 200, 50)
        pygame.draw.rect(screen, SEWER_PIPE_METAL, back_button_rect)
        pygame.draw.rect(screen, SEWER_PIPE_RUST, back_button_rect, 3)
        
        # Button highlight on hover
        mouse_pos = pygame.mouse.get_pos()
        if back_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, TEXT_SEWER_YELLOW, back_button_rect, 2)
        
        button_font = get_pixel_font(14)  # Reduced font size for better fit
        button_text = button_font.render("Back to Title", True, TEXT_SEWER_WHITE)
        button_text_rect = button_text.get_rect(center=back_button_rect.center)
        screen.blit(button_text, button_text_rect)
        
        # Controls button - made wider to fit text properly
        controls_button_rect = pygame.Rect(width - 140, height - 100, 120, 50)
        pygame.draw.rect(screen, SEWER_PIPE_METAL, controls_button_rect)
        pygame.draw.rect(screen, SEWER_PIPE_RUST, controls_button_rect, 3)
        
        # Controls button highlight on hover
        if controls_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, TEXT_SEWER_YELLOW, controls_button_rect, 2)
        
        controls_button_text = button_font.render("Controls", True, TEXT_SEWER_WHITE)
        controls_text_rect = controls_button_text.get_rect(center=controls_button_rect.center)
        screen.blit(controls_button_text, controls_text_rect)
        
        # Controls tooltip (only show on hover)
        if self.show_controls_tooltip:
            instruction_font = get_pixel_font(14)
            instructions = [
                "Navigate the sewers to reach your destination",
                "Click accessible nodes to enter levels",
                "$ = Upgrade Station (Coming Soon)",
                "☠ = Dangerous Boss Battle Ahead",
                "ESC = Return to Campaign Menu",
                "",
                "Panning Controls:",
                "• Arrow Keys: Pan view",
                "• Mouse Wheel: Scroll vertically",
                "• Shift + Mouse Wheel: Scroll horizontally",
                "• Right Click + Drag: Pan with mouse"
            ]
            
            # Calculate tooltip dimensions to fit all text
            max_text_width = 0
            text_surfaces = []
            for instruction in instructions:
                if instruction:  # Skip empty lines for width calculation
                    text_surface = instruction_font.render(instruction, True, TEXT_SEWER_WHITE)
                    text_surfaces.append(text_surface)
                    max_text_width = max(max_text_width, text_surface.get_width())
                else:
                    text_surfaces.append(None)
            
            # Tooltip dimensions with proper padding
            tooltip_width = max_text_width + 30
            tooltip_height = len(instructions) * 22 + 20
            tooltip_x = width - tooltip_width - 10
            tooltip_y = height - 120 - tooltip_height
            
            # Tooltip background with proper coverage
            tooltip_panel = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
            pygame.draw.rect(screen, (*SEWER_BASE_DARK, 240), tooltip_panel)
            pygame.draw.rect(screen, SEWER_PIPE_RUST, tooltip_panel, 2)
            
            # Draw instructions with proper positioning
            for i, (instruction, text_surface) in enumerate(zip(instructions, text_surfaces)):
                if text_surface:  # Only draw non-empty lines
                    screen.blit(text_surface, (tooltip_x + 15, tooltip_y + 10 + i * 22))
    
    def display(self, screen: pygame.Surface, clock: pygame.time.Clock, 
               width: int, height: int, debug_console=None) -> str:
        """Main display loop for New Arkadia Sewerlines."""
        # Play zone-specific music
        zone = self.map_state.get_current_zone()
        if zone and zone.music_file and self.sound_manager:
            self.sound_manager.play_music(zone.music_file)
        
        while True:
            events = pygame.event.get()
            action = self.handle_input(events, width, height)
            
            if action:
                if action == "shop_blocked":
                    # Could show a popup here
                    print("Upgrade stations coming soon to New Arkadia!")
                    continue
                else:
                    return action
            
            self.draw(screen, width, height)
            
            if debug_console and debug_console.visible:
                debug_console.draw(screen, width, height)
            
            pygame.display.flip()
            clock.tick(60)