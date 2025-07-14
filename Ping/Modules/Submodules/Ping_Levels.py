"""
Ping Levels Module
This module contains different arena configurations that can be used to create various types of game levels.
Each level class defines parameters that will be used by the Arena module to create different gameplay experiences.
"""

# Default arena parameters from Ping_Arena
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

import random
import pygame  # Import pygame for color definitions if not already present
from .Ping_Sound import SoundManager
