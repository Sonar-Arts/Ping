import pygame

class Button:
    def __init__(self):
        # Button colors
        self.bg_default = (40, 40, 60)      # Dark blue-gray
        self.bg_hover = (60, 60, 80)        # Lighter blue-gray
        self.border_default = (100, 100, 140)  # Light blue-gray
        self.border_hover = (140, 140, 180)  # Very light blue-gray
        self.border_width = 2
        self.corner_radius = 8

    def draw(self, screen, rect, text, font, is_hovered=False, is_checkbox=False, is_checked=False):
        """
        Draw a button or checkbox with consistent styling.
        
        Args:
            screen: Pygame surface to draw on
            rect: Rectangle defining button boundaries
            text: Text to display (or checkbox label)
            font: Font to use for text
            is_hovered: Whether mouse is hovering over button
            is_checkbox: Whether to draw as checkbox
            is_checked: Whether checkbox is checked (ignored if not checkbox)
        """
        # Select colors based on hover state
        bg_color = self.bg_hover if is_hovered else self.bg_default
        border_color = self.border_hover if is_hovered else self.border_default
        
        if is_checkbox:
            # Draw checkbox portion
            checkbox_size = min(rect.height - 4, 20)  # Size relative to rect height
            checkbox_rect = pygame.Rect(rect.x + 4, rect.y + (rect.height - checkbox_size) // 2,
                                     checkbox_size, checkbox_size)
            
            # Draw checkbox background
            pygame.draw.rect(screen, bg_color, checkbox_rect,
                           border_radius=self.corner_radius)
            pygame.draw.rect(screen, border_color, checkbox_rect,
                           self.border_width, border_radius=self.corner_radius)
            
            # Draw checkmark if checked
            if is_checked:
                checkmark_points = [
                    (checkbox_rect.x + checkbox_size * 0.2, checkbox_rect.y + checkbox_size * 0.5),
                    (checkbox_rect.x + checkbox_size * 0.4, checkbox_rect.y + checkbox_size * 0.7),
                    (checkbox_rect.x + checkbox_size * 0.8, checkbox_rect.y + checkbox_size * 0.3)
                ]
                pygame.draw.lines(screen, border_color, False, checkmark_points, 2)
            
            # Draw label text
            text_surf = font.render(text, True, (255, 255, 255))
            text_pos = (checkbox_rect.right + 8,
                       rect.centery - text_surf.get_height() // 2)
            screen.blit(text_surf, text_pos)
            
        else:
            # Draw regular button
            pygame.draw.rect(screen, bg_color, rect,
                           border_radius=self.corner_radius)
            pygame.draw.rect(screen, border_color, rect,
                           self.border_width, border_radius=self.corner_radius)
            
            # Draw centered text
            text_surf = font.render(text, True, (255, 255, 255))
            text_pos = (rect.centerx - text_surf.get_width() // 2,
                       rect.centery - text_surf.get_height() // 2)
            screen.blit(text_surf, text_pos)

# Global button instance
_button = None

def get_button():
    """Get the global button instance."""
    global _button
    if _button is None:
        _button = Button()
    return _button