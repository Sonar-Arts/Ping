import pygame

# Track if numpy/surfarray is available
_has_numpy = False
try:
    import numpy
    _has_numpy = True
except ImportError:
    print("Warning: numpy not available, using fallback pixel effect method")

class PixelShader:
    """A shader effect class that applies pixel art style to surfaces with optimized performance."""
    
    def __init__(self):
        # Pixel art effect configuration
        self.pixel_size = 3  # Size of each pixel block
        self.edge_threshold = 0.4  # Edge detection sensitivity
        self.glow_strength = 1.2  # Edge glow intensity
        self.contrast_factor = 1.2  # Color contrast enhancement
        self.sharpness = 1.0  # Edge sharpness
        
        # Performance optimization
        self._cached_surface = None
        self._cached_surface_size = (0, 0)
        self._cache_pixels3d = None
        self._cache_alpha = None
        self._contrast_table = None
        self._sharpness_table = None
        
        # Error tracking
        self._shader_failed = False
        self._using_fallback = not _has_numpy
        
        # Initialize numpy and color tables if available
        if _has_numpy:
            try:
                # Pre-compile common numpy operations
                self._empty_mask = numpy.zeros((1, 1), dtype=bool)
                self._identity = numpy.eye(3, dtype=numpy.float32)
                # Initialize color lookup tables
                self._init_color_tables()
            except Exception as e:
                print(f"Warning: Could not initialize numpy optimizations: {e}")
                self._using_fallback = True
                # Initialize fallback color tables
                self._init_color_tables()
        else:
            # Initialize fallback color tables
            self._init_color_tables()

    def _init_cache(self, width, height):
        """Initialize or resize cache surfaces for better performance."""
        if (not self._cached_surface or
            self._cached_surface_size != (width, height)):
            # Clear old cache
            self._cached_surface = None
            self._cache_pixels3d = None
            self._cache_alpha = None
            
            # Create new cache
            self._cached_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            self._cached_surface_size = (width, height)

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
        color_params_changed = False
        for key, value in kwargs.items():
            if hasattr(self, key):
                old_value = getattr(self, key)
                setattr(self, key, value)
                # Check if color-related parameter changed
                if key in ('contrast_factor', 'sharpness') and old_value != value:
                    color_params_changed = True
        
        # Rebuild color lookup tables if needed
        if color_params_changed:
            self._contrast_table = None
            self._sharpness_table = None
            self._init_color_tables()
    
    def apply_to_surface(self, surface):
        """Apply pixel art effect to a surface using highly optimized numpy operations."""
        width = surface.get_width()
        height = surface.get_height()
        
        # Initialize or update cache if needed
        self._init_cache(width, height)
        
        try:
            # Lock surfaces for faster pixel access
            surface.lock()
            self._cached_surface.lock()
            
            # Get pixel arrays using numpy and cache them
            if self._cache_pixels3d is None:
                pixels3d = pygame.surfarray.pixels3d(surface)
                alpha = pygame.surfarray.pixels_alpha(surface)
                
                # Pre-allocate arrays for improved performance
                self._cache_pixels3d = numpy.zeros_like(pixels3d)
                self._cache_alpha = numpy.zeros_like(alpha)
            else:
                # Reuse cached arrays
                pixels3d = pygame.surfarray.pixels3d(surface)
                alpha = pygame.surfarray.pixels_alpha(surface)
            
            # Create block masks for entire surface at once
            alpha_blocks = alpha.reshape(height // self.pixel_size + 1, self.pixel_size,
                                      width // self.pixel_size + 1, self.pixel_size)
            block_masks = alpha_blocks.any(axis=(1, 3))
            
            # Process only non-transparent blocks
            for x, y in zip(*numpy.where(block_masks)):
                block_x = x * self.pixel_size
                block_y = y * self.pixel_size
                block_width = min(self.pixel_size, width - block_x)
                block_height = min(self.pixel_size, height - block_y)
                
                # Extract block data using efficient numpy slicing
                block = pixels3d[block_x:block_x+block_width,
                               block_y:block_y+block_height]
                block_alpha = alpha[block_x:block_x+block_width,
                                  block_y:block_y+block_height]
                
                mask = block_alpha > 0
                if mask.any():
                    # Process colors using vectorized operations
                    avg_rgb = numpy.mean(block.reshape(-1, 3)[mask.reshape(-1)], axis=0)
                    avg_alpha = numpy.mean(block_alpha[mask])
                    enhanced_color = self._enhance_color((*map(int, avg_rgb), int(avg_alpha)))
                    
                    # Apply colors using optimized array operations
                    self._cache_pixels3d[block_x:block_x+block_width,
                                       block_y:block_y+block_height] = enhanced_color[:3]
                    self._cache_alpha[block_x:block_x+block_width,
                                    block_y:block_y+block_height] = enhanced_color[3]
                    
                    # Handle edge effects more efficiently
                    if self._is_edge(surface, block_x, block_y):
                        glow_alpha = min(255, int(enhanced_color[3] * self.glow_strength))
                        self._cache_alpha[block_x:block_x+block_width,
                                        block_y:block_y+block_height] = glow_alpha
                        
                        # Draw crisp borders directly to cache
                        pygame.draw.rect(self._cached_surface, (*enhanced_color[:3], 255),
                                      (block_x, block_y, block_width, block_height), 1)
            
            # Update cached surface with processed data
            pygame.surfarray.pixels3d(self._cached_surface)[:] = self._cache_pixels3d
            pygame.surfarray.pixels_alpha(self._cached_surface)[:] = self._cache_alpha
            
            return self._cached_surface.copy()
            
        finally:
            try:
                surface.unlock()
                self._cached_surface.unlock()
            except:
                pass
    
    def _get_average_color_fast(self, surface):
        """Get average color using optimized numpy operations."""
        try:
            # Lock surface once for all operations
            surface.lock()
            pixels3d = pygame.surfarray.pixels3d(surface)
            alpha = pygame.surfarray.pixels_alpha(surface)
            
            # Use numpy's masked operations for efficient processing
            mask = alpha > 0
            if not mask.any():
                return (0, 0, 0, 0)
            
            # Process all colors at once using numpy's vectorized operations
            rgb_means = numpy.mean(pixels3d[mask.reshape(mask.shape[0], mask.shape[1], 1)].reshape(-1, 3), axis=0)
            a_mean = numpy.mean(alpha[mask])
            
            return tuple(map(int, (*rgb_means, a_mean)))
        except Exception as e:
            if not self._shader_failed:
                print(f"Warning: Fast pixel processing unavailable, using fallback method: {e}")
                self._shader_failed = True
                self._using_fallback = True
            return None
        finally:
            try:
                surface.unlock()
            except:
                pass
    
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
    
    def _init_color_tables(self):
        """Initialize lookup tables for color enhancement."""
        if not hasattr(self, '_contrast_table') or not hasattr(self, '_sharpness_table'):
            if _has_numpy:
                try:
                    # Create lookup tables using numpy for better performance
                    indices = numpy.arange(256, dtype=numpy.float32)
                    mid = 128.0
                    
                    # Contrast table
                    contrast = mid + (indices - mid) * self.contrast_factor
                    self._contrast_table = numpy.clip(contrast, 0, 255).astype(numpy.uint8)
                    
                    # Sharpness table
                    if self.sharpness > 1.0:
                        bright_mask = indices > mid
                        sharpness = numpy.copy(indices)
                        # Vectorized sharpness calculation
                        sharpness[bright_mask] += (255 - sharpness[bright_mask]) * (self.sharpness - 1.0)
                        sharpness[~bright_mask] -= sharpness[~bright_mask] * (self.sharpness - 1.0)
                        self._sharpness_table = numpy.clip(sharpness, 0, 255).astype(numpy.uint8)
                    else:
                        self._sharpness_table = indices.astype(numpy.uint8)
                    
                    return True
                except Exception as e:
                    print(f"Warning: Could not initialize color tables with numpy: {e}")
            
            # Fallback to regular Python lists
            self._contrast_table = [
                min(255, max(0, int(128 + (i - 128) * self.contrast_factor)))
                for i in range(256)
            ]
            
            if self.sharpness > 1.0:
                self._sharpness_table = [
                    min(255, max(0, int(
                        i + (255 - i) * (self.sharpness - 1.0) if i > 128
                        else i - i * (self.sharpness - 1.0)
                    ))) for i in range(256)
                ]
            else:
                self._sharpness_table = list(range(256))
            
            return False

    def _enhance_color(self, color):
        """
        Enhance color contrast for pixel art style using lookup tables.
        """
        r, g, b, a = color
        
        # Initialize tables if needed
        if not hasattr(self, '_contrast_table'):
            self._init_color_tables()
        
        # Apply enhancements using lookup tables
        r = self._contrast_table[r]
        g = self._contrast_table[g]
        b = self._contrast_table[b]
        
        if self.sharpness > 1.0:
            r = self._sharpness_table[r]
            g = self._sharpness_table[g]
            b = self._sharpness_table[b]
        
        return (r, g, b, min(255, max(0, int(a))))

    def _is_edge(self, surface, x, y):
        """
        Optimized edge detection using numpy array operations.
        """
        width = surface.get_width()
        height = surface.get_height()
        
        # Early exit for border pixels
        if x <= 0 or y <= 0 or x >= width-1 or y >= height-1:
            return False
            
        try:
            # Get alpha channel for the region of interest
            alpha = pygame.surfarray.pixels_alpha(surface)
            center_alpha = alpha[x, y]
            
            # Skip transparent pixels
            if center_alpha == 0:
                return False
                
            # Extract 3x3 region around pixel
            region = alpha[max(0, x-1):min(width, x+2),
                         max(0, y-1):min(height, y+2)]
            
            # Calculate max difference using numpy operations
            edge_strength = numpy.abs(region - center_alpha).max() / 255.0
            
            return edge_strength > self.edge_threshold
            
        except Exception:
            # Fallback to simpler edge detection if numpy fails
            return self._is_edge_fallback(surface, x, y)
            
    def _is_edge_fallback(self, surface, x, y):
        """Fallback edge detection for when numpy operations fail."""
        width = surface.get_width()
        height = surface.get_height()
        
        center = surface.get_at((x, y))
        if center.a == 0:
            return False
            
        # Check only cardinal directions for speed
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        edge_strength = 0
        for dx, dy in directions:
            if 0 <= x + dx < width and 0 <= y + dy < height:
                neighbor = surface.get_at((x + dx, y + dy))
                diff = abs(neighbor.a - center.a) / 255.0
                edge_strength = max(edge_strength, diff)
                
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