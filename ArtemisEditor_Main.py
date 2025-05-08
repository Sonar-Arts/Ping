import sys
import pygame
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QMenuBar, QStatusBar, QDockWidget, QMenu, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSize, QByteArray, QDir, QTimer # Added QByteArray, QDir, QTimer
import os
# import json # No longer needed here
# Import the actual widgets from Artemis Modules
# from Artemis_Modules.artemis_level_view import LevelViewWidget # Changed import style
import Artemis_Modules.artemis_level_view # Changed import style
from Artemis_Modules.artemis_object_palette import ObjectPaletteWidget
from Artemis_Modules.artemis_property_editor import PropertyEditorWidget
from Artemis_Modules.artemis_level_properties import LevelPropertiesWidget # Added Level Properties
from Artemis_Modules.artemis_tool_palette import ToolPaletteWidget, TOOL_SELECT, TOOL_ERASER # Import new palette
from Artemis_Modules.artemis_background_palette import BackgroundPalette # Import Background Palette
from Artemis_Modules.artemis_sprite_palette import SpritePalette # Import Sprite Palette
# Import core and file handler
from Artemis_Modules.artemis_core import ArtemisCore # Import the class
from Artemis_Modules.artemis_file_handler import save_pmf, load_pmf
# Import the new layout manager
from Artemis_Modules.artemis_layout_manager import save_editor_layout, load_editor_layout
# Import QAction for the toolbar save button
from PyQt6.QtGui import QAction # EditorToolBar import removed
# from Artemis_Modules.artemis_tool_bar import EditorToolBar # No longer needed

# Import the new function from ping_graphics
try:
    # Assuming ping_graphics is in Modules directory relative to project root
    from Modules.ping_graphics import get_background_theme_colors
except ImportError as e:
    print(f"Warning: Could not import get_background_theme_colors from Modules.ping_graphics: {e}")
    get_background_theme_colors = None # Define as None if import fails

class ArtemisEditorWindow(QMainWindow):
    """Main window for the Artemis Level Editor."""
    active_tool_source = None # 'toolbar', 'palette', 'tool_palette', or None

    def __init__(self):
        super().__init__()

        # --- Core Logic ---
        # Instantiate the core logic AFTER the main window exists
        self.core_logic = ArtemisCore(self)

        # --- Pygame Initialization (Basic) ---
        # No longer needed here, core logic doesn't directly depend on it yet
        # self.current_level_path = None # Managed by core_logic
        # self.level_modified = False # Managed by core_logic

        try:
            pygame.init()
            print("Pygame initialized successfully.")
        except pygame.error as e:
            print(f"Error initializing Pygame: {e}")

        # --- Window Properties ---
        self.setWindowTitle("Artemis Editor - New Level") # Start with new level title
        self.setMinimumSize(QSize(800, 600))
        self.resize(1200, 800)

        # --- Central Widget ---
        # Pass core_logic to LevelViewWidget
        # Changed instantiation to use module namespace
        self.level_view = Artemis_Modules.artemis_level_view.LevelViewWidget(self.core_logic, self)
        self.setCentralWidget(self.level_view)

        # --- Define Settings Path Early ---
        self.layout_settings_path = os.path.join("Artemis_Data", "editor_layout.json") # Changed extension
 
        # --- Layout Save Timer (Removed) ---
 
        # --- Create UI Elements (Order Matters!) ---
        self._create_docks() # Pass core_logic here
        self._create_menu_bar()
        self._create_tool_bar()

        # --- Status Bar ---
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")

        # --- Connect Signals (After all UI elements exist) ---
        self._connect_signals()

        # Layout settings are now loaded within _create_docks using the new manager

        # Show window and then initialize UI state
        self.show() # Ensure window is shown before initial update
        self.update_ui_for_level_state() # Call directly after showing

        # Apply stylesheet to normalize menu bar item appearance and hover
        self.menuBar().setStyleSheet("""
            QMenuBar::item {
                /* Normalize appearance for all items (menus and actions) */
                padding: 4px 8px;      /* Adjust padding as needed */
                background: transparent; /* Ensure no default background */
                border: none;          /* Remove any default border */
            }
            QMenuBar::item:selected { /* Hover state */
                background-color: #555; /* Consistent hover background (adjust color) */
            }
            QMenuBar::item:pressed {  /* Optional: Style when pressed */
                background-color: #444; /* Consistent pressed background (adjust color) */
            }
        """)

        print("Artemis Editor window initialized.")
 
    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        # File Menu
        file_menu = menu_bar.addMenu("&File")

        # --- Save Action (Moved to Menu Bar) ---
        # TODO: Add an actual icon for save? (Might look odd on menu bar)
        save_action = QAction("Save", self)
        save_action.setToolTip("Save the current level (Ctrl+S)")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.file_save)
        menu_bar.addAction(save_action) # Add directly to the menu bar

        # --- New Level Submenu (Inside File Menu) ---
        new_menu = file_menu.addMenu("&New")
        # Define standard 16:9 sizes
        sizes = {
            "Small (800x450)": (800, 450),
            "Medium (1280x720)": (1280, 720),
            "Large (1920x1080)": (1920, 1080),
        }
        for text, (width, height) in sizes.items():
            action = QAction(text, self)
            # Use lambda to capture width and height for the slot
            action.triggered.connect(lambda checked=False, w=width, h=height: self.file_new_level(w, h))
            new_menu.addAction(action)
        # --- End New Level Submenu ---

        file_menu.addAction("&Open...", self.file_open)
        file_menu.addAction("&Save", self.file_save)
        file_menu.addAction("Save As...", self.file_save_as)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Edit Menu (Placeholder)
        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction("Undo", self.edit_undo)
        edit_menu.addAction("Redo", self.edit_redo)

        # Window Menu (Formerly View)
        window_menu = menu_bar.addMenu("&Window")
        window_menu.addAction(self.object_palette_dock.toggleViewAction())
        window_menu.addAction(self.property_editor_dock.toggleViewAction())
        window_menu.addAction(self.level_properties_dock.toggleViewAction())
        window_menu.addAction(self.tool_palette_dock.toggleViewAction()) # Add toggle for tool palette
        window_menu.addAction(self.background_palette_dock.toggleViewAction()) # Add toggle for background palette
        window_menu.addAction(self.sprite_palette_dock.toggleViewAction()) # Add toggle for sprite palette
        window_menu.addSeparator()

        # --- Grid Snapping Toggle ---
        self.grid_snap_action = QAction("Snap to Grid", self)
        self.grid_snap_action.setCheckable(True)
        # Initial state should ideally come from core_logic or settings later
        self.grid_snap_action.setChecked(self.level_view.grid_enabled)
        self.grid_snap_action.triggered.connect(self.toggle_grid_snapping)
        window_menu.addAction(self.grid_snap_action)

        # Help Menu (Placeholder)
        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction("About", self.help_about)

    def _create_docks(self):
        # Object Palette Dock
        self.object_palette_dock = QDockWidget("Object Palette", self)
        self.object_palette_dock.setObjectName("ObjectPaletteDock") # Set object name
        self.object_palette_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        # Pass core_logic (optional for now, but good practice)
        self.object_palette = ObjectPaletteWidget(self.object_palette_dock) # core_logic could be passed here
        self.object_palette_dock.setWidget(self.object_palette)
        # Add dock widget - necessary for restoreState to find it
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.object_palette_dock)
        # Connect signals (Removed - Using save on close for now)

        # Property Editor Dock
        self.property_editor_dock = QDockWidget("Property Editor", self)
        self.property_editor_dock.setObjectName("PropertyEditorDock") # Set object name
        self.property_editor_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        # Pass core_logic to PropertyEditorWidget
        self.property_editor = PropertyEditorWidget(self.core_logic, self.property_editor_dock)
        self.property_editor_dock.setWidget(self.property_editor)
        # Add dock widget
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.property_editor_dock)
        # Connect signals (Removed)

        # Level Properties Dock
        self.level_properties_dock = QDockWidget("Level Properties", self)
        self.level_properties_dock.setObjectName("LevelPropertiesDock") # Set object name
        self.level_properties_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        # Pass core_logic to LevelPropertiesWidget
        self.level_properties_widget = LevelPropertiesWidget(self.core_logic, self.level_properties_dock)
        self.level_properties_dock.setWidget(self.level_properties_widget)
        # Add dock widget
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.level_properties_dock)
        # Connect signals (Removed)
        # Optionally, tabify with another dock (Handled conditionally below)

        # Tool Palette Dock (New)
        self.tool_palette_dock = QDockWidget("Tools", self)
        self.tool_palette_dock.setObjectName("ToolPaletteDock") # Set object name
        self.tool_palette_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.tool_palette = ToolPaletteWidget(self.tool_palette_dock)
        self.tool_palette_dock.setWidget(self.tool_palette)
        # Add dock widget
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tool_palette_dock)
        # Connect signals (Removed)

        # Background Palette Dock (New)
        self.background_palette_dock = QDockWidget("Backgrounds", self)
        self.background_palette_dock.setObjectName("BackgroundPaletteDock")
        self.background_palette_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.background_palette = BackgroundPalette(self.background_palette_dock)
        self.background_palette_dock.setWidget(self.background_palette)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.background_palette_dock)
 
        # Sprite Palette Dock (New)
        self.sprite_palette_dock = QDockWidget("Sprites", self)
        self.sprite_palette_dock.setObjectName("SpritePaletteDock")
        self.sprite_palette_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.sprite_palette = SpritePalette(self.sprite_palette_dock)
        self.sprite_palette_dock.setWidget(self.sprite_palette)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sprite_palette_dock)

        # --- Load Layout using Standard Qt Methods via Manager ---
        # Call this AFTER creating AND adding all docks.
        restored_state_successfully = load_editor_layout(self, self.layout_settings_path)
 
        # --- Add Docks to Window (Done above) ---
 
        # --- Tabify (Apply default if restoreState failed or no file) ---
        if not restored_state_successfully:
            print("Setting default tab layout as restore failed or no state existed.")
            # Ensure docks are added before trying to tabify
            # (Already done above, but good to remember the dependency)
            try:
                # Tabify Tools, Objects, Backgrounds, and Level Properties together on the left
                # Tabify Tools, Objects, Backgrounds, Sprites, and Level Properties together on the left
                self.tabifyDockWidget(self.tool_palette_dock, self.object_palette_dock)
                self.tabifyDockWidget(self.object_palette_dock, self.background_palette_dock)
                self.tabifyDockWidget(self.background_palette_dock, self.sprite_palette_dock) # Add sprite palette to tabs
                self.tabifyDockWidget(self.sprite_palette_dock, self.level_properties_dock) # Tab properties after sprites
                # Optionally raise one to the front
                self.tool_palette_dock.raise_()
            except Exception as e:
                print(f"Error applying default tabbing: {e}") # Catch potential errors if docks aren't ready

    def _create_tool_bar(self):
        """Creates the main application toolbar with essential actions."""
        # Get the main window's toolbar or create one
        # Create the toolbar, but it might be empty now or have other actions later
        self.tool_bar = self.addToolBar("Main Actions")
        self.tool_bar.setObjectName("MainToolBar") # Set object name
        self.tool_bar.setMovable(False)
 
        # --- Save Action Removed from Toolbar ---

        # Add other global actions like Open, New here if desired (e.g., icons for Open/New)

    def _connect_signals(self):
        """Connects signals from UI elements to slots."""
        # Palettes/Toolbar -> Main Window (Tool Selection)
        self.object_palette.objectSelected.connect(self.on_palette_tool_selected)
        self.tool_palette.toolSelected.connect(self.on_tool_palette_selected) # Connect new palette
        # self.tool_bar.toolSelected.connect(self.on_toolbar_tool_selected) # Will be removed/modified later

        # Toolbar -> Main Window (Actions) - Save action connected directly above
        # self.tool_bar.saveActionTriggered.connect(self.file_save) # Removed

        # Level View -> Property Editor (Object Selection)
        # Assuming LevelViewWidget emits objectSelected(obj_id or None)
        self.level_view.objectSelected.connect(self.property_editor.update_display)

        # Level View -> Main Window (Modification Status)
        # Assuming LevelViewWidget emits levelModified(bool)
        self.level_view.levelModified.connect(self.on_level_modified)

        # Background Palette -> Core Logic (Background Selection)
        self.background_palette.backgroundSelected.connect(self.on_background_selected)

        # Core Logic -> UI Updates (Level Load/Properties Change)
        self.core_logic.levelLoaded.connect(self.update_ui_for_level_state) # Already updates most things
        self.core_logic.levelLoaded.connect(self.update_background_palette_selection) # Specific update for background palette
        self.core_logic.levelPropertiesChanged.connect(self.update_background_palette_selection) # Update palette if props change
 
        # Sprite Palette -> Main Window (Sprite Selection - Placeholder Handler)
        self.sprite_palette.spriteSelected.connect(self.on_sprite_selected)
 
    # --- Tool Selection Slots ---
    def on_palette_tool_selected(self, selected_type_key):
        """Handles selection from the Object Palette."""
        if selected_type_key:
            print(f"Object Palette tool selected: {selected_type_key}")
            self.active_tool_source = 'palette'
            # self.tool_bar.deselect_all() # Toolbar no longer has exclusive tools
            self.tool_palette.deselect_all() # Deselect tool palette
            # Get default props to potentially display info
            defaults = self.object_palette.get_selected_object_defaults()
            display_name = defaults.get('type', selected_type_key).replace('_', ' ').title()
            self.statusBar().showMessage(f"Selected Tool: Place {display_name}")
            # Inform Level View about the tool change
            self.level_view.set_active_tool(selected_type_key)
        else:
            # Only clear if the deselection came from the object palette itself
            if self.active_tool_source == 'palette':
                self.active_tool_source = None
                self.statusBar().showMessage("Ready (Select Tool)")
                self.level_view.set_active_tool(None) # Clear tool in level view

    def on_toolbar_tool_selected(self, selected_tool_id):
        """Handles selection from the main Tool Bar."""
        if selected_tool_id:
            # This handler will be removed or repurposed as the toolbar changes
            print(f"Toolbar action/tool selected: {selected_tool_id}")
            # If it's a tool like Select/Eraser (it shouldn't be anymore)
            if selected_tool_id in [TOOL_SELECT, TOOL_ERASER]:
                self.active_tool_source = 'toolbar' # Keep track temporarily
                self.object_palette.deselect_all()
                self.tool_palette.deselect_all() # Deselect tool palette too
                display_name = selected_tool_id.replace('_', ' ').title()
                self.statusBar().showMessage(f"Selected Tool: {display_name}")
                # Inform Level View about the tool change
                self.level_view.set_active_tool(selected_tool_id)
            else:
                # Handle other toolbar actions if any (like Save, which is handled separately)
                pass
        # else: # Handle deselection if toolbar buttons were checkable
            # if self.active_tool_source == 'toolbar':
            #     self.active_tool_source = None
            #     self.statusBar().showMessage("Ready (Select Tool)")
            #     self.level_view.set_active_tool(None) # Clear tool in level view
        pass # Keep method signature for now


    def on_tool_palette_selected(self, selected_tool_id):
        """Handles selection from the new Tool Palette."""
        if selected_tool_id:
            print(f"Tool Palette tool selected: {selected_tool_id}")
            self.active_tool_source = 'tool_palette'
            self.object_palette.deselect_all() # Deselect object palette
            # self.tool_bar.deselect_all() # Toolbar no longer has exclusive tools
            display_name = selected_tool_id.replace('_', ' ').title()
            self.statusBar().showMessage(f"Selected Tool: {display_name}")
            # Inform Level View about the tool change
            self.level_view.set_active_tool(selected_tool_id)
        else:
            # Only clear if the deselection came from the tool palette itself
            if self.active_tool_source == 'tool_palette':
                self.active_tool_source = None
                self.statusBar().showMessage("Ready (Select Tool)")
                self.level_view.set_active_tool(None) # Clear tool in level view


    # --- Background Selection Slot ---
    def on_background_selected(self, background_id):
        """Handles selection from the Background Palette."""
        print(f"Background selected: {background_id}")

        # Get the corresponding color theme
        theme_colors = {} # Default to empty if not found or import failed
        if get_background_theme_colors:
            theme_colors = get_background_theme_colors(background_id)
            if not theme_colors and background_id is not None:
                 print(f"Warning: No color theme found for background '{background_id}'. Using empty theme.")
        else:
            print("Warning: get_background_theme_colors function not available.")

        # Update core logic with both background ID and its colors
        # Use update_level_properties to set multiple values at once
        properties_to_update = {
            'level_background': background_id,
            'colors': theme_colors # Update the 'colors' dictionary
        }
        self.core_logic.update_level_properties(properties_to_update)

        # Status bar update (optional)
        self.statusBar().showMessage(f"Level background set to: {background_id}", 3000)


    # --- Sprite Selection Slot ---
    def on_sprite_selected(self, sprite_filename):
        """Handles selection from the Sprite Palette."""
        # TODO: This needs more sophisticated handling.
        # When an object is selected, the PropertyEditor should be informed
        # about the available sprites and the currently selected sprite for that object.
        # This might involve:
        # 1. Storing the selected sprite filename temporarily here.
        # 2. When an object is selected (level_view.objectSelected signal),
        #    pass this sprite filename (if any) to the property editor.
        # 3. The property editor needs to be updated to show a sprite selection widget
        #    (e.g., a dropdown) populated by the SpritePalette's contents,
        #    and set the current value based on the object's data or this selection.
        # 4. When the sprite is changed *in the property editor*, update the core_logic.
        print(f"Sprite selected in palette: {sprite_filename}")
        # For now, just show in status bar
        if sprite_filename:
            self.statusBar().showMessage(f"Sprite selected: {sprite_filename}", 3000)
        else:
            self.statusBar().showMessage("Sprite selection cleared", 3000)
        # We don't set an active tool here, sprite selection modifies object properties.

    # --- Menu Action Methods ---
    def toggle_grid_snapping(self, checked):
        """Toggles grid snapping in the level view."""
        self.level_view.toggle_grid(checked)
        print(f"Grid snapping toggled via menu: {checked}")

    def _confirm_unsaved_changes(self):
        """Checks for unsaved changes and asks the user if they want to save."""
        if self.core_logic.unsaved_changes:
            reply = QMessageBox.question(self, 'Unsaved Changes',
                                         "You have unsaved changes. Do you want to save before proceeding?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                                         QMessageBox.StandardButton.Cancel) # Default to Cancel

            if reply == QMessageBox.StandardButton.Save:
                return self._perform_save() # Returns True on success, False otherwise
            elif reply == QMessageBox.StandardButton.Discard:
                return True # User chose to discard changes
            else: # Cancel
                return False # User cancelled the operation
        return True # No unsaved changes, proceed

    # Modify file_new_level to accept width and height again
    def file_new_level(self, width=800, height=450): # Add default size
        """Creates a new blank level using core logic with specified dimensions."""
        print(f"Action: File -> New ({width}x{height})")
        if not self._confirm_unsaved_changes():
            return # User cancelled

        # Use core logic to reset state, passing dimensions
        self.core_logic.new_level(width, height) # Pass dimensions

        # Update UI elements
        self.update_ui_for_level_state()
        self.statusBar().showMessage(f"Created new {width}x{height} level", 3000)


    def file_open(self):
        """Opens a level file using core logic."""
        print("Action: File -> Open")
        if not self._confirm_unsaved_changes():
            return # User cancelled

        levels_dir = os.path.join(os.getcwd(), "Ping_Levels")
        if not os.path.exists(levels_dir):
            levels_dir = os.getcwd()

        filepath, selected_filter = QFileDialog.getOpenFileName(
            self, "Open Level File", levels_dir,
            "Ping Map Files (*.pmf);;All Files (*)"
        )

        if filepath:
            print(f"Attempting to load file: {filepath}")
            loaded_data = load_pmf(filepath)

            if loaded_data:
                try:
                    # Core logic handles loading and validation
                    self.core_logic.load_level(loaded_data, filepath)
                    # Update UI
                    self.update_ui_for_level_state()
                    self.statusBar().showMessage(f"Loaded level: {os.path.basename(filepath)}", 3000)

                except (KeyError, ValueError, TypeError) as e:
                    print(f"Error processing loaded level data: {e}")
                    QMessageBox.critical(self, "Load Error", f"Invalid level file format:\n{e}")
                    self.statusBar().showMessage(f"Error: Invalid level file format", 5000)
                    # Reset to a clean state after error
                    self.core_logic.new_level()
                    self.update_ui_for_level_state()
            else:
                self.statusBar().showMessage("Failed to load level file.", 5000)
                QMessageBox.warning(self, "Load Failed", "Could not load the selected level file.")
        else:
            print("File open cancelled by user.")
            self.statusBar().showMessage("Open cancelled.", 2000)


    def _perform_save(self, save_as=False):
        """Handles the core logic for saving using core logic."""
        target_path = self.core_logic.current_level_path
        perform_save_as = save_as or not target_path

        if perform_save_as:
            levels_dir = os.path.join(os.getcwd(), "Ping_Levels")
            if not os.path.exists(levels_dir):
                try:
                    os.makedirs(levels_dir)
                except OSError as e:
                    print(f"Warning: Could not create default save directory '{levels_dir}': {e}")
                    levels_dir = os.getcwd()

            suggested_name = os.path.basename(target_path) if target_path else "untitled.pmf"
            initial_path = os.path.join(levels_dir, suggested_name)

            filepath, selected_filter = QFileDialog.getSaveFileName(
                self, "Save Level As", initial_path,
                "Ping Map Files (*.pmf);;All Files (*)"
            )

            if not filepath:
                print("Save As cancelled by user.")
                self.statusBar().showMessage("Save cancelled.", 2000)
                return False # Indicate cancellation/failure

            if not filepath.lower().endswith(".pmf"):
                filepath += ".pmf"
            target_path = filepath # Use the new path selected by the user
            print(f"Performing Save As to: {target_path}")
        else:
            print(f"Saving to existing file: {target_path}")

        # Get data from core logic
        level_data = self.core_logic.get_level_data_for_saving()

        if level_data:
            if save_pmf(target_path, level_data):
                # Update core logic state
                self.core_logic.current_level_path = target_path
                self.core_logic.unsaved_changes = False
                # Update UI
                self.update_window_title()
                self.statusBar().showMessage(f"Level saved to {os.path.basename(target_path)}", 3000)
                return True
            else:
                QMessageBox.critical(self, "Save Error", f"Could not save level to:\n{target_path}")
                self.statusBar().showMessage("Error saving level!", 5000)
                return False
        else:
             QMessageBox.critical(self, "Save Error", "Could not retrieve level data for saving.")
             self.statusBar().showMessage("Error retrieving level data for saving.", 5000)
             return False

    def file_save(self):
        """Slot for the File -> Save action and Toolbar Save button."""
        print("Action: File -> Save")
        self._perform_save(save_as=False)

    def file_save_as(self):
        """Slot for the File -> Save As action."""
        print("Action: File -> Save As")
        self._perform_save(save_as=True)

    def edit_undo(self):
        self.statusBar().showMessage("Action: Edit -> Undo (Not Implemented)", 2000)
        print("Action: Edit -> Undo")
        # TODO: self.core_logic.undo() -> update UI

    def edit_redo(self):
        self.statusBar().showMessage("Action: Edit -> Redo (Not Implemented)", 2000)
        print("Action: Edit -> Redo")
        # TODO: self.core_logic.redo() -> update UI

    def help_about(self):
        self.statusBar().showMessage("Action: Help -> About (Not Implemented)", 2000)
        print("Action: Help -> About")
        QMessageBox.about(self, "About Artemis Editor",
                          "Artemis Level Editor for Ping\nVersion 0.1 (Alpha)")

    # --- UI Update / Helper Methods ---
    def update_window_title(self):
        """Updates the main window title based on current file and modified state."""
        base_title = "Artemis Editor"
        file_part = "New Level"
        if self.core_logic.current_level_path:
            file_part = os.path.basename(self.core_logic.current_level_path)
        modified_indicator = "*" if self.core_logic.unsaved_changes else ""
        self.setWindowTitle(f"{base_title} - {file_part}{modified_indicator}")

    def on_level_modified(self, modified_status):
        """Slot called when the level's modified status changes (e.g., from LevelView)."""
        # This might be redundant if core_logic.unsaved_changes is the source of truth
        # but useful if LevelView detects changes directly (like object move)
        if self.core_logic.unsaved_changes != modified_status:
             print(f"Level modified status changed externally to: {modified_status}")
             self.core_logic.unsaved_changes = modified_status
             self.update_window_title()

    def update_ui_for_level_state(self):
        """Updates various UI elements based on the current core_logic state."""
        self.update_window_title()
        # Update level view (assuming it has a method like 'refresh_display')
        self.level_view.refresh_display()
        # Update property editor (shows selected object or nothing)
        self.property_editor.update_display(None)
        # Update level properties display
        self.level_properties_widget.update_display() # Added update call
        # Deselect tools in all palettes/toolbars
        self.object_palette.deselect_all()
        self.tool_palette.deselect_all()
        # self.tool_bar.deselect_all() # Toolbar no longer has exclusive tools
        self.active_tool_source = None
        # Reverted diagnostic change: Call via instance
        self.level_view.set_active_tool(None)
        # Update background palette selection
        self.update_background_palette_selection()
        # Clear sprite palette selection visually (doesn't affect object data)
        self.sprite_palette.set_selected_sprite(None)


    def update_background_palette_selection(self):
        """Updates the background palette to reflect the current level's background."""
        current_bg = self.core_logic.level_properties.get('level_background')
        self.background_palette.set_selected_background(current_bg)
        # print(f"Background palette selection updated to: {current_bg}") # Optional debug print


    def get_selected_tool(self):
        """Gets the identifier of the currently active tool, if any."""
        if self.active_tool_source == 'palette':
            # Use the key now stored in the object palette
            return self.object_palette.get_selected_object_type_key()
        elif self.active_tool_source == 'tool_palette':
            # Get from the new tool palette
            return self.tool_palette.get_current_tool()
        # elif self.active_tool_source == 'toolbar': # Toolbar no longer primary source for these tools
            # return self.tool_bar.get_current_tool()
        else:
            return None

    # --- Layout Save/Load Methods Removed (Using Manager) ---

    # --- Event Handlers ---
    def closeEvent(self, event):
        """Overrides the default close event to check for unsaved changes."""
        print("Close event triggered...")
        if self._confirm_unsaved_changes():
            # --- Save Layout using Standard Qt Methods via Manager ---
            print("Saving final editor layout before closing...")
            save_editor_layout(self, self.layout_settings_path) # Call the manager function
            # --- End Save Layout ---

            print("Shutting down Pygame...")
            pygame.quit()
            print("Artemis Editor closing.")
            event.accept() # Accept the close event
        else:
            print("Close cancelled by user.")
            event.ignore() # Ignore the close event, keep window open

# --- Main Application Execution ---
if __name__ == "__main__":
    print("Starting Artemis Editor...")
    app = QApplication(sys.argv)
    # Apply some basic styling (optional)
    # app.setStyle("Fusion")
    window = ArtemisEditorWindow()
    # window.show() # Moved into __init__
    print("Entering main event loop...")
    exit_code = app.exec()
    print(f"Exiting with code {exit_code}")
    sys.exit(exit_code)