"""
Artemis Editor - Core Module

This module contains central application logic, coordination between
different parts of the editor, and manages the application state,
including the currently loaded level data and properties.
"""
import copy # For deep copying properties
from PyQt6.QtCore import QObject, pyqtSignal # Import QObject and pyqtSignal

# Placeholder for future core classes and functions
print("Artemis Modules/artemis_core.py loaded")

class ArtemisCore(QObject): # Inherit from QObject
    """
    Main application core logic class. Manages level data, properties,
    and coordinates interactions between editor components.
    """
    # --- Signals ---
    levelLoaded = pyqtSignal() # Emitted after new_level or load_level completes
    levelPropertiesChanged = pyqtSignal() # Emitted when level properties (like dimensions) change
    levelModifiedStateChanged = pyqtSignal(bool) # Emitted when unsaved_changes state flips
    layoutRestored = pyqtSignal() # Emitted by main window AFTER restoreState succeeds
    objectSelectionChanged = pyqtSignal(object) # Emitted by LevelView, maybe relayed? (TBD)
    objectUpdated = pyqtSignal(int) # Emitted when an object's properties are updated (passes obj_id)
    # TODO: Signals for objectAdded, objectDeleted

    def __init__(self, main_window):
        super().__init__() # Initialize QObject base class
        self.main_window = main_window
        self.level_objects = [] # List to store placed objects {id, type, properties}
        self.level_properties = self._get_default_level_properties()
        self.current_level_path = None # Track the path of the loaded level
        self._unsaved_changes = False # Use property setter now
        print("ArtemisCore initialized")

    # --- Unsaved Changes Property ---
    @property
    def unsaved_changes(self):
        return self._unsaved_changes

    @unsaved_changes.setter
    def unsaved_changes(self, value):
        if self._unsaved_changes != value:
            self._unsaved_changes = value
            self.levelModifiedStateChanged.emit(value) # Emit signal on change

    def _get_default_level_properties(self):
        """Returns a dictionary with the default level properties."""
        return {
            "name": "Untitled Level", # Added Name
            "width": 800,             # Added Width
            "height": 450,            # Added Height
            "background_color": (0, 0, 0), # Added Background Color (R,G,B tuple)
            "bounce_walls": False, # Ball scores on side walls instead of bouncing
            "use_goals": False,    # Use side walls for scoring instead of Goal objects
            "can_spawn_obstacles": False, # Dynamic obstacle spawning (runtime flag)
            "can_spawn_powerups": True,  # Dynamic power-up spawning (runtime flag)
            "can_spawn_ghosts": False, # Dynamic ghost spawning (runtime flag)
            "level_music": "",         # Filename of the music track (e.g., "PMainMusicTemp.wav")
            "level_background": None,  # Identifier for the background (e.g., "sewer")
            "has_lighting": False,     # Boolean to indicate if the level uses the lighting system
            "lighting_level": 75,      # Integer 0-100 for lighting intensity
            # Add other level-wide properties here
        }

    def load_level(self, level_data, file_path):
        """Loads level data, including objects and properties."""
        # Clear existing data
        self.level_objects = level_data.get("objects", [])
        # Load properties, falling back to defaults if missing
        loaded_props = level_data.get("properties", {})
        self.level_properties = self._get_default_level_properties() # Start with defaults
        self.level_properties.update(loaded_props) # Override with loaded values

        # --- Compatibility: Handle old 'dimensions' key ---
        if 'dimensions' in loaded_props and isinstance(loaded_props['dimensions'], (list, tuple)) and len(loaded_props['dimensions']) == 2:
            if 'width' not in loaded_props: # Prioritize explicit width/height
                self.level_properties['width'] = loaded_props['dimensions'][0]
            if 'height' not in loaded_props:
                self.level_properties['height'] = loaded_props['dimensions'][1]
            # We don't need to explicitly remove 'dimensions' as it won't be saved again
            print("Migrated 'dimensions' property to 'width' and 'height'.")
        # --- End Compatibility ---

        self.current_level_path = file_path
        self.unsaved_changes = False # Reset flag (setter emits signal)
        print(f"Level loaded from {file_path}")
        self.levelLoaded.emit() # Emit signal AFTER data is loaded

    def new_level(self, width=800, height=450): # Add width and height parameters
        """Resets the editor state for a new, empty level with specified dimensions."""
        self.level_objects = [] # Clear existing objects first
        self.level_properties = self._get_default_level_properties()
        # Set the dimensions and name directly in the properties
        self.level_properties['width'] = width
        self.level_properties['height'] = height
        self.level_properties['name'] = "Untitled Level" # Reset name for new level
        self.current_level_path = None
        self.unsaved_changes = False # New level starts unmodified

        # --- Add Default Paddle Spawns ---
        # Define necessary properties directly here to avoid import cycles
        paddle_w, paddle_h = 30, 100 # Use wider default width
        paddle_speed = 300
        offset_x = 50

        # Left Paddle Spawn
        left_x = offset_x
        left_y = (height - paddle_h) // 2
        left_paddle = {
            "id": 1, # Assign fixed IDs for default paddles
            "type": "paddle_spawn_left", # Use specific type
            "is_left": True,
            "x": left_x,
            "y": left_y,
            "width": paddle_w,
            "height": paddle_h,
            "speed": paddle_speed
            # Add other relevant default properties if needed
        }
        self.level_objects.append(left_paddle)

        # Right Paddle Spawn
        right_x = width - offset_x - paddle_w
        right_y = (height - paddle_h) // 2
        right_paddle = {
            "id": 2, # Assign fixed IDs for default paddles
            "type": "paddle_spawn_right", # Use specific type
            "is_left": False,
            "x": right_x,
            "y": right_y,
            "width": paddle_w,
            "height": paddle_h,
            "speed": paddle_speed
            # Add other relevant default properties if needed
        }
        self.level_objects.append(right_paddle)
        # --- End Default Paddle Spawns ---

        print(f"New level created ({width}x{height}) with default paddles.")
        self.levelLoaded.emit() # Emit signal AFTER data is set

    def get_level_data_for_saving(self):
        """Returns the current level data structured for saving."""
        return {
            "properties": copy.deepcopy(self.level_properties),
            "objects": copy.deepcopy(self.level_objects)
            # Add metadata like editor version later if needed
        }
    def update_level_properties(self, new_props):
        """Updates multiple level properties from a dictionary."""
        changed = False
        dimensions_changed = False
        valid_keys = self._get_default_level_properties().keys() # Get valid keys

        for key, value in new_props.items():
            if key not in valid_keys:
                print(f"Warning: Attempted to update unknown level property '{key}'. Skipping.")
                continue

            # Add specific validation if needed (e.g., for width/height)
            if key in ['width', 'height'] and (not isinstance(value, int) or value <= 0):
                 print(f"Warning: Invalid value '{value}' for level property '{key}'. Must be positive integer. Skipping.")
                 continue
            if key == 'background_color':
                 if not isinstance(value, (tuple, list)) or len(value) != 3 or not all(isinstance(v, int) and 0 <= v <= 255 for v in value):
                     print(f"Warning: Invalid value '{value}' for level property '{key}'. Must be RGB tuple/list of ints 0-255. Skipping.")
                     continue
                 # Convert list to tuple if necessary
                 value = tuple(value)
            elif key == 'lighting_level' and (not isinstance(value, int) or not (0 <= value <= 100)):
                print(f"Warning: Invalid value '{value}' for level property '{key}'. Must be integer 0-100. Skipping.")
                continue

            if self.level_properties.get(key) != value:
                self.level_properties[key] = value
                changed = True
                if key in ['width', 'height']:
                    dimensions_changed = True
                print(f"Level property '{key}' updated to: {value}")

        if changed:
            self.unsaved_changes = True # Setter emits signal
            # Emit general property change signal
            self.levelPropertiesChanged.emit()
            if dimensions_changed:
                 print("Level dimensions specifically changed.")
                 # LevelView is connected to levelPropertiesChanged, it will handle resize

        return changed # Indicate if any change was actually made

    def get_level_properties(self):
        """Returns a deep copy of the current level properties."""
        return copy.deepcopy(self.level_properties)

    def update_level_property(self, key, value):
        """Updates a specific level property. Returns True if value changed, False otherwise."""
        # This method might be redundant now with update_level_properties
        # If kept, it should also emit levelPropertiesChanged
        if key in self.level_properties:
            if self.level_properties[key] != value:
                self.level_properties[key] = value
                self.unsaved_changes = True # Setter emits signal
                print(f"Level property '{key}' updated to: {value}")
                self.levelPropertiesChanged.emit() # Emit signal
                return True # Value was changed
            else:
                return False # Value was the same, no change made
        else:
            print(f"Warning: Attempted to update unknown level property '{key}'")
            return False # Key not found

    def add_object(self, obj_data):
        """Adds a new object to the level."""
        # Assign a unique ID, ensuring it doesn't clash with default paddles (1, 2)
        # Start checking from ID 3 upwards
        existing_ids = {obj.get('id', 0) for obj in self.level_objects}
        new_id = 3
        while new_id in existing_ids:
            new_id += 1

        obj_data['id'] = new_id
        self.level_objects.append(obj_data)
        self.unsaved_changes = True # Setter emits signal
        print(f"Added object: {obj_data}")
        # TODO: Add objectAdded signal? For now, LevelView redraws on timer

    def update_object_properties(self, obj_id, new_properties):
        """Updates the properties of a specific object."""
        # ++ DEBUG LOGGING ++
        print(f"DEBUG Core: Attempting update for ID {obj_id} with properties: {new_properties}")
        updated = False # Track if any change was actually made

        for obj in self.level_objects:
            if obj.get('id') == obj_id:
                original_obj_repr = repr(obj) # Capture state before modification
                # Only update keys present in new_properties
                for key, value in new_properties.items():
                     if key != 'id': # Don't overwrite ID
                        # Compare before potentially updating
                        if obj.get(key) != value:
                            print(f"DEBUG Core: Changing '{key}' from '{obj.get(key)}' to '{value}' for ID {obj_id}")
                            obj[key] = value
                            updated = True # Mark that a change happened

                if updated:
                    self.unsaved_changes = True # Setter emits signal
                    print(f"DEBUG Core: Update applied for ID {obj_id}. New props: {new_properties}. Final object state snippet: {repr(obj)[:100]}...")
                    self.objectUpdated.emit(obj_id) # Emit signal that this object changed
                    return True # Return True as update happened
                else:
                    print(f"DEBUG Core: No changes applied for ID {obj_id} with new_properties {new_properties}. Object remained: {original_obj_repr}")
                    return False # Indicate no changes were made

        print(f"Warning Core: Could not find object with ID {obj_id} to update.")
        return False

    def delete_object(self, obj_id):
        """Deletes an object from the level."""
        initial_count = len(self.level_objects)
        self.level_objects = [obj for obj in self.level_objects if obj.get('id') != obj_id]
        if len(self.level_objects) < initial_count:
            self.unsaved_changes = True # Setter emits signal
            print(f"Deleted object ID {obj_id}")
            # TODO: Add objectDeleted signal?
            return True
        print(f"Warning: Could not find object with ID {obj_id} to delete.")
        return False

    def get_object_by_id(self, obj_id):
        """Retrieves a specific object by its ID."""
        for obj in self.level_objects:
            if obj.get('id') == obj_id:
                return copy.deepcopy(obj) # Return a copy
        return None

    # Add methods here later for coordinating editor functions like selection, undo/redo etc.