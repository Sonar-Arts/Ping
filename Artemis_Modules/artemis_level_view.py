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
# Ensure QRect is imported
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QImage, QColor # Added for direct painting

# Import tool constants
from .artemis_tool_palette import TOOL_ERASER, TOOL_SELECT # Import from the new tool palette module

# Import background drawing functions from the main game module
try:
    from Modules.ping_graphics import get_background_draw_function, generate_sludge_texture # Added generate_sludge_texture for potential future use
except ImportError as e:
    print(f"Warning: Could not import from Modules.ping_graphics: {e}")
    get_background_draw_function = None
    generate_sludge_texture = None


print("Artemis Modules/artemis_level_view.py loaded (Pygame)")

# --- Mock Compiler for Background Rendering ---
# This class mimics the structure expected by the background drawing functions
class MockCompiler:
    def __init__(self, view_widget):
        self.view = view_widget
        self.core = view_widget.core_logic
        props = self.core.get_level_properties()

        self.width = self.view.level_width
        self.height = self.view.level_height
        self.scale = 1.0 # Editor scale is fixed at 1.0 for simplicity
        self.offset_x = 0 # No camera offset in editor view like in game
        self.offset_y = 0
        self.scoreboard_height = props.get("scoreboard_height", 0) # Get from props or default
        # Use level properties for colors, fallback to empty dict
        self.colors = props.get("colors", {})
        # Ensure essential color keys have fallbacks if needed by draw functions
        # (Assuming draw functions handle missing keys gracefully for now)

        self.dt = 1/60.0 # Fixed delta time for editor animation updates

        # Provide object lists (some backgrounds might use specific lists)
        self.level_objects = self.core.level_objects # All objects
        self.manholes = [obj for obj in self.level_objects if obj.get('type') == 'manhole']
        # Add other specific lists if required by other backgrounds

        # Animation state - managed by the view widget itself
        # Ensure the attribute exists on the view widget
        if not hasattr(self.view, 'background_anim_state'):
            self.view.background_anim_state = {}
        self.background_animation_state = self.view.background_anim_state

        # Sludge texture - managed by the view widget (initially None)
        # The draw function should handle this being None
        self.sludge_texture = getattr(self.view, 'cached_sludge_texture', None)

        # Background details - required by some backgrounds like sewer
        self.background_details = props.get("background_details", {}) # Fetch from props, default to empty dict

    def scale_rect(self, rect):
        # Since editor scale is 1.0, this function doesn't need to scale
        # It just needs to handle the offset (which is 0 here)
        if isinstance(rect, pygame.Rect):
            # Return a *copy* to avoid modifying the original rect if passed by reference
            return rect.copy()
        elif isinstance(rect, (tuple, list)) and len(rect) == 4:
             # If passed as (x, y, w, h) tuple/list
             return pygame.Rect(rect)
        else:
             # Handle potential point scaling (like in draw_casino_background)
             # Assuming input is (x, y)
             if isinstance(rect, (tuple, list)) and len(rect) == 2:
                  # Return a Rect representing the point (or center if needed)
                  # The original scale_rect_func returned rect.center for points,
                  # let's return a 1x1 rect at the point for simplicity here.
                  return pygame.Rect(rect[0], rect[1], 1, 1)
             else:
                  print(f"Warning: Unsupported type for mock scale_rect: {type(rect)}")
                  return pygame.Rect(0, 0, 0, 0) # Return empty rect on error


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
        self.selected_object_id = None # Track the ID of the currently selected object
        self.is_dragging = False
        self.drag_offset = (0, 0)
        # --- Zoom & Pan ---
        self.zoom_level = 1.0
        self.min_zoom = 0.1 # Minimum zoom factor
        self.max_zoom = 5.0 # Maximum zoom factor
        self.pan_offset_x = 0 # Top-left corner of the visible area in Pygame surface coordinates
        self.pan_offset_y = 0
        self.is_panning = False # For potential middle-mouse panning later
        self.pan_start_pos = None
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
        self.render_offset_x = 0 # Offset for centering drawing (calculated in paintEvent)
        self.render_offset_y = 0
        self.effective_surface_width = 0 # Calculated size after zoom
        self.effective_surface_height = 0

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
        self.background_anim_state = {} # State for background animations (e.g., river offset)
        self.cached_sludge_texture = None # For potentially caching generated textures

        # --- Connect to Core Signals ---
        self.core_logic.levelLoaded.connect(self.refresh_display)
        self.core_logic.levelPropertiesChanged.connect(self.refresh_display) # This will trigger background redraw
        self.core_logic.objectUpdated.connect(self._handle_object_update) # Connect new signal
        self.core_logic.layoutRestored.connect(self.refresh_display) # Refresh after layout restore

        # Initial setup
        self._create_pygame_surface() # Create initial surface
        self._update_effective_surface_size() # Calculate initial scaled size
        self.timer.start()

        print("LevelViewWidget initialized (Direct Paint)")

    def _update_effective_surface_size(self):
        """Calculates the size of the Pygame surface as it appears on the widget."""
        # This is needed for centering calculations in paintEvent
        self.effective_surface_width = int(self.level_width * self.zoom_level)
        self.effective_surface_height = int(self.level_height * self.zoom_level)

    def map_widget_to_pygame(self, widget_pos):
        """Maps widget coordinates to Pygame surface coordinates, considering pan and zoom."""
        # Calculate position relative to the top-left of the *rendered* (potentially scaled) surface
        # Ensure zoom_level is not zero to avoid division errors
        safe_zoom = max(self.zoom_level, 0.0001)
        relative_x = widget_pos.x() - self.render_offset_x
        relative_y = widget_pos.y() - self.render_offset_y

        # Scale back to original Pygame coordinates and add pan offset
        pygame_x = (relative_x / safe_zoom) + self.pan_offset_x
        pygame_y = (relative_y / safe_zoom) + self.pan_offset_y

        return int(pygame_x), int(pygame_y)

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
            self._update_effective_surface_size() # Update scaled size after resize

            # 3. Update widget geometry hint and trigger layout recalc/repaint
            self.updateGeometry() # Signal that sizeHint may have changed
            # Consider resetting pan/zoom or clamping pan after resize? For now, just update size.
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
        # --- Drawing onto self.pygame_surface ---
        # Get background ID from core logic properties
        level_props = self.core_logic.get_level_properties()
        # Use the correct key "level_background" as indicated by debug output
        background_id = level_props.get("level_background")

        draw_func = None
        if background_id and get_background_draw_function:
            draw_func = get_background_draw_function(background_id)
        # Removed debug prints for background ID and function finding

        if draw_func:
            try:
                # --- Special Handling for Sewer Sludge Texture ---
                if background_id == "sewer":
                    # Check if texture needs generation/regeneration
                    regen_needed = False
                    current_dims = (int(self.level_width), int(self.level_height))
                    if self.cached_sludge_texture is None:
                        regen_needed = True
                    elif self.cached_sludge_texture.get_size() != current_dims:
                        regen_needed = True

                    if regen_needed and generate_sludge_texture:
                        # Use colors from level props, or provide defaults if missing
                        colors = level_props.get("colors", {})
                        sludge_colors = {
                            'SLUDGE_MID': colors.get('SLUDGE_MID', (80, 85, 60)),
                            'SLUDGE_HIGHLIGHT': colors.get('SLUDGE_HIGHLIGHT', (100, 105, 75))
                        }
                        # Generate texture (scale is 1.0 in editor)
                        tex_width = max(1, int(self.level_width))
                        tex_height = max(1, int(self.level_height))
                        self.cached_sludge_texture = generate_sludge_texture(
                            tex_width, tex_height, 1.0, sludge_colors
                        )
                        # Removed debug prints for sludge generation
                    elif not generate_sludge_texture and regen_needed:
                         print("[LevelView.update_pygame] Warning: Cannot generate sludge: generate_sludge_texture is None.") # Keep this warning
                elif self.cached_sludge_texture is not None and background_id != "sewer":
                     # Clear cached texture if switching away from sewer
                     self.cached_sludge_texture = None


                # Create the mock compiler instance to pass necessary info
                mock_compiler = MockCompiler(self)
                # Call the specific background drawing function
                draw_func(self.pygame_surface, mock_compiler)
            except Exception as e:
                print(f"Error drawing background '{background_id}': {e}")
                import traceback
                traceback.print_exc() # Print full traceback for debugging
                # Fallback to solid color on error
                self.pygame_surface.fill((40, 44, 52))
        else:
            # Default background if none selected or function not found
            self.pygame_surface.fill((40, 44, 52))
            if background_id:
                 # Keep this warning if the ID exists but function doesn't
                 print(f"Warning: Background '{background_id}' selected but draw function not found.")
            # Clear cached texture if no background is selected
            if self.cached_sludge_texture is not None:
                 self.cached_sludge_texture = None


        # Draw Arena Boundary (Over the background)
        arena_rect = pygame.Rect(0, 0, self.level_width, self.level_height)
        pygame.draw.rect(self.pygame_surface, (100, 100, 100), arena_rect, 1)

        # Draw Grid
        if self.grid_enabled:
            self.draw_grid() # Pass surface to draw_grid

        # Draw Placed Objects from core_logic
        placed_objects = self.core_logic.level_objects # Get current objects
        for obj_data in placed_objects:
            obj_type = obj_data.get('type', 'unknown')
            obj_id = obj_data.get('id')
            x = obj_data.get('x', 0)
            y = obj_data.get('y', 0)
            w = obj_data.get('width', 32)
            h = obj_data.get('height', 32)
            size = obj_data.get('size') # For ball/powerup, etc.

            # Define the bounding box for drawing and selection
            # Use width/height if available, otherwise size for circular/square objects
            if w is not None and h is not None:
                obj_rect = pygame.Rect(x, y, w, h)
            elif size is not None:
                 # Assume x,y is center for size-based objects
                 obj_rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
            else:
                 obj_rect = pygame.Rect(x, y, 10, 10) # Fallback small rect

            # --- Determine how to draw based on type ---
            is_paddle = "paddle_spawn" in obj_type
            is_generic_sprite = obj_type == 'sprite'

            sprite_to_draw = None
            draw_placeholder = False
            placeholder_color = (100, 100, 100) # Default grey

            if is_paddle:
                paddle_sprite_path = "Protag Paddle.webp" if obj_type == "paddle_spawn_left" else "Anttag Paddle.webp"
                # --- Debug Print for Left Paddle ---
                if obj_type == "paddle_spawn_left":
                    # print(f"DEBUG: Attempting to load left paddle with path: {paddle_sprite_path}") # Removed excessive debug print
                    pass # Add pass to maintain block structure if needed
                # --- End Debug Print ---
                if paddle_sprite_path not in self.sprite_cache:
                    try:
                        base_path = "."
                        relative_folder = os.path.join("Ping Assets", "Images", "Sprites")
                        full_path = os.path.normpath(os.path.join(base_path, relative_folder, paddle_sprite_path))
                        print(f"Loading paddle sprite: {full_path}")
                        if pygame.get_init():
                            loaded_image = pygame.image.load(full_path) # Removed .convert_alpha()
                            target_w = obj_data.get('width', 30) # Use new default width 30
                            target_h = obj_data.get('height', 100)
                            if loaded_image.get_size() != (target_w, target_h):
                                print(f"Resizing paddle sprite '{paddle_sprite_path}' from {loaded_image.get_size()} to ({target_w}, {target_h})")
                                loaded_image = pygame.transform.smoothscale(loaded_image, (target_w, target_h))
                            self.sprite_cache[paddle_sprite_path] = loaded_image
                            print(f"Cached paddle sprite: {paddle_sprite_path} - Size: {loaded_image.get_size()}")
                        else:
                            print("Warning: Pygame not initialized, cannot load paddle sprite.")
                            self.sprite_cache[paddle_sprite_path] = None
                    except pygame.error as e: # Catch specific Pygame errors
                        error_msg = pygame.get_error()
                        print(f"Pygame Error loading paddle sprite '{paddle_sprite_path}': {error_msg}")
                        if paddle_sprite_path.lower().endswith(".webp"):
                            print("NOTE: Pygame might not support .webp format without extra libraries (like pygame-webp or specific SDL_image builds).")
                        self.sprite_cache[paddle_sprite_path] = None
                    except Exception as e: # Catch other potential errors (e.g., file not found handled implicitly by pygame.error now)
                        print(f"Unexpected Error loading paddle sprite '{paddle_sprite_path}': {e}")
                        self.sprite_cache[paddle_sprite_path] = None

                sprite_to_draw = self.sprite_cache.get(paddle_sprite_path)
                if not sprite_to_draw:
                    draw_placeholder = True
                    placeholder_color = (200, 0, 0) # Red placeholder for missing paddle

            elif is_generic_sprite:
                image_path = obj_data.get('image_path')
                if image_path:
                    if image_path not in self.sprite_cache:
                        try:
                            base_path = "."
                            relative_folder = os.path.join("Ping Assets", "Images", "Sprites")
                            full_path = os.path.normpath(os.path.join(base_path, relative_folder, image_path))
                            print(f"Loading generic sprite: {full_path}")
                            if pygame.get_init():
                                loaded_image = pygame.image.load(full_path).convert_alpha()
                                # Generic sprites use their loaded size, update object data if needed elsewhere
                                self.sprite_cache[image_path] = loaded_image
                                print(f"Cached generic sprite: {image_path} - Size: {loaded_image.get_size()}")
                            else:
                                print("Warning: Pygame not initialized, cannot load generic sprite.")
                                self.sprite_cache[image_path] = None
                        except pygame.error as e: # Catch specific Pygame errors
                            error_msg = pygame.get_error()
                            print(f"Pygame Error loading generic sprite '{image_path}': {error_msg}")
                            if image_path.lower().endswith(".webp"):
                                print("NOTE: Pygame might not support .webp format without extra libraries (like pygame-webp or specific SDL_image builds).")
                            self.sprite_cache[image_path] = None
                        except Exception as e: # Catch other potential errors
                            print(f"Unexpected Error loading generic sprite '{image_path}': {e}")
                            self.sprite_cache[image_path] = None

                    sprite_to_draw = self.sprite_cache.get(image_path)
                    if not sprite_to_draw:
                        draw_placeholder = True
                        placeholder_color = (100, 100, 100) # Grey placeholder for missing generic sprite
                else:
                    # Sprite object with no image path set
                    draw_placeholder = True
                    placeholder_color = (50, 50, 50) # Darker grey for empty sprite object

            # --- Perform Drawing ---
            if sprite_to_draw:
                self.pygame_surface.blit(sprite_to_draw, obj_rect.topleft)
            elif draw_placeholder:
                pygame.draw.rect(self.pygame_surface, placeholder_color, obj_rect)
                # Draw an 'X' on the placeholder
                try:
                    if pygame.font.get_init():
                        font_size = max(10, min(obj_rect.width, obj_rect.height) // 2)
                        font = pygame.font.SysFont(None, font_size)
                        text_surf = font.render('X', True, (255, 255, 255)) # White X
                        text_rect = text_surf.get_rect(center=obj_rect.center)
                        self.pygame_surface.blit(text_surf, text_rect)
                except Exception as e:
                    print(f"Warning: Could not draw placeholder text: {e}")
            elif not is_paddle and not is_generic_sprite:
                # Draw other object types (non-sprite, non-paddle) using color
                color = self.get_object_color(obj_data)
                pygame.draw.rect(self.pygame_surface, color, obj_rect)

            # --- Draw Selection Highlight ---
            if obj_id == self.selected_object_id:
                pygame.draw.rect(self.pygame_surface, (255, 255, 0), obj_rect, 2) # Yellow highlight


        # --- Trigger Qt Repaint ---
        # Don't flip Pygame display, just update the Qt widget
        self.update() # Schedule paintEvent


    def get_object_color(self, obj_data):
        """Returns a distinct color based on the object's data. (Excludes paddle spawns now)"""
        obj_type = obj_data.get('type', 'unknown')
        # is_left = obj_data.get('is_left', None) # No longer needed here

        # Default colors (Paddle spawn removed as it's handled by sprite drawing)
        colors = {
            # "paddle_spawn": (0, 255, 0), # Handled by sprite drawing
            "ball_spawn": (255, 255, 255), # White
            "obstacle": (165, 42, 42), # Brown
            "goal": (0, 0, 200), # Blue
            "portal": (255, 0, 255), # Magenta
            "powerup": (0, 255, 255), # Cyan
            "manhole": (128, 128, 128), # Grey
            "unknown": (255, 165, 0) # Orange
        }

        # Specific color logic (Paddle spawn removed)
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
        if not self.pygame_surface:
             return

        # Handle panning with middle mouse button
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.pan_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        if event.button() != Qt.MouseButton.LeftButton:
            return

        selected_tool = self.main_window.get_selected_tool()
        widget_pos = event.pos()

        # Map widget coordinates to Pygame surface coordinates using the helper
        pygame_x, pygame_y = self.map_widget_to_pygame(widget_pos)

        # Check if the click is within the *logical* Pygame surface bounds
        # (The mapped coordinates could be outside if panning/zooming near edge)
        if 0 <= pygame_x < self.level_width and 0 <= pygame_y < self.level_height:
            # --- Tool Logic (using pygame_x, pygame_y) --- #
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
                 if rect and rect.collidepoint(pygame_x, pygame_y): # Use mapped coords
                     clicked_obj_id = obj_data.get('id')
                     break # Found the topmost clicked object

            if selected_tool == TOOL_ERASER:
                if clicked_obj_id:
                    # Prevent erasing default paddles
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
                    # Allow selecting paddles, but dragging will be prevented later
                    self.select_object(clicked_obj_id) # Selects and emits signal
                    self.is_dragging = True
                    # Calculate offset using mapped Pygame coords
                    selected_obj_data = self.core_logic.get_object_by_id(self.selected_object_id)
                    obj_x = selected_obj_data.get('x', 0)
                    obj_y = selected_obj_data.get('y', 0)
                    self.drag_offset = (pygame_x - obj_x, pygame_y - obj_y) # Use mapped coords
                else:
                    # Clicked empty space
                    self.deselect_object() # Deselects and emits signal

            elif selected_tool: # Placement tool from palette
                 self.deselect_object() # Deselect before placing
                 self._place_object_at(selected_tool, pygame_x, pygame_y) # Use mapped coords

            else: # No tool selected - treat as select
                 if clicked_obj_id:
                    # Allow selecting paddles, but dragging will be prevented later
                    self.select_object(clicked_obj_id)
                    self.is_dragging = True
                    selected_obj_data = self.core_logic.get_object_by_id(self.selected_object_id)
                    # Get x, y directly from the object data
                    obj_x = selected_obj_data.get('x', 0)
                    obj_y = selected_obj_data.get('y', 0)
                    self.drag_offset = (pygame_x - obj_x, pygame_y - obj_y) # Use mapped coords
                 else:
                    self.deselect_object()

        # else: click was outside the logical Pygame surface (e.g., in the border area)
        #       We might want to deselect here as well.
        #       For now, do nothing if click is outside logical area.

        event.accept()


    def mouseMoveEvent(self, event):
        if not self.pygame_surface:
            return

        # Handle panning
        if self.is_panning and self.pan_start_pos:
            delta = event.pos() - self.pan_start_pos
            # Adjust pan offset based on mouse movement, scaled by zoom
            # Ensure zoom_level is not zero
            safe_zoom = max(self.zoom_level, 0.0001)
            self.pan_offset_x -= delta.x() / safe_zoom
            self.pan_offset_y -= delta.y() / safe_zoom

            # Clamp pan offsets
            widget_size = self.size()
            visible_pygame_width = widget_size.width() / safe_zoom
            visible_pygame_height = widget_size.height() / safe_zoom
            max_pan_x = max(0, self.level_width - visible_pygame_width)
            max_pan_y = max(0, self.level_height - visible_pygame_height)
            self.pan_offset_x = max(0, min(self.pan_offset_x, max_pan_x))
            self.pan_offset_y = max(0, min(self.pan_offset_y, max_pan_y))

            self.pan_start_pos = event.pos() # Update start pos for next delta
            self.update() # Trigger repaint
            event.accept()
            return

        # Handle dragging selected object
        if not self.is_dragging or self.selected_object_id is None:
            return

        selected_obj_data = self.core_logic.get_object_by_id(self.selected_object_id)
        if not selected_obj_data: return # Safety check

        # --- Prevent dragging paddles ---
        if "paddle_spawn" in selected_obj_data.get("type", ""):
            # print("Cannot drag paddle spawn.") # Optional debug message
            return # Do not proceed with move logic for paddles
        # --- End Prevent dragging paddles ---

        widget_pos = event.pos()
        # Map widget coordinates to Pygame surface coordinates
        pygame_x, pygame_y = self.map_widget_to_pygame(widget_pos)

        # Dragging logic remains mostly the same, but uses the mapped pygame_x, pygame_y
        # to calculate the new position. Clamping should still happen against
        # self.level_width and self.level_height.

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
        new_x = pygame_x - self.drag_offset[0]
        new_y = pygame_y - self.drag_offset[1]

        # Clamp position within Pygame surface bounds
        new_x = max(0, min(new_x, self.level_width - obj_w))
        new_y = max(0, min(new_y, self.level_height - obj_h))

        # Snap dragged position to grid if enabled
        snapped_x, snapped_y = new_x, new_y
        if self.grid_enabled:
            snapped_x, snapped_y = self.snap_to_grid(new_x, new_y)
            # Re-clamp after snapping
            snapped_x = max(0, min(snapped_x, self.level_width - obj_w))
            snapped_y = max(0, min(snapped_y, self.level_height - obj_h))

        # Update object properties in core logic
        current_x = props.get('x')
        current_y = props.get('y')
        if current_x != snapped_x or current_y != snapped_y:
            self.core_logic.update_object_properties(self.selected_object_id, {'x': snapped_x, 'y': snapped_y})
            self.levelModified.emit(True)
            # Update property editor display if it's showing this object
            self.main_window.property_editor.update_display(self.selected_object_id)
        event.accept()


    def mouseReleaseEvent(self, event):
        # Handle panning release
        if event.button() == Qt.MouseButton.MiddleButton and self.is_panning:
            self.is_panning = False
            self.pan_start_pos = None
            self.unsetCursor() # Restore default cursor
            event.accept()
            return

        # Handle dragging release
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            print(f"Finished dragging object ID: {self.selected_object_id}")
            self.is_dragging = False
            # Final snap handled during move now
            # TODO: Add undo state here?
            event.accept()
            return

        # event.accept() # Accept other releases?


    def wheelEvent(self, event):
        """Handles mouse wheel events for zooming."""
        if not self.pygame_surface: return

        delta = event.angleDelta().y() # Typically +/- 120
        zoom_factor = 1.10 if delta > 0 else 1 / 1.10

        new_zoom = self.zoom_level * zoom_factor
        # Clamp zoom level
        new_zoom = max(self.min_zoom, min(new_zoom, self.max_zoom))

        if new_zoom == self.zoom_level: # No change after clamping
            return

        # --- Zoom towards cursor ---
        widget_mouse_pos = event.position()

        # 1. Get Pygame coordinates under the mouse *before* zoom
        pygame_mouse_x_before, pygame_mouse_y_before = self.map_widget_to_pygame(widget_mouse_pos)

        # 2. Update zoom level
        old_zoom = self.zoom_level
        self.zoom_level = new_zoom
        self._update_effective_surface_size() # Update scaled size for paintEvent centering

        # 3. Calculate where the *widget* mouse position corresponds to in Pygame coords *after* zoom
        #    This requires knowing the render offset *after* zoom, which paintEvent calculates.
        #    To simplify, let's recalculate a potential render offset here based on widget size.
        #    NOTE: This assumes the widget size doesn't change during the zoom event itself.
        widget_size = self.size()
        # Use the *new* effective size for centering calculation
        temp_render_offset_x = max(0, (widget_size.width() - self.effective_surface_width) // 2)
        temp_render_offset_y = max(0, (widget_size.height() - self.effective_surface_height) // 2)

        # Map widget mouse pos again, but only considering the new zoom and the *temporary* render offset
        # We don't add pan_offset here yet, as we are calculating the *new* pan offset.
        relative_x_after = widget_mouse_pos.x() - temp_render_offset_x
        relative_y_after = widget_mouse_pos.y() - temp_render_offset_y
        # Ensure zoom_level is not zero
        safe_zoom = max(self.zoom_level, 0.0001)
        pygame_mouse_x_target = relative_x_after / safe_zoom # Target Pygame X if pan was (0,0)
        pygame_mouse_y_target = relative_y_after / safe_zoom # Target Pygame Y if pan was (0,0)

        # 4. Adjust pan_offset so the Pygame point under the cursor remains the same
        # pan_offset = point_before - point_target
        self.pan_offset_x = pygame_mouse_x_before - pygame_mouse_x_target
        self.pan_offset_y = pygame_mouse_y_before - pygame_mouse_y_target

        # 5. Clamp pan offsets to keep view within bounds
        visible_pygame_width = widget_size.width() / safe_zoom
        visible_pygame_height = widget_size.height() / safe_zoom
        max_pan_x = max(0, self.level_width - visible_pygame_width)
        max_pan_y = max(0, self.level_height - visible_pygame_height)
        self.pan_offset_x = max(0, min(self.pan_offset_x, max_pan_x))
        self.pan_offset_y = max(0, min(self.pan_offset_y, max_pan_y))

        print(f"Zoom: {self.zoom_level:.2f}, Pan: ({int(self.pan_offset_x)}, {int(self.pan_offset_y)})")

        self.update() # Trigger repaint
        event.accept()

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
        """Draws the relevant portion of the Pygame surface onto the widget, scaled and panned."""
        if not self.pygame_surface:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        widget_size = self.size()
        surface_size = self.pygame_surface.get_size() # Full Pygame surface size

        # --- Calculate Source Rect (on Pygame surface) ---
        # Visible area width/height in Pygame coordinates
        # Prevent division by zero if zoom_level is somehow zero
        safe_zoom = max(self.zoom_level, 0.0001)
        visible_pygame_width = widget_size.width() / safe_zoom
        visible_pygame_height = widget_size.height() / safe_zoom

        # Clamp pan offsets again here to be safe, considering current widget size
        max_pan_x = max(0, self.level_width - visible_pygame_width)
        max_pan_y = max(0, self.level_height - visible_pygame_height)
        clamped_pan_x = max(0, min(self.pan_offset_x, max_pan_x))
        clamped_pan_y = max(0, min(self.pan_offset_y, max_pan_y))

        # Ensure source rect dimensions are not larger than the surface itself
        # Use max(1, ...) to prevent zero-width/height rects which subsurface might reject
        src_width = max(1, min(visible_pygame_width, self.level_width - clamped_pan_x))
        src_height = max(1, min(visible_pygame_height, self.level_height - clamped_pan_y))

        # Define the rectangle on the source Pygame surface to draw from
        src_rect = pygame.Rect(
            int(clamped_pan_x),
            int(clamped_pan_y),
            int(src_width),
            int(src_height)
        )

        # --- Calculate Destination Rect (on QWidget) ---
        # Calculate the size the source rect will be drawn at on the widget
        dest_draw_width = int(src_rect.width * self.zoom_level)
        dest_draw_height = int(src_rect.height * self.zoom_level)

        # Calculate centering offset for the *drawn* content within the widget
        # Use the calculated dest_draw_width/height, not the full effective_surface_width/height
        # Store these offsets as they are needed by map_widget_to_pygame
        self.render_offset_x = max(0, (widget_size.width() - dest_draw_width) // 2)
        self.render_offset_y = max(0, (widget_size.height() - dest_draw_height) // 2)

        # Define the rectangle on the widget where the scaled image will be drawn
        dest_rect = QRect(
            self.render_offset_x,
            self.render_offset_y,
            dest_draw_width,
            dest_draw_height
        )

        # Fill background for areas outside the drawn content
        painter.fillRect(self.rect(), QColor("#101010"))

        # --- Convert relevant part of Pygame surface to QImage ---
        # Optimization: Only convert the needed sub-surface if possible
        qimage = None # Initialize qimage
        try:
            # Ensure src_rect dimensions are valid before calling subsurface
            if src_rect.width > 0 and src_rect.height > 0 and \
               src_rect.x >= 0 and src_rect.y >= 0 and \
               src_rect.right <= self.pygame_surface.get_width() and \
               src_rect.bottom <= self.pygame_surface.get_height():

                sub_surface = self.pygame_surface.subsurface(src_rect)
                bytes_per_line = sub_surface.get_pitch()
                qimage_format = QImage.Format.Format_RGB32
                if sub_surface.get_flags() & pygame.SRCALPHA:
                    qimage_format = QImage.Format.Format_ARGB32_Premultiplied

                buffer = sub_surface.get_buffer()
                # Create QImage without copying if possible
                qimage = QImage(buffer.raw, src_rect.width, src_rect.height, bytes_per_line, qimage_format)
            else:
                 print(f"Warning: Invalid src_rect for subsurface: {src_rect}, Surface size: {self.pygame_surface.get_size()}")
                 # Create a tiny dummy QImage if src_rect is invalid
                 qimage = QImage(1, 1, QImage.Format.Format_RGB32)
                 qimage.fill(Qt.GlobalColor.black)


        except (ValueError, IndexError) as e: # Catch potential subsurface or buffer errors
            print(f"Warning: Pygame subsurface/get_buffer() failed ({e}), using slower full surface conversion.")
            # Convert the *entire* surface first (less efficient)
            full_bytes_per_line = self.pygame_surface.get_pitch()
            full_qimage_format = QImage.Format.Format_RGB32
            if self.pygame_surface.get_flags() & pygame.SRCALPHA:
                full_qimage_format = QImage.Format.Format_ARGB32_Premultiplied
            try:
                full_buffer = self.pygame_surface.get_buffer()
                full_qimage = QImage(full_buffer.raw, surface_size[0], surface_size[1], full_bytes_per_line, full_qimage_format)
            except ValueError: # Even fuller fallback
                 image_string = pygame.image.tostring(self.pygame_surface, "RGBX") # Or "RGBA"
                 full_qimage = QImage(image_string, surface_size[0], surface_size[1], QImage.Format.Format_RGB32)

            # Extract the relevant portion from the full QImage
            # Ensure source rect is valid before copying
            if src_rect.width > 0 and src_rect.height > 0 and \
               src_rect.x >= 0 and src_rect.y >= 0 and \
               src_rect.right <= full_qimage.width() and \
               src_rect.bottom <= full_qimage.height():
                 q_src_rect = QRect(src_rect.x, src_rect.y, src_rect.width, src_rect.height)
                 qimage = full_qimage.copy(q_src_rect)
            else:
                 print(f"Warning: Invalid src_rect for full_qimage.copy: {src_rect}, Full QImage size: {full_qimage.size()}")
                 qimage = QImage(1, 1, QImage.Format.Format_RGB32)
                 qimage.fill(Qt.GlobalColor.black)


        # --- Draw the QImage onto the widget ---
        # Draw the potentially converted/copied QImage (representing src_rect)
        # into the calculated dest_rect on the widget. This performs the scaling.
        if qimage and not qimage.isNull() and dest_rect.isValid():
             # Use SmoothTransformation for better scaling quality
             painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
             painter.drawImage(dest_rect, qimage)
        else:
             print(f"Warning: Skipping drawImage due to invalid QImage or dest_rect. QImage null: {qimage is None or qimage.isNull()}, DestRect valid: {dest_rect.isValid()}")


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