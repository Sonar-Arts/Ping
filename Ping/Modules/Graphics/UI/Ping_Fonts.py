import os
import pygame
from urllib.request import urlretrieve

class FontManager:
    """Manages font loading and caching for the game."""
    def __init__(self):
        self.fonts = {}
        self.pixel_font_path = self.ensure_pixel_font()
        
    def ensure_pixel_font(self):
        """Ensure the pixel font is available in the project."""
        # Try to find Press Start 2P in system fonts first
        system_fonts = pygame.font.get_fonts()
        for font in system_fonts:
            if 'pressstart2p' in font.lower().replace('-', '').replace(' ', ''):
                return pygame.font.match_font(font)
                
        # If not found in system fonts, try the project's font directory
        # Get the directory of this file (Ping/Modules/Submodules/Graphics/UI/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up four levels to get to Ping directory, then into Ping Assets
        font_dir = os.path.join(current_dir, "..", "..", "..", "..", "Ping Assets", "Fonts")
        font_path = os.path.join(font_dir, "PressStart2P-Regular.ttf")
        
        if os.path.exists(font_path):
            return font_path
            
        # If no font found, fall back to system default
        print("Note: Press Start 2P font not found. Please install the font or place it in 'Ping Assets/Fonts' directory.")
        return None
        
        try:
            print("Downloading pixel font...")
            urlretrieve(font_url, font_path)
            print("Font downloaded successfully!")
            return font_path
        except Exception as e:
            print(f"Error downloading font: {e}")
            return None
    
    def get_font(self, size):
        """Get a font at the specified size, with caching."""
        if size not in self.fonts:
            try:
                if self.pixel_font_path:
                    self.fonts[size] = pygame.font.Font(self.pixel_font_path, size)
                else:
                    self.fonts[size] = pygame.font.Font(None, size)
            except Exception as e:
                print(f"Error loading font: {e}")
                self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]

# Singleton instance
_font_manager = None

def get_font_manager():
    """Get the singleton font manager instance."""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager

def get_pixel_font(size=16):
    """Get a pixel font at the specified size."""
    return get_font_manager().get_font(size)