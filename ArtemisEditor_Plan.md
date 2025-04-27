# Artemis Editor - Ping Level Editor Plan

## 1. Purpose

Artemis Editor is a standalone development tool designed for the Ping game project. Its primary function is to provide a visual interface for creating, viewing, and modifying Ping game levels. This allows developers to design levels outside of the main game application, streamlining the level creation workflow.

## 2. Core Features

*   **Visual Level Editing:** Allow placement, resizing, and configuration of game objects (paddles, balls, obstacles, etc.) within the level boundaries.
*   **Level Loading/Saving:** Load and save level data from/to custom `.PMF` (Ping Map File) files.
*   **Object Properties:** Edit properties of selected game objects (e.g., obstacle type, ball speed, paddle behavior).
*   **Grid & Snapping:** Optional grid and snapping features for precise object placement.
*   **Zoom & Pan:** Navigate the level view easily.
*   **Real-time Preview (Potential):** A preview pane showing how the level might look or behave (potentially using Pygame rendering within the editor).

## 3. Technical Specifications

*   **Language:** Python
*   **GUI Framework:** PyQt6
*   **Rendering/Preview (Potential):** Pygame (integrated into a PyQt6 widget if feasible, or as a separate preview mechanism).
*   **Level Format:** `.PMF` (Ping Map File) - A JSON-based format defining level objects, properties, and layout.
    *   Example structure (TBD):
        ```json
        {
          "level_name": "Tutorial 1",
          "arena_dimensions": [800, 600],
          "background": "default_background",
          "objects": [
            { "type": "obstacle_rect", "id": "obs1", "position": [100, 100], "size": [50, 50], "properties": {} },
            { "type": "ball_spawn", "id": "ball1", "position": [400, 300], "properties": {"initial_speed": 5} },
            { "type": "player_paddle_spawn", "id": "p1", "position": [50, 250], "properties": {} }
          ]
        }
        ```
*   **Platform:** Cross-platform (Windows, macOS, Linux).

## 4. Project Structure

*   **Main Executable:** `ArtemisEditor_Main.py`
*   **Core Modules:** `Artemis Modules/`
    *   `Artemis Modules/artemis_core.py` (Main application logic, window management)
    *   `Artemis Modules/artemis_file_handler.py` (Loading/Saving .PMF files)
    *   `Artemis Modules/artemis_level_view.py` (The visual editing canvas widget)
    *   `Artemis Modules/artemis_object_palette.py` (Widget to select objects to place)
    *   `Artemis Modules/artemis_property_editor.py` (Widget to edit selected object properties)
*   **Submodules:** `Artemis Modules/Artemis Submodules/`
    *   Potentially for specific object types, rendering helpers, etc.

## 5. Development Phases

1.  **Foundation:** Set up the basic PyQt6 application window, menu bar, and placeholder widgets for level view, object palette, and property editor. Define the initial `.PMF` structure.
2.  **File Handling:** Implement loading and saving of `.PMF` files.
3.  **Visual Canvas:** Develop the core level view widget. Implement basic rendering of the arena boundaries and potentially simple shapes for objects based on loaded data. Add zoom/pan functionality.
4.  **Object Placement:** Implement the object palette and allow dragging/dropping or clicking to place objects onto the canvas.
5.  **Object Selection & Manipulation:** Allow selecting objects on the canvas, moving them, and potentially resizing them.
6.  **Property Editing:** Connect the property editor to selected objects, allowing modification of their attributes. Update the canvas and underlying data accordingly.
7.  **Advanced Features:** Implement grid/snapping, more sophisticated rendering (if using Pygame), undo/redo, etc.

## 6. Dependencies

*   PyQt6
*   Pygame (for rendering/preview)
*   Python 3.x