import pygame
import threading
import random

class SoundManager:
    """Handle all sound-related functionality for the game."""
    # Class variable to track if main music has started
    _main_music_started = False
    def __init__(self):
        """Initialize the sound manager."""
        # Load sound effects
        self.paddle_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/Paddle.wav")
        self.score_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/Score.wav")
        self.wahahoo_sound = pygame.mixer.Sound("Ping_Sounds/Ping_FX/wahahoo.wav")
        self.intro_music = pygame.mixer.Sound("Ping Assets/Music/PIntroMusicTemp.wav")
        self.main_music = pygame.mixer.Sound("Ping Assets/Music/PMainMusicTemp.wav")
        self.sewer_music = pygame.mixer.Sound("Ping Assets/Music/PSewerZoneTemp.wav")
        
        # Store base volumes for sounds (0-1 range)
        self.base_volumes = {
            'paddle': 0.5,
            'score': 0.5,
            'wahahoo': 0.5,
            'intro_music': 0.7,
            'main_music': 0.7,
            'sewer_music': 0.7
        }
        
        # Keep track of the music channel for looping
        self.music_channel = None
        
        # Store master volume (0-1 range)
        self.master_volume = 1.0
        
        # Set initial volumes
        self._apply_volumes()
        
        # Define pitch ranges for different collisions
        self.PITCH_RANGES = {
            'paddle': (0.7, 1.3),    # Moderate variation for paddle hits
            'wall': (0.5, 1.5),      # Wider variation for wall hits
            'obstacle': (0.4, 1.6),  # Widest variation for obstacle hits
            'manhole': (0.6, 1.4)    # Moderate variation for manhole hits
        }
    
    def set_volume(self, volume, sound_type=None):
        """
        Set volume for specified or all sound effects.
        
        Args:
            volume: Volume value between 0 and 1
            sound_type: Optional - specific sound to adjust ('paddle' or 'score')
        """
        if sound_type:
            self.base_volumes[sound_type] = volume
        else:
            # If no specific sound, update base volumes for all sounds
            for sound in self.base_volumes:
                self.base_volumes[sound] = volume
        self._apply_volumes()
    
    def set_master_volume(self, volume_percent):
        """
        Set master volume from percentage (0-100).
        
        Args:
            volume_percent: Volume percentage between 0 and 100
        """
        self.master_volume = volume_percent / 100.0
        self._apply_volumes()
    
    def _apply_volumes(self):
        """Apply master volume scaling to all sound effects."""
        self.paddle_sound.set_volume(self.base_volumes['paddle'] * self.master_volume)
        self.score_sound.set_volume(self.base_volumes['score'] * self.master_volume)
        self.wahahoo_sound.set_volume(self.base_volumes['wahahoo'] * self.master_volume)
        self.intro_music.set_volume(self.base_volumes['intro_music'] * self.master_volume)
        self.main_music.set_volume(self.base_volumes['main_music'] * self.master_volume)
        self.sewer_music.set_volume(self.base_volumes['sewer_music'] * self.master_volume)
    
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
    
    def play_wahahoo(self, pitch_speed=1.0):
        """Play wahahoo sound with optional pitch variation."""
        thread = threading.Thread(target=lambda: self.wahahoo_sound.play(maxtime=int(self.wahahoo_sound.get_length() * 1000 / pitch_speed)))
        thread.start()
    
    def play_intro_music(self):
        """Play the intro music."""
        self.intro_music.play()
    
    def play_main_music(self):
        """Stop current music channel and start playing the main menu music."""
        if self.music_channel:
            self.music_channel.stop() # Stop the tracked channel
        self.music_channel = pygame.mixer.find_channel(True) # Force find a new channel
        if self.music_channel:
            self.music_channel.play(self.main_music, loops=-1)
    
    def play_sewer_music(self):
        """Stop current music channel and start playing the sewer level music."""
        if self.music_channel:
            self.music_channel.stop() # Stop the tracked channel
        self.music_channel = pygame.mixer.find_channel(True) # Force find a new channel
        if self.music_channel:
            self.music_channel.play(self.sewer_music, loops=-1)

    def stop_all_music(self):
        """Stop music on the tracked music channel."""
        if self.music_channel:
            self.music_channel.stop()