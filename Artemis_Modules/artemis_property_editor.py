"""
Artemis Editor - Property Editor Module

This module contains the widget used to display and edit the properties
(like position, size, type, custom attributes) of the currently selected
object on the level canvas, or the level's global properties if no object
is selected.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout,
                             QLineEdit, QCheckBox, QScrollArea, QFrame)
from PyQt6.QtCore import Qt
from functools import partial
import copy

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
        self.object_prop_widgets = {} # Store object property widgets {key: widget}
        self._block_signals = False # Flag to prevent update loops

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
            editable_props = ['x', 'y', 'width', 'height', 'size', 'radius', 'speed', 'is_left', 'is_bottom', 'target_id', 'properties']

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

                    # Add the widget to the layout if created
                    if widget:
                        # Create a user-friendly label
                        label_text = key.replace('_', ' ').title() + ":"
                        self.form_layout.addRow(label_text, widget)
                        self.object_prop_widgets[key] = widget

            # Add more specific property handling here

        finally:
            self._block_signals = False # Re-enable signals


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
            if isinstance(sender, QLineEdit):
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