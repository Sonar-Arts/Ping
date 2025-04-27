"""
Artemis Editor - Tool Bar Module

Contains the main application toolbar with general editing tools like
select, eraser, etc.
"""
from PyQt6.QtWidgets import QToolBar, QWidgetAction
from PyQt6.QtGui import QAction, QIcon # Assuming we might add icons later
from PyQt6.QtCore import pyqtSignal, QObject

print("Artemis Modules/artemis_tool_bar.py loaded")

# Tool identifiers removed - Handled by ToolPaletteWidget
# TOOL_ERASER = "eraser"
# TOOL_SELECT = "select"

class EditorToolBar(QToolBar):
    """Custom QToolBar for editor tools."""

    # toolSelected signal removed - Tools are in the palette now
    # saveActionTriggered signal removed - Save action moved to main window
    # saveActionTriggered = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setMovable(False) # Keep it docked

        # self.current_tool = None # Removed - No exclusive tools here
        # self.tool_actions = {} # Removed - No exclusive tools here

        self._create_actions()

    def _create_actions(self):
        # --- Eraser Tool Removed ---
        # --- Select Tool Removed ---

        # --- Separator Removed ---
        # --- Save Action Removed --- (Moved to main window)
        pass # Add pass to avoid indentation error on empty method


    # Removed on_save_action_triggered - Save action moved to main window

    # Removed on_tool_button_triggered - No checkable tools left
    # Removed get_current_tool - No checkable tools left
    # Removed deselect_all - No checkable tools left