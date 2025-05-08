"""
Artemis Editor - Property Editor Module

This module contains the widget used to display and edit the properties
(like position, size, type, custom attributes) of the currently selected
object on the level canvas, or the level's global properties if no object
is selected.
"""
import os
import pygame # Need for getting image dimensions
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit,
                              QCheckBox, QScrollArea, QFrame, QPushButton,
                              QHBoxLayout, QFileDialog, QComboBox) # Added QComboBox
from PyQt6.QtCore import Qt, QObject, pyqtSignal # Correct Qt Imports
from functools import partial
import copy # Keep existing copy import

# Placeholder for future property editor widget
print("Artemis Modules/artemis_property_editor.py loaded")

class PropertyEditorWidget(QWidget):
    """
    Widget to display and edit properties of the selected object or the level.
    """
    def __init__(self, core_logic, parent=None):
        super().__init__(parent)
        self.core_logic = core_logic
        self.current_object_id = None # Track displayed object ID
        # self.level_prop_widgets = {} # Removed - Level properties handled elsewhere
        self.object_prop_widgets = {} # Store object property widgets {key: widget or layout_widget}
        self._block_signals = False # Flag to prevent update loops
        self._sprite_browse_button = None # Reference to the browse button
        self._block_size_updates = False # Flag to prevent size update loops

        self.setMinimumWidth(220) # Slightly wider
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5) # Reduce margins
        self.setLayout(self.main_layout)

        title = QLabel("<b>Property Editor</b>") # Bold title
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title)

        # Scroll Area for properties
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame) # Remove scroll area border
        self.main_layout.addWidget(self.scroll_area)

        # Widget inside Scroll Area
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)

        # Form layout inside the scroll widget
        self.form_layout = QFormLayout(self.scroll_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0) # No margins for form
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.scroll_widget.setLayout(self.form_layout)

        self.update_display(None) # Display empty state initially
        print("PropertyEditorWidget initialized")

    def _clear_layout(self, layout):
        """Helper to remove all widgets from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    # Disconnect signals before deleting if necessary
                    try:
                        widget.disconnect()
                    except TypeError: # Catch if no signals were connected
                        pass
                    widget.deleteLater()
                else:
                    # Recursively clear nested layouts
                    child_layout = item.layout()
                    if child_layout is not None:
                        self._clear_layout(child_layout)

    # Removed display_level_properties - Handled by LevelPropertiesWidget
    def display_object_properties(self, game_object_data):
        """Populates the editor with properties of the given game object."""
        # ++ DEBUG LOG ++ Print the data received before processing
        print(f"DEBUG PropertyEditor: Displaying properties for data: {repr(game_object_data)}")
        self._clear_layout(self.form_layout)
        # self.level_prop_widgets.clear() # Removed
        self.object_prop_widgets.clear()
        self.current_object_id = game_object_data.get('id')
        self._block_signals = True # Block signals during population

        try:
            if self.current_object_id is None:
                print("Error: Game object data missing ID.")
                self.display_no_object_selected() # Fallback to empty state
                return

            self.form_layout.addRow(QLabel(f"--- <b>Object Properties</b> ---"))

            # Display common properties (ID, Type) as labels
            self.form_layout.addRow("ID:", QLabel(str(self.current_object_id)))
            self.form_layout.addRow("Type:", QLabel(str(game_object_data.get('type', 'N/A'))))

            # --- Add editable fields for relevant properties ---
            # Order properties logically (Add 'radius' for RouletteSpinner)
            # Make ID/Type selectable for copying, but read-only
            id_label = QLineEdit(str(self.current_object_id))
            id_label.setReadOnly(True)
            self.form_layout.addRow("ID:", id_label)
            type_label = QLineEdit(str(game_object_data.get('type', 'N/A')))
            type_label.setReadOnly(True)
            self.form_layout.addRow("Type:", type_label)

            # --- Add editable fields for relevant properties ---
            # Determine editable props dynamically based on type? Or use a base set + specifics.
            obj_type = game_object_data.get('type')
            editable_props = ['x', 'y', 'width', 'height', 'size', 'radius', 'speed', 'is_left', 'is_bottom', 'target_id', 'image_path', 'properties']

            for key in editable_props:
                if key in game_object_data:
                    value = game_object_data[key]
                    widget = None

                    # Create appropriate widget based on key/value type
                    if key in ['x', 'y', 'width', 'height', 'size', 'speed', 'radius']: # Numeric types (Added radius)
                        widget = QLineEdit(str(value))
                        widget.textChanged.connect(partial(self._handle_object_property_changed, key))
                    elif key in ['is_left', 'is_bottom', 'active']: # Boolean types
                        widget = QCheckBox()
                        widget.setChecked(bool(value))
                        # Use lambda for stateChanged to pass boolean value directly
                        widget.stateChanged.connect(lambda state, k=key: self._handle_object_property_changed(k, bool(state == Qt.CheckState.Checked.value)))
                    elif key == 'target_id': # Could be None or int
                        widget = QLineEdit(str(value) if value is not None else "")
                        widget.setPlaceholderText("None")
                        widget.textChanged.connect(partial(self._handle_object_property_changed, key))
                    elif key == 'properties' and isinstance(value, dict): # Nested properties (e.g., Manhole)
                        # Add a sub-section for nested properties
                        self.form_layout.addRow(QLabel(f"  <i>Sub-Properties:</i>"))
                        for sub_key, sub_value in value.items():
                             sub_widget = QLineEdit(str(sub_value))
                             # Connect nested property changes using a compound key like "properties.sub_key"
                             compound_key = f"{key}.{sub_key}"
                             sub_widget.textChanged.connect(partial(self._handle_object_property_changed, compound_key))
                             # Create a more user-friendly label for nested props
                             sub_label_text = sub_key.replace('_', ' ').title() + ":"
                             self.form_layout.addRow(f"    {sub_label_text}", sub_widget)
                             self.object_prop_widgets[compound_key] = sub_widget # Store with compound key
                        continue # Skip adding main widget for 'properties' dict itself
                    # Correct Indentation for image_path block
                    elif key == 'image_path':
                        # Special handling for image path - add sprite selector
                        layout_widget = QWidget()
                        h_layout = QHBoxLayout(layout_widget)
                        h_layout.setContentsMargins(0, 0, 0, 0)
                        h_layout.setSpacing(4)

                        sprite_combo = QComboBox()
                        sprite_combo.addItem("None")  # Allow removing sprite
                        
                        # Populate sprite list from Sprites directory
                        sprite_dir = os.path.join("Ping Assets", "Images", "Sprites")
                        if os.path.exists(sprite_dir):
                            for filename in sorted(os.listdir(sprite_dir)):
                                if any(filename.lower().endswith(ext) for ext in ['.png', '.webp', '.jpg', '.jpeg']):
                                    sprite_combo.addItem(filename)

                        # Select current value or appropriate default based on type
                        current_value = str(value) if value else None
                        default_sprite = f"default_{obj_type}.png"  # e.g., default_ball.png
                        
                        if current_value:
                            index = sprite_combo.findText(current_value)
                            if index >= 0:
                                sprite_combo.setCurrentIndex(index)
                        elif default_sprite in [sprite_combo.itemText(i) for i in range(sprite_combo.count())]:
                            index = sprite_combo.findText(default_sprite)
                            sprite_combo.setCurrentIndex(index)
                        else:
                            sprite_combo.setCurrentIndex(0)  # Set to "None"
                        
                        sprite_combo.currentTextChanged.connect(
                            lambda text, k=key: self._on_sprite_changed(k, text))
                        h_layout.addWidget(sprite_combo)

                        # Add the combined layout to the form
                        label_text = key.replace('_', ' ').title() + ":"
                        self.form_layout.addRow(label_text, layout_widget)
                        # Store the combo box widget for potential updates
                        self.object_prop_widgets['image_path_edit'] = sprite_combo
                        continue # Skip default widget adding logic below


                    # Correct indentation for the final 'if widget' block
                    # Add the widget to the layout if created
                    if widget:
                        # Create a user-friendly label
                        label_text = key.replace('_', ' ').title() + ":"
                        self.form_layout.addRow(label_text, widget)
                        self.object_prop_widgets[key] = widget

            # Add more specific property handling here

        finally:
            self._block_signals = False # Re-enable signals


    def _on_sprite_changed(self, key, text):
        """Handle sprite changes from the combo box, including dimension updates"""
        if self._block_signals:
            return
        
        value = None if text == "None" else text
        self._handle_object_property_changed(key, value)

    # Removed _handle_level_property_changed - Handled by LevelPropertiesWidget
    def _handle_object_property_changed(self, key, value):
        """Handles changes from object property widgets."""
        if self._block_signals: return
        if self.current_object_id is None: return

        print(f"Object property '{key}' UI trying to change to: {value}")
        new_value = None
        original_data = self.core_logic.get_object_by_id(self.current_object_id)
        if not original_data: return # Safety check
        current_value = original_data.get(key) # For top-level keys
        is_nested = '.' in key # Check if it's a nested property like "properties.num_segments"
        main_key = None
        sub_key = None
        current_nested_dict = None

        if is_nested:
            main_key, sub_key = key.split('.', 1)
            current_nested_dict = original_data.get(main_key, {})
            current_value = current_nested_dict.get(sub_key) # Get the specific nested value

        sender = self.sender()
        try:
            # --- Special handling for image_path direct call ---
            # When called from _browse_for_sprite, 'key' is 'image_path' and 'value' is the correct string.
            # The sender() might not be a QLineEdit in this direct call case.
            if key == 'image_path' and isinstance(value, str):
                print(f"DEBUG PropEditor: Directly handling 'image_path' assignment.")
                new_value = value # Assign the string directly
            # --- Existing widget-based handling ---
            elif isinstance(sender, QLineEdit):
                value_str = str(value) # Value is the text
                # Determine type based on current value (or guess if None)
                target_type = type(current_value) if current_value is not None else str # Default to string
                # Refine type guessing for known nested keys if current_value is None
                if current_value is None:
                    if sub_key in ['num_segments', 'spin_speed_deg_s']: target_type = int # Example
                    # Add more specific type guesses if needed

                if target_type is bool:
                    new_value = value_str.lower() in ['true', '1', 'yes']
                elif target_type is int:
                    new_value = int(value_str) if value_str else 0
                elif target_type is float:
                    new_value = float(value_str) if value_str else 0.0
                elif key == 'target_id': # Special case: can be None or int
                    new_value = int(value_str) if value_str else None
                else: # Assume string
                    new_value = value_str
            elif isinstance(sender, QCheckBox): # Value is the boolean state
                 new_value = bool(value)
            # Add handling for other widget types (QSpinBox, QComboBox, etc.)
        except (ValueError, TypeError) as e:
            print(f"Warning: Invalid input '{value}' for property '{key}'. Error: {e}")
            # Optionally revert UI or show error message
            # self._revert_widget_value(key, current_value) # TODO: Implement revert
            return

        if new_value is not None and current_value != new_value:
            # Update the object's dimensions if this is an image change
            if key == 'image_path' and new_value:
                new_dimensions = self._get_image_size(new_value)
                if new_dimensions:
                    width, height = new_dimensions
                    self.core_logic.update_object_properties(self.current_object_id, {
                        'width': width,
                        'height': height
                    })
            if is_nested:
                # Update the nested dictionary
                updated_nested_dict = copy.deepcopy(current_nested_dict) # Work on a copy
                updated_nested_dict[sub_key] = new_value
                print(f"Object ID {self.current_object_id} nested property '{key}' updating to: {new_value}")
                self.core_logic.update_object_properties(self.current_object_id, {main_key: updated_nested_dict})
            else:
                # Update top-level property
                print(f"Object ID {self.current_object_id} property '{key}' updating to: {new_value}")
                self.core_logic.update_object_properties(self.current_object_id, {key: new_value})
            # Optionally signal core saved status changed
        elif new_value is not None and current_value == new_value:
             print(f"Object ID {self.current_object_id} property '{key}' value unchanged.")
        else:
             print(f"Object ID {self.current_object_id} property '{key}' could not determine new value.")

    def _get_image_size(self, relative_path):
        """Attempts to load image and return its dimensions (width, height)."""
        if not relative_path:
             return None

        # Use same logic as level_view: Construct full path from workspace root
        base_path = "." # Use relative path from workspace root
        relative_folder = os.path.join("Ping Assets", "Images", "Sprites")
        full_path = os.path.join(base_path, relative_folder, relative_path)
        full_path = os.path.normpath(full_path)

        try:
            # Check if pygame is initialized (might be needed depending on timing)
            if not pygame.get_init():
                 print("Warning: Initializing Pygame in property editor to get image size.")
                 pygame.init()

            if pygame.get_init(): # Double check after trying init
                 image = pygame.image.load(full_path)
                 print(f"Loaded '{relative_path}' - Size: {image.get_size()}")
                 return image.get_size() # Returns (width, height)
            else:
                print("Error: Pygame failed to initialize, cannot get image size.")
                return None
        except FileNotFoundError:
            print(f"Error: Image not found for size check: {full_path}")
            return None
        except pygame.error as e:
            print(f"Error loading image '{relative_path}' for size check: {e}")
            return None

    def _browse_for_sprite(self):
        """Opens a file dialog to select a sprite image."""
        if self.current_object_id is None:
            print("Cannot browse for sprite, no object selected.")
            return

        obj_data = self.core_logic.get_object_by_id(self.current_object_id)
        if not obj_data or obj_data.get('type') != 'sprite':
            print("Cannot browse for sprite, selected object is not a sprite.")
            return

        # Directory where sprites are stored, relative to the workspace root
        sprite_dir_relative = os.path.join("Ping Assets", "Images", "Sprites")
        sprite_dir_abs = os.path.abspath(os.path.join(os.getcwd(), sprite_dir_relative))
        sprite_dir_abs = os.path.normpath(sprite_dir_abs)

        # Make sure the directory exists
        if not os.path.isdir(sprite_dir_abs):
            print(f"Error: Sprite directory does not exist: {sprite_dir_abs}")
            # TODO: Optionally show a QMessageBox to the user
            return

        print(f"Opening file dialog in: {sprite_dir_abs}") # Debugging path

        current_relative_path = obj_data.get('image_path', "")
        current_full_path = os.path.join(sprite_dir_abs, current_relative_path)

        # Open file dialog
        # Start in the sprite directory, show compatible image types
        file_path_abs, _ = QFileDialog.getOpenFileName(
            self,
            "Select Sprite Image",
            sprite_dir_abs, # Start directory
            "Image Files (*.png *.jpg *.jpeg *.bmp)" # Filter
        )

        if file_path_abs:
            file_path_abs = os.path.normpath(file_path_abs)
            # Check if the selected file is actually within the allowed sprite directory
            if not file_path_abs.startswith(sprite_dir_abs):
                print(f"Error: Selected file {file_path_abs} is not within the designated sprite directory {sprite_dir_abs}. Selection ignored.")
                # TODO: Optionally show a QMessageBox
                return

            # Calculate the path relative to the sprite directory
            relative_path = os.path.relpath(file_path_abs, sprite_dir_abs)
            relative_path = relative_path.replace('\\', '/') # Use forward slashes for consistency

            print(f"Selected relative path: {relative_path}")

            # Update the UI text field (find the correct widget)
            path_edit_widget = self.object_prop_widgets.get('image_path_edit')
            if path_edit_widget and isinstance(path_edit_widget, QLineEdit):
                self._block_signals = True # Prevent immediate handling by textChanged
                path_edit_widget.setText(relative_path)
                self._block_signals = False

            # Trigger the core logic update for image_path
            self._handle_object_property_changed('image_path', relative_path)

            # Now, attempt to get dimensions and update core logic and UI for width/height
            new_dimensions = self._get_image_size(relative_path)

            if new_dimensions:
                new_width, new_height = new_dimensions
                print(f"Successfully got dimensions for '{relative_path}': {new_width}x{new_height}")
            else:
                 print(f"Could not get dimensions for sprite '{relative_path}'. Using default 32x32.")
                 # Use default dimensions if loading failed
                 new_width, new_height = 32, 32

            # --- Always update core logic dimensions ---
            self.core_logic.update_object_properties(self.current_object_id, {'width': new_width, 'height': new_height})
            print(f"Updated core object {self.current_object_id} dimensions to {new_width}x{new_height}")

            # --- Always update UI dimensions ---
            width_widget = self.object_prop_widgets.get('width')
            height_widget = self.object_prop_widgets.get('height')
            self._block_signals = True # Prevent immediate handling
            if width_widget and isinstance(width_widget, QLineEdit):
                 width_widget.setText(str(new_width))
                 print(f"Updated UI width field to {new_width}")
            if height_widget and isinstance(height_widget, QLineEdit):
                 height_widget.setText(str(new_height))
                 print(f"Updated UI height field to {new_height}")
            self._block_signals = False

        else:
            print("Sprite selection cancelled.")



    # --- Public Method for External Updates ---
    def update_display(self, selected_obj_id):
        """
        Updates the property editor to show properties for the given object ID,
        or level properties if selected_obj_id is None.
        """
        print(f"PropertyEditor updating display for ID: {selected_obj_id}")
        if selected_obj_id is None:
            # If currently displaying an object, clear it
            if self.current_object_id is not None:
                self.display_no_object_selected()
        else:
            # If changing object or no object was selected before
            if self.current_object_id != selected_obj_id:
                obj_data = self.core_logic.get_object_by_id(selected_obj_id)
                if obj_data:
                    self.display_object_properties(obj_data)
                else:
                    print(f"Error: Could not find object data for ID {selected_obj_id}")
                    self.display_no_object_selected() # Fallback to empty state

    def display_no_object_selected(self):
        """Clears the property editor and shows a message."""
        self._clear_layout(self.form_layout)
        self.object_prop_widgets.clear()
        self.current_object_id = None
        self.form_layout.addRow(QLabel("<i>No object selected</i>"))