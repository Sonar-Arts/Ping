import random
import math
from Modules.Ping_Arena import Arena
from Modules.Ping_GameObjects import PaddleObject

class PaddleAI:
    def __init__(self, arena):
        """
        Initialize AI paddle with arena dimensions and configurable parameters.
        
        Args:
            arena: Instance of Arena class containing game dimensions and properties
        """
        self.arena = arena
        # Create a dummy paddle to get standard dimensions and positions
        dummy_paddle = PaddleObject(
            x=0,
            y=0,
            width=20,
            height=120,
            arena_width=arena.width,
            arena_height=arena.height,
            scoreboard_height=arena.scoreboard_height,
            scale_rect=arena.scale_rect,
            is_left_paddle=False
        )
        self.paddle_height = dummy_paddle.rect.height
        self.paddle_x = self.arena.width - 70  # Fixed x-position (70px from right)
        self.accuracy_factor = 0.8  # AI accuracy (0-1)
        self.max_error = arena.height  # Maximum possible prediction error
        
        # Spike behavior parameters
        self.spike_probability = 0.3  # 30% chance to attempt spike
        self.spike_cooldown = 0  # Cooldown timer for spikes
        self.is_spiking = False  # Current spike attempt status
    
    def predict_intersection(self, ball_x, ball_y, ball_dx, ball_dy):
        """
        Predict where the ball will intersect with the AI paddle's vertical line.
        
        Args:
            ball_x: Current x position of the ball
            ball_y: Current y position of the ball
            ball_dx: Ball's velocity in x direction
            ball_dy: Ball's velocity in y direction
            
        Returns:
            float: Predicted y-coordinate where the ball will intersect paddle
        """
        # If ball is not moving towards paddle, maintain current position
        if ball_dx <= 0:
            return ball_y

        # Calculate time until intersection
        if ball_dx != 0:  # Avoid division by zero
            time_to_paddle = (self.paddle_x - ball_x) / ball_dx
            
            # Calculate ball's y position at intersection point
            predicted_y = ball_y + (ball_dy * time_to_paddle)
            
            # Handle bounces off walls
            arena_playable_height = self.arena.height - self.arena.scoreboard_height
            relative_y = predicted_y - self.arena.scoreboard_height
            
            # Number of full bounces
            bounces = int(abs(relative_y) / arena_playable_height)
            
            # Final position after bounces
            final_relative_y = relative_y % arena_playable_height
            if bounces % 2 == 1:  # Odd number of bounces means ball is going opposite direction
                final_relative_y = arena_playable_height - final_relative_y
                
            final_y = self.arena.scoreboard_height + final_relative_y
            
            # Add slight randomness to simulate human error
            error = random.uniform(-10, 10) * (1 - self.accuracy_factor)
            final_y += error
            
            # Ensure we stay within valid bounds
            return min(max(final_y, self.arena.scoreboard_height), self.arena.height)
            
        return ball_y

    def should_attempt_spike(self, ball_x, ball_dx):
        """Decide whether to attempt a spike based on ball position and trajectory."""
        if self.spike_cooldown > 0:
            self.spike_cooldown -= 1
            return False
            
        # Only consider spiking when ball is approaching
        if ball_dx <= 0:
            self.is_spiking = False
            return False
            
        # More likely to spike when ball is closer
        distance_factor = 1 - (ball_x - self.arena.width/2) / (self.arena.width/2)
        spike_chance = self.spike_probability * distance_factor
        
        if random.random() < spike_chance:
            self.is_spiking = True
            self.spike_cooldown = 60  # Set cooldown (about 1 second at 60 FPS)
            return True
        return False

    def calculate_spike_position(self, predicted_y):
        """Calculate strategic position to hit the ball for a spike."""
        # Choose from multiple spike strategies
        strategy = random.choice(['top', 'bottom', 'middle', 'surprise'])
        
        if strategy == 'top':
            # Hit with top quarter for sharp downward angle
            return predicted_y - (self.paddle_height * 0.75)
        elif strategy == 'bottom':
            # Hit with bottom quarter for sharp upward angle
            return predicted_y - (self.paddle_height * 0.25)
        elif strategy == 'middle':
            # Hit with center for straight shot
            return predicted_y - (self.paddle_height * 0.5)
        else:  # surprise
            # Random position for unpredictable angles
            return predicted_y - (self.paddle_height * random.uniform(0.2, 0.8))

    def calculate_movement_speed(self, current_y, target_y, max_movement):
        """Calculate the optimal movement speed based on distance to target."""
        distance = target_y - current_y
        if abs(distance) < max_movement:
            return distance  # Move exact distance if close
        return math.copysign(max_movement, distance)  # Move at max speed in correct direction

    def move_paddle(self, ball_x, ball_y, ball_dx, ball_dy, paddle_y, paddle_movement):
        """Calculate the next paddle position based on ball trajectory prediction."""
        # Get predicted intersection
        predicted_y = self.predict_intersection(ball_x, ball_y, ball_dx, ball_dy)
        
        # Update spike status and get target position
        if self.should_attempt_spike(ball_x, ball_dx):
            target_y = self.calculate_spike_position(predicted_y)
        elif self.is_spiking and ball_dx > 0:
            # Continue spike if ball is still approaching
            target_y = self.calculate_spike_position(predicted_y)
        else:
            # Reset spike status and do normal tracking
            self.is_spiking = False
            target_y = predicted_y - (self.paddle_height / 2)
        
        # Ensure target stays within bounds
        target_y = max(self.arena.scoreboard_height,
                      min(target_y, self.arena.height - self.paddle_height))
        
        # Calculate and apply movement
        movement = self.calculate_movement_speed(paddle_y, target_y, paddle_movement)
        return paddle_y + movement