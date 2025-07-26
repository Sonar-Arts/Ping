"""
Ping Map Tree Menu Module
Visual interface for the roguelike map tree system.
"""

import pygame
import math
import time
import random
from typing import Optional, List, Tuple
from ....Core.Ping_MapState import get_map_state, MapStateManager
from ....Core.Ping_MapTree import NodeType, MapNode, MapZone
from ..UI.Ping_Fonts import get_pixel_font
from ..UI.Ping_Button import get_button

# Sewer-themed color palette
SEWER_DARK = (25, 35, 30)           # Base dark sewer
SEWER_WATER_DARK = (15, 45, 35)    # Dark murky water
SEWER_WATER_LIGHT = (25, 65, 50)   # Flowing water highlights
SEWER_PIPE_METAL = (85, 85, 90)    # Metal pipe color
SEWER_PIPE_RUST = (120, 80, 50)    # Rusty pipe details
SEWER_ALGAE = (40, 80, 45)         # Algae/overgrowth
SEWER_MOSS = (60, 100, 65)         # Moss highlights
SEWER_GRIME = (45, 50, 45)         # Grime and stains
SEWER_CONCRETE = (70, 75, 70)      # Concrete walls
SEWER_SLIME = (55, 90, 60)         # Slime accent

# Node colors
NODE_ACCESSIBLE = (150, 200, 150)   # Available to enter
NODE_COMPLETED = (100, 150, 255)    # Completed level
NODE_BLOCKED = (100, 100, 100)      # Not accessible yet
NODE_CURRENT = (255, 200, 100)      # Current position
NODE_SHOP = (200, 150, 255)         # Shop node
NODE_BOSS = (255, 100, 100)         # Boss node

# UI colors
TEXT_WHITE = (255, 255, 255)
TEXT_GREEN = (150, 255, 150)
TEXT_RED = (255, 150, 150)
TEXT_YELLOW = (255, 255, 150)

class WaterParticle:
    """Animated water droplet for sewer atmosphere."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-0.5, 0.5)
        self.vel_y = random.uniform(0.5, 2.0)
        self.life = random.uniform(2.0, 4.0)
        self.max_life = self.life
        self.size = random.randint(1, 3)
        
    def update(self, dt: float):
        self.x += self.vel_x * dt * 60
        self.y += self.vel_y * dt * 60
        self.life -= dt
        self.vel_y += 0.1 * dt  # Gravity
        
    def draw(self, screen: pygame.Surface):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            color = (*SEWER_WATER_LIGHT, min(255, alpha))
            
            # Create a temporary surface for alpha blending
            if self.size > 1:
                temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
                screen.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))
            else:
                screen.set_at((int(self.x), int(self.y)), color[:3])
                
    def is_alive(self) -> bool:
        return self.life > 0

class MapTreeMenu:
    """Main map tree menu interface."""
    
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.map_state: MapStateManager = get_map_state()
        
        # Visual effects
        self.water_particles: List[WaterParticle] = []
        self.last_particle_spawn = 0
        self.particle_spawn_interval = 0.3
        
        # Animation
        self.water_flow_offset = 0
        self.node_pulse_timer = 0
        
        # Selection
        self.selected_node: Optional[str] = None
        self.hovered_node: Optional[str] = None
        
        # Scrolling
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_speed = 20
        self.scroll_bounds = 200  # Maximum scroll distance
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        
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
    
    def _clamp_scroll(self):
        """Clamp scroll values within bounds."""
        self.scroll_x = max(-self.scroll_bounds, min(self.scroll_bounds, self.scroll_x))
        self.scroll_y = max(-self.scroll_bounds, min(self.scroll_bounds, self.scroll_y))
    
    def _create_sewer_background(self, width: int, height: int) -> pygame.Surface:
        """Create animated sewer background."""
        surface = pygame.Surface((width, height))
        
        # Base dark sewer
        surface.fill(SEWER_DARK)
        
        # Create flowing water channels
        water_channels = [
            (width * 0.2, height * 0.1, width * 0.6, height * 0.15),  # Top channel
            (width * 0.1, height * 0.4, width * 0.8, height * 0.2),   # Middle channel
            (width * 0.15, height * 0.7, width * 0.7, height * 0.15)  # Bottom channel
        ]
        
        for channel_x, channel_y, channel_w, channel_h in water_channels:
            # Dark water base
            water_rect = pygame.Rect(int(channel_x), int(channel_y), int(channel_w), int(channel_h))
            pygame.draw.rect(surface, SEWER_WATER_DARK, water_rect)
            
            # Flowing water highlights (animated)
            flow_offset = int(self.water_flow_offset) % 20
            for i in range(0, int(channel_w), 20):
                highlight_x = int(channel_x + i + flow_offset)
                if highlight_x < channel_x + channel_w:
                    highlight_rect = pygame.Rect(highlight_x, int(channel_y), 8, int(channel_h))
                    pygame.draw.rect(surface, SEWER_WATER_LIGHT, highlight_rect)
        
        # Add intersection pipes
        intersections = [
            (width * 0.3, height * 0.25, 40, 20),
            (width * 0.6, height * 0.45, 50, 25),
            (width * 0.4, height * 0.65, 35, 18)
        ]
        
        for pipe_x, pipe_y, pipe_w, pipe_h in intersections:
            pipe_rect = pygame.Rect(int(pipe_x), int(pipe_y), int(pipe_w), int(pipe_h))
            pygame.draw.rect(surface, SEWER_PIPE_METAL, pipe_rect)
            pygame.draw.rect(surface, SEWER_PIPE_RUST, pipe_rect, 2)
            
            # Pipe joints
            joint_size = 6
            pygame.draw.circle(surface, SEWER_PIPE_RUST, 
                             (int(pipe_x), int(pipe_y + pipe_h/2)), joint_size)
            pygame.draw.circle(surface, SEWER_PIPE_RUST, 
                             (int(pipe_x + pipe_w), int(pipe_y + pipe_h/2)), joint_size)
        
        # Add algae and overgrowth
        for _ in range(15):
            algae_x = random.randint(0, width)
            algae_y = random.randint(0, height)
            algae_size = random.randint(8, 20)
            
            # Moss patches
            pygame.draw.circle(surface, SEWER_ALGAE, (algae_x, algae_y), algae_size)
            pygame.draw.circle(surface, SEWER_MOSS, (algae_x - 2, algae_y - 2), algae_size // 2)
        
        # Add grime stains
        for _ in range(25):
            grime_x = random.randint(0, width)
            grime_y = random.randint(0, height)
            grime_w = random.randint(10, 30)
            grime_h = random.randint(5, 15)
            
            grime_rect = pygame.Rect(grime_x, grime_y, grime_w, grime_h)
            pygame.draw.ellipse(surface, SEWER_GRIME, grime_rect)
        
        return surface
    
    def _draw_connection_line(self, surface: pygame.Surface, start_pos: Tuple[int, int], 
                            end_pos: Tuple[int, int], is_accessible: bool):
        """Draw a sewer pipe connection between nodes."""
        color = SEWER_PIPE_METAL if is_accessible else SEWER_PIPE_RUST
        
        # Main pipe
        pygame.draw.line(surface, color, start_pos, end_pos, 6)
        
        # Pipe highlights
        highlight_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.line(surface, highlight_color, start_pos, end_pos, 2)
        
        # Joint connectors at ends
        pygame.draw.circle(surface, SEWER_PIPE_RUST, start_pos, 8)
        pygame.draw.circle(surface, SEWER_PIPE_RUST, end_pos, 8)
        pygame.draw.circle(surface, color, start_pos, 5)
        pygame.draw.circle(surface, color, end_pos, 5)
    
    def _draw_node(self, surface: pygame.Surface, node: MapNode, position: Tuple[int, int], 
                  is_current: bool, is_selected: bool, is_hovered: bool):
        """Draw a single map node."""
        x, y = position
        
        # Determine node color and size
        if is_current:
            color = NODE_CURRENT
            size = 25
        elif node.is_completed:
            color = NODE_COMPLETED
            size = 20
        elif node.is_accessible:
            color = NODE_ACCESSIBLE
            size = 22
        else:
            color = NODE_BLOCKED
            size = 18
        
        # Special colors for special node types
        if node.type == NodeType.SHOP:
            color = NODE_SHOP
        elif node.type == NodeType.BOSS:
            color = NODE_BOSS
            size = 28
        
        # Pulsing effect for current node
        if is_current:
            pulse = 1.0 + 0.3 * math.sin(self.node_pulse_timer * 3)
            size = int(size * pulse)
        
        # Selection/hover ring
        if is_selected or is_hovered:
            ring_color = TEXT_YELLOW if is_hovered else TEXT_WHITE
            pygame.draw.circle(surface, ring_color, (x, y), size + 8, 3)
        
        # Node shadow
        shadow_color = (0, 0, 0, 100)
        shadow_surface = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, shadow_color, (size + 2, size + 2), size)
        surface.blit(shadow_surface, (x - size - 2, y - size - 2))
        
        # Main node circle
        pygame.draw.circle(surface, color, (x, y), size)
        
        # Node highlight
        highlight_color = tuple(min(255, c + 60) for c in color)
        pygame.draw.circle(surface, highlight_color, (x - size//3, y - size//3), size//2)
        
        # Node type indicator
        if node.type == NodeType.SHOP:
            # Shop icon ($ symbol)
            font = get_pixel_font(16)
            text = font.render("$", True, TEXT_WHITE)
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)
        elif node.type == NodeType.BOSS:
            # Boss icon (skull symbol)
            font = get_pixel_font(18)
            text = font.render("☠", True, TEXT_WHITE)
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)
        elif node.is_completed:
            # Completed checkmark
            font = get_pixel_font(14)
            text = font.render("✓", True, TEXT_WHITE)
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)
    
    def _draw_current_position_arrow(self, surface: pygame.Surface, position: Tuple[int, int]):
        """Draw arrow pointing to current position."""
        x, y = position
        
        # Animated arrow above current node
        arrow_offset = 40 + int(10 * math.sin(self.node_pulse_timer * 2))
        arrow_y = y - arrow_offset
        
        # Arrow shape
        arrow_points = [
            (x, arrow_y),
            (x - 10, arrow_y - 15),
            (x - 5, arrow_y - 15),
            (x - 5, arrow_y - 25),
            (x + 5, arrow_y - 25),
            (x + 5, arrow_y - 15),
            (x + 10, arrow_y - 15)
        ]
        
        # Draw arrow shadow
        shadow_points = [(px + 2, py + 2) for px, py in arrow_points]
        pygame.draw.polygon(surface, (0, 0, 0, 100), shadow_points)
        
        # Draw main arrow
        pygame.draw.polygon(surface, TEXT_YELLOW, arrow_points)
        pygame.draw.polygon(surface, TEXT_WHITE, arrow_points, 2)
    
    def _spawn_water_particles(self, width: int, height: int):
        """Spawn atmospheric water particles."""
        current_time = time.time()
        if current_time - self.last_particle_spawn > self.particle_spawn_interval:
            if len(self.water_particles) < 20:
                # Spawn from pipe joints and intersections
                spawn_locations = [
                    (width * 0.3, height * 0.25),
                    (width * 0.6, height * 0.45),
                    (width * 0.4, height * 0.65),
                    (width * 0.2, height * 0.1),
                    (width * 0.8, height * 0.6)
                ]
                
                spawn_x, spawn_y = random.choice(spawn_locations)
                spawn_x += random.randint(-20, 20) + self.scroll_x // 2
                spawn_y += random.randint(-10, 10) + self.scroll_y // 2
                
                self.water_particles.append(WaterParticle(spawn_x, spawn_y))
            
            self.last_particle_spawn = current_time
    
    def _get_node_screen_position(self, node: MapNode, width: int, height: int) -> Tuple[int, int]:
        """Convert node logical position to screen coordinates with scrolling."""
        # Scale the node positions to fit the screen
        node_x, node_y = node.position
        
        # Map logical coordinates (0-800, 0-500) to screen coordinates
        screen_x = int((node_x / 800) * width) + self.scroll_x
        screen_y = int((node_y / 500) * height) + self.scroll_y
        
        return screen_x, screen_y
    
    def _get_node_at_position(self, pos: Tuple[int, int], width: int, height: int) -> Optional[str]:
        """Get the node ID at the given screen position."""
        zone = self.map_state.get_current_zone()
        if not zone:
            return None
        
        mouse_x, mouse_y = pos
        
        for node_id, node in zone.nodes.items():
            node_x, node_y = self._get_node_screen_position(node, width, height)
            distance = math.sqrt((mouse_x - node_x) ** 2 + (mouse_y - node_y) ** 2)
            
            # Node radius varies by type and state
            radius = 25 if node_id == zone.current_node_id else 22
            if node.type == NodeType.BOSS:
                radius = 28
            
            if distance <= radius:
                return node_id
        
        return None
    
    def handle_input(self, events: List[pygame.event.Event], width: int, height: int) -> Optional[str]:
        """Handle user input."""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_node = self._get_node_at_position(mouse_pos, width, height)
        
        # Handle mouse dragging for scrolling
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[2]:  # Right mouse button for dragging
            if not self.dragging:
                self.dragging = True
                self.last_mouse_pos = mouse_pos
            else:
                dx = mouse_pos[0] - self.last_mouse_pos[0]
                dy = mouse_pos[1] - self.last_mouse_pos[1]
                self.scroll_x += dx
                self.scroll_y += dy
                self._clamp_scroll()
                self.last_mouse_pos = mouse_pos
        else:
            self.dragging = False
        
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back_to_campaign"
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_node:
                        return self._handle_node_selection(self.selected_node)
                # Scrolling controls - use arrow keys and numpad for now
                elif event.key == pygame.K_LEFT:
                    self.scroll_x += self.scroll_speed
                    self._clamp_scroll()
                elif event.key == pygame.K_RIGHT:
                    self.scroll_x -= self.scroll_speed
                    self._clamp_scroll()
                elif event.key == pygame.K_UP:
                    self.scroll_y += self.scroll_speed
                    self._clamp_scroll()
                elif event.key == pygame.K_DOWN:
                    self.scroll_y -= self.scroll_speed
                    self._clamp_scroll()
                # Additional numpad keys for scrolling  
                elif event.key == pygame.K_KP4:  # Numpad 4
                    self.scroll_x += self.scroll_speed
                    self._clamp_scroll()
                elif event.key == pygame.K_KP6:  # Numpad 6
                    self.scroll_x -= self.scroll_speed
                    self._clamp_scroll()
                elif event.key == pygame.K_KP8:  # Numpad 8
                    self.scroll_y += self.scroll_speed
                    self._clamp_scroll()
                elif event.key == pygame.K_KP2:  # Numpad 2
                    self.scroll_y -= self.scroll_speed
                    self._clamp_scroll()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    clicked_node = self._get_node_at_position(event.pos, width, height)
                    if clicked_node:
                        return self._handle_node_selection(clicked_node)
                    
                    # Check for back button (bottom left)
                    back_button_rect = pygame.Rect(50, height - 100, 200, 50)
                    if back_button_rect.collidepoint(event.pos):
                        return "back_to_title"
                elif event.button == 4:  # Mouse wheel up
                    self.scroll_y += self.scroll_speed
                    self._clamp_scroll()
                elif event.button == 5:  # Mouse wheel down
                    self.scroll_y -= self.scroll_speed
                    self._clamp_scroll()
            
            elif event.type == pygame.MOUSEWHEEL:
                # Modern pygame mouse wheel support
                self.scroll_y += event.y * self.scroll_speed
                self._clamp_scroll()
        
        return None
    
    def _handle_node_selection(self, node_id: str) -> Optional[str]:
        """Handle when a node is selected."""
        zone = self.map_state.get_current_zone()
        if not zone:
            return None
        
        node = zone.get_node(node_id)
        if not node:
            return None
        
        # Check if node is accessible
        if not node.is_accessible or node.is_completed:
            # Play error sound or show message
            return None
        
        # Handle different node types
        if node.type == NodeType.SHOP:
            # Shop nodes are blocked for now
            return "shop_blocked"
        elif node.type in [NodeType.LEVEL, NodeType.START, NodeType.BOSS]:
            # Move to this node and start the level
            self.map_state.move_to_node(node_id)
            return f"start_level:{node.level_file}"
        
        return None
    
    def draw(self, screen: pygame.Surface, width: int, height: int):
        """Draw the complete map tree interface."""
        # Update animations
        dt = 1/60
        self.water_flow_offset += 30 * dt  # Flow animation speed
        self.node_pulse_timer += dt
        
        # Cache background if needed
        if (self.background_surface is None or 
            self.background_width != width or 
            self.background_height != height):
            self.background_surface = self._create_sewer_background(width, height)
            self.background_width = width
            self.background_height = height
        
        # Draw background with scrolling offset
        screen.blit(self.background_surface, (self.scroll_x // 2, self.scroll_y // 2))
        
        # Spawn and update water particles
        self._spawn_water_particles(width, height)
        for particle in self.water_particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.water_particles.remove(particle)
        
        # Draw particles
        for particle in self.water_particles:
            particle.draw(screen)
        
        # Get current zone
        zone = self.map_state.get_current_zone()
        if not zone:
            return
        
        # Draw connections between nodes
        for node_id, node in zone.nodes.items():
            start_pos = self._get_node_screen_position(node, width, height)
            
            for connection_id in node.connections:
                connected_node = zone.get_node(connection_id)
                if connected_node:
                    end_pos = self._get_node_screen_position(connected_node, width, height)
                    is_accessible = connected_node.is_accessible
                    self._draw_connection_line(screen, start_pos, end_pos, is_accessible)
        
        # Draw nodes
        current_node_id = zone.current_node_id
        for node_id, node in zone.nodes.items():
            position = self._get_node_screen_position(node, width, height)
            is_current = (node_id == current_node_id)
            is_selected = (node_id == self.selected_node)
            is_hovered = (node_id == self.hovered_node)
            
            self._draw_node(screen, node, position, is_current, is_selected, is_hovered)
        
        # Draw current position arrow
        if current_node_id:
            current_node = zone.get_node(current_node_id)
            if current_node:
                current_pos = self._get_node_screen_position(current_node, width, height)
                self._draw_current_position_arrow(screen, current_pos)
        
        # Draw UI elements
        self._draw_ui_elements(screen, width, height)
    
    def _draw_ui_elements(self, screen: pygame.Surface, width: int, height: int):
        """Draw UI elements like title, stats, and buttons."""
        # Zone title
        title_font = get_pixel_font(32)
        zone = self.map_state.get_current_zone()
        if zone:
            title_text = zone.name
            title_surface = title_font.render(title_text, True, TEXT_WHITE)
            title_x = width // 2 - title_surface.get_width() // 2
            title_y = 30
            
            # Title shadow
            shadow_surface = title_font.render(title_text, True, (0, 0, 0))
            screen.blit(shadow_surface, (title_x + 2, title_y + 2))
            screen.blit(title_surface, (title_x, title_y))
        
        # Player stats
        stats = self.map_state.get_player_stats()
        stats_font = get_pixel_font(18)
        
        # Currency display
        currency_text = f"Currency: {stats['currency']}"
        currency_surface = stats_font.render(currency_text, True, TEXT_GREEN)
        screen.blit(currency_surface, (width - 200, 30))
        
        # Progress display
        progress = self.map_state.get_zone_progress()
        progress_text = f"Progress: {progress.get('completed_nodes', 0)}/{progress.get('total_nodes', 0)}"
        progress_surface = stats_font.render(progress_text, True, TEXT_WHITE)
        screen.blit(progress_surface, (width - 200, 60))
        
        # Back to title button (bottom left)
        back_button_rect = pygame.Rect(50, height - 100, 200, 50)
        button_color = SEWER_PIPE_METAL
        pygame.draw.rect(screen, button_color, back_button_rect)
        pygame.draw.rect(screen, TEXT_WHITE, back_button_rect, 2)
        
        button_font = get_pixel_font(16)
        button_text = button_font.render("Back to Title", True, TEXT_WHITE)
        button_text_rect = button_text.get_rect(center=back_button_rect.center)
        screen.blit(button_text, button_text_rect)
        
        # Instructions
        instruction_font = get_pixel_font(14)
        instructions = [
            "Click on accessible nodes to enter levels",
            "$ = Shop (Coming Soon)",
            "☠ = Boss Battle",
            "Arrow Keys/Numpad = Scroll | Mouse Wheel = Vertical Scroll",
            "Right Click + Drag = Pan | ESC = Back to Campaign Menu"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_surface = instruction_font.render(instruction, True, TEXT_WHITE)
            screen.blit(instruction_surface, (50, height - 200 + i * 20))
    
    def display(self, screen: pygame.Surface, clock: pygame.time.Clock, 
               width: int, height: int, debug_console=None) -> str:
        """Main display loop for the map tree menu."""
        # Play zone music
        zone = self.map_state.get_current_zone()
        if zone and zone.music_file and self.sound_manager:
            self.sound_manager.play_music(zone.music_file)
        
        while True:
            events = pygame.event.get()
            action = self.handle_input(events, width, height)
            
            if action:
                if action == "shop_blocked":
                    # Show shop blocked message (could be a popup)
                    print("Shop coming soon!")
                    continue
                else:
                    return action
            
            self.draw(screen, width, height)
            
            if debug_console and debug_console.visible:
                debug_console.draw(screen, width, height)
            
            pygame.display.flip()
            clock.tick(60)