# Artemis_Modules/artemis_sprite_palette.py

"""
Widget for selecting sprites in the Artemis Editor.
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import pyqtSignal, Qt

# Define the path to the sprites directory relative to the project root
SPRITE_DIR = "Ping Assets/Images/Sprites"
ALLOWED_EXTENSIONS = {".png", ".webp", ".jpg", ".jpeg", ".bmp", ".gif"} # Add more if needed

class SpritePalette(QWidget):
    """
    A widget that displays available sprites from the designated folder and allows selection.
    """
    spriteSelected = pyqtSignal(str) # Signal emitting the selected sprite filename (or None)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sprites")
        self._init_ui()
        self._populate_sprites()

    def _init_ui(self):
        """Initialize the UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)

        # Optional: Add a label if desired
        # title_label = QLabel("Sprites")
        # title_label.setAlignment(Qt.AlignCenter)
        # layout.addWidget(title_label)

        self.sprite_list = QListWidget()
        self.sprite_list.setSpacing(2)
        self.sprite_list.currentItemChanged.connect(self._on_sprite_selected)
        layout.addWidget(self.sprite_list)

        self.setLayout(layout)

    def _populate_sprites(self):
        """Fetch available sprites from the SPRITE_DIR and add them to the list."""
        self.sprite_list.clear()

        # Add a "None" option
        none_item = QListWidgetItem("None")
        self.sprite_list.addItem(none_item)

        if not os.path.isdir(SPRITE_DIR):
            print(f"Error: Sprite directory not found at '{SPRITE_DIR}'")
            error_item = QListWidgetItem("Sprite directory missing")
            error_item.setFlags(error_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.sprite_list.addItem(error_item)
            return

        try:
            found_sprites = False
            for filename in sorted(os.listdir(SPRITE_DIR)):
                # Check if the file has an allowed image extension
                if os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS:
                    item = QListWidgetItem(filename)
                    self.sprite_list.addItem(item)
                    found_sprites = True

            if not found_sprites:
                placeholder_item = QListWidgetItem("No sprites found")
                placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.sprite_list.addItem(placeholder_item)

        except Exception as e:
            print(f"Error populating sprite list: {e}")
            error_item = QListWidgetItem("Error loading sprites")
            error_item.setFlags(error_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.sprite_list.addItem(error_item)

    def _on_sprite_selected(self, current_item, previous_item):
        """Emit signal when a sprite is selected."""
        if current_item and (current_item.flags() & Qt.ItemFlag.ItemIsSelectable):
            selected_text = current_item.text()
            if selected_text == "None":
                 self.spriteSelected.emit(None) # Emit None for the "None" option
            else:
                 # Emit the filename, the full path can be constructed later if needed
                 self.spriteSelected.emit(selected_text)
        elif not current_item:
             # Optionally emit None when selection is cleared
             # self.spriteSelected.emit(None)
             pass

    def set_selected_sprite(self, sprite_filename):
        """Selects the item corresponding to the given sprite filename, or 'None'."""
        target_text = sprite_filename
        if sprite_filename is None or sprite_filename == "":
            target_text = "None"

        items = self.sprite_list.findItems(target_text, Qt.MatchFlag.MatchExactly)
        if items:
            self.sprite_list.blockSignals(True)
            self.sprite_list.setCurrentItem(items[0])
            self.sprite_list.blockSignals(False)
        else:
            self.sprite_list.blockSignals(True)
            self.sprite_list.clearSelection()
            self.sprite_list.blockSignals(False)
            if sprite_filename is not None and sprite_filename != "":
                 print(f"Warning: Sprite filename '{sprite_filename}' not found in palette.")


# Example usage (for testing)
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    palette = SpritePalette()

    def handle_selection(sprite_file):
        print(f"Sprite selected: {sprite_file}")
        if sprite_file:
            full_path = os.path.join(SPRITE_DIR, sprite_file)
            print(f"Full path (example): {full_path}")

    palette.spriteSelected.connect(handle_selection)
    palette.show()
    # Test setting selection (replace with an actual sprite name if available)
    # palette.set_selected_sprite("Protag Paddle.webp")
    sys.exit(app.exec_())