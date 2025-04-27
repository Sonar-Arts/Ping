# Artemis Editor Documentation

This document provides an overview of the Artemis Editor's components and their functionalities. The editor is built using PyQt for the user interface and integrates Pygame for the level visualization and interaction.

## Core Components (`Artemis_Modules/`)

### `ArtemisCore` (`artemis_core.py`)
- **Purpose:** Acts as the central brain of the editor. It manages the current level's data, including objects, properties, and overall state.
- **Key Functions:**
    - Loading and initializing new or existing levels (`load_level`, `new_level`).
    - Managing level properties (`update_level_properties`, `update_level_property`).
    - Handling game objects: adding, updating, deleting, and retrieving (`add_object`, `update_object_properties`, `delete_object`, `get_object_by_id`).
    - Tracking unsaved changes.
    - Providing level data for saving (`get_level_data_for_saving`).

### `LevelViewWidget` (`artemis_level_view.py`)
- **Purpose:** Provides the main visual canvas where the game level is displayed and edited. It uses an embedded Pygame surface for rendering.
- **Key Functions:**
    - Rendering the level, including objects and background.
    - Handling user interactions like mouse clicks and movements for object selection, placement, and manipulation (`mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`).
    - Implementing editing tools (select, place, etc.) based on the active tool selected in the `ToolPaletteWidget`.
    - Displaying and managing the editing grid (`toggle_grid`, `snap_to_grid`, `draw_grid`).
    - Refreshing the display when changes occur (`refresh_display`, `update_pygame`).

### `artemis_file_handler.py`
- **Purpose:** Contains utility functions specifically for handling the loading and saving of level data to/from `.pmf` (Ping Map File) format.
- **Key Functions:**
    - `load_pmf(filepath)`: Reads a `.pmf` file and parses the level data.
    - `save_pmf(filepath, level_data)`: Writes the current level data into a `.pmf` file.

### `artemis_layout_manager.py`
- **Purpose:** Manages the saving and loading of the editor's window layout (dock widget positions, sizes, toolbar locations). This allows users to customize and restore their preferred workspace arrangement.
- **Key Functions:**
    - `save_editor_layout(main_window, file_path)`: Saves the current layout state to a file (e.g., `editor_layout.json`).
    - `load_editor_layout(main_window, file_path)`: Restores the editor layout from a saved file.

## UI Widgets (`Artemis_Modules/`)

### `EditorToolBar` (`artemis_tool_bar.py`)
- **Purpose:** The main toolbar, typically located at the top of the editor window. Provides quick access to common actions.
- **Key Functions:**
    - Hosts actions like "New Level", "Load Level", "Save Level", "Toggle Grid". (Specific actions are defined in `ArtemisEditor_Main.py`).

### `ToolPaletteWidget` (`artemis_tool_palette.py`)
- **Purpose:** A dockable widget containing buttons for selecting the active editing tool (e.g., Select/Move, Place Object, Delete Object).
- **Key Functions:**
    - Displays tool buttons.
    - Emits a signal (`toolSelected`) when a tool button is clicked, indicating the newly active tool to other components (like `LevelViewWidget`).
    - Manages the visual state of tool buttons (selected/deselected).

### `ObjectPaletteWidget` (`artemis_object_palette.py`)
- **Purpose:** A dockable widget that displays available game object types (e.g., Wall, Paddle, Ball Spawn) that can be placed onto the level.
- **Key Functions:**
    - Displays buttons for each available object type.
    - Emits a signal (`objectSelected`) when an object type is chosen, usually activating the "Place Object" tool.
    - Provides default properties for the selected object type (`get_selected_object_defaults`).

### `PropertyEditorWidget` (`artemis_property_editor.py`)
- **Purpose:** A dockable widget used to display and edit the properties of the currently selected game object or the level itself.
- **Key Functions:**
    - Dynamically generates input fields (line edits, checkboxes, dropdowns) based on the properties of the selected object (`display_object_properties`).
    - Updates the `ArtemisCore` when a property value is changed by the user (`_handle_object_property_changed`).
    - Clears the display or shows a placeholder message when no object is selected (`display_no_object_selected`).
    - Receives signals when the selection changes to update its display (`update_display`).

### `LevelPropertiesWidget` (`artemis_level_properties.py`)
- **Purpose:** A dockable widget specifically for viewing and editing properties related to the entire level, such as dimensions, background music, and other global settings.
- **Key Functions:**
    - Displays fields for level name, width, height, music selection, etc. (`_init_ui`, `update_display`).
    - Populates dropdowns (e.g., for music files found in the assets folder) (`_populate_music_dropdown`).
    - Updates the `ArtemisCore` when level properties are modified (`_on_lineedit_finished`, `_on_checkbox_changed`, `_on_music_changed`, `_update_core_property`).

### `BackgroundPalette` (`artemis_background_palette.py`)
- **Purpose:** A dockable widget allowing the user to select a background image or theme for the level.
- **Key Functions:**
    - Displays available background options (likely loaded from an assets directory).
    - Emits a signal when a background is selected (`backgroundSelected`).
    - Updates the level properties in `ArtemisCore` when a background is chosen.

## Main Application (`ArtemisEditor_Main.py`)

- **Purpose:** This is the entry point of the application. It initializes the main window, creates instances of all the core components and UI widgets, connects their signals and slots, arranges the initial layout, and starts the Qt application event loop.
- **Key Functions:**
    - Creates the `QMainWindow`.
    - Instantiates `ArtemisCore`.
    - Instantiates all palette, view, editor, and toolbar widgets, passing the `ArtemisCore` instance where needed.
    - Connects signals (e.g., `toolSelected`, `objectSelected`, `propertyChanged`) to the appropriate slots in other components to orchestrate the editor's behavior.
    - Sets up the main menu bar and toolbar actions (New, Open, Save, etc.) and connects them to `ArtemisCore` or `artemis_file_handler` functions.
    - Loads the saved editor layout using `artemis_layout_manager`.
    - Shows the main window and runs the application.