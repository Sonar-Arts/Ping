"""
Artemis Editor - Level View Module (Pygame Embedding)

This module contains the main widget for visually displaying and interacting
with the Ping level being edited, using an embedded Pygame surface.
"""
import pygame
import os
import math # Added for spinner drawing calculations
import random # For unique IDs initially
import traceback # For error handling
# Ensure pygame is imported for SysFont

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication, QSizePolicy # Removed QScrollArea
# Import pyqtSignal
# Ensure QRect is imported
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QImage, QColor # Added for direct painting

# Import tool constants
from .artemis_tool_palette import TOOL_ERASER, TOOL_SELECT # Import from the new tool palette module

# Import background drawing functions from the main game module
try:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from Ping.Modules.ping_graphics import get_background_draw_function, generate_sludge_texture
except ImportError as e:
    print(f"Warning: Could not import from Ping.Modules.ping_graphics: {e}")
    get_background_draw_function = None
    generate_sludge_texture = None


print("Artemis Modules/artemis_level_view.py loaded (Pygame)")

# --- Mock Compiler for Background Rendering ---
# This class mimics the structure expected by the background drawing functions
class MockCompiler:
    def __init__(self, view_widget, log_init_details=False, log_dimension_details=False):
        self.view = view_widget
        self.core = view_widget.core_logic
        props = self.core.get_level_properties()
        
        if log_init_details:
            print(f"[MockCompiler] Initializing with background_id: '{props.get('level_background')}'")

        self.width = self.view.level_width
        self.height = self.view.level_height
        self.scale = 1.0 # Editor scale is fixed at 1.0 for simplicity
        self.offset_x = 0 # No camera offset in editor view like in game
        self.offset_y = 0
        if log_dimension_details:
            print(f"[MockCompiler] Dimensions set to: width={self.width}, height={self.height}, scale={self.scale}")
        self.scoreboard_height = 0 # Scoreboard is handled separately now
        
        # Get background ID from level properties
        self.background_id = props.get("level_background")
        
        # Initialize colors using the 'colors' dictionary from core_logic's properties
        self.colors = props.get("colors", {})
        if log_init_details:
            if self.background_id and not self.colors:
                print(f"[MockCompiler] Warning: No pre-loaded colors for '{self.background_id}'. Draw func may use defaults/fail.")
            # elif not self.background_id: # This case is normal, no need to log unless debugging
                # print(f"[MockCompiler] No background_id specified or no pre-loaded colors found for MockCompiler.")

        self.dt = 1/60.0 # Fixed delta time for editor animation updates

        # Provide object lists (some backgrounds might use specific lists)
        self.level_objects = self.core.level_objects # All objects
        self.manholes = [obj for obj in self.level_objects if obj.get('type') == 'manhole']
        # Add other specific lists if required by other backgrounds

        # Animation state for the draw function - managed by the view widget
        # MockCompiler gets a direct reference to this.
        if not hasattr(self.view, 'current_draw_func_anim_state'): # Should be initialized in LevelViewWidget
            self.view.current_draw_func_anim_state = {}
        self.background_animation_state = self.view.current_draw_func_anim_state

        # Sludge texture - managed by the view widget (initially None)
        self.sludge_texture = getattr(self.view, 'cached_sludge_texture', None)

        # Background details - required by some backgrounds like sewer
        self.background_details = props.get("background_details", {})
        if log_init_details and self.background_id == "sewer" and not self.background_details:
            print(f"[MockCompiler] Warning: No background_details for sewer; using defaults.")

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
        self.grid_size = 50 # Size of grid cells in logical units (matching casino background detail)
        self.grid_enabled = False # Start with grid off
        self.grid_color = (60, 60, 60) # Dark grey for grid lines
        # Removed show_mock_scoreboard flag

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
        self.sprite_paths = {} # Track which objects use which sprite paths
        self.sprite_load_errors = set() # Track which sprites failed to load
        self.current_draw_func_anim_state = {} # State for the current background's draw function
        self.last_logged_background_id = None  # Tracks the ID of the background for which logs were last made
        self.cached_sludge_texture = None # For potentially caching generated textures
        self._initial_background_draw_info_logged = False # True if initial logs for current last_logged_background_id are done
        self._log_compiler_dimensions_on_refresh = True # Log dimensions on first frame and after resize

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
            self._log_compiler_dimensions_on_refresh = True # Log compiler dimensions on next update_pygame

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
        # Get background ID from core logic properties
        level_props = self.core_logic.get_level_properties()
        # Use the correct key "level_background" as indicated by debug output
        background_id = level_props.get("level_background")

        draw_func = None
        if background_id and get_background_draw_function:
            draw_func = get_background_draw_function(background_id)
        
        # Detect background change for logging and animation state reset
        if background_id != self.last_logged_background_id:
            print(f"Background transition: '{self.last_logged_background_id}' -> '{background_id}'. Resetting one-time logs and draw func anim state.")
            self.last_logged_background_id = background_id
            self.current_draw_func_anim_state = {} # Fresh state for the new background's draw_func
            self._initial_background_draw_info_logged = False # Allow initial logs for this new background
            self.cached_sludge_texture = None # Reset cached texture if it's background-specific
            # _log_compiler_dimensions_on_refresh is typically set by __init__ or refresh_display on dimension change
        
        self.pygame_surface.fill((0, 0, 0)) # Start with a clean black canvas
        
        # Determine if MockCompiler should log details for this frame
        log_compiler_init_details = not self._initial_background_draw_info_logged
        log_compiler_dimension_details = self._log_compiler_dimensions_on_refresh
        
        # Create mock compiler for the current frame
        mock_compiler = MockCompiler(self,
                                     log_init_details=log_compiler_init_details,
                                     log_dimension_details=log_compiler_dimension_details)
        
        # If MockCompiler was asked to log its init details, then this initial logging phase is done for the current background.
        # This flag will be reset if the background_id changes.
        if log_compiler_init_details:
            self._initial_background_draw_info_logged = True

        if self._log_compiler_dimensions_on_refresh:
            self._log_compiler_dimensions_on_refresh = False # Reset dimension log flag after use

        # The "Background Update Attempt" header should also only appear if initial logs were requested.
        if log_compiler_init_details: # This implies it's the first frame for this background session
            if background_id:
                print(f"\n=== Background Update Attempt (Initial Log for '{background_id}') ===")
                if draw_func:
                    print(f"Found background draw function for '{background_id}'")
                else:
                    print(f"Warning: Draw function not found for '{background_id}'")
            else: # No background_id, and it's the initial log phase
                print("\n=== No Background Specified (Initial Log) ===")
        
        processed_background_attempt_this_frame = False # Keep track for potential success message
        if draw_func:
            try:
                if background_id == "sewer":
                    regen_needed = False
                    current_dims = (int(self.level_width), int(self.level_height))
                    if self.cached_sludge_texture is None or self.cached_sludge_texture.get_size() != current_dims:
                        regen_needed = True

                    if regen_needed and generate_sludge_texture:
                        sludge_colors_from_theme = mock_compiler.colors
                        sludge_colors = {
                            'SLUDGE_MID': sludge_colors_from_theme.get('SLUDGE_MID', (80, 85, 60)),
                            'SLUDGE_HIGHLIGHT': sludge_colors_from_theme.get('SLUDGE_HIGHLIGHT', (100, 105, 75))
                        }
                        tex_width = max(1, int(self.level_width))
                        tex_height = max(1, int(self.level_height))
                        self.cached_sludge_texture = generate_sludge_texture(
                            tex_width, tex_height, 1.0, sludge_colors
                        )
                        mock_compiler.sludge_texture = self.cached_sludge_texture
                    elif not generate_sludge_texture and regen_needed:
                         print("[LevelView.update_pygame] Warning: Cannot generate sludge: generate_sludge_texture is None.")
                elif self.cached_sludge_texture is not None and background_id != "sewer":
                     self.cached_sludge_texture = None
                     mock_compiler.sludge_texture = None

                draw_func(self.pygame_surface, mock_compiler)
                processed_background_attempt_this_frame = True # For success message
                
                if log_compiler_init_details and background_id: # Log success only on initial attempt
                    print(f"Background draw for '{background_id}' completed successfully.")
            except Exception as e:
                print(f"Error drawing background '{background_id}': {e}")
                traceback.print_exc()
                # processed_background_attempt_this_frame remains False or is not used for error log here
        elif background_id: # background_id exists, but no draw_func
            # The warning for this case is covered by the "Background Update Attempt" block above
            # if log_compiler_init_details was true.
            pass
            
        # The _initial_background_draw_info_logged flag is now set earlier if log_compiler_init_details was true.
        # No further setting of this flag is needed here.

        if self.cached_sludge_texture is not None and background_id != "sewer":
            self.cached_sludge_texture = None
            if hasattr(mock_compiler, 'sludge_texture'): # If mock_compiler was created
                 mock_compiler.sludge_texture = None


        # Draw Arena Boundary (Over the background)
        arena_rect = pygame.Rect(0, 0, self.level_width, self.level_height)
        pygame.draw.rect(self.pygame_surface, (100, 100, 100), arena_rect, 1)

        # Draw Grid
        if self.grid_enabled:
            self.draw_grid()

        # Draw Placed Objects from core_logic
        for obj_data in self.core_logic.level_objects:
            obj_type = obj_data.get('type', 'unknown')
            obj_id = obj_data.get('id')
            x = obj_data.get('x', 0)
            y = obj_data.get('y', 0)
            w = obj_data.get('width')
            h = obj_data.get('height')
            size = obj_data.get('size')

            if w is not None and h is not None:
                obj_rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
            elif size is not None:
                 obj_rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
            else:
                 obj_rect = pygame.Rect(x - 5, y - 5, 10, 10)

            is_paddle = "paddle_spawn" in obj_type
            is_generic_sprite = obj_type == 'sprite'
            sprite_to_draw = None
            draw_placeholder = False
            placeholder_color = (100, 100, 100)
            final_blit_surface = None
            image_path = obj_data.get('image_path')

            if image_path:
                self.sprite_paths[obj_id] = image_path
                if image_path in self.sprite_load_errors:
                    draw_placeholder = True
                    placeholder_color = (255, 0, 0)
                    # continue # Don't continue, draw placeholder instead

                if image_path not in self.sprite_cache:
                    try:
                        full_path = os.path.join("..", "Ping", "Ping Assets", "Images", "Sprites", image_path)
                        full_path = os.path.normpath(full_path)
                        if not os.path.isfile(full_path):
                            raise FileNotFoundError(f"Sprite file not found: {full_path}")
                        ext = os.path.splitext(image_path)[1].lower()
                        if ext not in {'.png', '.webp', '.jpg', '.jpeg'}:
                            raise ValueError(f"Unsupported image format: {ext}")
                        if pygame.get_init():
                            try:
                                sprite = pygame.image.load(full_path)
                                if sprite.get_size() != (obj_rect.width, obj_rect.height):
                                    sprite = pygame.transform.smoothscale(sprite, (obj_rect.width, obj_rect.height))
                                self.sprite_cache[image_path] = sprite
                            except Exception as e:
                                print(f"Error loading sprite '{image_path}': {e}")
                                self.sprite_load_errors.add(image_path)
                                self.sprite_cache[image_path] = None
                    except Exception as e:
                        print(f"Error loading sprite '{image_path}': {e}")
                        self.sprite_load_errors.add(image_path)
                        self.sprite_cache[image_path] = None
                
                sprite_to_draw = self.sprite_cache.get(image_path)
                if not sprite_to_draw and image_path in self.sprite_load_errors: # Check if it failed before
                    draw_placeholder = True
                    placeholder_color = (200, 0, 0)
                elif not sprite_to_draw: # Path exists but sprite is None (e.g. first load attempt failed)
                    draw_placeholder = True
                    placeholder_color = (200, 0, 0)


            if sprite_to_draw:
                self.pygame_surface.blit(sprite_to_draw, obj_rect.topleft)
            elif final_blit_surface: # This variable is never set, consider removing
                self.pygame_surface.blit(final_blit_surface, obj_rect.topleft)
            elif draw_placeholder:
                pygame.draw.rect(self.pygame_surface, placeholder_color, obj_rect)
                try:
                    if pygame.font.get_init():
                        font_size = max(10, min(obj_rect.width, obj_rect.height) // 2)
                        if font_size > 0:
                            font = pygame.font.SysFont(None, font_size)
                            text = font.render('X', True, (255, 255, 255))
                            text_rect = text.get_rect(center=obj_rect.center)
                            self.pygame_surface.blit(text, text_rect)
                except Exception as e:
                    print(f"Warning: Could not draw placeholder text: {e}")
            elif obj_type == 'bumper':
                outer_color = (255, 0, 0)
                inner_color = (255, 255, 0)
                radius = obj_rect.width // 2
                center = obj_rect.center
                pygame.draw.circle(self.pygame_surface, outer_color, center, radius)
                pygame.draw.circle(self.pygame_surface, inner_color, center, int(radius * 0.6))
            elif obj_type == 'roulette_spinner':
                 center = obj_rect.center
                 radius = obj_rect.width // 2
                 num_segments = obj_data.get('properties', {}).get('num_segments', 38)
                 base_color = (200, 200, 200)
                 alt_color = (255, 0, 0)
                 border_color = (50, 50, 50)
                 pygame.draw.circle(self.pygame_surface, base_color, center, radius)
                 if num_segments > 0:
                     angle_step = 360 / num_segments
                     for i in range(num_segments):
                         start_angle = math.radians(i * angle_step - 90)
                         end_angle = math.radians((i + 1) * angle_step - 90)
                         segment_color = alt_color if i % 2 == 0 else base_color
                         points = [center]
                         num_arc_points = 5
                         for j in range(num_arc_points + 1):
                              angle = start_angle + (end_angle - start_angle) * (j / num_arc_points)
                              x_arc = center[0] + radius * math.cos(angle)
                              y_arc = center[1] + radius * math.sin(angle)
                              points.append((int(x_arc), int(y_arc)))
                         if len(points) >= 3:
                              try:
                                   pygame.draw.polygon(self.pygame_surface, segment_color, points)
                              except ValueError as e:
                                   print(f"Warning: Could not draw roulette segment polygon: {e}, points: {points}")
                 pygame.draw.circle(self.pygame_surface, border_color, center, radius, 2)
            elif not is_paddle and not is_generic_sprite: # Ensure this condition is met for non-sprite, non-paddle
                color = self.get_object_color(obj_data)
                pygame.draw.rect(self.pygame_surface, color, obj_rect)

            if obj_id == self.selected_object_id:
                pygame.draw.rect(self.pygame_surface, (255, 255, 0), obj_rect, 2)

        self.update() # Schedule a repaint of the QWidget


    def get_object_color(self, obj_data):
        """Returns a distinct color based on the object's data."""
        obj_type = obj_data.get('type', 'unknown')
        colors = {
            "ball_spawn": (255, 255, 255),
            "obstacle": (165, 42, 42),
            "roulette_spinner": (200, 200, 200), # Fallback if detailed drawing fails
            "bumper": (255, 0, 0), # Fallback if detailed drawing fails
            "goal": (0, 0, 200),
            "portal": (255, 0, 255),
            "powerup": (0, 255, 255),
            "manhole": (128, 128, 128),
            "unknown": (255, 165, 0)
        }
        base_type = obj_type.split('_')[0] # e.g. "goal" from "goal_left"
        return colors.get(obj_type, colors.get(base_type, colors["unknown"]))


    def _place_object_at(self, obj_type_key, x, y):
        """Creates object data with defaults and adds it via core_logic."""
        defaults = self.main_window.object_palette.get_selected_object_defaults()
        if not defaults:
            print(f"Error: Could not get defaults for {obj_type_key}")
            return

        width = defaults.get('width')
        height = defaults.get('height')
        size = defaults.get('size')
        radius = defaults.get('radius')

        obj_w, obj_h = 0, 0

        if width is not None and height is not None:
            obj_w, obj_h = width, height
        elif size is not None:
            obj_w, obj_h = size, size
        elif radius is not None:
            obj_w = obj_h = radius * 2
        elif obj_type_key == "sprite":
            obj_w, obj_h = defaults.get('width', 32), defaults.get('height', 32) # Use defaults from palette if available
            print(f"Placing sprite '{obj_type_key}'. Using size {obj_w}x{obj_h}.")
        else:
            print(f"Warning: No width/height, size, or radius found for {obj_type_key}. Using 10x10.")
            obj_w, obj_h = 10, 10

        save_x, save_y = x, y # Click position is intended center

        if self.grid_enabled:
            save_x, save_y = self.snap_to_grid(save_x, save_y)

        min_center_x = obj_w / 2
        max_center_x = self.level_width - (obj_w / 2)
        min_center_y = obj_h / 2
        max_center_y = self.level_height - (obj_h / 2)
        save_x = max(min_center_x, min(save_x, max_center_x))
        save_y = max(min_center_y, min(save_y, max_center_y))

        new_obj_data = defaults.copy()
        new_obj_data['x'] = int(save_x)
        new_obj_data['y'] = int(save_y)
        
        # Ensure dimensions are consistently stored
        if 'radius' in new_obj_data: # For circular objects, ensure width/height match diameter
            new_obj_data['width'] = new_obj_data['radius'] * 2
            new_obj_data['height'] = new_obj_data['radius'] * 2
        elif 'size' in new_obj_data: # For square objects based on size
            new_obj_data['width'] = new_obj_data['size']
            new_obj_data['height'] = new_obj_data['size']
        else: # For rectangular objects or sprites
            new_obj_data['width'] = obj_w
            new_obj_data['height'] = obj_h
        
        if obj_type_key == "sprite" and 'image_path' not in new_obj_data:
             new_obj_data['image_path'] = defaults.get('image_path', '') # Ensure image_path is set

        self.core_logic.add_object(new_obj_data)
        self.levelModified.emit(True)


    def select_object(self, obj_id):
        """Selects the object with the given ID."""
        if self.selected_object_id != obj_id:
            self.selected_object_id = obj_id
            self.is_dragging = False
            print(f"Selected object ID: {self.selected_object_id}")
            obj_data = self.core_logic.get_object_by_id(obj_id) # Get data for signal
            self.objectSelected.emit(obj_data) # Emit actual object data or ID
            self.update()

    def deselect_object(self):
        """Deselects the currently selected object."""
        if self.selected_object_id is not None:
            print(f"Deselecting object ID: {self.selected_object_id}")
            self.selected_object_id = None
            self.is_dragging = False
            self.objectSelected.emit(None)
            self.update()

    def _handle_object_update(self, obj_id):
        """Handles the core signal indicating an object's properties have changed."""
        print(f"LevelView received objectUpdated signal for ID: {obj_id}.")
        obj_data = self.core_logic.get_object_by_id(obj_id)
        if not obj_data:
            if obj_id in self.sprite_paths:
                old_path = self.sprite_paths.pop(obj_id)
                if old_path and not any(path == old_path for path in self.sprite_paths.values()):
                    if old_path in self.sprite_cache:
                        del self.sprite_cache[old_path]
                        print(f"Removed unused sprite '{old_path}' from cache")
                    if old_path in self.sprite_load_errors: # Clear error if sprite is no longer used
                        self.sprite_load_errors.remove(old_path)
            self.update() # Repaint if object was deleted (e.g. selection highlight)
            return

        if obj_data.get('type') == 'sprite' or 'image_path' in obj_data: # Handle any object that might have a sprite
            new_path = obj_data.get('image_path')
            old_path = self.sprite_paths.get(obj_id)
            
            if old_path != new_path:
                if old_path: # If there was an old path
                    # Check if this old_path is still used by other objects
                    is_old_path_still_used = any(pid != obj_id and p == old_path for pid, p in self.sprite_paths.items())
                    if not is_old_path_still_used:
                        if old_path in self.sprite_cache:
                            del self.sprite_cache[old_path]
                            print(f"Removed unused sprite '{old_path}' from cache")
                        if old_path in self.sprite_load_errors:
                            self.sprite_load_errors.remove(old_path)
                            print(f"Cleared error state for unused sprite '{old_path}'")
                
                if new_path:
                    self.sprite_paths[obj_id] = new_path
                    # Sprite will be loaded on next draw if not cached
                elif obj_id in self.sprite_paths: # New path is None/empty, remove old association
                    del self.sprite_paths[obj_id]


        self.update()

    # --- Mouse Events ---
    def mousePressEvent(self, event):
        if not self.pygame_surface: return

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
        pygame_x, pygame_y = self.map_widget_to_pygame(widget_pos)

        if 0 <= pygame_x < self.level_width and 0 <= pygame_y < self.level_height:
            clicked_obj_id = None
            # Iterate in reverse to get topmost object
            for obj_data in reversed(self.core_logic.level_objects):
                 x = obj_data.get('x')
                 y = obj_data.get('y')
                 w = obj_data.get('width')
                 h = obj_data.get('height')
                 size = obj_data.get('size')
                 rect = None
                 if x is not None and y is not None:
                     if w is not None and h is not None:
                         rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
                     elif size is not None:
                         rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
                     else: # Fallback for objects with x,y but no w,h,size (should be rare)
                          rect = pygame.Rect(x - 5, y - 5, 10, 10)
                 
                 if rect and rect.collidepoint(pygame_x, pygame_y):
                     clicked_obj_id = obj_data.get('id')
                     break

            if selected_tool == TOOL_ERASER:
                if clicked_obj_id:
                    obj_data = self.core_logic.get_object_by_id(clicked_obj_id)
                    # Prevent erasing default paddles (IDs 1 and 2)
                    if obj_data and obj_data.get("id") in [1, 2] and "paddle_spawn" in obj_data.get("type", ""):
                         print(f"Cannot erase default paddle object: {clicked_obj_id}")
                    else:
                        print(f"Erasing object ID: {clicked_obj_id}")
                        if self.selected_object_id == clicked_obj_id:
                            self.deselect_object()
                        self.core_logic.delete_object(clicked_obj_id)
                        self.levelModified.emit(True)
                else:
                    print("Eraser clicked on empty space.")

            elif selected_tool == TOOL_SELECT:
                if clicked_obj_id:
                    self.select_object(clicked_obj_id)
                    self.is_dragging = True
                    selected_obj_data = self.core_logic.get_object_by_id(self.selected_object_id)
                    obj_x_center = selected_obj_data.get('x', 0)
                    obj_y_center = selected_obj_data.get('y', 0)
                    self.drag_offset = (pygame_x - obj_x_center, pygame_y - obj_y_center)
                else:
                    self.deselect_object()

            elif selected_tool: # Placement tool from object palette
                 self.deselect_object()
                 self._place_object_at(selected_tool, pygame_x, pygame_y)

            else: # No tool selected - treat as select
                 if clicked_obj_id:
                    self.select_object(clicked_obj_id)
                    self.is_dragging = True
                    selected_obj_data = self.core_logic.get_object_by_id(self.selected_object_id)
                    obj_x_center = selected_obj_data.get('x', 0)
                    obj_y_center = selected_obj_data.get('y', 0)
                    self.drag_offset = (pygame_x - obj_x_center, pygame_y - obj_y_center)
                 else:
                    self.deselect_object()
        else: # Click outside logical pygame surface
            self.deselect_object() # Deselect if clicking outside the active area

        event.accept()


    def mouseMoveEvent(self, event):
        if not self.pygame_surface: return

        if self.is_panning and self.pan_start_pos:
            delta = event.pos() - self.pan_start_pos
            safe_zoom = max(self.zoom_level, 0.0001)
            self.pan_offset_x -= delta.x() / safe_zoom
            self.pan_offset_y -= delta.y() / safe_zoom

            widget_size = self.size()
            visible_pygame_width = widget_size.width() / safe_zoom
            visible_pygame_height = widget_size.height() / safe_zoom
            max_pan_x = max(0, self.level_width - visible_pygame_width)
            max_pan_y = max(0, self.level_height - visible_pygame_height)
            self.pan_offset_x = max(0, min(self.pan_offset_x, max_pan_x))
            self.pan_offset_y = max(0, min(self.pan_offset_y, max_pan_y))

            self.pan_start_pos = event.pos()
            self.update()
            event.accept()
            return

        if not self.is_dragging or self.selected_object_id is None:
            return

        selected_obj_data = self.core_logic.get_object_by_id(self.selected_object_id)
        if not selected_obj_data: return

        # Prevent dragging default paddles (IDs 1 and 2)
        if selected_obj_data.get("id") in [1, 2] and "paddle_spawn" in selected_obj_data.get("type", ""):
            return

        widget_pos = event.pos()
        pygame_x, pygame_y = self.map_widget_to_pygame(widget_pos)

        obj_w = selected_obj_data.get('width', 10) # Default to 10 if not found
        obj_h = selected_obj_data.get('height', 10)

        # new_x, new_y are the new *center* coordinates
        new_center_x = pygame_x - self.drag_offset[0]
        new_center_y = pygame_y - self.drag_offset[1]

        min_center_x = obj_w / 2
        max_center_x = self.level_width - (obj_w / 2)
        min_center_y = obj_h / 2
        max_center_y = self.level_height - (obj_h / 2)

        clamped_center_x = max(min_center_x, min(new_center_x, max_center_x))
        clamped_center_y = max(min_center_y, min(new_center_y, max_center_y))

        snapped_x, snapped_y = clamped_center_x, clamped_center_y
        if self.grid_enabled:
            snapped_x, snapped_y = self.snap_to_grid(clamped_center_x, clamped_center_y)
            # Re-clamp after snapping
            snapped_x = max(min_center_x, min(snapped_x, max_center_x))
            snapped_y = max(min_center_y, min(snapped_y, max_center_y))

        current_x = selected_obj_data.get('x')
        current_y = selected_obj_data.get('y')
        if current_x != int(snapped_x) or current_y != int(snapped_y):
            self.core_logic.update_object_properties(self.selected_object_id, {'x': int(snapped_x), 'y': int(snapped_y)})
            self.levelModified.emit(True)
            # Property editor is connected to core_logic.objectUpdated via main window,
            # or can be updated directly if main_window.property_editor.update_display(selected_obj_data) is called.
            # For now, rely on objectUpdated signal.
        event.accept()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton and self.is_panning:
            self.is_panning = False
            self.pan_start_pos = None
            self.unsetCursor()
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            print(f"Finished dragging object ID: {self.selected_object_id}")
            self.is_dragging = False
            # Final position already set during mouseMoveEvent
            event.accept()
            return


    def wheelEvent(self, event):
        if not self.pygame_surface: return

        delta = event.angleDelta().y()
        zoom_factor = 1.10 if delta > 0 else 1 / 1.10
        new_zoom = self.zoom_level * zoom_factor
        new_zoom = max(self.min_zoom, min(new_zoom, self.max_zoom))

        if new_zoom == self.zoom_level: return

        widget_mouse_pos = event.position()
        pygame_mouse_x_before, pygame_mouse_y_before = self.map_widget_to_pygame(widget_mouse_pos)

        self.zoom_level = new_zoom
        self._update_effective_surface_size()

        widget_size = self.size()
        temp_render_offset_x = max(0, (widget_size.width() - self.effective_surface_width) // 2)
        temp_render_offset_y = max(0, (widget_size.height() - self.effective_surface_height) // 2)

        relative_x_after = widget_mouse_pos.x() - temp_render_offset_x
        relative_y_after = widget_mouse_pos.y() - temp_render_offset_y
        safe_zoom = max(self.zoom_level, 0.0001)
        pygame_mouse_x_target = relative_x_after / safe_zoom
        pygame_mouse_y_target = relative_y_after / safe_zoom

        self.pan_offset_x = pygame_mouse_x_before - pygame_mouse_x_target
        self.pan_offset_y = pygame_mouse_y_before - pygame_mouse_y_target

        visible_pygame_width = widget_size.width() / safe_zoom
        visible_pygame_height = widget_size.height() / safe_zoom
        max_pan_x = max(0, self.level_width - visible_pygame_width)
        max_pan_y = max(0, self.level_height - visible_pygame_height)
        self.pan_offset_x = max(0, min(self.pan_offset_x, max_pan_x))
        self.pan_offset_y = max(0, min(self.pan_offset_y, max_pan_y))

        self.update()
        event.accept()

    # --- Grid Methods ---
    def toggle_grid(self, enabled):
        """Turns the grid display and snapping on or off."""
        self.grid_enabled = enabled
        print(f"Grid snapping {'enabled' if enabled else 'disabled'}")
        self.update() # Redraw to show/hide grid

    def snap_to_grid(self, x, y):
        """Snaps the given coordinates to the nearest grid intersection."""
        snapped_x = round(x / self.grid_size) * self.grid_size
        snapped_y = round(y / self.grid_size) * self.grid_size
        return snapped_x, snapped_y

    def draw_grid(self):
        """Draws the grid lines on the Pygame surface."""
        if not self.pygame_surface: return
        grid_start_y = 0 # Grid covers full height

        for x_coord in range(0, self.level_width, self.grid_size):
            pygame.draw.line(self.pygame_surface, self.grid_color, (x_coord, grid_start_y), (x_coord, self.level_height))

        for y_coord in range(grid_start_y, self.level_height, self.grid_size):
            pygame.draw.line(self.pygame_surface, self.grid_color, (0, y_coord), (self.level_width, y_coord))


    # --- Size Hint ---
    def sizeHint(self):
        """Provide a size hint based on the current level dimensions."""
        return QSize(self.level_width, self.level_height)

    # --- Paint Event ---
    def paintEvent(self, event):
        """Draws the relevant portion of the Pygame surface onto the widget, scaled and panned."""
        if not self.pygame_surface:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        widget_size = self.size()
        surface_size = self.pygame_surface.get_size()

        safe_zoom = max(self.zoom_level, 0.0001)
        visible_pygame_width = widget_size.width() / safe_zoom
        visible_pygame_height = widget_size.height() / safe_zoom

        max_pan_x = max(0, self.level_width - visible_pygame_width)
        max_pan_y = max(0, self.level_height - visible_pygame_height)
        clamped_pan_x = max(0, min(self.pan_offset_x, max_pan_x))
        clamped_pan_y = max(0, min(self.pan_offset_y, max_pan_y))

        src_width = max(1, min(visible_pygame_width, self.level_width - clamped_pan_x))
        src_height = max(1, min(visible_pygame_height, self.level_height - clamped_pan_y))

        src_rect_pygame = pygame.Rect(
            int(clamped_pan_x), int(clamped_pan_y),
            int(src_width), int(src_height)
        )

        dest_draw_width = int(src_rect_pygame.width * self.zoom_level)
        dest_draw_height = int(src_rect_pygame.height * self.zoom_level)

        self.render_offset_x = max(0, (widget_size.width() - dest_draw_width) // 2)
        self.render_offset_y = max(0, (widget_size.height() - dest_draw_height) // 2)

        dest_rect_qt = QRect(
            self.render_offset_x, self.render_offset_y,
            dest_draw_width, dest_draw_height
        )

        painter.fillRect(self.rect(), QColor("#101010")) # Background for widget area

        qimage = None
        try:
            if src_rect_pygame.width > 0 and src_rect_pygame.height > 0 and \
               src_rect_pygame.x >= 0 and src_rect_pygame.y >= 0 and \
               src_rect_pygame.right <= self.pygame_surface.get_width() and \
               src_rect_pygame.bottom <= self.pygame_surface.get_height():

                sub_surface = self.pygame_surface.subsurface(src_rect_pygame)
                bytes_per_line = sub_surface.get_pitch()
                qimage_format = QImage.Format.Format_RGB32
                if sub_surface.get_flags() & pygame.SRCALPHA:
                    qimage_format = QImage.Format.Format_ARGB32_Premultiplied
                
                buffer = sub_surface.get_buffer()
                qimage = QImage(buffer.raw, src_rect_pygame.width, src_rect_pygame.height, bytes_per_line, qimage_format)
            else:
                 print(f"Warning: Invalid src_rect_pygame for subsurface: {src_rect_pygame}, Surface size: {self.pygame_surface.get_size()}")
                 qimage = QImage(1, 1, QImage.Format.Format_RGB32)
                 qimage.fill(Qt.GlobalColor.black)
        except (ValueError, IndexError, pygame.error) as e: # Added pygame.error
            print(f"Warning: Pygame subsurface/get_buffer() failed ({e}). Check rect: {src_rect_pygame}")
            # Fallback: convert entire surface (less efficient)
            try:
                image_string = pygame.image.tostring(self.pygame_surface, "RGBA" if self.pygame_surface.get_flags() & pygame.SRCALPHA else "RGBX")
                full_qimage = QImage(image_string, surface_size[0], surface_size[1], 
                                     QImage.Format.Format_RGBA8888_Premultiplied if self.pygame_surface.get_flags() & pygame.SRCALPHA else QImage.Format.Format_RGBX8888)
                
                # Ensure src_rect_pygame is valid for full_qimage.copy
                q_src_rect_for_copy = QRect(src_rect_pygame.x, src_rect_pygame.y, src_rect_pygame.width, src_rect_pygame.height)
                if q_src_rect_for_copy.isValid() and \
                   q_src_rect_for_copy.right() <= full_qimage.width() and \
                   q_src_rect_for_copy.bottom() <= full_qimage.height():
                    qimage = full_qimage.copy(q_src_rect_for_copy)
                else:
                    print(f"Warning: Invalid QRect for full_qimage.copy: {q_src_rect_for_copy}, Full QImage size: {full_qimage.size()}")
                    qimage = QImage(1, 1, QImage.Format.Format_RGB32) # Tiny black image
                    qimage.fill(Qt.GlobalColor.black)

            except Exception as e_fallback:
                print(f"FATAL: Fallback image conversion failed: {e_fallback}")
                qimage = QImage(1, 1, QImage.Format.Format_RGB32) # Final fallback
                qimage.fill(Qt.GlobalColor.red) # Red to indicate critical failure


        if qimage and not qimage.isNull() and dest_rect_qt.isValid():
             painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
             painter.drawImage(dest_rect_qt, qimage)
        else:
             print(f"Warning: Skipping drawImage. QImage null: {qimage is None or qimage.isNull()}, DestRect valid: {dest_rect_qt.isValid()}")

        painter.end()


    # --- Tool Handling ---
    def set_active_tool(self, tool_id):
        """Informs the view about the currently active tool."""
        print(f"LevelView notified of active tool: {tool_id}")
        if tool_id != TOOL_SELECT and self.selected_object_id is not None:
             if tool_id and tool_id not in [TOOL_ERASER]: # Placement tools
                 self.deselect_object()


    # --- Cleanup ---
    def closeEvent(self, event):
        """Stop the timer when the widget closes."""
        print("LevelViewWidget closing, stopping timer.")
        self.timer.stop()
        super().closeEvent(event)