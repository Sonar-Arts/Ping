import pygame
import threading
import time
import os
import logging
from queue import Queue, Empty, Full
from collections import deque
from ..Submodules.Ping_Settings import SettingsScreen # Import SettingsScreen

# --- Constants ---
DEFAULT_SFX_CHANNELS = 16
DEFAULT_FADE_DURATION = 1.0
SOUND_END_EVENT = pygame.USEREVENT + 1 # Custom event for sound completion

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SoundManager:
    """
    Manages loading, caching, playback, and mixing of sound effects and music
    using threading for non-blocking audio.
    """

    def __init__(self, sfx_channels=DEFAULT_SFX_CHANNELS):
        """
        Initializes the SoundManager.

        Args:
            sfx_channels (int): Number of channels to reserve for sound effects.
        """
        if not pygame.mixer.get_init():
            logger.warning("Pygame mixer not initialized. Initializing now.")
            pygame.mixer.init() # Consider frequency, size, channels, buffer options if needed

        pygame.mixer.set_reserved(2) # Reserve 2 channels for music crossfading
        self._num_sfx_channels = min(sfx_channels, pygame.mixer.get_num_channels() - 2)
        if self._num_sfx_channels < 1:
            logger.error("Not enough available channels for SFX after reserving for music.")
            # Fallback or raise error? For now, let's try to proceed with 0 SFX channels.
            self._num_sfx_channels = 0

        pygame.mixer.set_num_channels(self._num_sfx_channels + 2) # Total channels
        logger.info(f"Initialized SoundManager with {self._num_sfx_channels} SFX channels and 2 Music channels.")

        # --- Caches ---
        self._sfx_cache = {}  # { name: pygame.Sound }
        self._music_cache = {} # { name: str (path) } - Music is streamed, only cache path

        # --- Volume Control (0.0 to 1.0) ---
        self._master_volume = 1.0
        self._sfx_volume = 1.0
        self._music_volume = 1.0
        # Store base volumes if needed for individual sound adjustments later
        # self._base_volumes = {}

        # --- Sound Effect Channel Management ---
        self._sfx_channels = [pygame.mixer.Channel(i) for i in range(self._num_sfx_channels)]
        self._available_sfx_channels = Queue(maxsize=self._num_sfx_channels)
        # Store channel indices (integers) in the queue
        for i in range(self._num_sfx_channels):
            channel = pygame.mixer.Channel(i)
            channel.set_endevent(SOUND_END_EVENT)
            self._available_sfx_channels.put(i) # Put index i into the queue
        self._active_sfx = {} # { channel_id (int): {sound_name, thread} }

        # --- Music Channel Management ---
        self._music_channel_a = pygame.mixer.Channel(self._num_sfx_channels)
        self._music_channel_b = pygame.mixer.Channel(self._num_sfx_channels + 1)
        self._active_music_channel = None # Reference to the currently primary music channel
        self._music_fade_thread = None
        self._current_music_name = None

        # --- Threading Locks ---
        self._sfx_cache_lock = threading.Lock()
        self._music_cache_lock = threading.Lock()
        self._channel_lock = threading.Lock() # Protects _available_sfx_channels and _active_sfx
        self._volume_lock = threading.Lock() # Protects volume attributes

        # --- Debugging ---
        # Load initial debug state from settings
        self._debug_enabled = SettingsScreen.get_sound_debug_enabled()
        # Set initial logger level based on loaded setting
        logger.setLevel(logging.INFO if self._debug_enabled else logging.WARNING)
        logger.info(f"SoundManager Initialized. Logging Level: {'INFO' if self._debug_enabled else 'WARNING'}")


        # --- Sound Definitions (Example - load from config later?) ---
        self._sound_paths = {
            'sfx': {
                'paddle': "Ping_Sounds/Ping_FX/Paddle.wav",
                'score': "Ping_Sounds/Ping_FX/Score.wav",
                'wahahoo': "Ping_Sounds/Ping_FX/wahahoo.wav",
                # Add more SFX here
            },
            'music': {
                'intro': "Ping Assets/Music/PIntroMusicTemp.wav",
                'main': "Ping Assets/Music/PMainMusicTemp.wav",
                'sewer': "Ping Assets/Music/PSewerZoneTemp.wav",
                # Add more music tracks here
            }
        }

        # Load initial volume settings (replace with your actual settings loading)
        self._load_volume_settings()


    # --- Sound Loading & Caching ---

    def _load_sfx(self, name):
        """Loads an SFX sound file. Not thread-safe; acquire lock before calling."""
        if name not in self._sound_paths['sfx']:
            logger.error(f"Sound effect name '{name}' not defined in sound paths.")
            return None
        path = self._sound_paths['sfx'][name]
        if not os.path.exists(path):
            logger.error(f"Sound effect file not found: {path}")
            return None
        try:
            sound = pygame.mixer.Sound(path)
            # Don't cache here, cache in get_sfx after successful load
            logger.info(f"Loaded SFX: {name} from {path}")
            return sound
        except pygame.error as e:
            logger.error(f"Error loading SFX '{name}' from {path}: {e}")
            return None

    def get_sfx(self, name):
        """Gets an SFX sound object, loading and caching it if necessary."""
        with self._sfx_cache_lock:
            if name in self._sfx_cache:
                return self._sfx_cache[name]
        # Load outside the lock to avoid holding it during file I/O
        sound = self._load_sfx(name) # This method handles logging errors
        # Add to cache if loaded successfully
        if sound:
             with self._sfx_cache_lock:
                  self._sfx_cache[name] = sound
        return sound # Returns None if loading failed

    def preload_sfx(self, names):
        """Preloads a list of SFX names into the cache."""
        for name in names:
            self.get_sfx(name) # This handles loading and caching

    def unload_sfx(self, name):
        """Removes an SFX from the cache."""
        with self._sfx_cache_lock:
            if name in self._sfx_cache:
                del self._sfx_cache[name]
                logger.info(f"Unloaded SFX: {name}")

    def _get_music_path(self, name):
        """Gets the path for a music track."""
        with self._music_cache_lock: # Although just reading, lock for consistency
            if name not in self._sound_paths['music']:
                logger.error(f"Music name '{name}' not defined in sound paths.")
                return None
            path = self._sound_paths['music'][name]
            if not os.path.exists(path):
                logger.error(f"Music file not found: {path}")
                return None
            # Optional: Cache path if lookup is complex, but here it's simple
            # self._music_cache[name] = path
            return path

    # --- Volume Control ---

    def _load_volume_settings(self):
        """Placeholder: Load volume settings from a file or config."""
        # Replace this with your actual settings loading logic
        try:
            # Example: Reading from settings.txt
            volume_settings = {} # Store only valid volume settings
            path = "Game Parameters/settings.txt"
            expected_volume_keys = {'MASTER_VOLUME', 'EFFECTS_VOLUME', 'MUSIC_VOLUME'}
            if os.path.exists(path):
                 with open(path, "r") as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            # Only process expected volume keys
                            if key in expected_volume_keys:
                                try:
                                    volume_settings[key] = float(value)
                                except ValueError:
                                    logger.warning(f"Invalid numeric value for volume setting {key} in {path}: '{value}'")
                            # else: # Optionally log ignored keys
                            if self._debug_enabled: logger.debug(f"Ignoring non-volume setting: {key}")
            else:
                logger.warning(f"Settings file not found: {path}. Using default volumes.")

            with self._volume_lock:
                # Use volume_settings dict which only contains valid floats
                self._master_volume = volume_settings.get('MASTER_VOLUME', 50.0) / 100.0
                self._sfx_volume = volume_settings.get('EFFECTS_VOLUME', 50.0) / 100.0
                self._music_volume = volume_settings.get('MUSIC_VOLUME', 50.0) / 100.0
            logger.info(f"Loaded volumes: Master={self._master_volume:.2f}, SFX={self._sfx_volume:.2f}, Music={self._music_volume:.2f}")
            # Apply loaded volumes immediately
            self._update_all_volumes()

        except Exception as e:
            logger.error(f"Error loading volume settings: {e}. Using default volumes.")
            with self._volume_lock:
                self._master_volume = 0.5
                self._sfx_volume = 0.5
                self._music_volume = 0.5
            self._update_all_volumes() # Apply default volumes

    def _save_volume_setting(self, setting_name, value_percent):
        """Placeholder: Save a single volume setting."""
         # Replace this with your actual settings saving logic
        try:
            path = "Game Parameters/settings.txt"
            if not os.path.exists(os.path.dirname(path)):
                 os.makedirs(os.path.dirname(path))

            lines = []
            updated = False
            if os.path.exists(path):
                with open(path, "r") as f:
                    lines = f.readlines()

            with open(path, "w") as f:
                found = False
                for i, line in enumerate(lines):
                    if line.startswith(f'{setting_name}='):
                        lines[i] = f"{setting_name}={value_percent}\n"
                        found = True
                        break
                if not found:
                    lines.append(f"{setting_name}={value_percent}\n")
                f.writelines(lines)
            logger.info(f"Saved setting: {setting_name}={value_percent}")
        except Exception as e:
            logger.error(f"Error saving volume setting {setting_name}: {e}")


    def set_master_volume(self, volume_percent):
        """Sets the master volume (0-100)."""
        volume = max(0.0, min(100.0, volume_percent)) / 100.0
        with self._volume_lock:
            if self._master_volume != volume:
                self._master_volume = volume
                logger.info(f"Master volume set to {volume:.2f}")
                self._update_all_volumes()
                # Save setting (consider debouncing if called rapidly)
                self._save_volume_setting('MASTER_VOLUME', volume_percent)


    def set_sfx_volume(self, volume_percent):
        """Sets the sound effects volume (0-100)."""
        volume = max(0.0, min(100.0, volume_percent)) / 100.0
        with self._volume_lock:
             if self._sfx_volume != volume:
                self._sfx_volume = volume
                logger.info(f"SFX volume set to {volume:.2f}")
                self._update_sfx_volumes()
                self._save_volume_setting('EFFECTS_VOLUME', volume_percent)

    def set_music_volume(self, volume_percent):
        """Sets the music volume (0-100)."""
        volume = max(0.0, min(100.0, volume_percent)) / 100.0
        with self._volume_lock:
            if self._music_volume != volume:
                self._music_volume = volume
                logger.info(f"Music volume set to {volume:.2f}")
                self._update_music_volume()
                self._save_volume_setting('MUSIC_VOLUME', volume_percent)

    def _update_all_volumes(self):
        """Updates volumes on all active channels. Assumes volume lock is held."""
        self._update_sfx_volumes()
        self._update_music_volume()

    def _update_sfx_volumes(self):
        """Updates volumes on active SFX channels. Assumes volume lock is held."""
        final_sfx_vol = self._master_volume * self._sfx_volume
        with self._channel_lock:
            for channel_id in self._active_sfx:
                try:
                    channel = pygame.mixer.Channel(channel_id)
                    # Add logic here if individual sounds have base volumes
                    channel.set_volume(final_sfx_vol)
                except IndexError:
                     logger.warning(f"Channel ID {channel_id} no longer valid during volume update.")


    def _update_music_volume(self):
        """Updates volume on the active music channel. Assumes volume lock is held."""
        final_music_vol = self._master_volume * self._music_volume
        # No channel lock needed for music channels as they aren't in the pool
        if self._active_music_channel and self._active_music_channel.get_sound():
             # Don't adjust volume during fade, it's handled by the fade thread
            if self._music_fade_thread is None or not self._music_fade_thread.is_alive():
                 try:
                     self._active_music_channel.set_volume(final_music_vol)
                 except pygame.error as e:
                      logger.warning(f"Error setting music channel volume: {e}")


    # --- Sound Effect Playback ---

    def play_sfx(self, name, loops=0, volume_multiplier=1.0, pitch_shift=0.0):
        """
        Plays a sound effect.

        Args:
            name (str): The name of the sound effect (must be defined).
            loops (int): Number of times to repeat (-1 for infinite).
            volume_multiplier (float): Adjusts volume relative to SFX setting (0.0 to N).
            pitch_shift (float): Semitones to shift pitch (experimental, requires sound manipulation). Not implemented yet.

        Returns:
            pygame.mixer.Channel or None: The channel playing the sound, or None if failed.
        """
        if pitch_shift != 0.0:
            logger.warning("Pitch shifting not implemented yet.")

        sound = self.get_sfx(name)
        if not sound:
            return None # Error logged in get_sfx

        channel_id = None
        channel_obj = None
        try:
            # Get a channel index without blocking indefinitely
            with self._channel_lock:
                channel_id = self._available_sfx_channels.get_nowait()
                channel_obj = pygame.mixer.Channel(channel_id) # Get object from index
        except Empty:
            # --- Priority Logic (Simple Example: Steal oldest sound) ---
            with self._channel_lock:
                if self._active_sfx:
                    # Find the channel ID that started earliest (approximate)
                    try:
                        # Get the first key (channel_id) from the active dictionary
                        oldest_channel_id_to_steal = next(iter(self._active_sfx))
                        channel_obj_to_steal = pygame.mixer.Channel(oldest_channel_id_to_steal)
                        old_sound_info = self._active_sfx.pop(oldest_channel_id_to_steal, None)
                        if old_sound_info:
                            logger.warning(f"No free channels. Stealing channel {oldest_channel_id_to_steal} (was playing {old_sound_info['sound_name']}) for {name}.")
                            channel_obj_to_steal.stop() # Stop the old sound
                            # The stolen channel ID is now implicitly available
                            channel_id = oldest_channel_id_to_steal
                            channel_obj = channel_obj_to_steal
                        else:
                             logger.warning(f"No free channels and couldn't determine oldest channel to steal for {name}.")
                             # Attempt to put the popped ID back? Or just fail. Let's fail for now.
                             return None # Truly no channels available
                    except (StopIteration, IndexError) as e: # Handle potential errors getting channel
                         logger.warning(f"Error finding channel to steal: {e}. Cannot play {name}.")
                         return None
                else:
                    logger.warning(f"No free SFX channels available to play {name}.")
                    return None


        # Ensure we got a valid channel ID and object
        if channel_id is None or channel_obj is None:
             logger.error(f"Failed to acquire channel for SFX '{name}'.")
             return None

        # --- Play in a separate thread ---
        # Pass channel_id and channel_obj to the thread
        def sfx_playback_thread(target_channel_id, target_channel_obj, target_sound, sound_name, target_loops, target_vol_mult):
            try:
                with self._volume_lock:
                    final_volume = self._master_volume * self._sfx_volume * target_vol_mult
                    final_volume = max(0.0, min(1.0, final_volume)) # Clamp volume

                target_channel_obj.set_volume(final_volume)
                target_channel_obj.play(target_sound, loops=target_loops)
                if self._debug_enabled: logger.debug(f"Playing SFX '{sound_name}' on channel {target_channel_id}")

                # Keep track of active sound using channel_id (outside volume lock)
                with self._channel_lock:
                     self._active_sfx[target_channel_id] = {'sound_name': sound_name, 'thread': threading.current_thread()}

            except Exception as e:
                logger.error(f"Error in SFX playback thread for '{sound_name}' on channel {target_channel_id}: {e}")
                # Ensure channel ID is returned even if playback fails immediately
                # Pass the integer channel_id
                self.handle_sound_end(target_channel_id)

        thread = threading.Thread(target=sfx_playback_thread, args=(channel_id, channel_obj, sound, name, loops, volume_multiplier), daemon=True)
        thread.start()

        return channel_obj # Return the channel object immediately for potential external use (like stop)

    # Updated signature to accept channel_id
    def handle_sound_end(self, channel_id):
        """
        Called when a sound finishes (via SOUND_END_EVENT or manually).
        Returns the channel to the available pool.

        Args:
            channel_id (int): The ID of the channel that finished.
        """
        if channel_id is None: return

        try:
            # Check if it's an SFX channel before proceeding
            if 0 <= channel_id < self._num_sfx_channels:
                 with self._channel_lock:
                    # Remove from active list
                    if channel_id in self._active_sfx:
                        sound_name = self._active_sfx.pop(channel_id, {}).get('sound_name', 'unknown')
                        if self._debug_enabled: logger.debug(f"SFX '{sound_name}' ended on channel {channel_id}. Returning to pool.")
                    else:
                        # Could happen if stop_sfx was called simultaneously
                        if self._debug_enabled: logger.debug(f"Channel {channel_id} ended but wasn't in active list (likely stopped manually).")

                    # Return channel index (integer) to queue if it's not full
                    try:
                        # No need to get the object, just put the ID back
                        self._available_sfx_channels.put_nowait(channel_id)
                    except Full:
                        # This warning seems to be happening, investigate why pool might be full
                        logger.warning(f"SFX channel pool queue unexpectedly full when returning channel {channel_id}.")
                    # No need for IndexError check here as we are just putting the ID back
            else:
                # Potentially a music channel event, ignore here
                pass
        except pygame.error as e: # Catch potential error if channel is invalid
             logger.warning(f"Error handling sound end for channel ID {channel_id}: {e}")


    def stop_sfx(self, name=None, channel=None):
        """Stops specific SFX instances or all SFX."""
        with self._channel_lock:
            channels_to_stop = []
            if channel:
                # Stop specific channel if it's active
                try:
                    ch_id = channel.get_id()
                    if ch_id in self._active_sfx:
                        channels_to_stop.append(ch_id)
                except pygame.error:
                     logger.warning("Provided channel for stop_sfx is invalid.")
            elif name:
                # Stop all instances of a named sound
                for ch_id, info in list(self._active_sfx.items()): # Iterate over copy
                    if info['sound_name'] == name:
                        channels_to_stop.append(ch_id)
            else:
                # Stop all SFX
                channels_to_stop.extend(list(self._active_sfx.keys()))

            for ch_id in channels_to_stop:
                try:
                    pygame.mixer.Channel(ch_id).stop()
                    # Stopping should trigger the end event, which calls handle_sound_end
                    # If end event fails, channel might get stuck. Consider manual cleanup:
                    # if ch_id in self._active_sfx: del self._active_sfx[ch_id]
                    # try: self._available_sfx_channels.put_nowait(pygame.mixer.Channel(ch_id)) except Full: pass
                    if self._debug_enabled: logger.debug(f"Stopped SFX on channel {ch_id}")
                except IndexError:
                     logger.warning(f"Channel ID {ch_id} no longer valid during stop_sfx.")
                except pygame.error as e:
                     logger.warning(f"Pygame error stopping SFX on channel {ch_id}: {e}")


    # --- Music Playback ---

    def play_music(self, name, loops=-1, fade_duration=DEFAULT_FADE_DURATION):
        """
        Plays a music track, crossfading from any currently playing music.

        Args:
            name (str): The name of the music track (must be defined).
            loops (int): Number of times to repeat (-1 for infinite).
            fade_duration (float): Duration of the crossfade in seconds.
        """
        if self._current_music_name == name and self._active_music_channel and self._active_music_channel.get_busy():
             logger.info(f"Music '{name}' is already playing.")
             return # Already playing this track

        music_path = self._get_music_path(name)
        if not music_path:
            return # Error logged in _get_music_path

        # --- Stop existing fade if any ---
        if self._music_fade_thread and self._music_fade_thread.is_alive():
            logger.info("Interrupting existing music fade.")
            # Need a way to signal the fade thread to stop cleanly.
            # For now, we rely on the new thread taking over volume control.
            # A more robust solution would use threading.Event.
            pass # Let the old thread finish, the new one will take over

        # --- Play in a separate thread ---
        def music_playback_thread(target_path, target_name, target_loops, target_fade_duration):
            logger.info(f"Starting music playback thread for '{target_name}'")
            from_channel = self._active_music_channel
            to_channel = self._music_channel_b if from_channel == self._music_channel_a else self._music_channel_a

            try:
                # Start loading/playing the new track on the 'to' channel at volume 0
                to_channel.set_volume(0)
                to_channel.play(pygame.mixer.Sound(target_path), loops=target_loops) # Load sound here for streaming
                logger.info(f"Started '{target_name}' on music channel (initially muted)")

                # --- Perform Fade ---
                start_time = time.monotonic()
                end_time = start_time + target_fade_duration

                with self._volume_lock:
                    target_music_volume = self._master_volume * self._music_volume

                # Get initial volume of the 'from' channel safely
                from_volume_start = 0.0
                if from_channel and from_channel.get_busy():
                    try:
                        from_volume_start = from_channel.get_volume()
                    except pygame.error: # Channel might have become invalid
                         logger.warning("Error getting volume from 'from_channel' during fade start.")
                         from_channel = None # Treat as if no music was playing

                logger.info(f"Fading from {'previous music channel' if from_channel else 'silence'} to new music channel over {target_fade_duration}s")

                while time.monotonic() < end_time:
                    elapsed = time.monotonic() - start_time
                    # Avoid division by zero if fade duration is 0
                    progress = 1.0 if target_fade_duration == 0 else min(1.0, elapsed / target_fade_duration)


                    # Calculate volumes based on progress
                    current_to_volume = target_music_volume * progress
                    current_from_volume = from_volume_start * (1.0 - progress)

                    # Apply volumes safely
                    try:
                        to_channel.set_volume(current_to_volume)
                    except pygame.error:
                        logger.warning(f"Error setting volume on 'to_channel' during fade.")
                        break # Should we abort the fade?
                    if from_channel:
                         try:
                            from_channel.set_volume(current_from_volume)
                         except pygame.error:
                            logger.warning(f"Error setting volume on 'from_channel' during fade.")
                            from_channel = None # Stop trying to fade out old channel

                    time.sleep(0.01) # Small sleep to avoid busy-waiting

                # --- Finalize Fade ---
                logger.info(f"Fade complete for '{target_name}'")
                try:
                    to_channel.set_volume(target_music_volume) # Ensure target volume is set
                except pygame.error:
                     logger.error(f"Failed to set final volume for '{target_name}' on music channel")

                if from_channel:
                    try:
                        from_channel.stop() # Stop the old music
                        if self._debug_enabled: logger.debug(f"Stopped old music on previous music channel")
                    except pygame.error:
                         logger.warning(f"Error stopping old music on previous music channel")


                # Update active channel reference
                self._active_music_channel = to_channel
                self._current_music_name = target_name

            except pygame.error as e:
                logger.error(f"Pygame error during music playback/fade for '{target_name}': {e}")
                # Attempt cleanup
                if to_channel: to_channel.stop()
                if from_channel: from_channel.stop()
                self._active_music_channel = None
                self._current_music_name = None
            except Exception as e:
                 logger.error(f"Unexpected error in music playback thread for '{target_name}': {e}")
                 if to_channel: to_channel.stop()
                 if from_channel: from_channel.stop()
                 self._active_music_channel = None
                 self._current_music_name = None


        self._music_fade_thread = threading.Thread(target=music_playback_thread, args=(music_path, name, loops, fade_duration), daemon=True)
        self._music_fade_thread.start()

    def stop_music(self, fade_duration=DEFAULT_FADE_DURATION):
        """Fades out and stops the currently playing music."""
        if not self._active_music_channel or not self._active_music_channel.get_busy():
            logger.info("No music currently playing.")
            return

        # --- Stop existing fade if any ---
        if self._music_fade_thread and self._music_fade_thread.is_alive():
            logger.info("Interrupting existing music fade to stop music.")
            # Signal thread to stop? For now, let the new fade take over.
            pass

        # --- Fade out in a separate thread ---
        def music_stop_thread(target_channel, target_fade_duration):
            logger.info(f"Starting music stop thread for active music channel")
            start_time = time.monotonic()
            end_time = start_time + target_fade_duration
            try:
                from_volume_start = target_channel.get_volume()
            except pygame.error:
                 logger.warning(f"Error getting volume from active music channel during stop fade start.")
                 target_channel.stop() # Stop immediately if volume can't be read
                 self._active_music_channel = None
                 self._current_music_name = None
                 return

            logger.info(f"Fading out music on active music channel over {target_fade_duration}s")

            while time.monotonic() < end_time:
                elapsed = time.monotonic() - start_time
                # Avoid division by zero if fade duration is 0
                progress = 1.0 if target_fade_duration == 0 else min(1.0, elapsed / target_fade_duration)
                current_from_volume = from_volume_start * (1.0 - progress)
                try:
                    target_channel.set_volume(current_from_volume)
                except pygame.error:
                     logger.warning(f"Error setting volume on active music channel during stop fade.")
                     break # Stop trying to fade
                time.sleep(0.01)

            # --- Finalize Stop ---
            try:
                target_channel.stop()
                logger.info(f"Stopped music on active music channel")
            except pygame.error:
                 logger.error(f"Error stopping music on active music channel after fade.")

            # Clear active channel only if this thread was responsible for the currently active channel
            if self._active_music_channel == target_channel:
                self._active_music_channel = None
                self._current_music_name = None


        # Use the currently active channel
        channel_to_stop = self._active_music_channel
        self._music_fade_thread = threading.Thread(target=music_stop_thread, args=(channel_to_stop, fade_duration), daemon=True)
        self._music_fade_thread.start()


    # --- Debugging Control ---
    def toggle_debug(self):
        """Toggles the logging level for SoundManager messages and saves the state."""
        self._debug_enabled = not self._debug_enabled
        if self._debug_enabled:
            logger.setLevel(logging.INFO) # Show INFO and higher when enabled
            # Or use logging.DEBUG if you have debug-level messages you want to see
            logger.info("SoundManager Logging Enabled (Level: INFO)")
        else:
            # Log before changing level so the user sees the confirmation message
            logger.info("SoundManager Logging Disabled (Level: ERROR)") # Log confirmation
            logger.setLevel(logging.ERROR) # Show only ERROR and CRITICAL when disabled

        # Save the new state to the settings file
        SettingsScreen.update_sound_debug_enabled(self._debug_enabled)

        return self._debug_enabled

    # --- Cleanup & Event Handling ---

    def handle_event(self, event):
        """Processes Pygame events, specifically looking for SOUND_END_EVENT."""
        if event.type == SOUND_END_EVENT:
            # Check which channel finished
            # Pygame doesn't reliably add channel info to the event object
            # We need to check all our managed SFX channels
            for i in range(self._num_sfx_channels):
                 channel = pygame.mixer.Channel(i)
                 try:
                     if not channel.get_busy():
                         # Check if it *was* busy and is now free
                         # Pass the channel *index* (ID) to handle_sound_end
                         self.handle_sound_end(i)
                 except pygame.error as e:
                      # Channel might be invalid if mixer was stopped abruptly
                      logger.warning(f"Error checking channel {i} busy state: {e}")


    def shutdown(self):
        """Stops all sounds and music, cleans up resources."""
        logger.info("Shutting down SoundManager...")
        self.stop_sfx() # Stop all sound effects
        self.stop_music(fade_duration=0.1) # Quick fade out for music

        # Wait briefly for fade threads to potentially finish
        # A more robust solution involves joining threads, but requires them not being daemons
        # or using signaling mechanisms (e.g., threading.Event)
        time.sleep(0.2)

        # Explicitly stop all channels
        pygame.mixer.stop()
        logger.info("All mixer channels stopped.")

        # Clear caches (optional, depending on desired behavior)
        with self._sfx_cache_lock:
            self._sfx_cache.clear()
        # self._music_cache.clear() # Music cache only stores paths usually

        # Clear channel queue and active lists
        with self._channel_lock:
            while not self._available_sfx_channels.empty():
                try:
                    self._available_sfx_channels.get_nowait()
                except Empty:
                    break
            self._active_sfx.clear()

        logger.info("SoundManager shutdown complete.")

# --- Example Usage (for testing) ---
if __name__ == '__main__':
    pygame.init()
    pygame.display.set_mode((200, 100)) # Need a display for events

    # Create dummy sound files if they don't exist
    os.makedirs("Ping_Sounds/Ping_FX", exist_ok=True)
    os.makedirs("Ping Assets/Music", exist_ok=True)
    dummy_files = {
        "Ping_Sounds/Ping_FX/Paddle.wav": b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\xfa\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00',
        "Ping_Sounds/Ping_FX/Score.wav": b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\xfa\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00',
        "Ping_Sounds/Ping_FX/wahahoo.wav": b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\xfa\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00',
        "Ping Assets/Music/PIntroMusicTemp.wav": b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\xfa\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00',
        "Ping Assets/Music/PMainMusicTemp.wav": b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\xfa\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00',
        "Ping Assets/Music/PSewerZoneTemp.wav": b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\xfa\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00',
    }
    for fpath, content in dummy_files.items():
        if not os.path.exists(fpath):
            with open(fpath, 'wb') as f:
                f.write(content)
            print(f"Created dummy file: {fpath}")

    # Create dummy settings file
    settings_path = "Game Parameters/settings.txt"
    if not os.path.exists(settings_path):
         os.makedirs(os.path.dirname(settings_path), exist_ok=True)
         with open(settings_path, "w") as f:
             f.write("MASTER_VOLUME=70\n")
             f.write("EFFECTS_VOLUME=60\n")
             f.write("MUSIC_VOLUME=50\n")
             # Add other non-volume settings to test loading robustness
             f.write("PLAYER_NAME=Tester\n")
             f.write("SHADER_ENABLED=true\n")
         print(f"Created dummy settings file: {settings_path}")


    sound_manager = SoundManager(sfx_channels=4) # Use fewer channels for testing

    print("Testing Sound Manager...")
    print("Press keys to test sounds:")
    print("  P: Play Paddle SFX")
    print("  S: Play Score SFX")
    print("  W: Play Wahahoo SFX (Looping)")
    print("  Space: Stop all SFX")
    print("  1: Play Intro Music")
    print("  2: Play Main Music (Fade)")
    print("  3: Play Sewer Music (Fade)")
    print("  0: Stop Music (Fade)")
    print("  Up/Down: Master Volume")
    print("  Left/Right: SFX Volume")
    print("  PgUp/PgDn: Music Volume")
    print("  Q: Quit")

    running = True
    clock = pygame.time.Clock()
    master_vol_pct = sound_manager._master_volume * 100
    sfx_vol_pct = sound_manager._sfx_volume * 100
    music_vol_pct = sound_manager._music_volume * 100

    while running:
        events = pygame.event.get() # Get events once per frame
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    print("Playing paddle...")
                    sound_manager.play_sfx('paddle')
                elif event.key == pygame.K_s:
                    print("Playing score...")
                    sound_manager.play_sfx('score')
                elif event.key == pygame.K_w:
                     print("Playing wahahoo (looping)...")
                     sound_manager.play_sfx('wahahoo', loops=-1) # Loop wahahoo
                elif event.key == pygame.K_SPACE:
                     print("Stopping all SFX...")
                     sound_manager.stop_sfx() # Stop all SFX
                elif event.key == pygame.K_1:
                    print("Playing intro music...")
                    sound_manager.play_music('intro', loops=0, fade_duration=0.1) # No loop, quick fade
                elif event.key == pygame.K_2:
                    print("Playing main music...")
                    sound_manager.play_music('main')
                elif event.key == pygame.K_3:
                    print("Playing sewer music...")
                    sound_manager.play_music('sewer')
                elif event.key == pygame.K_0:
                    print("Stopping music...")
                    sound_manager.stop_music()
                elif event.key == pygame.K_UP:
                    master_vol_pct = min(100, master_vol_pct + 10)
                    sound_manager.set_master_volume(master_vol_pct)
                    print(f"Master Vol: {master_vol_pct}%")
                elif event.key == pygame.K_DOWN:
                    master_vol_pct = max(0, master_vol_pct - 10)
                    sound_manager.set_master_volume(master_vol_pct)
                    print(f"Master Vol: {master_vol_pct}%")
                elif event.key == pygame.K_LEFT:
                    sfx_vol_pct = max(0, sfx_vol_pct - 10)
                    sound_manager.set_sfx_volume(sfx_vol_pct)
                    print(f"SFX Vol: {sfx_vol_pct}%")
                elif event.key == pygame.K_RIGHT:
                    sfx_vol_pct = min(100, sfx_vol_pct + 10)
                    sound_manager.set_sfx_volume(sfx_vol_pct)
                    print(f"SFX Vol: {sfx_vol_pct}%")
                elif event.key == pygame.K_PAGEUP:
                     music_vol_pct = min(100, music_vol_pct + 10)
                     sound_manager.set_music_volume(music_vol_pct)
                     print(f"Music Vol: {music_vol_pct}%")
                elif event.key == pygame.K_PAGEDOWN:
                     music_vol_pct = max(0, music_vol_pct - 10)
                     sound_manager.set_music_volume(music_vol_pct)
                     print(f"Music Vol: {music_vol_pct}%")

                elif event.key == pygame.K_q:
                    running = False

            # Let the sound manager handle its events (pass the current event)
            sound_manager.handle_event(event)

        # Keep pygame running
        pygame.display.flip()
        clock.tick(30)

    sound_manager.shutdown()
    pygame.quit()
    print("Test complete.")