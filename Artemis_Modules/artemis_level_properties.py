import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout,
                             QLineEdit, QSpinBox, QCheckBox, QComboBox) # Added QCheckBox, QComboBox
from PyQt6.QtCore import Qt
from functools import partial # Added partial
# Import SoundManager to access music definitions
from Modules.Submodules.Ping_Sound import SoundManager

class LevelPropertiesWidget(QWidget):
    """Widget to display and edit level-specific properties."""

    def __init__(self, core_logic, parent=None):
        super().__init__(parent)
        self.core_logic = core_logic
        self.level_prop_widgets = {} # Store widgets for easy access
        self._block_signals = False # Flag to prevent update loops (similar to property editor)
        self._init_ui()
        self.update_display() # Initial population

    def _init_ui(self):
        """Initializes the UI elements."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Keep elements at the top

        form_layout = QFormLayout()

        # --- Level Properties Fields ---
        self.level_name_edit = QLineEdit()
        self.level_width_spin = QSpinBox()
        self.level_height_spin = QSpinBox()
        self.background_color_edit = QLineEdit() # Simple for now
        self.bounce_walls_cb = QCheckBox()
        self.use_goals_cb = QCheckBox()
        self.spawn_obstacles_cb = QCheckBox()
        self.spawn_powerups_cb = QCheckBox()
        self.level_music_combo = QComboBox() # Added Music Combo Box

        # Configure spin boxes (adjust ranges as needed)
        self.level_width_spin.setRange(100, 10000)
        self.level_width_spin.setSuffix(" px")
        self.level_height_spin.setRange(100, 10000)
        self.level_height_spin.setSuffix(" px")

        form_layout.addRow("Level Name:", self.level_name_edit)
        form_layout.addRow("Width:", self.level_width_spin)
        form_layout.addRow("Height:", self.level_height_spin)
        form_layout.addRow("Background Color:", self.background_color_edit)
        form_layout.addRow("Bounce Walls:", self.bounce_walls_cb)
        form_layout.addRow("Use Goals:", self.use_goals_cb)
        form_layout.addRow("Runtime Spawn Obstacles:", self.spawn_obstacles_cb)
        form_layout.addRow("Runtime Spawn Powerups:", self.spawn_powerups_cb)
        form_layout.addRow("Level Music:", self.level_music_combo) # Added Music Row

        # Populate Music Dropdown
        self._populate_music_dropdown()

        # Store widgets for easier access in update_display and handlers
        self.level_prop_widgets["name"] = self.level_name_edit
        self.level_prop_widgets["width"] = self.level_width_spin
        self.level_prop_widgets["height"] = self.level_height_spin
        self.level_prop_widgets["background_color"] = self.background_color_edit
        self.level_prop_widgets["bounce_walls"] = self.bounce_walls_cb
        self.level_prop_widgets["use_goals"] = self.use_goals_cb
        self.level_prop_widgets["can_spawn_obstacles"] = self.spawn_obstacles_cb
        self.level_prop_widgets["can_spawn_powerups"] = self.spawn_powerups_cb
        self.level_prop_widgets["level_music"] = self.level_music_combo # Added Music Widget

        layout.addLayout(form_layout)
        self.setLayout(layout)

        # --- Connect Signals ---
        # Connect signals to update core_logic when values change
        self.level_name_edit.editingFinished.connect(self._on_lineedit_finished) # Changed to _on_lineedit_finished
        self.level_width_spin.valueChanged.connect(self._on_lineedit_finished) # Changed to _on_lineedit_finished
        self.level_height_spin.valueChanged.connect(self._on_lineedit_finished) # Changed to _on_lineedit_finished
        self.background_color_edit.editingFinished.connect(self._on_lineedit_finished) # Use specific handler
        # Connect checkboxes to a dedicated handler
        self.bounce_walls_cb.stateChanged.connect(partial(self._on_checkbox_changed, "bounce_walls"))
        self.use_goals_cb.stateChanged.connect(partial(self._on_checkbox_changed, "use_goals"))
        self.spawn_obstacles_cb.stateChanged.connect(partial(self._on_checkbox_changed, "can_spawn_obstacles"))
        self.spawn_powerups_cb.stateChanged.connect(partial(self._on_checkbox_changed, "can_spawn_powerups"))
        self.level_music_combo.currentTextChanged.connect(self._on_music_changed) # Connect music combo


    def _populate_music_dropdown(self):
        """Gets logical music names from SoundManager and populates the dropdown."""
        self.level_music_combo.clear()
        self.level_music_combo.addItem("(None)", "") # Add option for no music

        try:
            # Instantiate SoundManager temporarily to get the music mapping
            # Note: This assumes SoundManager can be instantiated without side effects here.
            # A better long-term solution might involve accessing this mapping via core_logic.
            temp_sound_manager = SoundManager()
            music_mapping = temp_sound_manager._sound_paths.get('music', {})
            logical_names = sorted(list(music_mapping.keys())) # Get and sort logical names

            for name in logical_names:
                # Add item with logical name as both display text and user data
                self.level_music_combo.addItem(name, name)

            print(f"Populated music dropdown with {len(logical_names)} logical names.")

        except Exception as e:
            print(f"Error getting music definitions from SoundManager: {e}")
            # Optionally add a placeholder if loading fails
            self.level_music_combo.addItem("Error loading music", "")


    def update_display(self):
        """Populates the fields with current level data from core_logic."""
        level_data = self.core_logic.get_level_properties() # Need to implement this in core

        # Temporarily disable signals to prevent loops during population
        self._set_signals_blocked(True)

        self.level_name_edit.setText(level_data.get('name', 'Untitled Level'))
        self.level_width_spin.setValue(level_data.get('width', 800))
        self.level_height_spin.setValue(level_data.get('height', 450))
        # Assuming background color is stored as a string like "R,G,B"
        bg_color_tuple = level_data.get('background_color', (0, 0, 0))
        self.background_color_edit.setText(f"{bg_color_tuple[0]},{bg_color_tuple[1]},{bg_color_tuple[2]}")
        self.bounce_walls_cb.setChecked(level_data.get("bounce_walls", False))
        self.use_goals_cb.setChecked(level_data.get("use_goals", False))
        self.spawn_obstacles_cb.setChecked(level_data.get("can_spawn_obstacles", False))
        self.spawn_powerups_cb.setChecked(level_data.get("can_spawn_powerups", True)) # Default True
        # Update Music Dropdown
        current_music = level_data.get("level_music", "")
        music_index = self.level_music_combo.findData(current_music) # Find by user data
        if music_index != -1:
            self.level_music_combo.setCurrentIndex(music_index)
        else:
            # If current music file not found (or is ""), select "(None)"
            none_index = self.level_music_combo.findData("")
            self.level_music_combo.setCurrentIndex(none_index if none_index != -1 else 0) # Default to first item if "(None)" somehow missing

        # Re-enable signals
        self._set_signals_blocked(False)

        print("Level Properties Widget updated.")


    def _set_signals_blocked(self, blocked):
        """Helper to block/unblock signals for all input widgets."""
        self.level_name_edit.blockSignals(blocked)
        self.level_width_spin.blockSignals(blocked)
        self.level_height_spin.blockSignals(blocked)
        self.background_color_edit.blockSignals(blocked)
        self.bounce_walls_cb.blockSignals(blocked)
        self.use_goals_cb.blockSignals(blocked)
        self.spawn_obstacles_cb.blockSignals(blocked)
        self.spawn_powerups_cb.blockSignals(blocked)
        self.level_music_combo.blockSignals(blocked) # Block music combo


    def _on_lineedit_finished(self):
        """Called when a QLineEdit or QSpinBox finishes editing."""
        if self._block_signals: return
        sender = self.sender()
        print(f"Level property (text/spin) changed by user via widget: {sender}")
        # Find which property corresponds to the sender (more robust than current)
        prop_key = None
        if sender == self.level_name_edit:
            prop_key = 'name'
        elif sender == self.level_width_spin:
            prop_key = 'width'
        elif sender == self.level_height_spin:
            prop_key = 'height'
        elif sender == self.background_color_edit:
            prop_key = 'background_color'

        if prop_key:
            self._update_core_property(prop_key)
        else:
             print(f"Warning: Could not determine property key for sender: {sender}")


    def _on_checkbox_changed(self, key, state):
        """Called when a QCheckBox state changes."""
        if self._block_signals: return
        print(f"Level property (checkbox) '{key}' changed by user.")
        new_value = bool(state == Qt.CheckState.Checked.value)
        self._update_core_property(key, new_value)


    def _on_music_changed(self, text):
        """Called when the music selection changes."""
        if self._block_signals: return
        print(f"Level property (combo) 'level_music' changed by user to: {text}")
        # Get the data associated with the selected item (which is the filename or "")
        selected_filename = self.level_music_combo.currentData()
        self._update_core_property("level_music", selected_filename)


    def _update_core_property(self, key, value=None):
         """Updates a specific property in the core logic."""
         if self._block_signals: return # Double check

         current_props = self.core_logic.get_level_properties()
         current_value = current_props.get(key)
         new_value = None

         # Determine the new value based on the widget type associated with the key
         widget = self.level_prop_widgets.get(key)
         if isinstance(widget, QLineEdit):
             if key == 'background_color':
                 try:
                     r, g, b = map(int, widget.text().split(','))
                     new_value = (r, g, b)
                 except ValueError:
                     print(f"Warning: Invalid background color format for key '{key}'. Not updating.")
                     widget.setText(f"{current_value[0]},{current_value[1]},{current_value[2]}") # Revert UI
                     return
             else: # Assume name
                 new_value = widget.text()
         elif isinstance(widget, QSpinBox):
             new_value = widget.value()
         elif isinstance(widget, QCheckBox):
             # For checkboxes, the value is passed directly from the handler
             new_value = value
         elif isinstance(widget, QComboBox):
              # For combo boxes, the value is passed directly from the handler
              # (We store the filename/"" in the user data)
              new_value = value
         else:
             print(f"Warning: Unknown widget type for key '{key}'. Cannot determine value.")
             return

         if new_value is not None and current_value != new_value:
             print(f"Updating core logic for '{key}': {current_value} -> {new_value}")
             if self.core_logic.update_level_property(key, new_value): # Use single property update
                 print(f"Core logic updated successfully for '{key}'.")
                 # self.core_logic.notify_level_changed() # Example
             else:
                 print(f"Core logic failed to update '{key}'.")
                 self.update_display() # Revert UI to core's state
         elif new_value is not None:
              print(f"Value for '{key}' unchanged ({new_value}). No update needed.")


    # Removed the old _on_property_changed method as it's unused and incorrect