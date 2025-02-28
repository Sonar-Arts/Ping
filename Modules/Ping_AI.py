import random
from Modules.Ping_Arena import Arena

class PaddleAI:
    def __init__(self, arena):
        """
        Initialize AI paddle with arena dimensions and configurable parameters.
        
        Args:
            arena: Instance of Arena class containing game dimensions and properties
        """
        self.arena = arena
        self.paddle_height = 120  # Standard paddle height
        self.paddle_x = arena.width - 70  # Fixed x-position (70px from right)
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
        # Only predict if ball is moving towards paddle
        if ball_dx <= 0:
            # Ball moving away, just track ball's current y position
            return ball_y
            
        # Calculate time to intersection using equation of motion
        time_to_intersection = (self.paddle_x - ball_x) / ball_dx
        
        # Calculate future y position
        future_y = ball_y + (ball_dy * time_to_intersection)
        
        # Account for bounces off top and bottom walls
        effective_y = future_y
        scoreboard = self.arena.scoreboard_height
        if future_y < scoreboard or future_y > self.arena.height:
            # Calculate number of bounces
            bounces = abs(future_y - max(scoreboard, min(future_y, self.arena.height))) // (self.arena.height - scoreboard)
            if bounces % 2 == 0:
                # Even number of bounces, use modulo to find final position
                effective_y = scoreboard + ((future_y - scoreboard) % (self.arena.height - scoreboard))
            else:
                # Odd number of bounces, reverse direction
                effective_y = self.arena.height - ((future_y - scoreboard) % (self.arena.height - scoreboard))
        
        # Add prediction error based on accuracy factor
        error_term = random.uniform(-self.max_error, self.max_error) * (1 - self.accuracy_factor)
        predicted_y = effective_y + error_term
        
        # Ensure prediction stays within valid range
        return max(self.arena.scoreboard_height, min(predicted_y, self.arena.height))

    def should_attempt_spike(self, ball_x):
        """Decide whether to attempt a spike based on ball position and probability."""
        if self.spike_cooldown > 0:
            self.spike_cooldown -= 1
            return False
            
        # Only consider spiking when ball is approaching and in front half of arena
        if ball_x < self.arena.width / 2 or self.is_spiking:
            return False
            
        # Random chance to attempt spike
        if random.random() < self.spike_probability:
            self.is_spiking = True
            self.spike_cooldown = 60  # Set cooldown (about 1 second at 60 FPS)
            return True
        return False

    def calculate_spike_position(self, ball_y):
        """Calculate optimal position to hit the ball for a spike."""
        # Try to hit the ball near the top or bottom of the paddle
        # This creates a steep angle for the spike
        if ball_y < self.arena.height / 2:
            return ball_y - (self.paddle_height * 0.8)  # Hit near bottom of paddle
        else:
            return ball_y - (self.paddle_height * 0.2)  # Hit near top of paddle

    def calculate_movement_speed(self, current_y, target_y, paddle_movement):
        """Calculate proportional movement speed based on distance to target."""
        distance = abs(target_y - current_y)
        if distance < paddle_movement:
            return distance  # Move exact distance if close
        return paddle_movement  # Use max speed if far

    def move_paddle(self, ball_x, ball_y, ball_dx, ball_dy, paddle_y, paddle_movement):
        """
        Calculate the next paddle position based on ball trajectory prediction.
        
        Args:
            ball_x: Current x position of the ball
            ball_y: Current y position of the ball
            ball_dx: Ball's velocity in x direction
            ball_dy: Ball's velocity in y direction
            paddle_y: Current Y coordinate of the AI paddle
            paddle_movement: Maximum amount the paddle can move this frame
            
        Returns:
            float: New Y position for the paddle
        """
        # Check if we should attempt a spike
        if not self.is_spiking and self.should_attempt_spike(ball_x):
            # Start spike attempt
            target_y = self.calculate_spike_position(ball_y)
        else:
            # Normal ball tracking
            predicted_y = self.predict_intersection(ball_x, ball_y, ball_dx, ball_dy)
            if self.is_spiking and abs(ball_x - self.paddle_x) > self.arena.width / 4:
                # Reset spiking if ball is too far
                self.is_spiking = False
                target_y = predicted_y - (self.paddle_height / 2)
            elif self.is_spiking:
                # Continue spike attempt
                target_y = self.calculate_spike_position(predicted_y)
            else:
                # Normal paddle center positioning
                target_y = predicted_y - (self.paddle_height / 2)

        # Calculate movement speed based on distance
        speed = self.calculate_movement_speed(paddle_y, target_y, paddle_movement)
        
        # Move towards target position
        if target_y > paddle_y and paddle_y + self.paddle_height < self.arena.height:
            new_y = paddle_y + speed
            return min(new_y, self.arena.height - self.paddle_height)
        elif target_y < paddle_y and paddle_y > self.arena.scoreboard_height:
            new_y = paddle_y - speed
            return max(self.arena.scoreboard_height, new_y)
        
        return paddle_y  # Keep current position if no movement needed