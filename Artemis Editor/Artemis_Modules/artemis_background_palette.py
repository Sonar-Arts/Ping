# Artemis_Modules/artemis_background_palette.py

"""
Widget for selecting the level background in the Artemis Editor.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt
import sys
import os

# Ensure the Modules directory is in the Python path
# This might be handled better by project structure or startup script in a real app
# Use a direct import assuming the script is run from the project root (c:/Users/Chace/Ping)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from Ping.Modules.Graphics.ping_graphics import get_available_backgrounds

class BackgroundPalette(QWidget):
    """
    A widget that displays available level backgrounds and allows selection.
    """
    backgroundSelected = pyqtSignal(object) # Signal emitting the selected background identifier (str or None)

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
        """Fetch available backgrounds and add them to the list, including a 'None' option."""
        self.background_list.clear()

        # Add the "None" option first
        none_item = QListWidgetItem("None")
        self.background_list.addItem(none_item)

        try:
            backgrounds = get_available_backgrounds()
            if not backgrounds:
                # Add a placeholder if no backgrounds are found (besides "None")
                placeholder_item = QListWidgetItem("No backgrounds defined")
                placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemFlag.ItemIsSelectable) # Make it non-selectable
                self.background_list.addItem(placeholder_item)
            else:
                for bg_id in sorted(backgrounds): # Sort alphabetically
                    item = QListWidgetItem(bg_id)
                    self.background_list.addItem(item)
        except Exception as e:
            print(f"Error populating background list: {e}")
            # Handle error, maybe show a message in the list
            error_item = QListWidgetItem("Error loading backgrounds")
            error_item.setFlags(error_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.background_list.addItem(error_item)


    def _on_background_selected(self, current_item, previous_item):
        """Emit signal when a background is selected, emitting None for the 'None' item."""
        if current_item and (current_item.flags() & Qt.ItemFlag.ItemIsSelectable): # Ensure item is valid and selectable
            selected_text = current_item.text()
            if selected_text == "None":
                self.backgroundSelected.emit(None) # Emit None for the "None" option
            else:
                self.backgroundSelected.emit(selected_text)
        # Handle case where selection is cleared (e.g., clicking outside)
        elif not current_item:
             # Optionally emit None when selection is cleared, or do nothing
             # self.backgroundSelected.emit(None)
             pass


    def set_selected_background(self, background_id):
        """Selects the item corresponding to the given background_id, or 'None'."""
        target_text = background_id
        if background_id is None or background_id == "":
            target_text = "None" # Select the "None" item

        items = self.background_list.findItems(target_text, Qt.MatchFlag.MatchExactly)
        if items:
            # Block signals temporarily to prevent emitting during programmatic selection
            self.background_list.blockSignals(True)
            self.background_list.setCurrentItem(items[0])
            self.background_list.blockSignals(False)
        else:
            # If the ID (or "None") is not found, clear selection
            self.background_list.blockSignals(True)
            self.background_list.clearSelection()
            self.background_list.blockSignals(False)
            if background_id is not None and background_id != "": # Avoid warning for intentionally setting None
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