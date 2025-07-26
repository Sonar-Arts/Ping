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

class Dropdown:
    def __init__(self, items, max_items=None):
        """
        Initialize a dropdown menu.
        
        Args:
            items: List of items to show in the dropdown
            max_items: Maximum number of items to show before scrolling
        """
        # Use same colors as Button class for consistency
        self.bg_default = (40, 40, 60)
        self.bg_hover = (60, 60, 80)
        self.border_default = (100, 100, 140)
        self.border_hover = (140, 140, 180)
        self.border_width = 2
        self.corner_radius = 8

        self.items = items
        self.max_items = max_items
        self.selected_index = 0
        self.is_open = False
        self.scroll_offset = 0
        self.hovered_index = -1

    def draw(self, screen, rect, font, hover_check_fn=None):
        """
        Draw the dropdown menu.
        
        Args:
            screen: Pygame surface to draw on
            rect: Rectangle defining dropdown boundaries
            font: Font to use for text
            hover_check_fn: Function to check if button is being hovered
        """
        # Use provided hover check function or fallback to simple collision
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = hover_check_fn(rect, mouse_pos) if hover_check_fn else rect.collidepoint(mouse_pos)
        # Draw main button with hover effect
        bg_color = self.bg_hover if (self.is_open or is_hovered) else self.bg_default
        border_color = self.border_hover if (self.is_open or is_hovered) else self.border_default

        pygame.draw.rect(screen, bg_color, rect, border_radius=self.corner_radius)
        pygame.draw.rect(screen, border_color, rect, self.border_width, border_radius=self.corner_radius)

        # Draw selected item
        selected_text = self.items[self.selected_index] if self.items else ""
        text_color = (200, 200, 255) if (is_hovered or self.is_open) else (255, 255, 255)
        text_surf = font.render(selected_text, True, text_color)
        text_pos = (rect.x + 10, rect.centery - text_surf.get_height() // 2)
        screen.blit(text_surf, text_pos)

        # Draw dropdown arrow
        arrow_points = [
            (rect.right - 20, rect.centery - 4),
            (rect.right - 10, rect.centery - 4),
            (rect.right - 15, rect.centery + 4)
        ]
        arrow_color = self.border_hover if (is_hovered or self.is_open) else self.border_default
        pygame.draw.polygon(screen, arrow_color, arrow_points)

        # Draw dropdown list if open
        if self.is_open and self.items:
            item_height = rect.height
            # If max_items is None or greater than items length, show all items
            visible_items = len(self.items) if self.max_items is None else min(self.max_items, len(self.items))
            dropdown_height = item_height * visible_items
            
            # Calculate if dropdown should appear above or below
            screen_height = screen.get_height()
            should_appear_above = rect.bottom + dropdown_height > screen_height
            
            # Create dropdown list surface with extra space for scrolling
            if should_appear_above:
                dropdown_rect = pygame.Rect(rect.x, rect.top - dropdown_height,
                                        rect.width, dropdown_height)
            else:
                dropdown_rect = pygame.Rect(rect.x, rect.bottom,
                                        rect.width, dropdown_height)

            # Fill the background behind the dropdown
            pygame.draw.rect(screen, (30, 30, 50), dropdown_rect,
                           border_radius=self.corner_radius)
            
            # Create a surface for the dropdown content
            dropdown_surface = pygame.Surface((dropdown_rect.width, dropdown_height), pygame.SRCALPHA)
            # Fill dropdown surface with semi-transparent background
            pygame.draw.rect(dropdown_surface, (30, 30, 50, 230),
                           (0, 0, dropdown_rect.width, dropdown_height),
                           border_radius=self.corner_radius)
            
            # Create a rect for hover checking dropdown items
            base_item_rect = pygame.Rect(rect.x, rect.bottom, rect.width, rect.height)
            # Calculate visible range based on scroll offset
            start_idx = self.scroll_offset
            end_idx = min(start_idx + visible_items, len(self.items))

            # Draw visible items
            for i in range(start_idx, end_idx):
                item_rect = pygame.Rect(0, (i - start_idx) * item_height,
                                     dropdown_rect.width, item_height)
                # Calculate the rect for hover checking this item
                if should_appear_above:
                    item_rect_for_hover = pygame.Rect(rect.x,
                                                    rect.top - (visible_items - (i - start_idx)) * item_height,
                                                    rect.width, item_height)
                else:
                    item_rect_for_hover = pygame.Rect(rect.x,
                                                    rect.bottom + (i - start_idx) * item_height,
                                                    rect.width, item_height)
                
                
                # Draw item background
                item_bg_color = self.bg_hover if (i == self.hovered_index or i == self.selected_index) else (40, 40, 60)
                pygame.draw.rect(dropdown_surface, item_bg_color, item_rect, border_radius=self.corner_radius)

                # Add hover effect
                if i == self.hovered_index:
                    # Draw highlight border
                    pygame.draw.rect(dropdown_surface, (100, 100, 160, 100), item_rect, 1, border_radius=self.corner_radius)
                
                # Draw item text with hover effect
                text_color = (200, 200, 255) if i == self.hovered_index else (255, 255, 255)
                text_surf = font.render(self.items[i], True, text_color)
                
                # Adjust text position for proper centering
                text_rect = text_surf.get_rect()
                text_rect.midleft = (10, item_rect.centery)
                dropdown_surface.blit(text_surf, text_rect)

            # Draw the dropdown surface and border
            screen.blit(dropdown_surface, dropdown_rect)
            # Draw inner and outer borders for better visibility
            pygame.draw.rect(screen, (60, 60, 80), dropdown_rect, 1, border_radius=self.corner_radius)  # Inner border
            pygame.draw.rect(screen, self.border_default, dropdown_rect, self.border_width, border_radius=self.corner_radius)  # Outer border
            # Add a subtle highlight at the top
            pygame.draw.line(screen, (80, 80, 100),
                           (dropdown_rect.left + self.corner_radius, dropdown_rect.top),
                           (dropdown_rect.right - self.corner_radius, dropdown_rect.top),
                           1)

    def handle_event(self, event, rect, hover_check_fn=None):
        """
        Handle mouse events for the dropdown.
        
        Args:
            event: Pygame event to handle
            rect: Rectangle defining dropdown boundaries
            hover_check_fn: Function to check if an area is being hovered over
            
        Returns:
            Selected item index if an item was selected, None otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                # Use hover check function for main button click detection
                if hover_check_fn:
                    is_clicked = hover_check_fn(rect, mouse_pos)
                else:
                    is_clicked = rect.collidepoint(mouse_pos)
                
                if is_clicked:
                    # Only toggle if it's the main button click
                    self.is_open = not self.is_open
                    print(f"[DEBUG] Dropdown is_open: {self.is_open}")  # Add this debug print
                    return None
                
                if self.is_open:
                    # Calculate dropdown list rect
                    item_height = rect.height
                    visible_items = min(self.max_items or len(self.items), len(self.items))
                    dropdown_height = item_height * visible_items
                    screen_height = pygame.display.get_surface().get_height()
                    should_appear_above = rect.bottom + dropdown_height > screen_height
                    
                    if should_appear_above:
                        dropdown_rect = pygame.Rect(rect.x, rect.top - dropdown_height,
                                                rect.width, dropdown_height)
                    else:
                        dropdown_rect = pygame.Rect(rect.x, rect.bottom,
                                                rect.width, dropdown_height)
                    
                    mouse_pos = event.pos
                    # Use hover check function for dropdown items too
                    # Use hover check function to detect clicks on individual items
                    item_height = rect.height
                    visible_items = min(self.max_items, len(self.items))
                    clicked_index = None
                    
                    # Improved click detection for dropdown items
                    for i in range(visible_items):
                        # Create item rect based on dropdown position
                        if dropdown_rect.y < rect.y:  # Dropdown is above
                            item_rect = pygame.Rect(rect.x, rect.top - (visible_items - i) * item_height,
                                                  rect.width, item_height)
                        else:  # Dropdown is below
                            item_rect = pygame.Rect(rect.x, rect.bottom + i * item_height,
                                                  rect.width, item_height)
                        
                        # Check if item is clicked using provided hover check function
                        if hover_check_fn(item_rect, mouse_pos) if hover_check_fn else item_rect.collidepoint(mouse_pos):
                            clicked_index = self.scroll_offset + i
                            break
                    
                    # If an item was clicked and it's valid
                    if clicked_index is not None and clicked_index < len(self.items):
                        self.selected_index = clicked_index
                        self.is_open = False
                        print(f"[DEBUG] Selected item {clicked_index}: {self.items[clicked_index]}")
                        return clicked_index
                    # Only close if clicking outside the dropdown area
                    elif not dropdown_rect.collidepoint(mouse_pos):
                        self.is_open = False
            
            elif event.button == 4 and self.is_open:  # Mouse wheel up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5 and self.is_open:  # Mouse wheel down
                max_offset = max(0, len(self.items) - self.max_items)
                self.scroll_offset = min(max_offset, self.scroll_offset + 1)
        
        elif event.type == pygame.MOUSEMOTION and self.is_open:
            # Enhanced hover detection
            item_height = rect.height
            visible_items = min(self.max_items, len(self.items)) if self.max_items else len(self.items)
            
            # Calculate if dropdown should appear above or below
            screen_height = pygame.display.get_surface().get_height()
            dropdown_height = item_height * visible_items
            should_appear_above = rect.bottom + dropdown_height > screen_height
            
            if should_appear_above:
                dropdown_rect = pygame.Rect(rect.x, rect.top - dropdown_height,
                                        rect.width, dropdown_height)
            else:
                dropdown_rect = pygame.Rect(rect.x, rect.bottom,
                                        rect.width, dropdown_height)
            
            mouse_pos = event.pos
            # Reset hover index initially
            self.hovered_index = -1
            
            # Check each item for hover
            for i in range(visible_items):
                # Calculate item rect based on dropdown position
                if should_appear_above:
                    item_rect = pygame.Rect(rect.x, rect.top - (visible_items - i) * item_height,
                                        rect.width, item_height)
                else:
                    item_rect = pygame.Rect(rect.x, rect.bottom + i * item_height,
                                        rect.width, item_height)
                
                if hover_check_fn(item_rect, mouse_pos) if hover_check_fn else item_rect.collidepoint(mouse_pos):
                    self.hovered_index = self.scroll_offset + i
                    break
        
        return None

# Global instances
_button = None
_dropdown = None

def get_button():
    """Get the global button instance."""
    global _button
    if _button is None:
        _button = Button()
    return _button

def get_dropdown(items=None, max_items=5):
    """Get a dropdown instance with the specified items."""
    global _dropdown
    if items is not None or _dropdown is None:
        _dropdown = Dropdown(items or [], max_items)
    return _dropdown