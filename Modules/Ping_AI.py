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
        self.min_speed = 500  # Minimum ball speed (should match Ball class)
        
        # Spike behavior parameters
        self.spike_probability = 0.3  # 30% chance to attempt spike
        self.spike_cooldown = 0  # Cooldown timer for spikes
        self.is_spiking = False  # Current spike attempt status

        # Prediction tracking
        self.last_prediction = None  # Store last predicted y-position
        
        # Reset behavior
        self.is_resetting = False  # Whether paddle is moving back to center
    
    def predict_intersection(self, ball_x, ball_y, ball_dx, ball_dy, all_balls=None):
        """
        Make a short-term prediction of ball movement to simulate human-like reaction.
        
        Args:
            ball_x: Current x position of the ball
            ball_y: Current y position of the ball
            ball_dx: Ball's velocity in x direction
            ball_dy: Ball's velocity in y direction
            all_balls: List of all active balls (optional)
            
        Returns:
            float: Predicted y-coordinate where the AI should move towards
        """
        # If there are multiple balls, focus on the closest threatening ball
        if all_balls:
            closest_ball = None
            min_time_to_paddle = float('inf')
            
            for current_ball in all_balls:
                if current_ball.ball.velocity_x > 0:  # Only consider balls moving towards AI
                    distance = self.paddle_x - current_ball.rect.x
                    if distance > 0:  # Ball is to the left of paddle
                        time_to_paddle = distance / current_ball.ball.velocity_x
                        if time_to_paddle < min_time_to_paddle:
                            min_time_to_paddle = time_to_paddle
                            closest_ball = current_ball
            
            if closest_ball:
                ball_x = closest_ball.rect.x
                ball_y = closest_ball.rect.y
                ball_dx = closest_ball.ball.velocity_x
                ball_dy = closest_ball.ball.velocity_y

        # Only react to ball when it's in the right half and moving towards paddle
        if ball_x <= self.arena.width / 2 or ball_dx <= 0:
            return (self.arena.height - self.paddle_height) / 2

        # Calculate time until ball reaches paddle's x position
        time_to_paddle = (self.paddle_x - ball_x) / ball_dx
        predicted_y = ball_y + (ball_dy * time_to_paddle)
        
        # Handle wall bounces that might occur before reaching paddle
        bounces = 0
        while bounces < 4:  # Limit bounce calculations
            if predicted_y < self.arena.scoreboard_height:
                predicted_y = self.arena.scoreboard_height + (self.arena.scoreboard_height - predicted_y)
                bounces += 1
            elif predicted_y > self.arena.height:
                predicted_y = self.arena.height - (predicted_y - self.arena.height)
                bounces += 1
            else:
                break
        
        # Add human error based on distance and speed
        distance_factor = (self.paddle_x - ball_x) / (self.arena.width / 2)
        speed_factor = abs(ball_dx) / self.min_speed  # Normalize based on min ball speed
        error = random.uniform(-20, 20) * distance_factor * (1 - self.accuracy_factor) * (1 + speed_factor)
        predicted_y += error
        
        # Store prediction for failure tracking
        self.last_prediction = predicted_y
        
        # Ensure prediction stays within bounds
        return min(max(predicted_y, self.arena.scoreboard_height), self.arena.height)

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

    def reset_position(self):
        """Start moving paddle back to center position."""
        self.is_resetting = True

    def calculate_movement_speed(self, current_y, target_y, max_movement):
        """Calculate the optimal movement speed based on distance to target."""
        distance = target_y - current_y
        if abs(distance) < max_movement:
            return distance  # Move exact distance if close
        return math.copysign(max_movement, distance)  # Move at max speed in correct direction

    def move_paddle(self, ball_x, ball_y, ball_dx, ball_dy, paddle_y, paddle_movement, ball_frozen, all_balls=None):
        """Calculate the next paddle position based on game state and ball trajectory."""
        center_y = (self.arena.height - self.paddle_height) // 2

        # If resetting to center, ignore all other states
        if self.is_resetting:
            movement = self.calculate_movement_speed(paddle_y, center_y, paddle_movement)
            new_y = paddle_y + movement
            
            # Check if we've reached center (within 2 pixels)
            if abs(new_y - center_y) < 2:
                self.is_resetting = False
                return center_y
            return new_y

        # If ball is frozen during respawn and we're at center, stay there
        if ball_frozen and not self.is_resetting and abs(paddle_y - center_y) < 2:
            return center_y

        # Check for failed prediction when ball gets past paddle
        if self.last_prediction is not None and ball_x > self.paddle_x + 20:  # Ball is past paddle
            actual_y = ball_y
            prediction_error = abs(actual_y - self.last_prediction)
            if prediction_error > self.paddle_height / 2:  # Significant error
                print(f"AI Prediction Failed! Error: {prediction_error:.1f}px")
                print(f"Predicted Y: {self.last_prediction:.1f}, Actual Y: {actual_y:.1f}")
            self.last_prediction = None

        # Get predicted intersection considering all balls
        predicted_y = self.predict_intersection(ball_x, ball_y, ball_dx, ball_dy, all_balls)
        
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