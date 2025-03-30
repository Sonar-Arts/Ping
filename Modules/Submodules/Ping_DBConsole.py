import pygame
import time
from ..Submodules.Ping_Fonts import get_pixel_font
from collections import deque

class DebugConsole:
    def __init__(self):
        # Message storage
        self.messages = deque(maxlen=100)  # Keep last 100 messages
        self.visible = False
        self.toggle_time = 0
        self.scroll_offset = 0
        
        # Visual settings
        self.bg_color = (0, 0, 0, 200)  # Semi-transparent background
        self.text_color = (0, 255, 0)  # Green text
        self.font_size = 16
        self.line_height = 20
        self.padding = 10
        self.console_height = 200
        
        # Command handling
        self.current_command = ""
        self.command_history = deque(maxlen=20)
        self.history_index = -1
        
        # Commands dictionary
        self.commands = {
            'help': self.cmd_help,
            'clear': self.cmd_clear,
            'toggle_shader': self.cmd_toggle_shader
        }
    
    def update(self, events):
        """Update console state based on events."""
        current_time = time.time()
        
        for event in events:
            # Handle backtick toggle first
            if event.type == pygame.KEYDOWN and event.key == 96:  # ASCII for backtick
                if current_time - self.toggle_time > 0.2:  # Debounce
                    self.visible = not self.visible
                    self.toggle_time = current_time
                    self.log(f"Console {'activated' if self.visible else 'deactivated'}")
                return True

        # Only handle other events if console is visible
        if self.visible:
            for event in events:
                if self.handle_event(event):
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
        for cmd in self.commands:
            self.log(f"  {cmd}")
    
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
                self.scroll_offset = min(len(self.messages), self.scroll_offset + 5)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_offset = max(0, self.scroll_offset - 5)
                return True
            elif event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            elif event.unicode.isprintable():
                self.current_command += event.unicode
                return True
            
        return False

    def draw(self, screen, WINDOW_WIDTH, WINDOW_HEIGHT):
        """Draw the console if visible."""
        if not self.visible:
            return
            
        # Create console background
        console_surface = pygame.Surface((WINDOW_WIDTH, self.console_height), pygame.SRCALPHA)
        pygame.draw.rect(console_surface, self.bg_color, (0, 0, WINDOW_WIDTH, self.console_height))
        
        # Get font for console text
        font = get_pixel_font(self.font_size)
        
        # Draw messages (moved up to leave space for command line)
        y = self.console_height - (2 * self.padding) - (2 * self.line_height)  # Start higher to leave room for command
        visible_messages = list(self.messages)[-10 - self.scroll_offset:]
        for message in reversed(visible_messages[-10:]):  # Show last 10 messages
            text = font.render(message, True, self.text_color)
            console_surface.blit(text, (self.padding, y))
            y -= self.line_height
        
        # Draw command line (at the bottom with extra padding)
        prompt = "> " + self.current_command
        if time.time() % 1 < 0.5:  # Blinking cursor
            prompt += "_"
        cmd_text = font.render(prompt, True, self.text_color)
        console_surface.blit(cmd_text, (self.padding, self.console_height - self.padding - self.line_height))
        
        screen.blit(console_surface, (0, 0))

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