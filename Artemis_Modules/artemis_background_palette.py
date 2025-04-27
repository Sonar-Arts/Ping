# Artemis_Modules/artemis_background_palette.py

"""
Widget for selecting the level background in the Artemis Editor.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
import sys
import os

# Ensure the Modules directory is in the Python path
# This might be handled better by project structure or startup script in a real app
# Use a direct import assuming the script is run from the project root (c:/Users/Chace/Ping)
from Modules.ping_graphics import get_available_backgrounds

class BackgroundPalette(QWidget):
    """
    A widget that displays available level backgrounds and allows selection.
    """
    backgroundSelected = pyqtSignal(str) # Signal emitting the selected background identifier

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backgrounds")
        self._init_ui()
        self._populate_backgrounds()

    def _init_ui(self):
        """Initialize the UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2) # Reduced margins
        layout.setSpacing(3) # Reduced spacing

        # Optional: Add a label if desired
        # title_label = QLabel("Backgrounds")
        # title_label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(title_label)

        self.background_list = QListWidget()
        self.background_list.setSpacing(2) # Spacing between items
        self.background_list.currentItemChanged.connect(self._on_background_selected)
        layout.addWidget(self.background_list)

        self.setLayout(layout)

    def _populate_backgrounds(self):
        """Fetch available backgrounds and add them to the list."""
        self.background_list.clear()
        try:
            backgrounds = get_available_backgrounds()
            if not backgrounds:
                # Add a placeholder if no backgrounds are found
                placeholder_item = QListWidgetItem("No backgrounds defined")
                placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemFlag.ItemIsSelectable) # Make it non-selectable
                self.background_list.addItem(placeholder_item)
            else:
                for bg_id in backgrounds:
                    item = QListWidgetItem(bg_id)
                    self.background_list.addItem(item)
        except Exception as e:
            print(f"Error populating background list: {e}")
            # Handle error, maybe show a message in the list
            error_item = QListWidgetItem("Error loading backgrounds")
            error_item.setFlags(error_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.background_list.addItem(error_item)


    def _on_background_selected(self, current_item, previous_item):
        """Emit signal when a background is selected."""
        if current_item and (current_item.flags() & Qt.ItemFlag.ItemIsSelectable): # Ensure item is valid and selectable
            self.backgroundSelected.emit(current_item.text())

    def set_selected_background(self, background_id):
        """Selects the item corresponding to the given background_id."""
        if not background_id:
            self.background_list.clearSelection()
            return

        items = self.background_list.findItems(background_id, Qt.MatchFlag.MatchExactly)
        if items:
            self.background_list.setCurrentItem(items[0])
        else:
            # If the ID is not found (e.g., level loaded with old/invalid ID), clear selection
            self.background_list.clearSelection()
            print(f"Warning: Background ID '{background_id}' not found in palette.")

# Example usage (for testing)
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys

    # Mock ping_graphics if running standalone and it wasn't imported
    if 'get_available_backgrounds' not in globals() or get_available_backgrounds() == []:
        def get_available_backgrounds():
            print("Using mock backgrounds for testing.")
            return ["sewer", "mock_bg_1", "mock_bg_2"]

    app = QApplication(sys.argv)
    palette = BackgroundPalette()

    def handle_selection(bg_id):
        print(f"Background selected: {bg_id}")

    palette.backgroundSelected.connect(handle_selection)
    palette.show()
    palette.set_selected_background("mock_bg_1") # Test setting selection
    sys.exit(app.exec_())