import pygame
import os

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
    
    def get_font(self, font_name, size=None):
        """Get a font with the specified name and size."""
        if font_name not in self.FONTS:
            return self.get_fallback_font(size)
        
        size = size or self.FONTS[font_name]['default_size']
        font_key = f"{font_name}_{size}"
        
        # Return cached font if available
        if font_key in self.fonts:
            return self.fonts[font_key]
        
        font_info = self.FONTS[font_name]
        try:
            if font_info['is_system_font']:
                # Try to create system font
                try:
                    font = pygame.font.SysFont(font_info['file'], size)
                    self.fonts[font_key] = font
                    return font
                except:
                    print(f"Error loading system font {font_info['file']}")
                    return self.get_fallback_font(size)
            else:
                # Try to load custom font file
                font_path = self._get_font_path(font_name)
                if font_path:
                    font = pygame.font.Font(font_path, size)
                    self.fonts[font_key] = font
                    return font
        except Exception as e:
            print(f"Error loading font {font_name}: {e}")
        
        # Fall back to default system font
        return self.get_fallback_font(size)
    
    def get_fallback_font(self, size):
        """Get the fallback system font with the specified size."""
        if not size:
            size = 24  # Default fallback size
        
        font_key = f"fallback_{size}"
        if font_key not in self.fonts:
            self.fonts[font_key] = pygame.font.Font(None, size)
        
        return self.fonts[font_key]
    
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