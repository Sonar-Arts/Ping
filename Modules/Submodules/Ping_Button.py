import pygame

class MenuButton:
    """A class to handle stylish menu button rendering."""
    
    def __init__(self):
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.DARK_GRAY = (30, 30, 30)
        self.LIGHT_GRAY = (60, 60, 60)
        self.GLOW_COLOR = (100, 100, 150, 100)  # Slightly blue glow
    
    def _create_gradient_surface(self, width, height, is_hovered=False):
        """Create a gradient surface for the button background."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if is_hovered:
            start_color = (70, 70, 90)
            end_color = (40, 40, 60)
        else:
            start_color = (50, 50, 70)
            end_color = (30, 30, 40)
        
        for y in range(height):
            # Calculate gradient color for this line
            factor = y / height
            color = [
                start_color[i] + (end_color[i] - start_color[i]) * factor
                for i in range(3)
            ]
            pygame.draw.line(surface, color, (0, y), (width, y))
        
        return surface
    
    def _create_glow(self, width, height):
        """Create a glow effect surface."""
        glow = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow, self.GLOW_COLOR, 
                        (0, 0, width + 10, height + 10), 
                        border_radius=10)
        return glow
    
    def draw(self, screen, rect, text, font, is_hovered=False):
        """Draw a stylish button with text."""
        # Draw glow effect if hovered
        if is_hovered:
            glow = self._create_glow(rect.width, rect.height)
            screen.blit(glow, 
                       (rect.x - 5, rect.y - 5))
        
        # Create and draw gradient background
        gradient = self._create_gradient_surface(rect.width, rect.height, is_hovered)
        gradient_rect = gradient.get_rect(center=rect.center)
        
        # Draw rounded rectangle background
        pygame.draw.rect(screen, self.DARK_GRAY, rect, border_radius=8)
        screen.blit(gradient, gradient_rect)
        
        # Draw subtle border
        pygame.draw.rect(screen, self.LIGHT_GRAY, rect, 1, border_radius=8)
        
        # Draw text
        text_surf = font.render(text, True, self.WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

# Global button instance
_button_instance = None

def get_button():
    """Get the global button instance."""
    global _button_instance
    if _button_instance is None:
        _button_instance = MenuButton()
    return _button_instance