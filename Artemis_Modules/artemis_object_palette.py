"""
Artemis Editor - Object Palette Module

This module contains the widget that displays available game objects
(like obstacles, balls, power-ups) that can be placed onto the level canvas.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

# --- Default Properties ---
# Derived from Ping_GameObjects.py, Ping_Obstacles.py, Ping_Paddle.py, Ping_Ball.py
DEFAULT_OBJECT_PROPERTIES = {
    "paddle_spawn_left": {"type": "paddle_spawn", "is_left": True, "width": 40, "height": 100, "speed": 300},
    "paddle_spawn_right": {"type": "paddle_spawn", "is_left": False, "width": 40, "height": 100, "speed": 300},
    "ball_spawn": {"type": "ball_spawn", "size": 20},
    "goal_left": {"type": "goal", "is_left": True, "width": 20, "height": 200},
    "goal_right": {"type": "goal", "is_left": False, "width": 20, "height": 200},
    "portal": {"type": "portal", "width": 30, "height": 80, "target_id": None}, # target_id links portals
    "manhole": {"type": "manhole", "width": 50, "height": 20, "is_bottom": True,
                "properties": {'spout_min_interval_sec': 5, 'spout_max_interval_sec': 20, 'spout_duration_sec': 1.0}},
    "bumper": {"type": "bumper", "width": 60, "height": 60, "properties": {"radius": 30}},
    "roulette_spinner": {"type": "roulette_spinner", "radius": 50, "properties": {"num_segments": 8, "spin_speed_deg_s": 180}},
    # Add other object types and their defaults here as needed
}
# --- End Default Properties ---


# Object palette widget
print("Artemis Modules/artemis_object_palette.py loaded")

class ObjectPaletteWidget(QWidget):
    """
    Widget to display and select game objects for placement.
    Provides default properties for selected objects.
    """
    # Signal emitted when an object type is selected or deselected
    # Argument is the object type string (key from DEFAULT_OBJECT_PROPERTIES), or None if deselected
    objectSelected = pyqtSignal(object, name='objectSelected') # Use object to allow None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(180) # Slightly wider for longer names
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.selected_object_type = None # Track the currently selected type key
        self.object_buttons = {} # Store buttons for potential styling/state changes

        title = QLabel("<b>Object Palette</b>") # Make title bold
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        # Define object types and their display names (using keys from DEFAULT_OBJECT_PROPERTIES)
        object_display_names = {
            "paddle_spawn_left": "Paddle Spawn (Left)",
            "paddle_spawn_right": "Paddle Spawn (Right)",
            "ball_spawn": "Ball Spawn",
            "goal_left": "Goal (Left)",
            "goal_right": "Goal (Right)",
            "portal": "Portal",
            "manhole": "Manhole",
            "bumper": "Pinball Bumper",
            "roulette_spinner": "Roulette Spinner"
        }
 
        # Create buttons for each object type defined in defaults
        for obj_type_key in DEFAULT_OBJECT_PROPERTIES.keys():
            display_name = object_display_names.get(obj_type_key, obj_type_key) # Fallback to key if no display name
            button = QPushButton(display_name)
            button.setCheckable(True) # Make buttons toggle-like
            button.setProperty("object_type_key", obj_type_key) # Store type identifier key
            button.clicked.connect(self.on_object_button_clicked)
            self.layout.addWidget(button)
            self.object_buttons[obj_type_key] = button

        print("ObjectPaletteWidget initialized")

    def on_object_button_clicked(self):
        """Handles clicks on object buttons, ensuring only one is selected."""
        sender_button = self.sender()
        clicked_type_key = sender_button.property("object_type_key")

        if sender_button.isChecked():
            self.selected_object_type = clicked_type_key
            print(f"Selected object type key: {self.selected_object_type}")
            # Uncheck all other buttons
            for obj_type_key, button in self.object_buttons.items():
                if button is not sender_button:
                    button.setChecked(False)
            # Emit signal *after* ensuring only one is checked
            self.objectSelected.emit(self.selected_object_type)
        else:
            # If the user clicks the already checked button, it becomes unchecked
            self.selected_object_type = None
            print("Object type deselected.")
            self.objectSelected.emit(None) # Emit signal with None

    def get_selected_object_type_key(self):
        """Returns the identifier key of the currently selected object type."""
        return self.selected_object_type

    def get_selected_object_defaults(self):
        """
        Returns the default properties dictionary for the currently selected object type.
        Returns None if no object type is selected.
        Returns a copy to prevent modification of the original defaults.
        """
        if self.selected_object_type:
            # Return a deep copy if properties contain mutable types like dicts
            import copy
            defaults = DEFAULT_OBJECT_PROPERTIES.get(self.selected_object_type)
            return copy.deepcopy(defaults) if defaults else None
        return None

    def deselect_all(self):
        """Deselects all buttons in the palette."""
        change_made = False
        for button in self.object_buttons.values():
            if button.isChecked():
                button.setChecked(False)
                change_made = True
        if change_made and self.selected_object_type is not None:
             self.selected_object_type = None
             print("Palette tools deselected externally.")
             # Don't emit signal here to avoid loops

    # Add methods here later for potentially populating the list dynamically, etc.