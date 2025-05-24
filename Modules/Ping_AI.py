import random
import math
import time
import pygame
from Modules.Ping_Arena import Arena
from Modules.Ping_GameObjects import PaddleObject


class AIConfig:
    """Configuration class for AI parameters to eliminate magic numbers."""
    
    # Paddle positioning
    PADDLE_DISTANCE_FROM_EDGE = 70  # Distance from right edge in pixels
    
    # AI skill parameters
    DEFAULT_ACCURACY = 0.8  # Base AI accuracy (0-1)
    MIN_BALL_SPEED = 500  # Minimum expected ball speed (px/s)
    MAX_BALL_SPEED = 1500  # Maximum expected ball speed (px/s)
    BASE_ERROR_RANGE = 30  # Base prediction error range in pixels
    
    # Spike behavior
    SPIKE_PROBABILITY = 0.3  # Base chance to attempt spike (0-1)
    SPIKE_COOLDOWN_DURATION = 1.5  # Time between spikes in seconds
    
    # Human-like behavior
    BASE_REACTION_TIME = 0.08  # Base reaction time in seconds (reduced for better responsiveness)
    REACTION_TIME_VARIANCE = 0.03  # Variance in reaction time (reduced for consistency)
    MOMENTUM_DECAY_RATE = 0.92  # How quickly momentum decays per second (increased for quicker direction changes)
    MAX_ACCELERATION = 1200  # Maximum paddle acceleration (px/s²) (increased for faster response)
    MOVEMENT_DEAD_ZONE = 1  # Dead zone to prevent jittering (reduced for more precision)
    
    # Threat assessment weights
    DISTANCE_THREAT_WEIGHT = 50  # Weight for distance-based threat
    VELOCITY_THREAT_WEIGHT = 30  # Weight for velocity-based threat
    POSITION_THREAT_WEIGHT = 20  # Weight for position-based threat
    TIME_THREAT_WEIGHT = 25  # Weight for time-to-impact threat
    PROXIMITY_THREAT_WEIGHT = 40  # Weight for proximity threat
    PROXIMITY_THRESHOLD = 100  # Proximity threshold in pixels
    
    # Ball tracking thresholds
    FAR_BALL_THRESHOLD = 0.15  # Fraction of arena width for "far" balls (more aggressive tracking)
    BALL_PAST_PADDLE_MARGIN = 50  # Margin for detecting ball past paddle
    SIGNIFICANT_ERROR_THRESHOLD = 0.5  # Fraction of paddle height for prediction errors
    
    # Spike strategy weights
    SPIKE_STRATEGY_WEIGHTS = {
        'upper_extreme': {'bottom': 100, 'middle': 0, 'top': 0},  # Very high balls
        'upper_mid': {'bottom': 60, 'middle': 30, 'top': 10},     # Mid-high balls
        'lower_mid': {'top': 60, 'middle': 30, 'bottom': 10},     # Mid-low balls
        'lower_extreme': {'top': 100, 'middle': 0, 'bottom': 0}   # Very low balls
    }
    
    # Score-based aggression modifiers
    AGGRESSION_MODIFIERS = {
        'behind_2_plus': 1.5,    # 50% more aggressive when behind by 2+
        'behind_1': 1.2,         # 20% more aggressive when behind by 1
        'tied': 1.0,             # Normal behavior when tied
        'ahead_1': 0.9,          # 10% less aggressive when ahead by 1
        'ahead_2_plus': 0.7      # 30% less aggressive when ahead by 2+
    }
    
    # Prediction physics
    ARENA_HEIGHT_FRACTIONS = {
        'upper_extreme': 0.3,    # Upper 30% of arena
        'lower_extreme': 0.7     # Lower 70% of arena
    }
    
    # Error calculation factors
    ERROR_DISTANCE_WEIGHT = 0.5  # Weight of distance in error calculation
    ERROR_SPEED_WEIGHT = 0.3     # Weight of speed in error calculation
    DISTANCE_NORMALIZATION = 0.75  # Fraction of arena width for distance normalization
    
    # Performance optimization
    PREDICTION_CACHE_DURATION = 0.010  # Cache predictions for ~0.6 frames (10ms) - very responsive
    MIN_BALL_CHANGE_THRESHOLD = 2  # Minimum pixel change to recalculate prediction (very sensitive)
    DEFAULT_PADDLE_HEIGHT = 120  # Default paddle height to avoid dummy object creation
    
    # Advanced features
    POWER_UP_THREAT_WEIGHT = 15  # Weight for power-up proximity threat
    POWER_UP_ATTRACTION_DISTANCE = 150  # Distance at which AI considers power-ups
    OBSTACLE_AVOIDANCE_MARGIN = 20  # Safety margin around obstacles
    MULTI_BALL_SPREAD_FACTOR = 0.3  # How much to spread position for multiple balls
    STRATEGIC_POSITIONING_WEIGHT = 10  # Weight for strategic positioning adjustments

class PaddleAI:
    def __init__(self, level_compiler, config=None):
        """
        Initialize AI paddle with game area dimensions and configurable parameters.
        
        Args:
            level_compiler: Instance of LevelCompiler (MCompile) containing game dimensions and properties
            config: Optional AIConfig instance for customization
        """
        self.level_compiler = level_compiler
        self.config = config or AIConfig()
        
        # Get actual game area dimensions from LevelCompiler (excludes scoreboard)
        self.game_width = level_compiler.width
        self.game_height = level_compiler.height
        
        # Calculate paddle dimensions directly without creating dummy object
        # Use scaled height based on level compiler's scale factor if available
        base_height = self.config.DEFAULT_PADDLE_HEIGHT
        if hasattr(level_compiler, 'scale_rect') and callable(level_compiler.scale_rect):
            # Get scaled height using level compiler's scaling function
            dummy_rect = pygame.Rect(0, 0, 0, base_height)
            scaled_rect = level_compiler.scale_rect(dummy_rect)
            self.paddle_height = scaled_rect.height
        else:
            self.paddle_height = base_height
            
        self.paddle_x = self.game_width - self.config.PADDLE_DISTANCE_FROM_EDGE
        
        # AI skill parameters
        self.accuracy_factor = self.config.DEFAULT_ACCURACY
        self.max_error = self.game_height  # Keep relative to actual game area
        self.min_speed = self.config.MIN_BALL_SPEED
        self.max_speed = self.config.MAX_BALL_SPEED
        
        # Spike behavior parameters
        self.spike_probability = self.config.SPIKE_PROBABILITY
        self.spike_cooldown_duration = self.config.SPIKE_COOLDOWN_DURATION
        self.is_spiking = False
        self.last_spike_time = 0.0

        # Prediction tracking
        self.last_prediction = None
        
        # Reset behavior
        self.is_resetting = False
        
        # Human-like behavior parameters
        self.base_reaction_time = self.config.BASE_REACTION_TIME
        self.reaction_time_variance = self.config.REACTION_TIME_VARIANCE
        self.last_reaction_time = 0.0
        self.target_y_delayed = None
        self.paddle_momentum = 0.0
        self.momentum_decay = self.config.MOMENTUM_DECAY_RATE
        self.max_acceleration = self.config.MAX_ACCELERATION
        
        # Performance optimization caches
        self.prediction_cache = {}  # Cache for ball predictions
        self.last_ball_state = {}   # Track ball state changes
        self.threat_score_cache = {}  # Cache for threat calculations
        self.last_cache_time = 0.0   # Track cache invalidation time
    
    def _get_ball_cache_key(self, ball):
        """Generate a cache key for a ball based on its state."""
        return (
            round(ball.rect.x / 5) * 5,  # Round to nearest 5 pixels for cache efficiency
            round(ball.rect.y / 5) * 5,
            round(ball.ball.velocity_x / 10) * 10,  # Round velocity for cache efficiency
            round(ball.ball.velocity_y / 10) * 10
        )
    
    def _should_invalidate_cache(self, current_time):
        """Check if caches should be invalidated based on time."""
        return current_time - self.last_cache_time > self.config.PREDICTION_CACHE_DURATION
    
    def _invalidate_caches_if_needed(self, current_time):
        """Invalidate caches if enough time has passed."""
        if self._should_invalidate_cache(current_time):
            self.prediction_cache.clear()
            self.threat_score_cache.clear()
            self.last_cache_time = current_time
    
    def _calculate_threat_score(self, ball):
        """
        Calculate a threat score for a ball based on multiple factors.
        Uses caching to improve performance for repeated calculations.
        
        Args:
            ball: Ball object to evaluate
            
        Returns:
            float: Threat score (higher = more threatening, 0 = no threat)
        """
        # Check cache first
        cache_key = self._get_ball_cache_key(ball)
        if cache_key in self.threat_score_cache:
            return self.threat_score_cache[cache_key]
        
        ball_x = ball.rect.x
        ball_y = ball.rect.y
        ball_dx = ball.ball.velocity_x
        ball_dy = ball.ball.velocity_y
        
        # Base threat score starts at 0
        threat_score = 0
        
        # Factor 1: Distance to paddle (closer = more threatening)
        distance_to_paddle = abs(self.paddle_x - ball_x)
        max_distance = self.game_width
        distance_factor = 1 - (distance_to_paddle / max_distance)
        threat_score += distance_factor * self.config.DISTANCE_THREAT_WEIGHT
        
        # Factor 2: Ball velocity towards paddle
        if ball_dx > 0:  # Moving towards AI
            velocity_factor = ball_dx / 1000  # Normalize velocity
            threat_score += velocity_factor * self.config.VELOCITY_THREAT_WEIGHT
        elif ball_dx < 0:  # Moving away from AI
            # Still consider if ball is very close and might bounce back
            if distance_to_paddle < self.game_width * 0.3:
                threat_score += 10  # Reduced but not zero threat
        
        # Factor 3: Ball position - prioritize balls in AI's half
        if ball_x > self.game_width / 2:
            threat_score += self.config.POSITION_THREAT_WEIGHT
        
        # Factor 4: Time to reach paddle (if moving towards it)
        if ball_dx > 0 and ball_x < self.paddle_x:
            time_to_paddle = (self.paddle_x - ball_x) / ball_dx
            # Shorter time = higher threat
            if time_to_paddle < 2.0:  # Less than 2 seconds
                threat_score += (2.0 - time_to_paddle) * self.config.TIME_THREAT_WEIGHT
        
        # Factor 5: Ball near paddle x-position (potential immediate threat)
        x_proximity = abs(ball_x - self.paddle_x)
        if x_proximity < self.config.PROXIMITY_THRESHOLD:
            proximity_factor = (self.config.PROXIMITY_THRESHOLD - x_proximity) / self.config.PROXIMITY_THRESHOLD
            threat_score += proximity_factor * self.config.PROXIMITY_THREAT_WEIGHT
        
        # Cache the result for future use
        final_score = max(0, threat_score)
        self.threat_score_cache[cache_key] = final_score
        return final_score
    
    def _evaluate_power_up_threat(self, level_compiler):
        """
        Evaluate threat/opportunity posed by power-ups in the game area.
        
        Args:
            level_compiler: LevelCompiler object containing power-up information
            
        Returns:
            float: Adjustment to paddle position (-1 to 1) based on power-up evaluation
        """
        if not hasattr(level_compiler, 'power_up') or not level_compiler.power_up:
            return 0.0
        
        power_up = level_compiler.power_up
        power_up_x = power_up.rect.x
        power_up_y = power_up.rect.centery
        
        # Calculate distance from AI paddle to power-up
        distance_to_power_up = abs(power_up_x - self.paddle_x)
        
        # Only consider power-ups within attraction distance
        if distance_to_power_up > self.config.POWER_UP_ATTRACTION_DISTANCE:
            return 0.0
        
        # Calculate positional adjustment toward power-up
        target_center_y = (self.game_height - self.paddle_height) / 2
        power_up_offset = power_up_y - target_center_y
        
        # Scale by distance (closer power-ups have more influence)
        distance_factor = 1 - (distance_to_power_up / self.config.POWER_UP_ATTRACTION_DISTANCE)
        
        # Return normalized adjustment (-1 to 1)
        return (power_up_offset / (self.game_height / 2)) * distance_factor
    
    def _calculate_strategic_positioning(self, all_balls):
        """
        Calculate strategic positioning when multiple balls are present.
        
        Args:
            all_balls: List of all active ball objects
            
        Returns:
            float: Y-position adjustment for strategic coverage
        """
        if not all_balls or len(all_balls) <= 1:
            return 0.0
        
        # Find balls moving toward AI with improved threat detection
        threatening_balls = []
        for ball in all_balls:
            # More comprehensive threat detection
            is_approaching = ball.ball.velocity_x > 0
            is_in_range = ball.rect.x < self.paddle_x and ball.rect.x > self.game_width * 0.2  # Slightly wider range
            
            # Also consider balls that might reach paddle soon even if moving slowly
            if is_approaching and is_in_range:
                time_to_paddle = (self.paddle_x - ball.rect.x) / ball.ball.velocity_x if ball.ball.velocity_x > 0 else float('inf')
                if time_to_paddle < 3.0:  # Within 3 seconds
                    threatening_balls.append(ball)
        
        if len(threatening_balls) <= 1:
            return 0.0
        
        # Calculate coverage area needed
        ball_y_positions = [ball.rect.centery for ball in threatening_balls]
        min_y = min(ball_y_positions)
        max_y = max(ball_y_positions)
        coverage_center = (min_y + max_y) / 2
        
        # Calculate spread factor based on ball distribution
        spread = max_y - min_y
        arena_center = (self.game_height - self.paddle_height) / 2
        
        # Weight positioning toward coverage center, scaled by spread
        position_adjustment = coverage_center - arena_center
        spread_factor = min(spread / (self.game_height * 0.5), 1.0)
        
        return position_adjustment * spread_factor * self.config.MULTI_BALL_SPREAD_FACTOR
    
    def _check_obstacle_collision_risk(self, predicted_y, ball_y, ball_approaching, level_compiler):
        """
        Check if predicted paddle position would create collision risk with obstacles.
        Only avoid if avoidance doesn't compromise ball tracking.
        
        Args:
            predicted_y: Predicted paddle Y position
            ball_y: Current ball Y position (to assess tracking importance)
            ball_approaching: Whether ball is approaching the paddle
            level_compiler: LevelCompiler object containing obstacle information
            
        Returns:
            float: Position adjustment to avoid obstacle collision (or 0 if avoidance is detrimental)
        """
        if not hasattr(level_compiler, 'obstacle') or not level_compiler.obstacle:
            return 0.0
        
        obstacle = level_compiler.obstacle
        paddle_rect = pygame.Rect(
            self.paddle_x - 20,  # Paddle width approximation
            predicted_y,
            20,
            self.paddle_height
        )
        
        # Check for potential collision with margin
        expanded_obstacle = obstacle.rect.inflate(
            self.config.OBSTACLE_AVOIDANCE_MARGIN * 2,
            self.config.OBSTACLE_AVOIDANCE_MARGIN * 2
        )
        
        if paddle_rect.colliderect(expanded_obstacle):
            # Calculate potential avoidance positions
            obstacle_center_y = obstacle.rect.centery
            paddle_center_y = predicted_y + (self.paddle_height / 2)
            
            if paddle_center_y < obstacle_center_y:
                # Option: Move up to avoid obstacle
                avoid_up_pos = obstacle.rect.top - self.config.OBSTACLE_AVOIDANCE_MARGIN - self.paddle_height
                avoidance_adjustment = avoid_up_pos - predicted_y
            else:
                # Option: Move down to avoid obstacle  
                avoid_down_pos = obstacle.rect.bottom + self.config.OBSTACLE_AVOIDANCE_MARGIN
                avoidance_adjustment = avoid_down_pos - predicted_y
            
            # If ball is approaching and avoidance would move paddle significantly away from ball,
            # don't avoid - better to risk obstacle collision than miss the ball
            if ball_approaching:
                distance_from_ball_current = abs(predicted_y + (self.paddle_height / 2) - ball_y)
                distance_from_ball_avoided = abs((predicted_y + avoidance_adjustment) + (self.paddle_height / 2) - ball_y)
                
                # If avoidance would move us much further from the ball, don't avoid
                if distance_from_ball_avoided > distance_from_ball_current * 2:
                    return 0.0
            
            return avoidance_adjustment
        
        return 0.0
    
    def _simulate_reaction_time(self, current_time, ball_changed_significantly=False):
        """
        Simulate human reaction time and delayed recognition of ball state changes.
        
        Args:
            current_time: Current game time
            ball_changed_significantly: Whether ball trajectory changed significantly
            
        Returns:
            bool: Whether AI should update its target (reaction time elapsed)
        """
        # Generate new reaction time if ball changed or this is first reaction
        if ball_changed_significantly or self.last_reaction_time == 0.0:
            # Vary reaction time based on human-like factors
            reaction_delay = self.base_reaction_time + random.uniform(
                -self.reaction_time_variance, 
                self.reaction_time_variance
            )
            self.last_reaction_time = current_time + reaction_delay
            return False  # Still reacting, don't update target yet
        
        # Check if reaction time has elapsed
        return current_time >= self.last_reaction_time
    
    def _apply_momentum_physics(self, current_y, target_y, frame_time):
        """
        Apply momentum and acceleration physics to paddle movement.
        
        Args:
            current_y: Current paddle position
            target_y: Target paddle position
            frame_time: Time since last frame
            
        Returns:
            float: New paddle position with momentum applied
        """
        # Calculate desired acceleration toward target
        distance_to_target = target_y - current_y
        
        # Apply momentum decay
        self.paddle_momentum *= (self.momentum_decay ** frame_time)
        
        # Calculate acceleration needed to reach target
        if abs(distance_to_target) > self.config.MOVEMENT_DEAD_ZONE:
            # Apply gentler damping only when very close to target to prevent overshooting
            if abs(distance_to_target) < self.paddle_height * 0.5:  # Only damp when very close
                distance_factor = max(0.3, abs(distance_to_target) / (self.paddle_height * 0.5))  # Min 30% responsiveness
            else:
                distance_factor = 1.0  # Full responsiveness when not very close
            
            desired_acceleration = distance_to_target * 5 * distance_factor  # Increased base responsiveness
            
            # Enhanced braking when momentum and target are in opposite directions
            if (self.paddle_momentum > 0 and distance_to_target < 0) or (self.paddle_momentum < 0 and distance_to_target > 0):
                desired_acceleration *= 1.8  # Stronger braking force
            
            # Clamp acceleration
            desired_acceleration = max(-self.max_acceleration, 
                                     min(desired_acceleration, self.max_acceleration))
            
            # Apply acceleration to momentum
            self.paddle_momentum += desired_acceleration * frame_time
        
        # Apply momentum to position
        new_position = current_y + (self.paddle_momentum * frame_time)
        
        return new_position
    
    def predict_intersection(self, ball_x, ball_y, ball_dx, ball_dy, all_balls=None):
        """
        Make a short-term prediction of ball movement to simulate human-like reaction.
        Uses caching to avoid recalculating predictions for similar ball states.
        
        Args:
            ball_x: Current x position of the ball
            ball_y: Current y position of the ball
            ball_dx: Ball's velocity in x direction
            ball_dy: Ball's velocity in y direction
            all_balls: List of all active balls (optional)
            
        Returns:
            float: Predicted y-coordinate where the AI should move towards
        """
        # Early exit if ball is moving away and very far - be more aggressive about tracking
        if ball_dx <= 0 and ball_x < self.game_width * 0.3:  # Only give up if ball is very far and moving away
            return (self.game_height - self.paddle_height) / 2
        # If there are multiple balls, assess all potential threats
        # Override passed ball parameters with most threatening ball
        if all_balls and len(all_balls) > 1:  # Only multi-ball logic if actually multiple balls
            most_threatening_ball = None
            highest_threat_score = -1
            
            # Prioritize balls that are approaching and close
            for current_ball in all_balls:
                threat_score = self._calculate_threat_score(current_ball)
                
                # Give bonus to balls that are very close to the paddle
                distance_to_paddle = abs(self.paddle_x - current_ball.rect.x)
                if distance_to_paddle < self.game_width * 0.2:  # Very close
                    threat_score *= 1.5
                
                if threat_score > highest_threat_score:
                    highest_threat_score = threat_score
                    most_threatening_ball = current_ball
            
            # Use most threatening ball if found, otherwise use passed parameters
            if most_threatening_ball and highest_threat_score > 0:
                ball_x = most_threatening_ball.rect.x
                ball_y = most_threatening_ball.rect.y
                ball_dx = most_threatening_ball.ball.velocity_x
                ball_dy = most_threatening_ball.ball.velocity_y
            # If no threatening ball found from list, fall back to passed parameters

        # Check prediction cache before expensive calculations
        prediction_key = (
            round(ball_x / 5) * 5,  # Round for cache efficiency
            round(ball_y / 5) * 5,
            round(ball_dx / 10) * 10,
            round(ball_dy / 10) * 10
        )
        
        if prediction_key in self.prediction_cache:
            return self.prediction_cache[prediction_key]

        # Handle edge case where ball has no horizontal velocity
        if ball_dx == 0:
            return (self.game_height - self.paddle_height) / 2
        
        # Only return to center if ball is very far away and moving away
        if ball_x < self.game_width * self.config.FAR_BALL_THRESHOLD and ball_dx <= 0:
            return (self.game_height - self.paddle_height) / 2
        
        # Handle case where ball is past paddle and moving away (already scored)
        if ball_dx < 0 and ball_x >= self.paddle_x + self.config.BALL_PAST_PADDLE_MARGIN:
            return (self.game_height - self.paddle_height) / 2

        # Calculate time until ball reaches paddle's x position
        time_to_paddle = (self.paddle_x - ball_x) / ball_dx
        
        # Additional safety check for negative time (shouldn't happen with above checks)
        if time_to_paddle < 0:
            return (self.game_height - self.paddle_height) / 2
            
        predicted_y = ball_y + (ball_dy * time_to_paddle)
        
        # Handle wall bounces that might occur before reaching paddle
        # Use physics-based bounce simulation with proper bounds checking
        playable_height = self.game_height
        
        # Normalize position relative to game area
        relative_y = predicted_y
        
        # Calculate number of complete bounces needed
        if ball_dy != 0 and playable_height > 0:
            # Determine how many times the ball would cross the playable area
            cycles = abs(relative_y) / playable_height
            complete_cycles = int(cycles)
            remainder = cycles - complete_cycles
            
            # Apply bounce physics based on direction and position
            if ball_dy > 0:  # Ball moving downward
                if complete_cycles % 2 == 0:
                    # Even number of bounces - ball maintains direction
                    final_relative_y = remainder * playable_height
                else:
                    # Odd number of bounces - ball reverses direction
                    final_relative_y = playable_height - (remainder * playable_height)
            else:  # Ball moving upward
                if complete_cycles % 2 == 0:
                    # Even number of bounces - ball maintains direction  
                    final_relative_y = playable_height - (remainder * playable_height)
                else:
                    # Odd number of bounces - ball reverses direction
                    final_relative_y = remainder * playable_height
            
            # Convert back to absolute coordinates
            predicted_y = final_relative_y
        
        # Clamp to valid range as safety check (before adding error)
        predicted_y = max(0, min(predicted_y, self.game_height))
        
        # Add human error based on distance and speed with improved calculation
        # Distance factor: normalized to 0-1 range, higher for farther distances
        distance_factor = min(abs(self.paddle_x - ball_x) / (self.game_width * self.config.DISTANCE_NORMALIZATION), 1.0)
        
        # Speed factor: normalized based on realistic speed range
        speed_factor = min(max(abs(ball_dx) - self.min_speed, 0) / (self.max_speed - self.min_speed), 1.0)
        
        # Base error range scales with accuracy (perfect accuracy = no error)
        base_error_range = self.config.BASE_ERROR_RANGE * (1 - self.accuracy_factor)
        
        # Combine factors: more error for distant, fast balls
        error_multiplier = 1 + (distance_factor * self.config.ERROR_DISTANCE_WEIGHT) + (speed_factor * self.config.ERROR_SPEED_WEIGHT)
        final_error_range = base_error_range * error_multiplier
        
        # Apply random error within calculated range
        error = random.uniform(-final_error_range, final_error_range)
        predicted_y += error
        
        # Store prediction for failure tracking
        self.last_prediction = predicted_y
        
        # Ensure prediction stays within bounds and cache result
        # Account for paddle centering - the prediction should be the ball Y position,
        # but we need to ensure the resulting paddle position will be valid
        min_ball_y = self.paddle_height / 2
        max_ball_y = self.game_height - (self.paddle_height / 2)
        final_prediction = min(max(predicted_y, min_ball_y), max_ball_y)
        self.prediction_cache[prediction_key] = final_prediction
        return final_prediction

    def should_attempt_spike(self, ball_x, ball_dx, score_ai=0, score_opponent=0):
        """Decide whether to attempt a spike based on ball position, trajectory, and game state."""
        current_time = time.time()
        
        # Check time-based cooldown
        if current_time - self.last_spike_time < self.spike_cooldown_duration:
            return False
            
        # Only consider spiking when ball is approaching
        if ball_dx <= 0:
            self.is_spiking = False
            return False
            
        # Calculate base spike probability based on distance
        distance_factor = max(0, 1 - (ball_x - self.game_width/2) / (self.game_width/2))
        
        # Adjust spike probability based on game state
        score_difference = score_ai - score_opponent
        
        # More aggressive when behind, more conservative when ahead
        if score_difference < -2:
            aggression_modifier = self.config.AGGRESSION_MODIFIERS['behind_2_plus']
        elif score_difference < 0:
            aggression_modifier = self.config.AGGRESSION_MODIFIERS['behind_1']
        elif score_difference > 2:
            aggression_modifier = self.config.AGGRESSION_MODIFIERS['ahead_2_plus']
        elif score_difference > 0:
            aggression_modifier = self.config.AGGRESSION_MODIFIERS['ahead_1']
        else:
            aggression_modifier = self.config.AGGRESSION_MODIFIERS['tied']
        
        # Calculate final spike chance
        spike_chance = self.spike_probability * distance_factor * aggression_modifier
        
        if random.random() < spike_chance:
            self.is_spiking = True
            self.last_spike_time = current_time
            return True
        return False

    def calculate_spike_position(self, predicted_y, ball_y):
        """Calculate strategic position to hit the ball for a spike based on optimal angles."""
        # Determine best spike strategy based on ball position and arena geometry
        center_y = self.game_height / 2
        
        # Calculate which spike angle would be most effective
        if predicted_y < center_y:
            # Ball is in upper half - prefer downward spikes for sharp angles
            if predicted_y < self.game_height * self.config.ARENA_HEIGHT_FRACTIONS['upper_extreme']:
                # Very high ball - use extreme strategy
                weights = self.config.SPIKE_STRATEGY_WEIGHTS['upper_extreme']
                strategy = random.choices(
                    list(weights.keys()), 
                    weights=list(weights.values()), 
                    k=1
                )[0]
            else:
                # Mid-high ball - weighted choice favoring downward angles
                weights = self.config.SPIKE_STRATEGY_WEIGHTS['upper_mid']
                strategy = random.choices(
                    list(weights.keys()), 
                    weights=list(weights.values()), 
                    k=1
                )[0]
        else:
            # Ball is in lower half - prefer upward spikes for sharp angles
            if predicted_y > self.game_height * self.config.ARENA_HEIGHT_FRACTIONS['lower_extreme']:
                # Very low ball - use extreme strategy
                weights = self.config.SPIKE_STRATEGY_WEIGHTS['lower_extreme']
                strategy = random.choices(
                    list(weights.keys()), 
                    weights=list(weights.values()), 
                    k=1
                )[0]
            else:
                # Mid-low ball - weighted choice favoring upward angles
                weights = self.config.SPIKE_STRATEGY_WEIGHTS['lower_mid']
                strategy = random.choices(
                    list(weights.keys()), 
                    weights=list(weights.values()), 
                    k=1
                )[0]
        
        # Apply chosen strategy with refined positioning
        if strategy == 'top':
            # Hit with top quarter for sharp upward angle
            target_y = predicted_y - (self.paddle_height * 0.8)
        elif strategy == 'bottom':
            # Hit with bottom quarter for sharp downward angle
            target_y = predicted_y - (self.paddle_height * 0.2)
        else:  # middle
            # Hit with center for controlled straight shot
            target_y = predicted_y - (self.paddle_height * 0.5)
        
        # Ensure spike position stays within bounds
        target_y = max(0, min(target_y, self.game_height - self.paddle_height))
        return target_y

    def reset_position(self):
        """Start moving paddle back to center position."""
        self.is_resetting = True

    def calculate_movement_speed(self, current_y, target_y, max_movement):
        """Calculate the optimal movement speed based on distance to target."""
        distance = target_y - current_y
        if abs(distance) < max_movement:
            return distance  # Move exact distance if close
        return math.copysign(max_movement, distance)  # Move at max speed in correct direction

    def move_paddle(self, ball_x, ball_y, ball_dx, ball_dy, paddle_y, paddle_movement, ball_frozen, all_balls=None, score_ai=0, score_opponent=0, frame_time=1/60.0):
        """Calculate the next paddle position based on game state and ball trajectory."""
        center_y = int((self.game_height - self.paddle_height) // 2)

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
        if self.last_prediction is not None and ball_x > self.paddle_x + self.config.BALL_PAST_PADDLE_MARGIN:
            actual_y = ball_y
            prediction_error = abs(actual_y - self.last_prediction)
            if prediction_error > self.paddle_height * self.config.SIGNIFICANT_ERROR_THRESHOLD:
                print(f"AI Prediction Failed! Error: {prediction_error:.1f}px")
                print(f"Predicted Y: {self.last_prediction:.1f}, Actual Y: {actual_y:.1f}")
            self.last_prediction = None

        # Simulate human-like reaction time and target updating
        current_time = time.time()
        
        # Invalidate caches if needed for performance optimization
        self._invalidate_caches_if_needed(current_time)
        
        can_react = self._simulate_reaction_time(current_time, False)  # TODO: detect ball changes
        
        # Override reaction time for close balls to be more responsive
        ball_very_close = ball_dx > 0 and ball_x > (self.paddle_x - self.game_width * 0.25)  # Wider range for immediate response
        
        # Only update target if reaction time allows, no delayed target exists, or ball is very close
        if can_react or self.target_y_delayed is None or ball_very_close:
            # Get predicted intersection considering all balls
            predicted_y = self.predict_intersection(ball_x, ball_y, ball_dx, ball_dy, all_balls)
            
            # Update spike status and get target position
            if self.should_attempt_spike(ball_x, ball_dx, score_ai, score_opponent):
                target_y = self.calculate_spike_position(predicted_y, ball_y)
            elif self.is_spiking and ball_dx > 0:
                # Continue spike if ball is still approaching
                target_y = self.calculate_spike_position(predicted_y, ball_y)
            else:
                # Reset spike status and do normal tracking
                self.is_spiking = False
                target_y = predicted_y - (self.paddle_height / 2)
            
            # Apply advanced features adjustments
            if self.level_compiler:
                # Apply power-up awareness
                power_up_adjustment = self._evaluate_power_up_threat(self.level_compiler)
                power_up_offset = power_up_adjustment * self.config.POWER_UP_THREAT_WEIGHT
                target_y += power_up_offset
                
                # Apply strategic positioning for multiple balls
                strategic_adjustment = self._calculate_strategic_positioning(all_balls)
                target_y += strategic_adjustment * self.config.STRATEGIC_POSITIONING_WEIGHT
                
                # Check and avoid obstacle collisions (only if it doesn't compromise ball tracking)
                ball_approaching = ball_dx > 0  # Ball moving toward AI paddle
                obstacle_avoidance = self._check_obstacle_collision_risk(target_y, ball_y, ball_approaching, self.level_compiler)
                target_y += obstacle_avoidance
            
            # Ensure target stays within bounds
            target_y = max(0, min(target_y, self.game_height - self.paddle_height))
            
            # Store delayed target
            self.target_y_delayed = target_y
        
        # Use delayed target for movement (simulates human reaction delay)
        if self.target_y_delayed is not None:
            # Apply momentum physics for human-like movement
            new_y = self._apply_momentum_physics(paddle_y, self.target_y_delayed, frame_time)
        else:
            # Fallback to simple movement if no target set
            new_y = paddle_y
        
        # Final validation to ensure returned position is within bounds
        # This prevents any edge cases from causing out-of-bounds positions
        final_y = max(0, min(new_y, self.game_height - self.paddle_height))
        
        return final_y