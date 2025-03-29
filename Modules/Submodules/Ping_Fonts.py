import pygame
import os
from .Ping_Shader import get_shader
# Avoid circular import
def get_shader_enabled():
    """Get shader enabled state from settings."""
    try:
        from .Ping_Settings import SettingsScreen
        return SettingsScreen.get_shader_enabled()
    except:
        return True  # Default to enabled if settings not available

__all__ = ['FontManager', 'ShaderFont', 'get_font_manager']

class ShaderFont:
    """Font wrapper that applies optimized pixel shader effect to rendered text."""
    def __init__(self, original_font, font_manager=None):
        """
        Initialize a shader-enabled font.
        
        Args:
            original_font: The base pygame font object
            font_manager: Optional FontManager instance for shader management
        """
        if not original_font:
            raise ValueError("Original font is required")
        
        self.original_font = original_font
        self._shader_failed = False
        self._render_cache = {}
        self._cache_size = 100
        
        try:
            self.shader = font_manager.shader if font_manager else get_shader('text')
        except Exception as e:
            if not self._shader_failed:
                print(f"Warning: Could not initialize shader: {str(e)}")
                self._shader_failed = True
            self.shader = None
    
    def render(self, text, antialias, color):
        """
        Render text with shader effect if available, otherwise fall back to normal rendering.
        Uses caching to prevent re-rendering the same text.
        """
        # Create cache key from parameters
        cache_key = (text, antialias, color)
        
        # Check cache first
        if cache_key in self._render_cache:
            return self._render_cache[cache_key].copy()
        
        try:
            # Only attempt shader rendering if we haven't had previous failures
            if self.shader and not self._shader_failed:
                try:
                    # Create slightly larger surface for better shader effect
                    base_size = self.original_font.size(text)
                    padded_size = (base_size[0] + 4, base_size[1] + 4)
                    base_surface = pygame.Surface(padded_size, pygame.SRCALPHA)
                    
                    # Render text with padding
                    text_surface = self.original_font.render(text, antialias, color)
                    base_surface.blit(text_surface, (2, 2))  # Center in padded surface
                    
                    # Apply shader effect
                    shaded_surface = self.shader.apply_to_surface(base_surface)
                    
                    # Create final surface with original dimensions
                    final_surface = pygame.Surface(base_size, pygame.SRCALPHA)
                    final_surface.blit(shaded_surface, (-2, -2))  # Offset to remove padding
                    
                    # Cache the result
                    self._cache_result(cache_key, final_surface)
                    return final_surface
                    
                except Exception as e:
                    if not self._shader_failed:
                        print(f"Shader effect failed: {str(e)}, falling back to normal rendering")
                        self._shader_failed = True
            
            # Fall back to normal rendering
            result = self.original_font.render(text, antialias, color)
            self._cache_result(cache_key, result)
            return result
            
        except Exception as e:
            print(f"Critical error in text rendering: {str(e)}")
            # Don't cache errors
            return self.original_font.render(text, antialias, color)
    
    def _cache_result(self, key, surface):
        """Cache a rendered surface and manage cache size."""
        self._render_cache[key] = surface
        if len(self._render_cache) > self._cache_size:
            # Remove oldest item
            self._render_cache.pop(next(iter(self._render_cache)))
    
    def get_height(self):
        return self.original_font.get_height()
    
    def size(self, text):
        # Return original size without padding
        return self.original_font.size(text)

class FontManager:
    """Manages game fonts and provides a simple interface for font loading and caching."""
    
    # Font paths
    FONT_DIR = "../Ping_Graphics/Ping_Fonts"
    
    # Font definitions with their respective filenames/system fonts and default sizes
    FONTS = {
        'title': {
            'file': 'RubikBubbles-Regular.ttf',  # Display font for titles
            'default_size': 74,
            'is_system_font': False
        },
        'menu': {
            'file': 'corbel',  # Windows system font for menu items
            'default_size': 48,
            'is_system_font': True
        },
        'score': {
            'file': 'RobotoMono-Bold.ttf',  # Monospace font for scores
            'default_size': 36,
            'is_system_font': False
        },
        'text': {
            'file': 'Roboto-Light.ttf',  # Light font for general text
            'default_size': 24,
            'is_system_font': False
        }
    }
    
    def __init__(self):
        """Initialize the font manager."""
        self.fonts = {}
        self.fallback_font = None
        pygame.font.init()  # Ensure pygame font is initialized
        self.shader = get_shader('text')  # Use text-optimized shader preset
    
    def _get_font_path(self, font_name):
        """Get the full path for a font file."""
        if font_name not in self.FONTS:
            return None
        
        font_info = self.FONTS[font_name]
        if font_info['is_system_font']:
            return font_info['file']  # Return system font name directly
            
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct path to font file
        font_file = font_info['file']
        font_path = os.path.join(current_dir, self.FONT_DIR, font_file)
        
        return font_path if os.path.exists(font_path) else None
    
    def get_font(self, font_name, size=None, use_shader=None):
        """
        Get a font with the specified name and size.
        
        Args:
            font_name: Name of the font to get
            size: Size of the font (optional)
            use_shader: Whether to apply pixel shader effect (default True)
        """
        if font_name not in self.FONTS:
            return self.get_fallback_font(size)
        
        # Determine if shader should be used
        if use_shader is None:
            use_shader = get_shader_enabled()

        size = size or self.FONTS[font_name]['default_size']
        font_key = f"{font_name}_{size}"
        shader_key = f"{font_key}_shader"
        
        # Return cached version if available
        if use_shader and shader_key in self.fonts:
            return self.fonts[shader_key]
        if not use_shader and font_key in self.fonts:
            return self.fonts[font_key]
        
        font_info = self.FONTS[font_name]
        try:
            try:
                # Create the base font
                if font_info['is_system_font']:
                    try:
                        base_font = pygame.font.SysFont(font_info['file'], size)
                    except:
                        print(f"Error loading system font {font_info['file']}")
                        return self.get_fallback_font(size, use_shader)
                else:
                    font_path = self._get_font_path(font_name)
                    if font_path:
                        base_font = pygame.font.Font(font_path, size)
                    else:
                        return self.get_fallback_font(size, use_shader)
                
                # Cache and return appropriate version
                if use_shader:
                    shader_font = ShaderFont(base_font, self)
                    self.fonts[shader_key] = shader_font
                    self.fonts[font_key] = base_font  # Cache base font too
                    return shader_font
                else:
                    self.fonts[font_key] = base_font
                    return base_font
                
            except Exception as e:
                print(f"Error creating font {font_name}: {str(e)}")
                return self.get_fallback_font(size, use_shader)
        except Exception as e:
            print(f"Error loading font {font_name}: {e}")
        
        # Fall back to default system font
        return self.get_fallback_font(size)
    
    def get_fallback_font(self, size, use_shader=None):
        """Get the fallback system font with the specified size."""
        if not size:
            size = 24  # Default fallback size
            
        # Determine if shader should be used
        if use_shader is None:
            use_shader = get_shader_enabled()
        
        font_key = f"fallback_{size}"
        shader_key = f"{font_key}_shader"
        
        # Return cached font if available
        if use_shader and shader_key in self.fonts:
            return self.fonts[shader_key]
        if not use_shader and font_key in self.fonts:
            return self.fonts[font_key]
        
        try:
            # Create new fallback font
            base_font = pygame.font.Font(None, size)
            self.fonts[font_key] = base_font
            
            if use_shader:
                try:
                    shader_font = ShaderFont(base_font, self)
                    self.fonts[shader_key] = shader_font
                    return shader_font
                except Exception as e:
                    print(f"Error creating shader font: {str(e)}, falling back to base font")
                    return base_font
            
            return base_font
        except Exception as e:
            print(f"Critical error creating fallback font: {str(e)}")
            return pygame.font.Font(None, 24)  # Last resort fallback
    
    def scale_size(self, base_size, scale):
        """Scale a font size while maintaining minimum readability."""
        return max(12, int(base_size * scale))

# Global font manager instance
_font_manager = None

def get_font_manager():
    """Get the global font manager instance."""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager