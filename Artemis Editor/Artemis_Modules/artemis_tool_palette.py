"""
Artemis Editor - Tool Palette Module

Provides a vertical palette for selecting editing tools like Select, Eraser, etc.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt

# Tool Identifiers (Consider moving to a central constants file later)
TOOL_SELECT = "select"
TOOL_ERASER = "eraser"

class ToolPaletteWidget(QWidget):
    """
    A widget containing buttons for selecting editor tools (Select, Eraser).
    Emits a signal when a tool is selected.
    """
    toolSelected = pyqtSignal(str) # Emits the tool identifier string, or None if deselected

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.current_tool = None

    def _init_ui(self):
        """Initializes the UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5) # Add some padding
        layout.setSpacing(5) # Space between buttons
        layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Keep buttons at the top

        # Use a button group for exclusive selection
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True) # Only one button can be checked at a time
        self.button_group.buttonClicked.connect(self._on_button_clicked)

        # --- Tool Buttons ---
        self.select_button = QPushButton("Select")
        self.select_button.setCheckable(True)
        self.select_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.button_group.addButton(self.select_button)
        layout.addWidget(self.select_button)

        self.eraser_button = QPushButton("Eraser")
        self.eraser_button.setCheckable(True)
        self.eraser_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.button_group.addButton(self.eraser_button)
        layout.addWidget(self.eraser_button)

        # Add more tools here as needed

        layout.addStretch() # Push buttons to the top
        self.setLayout(layout)

    def _on_button_clicked(self, button):
        """Handles button clicks within the group."""
        if button.isChecked():
            if button == self.select_button:
                self.current_tool = TOOL_SELECT
            elif button == self.eraser_button:
                self.current_tool = TOOL_ERASER
            else:
                self.current_tool = None # Should not happen with exclusive group
            print(f"Tool Palette: Selected '{self.current_tool}'")
            self.toolSelected.emit(self.current_tool)
        else:
            # If a button is unchecked (e.g., programmatically or if exclusive=False)
            # This case might not be reachable with exclusive=True if a button is always checked
            # unless deselect_all is called.
            if self.current_tool is not None:
                 print(f"Tool Palette: Deselected '{self.current_tool}'")
                 self.current_tool = None
                 self.toolSelected.emit(None)


    def deselect_all(self):
        """Deselects any currently selected tool button."""
        checked_button = self.button_group.checkedButton()
        if checked_button:
            # Temporarily disable exclusivity to allow unchecking
            self.button_group.setExclusive(False)
            checked_button.setChecked(False)
            self.button_group.setExclusive(True)
            if self.current_tool is not None:
                print(f"Tool Palette: Deselected '{self.current_tool}' via deselect_all()")
                self.current_tool = None
                # Don't emit signal here, usually called when another tool/palette gets focus

    def get_current_tool(self):
        """Returns the identifier of the currently selected tool, or None."""
        return self.current_tool

print("Artemis Modules/artemis_tool_palette.py loaded")