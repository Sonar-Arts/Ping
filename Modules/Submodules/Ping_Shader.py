import pygame

# Track if numpy/surfarray is available
_has_numpy = False
try:
    import numpy
    _has_numpy = True
except ImportError:
    print("Warning: numpy not available, using fallback pixel effect method")

class PixelShader:
    """A shader effect class that applies pixel art style to surfaces."""
    
    def __init__(self):
        # Pixel art effect configuration
        self.pixel_size = 3  # Size of each pixel block
        self.edge_threshold = 0.4  # Edge detection sensitivity
        self.glow_strength = 1.2  # Edge glow intensity
        self.contrast_factor = 1.2  # Color contrast enhancement
        self.sharpness = 1.0  # Edge sharpness
        
        # Error tracking
        self._shader_failed = False
        self._using_fallback = not _has_numpy

    def configure(self, **kwargs):
        """
        Configure shader parameters.
        
        Args:
            pixel_size (int): Size of pixel blocks (default: 3)
            edge_threshold (float): Edge detection sensitivity (default: 0.4)
            glow_strength (float): Edge glow intensity (default: 1.2)
            contrast_factor (float): Color contrast (default: 1.2)
            sharpness (float): Edge sharpness (default: 1.0)
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def apply_to_surface(self, surface):
        """Apply pixel art effect to a surface."""
        width = surface.get_width()
        height = surface.get_height()
        
        # Create working surface with alpha
        working = pygame.Surface((width, height), pygame.SRCALPHA)
        working.blit(surface, (0, 0))
        
        # Create output surface
        output = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Process pixels in blocks
        for x in range(0, width, self.pixel_size):
            for y in range(0, height, self.pixel_size):
                # Get the color of the first pixel in the block
                block_width = min(self.pixel_size, width - x)
                block_height = min(self.pixel_size, height - y)
                
                # Extract block
                block = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
                block.blit(working, (0, 0), (x, y, block_width, block_height))
                
                # Get average color of block
                avg_color = self._get_average_color(block)
                
                # Only process blocks with some opacity
                if avg_color[3] > 0:
                    # Enhance contrast for pixel art look
                    enhanced_color = self._enhance_color(avg_color)
                    
                    # Draw block with enhanced color
                    pygame.draw.rect(output, enhanced_color,
                                  (x, y, block_width, block_height))
                    
                    # Add edge emphasis with glow if this is an edge pixel
                    if self._is_edge(working, x, y):
                        # Create glow effect on edges
                        glow_alpha = min(255, int(enhanced_color[3] * self.glow_strength))
                        edge_color = (*enhanced_color[:3], glow_alpha)
                        
                        # Draw edge highlight
                        pygame.draw.rect(output, edge_color,
                                      (x, y, block_width, block_height))
                        
                        # Draw pixel border for crisp look
                        border_color = (*enhanced_color[:3], 255)
                        pygame.draw.rect(output, border_color,
                                      (x, y, block_width, block_height), 1)
        
        return output
    
    def _get_average_color_fast(self, surface):
        """Get average color using numpy/surfarray."""
        try:
            pixels3d = pygame.surfarray.pixels3d(surface)
            alpha = pygame.surfarray.pixels_alpha(surface)
            
            # Create mask for non-transparent pixels
            mask = alpha > 0
            if not mask.any():
                return (0, 0, 0, 0)
            
            # Calculate average color components for non-transparent pixels
            r = int(pixels3d[:, :, 0][mask].mean())
            g = int(pixels3d[:, :, 1][mask].mean())
            b = int(pixels3d[:, :, 2][mask].mean())
            a = int(alpha[mask].mean())
            
            return (r, g, b, a)
        except Exception as e:
            if not self._shader_failed:
                print("Warning: Fast pixel processing unavailable, using fallback method")
                self._shader_failed = True
                self._using_fallback = True
            return None
    
    def _get_average_color_fallback(self, surface):
        """Get average color using direct pixel access."""
        width = surface.get_width()
        height = surface.get_height()
        
        if width == 0 or height == 0:
            return (0, 0, 0, 0)
        
        # Sample every Nth pixel for better performance
        sample_step = max(1, min(width, height) // 10)
        r_total = g_total = b_total = a_total = count = 0
        
        for x in range(0, width, sample_step):
            for y in range(0, height, sample_step):
                color = surface.get_at((x, y))
                if color.a > 0:  # Only count non-transparent pixels
                    r_total += color.r
                    g_total += color.g
                    b_total += color.b
                    a_total += color.a
                    count += 1
        
        if count == 0:
            return (0, 0, 0, 0)
        
        return (
            int(r_total / count),
            int(g_total / count),
            int(b_total / count),
            int(a_total / count)
        )
    
    def _get_average_color(self, surface):
        """Get the average color of all pixels in a surface."""
        if not self._using_fallback:
            result = self._get_average_color_fast(surface)
            if result is not None:
                return result
        return self._get_average_color_fallback(surface)
    
    def _enhance_color(self, color):
        """
        Enhance color contrast for pixel art style.
        Increases saturation and adjusts brightness to create more defined pixels.
        """
        r, g, b, a = color
        
        # Apply configurable contrast
        mid = 128
        r = int(min(255, max(0, mid + (r - mid) * self.contrast_factor)))
        g = int(min(255, max(0, mid + (g - mid) * self.contrast_factor)))
        b = int(min(255, max(0, mid + (b - mid) * self.contrast_factor)))

        # Apply sharpness enhancement
        if self.sharpness > 1.0:
            r = self._apply_sharpness(r, mid)
            g = self._apply_sharpness(g, mid)
            b = self._apply_sharpness(b, mid)
        
        # Ensure alpha remains unchanged but valid
        a = min(255, max(0, int(a)))
        
        return (r, g, b, a)

    def _apply_sharpness(self, value, mid):
        """
        Apply sharpness enhancement to a color value.
        Makes bright colors brighter and dark colors darker.
        """
        if value > mid:
            return int(min(255, value + (255 - value) * (self.sharpness - 1.0)))
        else:
            return int(max(0, value - value * (self.sharpness - 1.0)))

    def _is_edge(self, surface, x, y):
        """
        Determine if a pixel is an edge by checking surrounding pixels including diagonals.
        Uses enhanced edge detection for sharper pixel art look.
        """
        width = surface.get_width()
        height = surface.get_height()
        
        if x <= 0 or y <= 0 or x >= width-1 or y >= height-1:
            return False
        
        center = surface.get_at((x, y))
        if center.a == 0:  # Skip transparent pixels
            return False
        
        # Check surrounding pixels including diagonals
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),  # Cardinal directions
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonals
        ]
        
        edge_strength = 0
        for dx, dy in directions:
            if 0 <= x + dx < width and 0 <= y + dy < height:
                neighbor = surface.get_at((x + dx, y + dy))
                # Calculate edge strength based on alpha difference
                diff = abs(neighbor.a - center.a) / 255.0
                edge_strength = max(edge_strength, diff)
        
        # Return true if edge strength exceeds threshold
        return edge_strength > self.edge_threshold

# Global shader instance
_shader = None

def get_shader(preset='default'):
    """
    Get the global shader instance with optional preset configuration.
    
    Args:
        preset (str): Configuration preset ('default', 'text', 'ui')
    """
    global _shader
    if _shader is None:
        _shader = PixelShader()
    
    # Configure shader based on preset
    if preset == 'text':
        # Optimized for text rendering
        _shader.configure(
            pixel_size=2,  # Smaller pixels for text clarity
            edge_threshold=0.2,  # Very sensitive edges
            glow_strength=1.2,  # Moderate glow
            contrast_factor=1.5,  # Strong contrast
            sharpness=1.6  # Extra sharp edges
        )
    elif preset == 'ui':
        # Optimized for UI elements
        _shader.configure(
            pixel_size=3,  # Standard pixel size
            edge_threshold=0.4,  # Standard edges
            glow_strength=1.2,  # Standard glow
            contrast_factor=1.2,  # Standard contrast
            sharpness=1.0  # No extra sharpness
        )
    else:  # default
        # Reset to default settings
        _shader.configure(
            pixel_size=3,  # Balanced pixel size for UI
            edge_threshold=0.25,  # Very sensitive edges
            glow_strength=1.3,  # Enhanced glow
            contrast_factor=1.4,  # Balanced contrast
            sharpness=1.5  # Very sharp edges
        )
    
    return _shader