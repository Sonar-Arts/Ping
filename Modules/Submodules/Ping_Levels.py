"""
Ping Levels Module
This module contains different arena configurations that can be used to create various types of game levels.
Each level class defines parameters that will be used by the Arena module to create different gameplay experiences.
"""

# Default arena parameters from Ping_Arena
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

# Sewer Level Implementation
class SewerLevel:
    """Sewer level configuration with goals instead of traditional scoring."""
    def __init__(self):
        # Arena dimensions - set to 1280x720 as specified
        self.width = 1280
        self.height = 720
        self.scoreboard_height = 50
        
        # Colors - dark and moody for sewer theme
        self.colors = {
            'WHITE': (255, 255, 255),
            'BLACK': (20, 20, 20),  # Darker black for atmosphere
            'DARK_BLUE': (30, 40, 50),  # Darker blue for sewer atmosphere
            'PORTAL': (0, 0, 0)  # Black for sewer portals
        }
        
        # No center line in sewer level
        self.center_line = {
            'box_width': 0,
            'box_height': 0,
            'box_spacing': 0
        }
        
        # Calculate paddle positions with precise gaps
        goal_width = 20  # Goal width from GoalObject
        self.paddle_positions = {
            'left_x': 10 + goal_width + 6,  # 10px to wall + goal width + 6px gap
            'right_x': self.width - (10 + goal_width + 6 + 20),  # Same from right (20 is paddle width)
            'y': (self.height - 120) // 2  # Vertically centered
        }
        
        # Special ball behavior for sewer level
        self.ball_behavior = {
            'bounce_walls': True  # Make ball bounce off side walls instead of scoring
        }
        
        # Goal parameters added to level configuration
        self.goals = {
            'left': True,   # Include left goal
            'right': True,  # Include right goal
        }
        
        # Portal parameters
        portal_width = 20
        portal_height = 80
        self.portals = {
            'width': portal_width,
            'height': portal_height,
            'positions': {
                'top_left': {'x': 0, 'y': self.scoreboard_height + 20},
                'bottom_left': {'x': 0, 'y': self.height - portal_height - 20},
                'top_right': {'x': self.width - portal_width, 'y': self.scoreboard_height + 20},
                'bottom_right': {'x': self.width - portal_width, 'y': self.height - portal_height - 20}
            }
        }
        
        # Power-up parameters
        power_up_size = 20
        self.power_ups = {
            'ball_duplicator': {
                'active': True,
                'size': power_up_size,
                'color': (0, 255, 0),  # Green color for visibility
                'position': {
                    'x': (self.width - power_up_size) // 2,
                    'y': (self.height - power_up_size) // 2
                }
            }
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
            'paddle_positions': self.paddle_positions,
            'goals': self.goals,
            'portals': self.portals,
            'power_ups': self.power_ups
        }

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