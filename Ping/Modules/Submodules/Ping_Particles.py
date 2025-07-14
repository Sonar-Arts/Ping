import pygame
import random
import math

class Particle:
    """Individual particle for effects like water."""
    def __init__(self, x, y, velocity_x, velocity_y, lifetime, size=2, color=(135, 206, 250), gravity_scale=1.0):
        """Initialize a particle with position, velocity, lifetime and color."""
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.color = color
        self.gravity_scale = gravity_scale

    def update(self, delta_time):
        """Update particle position and lifetime."""
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.lifetime -= delta_time
        # Add scaled gravity effect
        self.velocity_y += 400 * delta_time * self.gravity_scale  # Gravity acceleration

    def draw(self, screen, scale_rect):
        """Draw the particle with proper scaling."""
        # Create surface and draw particle
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        # Create color with alpha
        r, g, b = self.color
        pygame.draw.circle(particle_surface, (r, g, b), (self.size, self.size), self.size)
        # Apply alpha to the whole surface
        particle_surface.set_alpha(alpha)
        
        # Scale and position the particle
        scaled_pos = scale_rect(pygame.Rect(self.x, self.y, self.size * 2, self.size * 2))
        screen.blit(particle_surface, scaled_pos)
    
    @property
    def is_alive(self):
        """Check if particle is still alive."""
        return self.lifetime > 0

class WaterSpout:
    """Manages a collection of water particles for manhole effects."""
    def __init__(self, x, y, width, is_bottom=True):
        self.x = x
        self.y = y
        self.width = width
        self.is_bottom = is_bottom  # Determines spray direction
        self.particles = []
        self.spawn_rate = 60 if is_bottom else 50  # More particles for upward spray
        self.spawn_accumulator = 0
        
        # Adjust particle parameters based on direction
        self.min_lifetime = 0.6 if is_bottom else 0.4  # Longer lifetime for upward spray
        self.max_lifetime = 1.2 if is_bottom else 0.8
        self.min_speed = 250 if is_bottom else 200    # Faster speed for upward spray
        self.max_speed = 350 if is_bottom else 300
    
    def update(self, delta_time):
        """Update all particles and spawn new ones."""
        # Update existing particles
        self.particles = [p for p in self.particles if p.is_alive]
        for particle in self.particles:
            particle.update(delta_time)
        
        # Spawn new particles
        self.spawn_accumulator += delta_time * self.spawn_rate
        while self.spawn_accumulator >= 1:
            self.spawn_particle()
            self.spawn_accumulator -= 1
    
    def spawn_particle(self):
        """Create a new water particle."""
        spread = self.width * 0.4  # Horizontal spread
        x = self.x + random.uniform(-spread, spread)
        y = self.y
        
        # Initial velocity with adjusted angles based on direction
        angle = random.uniform(-25, 25) if self.is_bottom else random.uniform(-35, 35)
        speed = random.uniform(self.min_speed, self.max_speed)
        velocity_x = speed * math.sin(math.radians(angle))
        
        # Velocity direction and color depends on manhole position
        if self.is_bottom:
            velocity_y = -speed * math.cos(math.radians(angle))  # Spray upward
            color = (135, 206, 250)  # Light sky blue for upward spray
            size = random.uniform(2.5, 4.5)
            gravity_scale = 0.8  # Less gravity effect for upward spray
        else:
            velocity_y = speed * math.cos(math.radians(angle))   # Spray downward
            color = (173, 216, 230)  # Light blue for downward spray
            size = random.uniform(2, 3.5)
            gravity_scale = 0.6  # Even less gravity for downward spray
        
        # Random lifetime based on direction
        lifetime = random.uniform(self.min_lifetime, self.max_lifetime)
        
        particle = Particle(x, y, velocity_x, velocity_y, lifetime, size, color, gravity_scale)
        self.particles.append(particle)
    
    def draw(self, screen, scale_rect):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(screen, scale_rect)
