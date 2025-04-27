import json
import os
from PyQt6.QtWidgets import QMainWindow, QDockWidget
from PyQt6.QtCore import Qt, QByteArray

# Define constants for dock areas mapping (string to Qt enum and back)
# This helps make the JSON more readable
DOCK_AREA_MAP_TO_STR = {
    Qt.DockWidgetArea.LeftDockWidgetArea: "Left",
    Qt.DockWidgetArea.RightDockWidgetArea: "Right",
    Qt.DockWidgetArea.TopDockWidgetArea: "Top",
    Qt.DockWidgetArea.BottomDockWidgetArea: "Bottom",
    Qt.DockWidgetArea.NoDockWidgetArea: "Floating", # Or handle floating separately
    Qt.DockWidgetArea.AllDockWidgetAreas: "All" # Should not happen for a single dock
}
DOCK_AREA_MAP_FROM_STR = {v: k for k, v in DOCK_AREA_MAP_TO_STR.items()} # Keep for potential future use? Or remove? Let's keep for now.

def save_editor_layout(main_window: QMainWindow, file_path: str):
    """Saves the main window geometry and state using standard Qt methods."""
    settings = {}

    # 1. Save Main Window Geometry
    geometry_data = main_window.saveGeometry()
    settings['geometry'] = geometry_data.toBase64().data().decode('ascii')

    # 2. Save Dock/Toolbar State
    state_data = main_window.saveState()
    settings['state'] = state_data.toBase64().data().decode('ascii')

     # Ensure directory exists
    data_dir = os.path.dirname(file_path)
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
        except OSError as e:
            print(f"Error: Could not create data directory '{data_dir}': {e}")
            # Optionally show a message box, but might be annoying on close
            return # Abort saving

     # Save to JSON
    try:
        with open(file_path, 'w') as f:
            json.dump(settings, f, indent=4)
        # print(f"Standard editor layout saved to {file_path}") # Less verbose print
    except (IOError, TypeError) as e:
        print(f"Error saving standard layout settings: {e}")


def load_editor_layout(main_window: QMainWindow, file_path: str):
    """Loads and applies layout state using standard Qt methods. Returns True on state restore success."""
    restored_state = False
    if not os.path.exists(file_path):
        print(f"Layout settings file not found: {file_path}. Using default layout.")
        return False

    try:
        with open(file_path, 'r') as f:
            settings = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading layout settings file '{file_path}': {e}")
        return False

    # 1. Restore Main Window Geometry
    geom_data_b64 = settings.get('geometry')
    if geom_data_b64:
        geometry_data = QByteArray.fromBase64(geom_data_b64.encode('ascii'))
        if not main_window.restoreGeometry(geometry_data):
            print("Warning: Failed to restore main window geometry.")
        else:
            print("Editor geometry restored.")

    # 2. Restore Dock/Toolbar State
    state_data_b64 = settings.get('state')
    if state_data_b64:
        state_data = QByteArray.fromBase64(state_data_b64.encode('ascii'))
        if not main_window.restoreState(state_data):
            print("Warning: Failed to restore layout state (restoreState returned False).")
        else:
            print("Editor layout state restored.")
            restored_state = True # Mark state restoration as successful
    else:
        print("Warning: Layout state data not found in settings file.")


    print("Standard layout loading process complete.")
    return restored_state # Return status of restoreState