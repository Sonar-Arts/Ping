import pygame
import time
from ..Submodules.Ping_Fonts import get_pixel_font
from collections import deque

class DebugConsole:
    def __init__(self):
        # Message storage
        self.messages = deque(maxlen=1000)  # Keep last 1000 messages
        self.visible = False
        self.toggle_time = 0
        self.scroll_offset = 0
        
        # Debug flags
        self.debug_ai = False
        self.debug_collisions = False
        self.debug_input = False
        self.debug_sound = False
        self.debug_physics = False
        self.debug_settings = False
        
        # Visual settings
        self.bg_color = (0, 0, 0, 200)  # Semi-transparent background
        self.text_color = (0, 255, 0)  # Green text
        self.selected_color = (0, 100, 0, 150)  # Selection highlight color with transparency
        self.font_size = 16
        self.line_height = 20
        self.padding = 10
        self.console_height = 300
        
        # Line wrapping
        self.wrapped_lines = []  # Cache for wrapped lines
        self.max_line_width = 0  # Will be set in draw()
        
        # Selection handling
        self.selection_start = None  # (line_index, char_index)
        self.selection_end = None    # (line_index, char_index)
        self.dragging = False
        
        # Command handling
        self.current_command = ""
        self.command_history = deque(maxlen=20)
        self.history_index = -1
        
        # Reference to other game systems (must be set externally)
        self.sound_manager = None # Needs to be set to the SoundManager instance
        self.game_state = None # Reference to hold game state for debug commands
        
        # Commands dictionary
        self.commands = {
            'help': self.cmd_help,
            'clear': self.cmd_clear,
            'toggle_shader': self.cmd_toggle_shader,
            'win_scores': self.cmd_win_scores,
            'debug_ai': self.cmd_debug_ai,
            'debug_collisions': self.cmd_debug_collisions,
            'debug_input': self.cmd_debug_input,
            'debug_sound': self.cmd_debug_sound,
            'debug_physics': self.cmd_debug_physics,
            'debug_settings': self.cmd_debug_settings,
            'toggle_sound_debug': self.cmd_toggle_sound_debug,
            'spawn_ball': self.cmd_spawn_ball # Command to spawn additional balls
        }

    def update(self, events):
        """Update console state based on events."""
        current_time = time.time()
        
        # Handle backtick toggle first
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == 96:  # ASCII for backtick
                if current_time - self.toggle_time > 0.2:  # Debounce
                    was_visible = self.visible
                    self.visible = not was_visible
                    self.toggle_time = current_time
                    if not self.visible:
                        self.clear_selection()  # Clear selection when hiding
                    self.scroll_offset = 0  # Reset scroll position when toggling
                    print(f"Debug Console {'activated' if self.visible else 'deactivated'}")  # Terminal output only
                    return True
        
        # Handle events when console is visible
        if self.visible:
            # Calculate maximum scroll offset
            max_scroll = max(0, len(self.wrapped_lines) - self.console_height // self.line_height + 3)
            
            for event in events:
                # Handle mouse wheel scrolling first
                if event.type == pygame.MOUSEWHEEL:
                    mouse_y = pygame.mouse.get_pos()[1]
                    if mouse_y < self.console_height:
                        # Only scroll if not selecting text
                        if not self.dragging:
                            # Update scroll offset with bounds checking
                            self.scroll_offset = max(0, min(max_scroll,
                                                        self.scroll_offset - event.y * 3))
                # Handle mouse selection
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[1] < self.console_height:
                        line_idx = self._get_line_index(mouse_pos)
                        if line_idx is not None and 0 <= line_idx < len(self.wrapped_lines):
                            self.start_selection(mouse_pos)
                            self.dragging = True
                        else:
                            self.clear_selection()  # Clear selection when clicking empty space
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.dragging:
                        self.dragging = False
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    self.update_selection(pygame.mouse.get_pos())
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.copy_selection()
                # Handle all other events
                elif self.handle_event(event):
                    return True

        return False

    def log(self, message):
        """Add a message to the console."""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.messages.append(f"[{timestamp}] {message}")
    
    def execute_command(self):
        """Execute entered command."""
        if not self.current_command:
            return
            
        self.log(f"> {self.current_command}")
        print(f"Executing command: {self.current_command}")  # Keep initial debug print
        
        cmd_parts = self.current_command.split()
        cmd = cmd_parts[0].lower()
        
        if cmd in self.commands:
            try:
                self.commands[cmd](cmd_parts[1:])
            except Exception as e:
                error_msg = f"Error executing command: {str(e)}"
                self.log(error_msg)
        else:
            error_msg = f"Unknown command: {cmd}"
            self.log(error_msg)
        
        self.command_history.append(self.current_command)
        self.current_command = ""
        self.history_index = -1
    
    def cmd_help(self, args):
        """Show available commands."""
        self.log("Available commands:")
        command_help = {
            'help': 'Show this help message',
            'clear': 'Clear console messages',
            'toggle_shader': 'Toggle shader effects on/off',
            'win_scores': 'Set number of scores needed to win (usage: win_scores <number>)',
            'debug_ai': 'Toggle AI debug messages',
            'debug_collisions': 'Toggle collision detection debug messages',
            'debug_input': 'Toggle input processing debug messages',
            'debug_sound': 'Toggle sound system debug messages',
            'debug_physics': 'Toggle physics simulation debug messages',
            'debug_settings': 'Toggle settings menu debug messages',
            'toggle_sound_debug': 'Toggle SoundManager debug messages',
            'spawn_ball': 'Spawn a new ball in the game'
        }
        for cmd, desc in command_help.items():
            self.log(f"  {cmd:<16} - {desc}")
    
    def cmd_clear(self, args):
        """Clear console messages."""
        self.messages.clear()
        self.log("Console cleared")
    
    def cmd_toggle_shader(self, args):
        """Toggle shader on/off."""
        from ..Submodules.Ping_Settings import SettingsScreen
        current = SettingsScreen.get_shader_enabled()
        SettingsScreen.update_shader_enabled(not current)
        self.log(f"Shader {'disabled' if current else 'enabled'}")

    def cmd_win_scores(self, args):
        """Set the number of scores needed to win."""
        if not args:
            self.log("Usage: win_scores <number>")
            return
        try:
            new_score = int(args[0])
            if new_score <= 0:
                self.log("Error: Score must be greater than 0")
                return
            from ..Submodules.Ping_Settings import SettingsScreen
            SettingsScreen.update_win_scores(new_score)
            self.log(f"Win scores set to {new_score}")
        except ValueError:
            self.log("Error: Score must be a valid number")
    def cmd_debug_ai(self, args):
        """Toggle AI debug messages."""
        self.debug_ai = not self.debug_ai
        self.log(f"AI debug messages {'enabled' if self.debug_ai else 'disabled'}")
    
    def cmd_debug_collisions(self, args):
        """Toggle collision detection debug messages."""
        self.debug_collisions = not self.debug_collisions
        self.log(f"Collision debug messages {'enabled' if self.debug_collisions else 'disabled'}")
    
    def cmd_debug_input(self, args):
        """Toggle input processing debug messages."""
        self.debug_input = not self.debug_input
        self.log(f"Input debug messages {'enabled' if self.debug_input else 'disabled'}")
    
    def cmd_debug_sound(self, args):
        """Toggle sound system debug messages."""
        self.debug_sound = not self.debug_sound
        self.log(f"Sound debug messages {'enabled' if self.debug_sound else 'disabled'}")
    
    def cmd_debug_physics(self, args):
        """Toggle physics simulation debug messages."""
        self.debug_physics = not self.debug_physics
        self.log(f"Physics debug messages {'enabled' if self.debug_physics else 'disabled'}")

    def cmd_debug_settings(self, args):
        """Toggle settings menu debug messages."""
        self.debug_settings = not self.debug_settings
        self.log(f"Settings menu debug messages {'enabled' if self.debug_settings else 'disabled'}")

    def cmd_toggle_sound_debug(self, args):
        """Toggle SoundManager debug messages."""
        if self.sound_manager:
            try:
                # The toggle_debug method in SoundManager already logs the change
                self.sound_manager.toggle_debug()
            except Exception as e:
                self.log(f"Error toggling sound debug: {e}")
        else:
            self.log("Error: SoundManager instance not available to the console.")
            self.log("Hint: Ensure the SoundManager instance is passed to the console.")

    def cmd_spawn_ball(self, args):
        """Spawn a new ball in the game."""
        if self.game_state and hasattr(self.game_state, 'balls') and hasattr(self.game_state, 'arena'):
            try:
                from ..Ping_GameObjects import BallObject
                new_ball = BallObject(
                    arena_width=self.game_state.arena.width,
                    arena_height=self.game_state.arena.height,
                    scoreboard_height=self.game_state.arena.scoreboard_height,
                    scale_rect=self.game_state.arena.scale_rect,
                    size=20  # Standard ball size
                )
                new_ball.reset_position()
                self.game_state.balls.append(new_ball)
                self.log("Spawned a new ball")
            except Exception as e:
                self.log(f"Error spawning ball: {e}")
        else:
            self.log("Error: Game state not initialized or missing required attributes")

    def handle_event(self, event):
        """Handle keyboard input."""
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.execute_command()
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.current_command = self.current_command[:-1]
                return True
            elif event.key == pygame.K_UP:
                if len(self.command_history) > 0:
                    self.history_index = min(len(self.command_history) - 1, self.history_index + 1)
                    self.current_command = self.command_history[-1 - self.history_index]
                return True
            elif event.key == pygame.K_DOWN:
                if self.history_index > 0:
                    self.history_index -= 1
                    self.current_command = self.command_history[-1 - self.history_index]
                else:
                    self.history_index = -1
                    self.current_command = ""
                return True
            elif event.key == pygame.K_PAGEUP:
                # Calculate maximum scroll offset
                max_scroll = max(0, len(self.wrapped_lines) - self.console_height // self.line_height + 3)
                self.scroll_offset = min(max_scroll, self.scroll_offset + self.console_height // self.line_height)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset = max(0, self.scroll_offset - self.console_height // self.line_height)
                return True
            elif event.key == pygame.K_HOME:
                # Scroll to oldest message
                max_scroll = max(0, len(self.wrapped_lines) - self.console_height // self.line_height + 3)
                self.scroll_offset = max_scroll
                return True
            elif event.key == pygame.K_END:
                # Scroll to newest message
                self.scroll_offset = 0
                return True
            elif event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            elif event.unicode.isprintable():
                self.current_command += event.unicode
                return True
            
        return False

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within the specified width."""
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = font.render(word, True, self.text_color)
            word_width = word_surface.get_width()
            
            if current_width + word_width + (len(current_line) * font.size(' ')[0]) <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def draw(self, screen, WINDOW_WIDTH, WINDOW_HEIGHT):
        """Draw the console if visible."""
        if not self.visible:
            return
            
        # Create console background
        console_surface = pygame.Surface((WINDOW_WIDTH, self.console_height), pygame.SRCALPHA)
        pygame.draw.rect(console_surface, self.bg_color, (0, 0, WINDOW_WIDTH, self.console_height))
        
        # Get font for console text
        font = get_pixel_font(self.font_size)
        self.max_line_width = WINDOW_WIDTH - (2 * self.padding)
        
        # Update wrapped lines cache
        self.wrapped_lines = []
        for message in self.messages:
            wrapped = self.wrap_text(message, font, self.max_line_width)
            self.wrapped_lines.extend(wrapped)
        
        # Calculate max visible lines
        max_lines = (self.console_height - (3 * self.padding) - self.line_height) // self.line_height
        
        # Draw messages with proper scrolling
        # Calculate starting position for text
        y = self.console_height - (2 * self.padding) - (2 * self.line_height)
        
        # Get visible portion of lines based on scroll offset
        start_idx = max(0, len(self.wrapped_lines) - max_lines - self.scroll_offset)
        end_idx = len(self.wrapped_lines) - self.scroll_offset
        self.visible_start_idx = start_idx  # Store for selection calculations
        visible_lines = self.wrapped_lines[start_idx:end_idx]
        
        # Draw lines from bottom to top with selection highlighting
        for i, line in enumerate(reversed(visible_lines)):
            line_idx = end_idx - i - 1
            
            # Check if this line is selected
            if (self.selection_start is not None and
                self.selection_end is not None and
                min(self.selection_start[0], self.selection_end[0]) <= line_idx <=
                max(self.selection_start[0], self.selection_end[0])):
                # Draw selection background
                text_width = font.size(line)[0]
                selection_rect = pygame.Rect(self.padding, y, text_width, self.line_height)
                pygame.draw.rect(console_surface, self.selected_color, selection_rect)
            
            # Draw text
            text = font.render(line, True, self.text_color)
            console_surface.blit(text, (self.padding, y))
            y -= self.line_height
        
        # Draw command line with text wrapping
        prompt = "> " + self.current_command
        if time.time() % 1 < 0.5:  # Blinking cursor
            prompt += "_"
        wrapped_cmd = self.wrap_text(prompt, font, self.max_line_width)
        y = self.console_height - self.padding - (len(wrapped_cmd) * self.line_height)
        for line in wrapped_cmd:
            cmd_text = font.render(line, True, self.text_color)
            console_surface.blit(cmd_text, (self.padding, y))
            y += self.line_height
        
        screen.blit(console_surface, (0, 0))
        
    def start_selection(self, mouse_pos):
        """Start text selection at the given mouse position."""
        line_idx = self._get_line_index(mouse_pos)
        if line_idx is not None:
            self.selection_start = (line_idx, self._get_char_index(mouse_pos, line_idx))
            self.selection_end = self.selection_start
    
    def update_selection(self, mouse_pos):
        """Update the selection end point as the mouse moves."""
        line_idx = self._get_line_index(mouse_pos)
        if line_idx is not None:
            self.selection_end = (line_idx, self._get_char_index(mouse_pos, line_idx))
    
    def copy_selection(self):
        """Copy selected text to clipboard."""
        if (self.selection_start is None or
            self.selection_end is None or
            self.selection_start == self.selection_end):
            return
            
        # Get the selected lines
        start_line = min(self.selection_start[0], self.selection_end[0])
        end_line = max(self.selection_start[0], self.selection_end[0])
        
        selected_text = []
        for i in range(start_line, end_line + 1):
            if 0 <= i < len(self.wrapped_lines):
                selected_text.append(self.wrapped_lines[i])
        
        # Join lines and copy to clipboard
        if selected_text:
            text = '\n'.join(selected_text)
            pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode())
    
    def _get_line_index(self, mouse_pos):
        """Convert mouse Y position to line index."""
        if not self.visible or mouse_pos[1] >= self.console_height:
            return None
            
        # Calculate line index based on direct mouse Y position
        # Account for padding and visible area offset
        visible_line = (mouse_pos[1] - self.padding) // self.line_height
        # Adjust for visible lines
        max_visible_lines = (self.console_height - 3 * self.padding - self.line_height) // self.line_height
        if visible_line >= max_visible_lines:
            return None
        
        # Calculate actual line index from visible position
        line_idx = len(self.wrapped_lines) - max_visible_lines + visible_line - self.scroll_offset
        if 0 <= line_idx < len(self.wrapped_lines):
            return line_idx
        return None
    
    def _get_char_index(self, mouse_pos, line_idx):
        """Convert mouse X position to character index in the line."""
        if 0 <= line_idx < len(self.wrapped_lines):
            font = get_pixel_font(self.font_size)
            relative_x = mouse_pos[0] - self.padding
            line = self.wrapped_lines[line_idx]
            
            # Find character index by measuring text widths
            for i in range(len(line) + 1):
                if font.size(line[:i])[0] >= relative_x:
                    return i
            return len(line)
        return 0

    def clear_selection(self):
        """Clear the current text selection."""
        self.selection_start = None
        self.selection_end = None
        self.dragging = False

# Global console instance
_console = None

def get_console():
    """Get the global console instance."""
    global _console
    if _console is None:
        _console = DebugConsole()
    return _console

def log_message(message):
    """Global function to log messages to the console."""
    console = get_console()
    console.log(message)