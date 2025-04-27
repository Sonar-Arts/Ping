# Modules/Ping_MCompile.py
# Initially, this will be a copy of Ping_Arena.py
# We will modify it to handle .pmf files

import pygame
import random  # Import random for background generation
import math  # Import math for river animation
import json # Import JSON for PMF parsing (assuming JSON format)
import threading
import time
from Modules.Ping_GameObjects import ObstacleObject, GoalObject, PortalObject, PowerUpBallObject, BallObject, ManHoleObject
# Removed import for DebugLevel, SewerLevel
from Modules.Submodules.Ping_Scoreboard import Scoreboard
# Import the generation function specifically
from Modules.ping_graphics import get_background_draw_function, generate_sludge_texture

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
        self.height = dimensions.get('height', 600)
        self.scoreboard_height = dimensions.get('scoreboard_height', 60)

        # --- Store Core Level Properties ---
        # These are now parsed from PMF or taken from level instance params
        self.bounce_walls = params.get('bounce_walls', True) # Default to True if missing
        self.use_goals = params.get('use_goals', True) # Default to True if missing
        self.can_spawn_obstacles = params.get('can_spawn_obstacles', False) # Default to False
        self.can_spawn_powerups = params.get('can_spawn_powerups', False) # Default to False


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
            'MANHOLE_DETAIL': (110, 110, 110) # Added detail color
        })

        # Store background details if available (kept for potential fallback/compatibility)
        self.background_details = params.get('background_details', None)
        # Store new level properties
        self.level_music = params.get('level_music', None) # Get from parsed params
        self.level_background = params.get('level_background', 'default') # Get from parsed params, default to 'default'
        self.level_name = params.get('level_name', "Unknown Level") # Get level name, default if missing
        self.river_animation_offset = 0  # Initialize river animation offset (used by specific backgrounds)

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
        self.obstacle = None
        self.goals = []
        self.portals = []
        self.manholes = []
        self.power_up = None

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
                width = self.width * self.scale # Use scaled width/height
                height = (self.height - self.scoreboard_height) * self.scale # Use scaled playable height
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

            # Iterate through potential brick positions (similar to drawing logic)
            for y_logic in range(self.scoreboard_height, self.height, brick_h):
                row_offset = (y_logic // brick_h) % 2 * (brick_w // 2)
                for x_logic in range(0, self.width, brick_w):
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
        params['dimensions'] = {
            'width': width,
            'height': height,
            'scoreboard_height': 60 # Default scoreboard height, maybe make this a PMF property?
        }

        # --- Parse Core Level Properties ---
        params['bounce_walls'] = properties.get('bounce_walls', True)
        params['use_goals'] = properties.get('use_goals', True)
        params['can_spawn_obstacles'] = properties.get('can_spawn_obstacles', False)
        params['can_spawn_powerups'] = properties.get('can_spawn_powerups', False)

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
                obj_w = obj.get('width', 20) # Default paddle width if not specified
                obj_h = obj.get('height', 100) # Default paddle height if not specified
                rel_x = (obj_x + obj_w / 2) / width
                rel_y = (obj_y + obj_h / 2) / height

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
        """Creates game objects based on the 'objects' list in PMF data."""
        objects = pmf_data.get('objects', [])
        width = self.width # Get dimensions set earlier
        height = self.height

        # Initialize object lists
        self.manholes = []
        self.obstacle = None # Use singular for now, assuming max 1 obstacle from PMF/default
        self.goals = []
        self.portals = []
        self.power_up = None # Use singular for now, assuming max 1 powerup from PMF/default

        # Flags to track if specific types were created from the list
        obstacle_created_from_list = False
        powerup_created_from_list = False

        # --- Create Goals (Based on global flag) ---
        if self.use_goals:
            self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=True))
            self.goals.append(GoalObject(self.width, self.height, self.scoreboard_height, self.scale_rect, is_left_goal=False))

        # --- Create Objects from PMF List ---
        for obj_index, obj in enumerate(objects):
            obj_type = obj.get('type')
            # Get common geometry and properties (default to empty dict)
            obj_x = obj.get('x')
            obj_y = obj.get('y')
            obj_width = obj.get('width')
            obj_height = obj.get('height')
            properties = obj.get('properties', {}) # Ensure properties is always a dict

            # Skip if essential geometry is missing
            if obj_x is None or obj_y is None or obj_width is None or obj_height is None:
                self._log_warning(f"Skipping PMF object #{obj_index} due to missing geometry: {obj}")
                continue

            # --- Object Type Specific Creation ---

            if obj_type == 'paddle_spawn':
                # Paddle spawns are handled during parameter parsing (_parse_pmf_to_params)
                # to set self.paddle_positions. No object created here.
                pass # Already handled

            elif obj_type == 'manhole':
                # Determine if it's a top or bottom manhole based on absolute Y
                is_bottom = obj_y > (self.height / 2)
                manhole = ManHoleObject(self.width, self.height, self.scoreboard_height, self.scale_rect,
                                        obj_x, obj_y, obj_width, obj_height, is_bottom, properties) # Pass properties
                self.manholes.append(manhole)
                self._log_warning(f"Created ManHoleObject at ({obj_x},{obj_y}) with properties: {properties}")

            elif obj_type == 'obstacle':
                # Only create one obstacle for now, even if multiple are defined
                if not obstacle_created_from_list:
                    self.obstacle = ObstacleObject(
                        arena_width=self.width,
                        arena_height=self.height,
                        scoreboard_height=self.scoreboard_height,
                        scale_rect=self.scale_rect,
                        x=obj_x,
                        y=obj_y,
                        width=obj_width,
                        height=obj_height,
                        properties=properties # Pass the properties dict
                    )
                    obstacle_created_from_list = True
                    self._log_warning(f"Created ObstacleObject at ({obj_x},{obj_y}) with properties: {properties}")
                else:
                    self._log_warning(f"Ignoring additional PMF obstacle object #{obj_index} (only one supported currently): {obj}")

            elif obj_type == 'powerup_ball_duplicator': # Specific type
                # Only create one powerup for now
                if not powerup_created_from_list:
                    # Get size from properties, fallback to object width
                    powerup_size = properties.get('size', obj_width)
                    self.power_up = PowerUpBallObject(
                        arena_width=self.width,
                        arena_height=self.height,
                        scoreboard_height=self.scoreboard_height,
                        scale_rect=self.scale_rect,
                        x=obj_x,
                        y=obj_y,
                        size=powerup_size,
                        properties=properties # Pass the properties dict
                    )
                    powerup_created_from_list = True
                    self._log_warning(f"Created PowerUpBallObject at ({obj_x},{obj_y}) with size {powerup_size} and properties: {properties}")
                else:
                     self._log_warning(f"Ignoring additional PMF powerup object #{obj_index} (only one supported currently): {obj}")

            elif obj_type == 'portal':
                 portal_id = obj.get('id')
                 target_id = obj.get('target_id')

                 if portal_id is None:
                     self._log_warning(f"Skipping PMF portal object #{obj_index} due to missing 'id': {obj}")
                     continue
                 # Target ID can be None for unlinked portals initially

                 portal = PortalObject(
                     self.width, self.height, self.scoreboard_height, self.scale_rect,
                     obj_x, obj_y, obj_width, obj_height
                     # Properties are not currently used by PortalObject/Portal, but could be passed: properties=properties
                 )
                 self.portals.append(portal)
                 self._log_warning(f"Created PortalObject (id={portal_id}, target={target_id}) at ({obj_x},{obj_y}).")

                 # Store data needed for linking later
                 if not hasattr(self, '_portal_link_data'):
                      self._portal_link_data = []
                 # Store ID and instance always, target_id only if present
                 self._portal_link_data.append({'instance': portal, 'id': portal_id, 'target_id': target_id})

            else:
                self._log_warning(f"Unknown object type '{obj_type}' in PMF object #{obj_index}: {obj}")


        # --- Post-Object Creation Linking & Defaults ---

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


        # Create default obstacle if flag is set AND none were created from list
        if not obstacle_created_from_list and self.can_spawn_obstacles:
             self._log_warning("No obstacle defined in PMF 'objects', creating default obstacle because 'can_spawn_obstacles' is true.")
             # Create default obstacle (ObstacleObject handles random positioning)
             # Pass empty properties dict for default obstacle
             self.obstacle = ObstacleObject(
                 arena_width=self.width,
                 arena_height=self.height,
                 scoreboard_height=self.scoreboard_height,
                 scale_rect=self.scale_rect,
                 properties={}
             )

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

    def reset_obstacle(self):
        """Resets the obstacle based on the initial parameters."""
        # Re-create the obstacle using the stored parameters, respecting the flag
        if self.can_spawn_obstacles:
            # Always create an active obstacle when resetting,
            # regardless of the initial 'obstacle_definition' params.
            # Pass {'active': True} to ensure create_obstacle doesn't return None.
            # We could potentially merge {'active': True} with self.obstacle_params
            # if we wanted to preserve other potential definition params (like size/color).
            # For now, just ensure it's active.
            reset_params = {'active': True}
            # Optionally merge with original params if they exist and we want to keep size/color etc.
            # reset_params.update(self.obstacle_params) # Example if needed later
            self.obstacle = self.create_obstacle(reset_params)
        else:
            self.obstacle = None


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
        if self.width <= 0 or self.height <= 0: # Prevent division by zero
             self.scale_x = 1.0
             self.scale_y = 1.0
             self.scale = 1.0
             self.offset_x = 0
             self.offset_y = 0
             return

        self.scale_x = window_width / self.width
        self.scale_y = window_height / self.height
        self.scale = min(self.scale_x, self.scale_y)

        # Calculate centering offsets
        self.offset_x = (window_width - (self.width * self.scale)) / 2
        self.offset_y = (window_height - (self.height * self.scale)) / 2

        # Update scoreboard scaling if initialized
        if self.scoreboard:
            self.scoreboard.scale_y = self.scale_y # Should scoreboard scale with overall scale? Or just Y? Check Scoreboard impl.
            # Maybe self.scoreboard.scale = self.scale ?

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

        return pygame.Rect(
            (rect.x * self.scale) + self.offset_x,
            (rect.y * self.scale) + self.offset_y,
            scale_w,
            scale_h
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

        # Calculate number of boxes based on available height (excluding scoreboard)
        drawable_height = self.height - self.scoreboard_height
        drawable_height_scaled = drawable_height * self.scale
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
        # Ensure obstacle exists before adding
        obstacles = [obs for obs in [self.obstacle] + self.goals + self.portals + self.manholes if obs is not None]

        self.power_up.update(
            ball_count,
            self.width,
            self.height,
            self.scoreboard_height,
            obstacles
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

        # Log portal list content before drawing
        self._log_warning(f"Drawing portals. self.portals list: {self.portals}")

        # Draw portals first (potentially over background elements)
        for portal in self.portals:
            portal.draw(target_surface, self.colors, self.scale_rect)

        # Draw manholes
        for manhole in self.manholes:
            manhole.draw(target_surface, self.colors)

        # Draw goals (only if they exist)
        for goal in self.goals:
            goal.draw(target_surface, self.colors.get('WHITE', (255, 255, 255)))

        # Draw obstacle
        if self.obstacle: # Check if obstacle exists and is active? ObstacleObject might handle drawing based on its state
             self.obstacle.draw(target_surface, self.colors.get('WHITE', (255, 255, 255)))

        # Draw game objects (Paddles, Ball) - Draw Ball last so it's on top?
        paddles = [obj for obj in game_objects if not isinstance(obj, BallObject)]
        balls = [obj for obj in game_objects if isinstance(obj, BallObject)]

        for obj in paddles:
             if hasattr(obj, 'draw') and callable(obj.draw):
                 obj.draw(target_surface, self.colors.get('WHITE', (255, 255, 255)))
             else:
                 self._log_warning(f"Object {obj} in game_objects list does not have a draw method.")

        # Draw power-up if active (before ball?)
        # Check the 'active' attribute of the underlying PowerUpBall instance
        if self.power_up and self.power_up.power_up.active:
            self.power_up.draw(target_surface, self.colors.get('WHITE', (255, 255, 255)))

        # Draw balls last
        for obj in balls:
             if hasattr(obj, 'draw') and callable(obj.draw):
                 obj.draw(target_surface, self.colors.get('WHITE', (255, 255, 255)))
             else:
                 self._log_warning(f"Object {obj} in game_objects list does not have a draw method.")


        # --- Draw UI Elements ---

        # Draw scoreboard
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