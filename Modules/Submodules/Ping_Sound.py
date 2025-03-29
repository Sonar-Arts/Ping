import pygame
import threading
import random

class SoundManager:
    """Handle all sound-related functionality for the game."""
    def __init__(self):
        """Initialize the sound manager."""
        # Load sound effects
        self.paddle_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/Paddle.wav")
        self.score_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/Score.wav")
        
        # Set default volume
        self.set_volume(0.5)
        
        # Define pitch ranges for different collisions
        self.PITCH_RANGES = {
            'paddle': (0.7, 1.3),    # Moderate variation for paddle hits
            'wall': (0.5, 1.5),      # Wider variation for wall hits
            'obstacle': (0.4, 1.6),  # Widest variation for obstacle hits
            'manhole': (0.6, 1.4)    # Moderate variation for manhole hits
        }
    
    def set_volume(self, volume):
        """Set volume for all sound effects."""
        self.paddle_sound.set_volume(volume)
        self.score_sound.set_volume(volume)
    
    def play_sound(self, sound_type, collision_type=None):
        """
        Play a sound effect with optional pitch variation.
        
        Args:
            sound_type: String identifying the sound ('paddle' or 'score')
            collision_type: String identifying the collision type for pitch variation
                          ('paddle', 'wall', 'obstacle', 'manhole')
        """
        def play_threaded():
            if sound_type == 'paddle':
                sound = self.paddle_sound
                if collision_type and collision_type in self.PITCH_RANGES:
                    min_pitch, max_pitch = self.PITCH_RANGES[collision_type]
                    pitch = random.uniform(min_pitch, max_pitch)
                    # Scale volume inversely with pitch to maintain perceived loudness
                    volume_scale = min(1.0, 1.0 / pitch) if pitch > 1.0 else min(1.0, pitch)
                    channel = pygame.mixer.find_channel()
                    if channel:
                        channel.play(sound)
                        channel.set_volume(sound.get_volume() * volume_scale)
                else:
                    sound.play()
            elif sound_type == 'score':
                self.score_sound.play()
        
        threading.Thread(target=play_threaded).start()
    
    def play_paddle_hit(self, collision_type='paddle'):
        """Play paddle hit sound with appropriate pitch variation."""
        self.play_sound('paddle', collision_type)
    
    def play_score(self):
        """Play score sound."""
        self.play_sound('score')