# Modules/Ping_MCompile.py
# Initially, this will be a copy of Ping_Arena.py
# We will modify it to handle .pmf files

import pygame
import pygame.gfxdraw # For smooth lighting
import random  # Import random for background generation
import math  # Import math for river animation
import json # Import JSON for PMF parsing (assuming JSON format)
import threading
import time
from .Ping_GameObjects import ObstacleObject, GoalObject, PortalObject, PowerUpBallObject, BallObject, ManHoleObject, BumperObject, SpriteObject, CandleObject, GhostObstacleObject, Pickles # Import SpriteObject, CandleObject, GhostObstacleObject, and Pickles
from .Submodules.Ping_Obstacles import RouletteSpinner, PistonObstacle, TeslaCoilObstacle, GhostObstacle # Import the new obstacles
# Removed import for DebugLevel, SewerLevel
from .Submodules.Ping_Scoreboard import Scoreboard
# Import the generation function specifically
from .ping_graphics import get_background_draw_function, generate_sludge_texture, load_sprite_image

class LevelCompiler: # Renamed from Arena
    """Handles loading and compiling level data from .pmf files or level instances."""
    def __init__(self, level_source):
        """
        Initialize the level compiler.

        Args:
            level_source: Either a path to a .pmf file (str) or a level instance object.
        """
        params = None
        self.level_instance = None # Keep track if we loaded from an instance
        self.obstacle_params = {} # Store obstacle params for reset
        pmf_data = None # To store raw PMF data if loaded

        if isinstance(level_source, str) and level_source.lower().endswith('.pmf'):
            # Load from .pmf file
            try:
                pmf_data = self._load_pmf(level_source) # Load raw PMF data first
                params = self._parse_pmf_to_params(pmf_data) # NOW parse into structured params
                # We don't have a level instance when loading from PMF
                self.level_instance = None
                self.level_source_path = level_source # Store the path
            except Exception as e:
                print(f"Error loading PMF file '{level_source}': {e}")
                # PMF loading failed, raise an error or handle appropriately
                # Removed fallback to DebugLevel
                print("Error: PMF loading failed. Cannot fall back to DebugLevel.")
                # Option 1: Raise an exception
                raise ValueError(f"Failed to load PMF file: {level_source}")
                # Option 2: Set params to None or an empty dict and handle later
                # params = {} # Or None
                pmf_data = None # Ensure pmf_data is None on fallback
                self.level_source_path = None # No path on fallback
        elif hasattr(level_source, 'get_parameters'):
            # Load from level instance (existing behavior)
            self.level_instance = level_source
            params = self.level_instance.get_parameters()
            self.level_source_path = None # No path when loading from instance
            pmf_data = None # Ensure pmf_data is None
        else:
            # Invalid level source, raise an error
            # Removed default to DebugLevel
            print(f"Error: Invalid level source: {level_source}. Cannot default to DebugLevel.")
            raise ValueError(f"Invalid level source provided: {level_source}")
            # Or set params to None/empty dict
            # params = {} # Or None
            pmf_data = None # Ensure pmf_data is None
            self.level_source_path = None # No path on default

        if not params:
             raise ValueError("Failed to load level parameters.")

        # --- Parameter Loading (Copied from Arena, uses 'params' dict) ---

        # Set dimensions (Now guaranteed to be a dict because PMF was parsed)
        dimensions = params.get('dimensions', {'width': 800, 'height': 600, 'scoreboard_height': 60})
        self.width = dimensions.get('width', 800)
        # Assume the 'height' from PMF/params is the PLAYABLE height.
        playable_height_from_pmf = dimensions.get('height', 600)
        self.scoreboard_height = dimensions.get('scoreboard_height', 60)
        # Set self.height directly to the value from the PMF/params.
        self.height = playable_height_from_pmf

        # --- Store Core Level Properties ---
        # These are now parsed from PMF or taken from level instance params
        self.bounce_walls = params.get('bounce_walls', True) # Default to True if missing
        self.use_goals = params.get('use_goals', True) # Default to True if missing
        self.can_spawn_obstacles = params.get('can_spawn_obstacles', False) # Default to False
        self.can_spawn_powerups = params.get('can_spawn_powerups', False) # Default to False
        self.can_spawn_ghosts = params.get('can_spawn_ghosts', False) # Default to False for ghosts
 
        # Set up shader handling
        self._shader_warning_shown = False
        self._shader = None
        self._settings = None
        self._shader_instance = None
        try:
            from .Submodules.Ping_Settings import SettingsScreen
            from .Submodules.Ping_Shader import get_shader
            self._settings = SettingsScreen
            self._shader_instance = get_shader()  # Create shader instance once
        except ImportError as e:
            # Use a placeholder logger if DBConsole is unavailable during init
            self._log_warning(f"Shader system unavailable: {e}")
            self._shader_warning_shown = True
        except Exception as e: # Catch other potential errors during shader init
             self._log_warning(f"Error initializing shader system: {e}")
             self._shader_warning_shown = True


        # Get colors from level configuration
        # Get colors from level configuration (use defaults if missing)
        self.colors = params.get('colors', {
            'WHITE': (255, 255, 255), 'BLACK': (0, 0, 0), 'DARK_BLUE': (0, 0, 139),
            # Add other defaults used by drawing functions if necessary
            'BRICK_LIGHT': (160, 160, 160), 'BRICK_DARK': (140, 140, 140),
            'BRICK_MORTAR': (100, 100, 100), 'MANHOLE_BRICK_LIGHT': (170, 170, 150),
            'MANHOLE_BRICK_DARK': (150, 150, 130), 'CRACK_COLOR': (50, 50, 50),
            'VEGETATION_COLOR': (0, 100, 0), 'RIVER_WATER_DARK': (0, 50, 80),
            'RIVER_WATER_LIGHT': (0, 70, 100), 'RIVER_HIGHLIGHT': (100, 150, 200),
            # Add Manhole Colors
            'MANHOLE_OUTER': (100, 100, 100), 'MANHOLE_INNER': (80, 80, 80),
            'MANHOLE_SHADOW': (40, 40, 40), 'MANHOLE_HIGHLIGHT': (120, 120, 120),
            'MANHOLE_WATER': (0, 60, 90), # For spouting effect
            'MANHOLE_DETAIL': (110, 110, 110), # Added detail color
            # Add Tesla Coil Colors
            'TESLA_COIL_BASE': (60, 50, 80),
            'TESLA_COIL_HIGHLIGHT': (90, 80, 110),
            'TESLA_SPARK_CORE': (255, 255, 255),
            'TESLA_SPARK_GLOW': (200, 200, 255, 150) # RGBA for glow
        })

        # Store background details if available (kept for potential fallback/compatibility)
        self.background_details = params.get('background_details', None)
        # Store new level properties
        self.level_music = params.get('level_music', None) # Get from parsed params
        self.level_background = params.get('level_background', 'default') # Get from parsed params, default to 'default'
        self.level_name = params.get('level_name', "Unknown Level") # Get level name, default if missing
        self.has_lighting = params.get('has_lighting', False) # Get lighting property
        self.lighting_level = params.get('lighting_level', 75) # Get lighting level, default 75
        self.river_animation_offset = 0  # Initialize river animation offset
        self.dt = 1.0 / 60.0  # Default delta time (60 FPS)

        # --- Store all relevant properties in self.level_properties for graphics functions ---
        # This dictionary should align with what Artemis_Modules/artemis_core.py expects
        # and what artemis_level_properties.py might query via core_logic.
        self.level_properties = {
            "name": self.level_name,
            "width": self.width,
            "height": self.height, # Playable height
            # background_color is tricky as PMF uses level_background identifier.
            # For now, use a placeholder or derive from self.colors if a suitable key exists.
            # Artemis core expects an RGB tuple.
            "background_color": self.colors.get('BACKGROUND_TUPLE_FOR_ARTEMIS', (10,10,10)), # Placeholder
            "bounce_walls": self.bounce_walls,
            "use_goals": self.use_goals,
            "can_spawn_obstacles": self.can_spawn_obstacles,
            "can_spawn_powerups": self.can_spawn_powerups,
            "can_spawn_ghosts": self.can_spawn_ghosts,
            "level_music": self.level_music,
            "level_background": self.level_background, # Identifier like "sewer", "casino"
            "has_lighting": self.has_lighting,
            "lighting_level": self.lighting_level
            # Add other properties from ArtemisCore._get_default_level_properties if needed
        }

        # Initialize scoreboard as None
        self.scoreboard = None

        # Calculate scaling factors
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Set center line properties
        # Use .get() with defaults for robustness against missing keys in PMF
        center_line_params = params.get('center_line', {})
        self.center_line_box_width = center_line_params.get('box_width', 0)
        self.center_line_box_height = center_line_params.get('box_height', 0)
        self.center_line_box_spacing = center_line_params.get('box_spacing', 0)


        # Store paddle positions
        self.paddle_positions = params.get('paddle_positions', {}) # Use .get()

        # Initialize object lists (will be populated by helper methods)
        self.obstacles = [] # Changed from self.obstacle = None
        self.goals = []
        self.portals = []
        self.manholes = []
        self.bumpers = []  # Added bumpers list
        self.power_up = None
        # Removed self.loaded_sprites
        self.sprites = [] # List to hold SpriteObject instances
        self.candles = [] # List to hold CandleObject instances
        self.ghost_obstacles = [] # List to hold GhostObstacleObject instances
        self.pickles_objects = [] # List to hold Pickles instances

        # --- Object Creation ---
        # Create objects based on the source (PMF data or params dict)
        if pmf_data:
            # Create objects directly from parsed PMF data
            # We still need obstacle_params for reset, get it from the parsed params
            self.obstacle_params = params.get('obstacle', {}) # Get obstacle *definition* params if any
            self._create_objects_from_pmf(pmf_data)
        else:
            # Create objects using the params dictionary (original logic for class levels)
            # obstacle_params is already set from params dict earlier in this case
            self._create_objects_from_params(params)

        # --- Generate Static Background Features (like cracks) ---
        self._generate_background_features()

        # --- Initialize Background Animation Threading (if needed) ---
        self.sludge_texture = None
        self.sludge_texture_lock = threading.Lock()
        self.sludge_thread = None
        self.stop_sludge_thread = threading.Event()
        self.needs_sludge_texture_update = False # Flag to signal regeneration

        # Removed old sprite loading block from __init__
        # Sprite objects are now created in _create_objects_from_pmf

        if self.level_background == 'sewer':
            self._log_warning("Sewer background detected, starting texture generation thread.")
            self.needs_sludge_texture_update = True # Initial generation needed
            self.sludge_thread = threading.Thread(target=self._sludge_texture_worker, daemon=True)
            self.sludge_thread.start()

    def stop_background_threads(self):
        """Signals any running background threads to stop and waits for them."""
        if self.sludge_thread and self.sludge_thread.is_alive():
            self._log_warning("Stopping sludge texture thread...")
            self.stop_sludge_thread.set()
            self.sludge_thread.join(timeout=2) # Wait max 2 seconds
            if self.sludge_thread.is_alive():
                self._log_warning("Sludge texture thread did not stop gracefully.")
            else:
                self._log_warning("Sludge texture thread stopped.")


    def _sludge_texture_worker(self):
        """Worker function for the background thread generating sludge texture."""
        self._log_warning("Sludge texture worker thread started.")
        while not self.stop_sludge_thread.is_set():
            update_needed = False
            with self.sludge_texture_lock: # Check flag under lock
                if self.needs_sludge_texture_update:
                    update_needed = True
                    self.needs_sludge_texture_update = False # Reset flag

            if update_needed:
                self._log_warning("Generating new sludge texture...")
                # Generate texture using current state (ensure these are thread-safe reads if they change)
                # It's generally safer to pass necessary values if they might change,
                # but for scale/dimensions updated in main thread via update_scaling,
                # reading them here should be okay as long as generation is fast enough
                # or update_scaling happens infrequently.
                # A more robust solution might involve passing params via a queue.
                width = self.width * self.scale # Use scaled width
                height = self.height * self.scale # Use scaled playable height (self.height)
                current_scale = self.scale
                current_colors = self.colors # Assuming colors don't change dynamically

                new_texture = generate_sludge_texture(width, height, current_scale, current_colors)

                if new_texture:
                    with self.sludge_texture_lock:
                        self.sludge_texture = new_texture
                        self._log_warning(f"Sludge texture updated (Size: {new_texture.get_size()}).")
                else:
                     self._log_warning("Failed to generate sludge texture (invalid dimensions?).")


            # Sleep to prevent busy-waiting and control regeneration check frequency
            # This doesn't directly control animation FPS, just how often it checks the flag.
            time.sleep(0.1) # Check for updates 10 times per second

        self._log_warning("Sludge texture worker thread finished.")


    def _generate_background_features(self):
        """Generates static visual features for backgrounds (e.g., cracks)"""
        if self.level_background == 'sewer':
            # Ensure background_details exists and has necessary info
            if not self.background_details:
                self._log_warning("Cannot generate sewer cracks: background_details missing.")
                # Use default details if missing entirely (matching draw function)
                self.background_details = {
                     'brick_width': 50, 'brick_height': 25, 'river_width_ratio': 0.25,
                     'manhole_brick_padding': 5, 'crack_frequency': 0.03, # Use updated freq
                     'vegetation_frequency': 0.02
                }
                self._log_warning("Using default sewer background details for crack generation.")

            # Ensure background_details is a dictionary before proceeding
            if not isinstance(self.background_details, dict):
                self._log_warning("Cannot generate sewer cracks: background_details is not a dictionary.")
                self.background_details = {'cracks': []} # Ensure 'cracks' key exists
                return

            details = self.background_details
            brick_w = details.get('brick_width', 50)
            brick_h = details.get('brick_height', 25)
            river_width_ratio = details.get('river_width_ratio', 0.25)
            river_width = self.width * river_width_ratio
            river_x_start = (self.width - river_width) / 2
            river_x_end = river_x_start + river_width
            manhole_padding = details.get('manhole_brick_padding', 5)
            crack_freq = details.get('crack_frequency', 0.03) # Use same freq as draw

            cracks_data = [] # List to store (start_x, start_y, end_x, end_y) in logical coords

            # Iterate through potential brick positions within the playable area (logical Y from 0 to self.height)
            for y_logic in range(0, self.height, brick_h): # Start Y loop from 0 (top of playable area)
                row_offset = (y_logic // brick_h) % 2 * (brick_w // 2)
                for x_logic in range(0, self.width, brick_w):
                    # Create rect with logical coordinates relative to playable area top-left (0,0)
                    brick_rect_logic = pygame.Rect(x_logic - row_offset, y_logic, brick_w, brick_h)

                    # Skip if brick is in river area
                    if brick_rect_logic.right > river_x_start and brick_rect_logic.left < river_x_end:
                        continue

                    # Skip if near a manhole
                    is_near_manhole = False
                    for manhole in self.manholes:
                        if hasattr(manhole, 'rect') and isinstance(manhole.rect, pygame.Rect):
                            manhole_rect_padded = manhole.rect.inflate(manhole_padding * 2, manhole_padding * 2)
                            if brick_rect_logic.colliderect(manhole_rect_padded):
                                is_near_manhole = True
                                break
                    if is_near_manhole:
                        continue

                    # Generate crack based on frequency
                    if random.random() < crack_freq:
                        # Generate crack coordinates within this brick's logical rect
                        # Start near an edge
                        edge = random.choice(['top', 'bottom', 'left', 'right'])
                        if edge == 'top':
                            start_x = brick_rect_logic.left + random.randint(2, brick_rect_logic.width - 3)
                            start_y = brick_rect_logic.top + random.randint(0, 2)
                        elif edge == 'bottom':
                            start_x = brick_rect_logic.left + random.randint(2, brick_rect_logic.width - 3)
                            start_y = brick_rect_logic.bottom - random.randint(0, 2)
                        elif edge == 'left':
                            start_x = brick_rect_logic.left + random.randint(0, 2)
                            start_y = brick_rect_logic.top + random.randint(2, brick_rect_logic.height - 3)
                        else: # right
                            start_x = brick_rect_logic.right - random.randint(0, 2)
                            start_y = brick_rect_logic.top + random.randint(2, brick_rect_logic.height - 3)

                        # Make crack longer and more jagged (relative to brick size)
                        crack_length_scale = random.uniform(0.5, 1.5)
                        end_x = start_x + random.randint(-int(brick_w * crack_length_scale), int(brick_w * crack_length_scale))
                        end_y = start_y + random.randint(-int(brick_h * crack_length_scale), int(brick_h * crack_length_scale))

                        # Clamp end point to stay roughly within brick bounds
                        end_x = max(brick_rect_logic.left, min(brick_rect_logic.right, end_x))
                        end_y = max(brick_rect_logic.top, min(brick_rect_logic.bottom, end_y))

                        # Generate zig-zag points instead of a single line
                        crack_points = self._generate_zigzag_points((start_x, start_y), (end_x, end_y), segments=random.randint(3, 6), magnitude=random.uniform(1, 4))
                        cracks_data.append(crack_points) # Store list of points

            # Store the generated cracks (list of lists of points) in background_details
            self.background_details['cracks'] = cracks_data
            self._log_warning(f"Generated {len(cracks_data)} cracks for sewer background.")


    def _generate_zigzag_points(self, start_pos, end_pos, segments=5, magnitude=3):
        """Generates a list of points for a zig-zag line between start and end."""
        points = [start_pos]
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx**2 + dy**2)
        if length == 0: # Avoid division by zero for zero-length cracks
            return [start_pos, end_pos]

        # Calculate perpendicular vector components (normalized)
        perp_dx = -dy / length
        perp_dy = dx / length

        for i in range(1, segments):
            progress = i / segments
            # Base point along the straight line
            base_x = start_x + dx * progress
            base_y = start_y + dy * progress
            # Random offset perpendicular to the line
            offset = random.uniform(-magnitude, magnitude)
            # Add offset to the base point
            point_x = base_x + perp_dx * offset
            point_y = base_y + perp_dy * offset
            points.append((int(point_x), int(point_y))) # Store as integer points

        points.append(end_pos) # Add the final end point
        return points

    def _parse_pmf_to_params(self, pmf_data):
        """Parses raw PMF data into the structured 'params' dictionary."""
        params = {}
        properties = pmf_data.get('properties', {}) # Get the main properties block
        # level_properties = pmf_data.get('level_properties', {}) # No longer needed for these properties

        # --- Parse Dimensions ---
        # Read width and height directly from properties, with defaults
        width = properties.get('width', 800)
        height = properties.get('height', 600)
        # Store total height in the parsed params for potential reference,
        # but the compiler instance uses self.height (playable) and self.scoreboard_height
        params['dimensions'] = {
            'width': width,
            'height': height, # Store total height here in the params dict
            'scoreboard_height': 60 # Default scoreboard height, maybe make this a PMF property?
        }
        # Note: LevelCompiler instance uses self.height = height - scoreboard_height

        # --- Parse Core Level Properties ---
        params['bounce_walls'] = properties.get('bounce_walls', True)
        params['use_goals'] = properties.get('use_goals', True)
        params['can_spawn_obstacles'] = properties.get('can_spawn_obstacles', False)
        params['can_spawn_powerups'] = properties.get('can_spawn_powerups', False)
        params['can_spawn_ghosts'] = properties.get('can_spawn_ghosts', False) # Parse new ghost flag
 
        # --- Add Defaults for missing PMF sections ---
        params['colors'] = pmf_data.get('colors', { # Allow PMF to define colors, else use default
            'WHITE': (255, 255, 255), 'BLACK': (0, 0, 0), 'DARK_BLUE': (0, 0, 139),
            'BRICK_LIGHT': (160, 160, 160), 'BRICK_DARK': (140, 140, 140),
            'BRICK_MORTAR': (100, 100, 100), 'MANHOLE_BRICK_LIGHT': (170, 170, 150),
            'MANHOLE_BRICK_DARK': (150, 150, 130), 'CRACK_COLOR': (50, 50, 50),
            'VEGETATION_COLOR': (0, 100, 0), 'RIVER_WATER_DARK': (0, 50, 80),
            'RIVER_WATER_LIGHT': (0, 70, 100), 'RIVER_HIGHLIGHT': (100, 150, 200),
            'MANHOLE_OUTER': (100, 100, 100), 'MANHOLE_INNER': (80, 80, 80),
            'MANHOLE_SHADOW': (40, 40, 40), 'MANHOLE_HIGHLIGHT': (120, 120, 120),
            'MANHOLE_WATER': (0, 60, 90),
            'MANHOLE_DETAIL': (110, 110, 110)
        })
        params['center_line'] = pmf_data.get('center_line', {'box_width': 10, 'box_height': 20, 'box_spacing': 15}) # Allow PMF override
        params['obstacle'] = pmf_data.get('obstacle_definition', {'active': False}) # Look for specific obstacle definition in PMF
        # Goals are handled by use_goals property now
        # Portals are handled by object creation
        # Powerups are handled by can_spawn_powerups and object creation
        params['background_details'] = pmf_data.get('background_details', {'type': 'default'}) # Allow PMF override (kept for potential fallback)

        # --- Parse New Level Properties (from main properties dict now) ---
        params['level_music'] = properties.get('level_music', None) # Get music file path from properties, default None
        params['level_background'] = properties.get('level_background', 'default') # Get background ID from properties, default 'default'
        # Prioritize "name" key, fall back to "level_name", then default
        params['level_name'] = properties.get('name', properties.get('level_name', "Unnamed PMF Level"))
        params['has_lighting'] = properties.get('has_lighting', False) # Default to False if not present
        params['lighting_level'] = properties.get('lighting_level', 75) # Default to 75 if not present

        # --- Parse Objects for specific params (like paddle spawns) ---
        params['paddle_positions'] = {}
        objects = pmf_data.get('objects', [])
        for obj in objects:
            obj_type = obj.get('type')
            # Use direct x, y from PMF object
            obj_x = obj.get('x')
            obj_y = obj.get('y')

            if obj_type == 'paddle_spawn' and obj_x is not None and obj_y is not None:
                # Calculate relative positions (center x, center y)
                # Use TOTAL height for relative Y calculation from PMF coordinates
                total_height = height # Use the height read from PMF (which includes scoreboard)
                obj_w = obj.get('width', 20) # Default paddle width if not specified
                obj_h = obj.get('height', 100) # Default paddle height if not specified
                rel_x = (obj_x + obj_w / 2) / width
                # Adjust Y coordinate from PMF (relative to top of window) to be relative to top of playable area
                # Subtract scoreboard height before calculating relative position within playable area
                playable_height = total_height - 60 # Assuming default scoreboard height for now
                if playable_height <= 0: playable_height = 1 # Avoid division by zero
                # Calculate relative Y based on the playable area height
                # Assume obj_y from PMF is relative to the playable area top (Y=0)
                rel_y = (obj_y + obj_h / 2) / playable_height
                # Clamp rel_y between 0 and 1? Or let it be outside? For now, let it be.

                # Get properties dict for this object
                properties = obj.get('properties', {})
                # Get 'is_left' from the properties dict (Standardized PMF)
                is_left = properties.get('is_left', False) # Default to False if missing

                if is_left:
                    params['paddle_positions']['left'] = {'x': rel_x, 'y': rel_y}
                else:
                    params['paddle_positions']['right'] = {'x': rel_x, 'y': rel_y}

            # Note: Manholes, obstacles etc. are created later in _create_objects_from_pmf

        # Add defaults if paddles weren't found
        if 'left' not in params['paddle_positions']:
             params['paddle_positions']['left'] = {'x': 0.05, 'y': 0.5}
        if 'right' not in params['paddle_positions']:
             params['paddle_positions']['right'] = {'x': 0.95, 'y': 0.5}

        return params

    def _create_objects_from_pmf(self, pmf_data):
        """Creates game objects based on the 'objects' and 'sprites' lists in PMF data."""
        # Reset GhostObstacle class variables at the start of level loading
        if hasattr(GhostObstacleObject, 'ghost') and hasattr(GhostObstacleObject.ghost, 'reset_class_vars'): # Check specific path first
             GhostObstacleObject.ghost.reset_class_vars()
        elif hasattr(GhostObstacle, 'reset_class_vars'): # Fallback to direct class if GhostObstacleObject not fully formed or path changed
            GhostObstacle.reset_class_vars()


        objects_list = pmf_data.get('objects', [])
        sprites_list = pmf_data.get('sprites', []) # Get the separate sprites list
        combined_list = objects_list + sprites_list # Combine them for iteration
        width = self.width # Get dimensions set earlier
        height = self.height

        # Initialize object lists
        self.manholes = []
        self.obstacles = [] # Changed from self.obstacle = None
        self.goals = []
        self.portals = []
        self.bumpers = []
        self.sprites = [] # Initialize list for SpriteObjects
        self.candles = [] # Initialize list for CandleObject instances
        self.ghost_obstacles = [] # Initialize list for GhostObstacleObjects
        self.pickles_objects = [] # Initialize list for Pickles instances
        self.power_up = None # Use singular for now, assuming max 1 powerup from PMF/default

        # Flags to track if specific types were created from the list
        # Removed obstacle_created_from_list flag
        powerup_created_from_list = False

        # --- Create Goals (Based on global flag) ---
        if self.use_goals:
            self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=True))
            self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=False))

        # --- Create Objects from COMBINED PMF List ---
        self._log_warning(f"DEBUG: Processing combined list of {len(combined_list)} objects/sprites from PMF.") # ++Log++
        for obj_index, obj in enumerate(combined_list): # Iterate the combined list
            obj_type = obj.get('type')
            # Get common geometry and properties (default to empty dict)
            obj_x = obj.get('x')
            obj_y = obj.get('y')
            obj_width = obj.get('width')
            obj_height = obj.get('height')
            properties = obj.get('properties', {}) # Ensure properties is always a dict

            # Skip if essential geometry is missing (allow tesla_coil without width)
            missing_geometry = False
            if obj_x is None or obj_y is None or obj_height is None:
                missing_geometry = True
            # Tesla coil doesn't strictly need width defined in PMF if radii are used
            if obj_type != 'tesla_coil' and obj_width is None:
                 missing_geometry = True

            if missing_geometry:
                self._log_warning(f"Skipping PMF object #{obj_index} due to missing geometry: {obj}")
                continue

            # --- Object Type Specific Creation ---

            # All checks below should have 12 spaces before if/elif/else
            if obj_type == 'paddle_spawn':
                # Paddle spawns are handled during parameter parsing (_parse_pmf_to_params)
                # to set self.paddle_positions. No object created here.
                pass # Already handled

            elif obj_type == 'manhole':
                # Determine if it's a top or bottom manhole based on absolute Y relative to PLAYABLE area
                # Use obj_y directly as it's relative to the playable area top (Y=0)
                obj_y_relative_to_playable = obj_y # Use Y directly (relative to playable area top)
                is_bottom = obj_y > (self.height / 2) # self.height is playable height
                # Pass the original obj_y coordinate to the ManHoleObject constructor
                manhole = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                        obj_x, obj_y, obj_width, obj_height, is_bottom, properties) # Pass properties
                self.manholes.append(manhole)
                self._log_warning(f"Created ManHoleObject at logical ({obj_x},{obj_y}) with properties: {properties}")

            elif obj_type == 'bumper':
                bumper = BumperObject(
                    arena_width=self.width, # Logical width
                    arena_height=self.height, # Logical playable height
                    scoreboard_height=self.scoreboard_height,
                    scale_rect=self.scale_rect,
                    x=obj_x, # Logical X
                    y=obj_y, # Use Y directly (relative to playable area top)
                    radius=properties.get('radius', 30)
                )
                self.bumpers.append(bumper)
                self._log_warning(f"Created BumperObject at logical ({obj_x},{obj_y}) with properties: {properties}")

            elif obj_type == 'obstacle':
                # Create and append ObstacleObject
                obj_y_relative_to_playable = obj_y # Use Y directly
                new_obstacle = ObstacleObject(
                    arena_width=self.width, # Logical width
                    arena_height=self.height, # Logical playable height
                    scoreboard_height=self.scoreboard_height,
                    scale_rect=self.scale_rect,
                    x=obj_x, # Logical X
                    y=obj_y_relative_to_playable, # Adjusted Y
                    width=obj_width,
                    height=obj_height,
                    properties=properties # Pass the properties dict
                )
                self.obstacles.append(new_obstacle) # Append to list
                self._log_warning(f"Created and appended ObstacleObject at logical ({obj_x},{obj_y}) with properties: {properties}")

            elif obj_type == 'roulette_spinner': # Match lowercase type from PMF
                # Handle the new RouletteSpinner obstacle type
                # Create and append RouletteSpinner
                # Extract specific properties needed by RouletteSpinner constructor
                radius = obj.get('radius', 100) # Get radius from top level
                spinner_props = obj.get('properties', {})
                num_segments = spinner_props.get('num_segments', 38)
                spin_speed = spinner_props.get('spin_speed_deg_s', 90)

                # Use Y coordinate directly
                obj_y_relative_to_playable = obj_y # Use Y directly
                # Instantiate RouletteSpinner directly
                new_spinner = RouletteSpinner(
                    x=obj_x, # Logical X
                    y=obj_y_relative_to_playable, # Adjusted Y
                    radius=radius,
                    num_segments=num_segments,
                    spin_speed_deg_s=spin_speed
                )
                self.obstacles.append(new_spinner) # Append to list
                self._log_warning(f"Created and appended RouletteSpinner at logical ({obj_x},{obj_y}) with radius={radius}, segments={num_segments}, speed={spin_speed}")

            elif obj_type == 'powerup_ball_duplicator': # Specific type
                # Only create one powerup for now
                if not powerup_created_from_list:
                    # Use Y coordinate directly
                    obj_y_relative_to_playable = obj_y # Keep variable name, no subtraction
                    # Get size from properties, fallback to object width
                    powerup_size = properties.get('size', obj_width)
                    self.power_up = PowerUpBallObject(
                        arena_width=self.width, # Logical width
                        arena_height=self.height, # Logical playable height
                        scoreboard_height=self.scoreboard_height,
                        scale_rect=self.scale_rect,
                        x=obj_x, # Logical X
                        y=obj_y_relative_to_playable, # Adjusted Y
                        size=powerup_size,
                        properties=properties # Pass the properties dict
                    )
                    powerup_created_from_list = True
                    self._log_warning(f"Created PowerUpBallObject at logical ({obj_x},{obj_y}) with size {powerup_size} and properties: {properties}")
                else:
                     self._log_warning(f"Ignoring additional PMF powerup object #{obj_index} (only one supported currently): {obj}")

            elif obj_type == 'portal':
                 portal_id = obj.get('id')
                 target_id = obj.get('target_id')

                 if portal_id is None:
                     self._log_warning(f"Skipping PMF portal object #{obj_index} due to missing 'id': {obj}")
                     continue
                 # Target ID can be None for unlinked portals initially

                 # Use Y coordinate directly
                 obj_y_relative_to_playable = obj_y # Keep variable name, no subtraction
                 portal = PortalObject(
                     self.width, self.height, self.scoreboard_height, self.scale_rect,
                     obj_x, obj_y_relative_to_playable, obj_width, obj_height
                     # Properties are not currently used by PortalObject/Portal, but could be passed: properties=properties
                 )
                 self.portals.append(portal)
                 self._log_warning(f"Created PortalObject (id={portal_id}, target={target_id}) at logical ({obj_x},{obj_y}).")

                 # Store data needed for linking later
                 if not hasattr(self, '_portal_link_data'):
                      self._portal_link_data = []
                 # Store ID and instance always, target_id only if present
                 self._portal_link_data.append({'instance': portal, 'id': portal_id, 'target_id': target_id})

            elif obj_type == 'piston':
                 # Use Y coordinate directly
                 obj_y_relative_to_playable = obj_y
                 piston = PistonObstacle(
                     x=obj_x,
                     y=obj_y_relative_to_playable,
                     width=obj_width,
                     height=obj_height,
                     properties=properties # Pass properties dict
                 )
                 self.obstacles.append(piston)
                 self._log_warning(f"Created PistonObstacle at logical ({obj_x},{obj_y}) with properties: {properties}")

            elif obj_type == 'tesla_coil':
                 # Use Y coordinate directly
                 obj_y_relative_to_playable = obj_y
                 # Extract specific properties for TeslaCoil constructor
                 base_radius = obj.get('base_radius', 15) # Get from top level or default
                 top_radius = obj.get('top_radius', 8)   # Get from top level or default
                 tesla_props = obj.get('properties', {}) # Get properties dict

                 tesla = TeslaCoilObstacle(
                     x=obj_x,
                     y=obj_y_relative_to_playable,
                     base_radius=base_radius,
                     top_radius=top_radius,
                     height=obj_height, # Use main height
                     properties=tesla_props # Pass properties dict
                 )
                 self.obstacles.append(tesla)
                 self._log_warning(f"Created TeslaCoilObstacle at logical ({obj_x},{obj_y}) with properties: {tesla_props}")


            elif obj_type == 'sprite': # Now correctly indented
                 self._log_warning(f"DEBUG: Found PMF object of type 'sprite': {obj}") # ++ ADDED LOG ++
                 image_path = obj.get('image_path') # Standardized key from Artemis
                 if not image_path: # Skip if path is missing or empty
                      self._log_warning(f"Skipping PMF sprite object #{obj_index} due to missing 'image_path': {obj}")
                      continue

                 # Ensure essential geometry exists for SpriteObject too
                 if obj_x is None or obj_y is None or obj_width is None or obj_height is None:
                     self._log_warning(f"Skipping PMF sprite object #{obj_index} due to missing geometry (using standard keys): {obj}")
                     continue

                 # Use Y coordinate directly
                 obj_y_relative_to_playable = obj_y # Keep variable name, no subtraction
                 sprite = SpriteObject(
                     arena_width=self.width, # Logical width
                     arena_height=self.height, # Logical playable height
                     scoreboard_height=self.scoreboard_height,
                     scale_rect=self.scale_rect,
                     x=obj_x, # Logical X
                     y=obj_y_relative_to_playable, # Adjusted Y
                     width=obj_width,
                     height=obj_height,
                     image_path=image_path,
                     properties=properties # Pass properties dict as well
                 )
                 self._log_warning(f"DEBUG: Attempting to append SpriteObject: {sprite}") # ++ ADDED LOG ++
                 self.sprites.append(sprite)
                 self._log_warning(f"Successfully created and appended SpriteObject with path '{image_path}' at logical ({obj_x},{obj_y})") # Modified log

            elif obj_type == 'candle':
                # Use Y coordinate directly
                obj_y_relative_to_playable = obj_y
                candle = CandleObject(
                    arena_width=self.width,
                    arena_height=self.height,
                    scoreboard_height=self.scoreboard_height,
                    scale_rect_func=self.scale_rect, # Pass the method itself
                    x=obj_x,
                    y=obj_y_relative_to_playable,
                    properties=properties
                )
                self.candles.append(candle)
                self._log_warning(f"Created CandleObject at logical ({obj_x},{obj_y}) with properties: {properties}")

            elif obj_type == 'ghost':
                obj_y_relative_to_playable = obj_y
                # game_ball_instance is None here, will be passed during update
                ghost = GhostObstacleObject(
                    arena_width=self.width,
                    arena_height=self.height, # Playable height
                    scoreboard_height=self.scoreboard_height,
                    scale_rect=self.scale_rect,
                    x=obj_x,
                    y=obj_y_relative_to_playable,
                    width=obj_width,
                    height=obj_height,
                    game_ball_instance=None,
                    properties=properties
                )
                # The GhostObstacleObject's __init__ handles the active_ghost_count check.
                # We only add it to the list if it's an active instance.
                if ghost.is_active_instance:
                    self.ghost_obstacles.append(ghost)
                    self._log_warning(f"Created GhostObstacleObject at logical ({obj_x},{obj_y}) with properties: {properties}")
                else:
                    self._log_warning(f"GhostObstacleObject at logical ({obj_x},{obj_y}) not added, MAX_GHOSTS_ON_SCREEN likely reached during init or instance marked inactive.")

            elif obj_type == 'pickles':
                obj_y_relative_to_playable = obj_y
                
                # Force Pickles dimensions, overriding PMF if necessary for debugging/testing
                original_pmf_width = properties.get('width')
                original_pmf_height = properties.get('height')
                properties['width'] = 60  # Force desired width
                properties['height'] = 40 # Force desired height
                if original_pmf_width != 60 or original_pmf_height != 40:
                    self._log_warning(f"Pickles object at ({obj_x},{obj_y}): Forcing width=60, height=40. Original PMF values were width={original_pmf_width}, height={original_pmf_height}.")
                else:
                    self._log_warning(f"Pickles object at ({obj_x},{obj_y}): PMF values matched desired 60x40 or were absent, ensuring 60x40.")


                pickles_instance = Pickles(
                    arena_width=self.width,
                    arena_height=self.height,
                    scoreboard_height=self.scoreboard_height,
                    scale_rect=self.scale_rect,
                    x=obj_x,
                    y=obj_y_relative_to_playable,
                    properties=properties # Pass the (potentially modified) properties
                )
                self.pickles_objects.append(pickles_instance)
                self._log_warning(f"Created Pickles object at logical ({obj_x},{obj_y}) with properties: {properties}")


            else: # Now correctly indented
                 self._log_warning(f"Unknown object type '{obj_type}' in PMF object #{obj_index}: {obj}")
            # End of the 'for' loop over objects (comment adjusted)

        # --- Post-Object Creation Linking & Defaults --- # This line is now correctly aligned (8 spaces)

       # Link portals
        if hasattr(self, '_portal_link_data') and self._portal_link_data:
             portal_id_map = {p['id']: p['instance'] for p in self._portal_link_data}
             for portal_info in self._portal_link_data:
                 portal_instance = portal_info['instance']
                 target_id = portal_info['target_id']
                 portal_id = portal_info['id'] # For logging

                 if target_id is None:
                     self._log_warning(f"Portal (id={portal_id}) has no target_id defined.")
                     continue # Skip linking if no target defined

                 target_portal_instance = portal_id_map.get(target_id)
                 if target_portal_instance:
                     portal_instance.set_target(target_portal_instance)
                     self._log_warning(f"Linked portal (id={portal_id}) to target portal (id={target_id}).")
                 else:
                     self._log_warning(f"Could not link portal (id={portal_id}): Target portal with id={target_id} not found in PMF objects.")

             del self._portal_link_data # Clean up temporary data


        # Create default obstacle if flag is set AND the obstacles list is empty
        if not self.obstacles and self.can_spawn_obstacles: # Check if list is empty
             self._log_warning("No obstacles defined in PMF 'objects', creating default obstacle because 'can_spawn_obstacles' is true.")
             # Create default obstacle (ObstacleObject handles random positioning)
             # Pass empty properties dict for default obstacle
             default_obstacle = ObstacleObject(
                 arena_width=self.width,
                 arena_height=self.height,
                 scoreboard_height=self.scoreboard_height,
                 scale_rect=self.scale_rect,
                 properties={}
             )
             self.obstacles.append(default_obstacle) # Append default to list

        # Create GhostObstacles if 'can_spawn_obstacles' flag is set.
        # These are spawned in addition to any 'ghost' type objects defined in the PMF.
        # The GhostObstacle class itself manages the maximum number on screen.
        # GhostObstacle.reset_class_vars() was already called at the start of _create_objects_from_pmf
        if self.can_spawn_ghosts: # Use the new specific flag
            self._log_warning("Runtime Spawning: Checking for GhostObstacle creation as 'can_spawn_ghosts' is true.")
            
            # Try to spawn ghosts up to the MAX_GHOSTS_ON_SCREEN limit.
            # PMF-defined ghosts would have already incremented active_ghost_count.
            for _ in range(GhostObstacle.MAX_GHOSTS_ON_SCREEN):
                if GhostObstacle.active_ghost_count >= GhostObstacle.MAX_GHOSTS_ON_SCREEN:
                    self._log_warning(f"Runtime Spawning: Ghost limit ({GhostObstacle.MAX_GHOSTS_ON_SCREEN}) reached. No more runtime ghosts will be spawned. Current active: {GhostObstacle.active_ghost_count}")
                    break # Stop trying if max is already met or exceeded

                ghost_width = 30  # Default width for runtime spawned ghosts
                ghost_height = 40 # Default height for runtime spawned ghosts
                
                # Random position within the playable area (self.height is playable height)
                rand_x = random.randint(ghost_width // 2, self.width - ghost_width // 2)
                rand_y = random.randint(ghost_height // 2, self.height - ghost_height // 2)

                ghost = GhostObstacleObject(
                    arena_width=self.width,
                    arena_height=self.height, # Playable height
                    scoreboard_height=self.scoreboard_height,
                    scale_rect=self.scale_rect,
                    x=rand_x,
                    y=rand_y,
                    width=ghost_width,
                    height=ghost_height,
                    game_ball_instance=None, # Will be set during update loop
                    properties={} # No specific properties for runtime spawned
                )
                
                # GhostObstacleObject.__init__ calls GhostObstacle.__init__,
                # which increments active_ghost_count and sets ghost.is_active_instance.
                if ghost.is_active_instance:
                    self.ghost_obstacles.append(ghost)
                    self._log_warning(f"Runtime Spawning: Successfully spawned and added GhostObstacleObject at logical ({rand_x},{rand_y}). Active count now: {GhostObstacle.active_ghost_count}")
                else:
                    # This implies GhostObstacle.__init__ decided not to activate this instance (MAX reached).
                    self._log_warning(f"Runtime Spawning: GhostObstacleObject at logical ({rand_x},{rand_y}) created but not activated (MAX likely reached during its init). Active count: {GhostObstacle.active_ghost_count}")
                    break # If an instance wasn't activated, the limit is hit.
        
         # Create default powerup if flag is set AND none were created from list
        if not powerup_created_from_list and self.can_spawn_powerups:
             self._log_warning("No powerup defined in PMF 'objects', creating default powerup because 'can_spawn_powerups' is true.")
             # Create default powerup (PowerUpBallObject handles positioning)
             # Pass empty properties dict for default powerup
             default_x = self.width / 2
             default_y = self.height / 2
             self.power_up = PowerUpBallObject(
                 arena_width=self.width,
                 arena_height=self.height,
                 scoreboard_height=self.scoreboard_height,
                 scale_rect=self.scale_rect,
                 x=default_x,
                 y=default_y,
                 # Use default size from constructor
                 properties={}
             )


    def _create_objects_from_params(self, params):
        """Creates game objects using the structured params dictionary (for class levels)."""
        # This contains the original object creation logic based on the params dict

        # Obstacle (obstacle_params should already be set)
        # Only create if the flag allows it (relevant for class-based levels too)
        if self.can_spawn_obstacles:
            self.obstacle = self.create_obstacle(self.obstacle_params)
        else:
            self.obstacle = None # Ensure no obstacle if flag is false

        # Manholes (original 4-corner logic) - Keep for class-based levels
        if 'manholes' in params:
            manhole_params = params['manholes']
            positions = manhole_params.get('positions', {})
            manhole_width = manhole_params.get('width', 20)
            manhole_height = manhole_params.get('height', 20)
            # Get manhole properties if defined for class levels
            manhole_props = manhole_params.get('properties', {})
            pos_bl = positions.get('bottom_left', {'x': 0.1, 'y': 0.8})
            bottom_left = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect, pos_bl['x'], pos_bl['y'], manhole_width, manhole_height, True, manhole_props)
            pos_br = positions.get('bottom_right', {'x': 0.9, 'y': 0.8})
            bottom_right = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect, pos_br['x'], pos_br['y'], manhole_width, manhole_height, True, manhole_props)
            pos_tl = positions.get('top_left', {'x': 0.1, 'y': 0.2})
            top_left = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect, pos_tl['x'], pos_tl['y'], manhole_width, manhole_height, False, manhole_props)
            pos_tr = positions.get('top_right', {'x': 0.9, 'y': 0.2})
            top_right = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect, pos_tr['x'], pos_tr['y'], manhole_width, manhole_height, False, manhole_props)
            self.manholes.extend([bottom_left, bottom_right, top_left, top_right])

        # Power-up (original logic) - Keep for class-based levels
        # Only create if the flag allows it
        if self.can_spawn_powerups:
            power_ups_params = params.get('power_ups', {})
            if 'ball_duplicator' in power_ups_params:
                power_up_config = power_ups_params['ball_duplicator']
                if power_up_config.get('active', False):
                    pos = power_up_config.get('position', {'x': 0.5, 'y': 0.5})
                    size = power_up_config.get('size', 15)
                    # Get powerup properties if defined for class levels
                    powerup_props = power_up_config.get('properties', {})
                    self.power_up = PowerUpBallObject(self.width, self.height, self.scoreboard_height, self.scale_rect, pos['x'], pos['y'], size, powerup_props)
        else:
            self.power_up = None # Ensure no powerup if flag is false

        # Goals (original logic) - Keep for class-based levels
        # Only create if the flag allows it
        if self.use_goals:
            goals_params = params.get('goals', {}) # Check specific goal params for class levels
            if goals_params:
                if goals_params.get('left', True): # Default to true if 'goals' dict exists but 'left' is missing
                    self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=True))
                if goals_params.get('right', True): # Default to true
                    self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=False))
            # If 'goals' dict is missing in params, but use_goals is True, maybe add defaults?
            # elif not goals_params: # Add default goals if use_goals=True but no specific params
            #     self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=True))
            #     self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=False))

        # Portals (original logic) - Keep for class-based levels
        if 'portals' in params:
            portal_params = params['portals']
            positions = portal_params.get('positions', {})
            portal_width = portal_params.get('width', 30)
            portal_height = portal_params.get('height', 30)
            pos_tl = positions.get('top_left', {'x': 0.2, 'y': 0.1})
            top_left = PortalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, pos_tl['x'], pos_tl['y'], portal_width, portal_height)
            pos_bl = positions.get('bottom_left', {'x': 0.2, 'y': 0.9})
            bottom_left = PortalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, pos_bl['x'], pos_bl['y'], portal_width, portal_height)
            pos_tr = positions.get('top_right', {'x': 0.8, 'y': 0.1})
            top_right = PortalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, pos_tr['x'], pos_tr['y'], portal_width, portal_height)
            pos_br = positions.get('bottom_right', {'x': 0.8, 'y': 0.9})
            bottom_right = PortalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, pos_br['x'], pos_br['y'], portal_width, portal_height)
            top_left.set_target(bottom_right)
            bottom_right.set_target(top_left)
            bottom_left.set_target(top_right)
            top_right.set_target(bottom_left)
            self.portals.extend([top_left, bottom_left, top_right, bottom_right])


    def _log_warning(self, message):
        """Logs a warning message, trying the debug console first."""
        try:
            from .Submodules.Ping_DBConsole import get_console
            debug_console = get_console()
            debug_console.log(f"Warning: {message}")
        except ImportError:
            print(f"Warning: {message}") # Fallback to print if console not available

    def _load_pmf(self, file_path):
        """Loads and parses a .pmf file (assuming JSON format)."""
        print(f"Attempting to load PMF: {file_path}") # Debug print
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            # TODO: Add schema validation for PMF data structure here
            print(f"Successfully loaded PMF data.") # Debug print
            return data # Assuming the JSON root is the 'params' dictionary
        except FileNotFoundError:
             print(f"Error: PMF file not found at {file_path}")
             raise # Re-raise the exception
        except json.JSONDecodeError as e:
             print(f"Error: Invalid JSON in PMF file {file_path}: {e}")
             raise # Re-raise the exception
        except Exception as e:
             print(f"Error: An unexpected error occurred loading PMF {file_path}: {e}")
             raise # Re-raise the exception


    # --- Rest of the methods copied from Arena ---
    # Minor modification to create_obstacle to accept params
    def create_obstacle(self, obstacle_params):
        """Create a new obstacle in the arena based on params."""
        # Use default values if not provided in params
        # (Assuming ObstacleObject handles defaults or specific params are passed)
        # Check if obstacle is explicitly disabled in params
        if not obstacle_params or obstacle_params.get('active', True) == False:
             return None # Return None if no obstacle params or explicitly inactive

        # Ensure we only create if the level allows it
        if not self.can_spawn_obstacles:
            return None

        # ObstacleObject handles its own default positioning and sizing internally.
        # We only need to pass the arena parameters and scale function.
        # We can optionally pass width/height if defined in obstacle_params.
        obstacle_width = obstacle_params.get('size', {}).get('width') if obstacle_params.get('size') else None
        obstacle_height = obstacle_params.get('size', {}).get('height') if obstacle_params.get('size') else None

        # Use default width/height from ObstacleObject if not specified
        if obstacle_width is not None and obstacle_height is not None:
            return ObstacleObject(
                arena_width=self.width,
                arena_height=self.height,
                scoreboard_height=self.scoreboard_height,
                scale_rect=self.scale_rect,
                width=obstacle_width,
                height=obstacle_height
            )
        else:
             # Call with defaults if size wasn't specified in params
             return ObstacleObject(
                 arena_width=self.width,
                 arena_height=self.height,
                 scoreboard_height=self.scoreboard_height,
                 scale_rect=self.scale_rect
             )

    def check_goal_collisions(self, ball):
        """Check for collisions between ball and goals."""
        # Only check if goals are used in this level
        if not self.use_goals:
            return None

        for goal in self.goals:
            result = goal.handle_collision(ball)
            if result == "left" or result == "right":
                return result
            elif result == "bounce":
                # Continue checking other goals if it's just a bounce
                pass
        return None # Return None if no score occurred

    def check_portal_collisions(self, ball):
        """Check for collisions between ball and portals."""
        # Update cooldowns for all portals
        for portal in self.portals:
            portal.update_cooldown()

        # Check for collisions
        for portal in self.portals:
            if portal.handle_collision(ball):
                return True # Exit early once a portal collision occurs
        return False

    def update_manholes(self, delta_time=1/60):
        """Update all manhole states."""
        active_manholes = [m for m in self.manholes if m.is_spouting]
        for manhole in self.manholes:
            manhole.update(active_manholes, delta_time)

    def check_manhole_collisions(self, ball):
        """Check for collisions between ball and manholes."""
        for manhole in self.manholes:
            if manhole.handle_collision(ball):
                return True # Exit early once a manhole collision occurs
        return False
        
    def check_bumper_collisions(self, ball, sound_manager=None): # Added sound_manager
        """Check for collisions between ball and bumpers."""
        for bumper in self.bumpers:
            # Pass sound_manager to BumperObject's handle_collision
            if bumper.handle_collision(ball, sound_manager):
                return True # Exit early once a bumper collision occurs
        return False

    def update_ghosts(self, delta_time, game_ball_instance):
        """Update all ghost states and handle their removal and respawning."""
        # Remove any ghosts that are done
        for ghost_obj in self.ghost_obstacles[:]: # Iterate over a copy for safe removal
            # Pass self.pickles_objects to the ghost's update method
            ghost_obj.update(delta_time, game_ball_instance, self.candles, self.pickles_objects, self.scale, self.scale_rect)
            if ghost_obj.is_done():
                self.ghost_obstacles.remove(ghost_obj)
                self._log_warning(f"Removed an inactive ghost. Active count: {GhostObstacle.active_ghost_count}")

        # Attempt to spawn new ghosts if below max and level allows
        if self.can_spawn_ghosts:
            while GhostObstacle.active_ghost_count < GhostObstacle.MAX_GHOSTS_ON_SCREEN:
                self._log_warning(f"Attempting to spawn new ghost. Current active: {GhostObstacle.active_ghost_count}, Max: {GhostObstacle.MAX_GHOSTS_ON_SCREEN}")
                ghost_width = 30
                ghost_height = 40
                # Ensure spawn position is within playable area (self.height is playable height)
                rand_x = random.randint(ghost_width // 2, self.width - ghost_width // 2)
                rand_y = random.randint(ghost_height // 2, self.height - ghost_height // 2)

                new_ghost = GhostObstacleObject(
                    arena_width=self.width,
                    arena_height=self.height, # Playable height
                    scoreboard_height=self.scoreboard_height,
                    scale_rect=self.scale_rect,
                    x=rand_x,
                    y=rand_y,
                    width=ghost_width,
                    height=ghost_height,
                    game_ball_instance=game_ball_instance,
                    properties={}
                )
                if new_ghost.is_active_instance:
                    self.ghost_obstacles.append(new_ghost)
                    self._log_warning(f"Successfully spawned GhostObstacleObject at logical ({rand_x},{rand_y}). Active count now: {GhostObstacle.active_ghost_count}")
                else:
                    # This means GhostObstacle.__init__ decided not to activate, likely because MAX_GHOSTS_ON_SCREEN was (momentarily) hit
                    # by another concurrent spawn attempt if this were threaded, or if MAX_GHOSTS_ON_SCREEN is 0.
                    # Or, if the GhostObstacleObject itself decided not to be active for other reasons.
                    self._log_warning(f"Failed to spawn new ghost (MAX likely reached or instance not activated during its init). Active count: {GhostObstacle.active_ghost_count}")
                    break # Stop trying to spawn if one attempt fails to activate

    def update_pickles(self, delta_time, all_game_entities, scale_factor):
        """Update all Pickles instances."""
        
        balls_for_pickles = []
        if all_game_entities:
            for entity in all_game_entities:
                # Check if the entity is an instance of BallObject and has a 'ball' attribute
                if isinstance(entity, BallObject) and hasattr(entity, 'ball'):
                    balls_for_pickles.append(entity.ball)

        current_game_objects_for_pickles = {
            'balls': balls_for_pickles,
            'ghosts': self.ghost_obstacles,
            'candles': self.candles
        }
        
        if not self.pickles_objects:
            # print("DEBUG: No Pickles objects to update.")
            return

        # print(f"DEBUG: Updating {len(self.pickles_objects)} Pickles objects. Balls for Pickles: {len(balls_for_pickles)}")
        for pickles_obj in self.pickles_objects:
            pickles_obj.update(delta_time, current_game_objects_for_pickles, scale_factor)

    def reset_obstacle(self):
        """Resets obstacles. Clears the list and adds a default if applicable."""
        self.obstacles = [] # Clear the list
        self.ghost_obstacles = [] # Clear ghost obstacles as well
        self.pickles_objects = [] # Clear Pickles objects as well
        if hasattr(GhostObstacle, 'reset_class_vars'): # Reset class-level counters for ghosts
            GhostObstacle.reset_class_vars()

        # Re-add a default obstacle if the flag is set (mirroring PMF loading logic)
        if self.can_spawn_obstacles: # This remains for general obstacles
             self._log_warning("Resetting obstacles: Adding default obstacle because 'can_spawn_obstacles' is true.")
             default_obstacle = ObstacleObject(
                 arena_width=self.width,
                 arena_height=self.height,
                 scoreboard_height=self.scoreboard_height,
                 scale_rect=self.scale_rect,
                 properties={}
             )
             self.obstacles.append(default_obstacle)
        # Note: This doesn't re-load obstacles from the original PMF file upon reset.
        # A more complex reset might re-run parts of _create_objects_from_pmf.


    def initialize_scoreboard(self):
        """Initialize the scoreboard after level selection."""
        # Ensure colors are loaded before initializing
        if not hasattr(self, 'colors') or not self.colors:
             self._log_warning("Cannot initialize scoreboard: Colors not loaded.")
             return

        self.scoreboard = Scoreboard(
            height=self.scoreboard_height,
            scale_y=1.0,  # Will be updated when scaling changes
            colors={
                'WHITE': self.colors.get('WHITE', (255, 255, 255)), # Use .get() with defaults
                'DARK_BLUE': self.colors.get('DARK_BLUE', (0, 0, 139))
            }
        )

    def update_scaling(self, window_width, window_height):
        """Update scaling factors based on window dimensions."""
        # Use total logical height for scaling calculations
        total_logical_height = self.height + self.scoreboard_height
        if self.width <= 0 or total_logical_height <= 0: # Prevent division by zero
             self.scale_x = 1.0
             self.scale_y = 1.0
             self.scale = 1.0
             self.offset_x = 0
             self.offset_y = 0
             return

        # Calculate scale based on the *entire* logical area (playable + scoreboard) fitting into the window
        self.scale_x = window_width / self.width
        self.scale_y = window_height / total_logical_height
        self.scale = min(self.scale_x, self.scale_y) # Use the smaller scale factor to fit everything

        # Calculate centering offsets based on the scaled total logical size
        scaled_total_width = self.width * self.scale
        scaled_total_height = total_logical_height * self.scale
        self.offset_x = (window_width - scaled_total_width) / 2
        self.offset_y = (window_height - scaled_total_height) / 2

        # Update scoreboard scaling if initialized
        if self.scoreboard:
            # Scoreboard should probably scale uniformly with the rest of the game
            self.scoreboard.scale_y = self.scale # Use the overall scale factor

        # Signal sludge texture regeneration if needed
        if self.level_background == 'sewer':
             with self.sludge_texture_lock:
                 self.needs_sludge_texture_update = True
             self._log_warning("Scaling updated, flagged sludge texture for regeneration.")


    def scale_rect(self, rect):
        """Scale a rectangle according to current scaling factors."""
        # Ensure rect is a pygame.Rect
        if not isinstance(rect, pygame.Rect):
             # Attempt to convert if it looks like a rect tuple/list
             if isinstance(rect, (list, tuple)) and len(rect) == 4:
                 try:
                      rect = pygame.Rect(rect)
                 except TypeError as e:
                      self._log_warning(f"Failed to convert {rect} to pygame.Rect: {e}")
                      return pygame.Rect(0,0,0,0)
             else:
                 # Handle error or return a default rect if conversion fails
                 self._log_warning(f"scale_rect received non-Rect type: {type(rect)}, value: {rect}")
                 return pygame.Rect(0,0,0,0) # Or raise an error

        # Ensure scale factors are positive
        scale_w = max(0, rect.width * self.scale)
        scale_h = max(0, rect.height * self.scale)

        # The key change: don't add scoreboard_height to the y-coordinate
        # This way, (0,0) in logical space maps to the top-left of the playable area
        return pygame.Rect(
            int((rect.x * self.scale) + self.offset_x),
            # Add offset_y directly without adding scoreboard height
            int((rect.y * self.scale) + self.offset_y + (self.scoreboard_height * self.scale)),
            int(scale_w),
            int(scale_h)
        )

    def draw_center_line(self, screen):
        """Draw the dashed center line."""
        # Check if center line should be drawn
        if self.center_line_box_width <= 0 or self.center_line_box_height <= 0:
            return

        box_width = self.center_line_box_width * self.scale
        box_height = self.center_line_box_height * self.scale
        box_spacing = self.center_line_box_spacing * self.scale # Scale spacing too

        # Prevent division by zero if height or spacing is zero/negative after scaling
        total_box_height_scaled = box_height + box_spacing
        if total_box_height_scaled <= 0:
            return

        # Calculate number of boxes based on available playable height (self.height)
        drawable_height_scaled = self.height * self.scale # self.height is playable height
        num_boxes = int(drawable_height_scaled // total_box_height_scaled)

        # Calculate starting y position (top of the playable area)
        start_y = self.scoreboard_height * self.scale + self.offset_y

        # Calculate starting x position (centered)
        start_x = (self.width / 2) * self.scale + self.offset_x - (box_width / 2)


        for i in range(num_boxes):
            box_y = start_y + i * total_box_height_scaled
            # Ensure colors are available
            line_color = self.colors.get('WHITE', (255, 255, 255))
            # Ensure rect dimensions are positive integers for drawing
            draw_x = int(start_x)
            draw_y = int(box_y)
            draw_w = int(max(1, box_width)) # Ensure at least 1 pixel wide
            draw_h = int(max(1, box_height)) # Ensure at least 1 pixel high

            pygame.draw.rect(screen, line_color, (draw_x, draw_y, draw_w, draw_h))


    def draw_scoreboard(self, screen, player_name, score_a, opponent_name, score_b, font, respawn_timer=None):
        """Draw the scoreboard at the top of the arena."""
        if self.scoreboard:
            # Ensure font is loaded and valid
            if font:
                 self.scoreboard.draw(screen, player_name, score_a, opponent_name, score_b, font, respawn_timer)
            else:
                 self._log_warning("Cannot draw scoreboard: Font not provided.")

    def get_paddle_positions(self):
        """Get the paddle positions from the loaded level configuration."""
        # Return default positions if not specified in params
        return {
            'left': self.paddle_positions.get('left', {'x': 0.05, 'y': 0.5}), # Default left paddle pos
            'right': self.paddle_positions.get('right', {'x': 0.95, 'y': 0.5}) # Default right paddle pos
        }

    def get_level_name(self):
        """Returns the name of the loaded level."""
        return self.level_name


    def get_ball_position(self, ball_size):
        """Get the initial ball position."""
        # Allow PMF to specify initial ball position
        # TODO: Allow PMF to define ball start pos via an object type or property
        # For now, always start ball in the center.
        ball_start_pos = {'x': 0.5, 'y': 0.5}

        # Convert relative coordinates to absolute pixels
        abs_x = ball_start_pos['x'] * self.width
        abs_y = ball_start_pos['y'] * self.height

        # Adjust for ball size to center it
        return (
            abs_x - ball_size / 2,
            abs_y - ball_size / 2
        )


    def draw_pause_overlay(self, screen, font):
        """Draw pause overlay and text."""
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA) # Use SRCALPHA for transparency
        overlay.fill((*self.colors.get('BLACK', (0,0,0)), 128)) # Fill with semi-transparent black
        screen.blit(overlay, (0, 0))

        if font:
            try:
                pause_text_render = font.render("Paused", True, self.colors.get('WHITE', (255, 255, 255)))
                screen.blit(pause_text_render, (
                    screen.get_width()//2 - pause_text_render.get_width()//2,
                    screen.get_height()//2 - pause_text_render.get_height()//2
                ))
            except Exception as e:
                 self._log_warning(f"Failed to render pause text: {e}")
        else:
             self._log_warning("Cannot draw pause text: Font not provided.")


    def check_power_up_collision(self, ball, ball_count):
        """Check for collisions between ball and power-up."""
        # Only check if powerups are allowed and one exists
        if not self.can_spawn_powerups or not self.power_up:
            return None

        # Check the 'active' attribute of the underlying PowerUpBall instance
        # and directly return the result of its collision handler.
        # The handler returns a raw Ball instance if collision occurs, otherwise None.
        # The main game loop in ping_base.py handles creating the BallObject.
        if self.power_up.power_up.active:
            return self.power_up.handle_collision(ball)

        return None # Return None if power-up is inactive or no collision


    def update_power_up(self, ball_count):
        """Update power-up state and check for respawn."""
        # Only update if powerups are allowed and one exists
        if not self.can_spawn_powerups or not self.power_up:
            return

        # Pass arena dimensions and obstacles for valid spawn position
        # Combine all potential collision objects into one list
        obstacles_for_spawn = [obs for obs in self.obstacles + self.goals + self.portals + self.manholes + self.bumpers + self.ghost_obstacles if obs is not None]

        self.power_up.update(
            ball_count,
            self.width,
            self.height,
            self.scoreboard_height,
            obstacles_for_spawn # Pass the combined list
        )

    # Removed redundant _draw_sewer_background method.
    # The drawing is now handled by the imported function from ping_graphics.py
    def draw(self, screen, game_objects, font, player_name, score_a, opponent_name, score_b, respawn_timer=None, paused=False):
        """Draw the complete game state."""
        # Create intermediate surface for shader processing if shaders might be used
        use_intermediate = self._settings and self._shader_instance and self._settings.get_shader_enabled()
        target_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA) if use_intermediate else screen

        # --- Fill background first to prevent artifacts ---
        target_surface.fill(self.colors.get('BLACK', (0, 0, 0))) # Clear with black

        # --- Draw Specific Level Background ---
        try:
            # Get the drawing function based on the level_background identifier
            # Ensure a default like 'default' or 'color' exists in ping_graphics
            bg_identifier = self.level_background if self.level_background else 'default'
            draw_func = get_background_draw_function(bg_identifier)

            if draw_func:
                # Acquire lock before drawing if it's the sewer background
                # to prevent texture being modified while drawing reads it.
                lock_acquired = False
                if bg_identifier == 'sewer':
                    self.sludge_texture_lock.acquire()
                    lock_acquired = True

                try:
                    # Call the function to draw the background, passing the compiler instance
                    # The draw_func is expected to handle filling the background first
                    # For sewer, it will read self.sludge_texture internally (under lock)
                    draw_func(target_surface, self)
                finally:
                    # Ensure lock is released even if drawing fails
                    if lock_acquired:
                        self.sludge_texture_lock.release()

            else:
                # Fallback if no specific function found (should ideally not happen if 'default' exists)
                self._log_warning(f"No background draw function found for identifier: '{bg_identifier}'. Drawing solid color.")
                # Don't fill again here, just draw center line if needed
                self.draw_center_line(target_surface) # Draw center line on top
        except Exception as e:
            self._log_warning(f"Error getting/drawing background for '{bg_identifier}': {e}")
            # Don't fill again here, just draw center line if needed
            self.draw_center_line(target_surface) # Draw center line on top

        # --- Draw Game Elements ---
        # No clipping needed now, scale_rect handles coordinate mapping.

        # Draw Sprites
        if self.sprites:
             for sprite in self.sprites:
                 sprite.draw(target_surface) # SpriteObject uses scale_rect internally

        # Draw Candles
        if self.candles:
            for candle in self.candles:
                candle.update(1/60.0, self.scale) # Update animation with fixed dt and current scale
                candle.draw(target_surface, self.scale) # Draw candle

        # Draw portals
        for portal in self.portals:
             portal.draw(target_surface, self.colors, self.scale_rect) # PortalObject uses scale_rect

        # Draw manholes and bumpers
        for manhole in self.manholes:
            manhole.draw(target_surface, self.colors) # ManholeObject uses scale_rect
        
        # Update and Draw Pickles
        # Assuming a fixed delta_time for now, similar to bumpers.
        # game_objects is passed to LevelCompiler.draw from ping_base.py
        self.update_pickles(self.dt, game_objects, self.scale)

        for bumper in self.bumpers:
            bumper.update(1/60)
            bumper.draw(target_surface, self.colors.get('WHITE', (255, 255, 255))) # BumperObject uses scale_rect

        # Draw goals
        for goal in self.goals:
            goal.draw(target_surface, self.colors.get('WHITE', (255, 255, 255))) # GoalObject uses scale_rect

        # Draw obstacles
        for obstacle in self.obstacles: # Iterate through the list
             if obstacle and hasattr(obstacle, 'draw') and callable(obstacle.draw):
                 # ObstacleObject and RouletteSpinner use scale_rect or handle scaling internally
                 obstacle.draw(target_surface, self.colors, self.scale_rect)
        
        # Draw Ghost Obstacles
        for ghost_obj in self.ghost_obstacles:
            ghost_obj.draw(target_surface, self.colors)

        # Draw Pickles Objects
        for pickles_obj in self.pickles_objects:
            pickles_obj.draw(target_surface, self.colors) # Pickles.draw uses scale_rect internally via self.scale_rect


        # Draw game objects (Paddles, Ball)
        paddles = [obj for obj in game_objects if not isinstance(obj, BallObject)]
        balls = [obj for obj in game_objects if isinstance(obj, BallObject)]
        for obj in paddles:
             if hasattr(obj, 'draw') and callable(obj.draw):
                 # Assumes PaddleObject.draw uses scale_rect or handles scaling
                 obj.draw(target_surface, self.colors.get('WHITE', (255, 255, 255)))
        # Draw power-up if active
        if self.power_up and self.power_up.power_up.active:
            # PowerUpBallObject uses scale_rect
            self.power_up.draw(target_surface, self.colors.get('WHITE', (255, 255, 255)))
        # Draw balls last
        for obj in balls:
             if hasattr(obj, 'draw') and callable(obj.draw):
                 # Assumes BallObject.draw uses scale_rect or handles scaling
                 obj.draw(target_surface, self.colors.get('WHITE', (255, 255, 255)))

        # --- Draw Lighting Layer ---
        if self.has_lighting:
            # Create a surface for the dimming overlay
            # Playable area dimensions scaled
            overlay_width = int(self.width * self.scale)
            overlay_height = int(self.height * self.scale)

            if overlay_width > 0 and overlay_height > 0:
                lighting_overlay_surface = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                lighting_overlay_surface.fill((0, 0, 0, 192))  # Black with ~75% opacity (192/255)

                # Calculate position for the overlay (top-left of the scaled playable area)
                overlay_x = self.offset_x
                overlay_y = self.offset_y + (self.scoreboard_height * self.scale)

                # Apply light sources (e.g., from candles)
                for candle in self.candles:
                    if hasattr(candle, 'get_light_properties'):
                        light_props = candle.get_light_properties(self.scale)
                        if light_props:
                            # light_props contains scaled x, y, radius, intensity
                            # x, y are absolute screen coordinates
                            # We need to draw on lighting_overlay_surface, so adjust coordinates
                            light_center_x_on_overlay = light_props['x'] - overlay_x
                            light_center_y_on_overlay = light_props['y'] - overlay_y
                            radius = light_props['radius']
                            intensity = light_props['intensity'] # 0 to 1

                            if radius > 0 and intensity > 0:
                                # Create a circular "hole" in the overlay.
                                # The alpha value determines how much the dimming is reduced.
                                # Max reduction (alpha 0) for full intensity.
                                # No reduction (alpha 192) for zero intensity (though light_props would be None).
                                # For simplicity, let's make it fully clear if intensity > some threshold,
                                # or scale the transparency.
                                # Using (0,0,0,0) will make the area fully transparent.
                                # A more advanced approach could use intensity to blend.
                                # For now, full punch-out:
                                light_color_alpha = 0 # Fully transparent
                                
                                # To make the light effect softer, we can draw a gradient or use blending.
                                # For now, a simple circle punch-out:
                                # Ensure integer coordinates for drawing
                                draw_x = int(light_center_x_on_overlay)
                                draw_y = int(light_center_y_on_overlay)
                                draw_radius = int(radius)
                                center_x_on_overlay = int(light_center_x_on_overlay)
                                center_y_on_overlay = int(light_center_y_on_overlay)

                                if draw_radius > 0 and intensity > 0:
                                    # Create a single surface for the entire light effect gradient
                                    light_effect_surface_size = draw_radius * 2
                                    if light_effect_surface_size <= 0: continue

                                    light_effect_surface = pygame.Surface((light_effect_surface_size, light_effect_surface_size), pygame.SRCALPHA)
                                    light_effect_surface.fill((0, 0, 0, 192))  # Initialize with overlay's base alpha

                                    # Iterate from the outer edge of the light to the center, drawing on light_effect_surface
                                    for r_step in range(draw_radius, 0, -1):
                                        if r_step <= 0: continue # Should not happen with range(draw_radius, 0, -1) if draw_radius > 0

                                        edge_progress = r_step / float(draw_radius)
                                        min_alpha_at_center = 192 * (1.0 - intensity)
                                        alpha_value = int(min_alpha_at_center + (192 - min_alpha_at_center) * edge_progress)
                                        alpha_value = max(0, min(192, alpha_value))

                                        # Draw circle directly onto light_effect_surface, centered
                                        # The center of light_effect_surface is (draw_radius, draw_radius)
                                        pygame.gfxdraw.filled_circle(light_effect_surface, draw_radius, draw_radius, r_step, (0, 0, 0, alpha_value))

                                    # Blit the completed light_effect_surface onto the lighting_overlay_surface
                                    blit_pos_x = center_x_on_overlay - draw_radius
                                    blit_pos_y = center_y_on_overlay - draw_radius
                                    lighting_overlay_surface.blit(light_effect_surface, (blit_pos_x, blit_pos_y), special_flags=pygame.BLEND_RGBA_MIN)
                target_surface.blit(lighting_overlay_surface, (overlay_x, overlay_y))


        # --- Draw UI Elements ---
        # Scoreboard is drawn relative to the top of the screen (0,0) before offsets/scaling are applied by its own draw method
        self.draw_scoreboard(target_surface, player_name, score_a, opponent_name, score_b, font, respawn_timer)

        # Draw pause overlay if paused (drawn last on the target surface)
        if paused:
            self.draw_pause_overlay(target_surface, font)

        # --- Final Blit / Shader Application ---
        if use_intermediate:
            # Try to apply shader if enabled and available
            try:
                processed = self._shader_instance.apply_to_surface(target_surface)
                screen.blit(processed, (0, 0))
            except Exception as e:
                if not self._shader_warning_shown:
                    self._log_warning(f"Shader processing failed, using fallback rendering: {e}")
                    self._shader_warning_shown = True
                # Fall back to direct rendering if shader failed
                screen.blit(target_surface, (0, 0))
        # else: screen already holds the drawn elements if not using intermediate

# Helper function to get parameters from a source (path or instance)
# This could be used externally to create the LevelCompiler instance
def load_level_parameters(level_source):
     if isinstance(level_source, str) and level_source.lower().endswith('.pmf'):
         try:
             # Use the compiler's internal methods for consistency
             compiler = LevelCompiler(level_source)
             # We need the parsed 'params', not the raw pmf_data
             # The compiler __init__ already does the parsing.
             # This helper might be redundant now? Or should return the compiler instance?
             # Let's return the parsed params from the instance:
             params = {}
             params['dimensions'] = {'width': compiler.width, 'height': compiler.height, 'scoreboard_height': compiler.scoreboard_height}
             params['bounce_walls'] = compiler.bounce_walls
             params['use_goals'] = compiler.use_goals
             params['can_spawn_obstacles'] = compiler.can_spawn_obstacles
             params['can_spawn_powerups'] = compiler.can_spawn_powerups
             params['can_spawn_ghosts'] = compiler.can_spawn_ghosts # Add new property
             params['colors'] = compiler.colors
             params['center_line'] = {'box_width': compiler.center_line_box_width, 'box_height': compiler.center_line_box_height, 'box_spacing': compiler.center_line_box_spacing}
             params['paddle_positions'] = compiler.paddle_positions
             params['background_details'] = compiler.background_details
             # Note: This doesn't return the created objects (manholes, etc.)
             return params

         except Exception as e:
             print(f"Error loading/parsing PMF {level_source} via LevelCompiler: {e}")
             # Removed fallback to DebugLevel params
             # Return None or raise error to indicate failure
             print(f"Error loading PMF {level_source}, cannot fallback.")
             return None # Or raise ValueError("Failed to load PMF")
     # Removed elif check for class-based levels (get_parameters)
     # elif hasattr(level_source, 'get_parameters'):
     #     # Handle potential remaining class-based levels (if any)
     #     try:
     #         # Instantiate if it's a class type, otherwise assume it's an instance
     #         instance = level_source() if isinstance(level_source, type) else level_source
     #         return instance.get_parameters()
     #     except Exception as e:
     #         print(f"Error getting parameters from level class {level_source}: {e}")
     #         return None # Indicate error
         return level_source.get_parameters()
     else:
         print(f"Invalid level source: {level_source}. Cannot use DebugLevel params.")
         # Return None or raise error
         return None # Or raise ValueError("Invalid level source")