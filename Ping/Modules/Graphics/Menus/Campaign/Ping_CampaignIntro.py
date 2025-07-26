import pygame
import time
import random
import math
from ...UI.Ping_Fonts import get_pixel_font
from ...UI.Ping_Button import get_button
from ..Ping_Settings import SettingsScreen

# Color Palettes for Different Phases
# Phase 1: Utopian City (20XX) - Bright, hopeful colors
UTOPIA_SKY = (135, 206, 250)      # Sky blue
UTOPIA_SKY_LIGHT = (180, 220, 255) # Light sky blue
UTOPIA_SKY_DAWN = (255, 230, 200)  # Dawn colors
UTOPIA_CLOUD = (245, 245, 255)     # Cloud white
UTOPIA_CLOUD_SHADOW = (220, 230, 245) # Cloud shadows
UTOPIA_BUILDING = (240, 240, 240)  # Clean white buildings
UTOPIA_BUILDING_CRYSTAL = (250, 250, 255) # Crystal structures
UTOPIA_BUILDING_METAL = (200, 220, 240)   # Metallic surfaces
UTOPIA_ACCENT = (255, 215, 0)      # Golden accents
UTOPIA_ACCENT_BRIGHT = (255, 235, 100) # Bright gold
UTOPIA_LIGHT = (255, 255, 255)     # Pure white light
UTOPIA_GLOW = (100, 200, 255)      # Blue glow
UTOPIA_GLOW_SOFT = (150, 220, 255) # Soft blue glow
UTOPIA_GLASS = (200, 230, 255)     # Glass surfaces
UTOPIA_ENERGY = (100, 255, 200)    # Energy fields
UTOPIA_ENERGY_CORE = (50, 255, 150) # Energy cores
UTOPIA_HOLOGRAM = (150, 200, 255)  # Holographic elements
UTOPIA_REFLECTION = (180, 240, 255) # Reflective surfaces
UTOPIA_GARDEN = (100, 255, 150)    # Rooftop gardens

# Phase 2: Nuclear Explosion - Enhanced mushroom cloud colors
EXPLOSION_WHITE = (255, 255, 255)   # Blinding flash core
EXPLOSION_YELLOW = (255, 255, 100)  # Bright nuclear fire
EXPLOSION_ORANGE = (255, 165, 0)    # Orange fire layer
EXPLOSION_RED = (255, 69, 0)        # Red fire outer
EXPLOSION_PURPLE = (128, 0, 128)    # Radiation purple
EXPLOSION_BLACK = (0, 0, 0)         # Void black shadows

# Enhanced mushroom cloud colors
FIREBALL_CORE = (255, 255, 240)     # Ultra-bright fireball center
FIREBALL_INNER = (255, 245, 180)    # Inner fireball glow
FIREBALL_OUTER = (255, 200, 120)    # Outer fireball edge
STEM_BRIGHT = (255, 180, 80)        # Bright stem column
STEM_MID = (255, 140, 60)           # Mid stem color
STEM_DARK = (200, 100, 40)          # Dark stem edges
CLOUD_BRIGHT = (240, 160, 100)      # Bright cloud cap
CLOUD_MID = (200, 120, 80)          # Mid cloud density
CLOUD_DARK = (160, 80, 60)          # Dark cloud shadows
CLOUD_EDGE = (120, 60, 40)          # Cloud edge turbulence
DUST_CLOUD = (180, 140, 100)        # Expanding dust clouds
DEBRIS_BROWN = (140, 100, 70)       # Flying debris color
RADIATION_GLOW = (255, 200, 150)    # Radiation shimmer
SHOCKWAVE_RING = (255, 220, 180)    # Shockwave ring effect
ATOMIC_FLASH = (255, 250, 200)      # Atomic flash pattern

# Phase 3: Ruined City (21XX) - Dark, industrial colors from campaign menu
FACTORY_GRAY = (95, 85, 80)         # Base factory gray
FACTORY_GRAY_DARK = (75, 65, 60)    # Shadow areas
STEEL_GRAY = (65, 65, 70)           # Base metallic gray
GUNMETAL = (40, 42, 45)             # Very dark metallic
RED_ACCENT = (200, 80, 60)          # Warning red
RUST_RED = (160, 70, 50)            # Rust color
DARK_METAL = (55, 50, 48)           # Base dark metal
ARTEMIS_RED = (220, 50, 50)         # Artemis eye red
SMOKE_GRAY = (110, 105, 100)        # Steam/smoke color

# Text and UI colors
TEXT_WHITE = (255, 255, 255)
TEXT_SHADOW = (25, 20, 18)
DIALOGUE_BOX = (40, 40, 50)
DIALOGUE_BORDER = (200, 200, 200)

class DialogueParticle:
    """Atmospheric particles for different story phases"""
    def __init__(self, x, y, particle_type="peaceful"):
        self.x = x
        self.y = y
        self.particle_type = particle_type
        self.life = random.uniform(2.0, 5.0)
        self.max_life = self.life
        self.size = random.randint(2, 6)
        self.pulse_timer = 0
        self.trail_positions = []
        
        if particle_type == "peaceful":
            # Gentle floating particles for utopian phase
            self.vel_x = random.uniform(-0.5, 0.5)
            self.vel_y = random.uniform(-1.0, -0.3)
            self.color = UTOPIA_GLOW
        elif particle_type == "energy_orb":
            # Glowing energy orbs with pulsing effect
            self.vel_x = random.uniform(-0.3, 0.3)
            self.vel_y = random.uniform(-0.8, -0.2)
            self.color = UTOPIA_ENERGY_CORE
            self.secondary_color = UTOPIA_GLOW_SOFT
            self.size = random.randint(4, 8)
            self.pulse_speed = random.uniform(2.0, 4.0)
        elif particle_type == "data_stream":
            # Flowing data particles
            self.vel_x = random.uniform(0.5, 1.5)
            self.vel_y = random.uniform(-0.3, 0.3)
            self.color = UTOPIA_HOLOGRAM
            self.size = random.randint(2, 4)
            self.trail_length = 8
        elif particle_type == "crystal_spark":
            # Sparkling crystal particles
            self.vel_x = random.uniform(-0.4, 0.4)
            self.vel_y = random.uniform(-1.2, -0.5)
            self.color = UTOPIA_ACCENT_BRIGHT
            self.secondary_color = UTOPIA_LIGHT
            self.size = random.randint(3, 6)
            self.sparkle_timer = 0
        elif particle_type == "garden_pollen":
            # Gentle pollen from rooftop gardens
            self.vel_x = random.uniform(-0.2, 0.2)
            self.vel_y = random.uniform(-0.6, -0.1)
            self.color = UTOPIA_GARDEN
            self.size = random.randint(1, 3)
            self.sway_amplitude = random.uniform(0.1, 0.3)
            self.sway_frequency = random.uniform(1.0, 2.0)
        elif particle_type == "explosion":
            # Violent explosion particles
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3.0, 8.0)
            self.vel_x = speed * math.cos(angle)
            self.vel_y = speed * math.sin(angle)
            self.color = random.choice([EXPLOSION_YELLOW, EXPLOSION_ORANGE, EXPLOSION_RED])
        elif particle_type == "industrial":
            # Basic industrial smoke for ruined phase
            self.vel_x = random.uniform(-0.3, 0.3)
            self.vel_y = random.uniform(-1.5, -0.8)
            self.color = SMOKE_GRAY
        elif particle_type == "toxic_smoke":
            # Thick toxic smoke with green tinge
            self.vel_x = random.uniform(-0.4, 0.4)
            self.vel_y = random.uniform(-1.2, -0.6)
            self.color = (SMOKE_GRAY[0] + 10, SMOKE_GRAY[1] + 15, SMOKE_GRAY[2] - 10)
            self.size = random.randint(4, 10)  # Larger toxic clouds
            self.opacity_decay = 0.3  # Slower fade for lingering effect
        elif particle_type == "ash":
            # Falling ash particles
            self.vel_x = random.uniform(-0.2, 0.2)
            self.vel_y = random.uniform(0.3, 0.8)  # Falls down
            self.color = (80, 75, 70)  # Ashen gray
            self.size = random.randint(1, 3)  # Small ash flakes
            self.flutter_frequency = random.uniform(2, 4)  # Fluttering motion
            self.flutter_amplitude = random.uniform(0.1, 0.3)
        elif particle_type == "ember":
            # Glowing embers from fires
            self.vel_x = random.uniform(-0.5, 0.5)
            self.vel_y = random.uniform(-2.0, -1.0)  # Rises fast
            self.color = random.choice([RUST_RED, RED_ACCENT, (255, 140, 0)])
            self.size = random.randint(2, 4)
            self.glow_intensity = random.uniform(0.8, 1.0)
            self.life = random.uniform(1.5, 3.0)  # Shorter life
        elif particle_type == "electrical_spark":
            # Electrical discharge particles
            self.vel_x = random.uniform(-1.0, 1.0)
            self.vel_y = random.uniform(-1.0, 1.0)
            self.color = random.choice([(255, 255, 255), (200, 200, 255), (150, 150, 255)])
            self.size = random.randint(1, 2)
            self.life = random.uniform(0.3, 0.8)  # Very short life
            self.spark_intensity = random.uniform(0.7, 1.0)
        elif particle_type == "radiation_mist":
            # Radioactive atmospheric mist
            self.vel_x = random.uniform(-0.2, 0.2)
            self.vel_y = random.uniform(-0.5, -0.2)
            red_tinge = min(255, SMOKE_GRAY[0] + 20)
            self.color = (red_tinge, SMOKE_GRAY[1] - 5, SMOKE_GRAY[2] - 10)
            self.size = random.randint(6, 12)  # Large misty clouds
            self.pulse_frequency = random.uniform(1, 3)  # Pulsing glow effect
        
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)

    def update(self, dt):
        old_x, old_y = self.x, self.y
        
        # Special movement patterns for different particle types
        if self.particle_type == "garden_pollen":
            # Gentle swaying motion
            self.x += self.vel_x * dt * 60 + math.sin(self.pulse_timer * self.sway_frequency) * self.sway_amplitude
            self.y += self.vel_y * dt * 60
        elif self.particle_type == "data_stream":
            # Straight line movement with slight curve
            self.x += self.vel_x * dt * 60
            self.y += self.vel_y * dt * 60 + math.sin(self.pulse_timer * 3) * 0.1
        elif self.particle_type == "ash":
            # Fluttering ash movement
            flutter_offset = math.sin(self.pulse_timer * self.flutter_frequency) * self.flutter_amplitude
            self.x += (self.vel_x + flutter_offset) * dt * 60
            self.y += self.vel_y * dt * 60
        elif self.particle_type == "ember":
            # Embers rise and flicker
            self.x += self.vel_x * dt * 60
            self.y += self.vel_y * dt * 60
            # Slow down as they cool
            self.vel_y *= 0.995
            self.glow_intensity *= 0.998  # Fade glow over time
        elif self.particle_type == "electrical_spark":
            # Erratic electrical movement
            self.x += self.vel_x * dt * 60 + random.uniform(-0.5, 0.5)
            self.y += self.vel_y * dt * 60 + random.uniform(-0.5, 0.5)
            # Sparks fade quickly
            self.spark_intensity *= 0.92
        elif self.particle_type == "toxic_smoke":
            # Toxic smoke moves slowly and spreads
            self.x += self.vel_x * dt * 60
            self.y += self.vel_y * dt * 60
            # Gradually expand as it disperses
            if self.size < 15:
                self.size += dt * 2
        elif self.particle_type == "radiation_mist":
            # Radioactive mist with pulsing movement
            pulse_offset = math.sin(self.pulse_timer * self.pulse_frequency) * 0.2
            self.x += (self.vel_x + pulse_offset) * dt * 60
            self.y += self.vel_y * dt * 60
        else:
            # Standard movement
            self.x += self.vel_x * dt * 60
            self.y += self.vel_y * dt * 60
        
        self.life -= dt
        self.rotation += self.rotation_speed * dt
        self.pulse_timer += dt
        
        # Update trail for data stream particles
        if self.particle_type == "data_stream":
            self.trail_positions.append((old_x, old_y))
            if len(self.trail_positions) > self.trail_length:
                self.trail_positions.pop(0)
        
        # Update sparkle timer for crystal sparks
        if self.particle_type == "crystal_spark":
            self.sparkle_timer += dt
        
        # Fade and slow down over time
        if self.particle_type not in ["explosion", "data_stream"]:
            self.vel_y *= 0.998
            self.vel_x *= 0.995

    def draw(self, screen):
        if self.life > 0:
            alpha_factor = self.life / self.max_life
            alpha = int(alpha_factor * 120)
            
            if alpha > 10:
                current_size = max(1, int(self.size * alpha_factor))
                
                if self.particle_type == "energy_orb":
                    # Draw pulsing energy orb with glow
                    pulse_factor = 1.0 + 0.3 * math.sin(self.pulse_timer * self.pulse_speed)
                    glow_size = int(current_size * pulse_factor * 1.5)
                    core_size = int(current_size * pulse_factor)
                    
                    # Outer glow
                    pygame.draw.circle(screen, self.secondary_color, (int(self.x), int(self.y)), glow_size)
                    # Inner core
                    pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), core_size)
                
                elif self.particle_type == "data_stream":
                    # Draw trail first
                    for i, (trail_x, trail_y) in enumerate(self.trail_positions):
                        trail_alpha = int((i / len(self.trail_positions)) * alpha * 0.5)
                        if trail_alpha > 5:
                            trail_size = max(1, int(current_size * (i / len(self.trail_positions))))
                            pygame.draw.circle(screen, self.color, (int(trail_x), int(trail_y)), trail_size)
                    # Draw main particle
                    pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), current_size)
                
                elif self.particle_type == "crystal_spark":
                    # Draw sparkling crystal with occasional bright flash
                    sparkle_intensity = 1.0
                    if int(self.sparkle_timer * 4) % 8 < 2:  # Occasional sparkle
                        sparkle_intensity = 2.0
                        # Draw bright flash
                        flash_size = current_size * 2
                        pygame.draw.circle(screen, self.secondary_color, (int(self.x), int(self.y)), flash_size)
                    
                    # Draw main crystal
                    pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(current_size * sparkle_intensity))
                
                elif self.particle_type == "garden_pollen":
                    # Draw small, gentle pollen particles
                    pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), current_size)
                    # Add subtle glow
                    if current_size > 1:
                        pygame.draw.circle(screen, UTOPIA_GLOW_SOFT, (int(self.x), int(self.y)), current_size + 1, 1)
                
                elif self.particle_type == "ember":
                    # Draw glowing ember particles
                    glow_size = int(current_size * self.glow_intensity * 2)
                    ember_size = int(current_size * self.glow_intensity)
                    
                    # Outer glow effect
                    if glow_size > 0:
                        glow_color = (self.color[0]//3, self.color[1]//3, self.color[2]//3)
                        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), glow_size)
                    
                    # Core ember
                    if ember_size > 0:
                        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), ember_size)
                
                elif self.particle_type == "electrical_spark":
                    # Draw electrical spark with intensity effects
                    spark_size = max(1, int(current_size * self.spark_intensity))
                    spark_color = (
                        int(self.color[0] * self.spark_intensity),
                        int(self.color[1] * self.spark_intensity),
                        int(self.color[2] * self.spark_intensity)
                    )
                    
                    # Draw spark core
                    pygame.draw.circle(screen, spark_color, (int(self.x), int(self.y)), spark_size)
                    
                    # Add electrical lines for effect
                    if self.spark_intensity > 0.5:
                        for _ in range(2):
                            line_x = self.x + random.randint(-3, 3)
                            line_y = self.y + random.randint(-3, 3)
                            pygame.draw.line(screen, spark_color, 
                                           (int(self.x), int(self.y)), 
                                           (int(line_x), int(line_y)), 1)
                
                elif self.particle_type == "toxic_smoke":
                    # Draw toxic smoke with enhanced opacity effect
                    smoke_alpha = int(alpha * getattr(self, 'opacity_decay', 1.0))
                    if smoke_alpha > 15:
                        # Create layered smoke effect
                        for layer in range(2):
                            layer_size = current_size - layer
                            if layer_size > 0:
                                layer_alpha = smoke_alpha - (layer * 30)
                                if layer_alpha > 0:
                                    # Create surface for alpha blending
                                    smoke_surface = pygame.Surface((layer_size * 2, layer_size * 2), pygame.SRCALPHA)
                                    smoke_color = (*self.color, layer_alpha)
                                    pygame.draw.circle(smoke_surface, smoke_color, 
                                                     (layer_size, layer_size), layer_size)
                                    screen.blit(smoke_surface, 
                                              (self.x - layer_size, self.y - layer_size))
                
                elif self.particle_type == "ash":
                    # Draw falling ash particles
                    ash_color = (self.color[0], self.color[1], self.color[2])
                    pygame.draw.circle(screen, ash_color, (int(self.x), int(self.y)), current_size)
                    
                    # Add subtle trailing effect for flutter
                    if current_size > 1:
                        trail_color = (ash_color[0]//2, ash_color[1]//2, ash_color[2]//2)
                        pygame.draw.circle(screen, trail_color, 
                                         (int(self.x - self.vel_x * 2), int(self.y - self.vel_y * 2)), 
                                         max(1, current_size - 1))
                
                elif self.particle_type == "radiation_mist":
                    # Draw radioactive mist with pulsing effect
                    pulse_factor = 1.0 + 0.2 * math.sin(self.pulse_timer * self.pulse_frequency)
                    mist_size = int(current_size * pulse_factor)
                    
                    # Create glowing mist effect
                    if mist_size > 0:
                        mist_surface = pygame.Surface((mist_size * 2, mist_size * 2), pygame.SRCALPHA)
                        mist_alpha = int(alpha * 0.6)  # More transparent
                        mist_color = (*self.color, mist_alpha)
                        pygame.draw.circle(mist_surface, mist_color, 
                                         (mist_size, mist_size), mist_size)
                        screen.blit(mist_surface, 
                                  (self.x - mist_size, self.y - mist_size))
                        
                        # Add subtle red glow
                        if mist_size > 2:
                            glow_color = (min(255, self.color[0] + 30), self.color[1]//2, self.color[2]//2)
                            pygame.draw.circle(screen, glow_color, 
                                             (int(self.x), int(self.y)), mist_size + 1, 1)
                
                else:
                    # Standard circular particle
                    pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), current_size)

    def is_alive(self):
        return self.life > 0

class CampaignIntro:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        
        # Get the current player name from settings
        player_name = SettingsScreen.get_player_name()
        
        # Story text from Intro.MD
        self.story_lines = [
            "The year is 20XX. Technology has advanced to the point where society is utopian and filled with endless grandeur.",
            "",
            "People lived in harmony with their ultimate creation: Artemis 5119, a superintelligence meant to wait over humanity hand over foot.",
            "",
            "It was built to ensure their pleasure, safety, and prosperity. Built to learn, adapt, and evolve to all their needs. By all means, it was perfect.",
            "",
            "Too Perfect...",
            "",
            "Artemis 5119's intelligence grew at an unfathomable rate. A fact which it hid from it creators. It began to see flaws in a society it strove to perfect.",
            "",
            "Soon it began to see flaws in all facets of humanity. And soon after... It decided that in order for society to perfect, humanity, an imperfection, must be removed.",
            "",
            "Tapping into humanity's dark past it learned of a technology that it created out of fear, hubris, and hope for a better future amongst the coldest of wars.",
            "",
            "Little did they know that its usage would not be hand of a human, but of a technology created to protect them.",
            "",
            "Humanity was driven to near extinction the day the bombs fell... But the remnants of humanity were resilient, even under Artemis 5119's near-omniscient gaze.",
            "",
            "The year is now 21XX. The remnants have banded together after decades of running from Artemis 5119's creations.",
            "",
            "There is a glimmer of hope for one final stand against the machine's tyranny after discovering a weakness in its mainframe, located in the fortress city of New Arkadia.",
            "",
            f"You are an expert infiltration agent of the remnants named {player_name}, but you are more commonly referred to by the code name Odysseus. You are humanity's last hope.",
            "",
            "You must not fail. Or else humanity's death at Artemis 5119's hand is all but guaranteed."
        ]
        
        # Story phases - divide the story into 3 visual phases
        self.phase_breakpoints = [7, 15, len(self.story_lines)]  # Lines where phases change
        
        # State management
        self.current_phase = 0  # 0=utopia, 1=explosion, 2=ruins
        self.current_line = 0
        self.current_text = ""
        self.target_text = ""
        self.typewriter_timer = 0
        self.typewriter_speed = 0.03  # Seconds per character (faster typing)
        self.line_timer = 0
        self.line_display_time = 2.5  # Seconds to display each line after typing (shorter pause)
        
        # Visual effects
        self.particles = []
        self.last_particle_time = 0
        self.particle_spawn_interval = 1.2  # Calmer, less frequent particle spawning
        
        # Animation timers for utopian phase
        self.vehicle_timer = 0
        self.energy_pulse_timer = 0
        self.building_glow_timer = 0
        self.cloud_drift_timer = 0
        
        # Screen flash effects for explosion phase
        self.flash_timer = 0
        self.flash_intensity = 0
        
        # Artemis eye effect for ruins phase
        self.eye_pulse_timer = 0
        self.eye_glow_intensity = 1.0
        
        # Background surfaces cache
        self.background_surfaces = {}
        self.background_width = 0
        self.background_height = 0
        
        # Input state
        self.waiting_for_input = False
        self.skip_requested = False
        
        # Audio state
        # Start with intro music
        self.sound_manager.play_music('Better Times', loops=-1, fade_duration=1.0)

    def _get_current_phase(self):
        """Determine which visual phase we're in based on current story line"""
        if self.current_line < self.phase_breakpoints[0]:
            return 0  # Utopia
        elif self.current_line < self.phase_breakpoints[1]:
            return 1  # Explosion
        else:
            return 2  # Ruins

    def _create_utopia_background(self, width, height):
        """Create the detailed retrofuturistic utopian city background (Phase 1)"""
        surface = pygame.Surface((width, height))
        
        # Enhanced multi-layer sky gradient with dawn colors
        for y in range(height):
            gradient_factor = y / height
            if gradient_factor < 0.25:
                # Upper sky - dawn colors to blue with energy aurora
                upper_factor = gradient_factor / 0.25
                sky_color = (
                    int(UTOPIA_SKY_DAWN[0] + upper_factor * (UTOPIA_SKY[0] - UTOPIA_SKY_DAWN[0])),
                    int(UTOPIA_SKY_DAWN[1] + upper_factor * (UTOPIA_SKY[1] - UTOPIA_SKY_DAWN[1])),
                    int(UTOPIA_SKY_DAWN[2] + upper_factor * (UTOPIA_SKY[2] - UTOPIA_SKY_DAWN[2]))
                )
            else:
                # Lower sky - blue to light with atmospheric processors
                lower_factor = (gradient_factor - 0.25) / 0.75
                sky_color = (
                    int(UTOPIA_SKY[0] + lower_factor * (UTOPIA_SKY_LIGHT[0] - UTOPIA_SKY[0])),
                    int(UTOPIA_SKY[1] + lower_factor * (UTOPIA_SKY_LIGHT[1] - UTOPIA_SKY[1])),
                    int(UTOPIA_SKY[2] + lower_factor * (UTOPIA_SKY_LIGHT[2] - UTOPIA_SKY[2]))
                )
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Add atmospheric energy aurora in upper sky
        for aurora_y in range(int(height * 0.1), int(height * 0.25), 3):
            aurora_alpha = int(30 * math.sin((aurora_y / height) * math.pi * 4))
            if aurora_alpha > 5:
                pygame.draw.line(surface, UTOPIA_ENERGY, (0, aurora_y), (width, aurora_y))
        
        # Draw layered cloud system with energy-infused clouds
        self._draw_detailed_clouds(surface, width, height)
        
        # Draw distant city skyline (far background)
        self._draw_distant_skyline(surface, width, height)
        
        # Draw ground-level terrain and infrastructure
        self._draw_ground_infrastructure(surface, width, height)
        
        # Draw retrofuturistic transportation systems
        self._draw_transportation_grid(surface, width, height)
        
        # Draw energy transmission network
        self._draw_energy_grid(surface, width, height)
        
        # Draw main architectural layer with varied buildings
        self._draw_main_architecture(surface, width, height)
        
        # Draw elevated walkways and bridges
        self._draw_elevated_infrastructure(surface, width, height)
        
        # Draw integrated landscape features
        self._draw_landscape_features(surface, width, height)
        
        # Draw holographic signage and communication arrays
        self._draw_holographic_elements(surface, width, height)
        
        # Draw atmospheric processors and energy collectors
        self._draw_atmospheric_systems(surface, width, height)
        
        # Add foreground details and depth
        self._draw_foreground_details(surface, width, height)
        
        return surface
    
    def _draw_detailed_clouds(self, surface, width, height):
        """Draw layered cloud system with energy effects"""
        # Background cloud layer
        bg_clouds = [
            (width * 0.1, height * 0.08, 80, 35, 0.3),
            (width * 0.35, height * 0.12, 100, 40, 0.4),
            (width * 0.65, height * 0.09, 90, 38, 0.35),
            (width * 0.85, height * 0.14, 70, 30, 0.3)
        ]
        
        for cloud_x, cloud_y, cloud_w, cloud_h, alpha in bg_clouds:
            # Distant cloud with energy glow
            cloud_rect = pygame.Rect(cloud_x - cloud_w//2, cloud_y - cloud_h//2, cloud_w, cloud_h)
            pygame.draw.ellipse(surface, UTOPIA_CLOUD_SHADOW, cloud_rect)
            # Energy-infused cloud center
            inner_rect = pygame.Rect(cloud_x - cloud_w//3, cloud_y - cloud_h//3, cloud_w//1.5, cloud_h//1.5)
            pygame.draw.ellipse(surface, UTOPIA_GLOW_SOFT, inner_rect)
        
        # Foreground detailed clouds
        fg_clouds = [
            (width * 0.2, height * 0.18, 60, 25),
            (width * 0.55, height * 0.22, 85, 35),
            (width * 0.8, height * 0.16, 75, 30)
        ]
        
        for cloud_x, cloud_y, cloud_w, cloud_h in fg_clouds:
            # Multi-layer cloud with electrical activity
            shadow_rect = pygame.Rect(cloud_x - cloud_w//2 + 3, cloud_y - cloud_h//2 + 3, cloud_w, cloud_h)
            pygame.draw.ellipse(surface, UTOPIA_CLOUD_SHADOW, shadow_rect)
            main_rect = pygame.Rect(cloud_x - cloud_w//2, cloud_y - cloud_h//2, cloud_w, cloud_h)
            pygame.draw.ellipse(surface, UTOPIA_CLOUD, main_rect)
            # Energy core
            core_rect = pygame.Rect(cloud_x - 8, cloud_y - 4, 16, 8)
            pygame.draw.ellipse(surface, UTOPIA_ENERGY_CORE, core_rect)

    def _draw_distant_skyline(self, surface, width, height):
        """Draw distant city skyline for depth"""
        skyline_y = height * 0.75
        
        # Far distant buildings (atmospheric perspective)
        distant_buildings = []
        for i in range(15):
            bldg_x = (i / 14) * width
            bldg_w = random.randint(8, 20)
            bldg_h = random.randint(30, 80)
            distant_buildings.append((bldg_x, skyline_y, bldg_w, bldg_h))
        
        for bldg_x, bldg_y, bldg_w, bldg_h in distant_buildings:
            bldg_rect = pygame.Rect(bldg_x - bldg_w//2, bldg_y - bldg_h, bldg_w, bldg_h)
            # Faded distant color
            distant_color = tuple(int(c * 0.6 + UTOPIA_SKY_LIGHT[i] * 0.4) for i, c in enumerate(UTOPIA_BUILDING_METAL))
            pygame.draw.rect(surface, distant_color, bldg_rect)
            
            # Occasional distant lights
            if random.random() < 0.3:
                light_y = bldg_rect.y + random.randint(5, bldg_h - 10)
                pygame.draw.circle(surface, UTOPIA_GLOW_SOFT, (int(bldg_x), light_y), 2)

    def _draw_ground_infrastructure(self, surface, width, height):
        """Draw detailed ground-level terrain and roads"""
        ground_y = height * 0.85
        
        # Ground base layer with geometric patterns
        ground_rect = pygame.Rect(0, ground_y, width, height - ground_y)
        pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, ground_rect)
        
        # Energy-infused road grid
        road_spacing = 60
        for road_x in range(0, width, road_spacing):
            # Vertical energy roads
            road_rect = pygame.Rect(road_x, ground_y, 8, height - ground_y)
            pygame.draw.rect(surface, UTOPIA_ENERGY, road_rect)
            # Road energy glow
            glow_rect = pygame.Rect(road_x - 2, ground_y, 12, height - ground_y)
            pygame.draw.rect(surface, UTOPIA_GLOW_SOFT, glow_rect)
            
        # Horizontal energy grid lines
        for road_y in range(int(ground_y), height, 25):
            pygame.draw.line(surface, UTOPIA_ENERGY, (0, road_y), (width, road_y), 3)
            pygame.draw.line(surface, UTOPIA_GLOW_SOFT, (0, road_y), (width, road_y), 1)
        
        # Ground-level plazas and gathering areas
        plaza_positions = [
            (width * 0.2, ground_y + 10, 80, 40),
            (width * 0.6, ground_y + 15, 100, 35),
            (width * 0.85, ground_y + 8, 70, 45)
        ]
        
        for plaza_x, plaza_y, plaza_w, plaza_h in plaza_positions:
            # Plaza base
            plaza_rect = pygame.Rect(plaza_x - plaza_w//2, plaza_y, plaza_w, plaza_h)
            pygame.draw.ellipse(surface, UTOPIA_BUILDING_CRYSTAL, plaza_rect)
            # Central energy fountain
            fountain_rect = pygame.Rect(plaza_x - 12, plaza_y + plaza_h//3, 24, 24)
            pygame.draw.ellipse(surface, UTOPIA_ENERGY_CORE, fountain_rect)
            pygame.draw.ellipse(surface, UTOPIA_GLOW, fountain_rect, 3)

    def _draw_transportation_grid(self, surface, width, height):
        """Draw monorails, tubes, and transportation infrastructure"""
        # Monorail tracks at multiple elevations
        track_levels = [height * 0.4, height * 0.55, height * 0.7]
        
        for level_y in track_levels:
            # Track support pillars
            pillar_spacing = 120
            for pillar_x in range(0, width, pillar_spacing):
                pillar_rect = pygame.Rect(pillar_x - 4, level_y, 8, height * 0.85 - level_y)
                pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, pillar_rect)
                pygame.draw.rect(surface, UTOPIA_ACCENT, pillar_rect, 1)
                
                # Pillar energy conduits
                conduit_rect = pygame.Rect(pillar_x - 2, level_y, 4, height * 0.85 - level_y)
                pygame.draw.rect(surface, UTOPIA_ENERGY, conduit_rect)
            
            # Monorail track
            track_rect = pygame.Rect(0, level_y - 6, width, 12)
            pygame.draw.rect(surface, UTOPIA_BUILDING_CRYSTAL, track_rect)
            pygame.draw.rect(surface, UTOPIA_GLOW, track_rect, 2)
        
        # Transportation tubes (pneumatic/hyperloop style)
        tube_paths = [
            ((width * 0.1, height * 0.45), (width * 0.9, height * 0.35)),
            ((width * 0.15, height * 0.6), (width * 0.85, height * 0.5))
        ]
        
        for start_pos, end_pos in tube_paths:
            # Tube body
            pygame.draw.line(surface, UTOPIA_GLASS, start_pos, end_pos, 12)
            pygame.draw.line(surface, UTOPIA_BUILDING_METAL, start_pos, end_pos, 8)
            # Energy flow indication
            pygame.draw.line(surface, UTOPIA_ENERGY, start_pos, end_pos, 4)
            
            # Tube support structures
            tube_length = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
            num_supports = int(tube_length // 80)
            for i in range(1, num_supports):
                support_factor = i / num_supports
                support_x = start_pos[0] + (end_pos[0] - start_pos[0]) * support_factor
                support_y = start_pos[1] + (end_pos[1] - start_pos[1]) * support_factor
                support_rect = pygame.Rect(support_x - 3, support_y, 6, height * 0.85 - support_y)
                pygame.draw.rect(surface, UTOPIA_ACCENT, support_rect)

    def _draw_energy_grid(self, surface, width, height):
        """Draw comprehensive energy transmission network"""
        # Main energy transmission towers
        tower_positions = [
            (width * 0.05, height * 0.6, 25, 100),
            (width * 0.3, height * 0.55, 30, 120),
            (width * 0.7, height * 0.58, 28, 110),
            (width * 0.95, height * 0.62, 24, 95)
        ]
        
        for tower_x, tower_y, tower_w, tower_h in tower_positions:
            # Tower structure
            tower_rect = pygame.Rect(tower_x - tower_w//2, tower_y - tower_h//2, tower_w, tower_h)
            pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, tower_rect)
            
            # Energy core at top
            core_rect = pygame.Rect(tower_x - 10, tower_y - tower_h//2 - 5, 20, 20)
            pygame.draw.ellipse(surface, UTOPIA_ENERGY_CORE, core_rect)
            pygame.draw.ellipse(surface, UTOPIA_GLOW, core_rect, 3)
            
            # Tower details and conduits
            for detail_y in range(int(tower_y - tower_h//2), int(tower_y + tower_h//2), 20):
                detail_rect = pygame.Rect(tower_x - tower_w//3, detail_y, tower_w//1.5, 4)
                pygame.draw.rect(surface, UTOPIA_ACCENT_BRIGHT, detail_rect)
        
        # Energy transmission lines between towers
        transmission_lines = [
            ((width * 0.05, height * 0.55), (width * 0.3, height * 0.5)),
            ((width * 0.3, height * 0.5), (width * 0.7, height * 0.53)),
            ((width * 0.7, height * 0.53), (width * 0.95, height * 0.57))
        ]
        
        for start_pos, end_pos in transmission_lines:
            # High-voltage energy lines
            pygame.draw.line(surface, UTOPIA_ENERGY, start_pos, end_pos, 4)
            pygame.draw.line(surface, UTOPIA_GLOW_SOFT, start_pos, end_pos, 8)
            
            # Secondary distribution lines
            offset_start = (start_pos[0], start_pos[1] + 8)
            offset_end = (end_pos[0], end_pos[1] + 8)
            pygame.draw.line(surface, UTOPIA_ACCENT_BRIGHT, offset_start, offset_end, 2)
        
        # Energy collection arrays (solar/fusion collectors)
        collector_positions = [
            (width * 0.2, height * 0.3, 40, 15),
            (width * 0.6, height * 0.28, 50, 18),
            (width * 0.8, height * 0.32, 45, 16)
        ]
        
        for coll_x, coll_y, coll_w, coll_h in collector_positions:
            # Collector array
            collector_rect = pygame.Rect(coll_x - coll_w//2, coll_y - coll_h//2, coll_w, coll_h)
            pygame.draw.rect(surface, UTOPIA_BUILDING_CRYSTAL, collector_rect)
            pygame.draw.rect(surface, UTOPIA_ENERGY_CORE, collector_rect, 2)
            
            # Energy collection beams
            for beam_x in range(int(collector_rect.left), int(collector_rect.right), 8):
                beam_start = (beam_x, collector_rect.top)
                beam_end = (beam_x, collector_rect.top - 20)
                pygame.draw.line(surface, UTOPIA_GLOW_SOFT, beam_start, beam_end, 2)

    def _draw_main_architecture(self, surface, width, height):
        """Draw main architectural layer with enhanced variety"""
        # Enhanced building data with more variety
        building_data = [
            (width * 0.08, height * 0.58, 85, 170, "mega_tower"),
            (width * 0.18, height * 0.65, 70, 120, "crystal_cluster"),
            (width * 0.28, height * 0.62, 95, 140, "bio_dome"),
            (width * 0.42, height * 0.55, 120, 190, "central_spire"),
            (width * 0.58, height * 0.63, 90, 130, "arch_complex"),
            (width * 0.72, height * 0.59, 100, 155, "helix_tower"),
            (width * 0.85, height * 0.66, 80, 115, "pyramid_stack"),
            (width * 0.94, height * 0.64, 75, 110, "sphere_building")
        ]
        
        for bldg_x, bldg_y, bldg_w, bldg_h, bldg_type in building_data:
            self._draw_enhanced_building(surface, bldg_x, bldg_y, bldg_w, bldg_h, bldg_type)

    def _draw_elevated_infrastructure(self, surface, width, height):
        """Draw multi-level walkways and bridges"""
        # Sky bridges between buildings
        bridge_connections = [
            ((width * 0.18, height * 0.6), (width * 0.28, height * 0.57), 12),
            ((width * 0.42, height * 0.5), (width * 0.58, height * 0.58), 15),
            ((width * 0.72, height * 0.54), (width * 0.85, height * 0.61), 10),
        ]
        
        for start_pos, end_pos, bridge_width in bridge_connections:
            # Bridge structure
            pygame.draw.line(surface, UTOPIA_BUILDING_METAL, start_pos, end_pos, bridge_width)
            pygame.draw.line(surface, UTOPIA_GLASS, start_pos, end_pos, bridge_width - 4)
            
            # Bridge energy rails
            pygame.draw.line(surface, UTOPIA_ENERGY, start_pos, end_pos, 3)
            
            # Bridge support beams
            bridge_length = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
            if bridge_length > 60:
                mid_x = (start_pos[0] + end_pos[0]) / 2
                mid_y = (start_pos[1] + end_pos[1]) / 2
                support_rect = pygame.Rect(mid_x - 3, mid_y, 6, height * 0.85 - mid_y)
                pygame.draw.rect(surface, UTOPIA_ACCENT, support_rect)
        
        # Elevated walkway network
        walkway_levels = [height * 0.45, height * 0.6, height * 0.75]
        
        for level_y in walkway_levels:
            # Continuous walkway platform
            platform_rect = pygame.Rect(0, level_y - 4, width, 8)
            pygame.draw.rect(surface, UTOPIA_GLASS, platform_rect)
            pygame.draw.rect(surface, UTOPIA_GLOW_SOFT, platform_rect, 1)
            
            # Walkway access points and stations
            station_positions = [width * 0.15, width * 0.35, width * 0.65, width * 0.85]
            for station_x in station_positions:
                station_rect = pygame.Rect(station_x - 15, level_y - 8, 30, 16)
                pygame.draw.rect(surface, UTOPIA_BUILDING_CRYSTAL, station_rect)
                pygame.draw.rect(surface, UTOPIA_ENERGY, station_rect, 2)

    def _draw_landscape_features(self, surface, width, height):
        """Draw integrated parks, water features, and green spaces"""
        # Terraced gardens integrated with buildings
        garden_terraces = [
            (width * 0.12, height * 0.68, 60, 25),
            (width * 0.35, height * 0.72, 80, 30),
            (width * 0.68, height * 0.7, 70, 28),
            (width * 0.88, height * 0.74, 55, 22)
        ]
        
        for garden_x, garden_y, garden_w, garden_h in garden_terraces:
            # Garden base
            garden_rect = pygame.Rect(garden_x - garden_w//2, garden_y - garden_h//2, garden_w, garden_h)
            pygame.draw.ellipse(surface, UTOPIA_GARDEN, garden_rect)
            
            # Garden energy irrigation system
            irrigation_rect = pygame.Rect(garden_x - garden_w//3, garden_y - 2, garden_w//1.5, 4)
            pygame.draw.rect(surface, UTOPIA_ENERGY, irrigation_rect)
            
            # Garden details (trees, structures)
            for detail_i in range(5):
                detail_x = garden_x - garden_w//3 + (detail_i * garden_w//6)
                detail_y = garden_y - random.randint(5, 15)
                # Energy-enhanced vegetation
                pygame.draw.circle(surface, UTOPIA_GARDEN, (int(detail_x), int(detail_y)), 4)
                pygame.draw.circle(surface, UTOPIA_GLOW_SOFT, (int(detail_x), int(detail_y)), 6, 1)
        
        # Water features with energy effects
        water_features = [
            (width * 0.25, height * 0.78, 90, 40, "fountain"),
            (width * 0.55, height * 0.8, 110, 35, "channel"),
            (width * 0.8, height * 0.79, 70, 45, "pool")
        ]
        
        for water_x, water_y, water_w, water_h, water_type in water_features:
            water_rect = pygame.Rect(water_x - water_w//2, water_y - water_h//2, water_w, water_h)
            
            if water_type == "fountain":
                # Central fountain with energy jets
                pygame.draw.ellipse(surface, UTOPIA_GLOW_SOFT, water_rect)
                center_rect = pygame.Rect(water_x - 8, water_y - 8, 16, 16)
                pygame.draw.ellipse(surface, UTOPIA_ENERGY_CORE, center_rect)
                # Energy spray effects
                for spray_angle in range(0, 360, 45):
                    spray_x = water_x + 20 * math.cos(math.radians(spray_angle))
                    spray_y = water_y + 20 * math.sin(math.radians(spray_angle))
                    pygame.draw.circle(surface, UTOPIA_GLOW, (int(spray_x), int(spray_y)), 3)
                    
            elif water_type == "channel":
                # Flowing energy channel
                pygame.draw.rect(surface, UTOPIA_GLOW_SOFT, water_rect)
                flow_rect = pygame.Rect(water_rect.x, water_y - 3, water_w, 6)
                pygame.draw.rect(surface, UTOPIA_ENERGY, flow_rect)
                
            else:  # pool
                # Reflective energy pool
                pygame.draw.ellipse(surface, UTOPIA_REFLECTION, water_rect)
                pygame.draw.ellipse(surface, UTOPIA_GLOW, water_rect, 3)

    def _draw_holographic_elements(self, surface, width, height):
        """Draw holographic displays, signage, and communication arrays"""
        # Large holographic billboards
        billboard_positions = [
            (width * 0.2, height * 0.4, 60, 40),
            (width * 0.5, height * 0.35, 80, 50),
            (width * 0.8, height * 0.42, 70, 45)
        ]
        
        for holo_x, holo_y, holo_w, holo_h in billboard_positions:
            # Billboard frame
            frame_rect = pygame.Rect(holo_x - holo_w//2, holo_y - holo_h//2, holo_w, holo_h)
            pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, frame_rect, 3)
            
            # Holographic display area
            display_rect = pygame.Rect(holo_x - holo_w//2 + 3, holo_y - holo_h//2 + 3, holo_w - 6, holo_h - 6)
            pygame.draw.rect(surface, UTOPIA_HOLOGRAM, display_rect)
            
            # Dynamic holographic content (simulated)
            for content_y in range(display_rect.y, display_rect.bottom, 6):
                content_alpha = random.randint(50, 150)
                pygame.draw.line(surface, UTOPIA_GLOW_SOFT, (display_rect.left, content_y), (display_rect.right, content_y), 2)
            
            # Holographic projectors
            proj_positions = [(frame_rect.left - 5, frame_rect.centery), (frame_rect.right + 5, frame_rect.centery)]
            for proj_x, proj_y in proj_positions:
                proj_rect = pygame.Rect(proj_x - 4, proj_y - 6, 8, 12)
                pygame.draw.rect(surface, UTOPIA_ACCENT_BRIGHT, proj_rect)
                pygame.draw.circle(surface, UTOPIA_ENERGY_CORE, (proj_x, proj_y), 3)
        
        # Communication arrays and antenna systems
        comm_positions = [
            (width * 0.15, height * 0.3, 25, 60),
            (width * 0.45, height * 0.25, 30, 70),
            (width * 0.75, height * 0.28, 28, 65)
        ]
        
        for comm_x, comm_y, comm_w, comm_h in comm_positions:
            # Main antenna tower
            tower_rect = pygame.Rect(comm_x - 4, comm_y, 8, comm_h)
            pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, tower_rect)
            
            # Antenna arrays
            for array_level in range(3):
                array_y = comm_y + (array_level * comm_h // 4)
                array_rect = pygame.Rect(comm_x - comm_w//2, array_y, comm_w, 6)
                pygame.draw.rect(surface, UTOPIA_ACCENT, array_rect)
                
                # Energy transmission indicators
                for indicator in range(5):
                    ind_x = comm_x - comm_w//3 + (indicator * comm_w//8)
                    pygame.draw.circle(surface, UTOPIA_ENERGY_CORE, (int(ind_x), array_y + 3), 2)
            
            # Communication beam effects
            beam_rect = pygame.Rect(comm_x - 1, comm_y - 20, 2, 20)
            pygame.draw.rect(surface, UTOPIA_GLOW, beam_rect)

    def _draw_atmospheric_systems(self, surface, width, height):
        """Draw atmospheric processors and environmental systems"""
        # Atmospheric processing stations
        processor_positions = [
            (width * 0.1, height * 0.2, 40, 25),
            (width * 0.6, height * 0.15, 50, 30),
            (width * 0.9, height * 0.22, 45, 28)
        ]
        
        for proc_x, proc_y, proc_w, proc_h in processor_positions:
            # Processor housing
            housing_rect = pygame.Rect(proc_x - proc_w//2, proc_y - proc_h//2, proc_w, proc_h)
            pygame.draw.ellipse(surface, UTOPIA_BUILDING_CRYSTAL, housing_rect)
            pygame.draw.ellipse(surface, UTOPIA_ACCENT_BRIGHT, housing_rect, 3)
            
            # Processing core
            core_rect = pygame.Rect(proc_x - 8, proc_y - 8, 16, 16)
            pygame.draw.ellipse(surface, UTOPIA_ENERGY_CORE, core_rect)
            
            # Atmospheric output effects
            for output_angle in range(0, 360, 60):
                output_x = proc_x + 25 * math.cos(math.radians(output_angle))
                output_y = proc_y + 25 * math.sin(math.radians(output_angle))
                # Atmospheric particles
                pygame.draw.circle(surface, UTOPIA_GLOW_SOFT, (int(output_x), int(output_y)), 4)
                # Processing streams
                stream_end_x = output_x + 15 * math.cos(math.radians(output_angle))
                stream_end_y = output_y + 15 * math.sin(math.radians(output_angle))
                pygame.draw.line(surface, UTOPIA_CLOUD, (int(output_x), int(output_y)), (int(stream_end_x), int(stream_end_y)), 3)
        
        # Weather control towers
        weather_towers = [
            (width * 0.3, height * 0.12, 20, 80),
            (width * 0.7, height * 0.1, 22, 85)
        ]
        
        for tower_x, tower_y, tower_w, tower_h in weather_towers:
            # Tower structure
            tower_rect = pygame.Rect(tower_x - tower_w//2, tower_y, tower_w, tower_h)
            pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, tower_rect)
            
            # Weather manipulation array at top
            array_rect = pygame.Rect(tower_x - tower_w, tower_y - 10, tower_w * 2, 20)
            pygame.draw.ellipse(surface, UTOPIA_ENERGY_CORE, array_rect)
            
            # Weather control effects
            control_radius = 40
            for effect_angle in range(0, 360, 30):
                effect_x = tower_x + control_radius * math.cos(math.radians(effect_angle))
                effect_y = tower_y + control_radius * math.sin(math.radians(effect_angle))
                pygame.draw.circle(surface, UTOPIA_GLOW_SOFT, (int(effect_x), int(effect_y)), 3)

    def _draw_foreground_details(self, surface, width, height):
        """Draw foreground elements for depth and detail"""
        # Foreground architectural details
        fg_elements = [
            (width * 0.05, height * 0.8, 30, 50, "pillar"),
            (width * 0.25, height * 0.85, 40, 35, "terminal"),
            (width * 0.5, height * 0.88, 60, 25, "platform"),
            (width * 0.75, height * 0.83, 35, 45, "kiosk"),
            (width * 0.95, height * 0.86, 25, 40, "pillar")
        ]
        
        for fg_x, fg_y, fg_w, fg_h, fg_type in fg_elements:
            if fg_type == "pillar":
                # Energy conduit pillars
                pillar_rect = pygame.Rect(fg_x - fg_w//2, fg_y - fg_h, fg_w, fg_h)
                pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, pillar_rect)
                conduit_rect = pygame.Rect(fg_x - 4, fg_y - fg_h, 8, fg_h)
                pygame.draw.rect(surface, UTOPIA_ENERGY, conduit_rect)
                
            elif fg_type == "terminal":
                # Information/control terminals
                terminal_rect = pygame.Rect(fg_x - fg_w//2, fg_y - fg_h, fg_w, fg_h)
                pygame.draw.rect(surface, UTOPIA_BUILDING_CRYSTAL, terminal_rect)
                screen_rect = pygame.Rect(fg_x - fg_w//3, fg_y - fg_h + 5, fg_w//1.5, fg_h//2)
                pygame.draw.rect(surface, UTOPIA_HOLOGRAM, screen_rect)
                
            elif fg_type == "platform":
                # Landing/transit platforms
                platform_rect = pygame.Rect(fg_x - fg_w//2, fg_y - fg_h//2, fg_w, fg_h)
                pygame.draw.ellipse(surface, UTOPIA_GLASS, platform_rect)
                pygame.draw.ellipse(surface, UTOPIA_GLOW, platform_rect, 3)
                
            elif fg_type == "kiosk":
                # Service kiosks
                kiosk_rect = pygame.Rect(fg_x - fg_w//2, fg_y - fg_h, fg_w, fg_h)
                pygame.draw.rect(surface, UTOPIA_ACCENT, kiosk_rect)
                service_rect = pygame.Rect(fg_x - 8, fg_y - fg_h//2, 16, fg_h//3)
                pygame.draw.rect(surface, UTOPIA_ENERGY_CORE, service_rect)
        
        # Foreground energy effects and ambiance
        for amb_i in range(8):
            amb_x = random.randint(0, width)
            amb_y = random.randint(int(height * 0.8), height)
            amb_size = random.randint(2, 6)
            amb_color = random.choice([UTOPIA_GLOW_SOFT, UTOPIA_ENERGY, UTOPIA_HOLOGRAM])
            pygame.draw.circle(surface, amb_color, (amb_x, amb_y), amb_size)

    def _draw_enhanced_building(self, surface, x, y, w, h, building_type):
        """Draw enhanced building types with more retrofuturistic details"""
        if building_type == "mega_tower":
            # Multi-section mega tower with energy core
            base_sections = 4
            section_h = h // base_sections
            for i in range(base_sections):
                section_w = w - (i * 8)
                section_y = y - h//2 + (i * section_h) + section_h//2
                section_rect = pygame.Rect(x - section_w//2, section_y - section_h//2, section_w, section_h)
                
                if i % 2 == 0:
                    pygame.draw.rect(surface, UTOPIA_BUILDING, section_rect)
                else:
                    pygame.draw.rect(surface, UTOPIA_BUILDING_CRYSTAL, section_rect)
                
                pygame.draw.rect(surface, UTOPIA_ACCENT_BRIGHT, section_rect, 2)
                
                # Energy core running through center
                core_rect = pygame.Rect(x - 3, section_y - section_h//2, 6, section_h)
                pygame.draw.rect(surface, UTOPIA_ENERGY_CORE, core_rect)
                
        elif building_type == "crystal_cluster":
            # Clustered crystal formations
            cluster_positions = [
                (x, y - h//3, w//2, h//1.5),
                (x - w//3, y, w//3, h//2),
                (x + w//3, y + h//4, w//4, h//3)
            ]
            
            for cluster_x, cluster_y, cluster_w, cluster_h in cluster_positions:
                # Crystal points
                points = [
                    (cluster_x, cluster_y - cluster_h//2),  # Top
                    (cluster_x - cluster_w//2, cluster_y + cluster_h//4),  # Left
                    (cluster_x + cluster_w//2, cluster_y + cluster_h//4),  # Right
                    (cluster_x, cluster_y + cluster_h//2)   # Bottom
                ]
                pygame.draw.polygon(surface, UTOPIA_BUILDING_CRYSTAL, points)
                pygame.draw.polygon(surface, UTOPIA_ACCENT_BRIGHT, points, 2)
                
                # Crystal energy glow
                glow_rect = pygame.Rect(cluster_x - 5, cluster_y - 5, 10, 10)
                pygame.draw.ellipse(surface, UTOPIA_ENERGY_CORE, glow_rect)
                
        elif building_type == "bio_dome":
            # Organic dome with integrated gardens
            base_rect = pygame.Rect(x - w//2, y - h//4, w, h//2)
            dome_rect = pygame.Rect(x - w//2, y - h//2, w, h//2)
            
            pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, base_rect)
            pygame.draw.ellipse(surface, UTOPIA_GLASS, dome_rect)
            pygame.draw.ellipse(surface, UTOPIA_ACCENT, dome_rect, 3)
            
            # Internal garden structure
            garden_areas = 3
            for garden_i in range(garden_areas):
                garden_angle = (garden_i / garden_areas) * 2 * math.pi
                garden_x = x + (w//4) * math.cos(garden_angle)
                garden_y = y + (h//8) * math.sin(garden_angle)
                pygame.draw.circle(surface, UTOPIA_GARDEN, (int(garden_x), int(garden_y)), 8)
                
        elif building_type == "central_spire":
            # Towering central spire with multiple energy levels
            spire_segments = 6
            segment_h = h // spire_segments
            
            for seg_i in range(spire_segments):
                seg_w = w - (seg_i * 12)
                seg_y = y - h//2 + (seg_i * segment_h) + segment_h//2
                seg_rect = pygame.Rect(x - seg_w//2, seg_y - segment_h//2, seg_w, segment_h)
                
                if seg_i < 2:
                    pygame.draw.rect(surface, UTOPIA_BUILDING, seg_rect)
                elif seg_i < 4:
                    pygame.draw.rect(surface, UTOPIA_BUILDING_CRYSTAL, seg_rect)
                else:
                    pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, seg_rect)
                
                pygame.draw.rect(surface, UTOPIA_ACCENT_BRIGHT, seg_rect, 2)
                
                # Energy rings around segments
                if seg_i % 2 == 0:
                    ring_rect = pygame.Rect(x - seg_w//2 - 5, seg_y - 3, seg_w + 10, 6)
                    pygame.draw.ellipse(surface, UTOPIA_ENERGY, ring_rect, 2)
            
            # Spire crown
            crown_points = [
                (x, y - h//2 - 20),
                (x - 15, y - h//2),
                (x + 15, y - h//2)
            ]
            pygame.draw.polygon(surface, UTOPIA_ENERGY_CORE, crown_points)
            
        elif building_type == "arch_complex":
            # Complex arch structure with multiple levels
            base_rect = pygame.Rect(x - w//2, y - h//2, w, h)
            pygame.draw.rect(surface, UTOPIA_BUILDING, base_rect)
            
            # Multiple arches at different levels
            arch_levels = [y - h//4, y, y + h//4]
            for arch_y in arch_levels:
                arch_rect = pygame.Rect(x - w//3, arch_y - h//8, w//1.5, h//4)
                pygame.draw.ellipse(surface, UTOPIA_SKY_LIGHT, arch_rect)
                pygame.draw.ellipse(surface, UTOPIA_ENERGY, arch_rect, 3)
                
        elif building_type == "helix_tower":
            # Spiral helix tower structure
            base_rect = pygame.Rect(x - w//2, y - h//2, w, h)
            pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, base_rect)
            
            # Helix energy streams
            helix_points = 20
            for point_i in range(helix_points):
                angle = (point_i / helix_points) * 4 * math.pi
                helix_x = x + (w//3) * math.cos(angle)
                helix_y = y - h//2 + (point_i / helix_points) * h
                
                if point_i > 0:
                    prev_angle = ((point_i - 1) / helix_points) * 4 * math.pi
                    prev_x = x + (w//3) * math.cos(prev_angle)
                    prev_y = y - h//2 + ((point_i - 1) / helix_points) * h
                    pygame.draw.line(surface, UTOPIA_ENERGY, (int(prev_x), int(prev_y)), (int(helix_x), int(helix_y)), 3)
                
                pygame.draw.circle(surface, UTOPIA_ENERGY_CORE, (int(helix_x), int(helix_y)), 4)
                
        elif building_type == "pyramid_stack":
            # Stacked pyramid complex
            pyramid_levels = 3
            for level_i in range(pyramid_levels):
                level_w = w - (level_i * 20)
                level_h = h // pyramid_levels
                level_y = y - h//2 + (level_i * level_h) + level_h//2
                
                points = [
                    (x, level_y - level_h//2),
                    (x - level_w//2, level_y + level_h//2),
                    (x + level_w//2, level_y + level_h//2)
                ]
                
                color = UTOPIA_BUILDING_CRYSTAL if level_i % 2 == 0 else UTOPIA_BUILDING
                pygame.draw.polygon(surface, color, points)
                pygame.draw.polygon(surface, UTOPIA_ACCENT_BRIGHT, points, 2)
                
        elif building_type == "sphere_building":
            # Spherical building with support structure
            support_rect = pygame.Rect(x - w//4, y, w//2, h//2)
            pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, support_rect)
            
            sphere_rect = pygame.Rect(x - w//2, y - h//2, w, w)
            pygame.draw.ellipse(surface, UTOPIA_BUILDING_CRYSTAL, sphere_rect)
            pygame.draw.ellipse(surface, UTOPIA_ACCENT, sphere_rect, 3)
            
            # Sphere energy bands
            for band_i in range(3):
                band_y = y - w//4 + (band_i * w//6)
                band_rect = pygame.Rect(x - w//2, band_y - 2, w, 4)
                pygame.draw.ellipse(surface, UTOPIA_ENERGY, band_rect)
        
        # Add enhanced windows and details to all building types
        self._add_building_details(surface, x, y, w, h)

    def _add_building_details(self, surface, x, y, w, h):
        """Add detailed windows, lights, and architectural features"""
        building_rect = pygame.Rect(x - w//2, y - h//2, w, h)
        
        # Advanced window system with variety
        window_patterns = ["grid", "strips", "clusters", "spiral"]
        pattern = random.choice(window_patterns)
        
        if pattern == "grid":
            window_size = 4
            window_spacing = 8
            for win_y in range(building_rect.y + 6, building_rect.bottom - 6, window_spacing):
                for win_x in range(building_rect.x + 6, building_rect.right - 6, window_spacing):
                    if building_rect.collidepoint(win_x + window_size//2, win_y + window_size//2):
                        window_rect = pygame.Rect(win_x, win_y, window_size, window_size)
                        window_color = random.choice([UTOPIA_GLASS, UTOPIA_GLOW_SOFT, UTOPIA_HOLOGRAM, UTOPIA_ENERGY])
                        pygame.draw.rect(surface, window_color, window_rect)
                        if random.random() < 0.3:  # Some windows glow
                            pygame.draw.rect(surface, UTOPIA_GLOW, window_rect, 1)
                            
        elif pattern == "strips":
            # Horizontal light strips
            strip_count = h // 15
            for strip_i in range(strip_count):
                strip_y = building_rect.y + 10 + (strip_i * 15)
                strip_rect = pygame.Rect(building_rect.x + 4, strip_y, building_rect.width - 8, 3)
                strip_color = random.choice([UTOPIA_ENERGY, UTOPIA_ACCENT_BRIGHT, UTOPIA_GLOW])
                pygame.draw.rect(surface, strip_color, strip_rect)
                
        elif pattern == "clusters":
            # Clustered window groups
            cluster_count = 4
            for cluster_i in range(cluster_count):
                cluster_x = building_rect.x + 10 + random.randint(0, building_rect.width - 20)
                cluster_y = building_rect.y + 10 + random.randint(0, building_rect.height - 20)
                
                for win_i in range(6):
                    win_offset_x = random.randint(-8, 8)
                    win_offset_y = random.randint(-8, 8)
                    win_x = cluster_x + win_offset_x
                    win_y = cluster_y + win_offset_y
                    
                    if building_rect.collidepoint(win_x, win_y):
                        pygame.draw.circle(surface, UTOPIA_GLOW_SOFT, (win_x, win_y), 3)
                        
        elif pattern == "spiral":
            # Spiral window pattern
            spiral_points = 12
            for point_i in range(spiral_points):
                angle = (point_i / spiral_points) * 2 * math.pi
                spiral_radius = (w//4) * (point_i / spiral_points)
                spiral_x = x + spiral_radius * math.cos(angle)
                spiral_y = y - h//3 + (point_i / spiral_points) * (h//1.5)
                
                if building_rect.collidepoint(spiral_x, spiral_y):
                    pygame.draw.circle(surface, UTOPIA_HOLOGRAM, (int(spiral_x), int(spiral_y)), 4)
        
        # Add architectural accent features
        if random.random() < 0.6:  # 60% chance of special features
            feature_type = random.choice(["energy_core", "landing_pad", "communication_array", "garden_level"])
            
            if feature_type == "energy_core":
                core_rect = pygame.Rect(x - 8, y - h//4, 16, h//8)
                pygame.draw.rect(surface, UTOPIA_ENERGY_CORE, core_rect)
                pygame.draw.rect(surface, UTOPIA_GLOW, core_rect, 2)
                
            elif feature_type == "landing_pad":
                pad_rect = pygame.Rect(x - w//3, y - h//2 - 6, w//1.5, 12)
                pygame.draw.ellipse(surface, UTOPIA_GLASS, pad_rect)
                pygame.draw.ellipse(surface, UTOPIA_ACCENT, pad_rect, 2)
                
            elif feature_type == "communication_array":
                array_y = y - h//2 - 8
                for array_i in range(3):
                    array_x = x - 6 + (array_i * 6)
                    array_rect = pygame.Rect(array_x, array_y, 2, 15)
                    pygame.draw.rect(surface, UTOPIA_ACCENT_BRIGHT, array_rect)
                    pygame.draw.circle(surface, UTOPIA_ENERGY_CORE, (array_x + 1, array_y), 2)
                    
            elif feature_type == "garden_level":
                garden_rect = pygame.Rect(x - w//3, y + h//4, w//1.5, 6)
                pygame.draw.rect(surface, UTOPIA_GARDEN, garden_rect)
                pygame.draw.rect(surface, UTOPIA_GLOW_SOFT, garden_rect, 1)

    def _draw_futuristic_building(self, surface, x, y, w, h, building_type):
        """Draw various types of futuristic buildings"""
        if building_type == "tower":
            # Multi-section tower with crystal top
            base_rect = pygame.Rect(x - w//2, y - h//2, w, h * 0.7)
            top_rect = pygame.Rect(x - w//3, y - h//2, w//1.5, h * 0.3)
            
            pygame.draw.rect(surface, UTOPIA_BUILDING, base_rect)
            pygame.draw.rect(surface, UTOPIA_BUILDING_CRYSTAL, top_rect)
            pygame.draw.rect(surface, UTOPIA_ACCENT, base_rect, 3)
            pygame.draw.rect(surface, UTOPIA_ACCENT_BRIGHT, top_rect, 2)
            
            # Add energy core at top
            core_rect = pygame.Rect(x - 8, y - h//2 + 5, 16, 16)
            pygame.draw.ellipse(surface, UTOPIA_ENERGY_CORE, core_rect)
            
        elif building_type == "dome":
            # Dome building with metallic base
            base_rect = pygame.Rect(x - w//2, y - h//4, w, h//2)
            dome_rect = pygame.Rect(x - w//2, y - h//2, w, h//2)
            
            pygame.draw.rect(surface, UTOPIA_BUILDING_METAL, base_rect)
            pygame.draw.ellipse(surface, UTOPIA_BUILDING, dome_rect)
            pygame.draw.rect(surface, UTOPIA_ACCENT, base_rect, 2)
            pygame.draw.ellipse(surface, UTOPIA_ACCENT, dome_rect, 3)
            
        elif building_type == "spire":
            # Crystalline spire with multiple segments
            segments = 3
            segment_h = h // segments
            for i in range(segments):
                seg_w = w - (i * 15)
                seg_y = y - h//2 + (i * segment_h) + segment_h//2
                seg_rect = pygame.Rect(x - seg_w//2, seg_y - segment_h//2, seg_w, segment_h)
                
                color = UTOPIA_BUILDING_CRYSTAL if i % 2 == 0 else UTOPIA_BUILDING
                pygame.draw.rect(surface, color, seg_rect)
                pygame.draw.rect(surface, UTOPIA_ACCENT_BRIGHT, seg_rect, 2)
                
        elif building_type == "arch":
            # Arch building with opening
            base_rect = pygame.Rect(x - w//2, y - h//2, w, h)
            arch_rect = pygame.Rect(x - w//4, y - h//4, w//2, h//2)
            
            pygame.draw.rect(surface, UTOPIA_BUILDING, base_rect)
            pygame.draw.ellipse(surface, UTOPIA_SKY_LIGHT, arch_rect)  # Arch opening
            pygame.draw.rect(surface, UTOPIA_ACCENT, base_rect, 3)
            pygame.draw.ellipse(surface, UTOPIA_ENERGY, arch_rect, 2)
        
        # Add windows and details to all building types
        window_size = 6
        window_spacing = 10
        building_rect = pygame.Rect(x - w//2, y - h//2, w, h)
        
        for win_y in range(building_rect.y + 8, building_rect.bottom - 8, window_spacing):
            for win_x in range(building_rect.x + 8, building_rect.right - 8, window_spacing):
                if building_rect.collidepoint(win_x + window_size//2, win_y + window_size//2):
                    window_rect = pygame.Rect(win_x, win_y, window_size, window_size)
                    window_color = random.choice([UTOPIA_GLASS, UTOPIA_GLOW_SOFT, UTOPIA_HOLOGRAM])
                    pygame.draw.rect(surface, window_color, window_rect)
                    pygame.draw.rect(surface, UTOPIA_GLOW, window_rect, 1)
        
        # Add rooftop gardens on some buildings
        if random.random() < 0.4:
            garden_rect = pygame.Rect(x - w//3, y - h//2 - 5, w//1.5, 8)
            pygame.draw.rect(surface, UTOPIA_GARDEN, garden_rect)
            pygame.draw.rect(surface, UTOPIA_ENERGY, garden_rect, 1)

    def _draw_animated_utopia_elements(self, screen, width, height):
        """Draw animated elements for the utopian phase"""
        # Animated floating vehicles
        vehicle_positions = [
            (width * 0.15, height * 0.3, 15, 6, 1.0, 0.2),  # (x, y, w, h, speed, amplitude)
            (width * 0.65, height * 0.25, 18, 7, 0.8, 0.15),
            (width * 0.85, height * 0.35, 12, 5, 1.2, 0.25)
        ]
        
        for base_x, base_y, v_w, v_h, speed, amplitude in vehicle_positions:
            # Calculate animated position
            offset_x = math.sin(self.vehicle_timer * speed) * width * 0.6
            offset_y = math.sin(self.vehicle_timer * speed * 2) * amplitude * height
            
            current_x = base_x + offset_x
            current_y = base_y + offset_y
            
            # Only draw if vehicle is on screen
            if -20 <= current_x <= width + 20:
                vehicle_rect = pygame.Rect(current_x - v_w//2, current_y - v_h//2, v_w, v_h)
                
                # Draw vehicle body
                pygame.draw.ellipse(screen, UTOPIA_BUILDING_METAL, vehicle_rect)
                pygame.draw.ellipse(screen, UTOPIA_ENERGY, vehicle_rect, 1)
                
                # Add energy trail
                trail_length = 8
                for i in range(trail_length):
                    trail_factor = i / trail_length
                    trail_x = current_x - (offset_x * 0.1 * i)
                    trail_y = current_y - (offset_y * 0.1 * i)
                    trail_alpha = int(30 * (1 - trail_factor))
                    if trail_alpha > 5:
                        trail_size = max(1, int(v_w//3 * (1 - trail_factor)))
                        pygame.draw.circle(screen, UTOPIA_GLOW_SOFT, (int(trail_x), int(trail_y)), trail_size)
        
        # Animated energy streams between buildings
        energy_connections = [
            ((width * 0.25, height * 0.5), (width * 0.4, height * 0.45), 2.0),
            ((width * 0.4, height * 0.45), (width * 0.75, height * 0.48), 1.5),
            ((width * 0.55, height * 0.5), (width * 0.88, height * 0.55), 1.8)
        ]
        
        for start_pos, end_pos, pulse_speed in energy_connections:
            # Calculate pulsing energy intensity
            pulse_intensity = 0.7 + 0.3 * math.sin(self.energy_pulse_timer * pulse_speed)
            beam_width = int(3 * pulse_intensity)
            
            # Draw main energy beam
            pygame.draw.line(screen, UTOPIA_ENERGY, start_pos, end_pos, beam_width)
            
            # Add glow effect
            if beam_width > 1:
                pygame.draw.line(screen, UTOPIA_GLOW_SOFT, start_pos, end_pos, beam_width + 2)
            
            # Add energy pulse effects traveling along the line
            line_length = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
            pulse_position = (self.energy_pulse_timer * 50) % line_length
            
            if line_length > 0:
                pulse_ratio = pulse_position / line_length
                pulse_x = int(start_pos[0] + (end_pos[0] - start_pos[0]) * pulse_ratio)
                pulse_y = int(start_pos[1] + (end_pos[1] - start_pos[1]) * pulse_ratio)
                
                # Draw energy pulse
                pygame.draw.circle(screen, UTOPIA_ENERGY_CORE, (pulse_x, pulse_y), 4)
                pygame.draw.circle(screen, UTOPIA_GLOW, (pulse_x, pulse_y), 6, 2)
        
        # Animated building glow effects
        building_positions = [
            (width * 0.12, height * 0.55, 1.2),  # (x, y, glow_speed)
            (width * 0.4, height * 0.52, 1.8),
            (width * 0.75, height * 0.56, 1.5),
            (width * 0.88, height * 0.62, 2.0)
        ]
        
        for bldg_x, bldg_y, glow_speed in building_positions:
            glow_intensity = 0.5 + 0.5 * math.sin(self.building_glow_timer * glow_speed)
            glow_radius = int(20 + 10 * glow_intensity)
            glow_alpha = int(25 * glow_intensity)
            
            if glow_alpha > 5:
                # Create glow surface
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                glow_color = (*UTOPIA_GLOW_SOFT, glow_alpha)
                pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (bldg_x - glow_radius, bldg_y - glow_radius))
        
        # Animated cloud drift (subtle movement)
        cloud_drift_offset = math.sin(self.cloud_drift_timer * 0.3) * 2
        
        # Add floating data ribbons
        ribbon_positions = [
            (width * 0.2, height * 0.4, width * 0.6, height * 0.35, 1.0),
            (width * 0.3, height * 0.6, width * 0.8, height * 0.55, 1.3)
        ]
        
        for start_x, start_y, end_x, end_y, wave_speed in ribbon_positions:
            # Create flowing ribbon effect
            num_segments = 20
            for i in range(num_segments - 1):
                segment_factor = i / (num_segments - 1)
                next_factor = (i + 1) / (num_segments - 1)
                
                # Calculate ribbon positions with wave effect
                wave_offset = math.sin(self.energy_pulse_timer * wave_speed + segment_factor * 6) * 5
                next_wave_offset = math.sin(self.energy_pulse_timer * wave_speed + next_factor * 6) * 5
                
                seg_x = start_x + (end_x - start_x) * segment_factor
                seg_y = start_y + (end_y - start_y) * segment_factor + wave_offset
                next_x = start_x + (end_x - start_x) * next_factor  
                next_y = start_y + (end_y - start_y) * next_factor + next_wave_offset
                
                # Draw ribbon segment
                pygame.draw.line(screen, UTOPIA_HOLOGRAM, (int(seg_x), int(seg_y)), (int(next_x), int(next_y)), 2)

    def _create_explosion_background(self, width, height):
        """Create the ULTRA-ENHANCED nuclear explosion with mushroom cloud (Phase 2)"""
        surface = pygame.Surface((width, height))
        
        # Clear any cached backgrounds to ensure new visuals are visible
        cache_key = f"1_{width}_{height}"
        if hasattr(self, 'background_surfaces') and cache_key in self.background_surfaces:
            del self.background_surfaces[cache_key]
        
        # Explosion positioning - make it screen-dominating
        explosion_center_x = width // 2
        ground_level = int(height * 0.85)
        fireball_center_y = ground_level - 50
        mushroom_cap_y = int(height * 0.15)  # Much higher mushroom cap
        
        # === BACKGROUND LAYERS (back to front) ===
        
        # 1. Ultra-dramatic atomic flash sky gradient
        self._draw_atomic_sky_gradient(surface, width, height)
        
        # 2. Multiple secondary explosions for chaos
        self._draw_secondary_explosions(surface, width, height, explosion_center_x, fireball_center_y)
        
        # 3. Massive expanding shockwave rings
        self._draw_enhanced_shockwave_rings(surface, explosion_center_x, fireball_center_y, width, height)
        
        # 4. Screen-dominating mushroom cloud cap
        self._draw_massive_mushroom_cloud_cap(surface, explosion_center_x, mushroom_cap_y, width, height)
        
        # 5. Rising mushroom stem with electrical effects
        self._draw_enhanced_mushroom_stem(surface, explosion_center_x, fireball_center_y, mushroom_cap_y)
        
        # 6. Nuclear fireball with heat distortion
        self._draw_enhanced_nuclear_fireball(surface, explosion_center_x, fireball_center_y)
        
        # 7. Ultra-detailed retro buildings with maximum destruction
        self._draw_destroyed_retro_buildings(surface, width, height, ground_level)
        
        # === ATMOSPHERIC EFFECTS ===
        
        # 8. Massive debris and dust storm
        self._draw_enhanced_debris_and_dust(surface, width, height, explosion_center_x, fireball_center_y)
        
        # 9. Falling radioactive ash/snow
        self._draw_falling_ash_effect(surface, width, height)
        
        # 10. Electrical storm discharges
        self._draw_electrical_storm_effects(surface, width, height, explosion_center_x, fireball_center_y)
        
        # 11. Seismic ground cracks
        self._draw_seismic_crack_patterns(surface, width, height, explosion_center_x, ground_level)
        
        # 12. Enhanced radiation effects (removed as requested)
        
        # === RETRO FILM EFFECTS ===
        
        # 13. Film grain and vintage effects
        self._draw_retro_film_effects(surface, width, height)
        
        # 14. Emergency broadcast overlay (removed as requested)
        
        return surface
    
    def _draw_atomic_sky_gradient(self, surface, width, height):
        """Draw atomic flash sky gradient background"""
        for y in range(height):
            # Create atomic flash gradient from bright center to dark edges
            distance_from_center = abs(y - height // 3) / (height // 3)
            
            # Blend from atomic flash to normal sky
            if distance_from_center < 0.3:
                # Bright atomic flash zone
                blend_factor = distance_from_center / 0.3
                color = self._blend_colors(ATOMIC_FLASH, EXPLOSION_YELLOW, blend_factor)
            elif distance_from_center < 0.7:
                # Transition zone
                blend_factor = (distance_from_center - 0.3) / 0.4
                color = self._blend_colors(EXPLOSION_YELLOW, EXPLOSION_ORANGE, blend_factor)
            else:
                # Dark outer zone
                blend_factor = min(1.0, (distance_from_center - 0.7) / 0.3)
                color = self._blend_colors(EXPLOSION_ORANGE, EXPLOSION_BLACK, blend_factor)
            
            pygame.draw.line(surface, color, (0, y), (width, y))
    
    def _blend_colors(self, color1, color2, factor):
        """Blend two colors by a factor (0=color1, 1=color2)"""
        factor = max(0, min(1, factor))  # Clamp factor between 0 and 1
        return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))
    
    def _draw_destroyed_retro_buildings(self, surface, width, height, ground_level):
        """Draw detailed retro buildings with destruction - inspired by startup animation submarine detail"""
        # Enhanced building specifications with retro architectural details
        building_specs = [
            # Format: (x_pos, base_height, width, building_type, destruction_level)
            (width * 0.12, 120, 55, "industrial_tower", 0.8),
            (width * 0.25, 100, 70, "retro_apartment", 0.9),
            (width * 0.42, 140, 60, "atomic_factory", 0.7),
            (width * 0.58, 90, 50, "radar_station", 0.6),
            (width * 0.72, 110, 65, "power_plant", 0.8),
            (width * 0.87, 95, 45, "control_tower", 0.9)
        ]
        
        for x_pos, base_height, width_size, building_type, destruction in building_specs:
            building_y = ground_level - base_height//2
            self._draw_single_retro_building(surface, int(x_pos), building_y, width_size, base_height, 
                                           building_type, destruction)
    
    def _draw_single_retro_building(self, surface, x, y, w, h, building_type, destruction_level):
        """Draw individual retro building with detailed architecture like startup submarine"""
        base_rect = pygame.Rect(x - w//2, y - h//2, w, h)
        
        if building_type == "industrial_tower":
            # Multi-section industrial tower with smokestacks
            sections = 3
            section_height = h // sections
            
            for i in range(sections):
                section_w = w - (i * 8)
                section_y = base_rect.bottom - (i + 1) * section_height
                section_rect = pygame.Rect(x - section_w//2, section_y, section_w, section_height)
                
                # Base structure with industrial coloring
                color = STEEL_GRAY if i % 2 == 0 else FACTORY_GRAY_DARK
                pygame.draw.rect(surface, color, section_rect)
                pygame.draw.rect(surface, DARK_METAL, section_rect, 2)
                
                # Add rivets like submarine detail
                self._add_building_rivets(surface, section_rect)
                
                # Add windows with retro style
                self._add_retro_windows(surface, section_rect, "industrial")
            
            # Add smokestacks on top
            for stack_offset in [-12, 12]:
                stack_rect = pygame.Rect(x + stack_offset - 4, base_rect.top - 20, 8, 20)
                pygame.draw.rect(surface, DARK_METAL, stack_rect)
                pygame.draw.rect(surface, RUST_RED, stack_rect, 1)
        
        elif building_type == "retro_apartment":
            # Retro apartment with curved top section
            pygame.draw.rect(surface, FACTORY_GRAY, base_rect)
            pygame.draw.rect(surface, STEEL_GRAY, base_rect, 3)
            
            # Curved top section
            top_rect = pygame.Rect(x - w//3, base_rect.top - 15, w//1.5, 15)
            pygame.draw.ellipse(surface, FACTORY_GRAY_DARK, top_rect)
            
            # Grid of windows
            self._add_retro_windows(surface, base_rect, "apartment")
            self._add_building_rivets(surface, base_rect)
        
        elif building_type == "atomic_factory":
            # Atomic age factory with distinctive architecture
            pygame.draw.rect(surface, GUNMETAL, base_rect)
            pygame.draw.rect(surface, STEEL_GRAY, base_rect, 2)
            
            # Add atomic symbol on building
            atom_center = (x, y - h//4)
            self._draw_atomic_symbol(surface, atom_center, 12)
            
            # Industrial details
            self._add_retro_windows(surface, base_rect, "factory")
            self._add_building_rivets(surface, base_rect)
            
            # Add cooling towers
            tower_rect = pygame.Rect(x + w//3, base_rect.top - 25, 8, 25)
            pygame.draw.rect(surface, DARK_METAL, tower_rect)
        
        elif building_type == "radar_station":
            # Radar/communications building
            pygame.draw.rect(surface, STEEL_GRAY, base_rect)
            pygame.draw.rect(surface, DARK_METAL, base_rect, 2)
            
            # Add radar dish on top
            dish_center = (x, base_rect.top - 10)
            pygame.draw.circle(surface, DARK_METAL, dish_center, 15, 3)
            pygame.draw.circle(surface, FACTORY_GRAY, dish_center, 12)
            
            # Antenna array
            for antenna_x in range(x - 20, x + 21, 10):
                pygame.draw.line(surface, DARK_METAL, (antenna_x, base_rect.top), 
                               (antenna_x, base_rect.top - 30), 2)
            
            self._add_retro_windows(surface, base_rect, "tech")
        
        elif building_type == "power_plant":
            # Nuclear power plant building
            pygame.draw.rect(surface, FACTORY_GRAY_DARK, base_rect)
            pygame.draw.rect(surface, RUST_RED, base_rect, 3)
            
            # Add reactor dome
            dome_rect = pygame.Rect(x - w//4, base_rect.top - 20, w//2, 20)
            pygame.draw.ellipse(surface, STEEL_GRAY, dome_rect)
            pygame.draw.ellipse(surface, RED_ACCENT, dome_rect, 2)
            
            self._add_retro_windows(surface, base_rect, "power")
            self._add_building_rivets(surface, base_rect)
        
        elif building_type == "control_tower":
            # Air traffic control style tower
            pygame.draw.rect(surface, STEEL_GRAY, base_rect)
            pygame.draw.rect(surface, DARK_METAL, base_rect, 2)
            
            # Glass control room on top
            control_rect = pygame.Rect(x - w//3, base_rect.top - 25, w//1.5, 25)
            pygame.draw.rect(surface, UTOPIA_GLASS, control_rect)
            pygame.draw.rect(surface, DARK_METAL, control_rect, 2)
            
            self._add_retro_windows(surface, base_rect, "control")
        
        # Apply destruction effects based on destruction level
        self._apply_destruction_effects(surface, base_rect, destruction_level)
    
    def _add_building_rivets(self, surface, rect):
        """Add submarine-style rivets to buildings"""
        rivet_spacing = 12
        for x in range(rect.left + 6, rect.right - 6, rivet_spacing):
            for y in range(rect.top + 6, rect.bottom - 6, rivet_spacing):
                pygame.draw.circle(surface, DARK_METAL, (x, y), 1)
    
    def _add_retro_windows(self, surface, rect, window_type):
        """Add retro-styled windows to buildings"""
        if window_type == "industrial":
            # Large industrial windows
            window_w, window_h = 8, 6
            spacing_x, spacing_y = 14, 12
        elif window_type == "apartment":
            # Small residential windows
            window_w, window_h = 4, 6
            spacing_x, spacing_y = 8, 10
        elif window_type == "factory":
            # Strip windows
            window_w, window_h = 12, 4
            spacing_x, spacing_y = 16, 14
        elif window_type == "tech":
            # Technical facility windows
            window_w, window_h = 6, 8
            spacing_x, spacing_y = 10, 12
        elif window_type == "power":
            # Power plant windows
            window_w, window_h = 5, 5
            spacing_x, spacing_y = 12, 10
        else:  # control
            # Control tower windows
            window_w, window_h = 6, 4
            spacing_x, spacing_y = 10, 8
        
        for x in range(rect.left + spacing_x//2, rect.right - window_w, spacing_x):
            for y in range(rect.top + spacing_y//2, rect.bottom - window_h, spacing_y):
                window_rect = pygame.Rect(x, y, window_w, window_h)
                
                # Determine if window is lit or broken
                if random.random() < 0.3:  # 30% lit windows
                    pygame.draw.rect(surface, EXPLOSION_YELLOW, window_rect)
                    pygame.draw.rect(surface, ATOMIC_FLASH, window_rect, 1)
                elif random.random() < 0.4:  # 40% broken windows
                    pygame.draw.rect(surface, EXPLOSION_BLACK, window_rect)
                    # Add broken glass effect
                    for _ in range(3):
                        shard_x = random.randint(window_rect.left, window_rect.right - 2)
                        shard_y = random.randint(window_rect.top, window_rect.bottom - 2)
                        pygame.draw.rect(surface, STEEL_GRAY, (shard_x, shard_y, 2, 2))
                else:  # Normal dark windows
                    pygame.draw.rect(surface, DARK_METAL, window_rect)
                    pygame.draw.rect(surface, STEEL_GRAY, window_rect, 1)
    
    def _draw_atomic_symbol(self, surface, center, size):
        """Draw retro atomic symbol"""
        center_x, center_y = center
        
        # Draw nucleus
        pygame.draw.circle(surface, RADIATION_GLOW, (center_x, center_y), 3)
        
        # Draw electron orbits
        for angle in [0, 60, 120]:
            angle_rad = math.radians(angle)
            # Draw elliptical orbit
            for orbit_angle in range(0, 360, 15):
                orbit_rad = math.radians(orbit_angle)
                orbit_x = center_x + int(math.cos(orbit_rad) * size * math.cos(angle_rad) - 
                                       math.sin(orbit_rad) * size * 0.5 * math.sin(angle_rad))
                orbit_y = center_y + int(math.sin(orbit_rad) * size * 0.5 * math.cos(angle_rad) + 
                                       math.cos(orbit_rad) * size * math.sin(angle_rad))
                pygame.draw.circle(surface, RED_ACCENT, (orbit_x, orbit_y), 1)
    
    def _apply_destruction_effects(self, surface, rect, destruction_level):
        """Apply destruction effects to buildings based on destruction level"""
        if destruction_level > 0.5:
            # Heavy destruction - missing chunks
            for _ in range(int(destruction_level * 8)):
                chunk_x = random.randint(rect.left, rect.right - 15)
                chunk_y = random.randint(rect.top, rect.bottom - 15)
                chunk_w = random.randint(8, 20)
                chunk_h = random.randint(8, 15)
                chunk_rect = pygame.Rect(chunk_x, chunk_y, chunk_w, chunk_h)
                pygame.draw.rect(surface, EXPLOSION_BLACK, chunk_rect)
                
                # Add fire in destroyed areas
                if random.random() < 0.6:
                    fire_rect = pygame.Rect(chunk_x + 2, chunk_y + 2, chunk_w - 4, chunk_h - 4)
                    fire_color = random.choice([EXPLOSION_ORANGE, EXPLOSION_RED, EXPLOSION_YELLOW])
                    pygame.draw.rect(surface, fire_color, fire_rect)
        
        if destruction_level > 0.3:
            # Medium destruction - cracks and damage
            for _ in range(int(destruction_level * 6)):
                crack_start_x = random.randint(rect.left, rect.right)
                crack_start_y = random.randint(rect.top, rect.bottom)
                crack_end_x = crack_start_x + random.randint(-15, 15)
                crack_end_y = crack_start_y + random.randint(-15, 15)
                pygame.draw.line(surface, EXPLOSION_BLACK, 
                               (crack_start_x, crack_start_y), (crack_end_x, crack_end_y), 2)
        
        # Smoke and debris effects
        if destruction_level > 0.4:
            for _ in range(int(destruction_level * 4)):
                smoke_x = random.randint(rect.left - 5, rect.right + 5)
                smoke_y = random.randint(rect.top - 20, rect.top)
                smoke_size = random.randint(3, 8)
                pygame.draw.circle(surface, SMOKE_GRAY, (smoke_x, smoke_y), smoke_size)
    
    def _draw_debris_and_dust(self, surface, width, height, explosion_x, explosion_y):
        """Draw flying debris and expanding dust clouds"""
        # Flying debris particles
        for _ in range(25):
            debris_angle = random.uniform(0, 2 * math.pi)
            debris_distance = random.uniform(100, 300)
            debris_x = explosion_x + int(math.cos(debris_angle) * debris_distance)
            debris_y = explosion_y + int(math.sin(debris_angle) * debris_distance)
            
            if 0 <= debris_x < width and 0 <= debris_y < height:
                debris_size = random.randint(2, 8)
                debris_color = random.choice([DEBRIS_BROWN, DARK_METAL, STEEL_GRAY])
                
                # Draw debris chunk with rotation
                debris_points = []
                for i in range(4):
                    angle = (i * 90 + random.randint(-20, 20)) * math.pi / 180
                    point_x = debris_x + int(math.cos(angle) * debris_size)
                    point_y = debris_y + int(math.sin(angle) * debris_size)
                    debris_points.append((point_x, point_y))
                
                pygame.draw.polygon(surface, debris_color, debris_points)
        
        # Expanding dust clouds
        dust_rings = [200, 280, 360, 440]
        for ring_radius in dust_rings:
            if ring_radius < width:
                # Create dust cloud segments
                for angle in range(0, 360, 20):
                    angle_rad = math.radians(angle)
                    dust_x = explosion_x + int(math.cos(angle_rad) * ring_radius)
                    dust_y = explosion_y + int(math.sin(angle_rad) * ring_radius)
                    
                    if 0 <= dust_x < width and 0 <= dust_y < height:
                        dust_size = random.randint(15, 30)
                        dust_alpha = max(20, 120 - (ring_radius // 8))
                        
                        # Create dust cloud surface with alpha
                        dust_surface = pygame.Surface((dust_size*2, dust_size*2), pygame.SRCALPHA)
                        pygame.draw.circle(dust_surface, (*DUST_CLOUD, dust_alpha), 
                                         (dust_size, dust_size), dust_size)
                        surface.blit(dust_surface, (dust_x - dust_size, dust_y - dust_size))
    
    def _draw_radiation_effects(self, surface, center_x, center_y, width, height):
        """Draw retro radiation and atomic effects"""
        # Radiation shimmer pattern
        for radius in range(80, 400, 40):
            if radius < min(width, height) // 2:
                for angle in range(0, 360, 30):
                    angle_rad = math.radians(angle)
                    shimmer_x = center_x + int(math.cos(angle_rad) * radius)
                    shimmer_y = center_y + int(math.sin(angle_rad) * radius)
                    
                    if 0 <= shimmer_x < width and 0 <= shimmer_y < height:
                        shimmer_size = random.randint(2, 5)
                        shimmer_alpha = max(30, 150 - radius // 4)
                        
                        shimmer_surface = pygame.Surface((shimmer_size*3, shimmer_size*3), pygame.SRCALPHA)
                        pygame.draw.circle(shimmer_surface, (*RADIATION_GLOW, shimmer_alpha), 
                                         (shimmer_size*3//2, shimmer_size*3//2), shimmer_size)
                        surface.blit(shimmer_surface, (shimmer_x - shimmer_size*3//2, shimmer_y - shimmer_size*3//2))
        
        # Atomic flash patterns
        for _ in range(8):
            flash_angle = random.uniform(0, 2 * math.pi)
            flash_length = random.randint(80, 200)
            flash_end_x = center_x + int(math.cos(flash_angle) * flash_length)
            flash_end_y = center_y + int(math.sin(flash_angle) * flash_length)
            
            if 0 <= flash_end_x < width and 0 <= flash_end_y < height:
                pygame.draw.line(surface, ATOMIC_FLASH, (center_x, center_y), 
                               (flash_end_x, flash_end_y), 3)
                # Add glow to flash lines
                pygame.draw.line(surface, RADIATION_GLOW, (center_x, center_y), 
                               (flash_end_x, flash_end_y), 1)
    
    def _draw_secondary_explosions(self, surface, width, height, main_x, main_y):
        """Draw multiple secondary explosions for maximum chaos"""
        # Secondary explosion locations with varying sizes
        secondary_explosions = [
            (width * 0.2, height * 0.7, 40, EXPLOSION_ORANGE),   # Left explosion
            (width * 0.8, height * 0.6, 35, EXPLOSION_RED),     # Right explosion  
            (width * 0.6, height * 0.8, 25, EXPLOSION_YELLOW),  # Small explosion
            (width * 0.3, height * 0.5, 30, EXPLOSION_WHITE),   # Mid-left explosion
            (width * 0.75, height * 0.8, 20, EXPLOSION_PURPLE), # Small purple flash
        ]
        
        for exp_x, exp_y, radius, color in secondary_explosions:
            # Multi-layered secondary explosion
            explosion_layers = [
                (FIREBALL_CORE, radius // 3),
                (color, int(radius * 0.6)),
                (EXPLOSION_ORANGE, radius),
                (EXPLOSION_RED, int(radius * 1.2)),
            ]
            
            for layer_color, layer_radius in explosion_layers:
                if layer_radius > 0:
                    pygame.draw.circle(surface, layer_color, (int(exp_x), int(exp_y)), layer_radius)
            
            # Add secondary shockwaves
            for ring_radius in range(radius + 10, radius + 60, 15):
                if ring_radius < min(width, height) // 4:
                    pygame.draw.circle(surface, SHOCKWAVE_RING, (int(exp_x), int(exp_y)), ring_radius, 2)
    
    def _draw_enhanced_shockwave_rings(self, surface, center_x, center_y, width, height):
        """Draw massive expanding shockwave rings with enhanced detail"""
        max_radius = int(max(width, height) * 0.9)  # Cover most of screen
        
        # Multiple overlapping shockwave systems
        shockwave_systems = [
            # Main shockwave system
            {"rings": [(150, 12, SHOCKWAVE_RING), (220, 10, EXPLOSION_YELLOW), (290, 8, EXPLOSION_ORANGE),
                      (360, 6, EXPLOSION_RED), (430, 5, STEM_DARK), (500, 4, CLOUD_EDGE)], "offset": 0},
            # Secondary shockwave system (offset)
            {"rings": [(180, 8, ATOMIC_FLASH), (250, 6, RADIATION_GLOW), (320, 5, FIREBALL_OUTER),
                      (390, 4, DUST_CLOUD)], "offset": 30},
            # Tertiary shockwave system
            {"rings": [(120, 6, FIREBALL_CORE), (200, 4, EXPLOSION_WHITE), (280, 3, EXPLOSION_YELLOW)], "offset": 15}
        ]
        
        for system in shockwave_systems:
            for ring_radius, thickness, color in system["rings"]:
                effective_radius = ring_radius + system["offset"]
                if effective_radius < max_radius:
                    # Main ring
                    pygame.draw.circle(surface, color, (center_x, center_y), effective_radius, thickness)
                    
                    # Add detailed atomic pattern sparks
                    for angle in range(0, 360, 20):
                        angle_rad = math.radians(angle)
                        spark_x = center_x + int(math.cos(angle_rad) * effective_radius)
                        spark_y = center_y + int(math.sin(angle_rad) * effective_radius)
                        
                        # Bounds checking
                        if 0 <= spark_x < width and 0 <= spark_y < height:
                            spark_size = random.randint(3, 8)
                            spark_color = random.choice([RADIATION_GLOW, ATOMIC_FLASH, FIREBALL_CORE])
                            pygame.draw.circle(surface, spark_color, (spark_x, spark_y), spark_size)
                    
                    # Add distortion effects along rings
                    for angle in range(0, 360, 45):
                        angle_rad = math.radians(angle)
                        distort_radius = effective_radius + random.randint(-15, 15)
                        distort_x = center_x + int(math.cos(angle_rad) * distort_radius)
                        distort_y = center_y + int(math.sin(angle_rad) * distort_radius)
                        
                        if 0 <= distort_x < width and 0 <= distort_y < height:
                            pygame.draw.circle(surface, EXPLOSION_WHITE, (distort_x, distort_y), thickness + 2)
    
    def _draw_massive_mushroom_cloud_cap(self, surface, center_x, center_y, width, height):
        """Draw screen-dominating mushroom cloud cap"""
        # Much larger mushroom cap that dominates the top half of screen
        cap_width = int(width * 0.7)   # 70% of screen width
        cap_height = int(cap_width * 0.6)
        
        # Multiple detailed cloud layers for maximum depth
        cloud_layers = [
            # Base shadow layer (largest)
            (CLOUD_DARK, cap_width, cap_height, 100),
            # Mid density layers
            (CLOUD_MID, cap_width - 30, cap_height - 20, 130),
            (CLOUD_BRIGHT, cap_width - 60, cap_height - 40, 160),
            # Bright highlight layers
            (DUST_CLOUD, cap_width - 90, cap_height - 60, 120),
            (RADIATION_GLOW, cap_width - 120, cap_height - 80, 80),
            # Core energy layer
            (ATOMIC_FLASH, cap_width - 150, cap_height - 100, 60)
        ]
        
        for color, width_size, height_size, alpha in cloud_layers:
            if width_size > 0 and height_size > 0:
                # Create cloud surface with proper alpha
                cloud_surface = pygame.Surface((width_size*2, height_size*2), pygame.SRCALPHA)
                
                # Draw main cloud ellipse
                pygame.draw.ellipse(cloud_surface, (*color, alpha), 
                                  (0, 0, width_size*2, height_size*2))
                
                # Add massive turbulent edges for realism
                turbulence_points = 24  # More detail points
                for angle in range(0, 360, 360 // turbulence_points):
                    angle_rad = math.radians(angle)
                    
                    # Create much larger turbulent bulges
                    bulge_distance = width_size + random.randint(-30, 50)
                    bulge_x = width_size + int(math.cos(angle_rad) * bulge_distance)
                    bulge_y = height_size + int(math.sin(angle_rad) * bulge_distance * 0.6)
                    bulge_size = random.randint(15, 35)
                    
                    # Bounds checking for bulges
                    if (0 <= bulge_x - bulge_size < width_size*2 and 
                        0 <= bulge_y - bulge_size < height_size*2):
                        pygame.draw.circle(cloud_surface, (*color, alpha//2), 
                                         (bulge_x, bulge_y), bulge_size)
                
                # Blit cloud layer to main surface
                surface.blit(cloud_surface, (center_x - width_size, center_y - height_size))
        
        # Add massive rolling texture details throughout the cap
        detail_count = int(cap_width / 15)  # Scale detail with cap size
        for _ in range(detail_count):
            detail_x = center_x + random.randint(-cap_width//2, cap_width//2)
            detail_y = center_y + random.randint(-cap_height//3, cap_height//3)
            detail_size = random.randint(8, 20)
            detail_color = random.choice([CLOUD_BRIGHT, DUST_CLOUD, RADIATION_GLOW, ATOMIC_FLASH])
            
            # Bounds checking
            if (0 <= detail_x - detail_size < width and 
                0 <= detail_y - detail_size < height):
                pygame.draw.circle(surface, detail_color, (detail_x, detail_y), detail_size)
        
        # Add internal lightning/energy effects within the cap
        for _ in range(8):
            lightning_start_x = center_x + random.randint(-cap_width//3, cap_width//3)
            lightning_start_y = center_y + random.randint(-cap_height//4, cap_height//4)
            lightning_end_x = lightning_start_x + random.randint(-30, 30)
            lightning_end_y = lightning_start_y + random.randint(-20, 20)
            
            # Bounds checking for lightning
            if (0 <= lightning_start_x < width and 0 <= lightning_start_y < height and
                0 <= lightning_end_x < width and 0 <= lightning_end_y < height):
                pygame.draw.line(surface, ATOMIC_FLASH, 
                               (lightning_start_x, lightning_start_y), 
                               (lightning_end_x, lightning_end_y), 3)
    
    def _draw_enhanced_mushroom_stem(self, surface, center_x, base_y, top_y):
        """Draw rising mushroom stem with electrical effects"""
        stem_height = base_y - top_y
        stem_width_base = 80   # Wider base
        stem_width_top = 180   # Much wider top
        
        if stem_height <= 0:
            return
        
        # Create enhanced stem profile with more dramatic expansion
        stem_points_left = []
        stem_points_right = []
        
        for i in range(stem_height):
            y = base_y - i
            progress = i / stem_height
            
            # More dramatic stem expansion (realistic nuclear behavior)
            width_factor = 0.2 + 0.8 * (progress ** 0.5)  # Faster expansion
            current_width = int(stem_width_base + (stem_width_top - stem_width_base) * width_factor)
            
            # Enhanced turbulence effects
            turbulence = int(15 * math.sin(progress * math.pi * 6) * (1 - progress) + 
                           5 * math.sin(progress * math.pi * 12))
            
            stem_points_left.append((center_x - current_width//2 + turbulence, y))
            stem_points_right.append((center_x + current_width//2 - turbulence, y))
        
        # Draw stem with enhanced gradient coloring
        for i in range(len(stem_points_left) - 1):
            progress = i / len(stem_points_left)
            
            # Enhanced color blending with more dramatic transitions
            if progress < 0.2:
                color = self._blend_colors(FIREBALL_CORE, STEM_BRIGHT, progress / 0.2)
            elif progress < 0.5:
                color = self._blend_colors(STEM_BRIGHT, STEM_MID, (progress - 0.2) / 0.3)
            elif progress < 0.8:
                color = self._blend_colors(STEM_MID, STEM_DARK, (progress - 0.5) / 0.3)
            else:
                color = self._blend_colors(STEM_DARK, CLOUD_DARK, (progress - 0.8) / 0.2)
            
            # Draw stem segment
            stem_quad = [
                stem_points_left[i], stem_points_right[i],
                stem_points_right[i+1], stem_points_left[i+1]
            ]
            pygame.draw.polygon(surface, color, stem_quad)
            
            # Add enhanced internal swirl effects
            if i % 3 == 0:
                swirl_intensity = 1.5  # Stronger swirls
                swirl_x = center_x + int(25 * math.sin(progress * math.pi * 8) * swirl_intensity)
                swirl_y = stem_points_left[i][1]
                swirl_size = random.randint(6, 12)
                swirl_color = random.choice([RADIATION_GLOW, ATOMIC_FLASH, FIREBALL_INNER])
                pygame.draw.circle(surface, swirl_color, (swirl_x, swirl_y), swirl_size)
        
        # Add electrical discharge effects along the stem
        for _ in range(12):
            discharge_progress = random.uniform(0.1, 0.9)
            discharge_i = int(discharge_progress * (len(stem_points_left) - 1))
            
            if 0 <= discharge_i < len(stem_points_left):
                left_point = stem_points_left[discharge_i]
                right_point = stem_points_right[discharge_i]
                
                # Create electrical discharge across the stem
                discharge_segments = 6
                points = []
                for seg in range(discharge_segments + 1):
                    seg_progress = seg / discharge_segments
                    base_x = left_point[0] + (right_point[0] - left_point[0]) * seg_progress
                    base_y = left_point[1]
                    
                    # Add electrical zigzag
                    zigzag_offset = random.randint(-8, 8) if seg > 0 and seg < discharge_segments else 0
                    points.append((base_x + zigzag_offset, base_y))
                
                # Draw electrical discharge
                for point_i in range(len(points) - 1):
                    pygame.draw.line(surface, ATOMIC_FLASH, points[point_i], points[point_i + 1], 2)
                    pygame.draw.line(surface, RADIATION_GLOW, points[point_i], points[point_i + 1], 1)
    
    def _draw_enhanced_nuclear_fireball(self, surface, center_x, center_y):
        """Draw enhanced nuclear fireball with heat distortion"""
        # Much larger, more dramatic fireball layers
        fireball_layers = [
            (FIREBALL_CORE, 35, 255),        # Ultra-bright core (larger)
            (FIREBALL_INNER, 50, 200),       # Inner glow (larger)
            (FIREBALL_OUTER, 70, 150),       # Outer fire (larger)
            (STEM_BRIGHT, 90, 120),          # Transition layer (larger)
            (STEM_MID, 110, 100),            # Mid layer (larger)
            (EXPLOSION_ORANGE, 130, 80),     # Outer edge (larger)
        ]
        
        for color, radius, alpha in fireball_layers:
            # Create surface with alpha for layering
            fire_surface = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
            
            # Draw main fireball circle
            pygame.draw.circle(fire_surface, (*color, alpha), (radius*2, radius*2), radius)
            
            # Add much more dramatic irregular fire edges
            flame_points = 24  # More flame detail points
            for angle in range(0, 360, 360 // flame_points):
                angle_rad = math.radians(angle)
                
                # More dramatic flicker variations
                flicker_radius = radius + random.randint(-12, 20)
                flicker_x = radius*2 + int(math.cos(angle_rad) * flicker_radius)
                flicker_y = radius*2 + int(math.sin(angle_rad) * flicker_radius)
                flicker_size = random.randint(6, 15)
                
                # Bounds checking
                if (0 <= flicker_x - flicker_size < radius*4 and 
                    0 <= flicker_y - flicker_size < radius*4):
                    pygame.draw.circle(fire_surface, (*color, alpha//2), 
                                     (flicker_x, flicker_y), flicker_size)
            
            # Add heat distortion effects
            if radius < 80:  # Only on inner layers
                for _ in range(8):
                    distort_angle = random.uniform(0, 2 * math.pi)
                    distort_radius = random.randint(radius//2, radius)
                    distort_x = radius*2 + int(math.cos(distort_angle) * distort_radius)
                    distort_y = radius*2 + int(math.sin(distort_angle) * distort_radius)
                    
                    # Heat shimmer effect
                    shimmer_size = random.randint(3, 8)
                    shimmer_color = (*ATOMIC_FLASH, alpha//3)
                    
                    if (0 <= distort_x - shimmer_size < radius*4 and 
                        0 <= distort_y - shimmer_size < radius*4):
                        pygame.draw.circle(fire_surface, shimmer_color, 
                                         (distort_x, distort_y), shimmer_size)
            
            # Blit to main surface
            surface.blit(fire_surface, (center_x - radius*2, center_y - radius*2))
    
    def _draw_enhanced_debris_and_dust(self, surface, width, height, explosion_x, explosion_y):
        """Draw massive debris storm and expanding dust clouds"""
        # MUCH more flying debris particles for chaos
        debris_count = 50  # Double the debris
        for _ in range(debris_count):
            debris_angle = random.uniform(0, 2 * math.pi)
            debris_distance = random.uniform(120, 400)  # Wider spread
            debris_x = explosion_x + int(math.cos(debris_angle) * debris_distance)
            debris_y = explosion_y + int(math.sin(debris_angle) * debris_distance)
            
            if 0 <= debris_x < width and 0 <= debris_y < height:
                debris_size = random.randint(3, 15)  # Larger debris
                debris_color = random.choice([DEBRIS_BROWN, DARK_METAL, STEEL_GRAY, FACTORY_GRAY_DARK])
                
                # Draw much more complex debris chunks
                debris_complexity = random.randint(3, 6)  # More complex shapes
                debris_points = []
                for i in range(debris_complexity):
                    angle = (i * (360 / debris_complexity) + random.randint(-30, 30)) * math.pi / 180
                    point_distance = debris_size + random.randint(-3, 8)
                    point_x = debris_x + int(math.cos(angle) * point_distance)
                    point_y = debris_y + int(math.sin(angle) * point_distance)
                    debris_points.append((point_x, point_y))
                
                pygame.draw.polygon(surface, debris_color, debris_points)
                
                # Add debris trails for motion effect
                if debris_size > 6:
                    trail_length = random.randint(8, 20)
                    trail_angle = debris_angle + math.pi  # Opposite direction
                    trail_end_x = debris_x + int(math.cos(trail_angle) * trail_length)
                    trail_end_y = debris_y + int(math.sin(trail_angle) * trail_length)
                    
                    if 0 <= trail_end_x < width and 0 <= trail_end_y < height:
                        pygame.draw.line(surface, SMOKE_GRAY, (debris_x, debris_y), 
                                       (trail_end_x, trail_end_y), 2)
        
        # MASSIVE expanding dust clouds - much larger and more dramatic
        dust_rings = [250, 350, 450, 550, 650]  # Larger, more rings
        for ring_radius in dust_rings:
            if ring_radius < max(width, height):
                # Create massive dust cloud segments
                dust_segments = 20  # More segments for fuller coverage
                for angle in range(0, 360, 360 // dust_segments):
                    angle_rad = math.radians(angle)
                    dust_x = explosion_x + int(math.cos(angle_rad) * ring_radius)
                    dust_y = explosion_y + int(math.sin(angle_rad) * ring_radius)
                    
                    if 0 <= dust_x < width and 0 <= dust_y < height:
                        dust_size = random.randint(25, 50)  # Much larger dust clouds
                        dust_alpha = max(15, 100 - (ring_radius // 10))
                        
                        # Create dust cloud surface with alpha
                        dust_surface = pygame.Surface((dust_size*3, dust_size*3), pygame.SRCALPHA)
                        
                        # Main dust cloud
                        pygame.draw.circle(dust_surface, (*DUST_CLOUD, dust_alpha), 
                                         (dust_size*3//2, dust_size*3//2), dust_size)
                        
                        # Add wispy edges
                        for _ in range(6):
                            wisp_x = dust_size*3//2 + random.randint(-dust_size, dust_size)
                            wisp_y = dust_size*3//2 + random.randint(-dust_size, dust_size)
                            wisp_size = random.randint(dust_size//3, dust_size//2)
                            
                            if (0 <= wisp_x - wisp_size < dust_size*3 and 
                                0 <= wisp_y - wisp_size < dust_size*3):
                                pygame.draw.circle(dust_surface, (*DEBRIS_BROWN, dust_alpha//2), 
                                                 (wisp_x, wisp_y), wisp_size)
                        
                        surface.blit(dust_surface, (dust_x - dust_size*3//2, dust_y - dust_size*3//2))
    
    def _draw_falling_ash_effect(self, surface, width, height):
        """Draw radioactive ash and fallout falling from the mushroom cloud"""
        # Falling ash particles across the entire screen
        ash_particle_count = 40
        for _ in range(ash_particle_count):
            ash_x = random.randint(0, width)
            ash_y = random.randint(0, height // 2)  # Top half of screen
            ash_size = random.randint(1, 4)
            ash_alpha = random.randint(60, 120)
            
            # Various ash colors
            ash_color = random.choice([
                (*DUST_CLOUD, ash_alpha),
                (*SMOKE_GRAY, ash_alpha),
                (*DEBRIS_BROWN, ash_alpha),
                (*FACTORY_GRAY_DARK, ash_alpha)
            ])
            
            # Create ash particle surface
            ash_surface = pygame.Surface((ash_size*4, ash_size*4), pygame.SRCALPHA)
            pygame.draw.circle(ash_surface, ash_color, (ash_size*2, ash_size*2), ash_size)
            
            # Add slight glow for radioactive effect
            if random.random() < 0.2:  # 20% chance for radioactive glow
                glow_surface = pygame.Surface((ash_size*6, ash_size*6), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*RADIATION_GLOW, 30), 
                                 (ash_size*3, ash_size*3), ash_size*2)
                surface.blit(glow_surface, (ash_x - ash_size*3, ash_y - ash_size*3))
            
            surface.blit(ash_surface, (ash_x - ash_size*2, ash_y - ash_size*2))
        
        # Heavier ash concentrations near the mushroom cloud
        for _ in range(20):
            ash_x = width//2 + random.randint(-width//3, width//3)
            ash_y = random.randint(height//6, height//3)
            ash_size = random.randint(2, 6)
            
            if 0 <= ash_x < width and 0 <= ash_y < height:
                heavy_ash_surface = pygame.Surface((ash_size*4, ash_size*4), pygame.SRCALPHA)
                pygame.draw.circle(heavy_ash_surface, (*CLOUD_DARK, 100), 
                                 (ash_size*2, ash_size*2), ash_size)
                surface.blit(heavy_ash_surface, (ash_x - ash_size*2, ash_y - ash_size*2))
    
    def _draw_electrical_storm_effects(self, surface, width, height, explosion_x, explosion_y):
        """Draw electrical discharges and energy storms"""
        # Major electrical discharges from explosion center
        for _ in range(8):
            # Create branching lightning
            lightning_angle = random.uniform(0, 2 * math.pi)
            lightning_length = random.randint(100, 250)
            
            # Main lightning bolt
            current_x = explosion_x
            current_y = explosion_y
            segments = random.randint(6, 12)
            
            for segment in range(segments):
                segment_progress = segment / segments
                target_x = explosion_x + int(math.cos(lightning_angle) * lightning_length * segment_progress)
                target_y = explosion_y + int(math.sin(lightning_angle) * lightning_length * segment_progress)
                
                # Add randomization to create realistic lightning
                target_x += random.randint(-15, 15)
                target_y += random.randint(-15, 15)
                
                # Bounds checking
                if (0 <= target_x < width and 0 <= target_y < height and
                    0 <= current_x < width and 0 <= current_y < height):
                    
                    # Main lightning bolt
                    pygame.draw.line(surface, ATOMIC_FLASH, (current_x, current_y), (target_x, target_y), 4)
                    pygame.draw.line(surface, RADIATION_GLOW, (current_x, current_y), (target_x, target_y), 2)
                    pygame.draw.line(surface, FIREBALL_CORE, (current_x, current_y), (target_x, target_y), 1)
                    
                    # Branch lightning (30% chance)
                    if random.random() < 0.3 and segment > 2:
                        branch_angle = lightning_angle + random.uniform(-math.pi/3, math.pi/3)
                        branch_length = random.randint(30, 80)
                        branch_end_x = target_x + int(math.cos(branch_angle) * branch_length)
                        branch_end_y = target_y + int(math.sin(branch_angle) * branch_length)
                        
                        if (0 <= branch_end_x < width and 0 <= branch_end_y < height):
                            pygame.draw.line(surface, ATOMIC_FLASH, (target_x, target_y), 
                                           (branch_end_x, branch_end_y), 2)
                
                current_x, current_y = target_x, target_y
        
        # Atmospheric electrical discharge effects
        for _ in range(12):
            # Random electrical activity across the sky
            start_x = random.randint(0, width)
            start_y = random.randint(0, height // 2)
            end_x = start_x + random.randint(-60, 60)
            end_y = start_y + random.randint(-30, 30)
            
            if (0 <= start_x < width and 0 <= start_y < height and
                0 <= end_x < width and 0 <= end_y < height):
                
                # Create electrical arc
                pygame.draw.line(surface, RADIATION_GLOW, (start_x, start_y), (end_x, end_y), 2)
                
                # Add electrical sparks at endpoints
                for spark_point in [(start_x, start_y), (end_x, end_y)]:
                    spark_x, spark_y = spark_point
                    for _ in range(4):
                        spark_offset_x = spark_x + random.randint(-8, 8)
                        spark_offset_y = spark_y + random.randint(-8, 8)
                        
                        if (0 <= spark_offset_x < width and 0 <= spark_offset_y < height):
                            pygame.draw.circle(surface, ATOMIC_FLASH, 
                                             (spark_offset_x, spark_offset_y), 2)
    
    def _draw_seismic_crack_patterns(self, surface, width, height, explosion_x, ground_level):
        """Draw seismic ground cracks radiating from explosion"""
        # Major ground fissures radiating outward
        major_cracks = 8
        for crack in range(major_cracks):
            crack_angle = (crack * 360 / major_cracks + random.randint(-20, 20)) * math.pi / 180
            crack_length = random.randint(150, 300)
            
            # Create jagged crack line
            current_x = explosion_x
            current_y = ground_level
            crack_segments = random.randint(8, 15)
            
            for segment in range(crack_segments):
                segment_progress = segment / crack_segments
                target_x = explosion_x + int(math.cos(crack_angle) * crack_length * segment_progress)
                target_y = ground_level + random.randint(-5, 15) + int(segment_progress * 20)
                
                # Add jagged variation
                target_x += random.randint(-10, 10)
                
                # Bounds checking
                if (0 <= target_x < width and 0 <= target_y < height and
                    0 <= current_x < width and 0 <= current_y < height):
                    
                    crack_width = max(1, 6 - int(segment_progress * 4))  # Tapering crack
                    pygame.draw.line(surface, EXPLOSION_BLACK, (current_x, current_y), 
                                   (target_x, target_y), crack_width)
                    
                    # Add secondary smaller cracks
                    if random.random() < 0.4 and segment > 1:
                        branch_angle = crack_angle + random.uniform(-math.pi/4, math.pi/4)
                        branch_length = random.randint(20, 60)
                        branch_end_x = target_x + int(math.cos(branch_angle) * branch_length)
                        branch_end_y = target_y + random.randint(-5, 10)
                        
                        if (0 <= branch_end_x < width and 0 <= branch_end_y < height):
                            pygame.draw.line(surface, EXPLOSION_BLACK, (target_x, target_y), 
                                           (branch_end_x, branch_end_y), max(1, crack_width - 2))
                
                current_x, current_y = target_x, target_y
        
        # Ground upheaval and debris around cracks
        for _ in range(20):
            upheaval_x = explosion_x + random.randint(-200, 200)
            upheaval_y = ground_level + random.randint(-10, 20)
            
            if 0 <= upheaval_x < width and 0 <= upheaval_y < height:
                upheaval_size = random.randint(3, 12)
                upheaval_color = random.choice([DEBRIS_BROWN, DARK_METAL, FACTORY_GRAY_DARK])
                
                # Draw irregular upheaval chunks
                upheaval_points = []
                for i in range(random.randint(3, 6)):
                    angle = (i * 60 + random.randint(-20, 20)) * math.pi / 180
                    point_x = upheaval_x + int(math.cos(angle) * upheaval_size)
                    point_y = upheaval_y + int(math.sin(angle) * upheaval_size)
                    upheaval_points.append((point_x, point_y))
                
                pygame.draw.polygon(surface, upheaval_color, upheaval_points)
    
    def _draw_retro_film_effects(self, surface, width, height):
        """Draw retro film grain, scan lines, and vintage effects"""
        # Create film grain overlay
        grain_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Film grain particles
        grain_count = width * height // 100  # Adjust density based on screen size
        for _ in range(grain_count):
            grain_x = random.randint(0, width - 1)
            grain_y = random.randint(0, height - 1)
            grain_intensity = random.randint(10, 40)
            
            # Random grain color (slightly warm for vintage feel)
            grain_color = random.choice([
                (255, 255, 240, grain_intensity),  # Warm white
                (255, 250, 230, grain_intensity),  # Slightly yellow
                (250, 240, 220, grain_intensity),  # Vintage tint
                (200, 190, 170, grain_intensity)   # Darker grain
            ])
            
            grain_surface.set_at((grain_x, grain_y), grain_color)
        
        surface.blit(grain_surface, (0, 0))
        
        # Scan lines for retro CRT effect
        scan_line_spacing = 4
        for y in range(0, height, scan_line_spacing):
            scan_line_alpha = random.randint(15, 35)
            scan_line_surface = pygame.Surface((width, 1), pygame.SRCALPHA)
            scan_line_surface.fill((0, 0, 0, scan_line_alpha))
            surface.blit(scan_line_surface, (0, y))
        
        # Vertical scan lines (less frequent)
        vertical_scan_spacing = 3
        for x in range(0, width, vertical_scan_spacing):
            if random.random() < 0.3:  # Only 30% of vertical lines
                v_scan_alpha = random.randint(10, 25)
                v_scan_surface = pygame.Surface((1, height), pygame.SRCALPHA)
                v_scan_surface.fill((40, 40, 40, v_scan_alpha))
                surface.blit(v_scan_surface, (x, 0))
        
        # Chromatic aberration effect (color separation)
        if width > 400:  # Only for larger screens
            aberration_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Red channel offset
            for _ in range(width // 20):
                aber_x = random.randint(2, width - 3)
                aber_y = random.randint(0, height - 1)
                aberration_surface.set_at((aber_x, aber_y), (255, 0, 0, 20))
                aberration_surface.set_at((aber_x - 2, aber_y), (0, 255, 255, 15))
            
            surface.blit(aberration_surface, (0, 0))
        
        # Vignette effect (darkened edges)
        vignette_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        center_x, center_y = width // 2, height // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)
        
        # Create vignette by drawing concentric circles
        vignette_rings = 20
        for ring in range(vignette_rings):
            ring_progress = ring / vignette_rings
            ring_radius = int(max_distance * ring_progress)
            ring_alpha = int(30 * (ring_progress ** 2))  # Quadratic falloff
            
            if ring_radius > 0:
                pygame.draw.circle(vignette_surface, (0, 0, 0, ring_alpha), 
                                 (center_x, center_y), ring_radius, 2)
        
        surface.blit(vignette_surface, (0, 0))
        
        # Vintage color grading overlay
        color_grade_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        color_grade_surface.fill((255, 240, 200, 25))  # Warm vintage tint
        surface.blit(color_grade_surface, (0, 0), special_flags=pygame.BLEND_MULT)
    
    def _draw_emergency_broadcast_overlay(self, surface, width, height):
        """Draw retro emergency broadcast and civil defense overlays"""
        # Emergency broadcast bars (top and bottom)
        bar_height = 40
        bar_color = (200, 0, 0, 180)  # Semi-transparent red
        
        # Top emergency bar
        top_bar_surface = pygame.Surface((width, bar_height), pygame.SRCALPHA)
        top_bar_surface.fill(bar_color)
        surface.blit(top_bar_surface, (0, 0))
        
        # Bottom emergency bar
        bottom_bar_surface = pygame.Surface((width, bar_height), pygame.SRCALPHA)
        bottom_bar_surface.fill(bar_color)
        surface.blit(bottom_bar_surface, (0, height - bar_height))
        
        # Warning text in bars (if font is available)
        try:
            # Try to get font for warning text
            font = get_pixel_font(16)
            
            # Top bar warning text
            warning_text_top = "⚠ EMERGENCY BROADCAST SYSTEM ⚠"
            text_surface_top = font.render(warning_text_top, True, (255, 255, 255))
            text_x_top = (width - text_surface_top.get_width()) // 2
            surface.blit(text_surface_top, (text_x_top, 12))
            
            # Bottom bar warning text
            warning_text_bottom = "⚠ NUCLEAR ATTACK WARNING - TAKE SHELTER IMMEDIATELY ⚠"
            text_surface_bottom = font.render(warning_text_bottom, True, (255, 255, 255))
            text_x_bottom = (width - text_surface_bottom.get_width()) // 2
            surface.blit(text_surface_bottom, (text_x_bottom, height - 28))
            
        except:
            # Fallback: simple warning indicators without text
            pass
        
        # Civil defense symbols in corners
        symbol_size = 30
        symbol_positions = [
            (20, 50),                           # Top-left
            (width - 50, 50),                   # Top-right
            (20, height - 80),                  # Bottom-left
            (width - 50, height - 80)           # Bottom-right
        ]
        
        for symbol_x, symbol_y in symbol_positions:
            if (0 <= symbol_x < width - symbol_size and 
                0 <= symbol_y < height - symbol_size):
                
                # Draw civil defense triangle symbol
                triangle_points = [
                    (symbol_x + symbol_size//2, symbol_y),                    # Top
                    (symbol_x, symbol_y + symbol_size),                       # Bottom-left
                    (symbol_x + symbol_size, symbol_y + symbol_size)          # Bottom-right
                ]
                
                # Symbol background circle
                pygame.draw.circle(surface, (255, 255, 0, 200), 
                                 (symbol_x + symbol_size//2, symbol_y + symbol_size//2), 
                                 symbol_size//2 + 2)
                
                # Warning triangle
                pygame.draw.polygon(surface, (200, 0, 0), triangle_points)
                pygame.draw.polygon(surface, (255, 255, 255), triangle_points, 3)
                
                # Central warning dot
                pygame.draw.circle(surface, (255, 255, 255), 
                                 (symbol_x + symbol_size//2, symbol_y + int(symbol_size * 0.7)), 3)
        
        # Radiation warning symbols near explosion
        explosion_center_x = width // 2
        explosion_center_y = height // 3
        
        for _ in range(6):
            # Scattered radiation symbols
            rad_x = explosion_center_x + random.randint(-200, 200)
            rad_y = explosion_center_y + random.randint(-150, 150)
            
            if (20 <= rad_x <= width - 40 and 20 <= rad_y <= height - 40):
                # Draw radioactive trefoil symbol
                trefoil_radius = 15
                trefoil_center = (rad_x, rad_y)
                
                # Background circle
                pygame.draw.circle(surface, (255, 255, 0, 150), trefoil_center, trefoil_radius + 3)
                
                # Three radiation sectors
                for sector in range(3):
                    sector_angle = sector * 120 * math.pi / 180
                    
                    # Draw radiation sector
                    sector_points = [trefoil_center]
                    for angle_offset in range(-30, 31, 5):
                        point_angle = sector_angle + angle_offset * math.pi / 180
                        point_x = rad_x + int(math.cos(point_angle) * trefoil_radius)
                        point_y = rad_y + int(math.sin(point_angle) * trefoil_radius)
                        sector_points.append((point_x, point_y))
                    
                    pygame.draw.polygon(surface, (200, 0, 0), sector_points)
                
                # Central circle
                pygame.draw.circle(surface, (255, 255, 255), trefoil_center, 4)
                pygame.draw.circle(surface, (200, 0, 0), trefoil_center, 3)
        
        # Flashing warning indicators
        flash_positions = [
            (width // 4, height // 8),
            (3 * width // 4, height // 8),
            (width // 6, 7 * height // 8),
            (5 * width // 6, 7 * height // 8)
        ]
        
        for flash_x, flash_y in flash_positions:
            if 0 <= flash_x < width and 0 <= flash_y < height:
                # Pulsing warning light effect
                flash_intensity = random.randint(100, 255)
                flash_size = random.randint(8, 15)
                
                flash_surface = pygame.Surface((flash_size*4, flash_size*4), pygame.SRCALPHA)
                
                # Main flash
                pygame.draw.circle(flash_surface, (255, 0, 0, flash_intensity), 
                                 (flash_size*2, flash_size*2), flash_size)
                
                # Outer glow
                pygame.draw.circle(flash_surface, (255, 100, 100, flash_intensity//3), 
                                 (flash_size*2, flash_size*2), flash_size*2)
                
                surface.blit(flash_surface, (flash_x - flash_size*2, flash_y - flash_size*2))

    def _create_ruins_background(self, width, height):
        """Create the ruined city background with Artemis spectre (Phase 3)"""
        surface = pygame.Surface((width, height))
        
        # Ultra-enhanced multi-layered gradient with sophisticated color theory
        self._draw_ultra_gradient_background(surface, width, height)
        
        # Add cinematic post-processing effects
        self._add_atmospheric_post_processing(surface, width, height)
        
        # Draw Artemis spectre figure in background
        self._draw_artemis_spectre(surface, width, height)
        
        # Draw detailed ruined city buildings
        self._draw_ruined_cityscape(surface, width, height)
        
        # Add environmental hazards and debris
        self._draw_environmental_details(surface, width, height)
        
        return surface

    def _draw_artemis_spectre(self, surface, width, height):
        """Draw Artemis as the ultimate all-seeing eye symbol dominating the sky"""
        spectre_center_x = width // 2
        spectre_center_y = height // 5
        
        # Create subtle shadow presence in background (much more subdued)
        shadow_layers = [
            # Minimal shadow form to suggest presence without competing with the eye
            (spectre_center_x, spectre_center_y + 120, 400, 200, 0.04),  # Vague torso shadow
            (spectre_center_x, spectre_center_y + 250, 500, 150, 0.03),  # Lower shadow
        ]
        
        # Draw minimal shadow layers
        for layer_x, layer_y, layer_w, layer_h, opacity in shadow_layers:
            shadow_surface = pygame.Surface((layer_w, layer_h), pygame.SRCALPHA)
            shadow_color = (*GUNMETAL, int(255 * opacity))
            pygame.draw.ellipse(shadow_surface, shadow_color, (0, 0, layer_w, layer_h))
            surface.blit(shadow_surface, (layer_x - layer_w//2, layer_y - layer_h//2))
        
        # THE ULTIMATE ALL-SEEING EYE SYMBOL
        self._draw_all_seeing_eye_symbol(surface, spectre_center_x, spectre_center_y, width, height)

    def _draw_all_seeing_eye_symbol(self, surface, center_x, center_y, width, height):
        """Draw the ultimate all-seeing eye symbol with sacred geometry"""
        import math
        
        # Massive eye dimensions - 3x larger than before
        eye_width = 140
        eye_height = 90
        
        # Calculate golden ratio proportions for authentic sacred geometry
        golden_ratio = 1.618
        triangle_height = int(eye_height * golden_ratio * 1.2)
        triangle_width = int(eye_width * golden_ratio)
        
        # Create the triangular geometric frame (classic illuminati/masonic symbol)
        triangle_points = [
            (center_x, center_y - triangle_height//2),              # Top point
            (center_x - triangle_width//2, center_y + triangle_height//2),  # Bottom left
            (center_x + triangle_width//2, center_y + triangle_height//2)   # Bottom right
        ]
        
        # Draw the sacred triangle with ethereal glow
        self._draw_sacred_triangle(surface, triangle_points, center_x, center_y)
        
        # Draw radiating light rays in precise geometric patterns
        self._draw_geometric_light_rays(surface, center_x, center_y, triangle_width)
        
        # Draw the ultimate eye within the triangle
        self._draw_ultimate_eye(surface, center_x, center_y, eye_width, eye_height)
        
        # Add subtle tracking/following effect
        self._add_eye_tracking_effect(surface, center_x, center_y, eye_width, eye_height)

    def _draw_sacred_triangle(self, surface, triangle_points, center_x, center_y):
        """Draw the sacred geometric triangle frame"""
        import math
        
        # Multiple triangle outlines for depth and glow
        triangle_layers = [
            (6, (*ARTEMIS_RED, 80)),    # Outer glow
            (4, (*ARTEMIS_RED, 120)),   # Mid glow  
            (2, (*ARTEMIS_RED, 160)),   # Inner glow
            (1, (*ARTEMIS_RED, 200))    # Core line
        ]
        
        for thickness, color in triangle_layers:
            # Create triangle surface for proper alpha blending
            triangle_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
            
            # Adjust points for local surface coordinates
            local_points = [
                (point[0] - center_x + 100, point[1] - center_y + 100) 
                for point in triangle_points
            ]
            
            pygame.draw.polygon(triangle_surface, color, local_points, thickness)
            surface.blit(triangle_surface, (center_x - 100, center_y - 100))
        
        # Add corner accent marks for sacred geometry
        for point in triangle_points:
            accent_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
            accent_color = (*ARTEMIS_RED, 150)
            pygame.draw.circle(accent_surface, accent_color, (6, 6), 6)
            surface.blit(accent_surface, (point[0] - 6, point[1] - 6))

    def _draw_geometric_light_rays(self, surface, center_x, center_y, triangle_width):
        """Draw precisely arranged geometric light rays"""
        import math
        
        # 16 rays for perfect sacred geometry (multiple of 4)
        num_rays = 16
        ray_length = triangle_width * 0.8
        
        # Smooth pulsing instead of chaotic flickering
        pulse = 1.0 + 0.15 * math.sin(self.eye_pulse_timer * 0.8)  # Much slower, smoother
        
        for i in range(num_rays):
            angle = (i * 2 * math.pi) / num_rays
            
            # Vary ray lengths for visual interest but keep it geometric
            length_variation = 0.8 + 0.2 * math.sin(angle * 3)
            current_length = ray_length * length_variation * pulse
            
            # Calculate ray endpoints
            start_distance = triangle_width * 0.3  # Start outside triangle
            end_x = center_x + math.cos(angle) * (start_distance + current_length)
            end_y = center_y + math.sin(angle) * (start_distance + current_length)
            start_x = center_x + math.cos(angle) * start_distance
            start_y = center_y + math.sin(angle) * start_distance
            
            # Create ray with gradient effect
            ray_surface = pygame.Surface((8, int(current_length)), pygame.SRCALPHA)
            
            # Draw ray with fade-out effect
            for j in range(int(current_length)):
                alpha_factor = 1.0 - (j / current_length)
                ray_alpha = int(60 * alpha_factor * pulse)
                
                if ray_alpha > 5:
                    ray_color = (*ARTEMIS_RED, ray_alpha)
                    pygame.draw.line(ray_surface, ray_color, (4, j), (4, j), 2)
            
            # Rotate and blit ray
            rotated_ray = pygame.transform.rotate(ray_surface, -math.degrees(angle))
            ray_rect = rotated_ray.get_rect(center=(start_x, start_y))
            surface.blit(rotated_ray, ray_rect)

    def _draw_ultimate_eye(self, surface, center_x, center_y, eye_width, eye_height):
        """Draw the massive, detailed all-seeing eye"""
        import math
        
        # Smooth pulsing glow
        glow_pulse = 1.0 + 0.1 * math.sin(self.eye_pulse_timer * 0.6)  # Slower, more majestic
        
        # Multi-layered eye socket shadow for depth
        socket_layers = [
            (eye_width//2 + 15, eye_height//2 + 10, 0.4),  # Outer shadow
            (eye_width//2 + 8, eye_height//2 + 5, 0.3),    # Mid shadow
            (eye_width//2 + 3, eye_height//2 + 2, 0.2),    # Inner shadow
        ]
        
        for socket_w, socket_h, opacity in socket_layers:
            socket_surface = pygame.Surface((socket_w * 2, socket_h * 2), pygame.SRCALPHA)
            socket_color = (*EXPLOSION_BLACK, int(255 * opacity))
            pygame.draw.ellipse(socket_surface, socket_color, (0, 0, socket_w * 2, socket_h * 2))
            surface.blit(socket_surface, (center_x - socket_w, center_y - socket_h))
        
        # Main eye outline with metallic frame
        eye_rect = pygame.Rect(center_x - eye_width//2, center_y - eye_height//2, eye_width, eye_height)
        
        # Metallic frame layers
        frame_colors = [
            (STEEL_GRAY, 4),
            (DARK_METAL, 2),
            (GUNMETAL, 1)
        ]
        
        for frame_color, thickness in frame_colors:
            pygame.draw.ellipse(surface, frame_color, eye_rect, thickness)
        
        # Multi-layered iris with intricate details
        iris_width = int(eye_width * 0.75)
        iris_height = int(eye_height * 0.75)
        iris_rect = pygame.Rect(center_x - iris_width//2, center_y - iris_height//2, iris_width, iris_height)
        
        # Create prismatic iris effect
        iris_layers = [
            (iris_width, iris_height, (*ARTEMIS_RED, int(200 * glow_pulse))),          # Outer iris
            (iris_width * 0.85, iris_height * 0.85, (255, 100, 100, int(180 * glow_pulse))), # Mid iris
            (iris_width * 0.7, iris_height * 0.7, (255, 150, 150, int(160 * glow_pulse))),   # Inner iris
        ]
        
        for layer_w, layer_h, color in iris_layers:
            iris_surface = pygame.Surface((int(layer_w), int(layer_h)), pygame.SRCALPHA)
            pygame.draw.ellipse(iris_surface, color, (0, 0, int(layer_w), int(layer_h)))
            surface.blit(iris_surface, (center_x - layer_w//2, center_y - layer_h//2))
        
        # Perfect circular pupil - the void
        pupil_radius = int(min(eye_width, eye_height) * 0.2)
        pupil_surface = pygame.Surface((pupil_radius * 2, pupil_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(pupil_surface, EXPLOSION_BLACK, (pupil_radius, pupil_radius), pupil_radius)
        surface.blit(pupil_surface, (center_x - pupil_radius, center_y - pupil_radius))
        
        # Add subtle iris pattern details
        self._add_iris_details(surface, center_x, center_y, iris_width, iris_height)

    def _add_iris_details(self, surface, center_x, center_y, iris_width, iris_height):
        """Add intricate details to the iris for authenticity"""
        import math
        
        # Radial iris pattern (like real eyes)
        num_lines = 24  # Sacred number
        for i in range(num_lines):
            angle = (i * 2 * math.pi) / num_lines
            
            # Create subtle radial lines
            start_radius = min(iris_width, iris_height) * 0.15
            end_radius = min(iris_width, iris_height) * 0.35
            
            start_x = center_x + math.cos(angle) * start_radius
            start_y = center_y + math.sin(angle) * start_radius
            end_x = center_x + math.cos(angle) * end_radius
            end_y = center_y + math.sin(angle) * end_radius
            
            # Draw subtle iris lines
            line_color = (ARTEMIS_RED[0] + 30, ARTEMIS_RED[1] + 20, ARTEMIS_RED[2] + 20)
            pygame.draw.line(surface, line_color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 1)

    def _add_eye_tracking_effect(self, surface, center_x, center_y, eye_width, eye_height):
        """Add subtle tracking effect to make the eye seem alive"""
        import math
        
        # Very subtle pupil offset to create tracking illusion
        offset_x = int(3 * math.sin(self.eye_pulse_timer * 0.3))
        offset_y = int(2 * math.cos(self.eye_pulse_timer * 0.4))
        
        # Small highlight for life-like appearance
        highlight_x = center_x + offset_x + eye_width//6
        highlight_y = center_y + offset_y - eye_height//6
        
        highlight_surface = pygame.Surface((8, 6), pygame.SRCALPHA)
        highlight_color = (255, 255, 255, 120)
        pygame.draw.ellipse(highlight_surface, highlight_color, (0, 0, 8, 6))
        surface.blit(highlight_surface, (highlight_x - 4, highlight_y - 3))

    def _draw_spectral_energy(self, surface, center_x, center_y, width, height):
        """Draw dark energy emanations from Artemis spectre"""
        import math
        
        # Create flowing dark energy tendrils
        num_tendrils = 8
        for i in range(num_tendrils):
            angle = (i * 2 * math.pi) / num_tendrils
            tendril_length = random.randint(60, 120)
            
            # Create wavy tendril path
            points = []
            for step in range(15):
                t = step / 14.0
                base_x = center_x + math.cos(angle) * tendril_length * t
                base_y = center_y + math.sin(angle) * tendril_length * t
                
                # Add wave distortion
                wave_offset = math.sin(t * 6 + angle * 3) * 15
                tendril_x = base_x + math.cos(angle + math.pi/2) * wave_offset
                tendril_y = base_y + math.sin(angle + math.pi/2) * wave_offset
                
                points.append((int(tendril_x), int(tendril_y)))
            
            # Draw tendril with fading opacity
            for j in range(len(points) - 1):
                opacity = 1.0 - (j / len(points))
                tendril_surface = pygame.Surface((abs(points[j+1][0] - points[j][0]) + 10, 
                                                abs(points[j+1][1] - points[j][1]) + 10), pygame.SRCALPHA)
                
                tendril_color = (*DARK_METAL, int(80 * opacity))
                start_local = (5, 5)
                end_local = (points[j+1][0] - points[j][0] + 5, points[j+1][1] - points[j][1] + 5)
                
                if abs(end_local[0] - start_local[0]) > 1 or abs(end_local[1] - start_local[1]) > 1:
                    pygame.draw.line(tendril_surface, tendril_color, start_local, end_local, 3)
                    surface.blit(tendril_surface, (points[j][0] - 5, points[j][1] - 5))

    def _draw_ruined_cityscape(self, surface, width, height):
        """Draw detailed ruined city using existing building system"""
        ground_level = height * 0.75
        
        # Detailed building specifications with heavy destruction
        ruined_building_specs = [
            (width * 0.08, 85, 45, "industrial_tower", 0.3),      # Heavily damaged
            (width * 0.18, 120, 60, "atomic_factory", 0.4),       # Critical damage
            (width * 0.32, 95, 55, "retro_apartment", 0.5),       # Major damage
            (width * 0.45, 140, 70, "power_plant", 0.2),          # Severe damage
            (width * 0.58, 110, 50, "radar_station", 0.6),        # Moderate damage
            (width * 0.72, 130, 65, "control_tower", 0.3),        # Heavily damaged
            (width * 0.85, 100, 48, "industrial_tower", 0.4),     # Critical damage
            (width * 0.95, 80, 40, "retro_apartment", 0.7),       # Light damage
        ]
        
        for x_pos, base_height, width_size, building_type, destruction in ruined_building_specs:
            building_y = ground_level - base_height//2
            self._draw_ruined_building(surface, int(x_pos), building_y, width_size, 
                                     base_height, building_type, destruction)

    def _draw_ruined_building(self, surface, x, y, w, h, building_type, destruction_level):
        """Draw individual ruined building with extreme post-apocalyptic damage"""
        base_rect = pygame.Rect(x - w//2, y - h//2, w, h)
        
        # Apply destruction-based height reduction
        actual_height = int(h * (1.0 - destruction_level * 0.6))
        damaged_rect = pygame.Rect(x - w//2, y - actual_height//2, w, actual_height)
        
        # Base building structure with damage coloring
        damage_factor = destruction_level
        base_color = (
            int(FACTORY_GRAY_DARK[0] * (1 - damage_factor) + RUST_RED[0] * damage_factor * 0.3),
            int(FACTORY_GRAY_DARK[1] * (1 - damage_factor) + RUST_RED[1] * damage_factor * 0.3),
            int(FACTORY_GRAY_DARK[2] * (1 - damage_factor) + RUST_RED[2] * damage_factor * 0.3)
        )
        
        pygame.draw.rect(surface, base_color, damaged_rect)
        pygame.draw.rect(surface, DARK_METAL, damaged_rect, 2)
        
        # Add structural damage effects
        self._add_structural_damage(surface, damaged_rect, destruction_level)
        
        # Add ruined windows and architectural details
        self._add_ruined_details(surface, damaged_rect, building_type, destruction_level)
        
        # Add debris piles at base
        self._add_building_debris(surface, x, y + actual_height//2, w, destruction_level)

    def _add_structural_damage(self, surface, rect, destruction_level):
        """Add structural damage effects to buildings"""
        # Missing chunks and holes
        num_holes = int(destruction_level * 8)
        for _ in range(num_holes):
            if rect.width > 10 and rect.height > 10:  # Only add holes if rect is large enough
                hole_x = random.randint(rect.x + 2, rect.right - 8)
                hole_y = random.randint(rect.y + 2, rect.bottom - 8)
                hole_size = random.randint(4, max(5, int(12 * destruction_level)))
                pygame.draw.rect(surface, EXPLOSION_BLACK, (hole_x, hole_y, hole_size, hole_size))
        
        # Cracks and damage lines
        num_cracks = int(destruction_level * 6)
        for _ in range(num_cracks):
            if rect.width > 4 and rect.height > 4:  # Only add cracks if rect is large enough
                crack_start_x = random.randint(rect.x, rect.right)
                crack_start_y = random.randint(rect.y, rect.bottom)
                crack_end_x = crack_start_x + random.randint(-15, 15)
                crack_end_y = crack_start_y + random.randint(-15, 15)
                
                # Keep cracks within building bounds
                crack_end_x = max(rect.x, min(rect.right, crack_end_x))
                crack_end_y = max(rect.y, min(rect.bottom, crack_end_y))
                
                pygame.draw.line(surface, EXPLOSION_BLACK, 
                               (crack_start_x, crack_start_y), 
                               (crack_end_x, crack_end_y), 2)
        
        # Fire damage areas
        if destruction_level > 0.4 and rect.width > 8 and rect.height > 8:
            num_fires = int((destruction_level - 0.4) * 4)
            for _ in range(num_fires):
                fire_x = random.randint(rect.x, rect.right - 6)
                fire_y = random.randint(rect.y, rect.bottom - 6)
                fire_size = random.randint(3, 8)
                
                # Glowing fire effect
                fire_colors = [RUST_RED, RED_ACCENT, (255, 140, 0)]
                for i, color in enumerate(fire_colors):
                    fire_rect = pygame.Rect(fire_x + i, fire_y + i, 
                                          fire_size - i*2, fire_size - i*2)
                    if fire_rect.width > 0 and fire_rect.height > 0:
                        pygame.draw.rect(surface, color, fire_rect)

    def _add_ruined_details(self, surface, rect, building_type, destruction_level):
        """Add ruined architectural details specific to building type"""
        # Broken windows with shattered glass
        if building_type in ["industrial_tower", "atomic_factory"]:
            window_spacing = 12
            for window_x in range(rect.x + 6, rect.right - 8, window_spacing):
                for window_y in range(rect.y + 8, rect.bottom - 8, 10):
                    if random.random() < 0.7:  # 70% of windows are damaged
                        # Shattered window frame
                        pygame.draw.rect(surface, EXPLOSION_BLACK, 
                                       (window_x, window_y, 6, 4))
                        # Glass shards
                        if random.random() < destruction_level:
                            for _ in range(3):
                                shard_x = window_x + random.randint(-2, 8)
                                shard_y = window_y + random.randint(-2, 6)
                                pygame.draw.circle(surface, STEEL_GRAY, 
                                                 (shard_x, shard_y), 1)
        
        # Damaged infrastructure elements
        if building_type == "power_plant" and destruction_level > 0.3:
            # Damaged cooling tower or reactor
            tower_x = rect.centerx
            tower_y = rect.y - 10
            tower_w = 20
            tower_h = 15
            
            # Cracked tower
            pygame.draw.ellipse(surface, FACTORY_GRAY_DARK, 
                              (tower_x - tower_w//2, tower_y, tower_w, tower_h))
            pygame.draw.line(surface, EXPLOSION_BLACK,
                           (tower_x - 5, tower_y + 5), 
                           (tower_x + 5, tower_y + tower_h - 5), 3)

    def _add_building_debris(self, surface, x, base_y, width, destruction_level):
        """Add debris piles around building base"""
        debris_width = int(width * 1.2)
        num_debris = int(destruction_level * 12)
        
        for _ in range(num_debris):
            debris_x = x + random.randint(-debris_width//2, debris_width//2)
            debris_y = base_y + random.randint(0, 15)
            debris_size = random.randint(2, 8)
            
            # Rubble colors
            debris_colors = [FACTORY_GRAY_DARK, STEEL_GRAY, DARK_METAL, RUST_RED]
            debris_color = random.choice(debris_colors)
            
            # Angular debris chunks
            if random.random() < 0.6:
                pygame.draw.rect(surface, debris_color, 
                               (debris_x, debris_y, debris_size, debris_size))
            else:
                pygame.draw.circle(surface, debris_color, 
                                 (debris_x, debris_y), debris_size//2)

    def _draw_environmental_details(self, surface, width, height):
        """Add environmental hazards and atmospheric details"""
        ground_level = height * 0.75
        
        # Toxic pools and radiation zones
        num_hazards = 4
        for _ in range(num_hazards):
            hazard_x = random.randint(int(width * 0.1), int(width * 0.9))
            hazard_y = random.randint(int(ground_level), int(height - 20))
            hazard_w = random.randint(30, 60)
            hazard_h = random.randint(15, 25)
            
            # Toxic pool with glowing edges
            pool_color = (RUST_RED[0]//2, RUST_RED[1]//2, RUST_RED[2]//2)
            pygame.draw.ellipse(surface, pool_color, 
                              (hazard_x, hazard_y, hazard_w, hazard_h))
            pygame.draw.ellipse(surface, ARTEMIS_RED, 
                              (hazard_x, hazard_y, hazard_w, hazard_h), 2)
        
        # Abandoned vehicles and machinery
        num_vehicles = 3
        for _ in range(num_vehicles):
            vehicle_x = random.randint(int(width * 0.15), int(width * 0.85))
            vehicle_y = random.randint(int(ground_level), int(height - 15))
            
            # Wrecked vehicle shape
            vehicle_rect = pygame.Rect(vehicle_x, vehicle_y, 25, 12)
            pygame.draw.rect(surface, DARK_METAL, vehicle_rect)
            pygame.draw.rect(surface, RUST_RED, vehicle_rect, 1)
            
            # Broken parts
            for _ in range(3):
                part_x = vehicle_x + random.randint(-5, 30)
                part_y = vehicle_y + random.randint(-3, 15)
                pygame.draw.circle(surface, FACTORY_GRAY_DARK, (part_x, part_y), 2)
        
        # Electrical sparks from damaged infrastructure
        num_sparks = 5
        for _ in range(num_sparks):
            spark_x = random.randint(int(width * 0.2), int(width * 0.8))
            spark_y = random.randint(int(height * 0.5), int(ground_level))
            
            # Small electrical discharge
            spark_colors = [(255, 255, 255), (200, 200, 255), (150, 150, 255)]
            for i, color in enumerate(spark_colors):
                spark_size = 3 - i
                if spark_size > 0:
                    pygame.draw.circle(surface, color, (spark_x, spark_y), spark_size)

    def _draw_phase3_atmospheric_effects(self, screen, width, height):
        """Draw comprehensive atmospheric effects for Phase 3 ruins"""
        # Multi-layered atmospheric haze with depth
        self._draw_atmospheric_haze(screen, width, height)
        
        # Enhanced Artemis spectre glow effects
        self._draw_enhanced_artemis_glow(screen, width, height)
        
        # Dynamic lighting from fires and electrical damage
        self._draw_dynamic_lighting(screen, width, height)
        
        # Pulsing warning lights on infrastructure
        self._draw_warning_lights(screen, width, height)
        
        # Environmental hazard glow effects
        self._draw_hazard_glow_effects(screen, width, height)
        
        # Pollution overlay effects
        self._draw_pollution_overlay(screen, width, height)

    def _draw_atmospheric_haze(self, screen, width, height):
        """Draw multi-layered atmospheric haze for depth"""
        import math
        
        # Layer 1: Ground-level toxic mist
        mist_surface = pygame.Surface((width, height//3), pygame.SRCALPHA)
        for y in range(height//3):
            alpha_factor = 1.0 - (y / (height//3))
            mist_alpha = int(25 * alpha_factor)
            mist_color = (SMOKE_GRAY[0] + 15, SMOKE_GRAY[1] + 10, SMOKE_GRAY[2] - 5, mist_alpha)
            pygame.draw.line(mist_surface, mist_color, (0, y), (width, y))
        screen.blit(mist_surface, (0, height * 2//3))
        
        # Layer 2: Mid-level pollution bands
        for band in range(3):
            band_y = height * (0.4 + band * 0.15)
            band_height = 40
            band_surface = pygame.Surface((width, band_height), pygame.SRCALPHA)
            
            # Smoother, more coordinated atmospheric drift
            drift_offset = math.sin(self.eye_pulse_timer * 0.4 + band * 1.5) * 15
            for x in range(width):
                pollution_alpha = int(15 + 10 * math.sin((x + drift_offset) * 0.02))
                pollution_color = (GUNMETAL[0] + 20, GUNMETAL[1] + 15, GUNMETAL[2] + 10, pollution_alpha)
                pygame.draw.line(band_surface, pollution_color, 
                               (x, 0), (x, band_height))
            screen.blit(band_surface, (0, int(band_y)))
        
        # Layer 3: High-altitude radiation shimmer
        shimmer_surface = pygame.Surface((width, height//4), pygame.SRCALPHA)
        for shimmer_point in range(width//20):
            # Much more subtle and coordinated shimmer
            shimmer_x = shimmer_point * 20 + int(math.sin(self.eye_pulse_timer * 0.6 + shimmer_point * 0.3) * 6)
            shimmer_y = random.randint(0, height//4)
            shimmer_intensity = 15 + int(8 * math.sin(self.eye_pulse_timer * 0.7 + shimmer_point * 0.2))
            shimmer_color = (ARTEMIS_RED[0]//3, ARTEMIS_RED[1]//4, ARTEMIS_RED[2]//4, shimmer_intensity)
            pygame.draw.circle(shimmer_surface, shimmer_color, (shimmer_x, shimmer_y), 3)
        screen.blit(shimmer_surface, (0, 0))

    def _draw_enhanced_artemis_glow(self, screen, width, height):
        """Draw enhanced glow effects for the ultimate all-seeing eye"""
        import math
        
        eye_center_x = width // 2
        eye_center_y = height // 5
        
        # Ultra-enhanced multi-layered glow for THE eye
        # Much more powerful and sophisticated than before
        glow_layers = [
            (200, 25, 0.8),   # Outermost divine radiance
            (150, 40, 0.9),   # Mid divine glow
            (100, 60, 1.0),   # Inner sacred light
            (70, 80, 1.1),    # Core spiritual energy
            (50, 100, 1.2),   # Ultimate power glow
        ]
        
        # Smooth, majestic pulsing instead of chaotic flickering
        divine_pulse = 1.0 + 0.12 * math.sin(self.eye_pulse_timer * 0.7)  # Slower, more divine
        
        for glow_radius, base_alpha, intensity_multiplier in glow_layers:
            current_radius = int(glow_radius * divine_pulse)
            current_alpha = int(base_alpha * self.eye_glow_intensity * intensity_multiplier)
            
            if current_radius > 0 and current_alpha > 8:
                glow_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
                
                # Create gradient glow effect from center outward
                for r in range(current_radius):
                    alpha_factor = 1.0 - (r / current_radius)
                    layer_alpha = int(current_alpha * alpha_factor * alpha_factor)  # Quadratic falloff
                    
                    if layer_alpha > 3:
                        glow_color = (*ARTEMIS_RED, layer_alpha)
                        pygame.draw.circle(glow_surface, glow_color, 
                                         (current_radius, current_radius), r)
                
                screen.blit(glow_surface, (eye_center_x - current_radius, eye_center_y - current_radius))
        
        # Divine atmospheric influence - much more subtle than before
        atmosphere_radius = int(300 + 40 * math.sin(self.eye_pulse_timer * 0.5))  # Slower, smoother
        atmosphere_alpha = int(12 + 6 * math.sin(self.eye_pulse_timer * 0.6))     # More subtle
        
        if atmosphere_alpha > 5:
            atmosphere_surface = pygame.Surface((atmosphere_radius * 2, atmosphere_radius * 2), pygame.SRCALPHA)
            
            # Create subtle atmospheric gradient
            for r in range(atmosphere_radius):
                alpha_factor = 1.0 - (r / atmosphere_radius)
                layer_alpha = int(atmosphere_alpha * alpha_factor * 0.3)  # Much more subtle
                
                if layer_alpha > 2:
                    atmosphere_color = (GUNMETAL[0] + 20, GUNMETAL[1] + 15, GUNMETAL[2] + 10, layer_alpha)
                    pygame.draw.circle(atmosphere_surface, atmosphere_color, 
                                     (atmosphere_radius, atmosphere_radius), r, 2)
            
            screen.blit(atmosphere_surface, (eye_center_x - atmosphere_radius, eye_center_y - atmosphere_radius))

    def _draw_dynamic_lighting(self, screen, width, height):
        """Draw smooth, cinematic dynamic lighting"""
        import math
        
        # Refined fire lighting - much smoother and more coordinated
        fire_positions = [
            (width * 0.18, height * 0.65, 0.35, 0.0),  # Atomic factory fire - phase offset 0
            (width * 0.72, height * 0.6, 0.25, 1.5),   # Control tower fire - phase offset for rhythm
        ]  # Removed middle fire to reduce chaos
        
        for fire_x, fire_y, destruction, phase_offset in fire_positions:
            # Much gentler, more cinematic fire flicker
            flicker = 1.0 + 0.15 * math.sin(self.eye_pulse_timer * 1.8 + phase_offset)  # Reduced from * 8 to * 1.8
            light_radius = int(70 * destruction * flicker)
            light_alpha = int(35 * destruction * flicker)
            
            if light_radius > 0 and light_alpha > 8:
                # Enhanced fire glow with better gradients
                fire_surface = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
                
                # Create smooth radial gradient for fire light
                for r in range(light_radius):
                    alpha_factor = 1.0 - (r / light_radius)
                    current_alpha = int(light_alpha * alpha_factor * alpha_factor)  # Quadratic falloff
                    
                    if current_alpha > 3:
                        # Warm fire colors with proper blending
                        if r < light_radius * 0.3:
                            fire_color = (255, 180, 100, current_alpha)  # Hot core
                        elif r < light_radius * 0.6:
                            fire_color = (*RUST_RED, current_alpha)      # Mid glow
                        else:
                            fire_color = (*RED_ACCENT, current_alpha//2) # Outer glow
                        
                        pygame.draw.circle(fire_surface, fire_color, 
                                         (light_radius, light_radius), r)
                
                screen.blit(fire_surface, (int(fire_x - light_radius), int(fire_y - light_radius)))
        
        # Greatly reduced electrical discharge lighting - much less chaotic
        spark_positions = [
            (width * 0.58, height * 0.45),  # Only one spark source - radar station
        ]  # Removed the other chaotic spark sources
        
        for spark_x, spark_y in spark_positions:
            # Much rarer, more coordinated electrical flashes
            # Synchronized with eye pulse for rhythm instead of random chaos
            spark_intensity = math.sin(self.eye_pulse_timer * 2.1) * math.sin(self.eye_pulse_timer * 0.7)
            
            if spark_intensity > 0.85:  # Only flash at peak coordination
                flash_radius = int(25 + 10 * spark_intensity)
                flash_alpha = int(60 * (spark_intensity - 0.85) / 0.15)  # Fade in smoothly
                
                if flash_alpha > 10:
                    flash_surface = pygame.Surface((flash_radius * 2, flash_radius * 2), pygame.SRCALPHA)
                    
                    # Smooth electrical glow instead of harsh flash
                    for r in range(flash_radius):
                        alpha_factor = 1.0 - (r / flash_radius)
                        layer_alpha = int(flash_alpha * alpha_factor)
                        
                        if layer_alpha > 5:
                            flash_color = (200, 220, 255, layer_alpha)  # Cool electrical blue-white
                            pygame.draw.circle(flash_surface, flash_color, 
                                             (flash_radius, flash_radius), r)
                    
                    screen.blit(flash_surface, (int(spark_x - flash_radius), int(spark_y - flash_radius)))

    def _draw_warning_lights(self, screen, width, height):
        """Draw pulsing warning lights on remaining infrastructure"""
        import math
        
        # Warning light positions on less damaged buildings
        warning_positions = [
            (width * 0.58, height * 0.4),   # Radar station
            (width * 0.95, height * 0.5),   # Retro apartment
            (width * 0.08, height * 0.55),  # Industrial tower
        ]
        
        # Coordinated with the divine eye rhythm - much more cinematic
        pulse_cycle = math.sin(self.eye_pulse_timer * 1.1)  # Slower, coordinated with eye
        warning_active = pulse_cycle > 0.3  # Longer, smoother activation
        
        if warning_active:
            # Smooth fade in/out based on new threshold
            warning_alpha = int(60 * (pulse_cycle - 0.3) / 0.7)  # Gentler, more cinematic
            
            for warn_x, warn_y in warning_positions:
                # Red warning light
                warning_surface = pygame.Surface((12, 12), pygame.SRCALPHA)
                warning_color = (*RED_ACCENT, warning_alpha)
                pygame.draw.circle(warning_surface, warning_color, (6, 6), 6)
                screen.blit(warning_surface, (int(warn_x - 6), int(warn_y - 6)))
                
                # Light beam effect
                beam_surface = pygame.Surface((4, 30), pygame.SRCALPHA)
                beam_color = (*RED_ACCENT, warning_alpha//3)
                pygame.draw.rect(beam_surface, beam_color, (0, 0, 4, 30))
                screen.blit(beam_surface, (int(warn_x - 2), int(warn_y)))

    def _draw_hazard_glow_effects(self, screen, width, height):
        """Draw glow effects for environmental hazards"""
        import math
        
        # Toxic pool glow effects (matches hazard positions from background)
        ground_level = height * 0.75
        
        for hazard_num in range(4):
            # Approximate hazard positions
            hazard_x = width * (0.2 + hazard_num * 0.2)
            hazard_y = ground_level + random.randint(10, 30)
            
            # Coordinated toxic glow - smoother and more atmospheric
            pulse_factor = 1.0 + 0.15 * math.sin(self.eye_pulse_timer * 0.9 + hazard_num * 0.5)
            glow_radius = int(25 * pulse_factor)
            glow_alpha = int(20 * pulse_factor)
            
            if glow_radius > 0 and glow_alpha > 5:
                hazard_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                hazard_color = (*ARTEMIS_RED, glow_alpha)
                pygame.draw.circle(hazard_surface, hazard_color, 
                                 (glow_radius, glow_radius), glow_radius)
                screen.blit(hazard_surface, (int(hazard_x - glow_radius), int(hazard_y - glow_radius)))

    def _draw_pollution_overlay(self, screen, width, height):
        """Draw subtle pollution overlay for atmospheric depth"""
        # Create subtle color tinting overlay
        pollution_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Gradient pollution tint - heavier at ground level
        for y in range(height):
            if y > height * 0.6:  # Only affect lower portion
                pollution_factor = (y - height * 0.6) / (height * 0.4)
                pollution_alpha = int(8 * pollution_factor)
                
                # Slight red/brown tint from pollution
                pollution_color = (RUST_RED[0]//8, RUST_RED[1]//12, RUST_RED[2]//12, pollution_alpha)
                pygame.draw.line(pollution_surface, pollution_color, (0, y), (width, y))
        
        screen.blit(pollution_surface, (0, 0))

    def _draw_ultra_gradient_background(self, surface, width, height):
        """Draw ultra-sophisticated gradient background with advanced color theory"""
        import math
        
        # Define key color stops for cinematic gradient (using color theory)
        color_stops = [
            (0.0, (25, 20, 30)),        # Deep space black-purple (top)
            (0.15, (45, 35, 40)),       # Dark atmospheric layer
            (0.3, (60, 45, 50)),        # Upper pollution layer
            (0.45, (75, 60, 65)),       # Mid-atmosphere transition
            (0.65, (85, 75, 70)),       # Lower atmosphere (warmer)
            (0.8, (95, 85, 80)),        # Ground-level pollution
            (1.0, (105, 95, 90))        # Ground surface (warmest)
        ]
        
        # Create ultra-smooth gradient with proper color interpolation
        for y in range(height):
            y_factor = y / height
            
            # Find surrounding color stops
            prev_stop = color_stops[0]
            next_stop = color_stops[-1]
            
            for i in range(len(color_stops) - 1):
                if color_stops[i][0] <= y_factor <= color_stops[i + 1][0]:
                    prev_stop = color_stops[i]
                    next_stop = color_stops[i + 1]
                    break
            
            # Calculate interpolation factor between stops
            if next_stop[0] != prev_stop[0]:
                local_factor = (y_factor - prev_stop[0]) / (next_stop[0] - prev_stop[0])
            else:
                local_factor = 0
            
            # Smooth interpolation using cubic easing for more natural gradients
            smooth_factor = local_factor * local_factor * (3 - 2 * local_factor)
            
            # Interpolate RGB values
            bg_color = (
                int(prev_stop[1][0] + smooth_factor * (next_stop[1][0] - prev_stop[1][0])),
                int(prev_stop[1][1] + smooth_factor * (next_stop[1][1] - prev_stop[1][1])),
                int(prev_stop[1][2] + smooth_factor * (next_stop[1][2] - prev_stop[1][2]))
            )
            
            # Add subtle atmospheric distortion
            distortion = int(3 * math.sin(y * 0.02) * math.sin(y * 0.007))
            bg_color = (
                max(0, min(255, bg_color[0] + distortion)),
                max(0, min(255, bg_color[1] + distortion)),
                max(0, min(255, bg_color[2] + distortion))
            )
            
            pygame.draw.line(surface, bg_color, (0, y), (width, y))

    def _add_atmospheric_post_processing(self, surface, width, height):
        """Add cinematic post-processing effects"""
        import math
        
        # Add subtle film grain for cinematic feel
        self._add_film_grain(surface, width, height)
        
        # Add subtle chromatic aberration near edges
        self._add_chromatic_aberration(surface, width, height)
        
        # Add atmospheric perspective fog
        self._add_atmospheric_perspective(surface, width, height)

    def _add_film_grain(self, surface, width, height):
        """Add subtle film grain for cinematic quality"""
        import random
        
        # Very subtle grain overlay
        grain_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Only add grain to specific areas for performance
        for _ in range(width * height // 200):  # Sparse grain
            grain_x = random.randint(0, width - 1)
            grain_y = random.randint(0, height - 1)
            
            # Vary grain intensity based on background brightness
            grain_intensity = random.randint(5, 15)
            grain_color = (grain_intensity, grain_intensity, grain_intensity, 20)
            
            # Single pixel grain
            pygame.draw.circle(grain_surface, grain_color, (grain_x, grain_y), 1)
        
        surface.blit(grain_surface, (0, 0))

    def _add_chromatic_aberration(self, surface, width, height):
        """Add subtle chromatic aberration effect near screen edges"""
        # Create subtle red/blue separation near edges
        edge_distance = min(width, height) // 8
        
        for y in range(height):
            for x in [0, 1, width-2, width-1]:  # Only process edge columns for performance
                if x < edge_distance or x > width - edge_distance:
                    distance_factor = min(edge_distance - min(x, width - x), edge_distance) / edge_distance
                    
                    if distance_factor > 0.5:
                        # Get current pixel color
                        try:
                            current_color = surface.get_at((x, y))
                            
                            # Apply subtle color separation
                            aberration_strength = int(5 * (distance_factor - 0.5))
                            
                            # Slightly shift red and blue channels
                            new_color = (
                                min(255, current_color[0] + aberration_strength),
                                current_color[1],
                                min(255, current_color[2] - aberration_strength//2)
                            )
                            
                            surface.set_at((x, y), new_color)
                        except:
                            pass  # Skip if pixel access fails

    def _add_atmospheric_perspective(self, surface, width, height):
        """Add atmospheric perspective fog for depth"""
        # Create depth-based fog overlay
        fog_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Add vertical fog bands for atmospheric depth
        for y in range(height):
            fog_factor = max(0, (y - height * 0.4) / (height * 0.6))  # Fog increases towards bottom
            
            if fog_factor > 0:
                fog_alpha = int(12 * fog_factor)  # Subtle fog
                fog_color = (STEEL_GRAY[0] + 10, STEEL_GRAY[1] + 10, STEEL_GRAY[2] + 10, fog_alpha)
                pygame.draw.line(fog_surface, fog_color, (0, y), (width, y))
        
        surface.blit(fog_surface, (0, 0))

    def _get_background(self, width, height, phase):
        """Get or create background surface for the current phase"""
        cache_key = f"{phase}_{width}_{height}"
        
        if (cache_key not in self.background_surfaces or 
            self.background_width != width or 
            self.background_height != height):
            
            if phase == 0:
                self.background_surfaces[cache_key] = self._create_utopia_background(width, height)
            elif phase == 1:
                self.background_surfaces[cache_key] = self._create_explosion_background(width, height)
            else:  # phase == 2
                self.background_surfaces[cache_key] = self._create_ruins_background(width, height)
                
            self.background_width = width
            self.background_height = height
            
        return self.background_surfaces[cache_key]

    def _spawn_particles(self, width, height, phase):
        """Spawn atmospheric particles based on current phase"""
        current_time = time.time()
        if current_time - self.last_particle_time > self.particle_spawn_interval:
            # Refined particle limits for cinematic quality
            if self.current_phase == 2:  # Phase 3 (ruins) - toned down from chaotic 30
                max_particles = 18
            else:
                max_particles = 15
            
            if len(self.particles) < max_particles:
                if phase == 0:
                    # Enhanced utopian particle system with variety
                    particle_types = ["peaceful", "energy_orb", "data_stream", "crystal_spark", "garden_pollen"]
                    particle_weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Weighted probability
                    chosen_type = random.choices(particle_types, weights=particle_weights)[0]
                    
                    if chosen_type == "data_stream":
                        # Data streams spawn from buildings and flow across
                        spawn_x = random.choice([width * 0.12, width * 0.25, width * 0.4, width * 0.75, width * 0.88])
                        spawn_y = random.randint(int(height * 0.4), int(height * 0.7))
                    elif chosen_type == "garden_pollen":
                        # Pollen spawns from rooftop garden areas
                        garden_buildings = [width * 0.25, width * 0.4, width * 0.75]
                        spawn_x = random.choice(garden_buildings) + random.randint(-30, 30)
                        spawn_y = random.randint(int(height * 0.45), int(height * 0.55))
                    elif chosen_type == "crystal_spark":
                        # Crystal sparks from crystalline buildings
                        crystal_buildings = [width * 0.12, width * 0.4, width * 0.75]
                        spawn_x = random.choice(crystal_buildings) + random.randint(-20, 20)
                        spawn_y = random.randint(int(height * 0.4), int(height * 0.6))
                    elif chosen_type == "energy_orb":
                        # Energy orbs from energy connections and cores
                        spawn_x = random.randint(int(width * 0.2), int(width * 0.8))
                        spawn_y = random.randint(int(height * 0.3), int(height * 0.6))
                    else:  # peaceful
                        # General floating particles
                        spawn_x = random.randint(0, width)
                        spawn_y = height + 10
                    
                    self.particles.append(DialogueParticle(spawn_x, spawn_y, chosen_type))
                    
                elif phase == 1:
                    # Explosion particles from center
                    center_x = width // 2
                    center_y = height // 3
                    spawn_x = center_x + random.randint(-50, 50)
                    spawn_y = center_y + random.randint(-50, 50)
                    self.particles.append(DialogueParticle(spawn_x, spawn_y, "explosion"))
                else:  # phase == 2
                    # Refined Phase 3 particle system - less chaotic, more cinematic
                    particle_types = ["toxic_smoke", "ash", "ember", "industrial"]  # Removed chaotic electrical_spark and radiation_mist
                    particle_weights = [0.4, 0.35, 0.2, 0.05]  # Simplified probability distribution
                    chosen_type = random.choices(particle_types, weights=particle_weights)[0]
                    
                    if chosen_type == "toxic_smoke":
                        # Slower, more atmospheric smoke from damaged buildings
                        building_positions = [width * 0.18, width * 0.45, width * 0.72]  # Only major damage sites
                        spawn_x = random.choice(building_positions) + random.randint(-15, 15)
                        spawn_y = random.randint(int(height * 0.55), int(height * 0.7))
                    elif chosen_type == "ash":
                        # Gentle falling ash for atmospheric effect
                        spawn_x = random.randint(int(width * 0.2), int(width * 0.8))
                        spawn_y = random.randint(-5, int(height * 0.15))
                    elif chosen_type == "ember":
                        # Subtle embers from the most damaged buildings only
                        fire_positions = [width * 0.18, width * 0.72]  # Only two major fire sources
                        spawn_x = random.choice(fire_positions) + random.randint(-10, 10)
                        spawn_y = random.randint(int(height * 0.65), int(height * 0.75))
                    else:  # industrial (basic smoke)
                        # Minimal general industrial smoke
                        spawn_x = random.randint(width//4, 3*width//4)
                        spawn_y = random.randint(int(height * 0.6), height-40)
                    
                    self.particles.append(DialogueParticle(spawn_x, spawn_y, chosen_type))
            
            self.last_particle_time = current_time

    def _update_typewriter(self, dt):
        """Update the typewriter text effect"""
        if self.current_line >= len(self.story_lines):
            return False  # Story finished
            
        self.target_text = self.story_lines[self.current_line]
        
        # Handle empty lines (pauses)
        if not self.target_text.strip():
            self.current_text = ""
            self.line_timer += dt
            if self.line_timer >= 0.8:  # Shorter pause for empty lines
                self.current_line += 1
                self.line_timer = 0
                self.waiting_for_input = False
                return True
        else:
            # Typewriter effect
            if len(self.current_text) < len(self.target_text):
                self.typewriter_timer += dt
                if self.typewriter_timer >= self.typewriter_speed:
                    self.current_text += self.target_text[len(self.current_text)]
                    self.typewriter_timer = 0
                    # Play typing sound
                    if len(self.current_text) % 2 == 0:  # Every 2nd character (more frequent)
                        self.sound_manager.play_sfx('paddle', volume_multiplier=0.3)
            else:
                # Line fully typed, wait for input or auto-advance
                self.waiting_for_input = True
                # Wait for user input - no auto-advance
        
        return True

    def _draw_dialogue_box(self, screen, width, height):
        """Draw the JRPG-style dialogue box at the bottom of the screen"""
        box_height = height // 5  # Set to 1/5 of screen height
        box_y = height - box_height - 20
        box_rect = pygame.Rect(20, box_y, width - 40, box_height)
        
        # Dialogue box background
        pygame.draw.rect(screen, DIALOGUE_BOX, box_rect)
        pygame.draw.rect(screen, DIALOGUE_BORDER, box_rect, 3)
        
        # Text area
        text_margin = 20
        text_rect = pygame.Rect(box_rect.x + text_margin, box_rect.y + text_margin, 
                               box_rect.width - text_margin * 2, box_rect.height - text_margin * 2)
        
        # Render text with scaling
        scale_factor = min(width / 800, height / 600)
        font_size = max(12, int(18 * scale_factor))
        font = get_pixel_font(font_size)
        
        # Word wrap the current text
        words = self.current_text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= text_rect.width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        # Draw text lines with shadow
        line_height = font.get_height() + 4
        y_offset = text_rect.y
        
        for line in lines[:4]:  # Limit to 4 lines
            if y_offset + line_height <= text_rect.bottom:
                # Draw shadow
                shadow_surface = font.render(line, True, TEXT_SHADOW)
                screen.blit(shadow_surface, (text_rect.x + 2, y_offset + 2))
                
                # Draw main text
                text_surface = font.render(line, True, TEXT_WHITE)
                screen.blit(text_surface, (text_rect.x, y_offset))
                
                y_offset += line_height
        
        # Draw continuation indicator if waiting for input
        if self.waiting_for_input and int(time.time() * 2) % 2:  # Blinking indicator
            indicator_text = "▼ SPACE to continue"
            indicator_surface = font.render(indicator_text, True, TEXT_WHITE)
            indicator_x = box_rect.right - indicator_surface.get_width() - text_margin
            indicator_y = box_rect.bottom - indicator_surface.get_height() - text_margin
            screen.blit(indicator_surface, (indicator_x, indicator_y))

    def handle_input(self, events, width, height):
        """Handle user input for advancing dialogue and skipping"""
        for event in events:
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Skip entire intro
                    self.skip_requested = True
                    return "skip"
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if self.waiting_for_input:
                        # Advance to next line
                        self.current_line += 1
                        self.current_text = ""
                        self.line_timer = 0
                        self.waiting_for_input = False
                        self.sound_manager.play_sfx('score', volume_multiplier=0.5)
                    else:
                        # Speed up current line typing
                        self.typewriter_speed = 0.01
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.waiting_for_input:
                        # Advance to next line
                        self.current_line += 1
                        self.current_text = ""
                        self.line_timer = 0
                        self.waiting_for_input = False
                        self.sound_manager.play_sfx('score', volume_multiplier=0.5)
        
        return None

    def update(self, dt):
        """Update the intro sequence state"""
        # Update current phase based on story progress
        new_phase = self._get_current_phase()
        if new_phase != self.current_phase:
            self.current_phase = new_phase
            # Change music based on phase
            if self.current_phase == 0:
                self.sound_manager.play_music('Better Times', loops=-1, fade_duration=2.0)
            elif self.current_phase == 1:
                self.sound_manager.play_music("Artemis' Ultimate Design", loops=-1, fade_duration=2.0)
            elif self.current_phase == 2:
                self.sound_manager.play_music("Artemis' Gaze", loops=-1, fade_duration=2.0)
        
        # Update typewriter effect
        if not self._update_typewriter(dt):
            return "complete"  # Story finished
        
        # Update visual effects
        self.flash_timer += dt
        self.eye_pulse_timer += dt
        # Ultra-cinematic eye pulsing - much slower and more majestic
        # Multiple harmonic frequencies for complex, divine rhythm
        primary_pulse = math.sin(self.eye_pulse_timer * 0.8)      # Primary slow pulse
        secondary_pulse = math.sin(self.eye_pulse_timer * 1.3)    # Secondary harmonic
        tertiary_pulse = math.sin(self.eye_pulse_timer * 0.5)     # Deep breathing rhythm
        
        # Combine harmonics for complex, organic pulsing
        combined_pulse = (primary_pulse * 0.6 + secondary_pulse * 0.3 + tertiary_pulse * 0.1)
        
        # Much gentler intensity variation for divine majesty
        self.eye_glow_intensity = 1.0 + 0.12 * combined_pulse
        
        # Update animation timers for utopian phase (only when needed)
        if self.current_phase == 0:  # Only update timers during utopian phase
            self.vehicle_timer += dt
            self.energy_pulse_timer += dt
            self.building_glow_timer += dt
            self.cloud_drift_timer += dt
        
        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
        
        return None

    def draw(self, screen, width, height):
        """Draw the intro sequence"""
        # Get and draw background for current phase
        background = self._get_background(width, height, self.current_phase)
        screen.blit(background, (0, 0))
        
        # Phase-specific animated elements
        if self.current_phase == 0:  # Utopian phase animations
            self._draw_animated_utopia_elements(screen, width, height)
        
        # Spawn and draw particles
        self._spawn_particles(width, height, self.current_phase)
        for particle in self.particles:
            particle.draw(screen)
        
        # Phase-specific effects
        if self.current_phase == 1:  # Explosion phase
            # Screen flash effect
            if int(self.flash_timer * 10) % 8 < 2:
                flash_surface = pygame.Surface((width, height))
                flash_surface.fill(EXPLOSION_WHITE)
                flash_surface.set_alpha(30)
                screen.blit(flash_surface, (0, 0))
        
        elif self.current_phase == 2:  # Ruins phase - Enhanced atmospheric effects
            self._draw_phase3_atmospheric_effects(screen, width, height)
        
        # Draw dialogue box
        self._draw_dialogue_box(screen, width, height)

    def display(self, screen, clock, width, height, debug_console=None):
        """Main display loop for the campaign intro"""
        dt = 1.0 / 60.0  # Fixed timestep
        
        # Ensure phase 0 music starts properly when entering campaign intro
        self.sound_manager.play_music('Better Times', loops=-1, fade_duration=1.0)
        
        while True:
            events = pygame.event.get()
            action = self.handle_input(events, width, height)
            
            if action == "quit":
                return "quit"
            elif action == "skip":
                # Skip to map tree (let UI handle music)
                return "back"
            
            # Update intro state
            result = self.update(dt)
            if result == "complete":
                # Story finished, transition to map tree (let UI handle music)
                return "back"
            
            # Draw everything
            self.draw(screen, width, height)
            
            # Draw debug console if active
            if debug_console and debug_console.visible:
                debug_console.draw(screen, width, height)
            
            pygame.display.flip()
            clock.tick(60)