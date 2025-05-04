"""
Artemis Editor - Level View Module (Pygame Embedding)

This module contains the main widget for visually displaying and interacting
with the Ping level being edited, using an embedded Pygame surface.
"""
import pygame
import os
import random # For unique IDs initially
import pygame # Ensure pygame is imported for SysFont

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSizePolicy # Removed QScrollArea
# Import pyqtSignal
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QImage, QColor # Added for direct painting

# Import tool constants
from .artemis_tool_palette import TOOL_ERASER, TOOL_SELECT # Import from the new tool palette module

print("Artemis Modules/artemis_level_view.py loaded (Pygame)")

# --- Default Object Properties ---
# Define default sizes for objects when placed
DEFAULT_SIZES = {
    "paddle_spawn_left": (10, 80),
    "paddle_spawn_right": (10, 80),
    "ball_spawn": (20, 20),
    "obstacle_rect": (20, 60),
    "goal_left": (20, 200),
    "goal_right": (20, 200),
    "portal": (30, 30),
    "powerup_ball": (20, 20),
    "manhole": (40, 20) # Horizontal rect representation
}
DEFAULT_PADDLE_OFFSET_X = 50
DEFAULT_PADDLE_OFFSET_Y = 0 # Centered later

# Removed PygameContainerWidget

class LevelViewWidget(QWidget):
    """
    The main canvas for viewing and editing the level using Pygame, drawn via paintEvent.
    """
    # --- Signals ---
    # Emits the ID of the selected object, or None if deselected
    objectSelected = pyqtSignal(object, name='objectSelected')
    # Emits True when the level data is modified, False otherwise (e.g., after save/load)
    levelModified = pyqtSignal(bool, name='levelModified')

    def __init__(self, core_logic, main_window, parent=None): # Added core_logic
        super().__init__(parent)
        self.core_logic = core_logic # Store core logic reference
        self.main_window = main_window # Reference to access selected tool
        # Level state is now primarily managed by core_logic
        # self.level_width = 800
        # self.level_height = 450
        # self.placed_objects = [] # Managed by core_logic
        # self.next_object_id = 1 # Managed by core_logic
        self.selected_object_id = None # Track the ID of the currently selected object
        self.is_dragging = False
        self.drag_offset = (0, 0)
        # --- Grid ---
        self.grid_size = 20 # Size of grid cells in pixels
        self.grid_enabled = False # Start with grid off
        self.grid_color = (60, 60, 60) # Dark grey for grid lines

        # --- Pygame Surface Setup ---
        # Get initial size from core_logic defaults if possible, or use fallback
        initial_props = self.core_logic.get_level_properties() # Assuming core has defaults
        self.level_width = initial_props.get("width", 800) # Use width/height keys
        self.level_height = initial_props.get("height", 450)
        self.pygame_surface = None # Will be created in refresh_display/init
        self.render_offset_x = 0 # Offset for centering drawing
        self.render_offset_y = 0

        # --- Widget Setup ---
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        # Expand to fill available space, sizeHint will determine preferred size
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #101010;") # Set background for area outside canvas
        # Optimize painting
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        # --- Pygame Timer ---
        self.timer = QTimer(self)
        self.timer.setInterval(16) # Approx 60 FPS
        self.timer.timeout.connect(self.update_pygame)

        # --- Sprite Cache ---
        self.sprite_cache = {} # Cache for loaded sprite images

        # --- Connect to Core Signals ---
        self.core_logic.levelLoaded.connect(self.refresh_display)
        self.core_logic.levelPropertiesChanged.connect(self.refresh_display)
        self.core_logic.objectUpdated.connect(self._handle_object_update) # Connect new signal
        self.core_logic.layoutRestored.connect(self.refresh_display) # Refresh after layout restore

        # Initial setup
        self._create_pygame_surface() # Create initial surface
        self.timer.start()

        print("LevelViewWidget initialized (Direct Paint)")

    # Removed initialize_new_level - handled by core_logic + refresh_display
    # Removed load_level_data - handled by core_logic + refresh_display

    def _create_pygame_surface(self):
        """Creates or recreates the off-screen Pygame surface."""
        try:
            # Ensure Pygame is initialized (needed for surface creation)
            if not pygame.get_init():
                pygame.init()
            self.pygame_surface = pygame.Surface((self.level_width, self.level_height))
            print(f"Pygame surface created/resized to {self.level_width}x{self.level_height}")
        except pygame.error as e:
            print(f"Error creating Pygame surface: {e}")
            # Create a small fallback surface
            self.level_width, self.level_height = 320, 180
            try:
                self.pygame_surface = pygame.Surface((self.level_width, self.level_height))
                print("Created fallback Pygame surface (320x180)")
            except pygame.error as e2:
                print(f"FATAL: Could not create even fallback Pygame surface: {e2}")
                self.pygame_surface = None # Indicate critical failure

    def refresh_display(self):
        """Updates the view based on the current state in core_logic."""
        print("LevelView refreshing display...")
        # Get current level dimensions from core_logic
        level_props = self.core_logic.get_level_properties()
        new_width = level_props.get("width", self.level_width) # Use width/height keys
        new_height = level_props.get("height", self.level_height)

        # Resize Pygame surface if dimensions changed
        if new_width != self.level_width or new_height != self.level_height:
            print(f"Level dimensions changing from {self.level_width}x{self.level_height} to {new_width}x{new_height}")
            # 1. Update internal dimensions
            self.level_width = new_width
            self.level_height = new_height

            # 2. Recreate the Pygame surface
            self._create_pygame_surface()

            # 3. Update widget geometry hint and trigger layout recalc/repaint
            self.updateGeometry() # Signal that sizeHint may have changed
            self.update() # Schedule a repaint

        # Deselect object if it no longer exists in core_logic
        if self.selected_object_id is not None:
             if self.core_logic.get_object_by_id(self.selected_object_id) is None:
                 self.deselect_object() # This will emit the signal

        # Always trigger a repaint, even if dimensions didn't change
        # (e.g., objects might have been added/deleted)
        self.update()


    # Removed showEvent

    def update_pygame(self):
        """Update and redraw the internal Pygame surface."""
        if not self.pygame_surface: # Check if surface creation failed
            return

        # --- Drawing onto self.pygame_surface ---
        self.pygame_surface.fill((40, 44, 52)) # Background color

        # Draw Arena Boundary
        arena_rect = pygame.Rect(0, 0, self.level_width, self.level_height)
        pygame.draw.rect(self.pygame_surface, (100, 100, 100), arena_rect, 1)

        # Draw Grid
        if self.grid_enabled:
            self.draw_grid() # Pass surface to draw_grid

        # Draw Placed Objects from core_logic
        placed_objects = self.core_logic.level_objects # Get current objects
        for obj_data in placed_objects:
            obj_type = obj_data.get('type', 'unknown')
            obj_id = obj_data.get('id') # Get ID early

            if obj_type == 'sprite':
                image_path = obj_data.get('image_path')
                x = obj_data.get('x', 0) # Use defaults for safety
                y = obj_data.get('y', 0)
                w = obj_data.get('width', 32) # Use placeholder size as default
                h = obj_data.get('height', 32)


                sprite_surface = None
                if image_path:
                    if image_path not in self.sprite_cache:
                        try:
                            # Construct full path relative to workspace root
                            # Assuming workspace is c:/Users/Johnny/Documents/Workspaces/Ping/Ping-2
                            base_path = "." # Use relative path from workspace root
                            relative_folder = os.path.join("Ping Assets", "Images", "Sprites")
                            full_path = os.path.join(base_path, relative_folder, image_path)
                            # Ensure correct separators for OS
                            full_path = os.path.normpath(full_path)

                            print(f"Loading sprite: {full_path}") # Debugging
                            # Ensure Pygame is initialized (should be)
                            if pygame.get_init():
                                loaded_image = pygame.image.load(full_path).convert_alpha()
                                self.sprite_cache[image_path] = loaded_image
                                print(f"Cached sprite: {image_path} - Size: {loaded_image.get_size()}")
                                # TODO: We need to update obj_data['width']/['height'] in core_logic
                                # when image_path changes, likely in the property editor.
                                # This draw loop should just *use* the stored w/h.
                            else:
                                print("Warning: Pygame not initialized, cannot load sprite.")
                                self.sprite_cache[image_path] = None # Mark as failed
                        except FileNotFoundError:
                            print(f"Error: Sprite image not found at {full_path}")
                            self.sprite_cache[image_path] = None # Cache failure
                        except pygame.error as e:
                            print(f"Error loading sprite '{image_path}': {e}")
                            self.sprite_cache[image_path] = None # Cache failure

                    sprite_surface = self.sprite_cache.get(image_path)

                # Use the object's stored dimensions for the bounding/selection rect
                rect = pygame.Rect(x, y, w, h)

                if sprite_surface:
                     # Blit the loaded sprite at its x, y coordinates.
                     self.pygame_surface.blit(sprite_surface, (x, y)) # Blit using top-left

                else:
                    # Draw placeholder if no image or loading failed
                    pygame.draw.rect(self.pygame_surface, (100, 100, 100), rect) # Grey placeholder
                    # Draw an 'X'
                    try: # Pygame font might not be initialized yet
                        if pygame.font.get_init(): # Explicit check
                             font_size = max(10, min(w, h) // 2) # Adjust size reasonably
                             font = pygame.font.SysFont(None, font_size) # Simple font
                             text_surf = font.render('X', True, (255, 0, 0)) # Red X
                             text_rect = text_surf.get_rect(center=rect.center)
                             self.pygame_surface.blit(text_surf, text_rect)
                        else: print("Warning: Pygame font not init for placeholder X")
                    except Exception as e:
                        print(f"Warning: Could not draw placeholder text: {e}")


                # Draw selection highlight using the object's bounding box
                if obj_id == self.selected_object_id:
                    pygame.draw.rect(self.pygame_surface, (255, 255, 0), rect, 2)

            else: # --- Existing logic for non-sprite objects ---
                # Get position/size directly from obj_data
                x = obj_data.get('x')
                y = obj_data.get('y')
                w = obj_data.get('width')
                h = obj_data.get('height')
                size = obj_data.get('size') # For ball/powerup

                rect = None
                # Construct rect based on available data
                if x is not None and y is not None:
                    if w is not None and h is not None:
                        # Standard object with width/height
                        rect = pygame.Rect(x, y, w, h)
                    elif size is not None:
                        # Object defined by center x, y and size (like BallSpawn)
                        # Correcting potential center-to-top-left issue from original:
                        # If x,y are center, top-left is (x-size/2, y-size/2)
                        rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
                    else: # Added case: if x,y but no w,h,size -> treat as point? or small rect?
                        rect = pygame.Rect(x, y, 1, 1) # Treat as point

                # Fallback for older data format
                elif 'rect' in obj_data and isinstance(obj_data['rect'], pygame.Rect):
                     rect = obj_data['rect']
                     print(f"Warning: Using legacy rect format for object ID {obj_id}")


                if rect:
                    # Pass the full object data to get_object_color for context
                    color = self.get_object_color(obj_data)
                    pygame.draw.rect(self.pygame_surface, color, rect) # Draw on internal surface

                    # Draw selection highlight
                    if obj_id == self.selected_object_id:
                        pygame.draw.rect(self.pygame_surface, (255, 255, 0), rect, 2) # Draw on internal surface

        # --- Trigger Qt Repaint ---
        # Don't flip Pygame display, just update the Qt widget
        self.update() # Schedule paintEvent


    def get_object_color(self, obj_data):
        """Returns a distinct color based on the object's data."""
        obj_type = obj_data.get('type', 'unknown')
        is_left = obj_data.get('is_left', None) # Check for paddle side

        # Default colors
        colors = {
            "paddle_spawn": (0, 255, 0), # Default Green
            "ball_spawn": (255, 255, 255), # White
            "obstacle": (165, 42, 42), # Brown
            "goal": (0, 0, 200), # Blue
            "portal": (255, 0, 255), # Magenta
            "powerup": (0, 255, 255), # Cyan
            "manhole": (128, 128, 128), # Grey
            "unknown": (255, 165, 0) # Orange
        }

        # Specific color logic
        if obj_type == "paddle_spawn":
            if is_left is False: # Check if it's the right paddle
                return (255, 0, 0) # Red
            else:
                return colors["paddle_spawn"] # Green for left or unspecified
        else:
            # Handle specific types if needed, otherwise use base type
            base_type = obj_type.split('_')[0]
            return colors.get(obj_type, colors.get(base_type, colors["unknown"]))


    def _place_object_at(self, obj_type_key, x, y):
        """Creates object data with defaults and adds it via core_logic."""
        defaults = self.main_window.object_palette.get_selected_object_defaults()
        if not defaults:
            print(f"Error: Could not get defaults for {obj_type_key}")
            return

        # Get dimensions from defaults
        width = defaults.get('width')
        height = defaults.get('height')
        size = defaults.get('size') # For ball/powerup
        radius = defaults.get('radius') # Check for radius

        place_x, place_y = x, y
        obj_w, obj_h = 0, 0

        if width is not None and height is not None:
            # Standard width/height object
            obj_w, obj_h = width, height
            place_x -= obj_w // 2 # Center placement
            place_y -= obj_h // 2
        elif size is not None:
            # Object defined by size (e.g., BallSpawn)
            obj_w, obj_h = size, size
            place_x -= obj_w // 2 # Center placement
            place_y -= obj_h // 2
        elif radius is not None:
            # Object defined by radius (e.g., RouletteSpinner, Bumper)
            obj_w = obj_h = radius * 2
            place_x -= radius # Center placement using radius
            place_y -= radius
        elif obj_type_key == "sprite":
            # Sprite - Use placeholder size initially
            print(f"Placing sprite '{obj_type_key}'. Using placeholder 32x32 size.")
            obj_w, obj_h = 32, 32
            place_x -= obj_w // 2 # Center placement
            place_y -= obj_h // 2
        else:
            # Fallback if no dimensions found
            print(f"Warning: No width/height, size, or radius found in defaults for {obj_type_key}. Using 10x10.")
            obj_w, obj_h = 10, 10
            place_x -= 5
            place_y -= 5

        # Snap initial placement to grid if enabled
        if self.grid_enabled:
            place_x, place_y = self.snap_to_grid(place_x, place_y)

        # Ensure placement is within bounds after potential snapping
        place_x = max(0, min(place_x, self.level_width - obj_w))
        place_y = max(0, min(place_y, self.level_height - obj_h))

        # Prepare object data using defaults + position
        new_obj_data = defaults.copy() # Start with defaults
        new_obj_data['x'] = place_x
        new_obj_data['y'] = place_y
        # Ensure width/height/size/radius are set correctly based on what was found/calculated
        if width is not None and height is not None:
            new_obj_data['width'] = obj_w
            new_obj_data['height'] = obj_h
        elif size is not None:
            new_obj_data['size'] = obj_w # size is width/height
        elif radius is not None:
            # Store both radius and calculated width/height for consistency
            new_obj_data['radius'] = radius
            new_obj_data['width'] = obj_w
            new_obj_data['height'] = obj_h
        elif obj_type_key == "sprite":
             new_obj_data['width'] = obj_w # Store placeholder size
             new_obj_data['height'] = obj_h
             new_obj_data['image_path'] = defaults.get('image_path', '') # Ensure image_path is set

        # Add via core logic (which assigns ID)
        self.core_logic.add_object(new_obj_data)
        self.levelModified.emit(True) # Signal modification


    def select_object(self, obj_id):
        """Selects the object with the given ID."""
        if self.selected_object_id != obj_id:
            self.selected_object_id = obj_id
            self.is_dragging = False # Reset dragging state on new selection
            print(f"Selected object ID: {self.selected_object_id}")
            self.objectSelected.emit(self.selected_object_id) # Emit signal
            self.update() # Redraw needed for highlight

    def deselect_object(self):
        """Deselects the currently selected object."""
        if self.selected_object_id is not None:
            print(f"Deselecting object ID: {self.selected_object_id}")
            self.selected_object_id = None
            self.is_dragging = False
            self.objectSelected.emit(None) # Emit signal
            self.update() # Redraw needed to remove highlight

    def _handle_object_update(self, obj_id):
        """Handles the core signal indicating an object's properties have changed."""
        print(f"LevelView received objectUpdated signal for ID: {obj_id}.")

        # Check if the updated object is a sprite and clear its cache entry
        obj_data = self.core_logic.get_object_by_id(obj_id) # Get a fresh copy of data
        if obj_data and obj_data.get('type') == 'sprite':
            image_path = obj_data.get('image_path')
            if image_path and image_path in self.sprite_cache:
                try:
                    del self.sprite_cache[image_path]
                    print(f"Removed '{image_path}' from sprite cache for object {obj_id} due to update.")
                except KeyError:
                    print(f"Warning: Tried to remove '{image_path}' from cache for object {obj_id}, but key didn't exist.")
            elif image_path:
                 print(f"Sprite {obj_id} updated, path '{image_path}' wasn't in cache (will be loaded on draw).")


        # Trigger a repaint. The drawing logic will now fetch the latest data
        # and reload the sprite image if it was removed from cache.
        self.update()


    # --- Mouse Events ---
    def mousePressEvent(self, event):
        if not self.pygame_surface or event.button() != Qt.MouseButton.LeftButton:
            return

        selected_tool = self.main_window.get_selected_tool()
        widget_pos = event.pos()

        # Map widget coordinates to Pygame surface coordinates (considering centering offset)
        pygame_x = widget_pos.x() - self.render_offset_x
        pygame_y = widget_pos.y() - self.render_offset_y

        # Check if the click is within the Pygame surface bounds
        if 0 <= pygame_x < self.level_width and 0 <= pygame_y < self.level_height:
            # --- Tool Logic (using pygame_x, pygame_y) --- Corrected Indentation
            clicked_obj_id = None
            # Find which object was clicked (if any)
            # Iterate in reverse to get topmost object
            for obj_data in reversed(self.core_logic.level_objects):
                 # Get position/size directly from obj_data for collision check
                 x = obj_data.get('x')
                 y = obj_data.get('y')
                 w = obj_data.get('width')
                 h = obj_data.get('height')
                 size = obj_data.get('size') # For ball/powerup
                 rect = None
                 # Construct rect based on available data
                 if x is not None and y is not None:
                     if w is not None and h is not None:
                         # Standard object with width/height
                         rect = pygame.Rect(x, y, w, h)
                     elif size is not None:
                         # Object defined by center x, y and size (like BallSpawn)
                         rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
                 # Fallback for older data format
                 elif 'rect' in obj_data and isinstance(obj_data['rect'], pygame.Rect):
                      rect = obj_data['rect']

                 # Perform collision check if rect was successfully constructed
                 if rect and rect.collidepoint(pygame_x, pygame_y):
                     clicked_obj_id = obj_data.get('id')
                     break # Found the topmost clicked object

            if selected_tool == TOOL_ERASER:
                if clicked_obj_id:
                    # Prevent erasing default paddles (assuming they have specific IDs or types)
                    # TODO: Add more robust check for default/uneditable objects
                    obj_data = self.core_logic.get_object_by_id(clicked_obj_id)
                    if obj_data and "paddle_spawn" in obj_data.get("type", ""):
                         print(f"Cannot erase default object: {clicked_obj_id}")
                    else:
                        print(f"Erasing object ID: {clicked_obj_id}")
                        if self.selected_object_id == clicked_obj_id:
                            self.deselect_object() # Deselect first, emits signal
                        self.core_logic.delete_object(clicked_obj_id)
                        self.levelModified.emit(True)
                else:
                    print("Eraser clicked on empty space.")

            elif selected_tool == TOOL_SELECT:
                if clicked_obj_id:
                    # Prevent selecting default paddles
                    obj_data = self.core_logic.get_object_by_id(clicked_obj_id)
                    if obj_data and "paddle_spawn" in obj_data.get("type", ""):
                         print(f"Cannot select default object: {clicked_obj_id}")
                         self.deselect_object() # Deselect if something else was selected
                    else:
                        self.select_object(clicked_obj_id) # Selects and emits signal
                        self.is_dragging = True
                        # Calculate offset
                        selected_obj_data = self.core_logic.get_object_by_id(self.selected_object_id)
                        # Get x, y directly from the object data
                        obj_x = selected_obj_data.get('x', 0)
                        obj_y = selected_obj_data.get('y', 0)
                        self.drag_offset = (pygame_x - obj_x, pygame_y - obj_y)
                else:
                    # Clicked empty space
                    self.deselect_object() # Deselects and emits signal

            elif selected_tool: # Placement tool from palette
                 self.deselect_object() # Deselect before placing
                 self._place_object_at(selected_tool, pygame_x, pygame_y)

            else: # No tool selected - treat as select
                 if clicked_obj_id:
                    obj_data = self.core_logic.get_object_by_id(clicked_obj_id)
                    if obj_data and "paddle_spawn" in obj_data.get("type", ""):
                         print(f"Cannot select default object: {clicked_obj_id}")
                         self.deselect_object()
                    else:
                        self.select_object(clicked_obj_id)
                        self.is_dragging = True
                        selected_obj_data = self.core_logic.get_object_by_id(self.selected_object_id)
                        # Get x, y directly from the object data
                        obj_x = selected_obj_data.get('x', 0)
                        obj_y = selected_obj_data.get('y', 0)
                        self.drag_offset = (pygame_x - obj_x, pygame_y - obj_y)
                 else:
                    self.deselect_object()

        event.accept()

    def mouseMoveEvent(self, event):
        if not self.pygame_surface or not self.is_dragging or self.selected_object_id is None:
            return

        widget_pos = event.pos()
        # Map widget coordinates to Pygame surface coordinates
        pygame_x = widget_pos.x() - self.render_offset_x
        pygame_y = widget_pos.y() - self.render_offset_y

        # We only care about dragging *within* the surface bounds for updating position
        # (Clamping happens later anyway)
        # No explicit bounds check needed here unless we want to stop dragging if mouse leaves widget

        selected_obj_data = self.core_logic.get_object_by_id(self.selected_object_id)
        if not selected_obj_data: return # Safety check

        # Get properties from the object data itself, not nested 'properties'
        # props = selected_obj_data.get('properties', {}) # Old structure?
        props = selected_obj_data # Use the main object dict

        # Get dimensions directly from object data
        obj_w = props.get('width')
        obj_h = props.get('height')
        size = props.get('size')
        if obj_w is None and size is not None: obj_w = size
        if obj_h is None and size is not None: obj_h = size
        if obj_w is None or obj_h is None:
            print(f"Warning: Could not determine size for dragging object {self.selected_object_id}. Using 10x10.")
            obj_w, obj_h = 10, 10 # Fallback

        # Calculate new top-left based on mapped Pygame coords and offset
        # Note: drag_offset was calculated relative to Pygame coords in mousePressEvent
        new_x = pygame_x - self.drag_offset[0]
        new_y = pygame_y - self.drag_offset[1]

        # Clamp position within Pygame surface bounds
        new_x = max(0, min(new_x, self.level_width - obj_w)) # obj_w/h calculated above
        new_y = max(0, min(new_y, self.level_height - obj_h))

        # Snap dragged position to grid if enabled
        snapped_x, snapped_y = new_x, new_y
        if self.grid_enabled:
            snapped_x, snapped_y = self.snap_to_grid(new_x, new_y)
            # Re-clamp after snapping
            snapped_x = max(0, min(snapped_x, self.level_width - obj_w))
            snapped_y = max(0, min(snapped_y, self.level_height - obj_h))

        # Update object properties in core logic
        # Check if position actually changed to avoid unnecessary updates/signals
        current_x = props.get('x')
        current_y = props.get('y')
        if current_x != snapped_x or current_y != snapped_y:
            self.core_logic.update_object_properties(self.selected_object_id, {'x': snapped_x, 'y': snapped_y})
            self.levelModified.emit(True)
            # Update property editor display if it's showing this object
            self.main_window.property_editor.update_display(self.selected_object_id)


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            print(f"Finished dragging object ID: {self.selected_object_id}")
            self.is_dragging = False
            # Final snap handled during move now
            # TODO: Add undo state here?
        # event.accept()

    # --- Grid Methods ---
    def toggle_grid(self, enabled):
        """Turns the grid display and snapping on or off."""
        self.grid_enabled = enabled
        print(f"Grid snapping {'enabled' if enabled else 'disabled'}")

    def snap_to_grid(self, x, y):
        """Snaps the given coordinates to the nearest grid intersection."""
        snapped_x = round(x / self.grid_size) * self.grid_size
        snapped_y = round(y / self.grid_size) * self.grid_size
        return snapped_x, snapped_y

    def draw_grid(self): # Now draws on self.pygame_surface
        """Draws the grid lines on the Pygame surface."""
        if not self.pygame_surface: return
        for x in range(0, self.level_width, self.grid_size):
            pygame.draw.line(self.pygame_surface, self.grid_color, (x, 0), (x, self.level_height))
        for y in range(0, self.level_height, self.grid_size):
            pygame.draw.line(self.pygame_surface, self.grid_color, (0, y), (self.level_width, y))

# Removed draw_translation_handles

    # --- Size Hint ---
    def sizeHint(self):
        """Provide a size hint based on the Pygame container size."""
        # Use current level dimensions as the hint
        # This tells the layout system the preferred size
        return QSize(self.level_width, self.level_height)

    # minimumSizeHint can still provide a fallback if needed
    # def minimumSizeHint(self):
    #     """Provide a minimum size hint."""
    #     return QSize(320, 180)

    # --- Paint Event ---
    def paintEvent(self, event):
        """Draws the Pygame surface onto the widget."""
        if not self.pygame_surface:
            # Optionally draw an error message if surface failed
            super().paintEvent(event) # Draw background
            return

        painter = QPainter(self)
        widget_size = self.size()
        surface_size = self.pygame_surface.get_size()

        # Calculate top-left corner for centering
        self.render_offset_x = max(0, (widget_size.width() - surface_size[0]) // 2)
        self.render_offset_y = max(0, (widget_size.height() - surface_size[1]) // 2)

        # Fill background if widget is larger than surface
        painter.fillRect(self.rect(), QColor("#101010"))

        # Convert Pygame surface to QImage
        # Format might need adjustment based on Pygame surface format (RGB vs RGBA)
        # Assuming 32-bit surface (like default Pygame display)
        # If using 24-bit, format might be QImage.Format.Format_RGB888
        # Check pygame_surface.get_bitsize() if issues arise
        bytes_per_line = self.pygame_surface.get_pitch()
        qimage_format = QImage.Format.Format_RGB32 # Common default, adjust if needed
        if self.pygame_surface.get_flags() & pygame.SRCALPHA:
             qimage_format = QImage.Format.Format_ARGB32_Premultiplied

        # Get buffer view - requires Pygame 2+ ?
        try:
             buffer = self.pygame_surface.get_buffer()
             qimage = QImage(buffer.raw, surface_size[0], surface_size[1], bytes_per_line, qimage_format)
        except ValueError as e: # Fallback for older Pygame? Or if buffer fails
             print(f"Warning: Pygame get_buffer() failed ({e}), using slower tostring method.")
             image_string = pygame.image.tostring(self.pygame_surface, "RGBX") # Or "RGBA" if alpha
             qimage = QImage(image_string, surface_size[0], surface_size[1], QImage.Format.Format_RGB32)


        # Draw the QImage onto the widget at the calculated offset
        painter.drawImage(self.render_offset_x, self.render_offset_y, qimage)

        painter.end()


    # --- Tool Handling ---
    def set_active_tool(self, tool_id):
        """Informs the view about the currently active tool."""
        # This method might be used later for cursor changes or tool-specific drawing
        print(f"LevelView notified of active tool: {tool_id}")
        # If switching away from select tool, ensure nothing is selected
        if tool_id != TOOL_SELECT and self.selected_object_id is not None:
             # Check if the new tool is a placement tool
             if tool_id and tool_id not in [TOOL_ERASER]: # Placement tools are keys from palette
                 self.deselect_object()


    # --- Cleanup ---
    def closeEvent(self, event):
        """Stop the timer when the widget closes."""
        print("LevelViewWidget closing, stopping timer.")
        self.timer.stop()
        super().closeEvent(event)