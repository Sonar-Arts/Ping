"""
Ping Levels Module
This module contains different arena configurations that can be used to create various types of game levels.
Each level class defines parameters that will be used by the Arena module to create different gameplay experiences.
"""

# Default arena parameters from Ping_Arena
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

class DebugLevel:
    """Debug level configuration with default arena parameters."""
    def __init__(self):
        # Arena dimensions
        self.width = DEFAULT_WIDTH
        self.height = DEFAULT_HEIGHT
        self.scoreboard_height = 50
        
        # Colors
        self.colors = {
            'WHITE': (255, 255, 255),
            'BLACK': (0, 0, 0),
            'DARK_BLUE': (47, 62, 79)  # Dark grayish blue
        }
        
        # Center line properties
        self.center_line = {
            'box_width': 5,
            'box_height': 10,
            'box_spacing': 10
        }
        
        # Paddle positions
        self.paddle_positions = {
            'left_x': 50,  # Left paddle 50px from left
            'right_x': self.width - 70,  # Right paddle 70px from right
            'y': (self.height - 120) // 2  # Vertically centered (120 is paddle height)
        }

    def get_parameters(self):
        """Return all level parameters in a dictionary format."""
        return {
            'dimensions': {
                'width': self.width,
                'height': self.height,
                'scoreboard_height': self.scoreboard_height
            },
            'colors': self.colors,
            'center_line': self.center_line,
            'paddle_positions': self.paddle_positions
        }