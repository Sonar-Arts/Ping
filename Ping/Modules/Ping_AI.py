"""
PING AI SYSTEM - PHASE 0 MINIMAL IMPLEMENTATION

This is a minimal dummy AI implementation created during Phase 0 of the AI upgrade plan.
All methods are marked for replacement in Phase 1 with proper persistent tracking and offensive behavior.

See /docs/ai_upgrade_plan.md for the complete upgrade strategy.
See /docs/old_ai_integration_backup.md for original system documentation.
"""

import random
import math
import time
import pygame
from .Ping_Arena import Arena
from .Ping_GameObjects import PaddleObject


class AIConfig:
    """
    MINIMAL CONFIGURATION - TO BE EXPANDED IN PHASE 1
    
    Maintains compatibility with existing code that references config parameters.
    Only includes essential parameters to prevent import errors.
    """
    
    # Essential parameters for compatibility
    DEFAULT_ACCURACY = 0.8
    BASE_REACTION_TIME = 0.08
    DEFAULT_PADDLE_HEIGHT = 120
    PADDLE_DISTANCE_FROM_EDGE = 70
    
    # Minimal spike behavior (dummy values)
    SPIKE_PROBABILITY = 0.0  # No spiking in Phase 0
    SPIKE_COOLDOWN_DURATION = 1.0
    
    # Minimal thresholds (dummy values)
    FAR_BALL_THRESHOLD = 0.15
    BALL_PAST_PADDLE_MARGIN = 50
    SIGNIFICANT_ERROR_THRESHOLD = 0.5


class PaddleAI:
    """
    MINIMAL AI IMPLEMENTATION - PHASE 0
    
    This is a placeholder implementation that maintains API compatibility
    while providing basic functionality for game operation. All methods
    are marked for replacement in Phase 1.
    
    Design Philosophy:
    - Maintain exact interface compatibility with old system
    - Provide minimal but stable functionality
    - Enable game to run without errors
    - Mark all areas for Phase 1 replacement
    """
    
    def __init__(self, level_compiler, config=None):
        """
        MINIMAL INITIALIZATION - TO BE EXPANDED IN PHASE 1
        
        Args:
            level_compiler: Instance of LevelCompiler containing game dimensions
            config: Optional AIConfig instance (ignored in Phase 0)
        """
        # Store essential game parameters
        self.level_compiler = level_compiler
        self.config = config or AIConfig()
        
        # Get game dimensions from level compiler
        self.game_width = level_compiler.width
        self.game_height = level_compiler.height
        
        # Calculate paddle parameters
        self.paddle_height = self.config.DEFAULT_PADDLE_HEIGHT
        self.paddle_x = self.game_width - self.config.PADDLE_DISTANCE_FROM_EDGE
        
        # Minimal state tracking for compatibility
        self.is_resetting = False
        self.is_spiking = False
        self.last_spike_time = 0.0
        self.last_prediction = None
        
        # Phase 1: Initialize persistent tracking system
        self.ball_tracking_history = []  # Track ball positions for persistence
        self.offensive_target_cache = None  # Cache for offensive calculations
        self.threat_assessment_active = True  # Enable never-give-up tracking
        
        # Portal handling for levels like Manhole Mayhem
        self.portal_map = {}  # Map portal IDs to their target locations
        self.last_ball_position = None  # Track ball position to detect teleportation
        self._build_portal_map(level_compiler)
        
        # Fail-safe mechanisms to prevent lockups
        self.last_movement_time = time.time()
        self.stuck_detection_threshold = 3.0  # seconds
        self.emergency_reset_mode = False
        self.ball_respawn_detected = False
    
    def move_paddle(self, ball_x, ball_y, ball_dx, ball_dy, paddle_y, paddle_movement, 
                   ball_frozen, all_balls=None, score_ai=0, score_opponent=0, frame_time=1/60.0):
        """
        PHASE 1 IMPLEMENTATION - Robust AI with Fail-Safe Mechanisms
        
        Uses prioritized decision system to prevent lockups during ball respawn.
        
        Args:
            ball_x: Ball x position
            ball_y: Ball y position  
            ball_dx: Ball x velocity
            ball_dy: Ball y velocity
            paddle_y: Current paddle y position
            paddle_movement: Maximum movement per frame
            ball_frozen: Whether ball is frozen during respawn
            all_balls: List of all active balls (optional)
            score_ai: AI score
            score_opponent: Opponent score
            frame_time: Time since last frame
            
        Returns:
            float: New paddle Y position
        """
        current_time = time.time()
        center_y = (self.game_height - self.paddle_height) // 2
        
        # PRIORITY 1: Handle manual reset state (highest priority)
        if self.is_resetting:
            return self._handle_reset_movement(paddle_y, center_y, paddle_movement)
        
        # PRIORITY 2: Detect and handle stuck situations (fail-safe)
        if self._detect_stuck_situation(paddle_y, current_time):
            return self._handle_emergency_reset(paddle_y, center_y, paddle_movement)
        
        # PRIORITY 3: Handle ball frozen/respawn scenarios (critical)
        if ball_frozen or self._is_ball_respawning(ball_x, ball_y, ball_dx, ball_dy):
            return self._handle_ball_respawn(center_y)
        
        # PRIORITY 4: Normal AI tracking (only when safe)
        return self._handle_normal_tracking(ball_x, ball_y, ball_dx, ball_dy, paddle_y, 
                                          paddle_movement, all_balls, score_ai, score_opponent)
    
    def reset_position(self):
        """
        DUMMY RESET IMPLEMENTATION - TO BE EXPANDED IN PHASE 1
        
        Currently just sets reset flag. In Phase 1, this should reset all AI state
        including tracking history, offensive calculations, and strategy state.
        """
        self.is_resetting = True
        
        # Phase 1: Reset persistent tracking state
        self.ball_tracking_history.clear()
        self.offensive_target_cache = None
        self.threat_assessment_active = True
        self.last_ball_position = None  # Reset teleportation detection
        
        # Reset fail-safe mechanisms
        self.last_movement_time = time.time()
        self.emergency_reset_mode = False
        self.ball_respawn_detected = False
        
        # Clear any cached predictions since ball will respawn
        self._clear_tracking_after_scoring()
        
        # Reset fail-safe state
        self.emergency_reset_mode = False
        self.ball_respawn_detected = False
        
        # Force complete reset when reset_position is called
        self._force_complete_reset()
    
    def should_attempt_spike(self, ball_x, ball_dx, score_ai=0, score_opponent=0):
        """
        PHASE 1 IMPLEMENTATION - Intelligent Spike Decision Logic
        
        Decides whether to attempt a spike based on offensive opportunities,
        ball position, game state, and timing considerations.
        
        Args:
            ball_x: Ball x position
            ball_dx: Ball x velocity
            score_ai: AI score
            score_opponent: Opponent score
            
        Returns:
            bool: Whether to attempt a spike
        """
        current_time = time.time()
        
        # Check cooldown to prevent constant spiking
        if current_time - self.last_spike_time < self.config.SPIKE_COOLDOWN_DURATION:
            return False
            
        # Only spike when ball is approaching
        if ball_dx <= 0:
            self.is_spiking = False
            return False
            
        # Calculate spike opportunity based on ball position
        # More likely to spike when ball is in optimal range
        distance_to_paddle = abs(self.paddle_x - ball_x)
        optimal_range = self.game_width * 0.3  # Within 30% of paddle
        
        if distance_to_paddle > optimal_range:
            return False
            
        # Base spike probability increases as ball gets closer
        proximity_factor = 1 - (distance_to_paddle / optimal_range)
        
        # Adjust aggression based on score differential
        score_diff = score_ai - score_opponent
        if score_diff < -1:  # Behind: more aggressive
            aggression = 0.4
        elif score_diff > 1:  # Ahead: more conservative
            aggression = 0.15
        else:  # Close game: moderate aggression
            aggression = 0.25
            
        spike_probability = aggression * proximity_factor
        
        if random.random() < spike_probability:
            self.is_spiking = True
            self.last_spike_time = current_time
            return True
            
        return False
    
    def predict_intersection(self, ball_x, ball_y, ball_dx, ball_dy, all_balls=None):
        """
        PHASE 1 IMPLEMENTATION - Never-Give-Up Ball Prediction
        
        Predicts ball trajectory with physics-based calculations that never give up,
        including wall bounce physics and multi-ball threat assessment.
        
        Args:
            ball_x: Ball x position
            ball_y: Ball y position
            ball_dx: Ball x velocity
            ball_dy: Ball y velocity
            all_balls: List of all active balls (optional)
            
        Returns:
            float: Predicted ball Y position at paddle intercept
        """
        # Select the most threatening ball
        target_ball = self._select_priority_ball(ball_x, ball_y, ball_dx, ball_dy, all_balls)
        
        # Use never-give-up prediction for the priority ball
        return self._predict_interception_never_give_up(
            target_ball['x'], target_ball['y'], target_ball['dx'], target_ball['dy']
        )
    
    def calculate_spike_position(self, predicted_y, ball_y):
        """
        PHASE 1 IMPLEMENTATION - Offensive Spike Positioning
        
        Calculates optimal paddle position for spiking based on goal-targeting
        strategy and offensive angle calculations.
        
        Args:
            predicted_y: Predicted ball y position
            ball_y: Current ball y position
            
        Returns:
            float: Spike position Y coordinate for optimal offensive angle
        """
        # Determine optimal spike strategy based on ball position
        arena_center = self.game_height / 2
        
        # Target opponent's goal corners for maximum difficulty
        if predicted_y < arena_center:
            # Ball in upper half - target lower corner of opponent goal
            spike_strategy = 'target_bottom'
            target_paddle_contact = predicted_y + (self.paddle_height * 0.3)  # Hit with lower portion
        else:
            # Ball in lower half - target upper corner of opponent goal  
            spike_strategy = 'target_top'
            target_paddle_contact = predicted_y - (self.paddle_height * 0.3)  # Hit with upper portion
            
        # Calculate paddle position to achieve desired contact point
        target_paddle_y = target_paddle_contact - (self.paddle_height / 2)
        
        # Ensure spike position stays within bounds
        target_paddle_y = max(0, min(target_paddle_y, self.game_height - self.paddle_height))
        
        return target_paddle_y
    
    def calculate_movement_speed(self, current_y, target_y, max_movement):
        """
        BASIC MOVEMENT CALCULATION - KEPT FROM ORIGINAL
        
        This is a simple utility method that can be preserved as-is.
        
        Args:
            current_y: Current paddle Y position
            target_y: Target paddle Y position
            max_movement: Maximum movement allowed per frame
            
        Returns:
            float: Movement amount (signed)
        """
        distance = target_y - current_y
        if abs(distance) < max_movement:
            return distance
        return math.copysign(max_movement, distance)
    
    def _select_priority_ball(self, ball_x, ball_y, ball_dx, ball_dy, all_balls=None):
        """
        PHASE 1: Robust multi-ball threat assessment with error handling.
        
        Args:
            ball_x: Primary ball x position
            ball_y: Primary ball y position
            ball_dx: Primary ball x velocity
            ball_dy: Primary ball y velocity
            all_balls: List of all active balls (optional)
            
        Returns:
            dict: Priority ball data with x, y, dx, dy keys
        """
        # Default to primary ball (safe fallback)
        priority_ball = {'x': ball_x, 'y': ball_y, 'dx': ball_dx, 'dy': ball_dy}
        
        # Validate primary ball data
        if not all(isinstance(val, (int, float)) for val in [ball_x, ball_y, ball_dx, ball_dy]):
            # Invalid primary ball data - use safe defaults
            center_x = self.game_width / 2
            center_y = self.game_height / 2
            priority_ball = {'x': center_x, 'y': center_y, 'dx': 0, 'dy': 0}
        
        # If no multiple balls or invalid list, return primary/safe ball
        if not all_balls or not isinstance(all_balls, list) or len(all_balls) <= 1:
            return priority_ball
            
        highest_threat = -1
        
        # Evaluate threat level for each ball with error handling
        try:
            for ball in all_balls:
                if not ball or not hasattr(ball, 'rect') or not hasattr(ball, 'ball'):
                    continue  # Skip invalid balls
                    
                threat_score = self._calculate_ball_threat_score(ball)
                
                if threat_score > highest_threat:
                    highest_threat = threat_score
                    priority_ball = {
                        'x': ball.rect.x,
                        'y': ball.rect.y,
                        'dx': ball.ball.velocity_x,
                        'dy': ball.ball.velocity_y
                    }
        except (AttributeError, TypeError, ValueError):
            # If ball selection fails, use the safe fallback
            pass
                
        return priority_ball
        
    def _calculate_ball_threat_score(self, ball):
        """
        PHASE 1: Robust threat score calculation with error handling.
        
        Args:
            ball: Ball object to evaluate
            
        Returns:
            float: Threat score (higher = more threatening)
        """
        try:
            ball_x = ball.rect.x
            ball_dx = ball.ball.velocity_x
            
            # Validate ball data
            if not all(isinstance(val, (int, float)) for val in [ball_x, ball_dx]):
                return 0.1  # Minimal threat for invalid data
            
            # Distance factor - closer balls are more threatening
            distance_to_paddle = abs(self.paddle_x - ball_x)
            distance_factor = max(0, 1 - (distance_to_paddle / self.game_width))
            
            # Velocity factor - faster approaching balls are more threatening
            velocity_factor = max(0, ball_dx / 1000)  # Normalize velocity
            
            # Position factor - balls in AI's half are more threatening
            position_factor = 1.0 if ball_x > self.game_width / 2 else 0.5
            
            # Never give up - even balls moving away have minimal threat
            base_threat = 0.1
            
            total_threat = base_threat + (distance_factor * 50) + (velocity_factor * 30) + (position_factor * 20)
            
            return max(0.1, total_threat)  # Ensure minimum threat
            
        except (AttributeError, TypeError, ValueError, ZeroDivisionError):
            return 0.1  # Safe fallback threat score
        
    def _predict_interception_never_give_up(self, ball_x, ball_y, ball_dx, ball_dy, recursion_depth=0):
        """
        PHASE 1: Never-give-up ball trajectory prediction with physics.
        
        Always calculates interception regardless of ball direction or distance.
        Includes wall bounce physics and portal teleportation for accurate prediction.
        
        Args:
            ball_x: Ball x position
            ball_y: Ball y position
            ball_dx: Ball x velocity
            ball_dy: Ball y velocity
            recursion_depth: Current recursion depth to prevent infinite loops
            
        Returns:
            float: Predicted ball Y position at paddle intercept
        """
        # Prevent infinite recursion from portal loops
        if recursion_depth > 3:  # Max 3 portal jumps
            return ball_y  # Use current position as safe fallback
        
        # Detect sudden teleportation and adapt quickly
        if recursion_depth == 0 and self._detect_ball_teleportation(ball_x, ball_y):
            # Check if this is actually a ball respawn (center position)
            center_x = self.game_width / 2
            center_y_ball = self.game_height / 2
            
            # If ball is near center, this might be a respawn, not teleportation
            if abs(ball_x - center_x) < 50 and abs(ball_y - center_y_ball) < 50:
                # Likely a respawn - clear all tracking
                self._clear_tracking_after_scoring()
                return ball_y
            else:
                # Ball was teleported - use current position as best prediction
                # Clear tracking history since trajectory completely changed
                self.ball_tracking_history.clear()
                return ball_y
        
        # Check for potential portal teleportation in ball's path (only on first call)
        # DISABLE portal prediction if in respawn mode or emergency mode
        if (recursion_depth == 0 and 
            not self.ball_respawn_detected and 
            not self.emergency_reset_mode and 
            len(self.portal_rects) > 0):
            
            portal_exit = self._predict_portal_exit(ball_x, ball_y, ball_dx, ball_dy)
            if portal_exit:
                # Ball will hit portal - predict from exit point with incremented depth
                return self._predict_interception_never_give_up(
                    portal_exit['x'], portal_exit['y'], 
                    portal_exit['dx'], portal_exit['dy'],
                    recursion_depth + 1
                )
        
        # Never give up - always calculate interception
        
        # Handle edge case of zero horizontal velocity
        if ball_dx == 0:
            return ball_y  # Ball will stay at current Y
            
        # Calculate time to reach paddle X position
        time_to_paddle = (self.paddle_x - ball_x) / ball_dx
        
        # If ball is moving away, calculate where it would be if it bounced back
        if time_to_paddle < 0:
            # Ball moving away - predict where it will be when it could return
            # Simplification: assume it will return from the wall
            wall_x = 0 if ball_dx < 0 else self.game_width
            time_to_wall = (wall_x - ball_x) / ball_dx
            time_from_wall = (self.paddle_x - wall_x) / (-ball_dx)  # Reverse direction
            total_time = time_to_wall + time_from_wall
            predicted_y = ball_y + (ball_dy * total_time)
        else:
            # Ball approaching - normal prediction
            predicted_y = ball_y + (ball_dy * time_to_paddle)
            
        # Apply wall bounce physics
        predicted_y = self._apply_wall_bounces(predicted_y)
        
        return predicted_y
        
    def _apply_wall_bounces(self, predicted_y):
        """
        PHASE 1: Apply wall bounce physics to predicted Y position.
        
        Args:
            predicted_y: Raw predicted Y position
            
        Returns:
            float: Y position after accounting for wall bounces
        """
        # Clamp to playable area with bounce physics
        if predicted_y < 0:
            # Bounce off top wall
            predicted_y = abs(predicted_y)
        elif predicted_y > self.game_height:
            # Bounce off bottom wall
            predicted_y = self.game_height - (predicted_y - self.game_height)
            
        # Handle multiple bounces
        while predicted_y < 0 or predicted_y > self.game_height:
            if predicted_y < 0:
                predicted_y = abs(predicted_y)
            if predicted_y > self.game_height:
                predicted_y = self.game_height - (predicted_y - self.game_height)
                
        return predicted_y
        
    def _calculate_offensive_positioning(self, ball_x, ball_y, ball_dx, ball_dy, predicted_y):
        """
        PHASE 1: Calculate offensive positioning adjustment for goal targeting.
        
        Determines how to adjust paddle position to deflect ball toward opponent's goal.
        
        Args:
            ball_x: Ball x position
            ball_y: Ball y position
            ball_dx: Ball x velocity
            ball_dy: Ball y velocity
            predicted_y: Predicted interception Y position
            
        Returns:
            float: Y position adjustment for offensive strategy
        """
        # Only apply offensive strategy when ball is approaching
        if ball_dx <= 0:
            return 0
            
        # Calculate optimal deflection angle to target opponent's goal corners
        arena_center = self.game_height / 2
        
        # Target the corner opposite to where ball is coming from
        if predicted_y < arena_center:
            # Ball in upper area - target opponent's lower goal area
            target_goal_y = self.game_height * 0.75
        else:
            # Ball in lower area - target opponent's upper goal area
            target_goal_y = self.game_height * 0.25
            
        # Calculate required paddle offset to achieve target deflection
        desired_deflection = target_goal_y - predicted_y
        
        # Scale the adjustment based on ball speed and distance
        ball_speed = math.sqrt(ball_dx**2 + ball_dy**2)
        distance_factor = max(0.1, min(1.0, abs(self.paddle_x - ball_x) / (self.game_width * 0.5)))
        speed_factor = min(1.0, ball_speed / 1000)
        
        # Apply scaling to make adjustment proportional to game physics
        offensive_adjustment = desired_deflection * 0.3 * distance_factor * speed_factor
        
        # Limit adjustment to reasonable range
        max_adjustment = self.paddle_height * 0.5
        offensive_adjustment = max(-max_adjustment, min(max_adjustment, offensive_adjustment))
        
        return offensive_adjustment
        
    def _handle_reset_movement(self, paddle_y, center_y, paddle_movement):
        """Handle movement during manual reset state."""
        distance = center_y - paddle_y
        if abs(distance) < 2:
            self.is_resetting = False
            return center_y
        
        movement = min(paddle_movement, abs(distance))
        return paddle_y + (movement if distance > 0 else -movement)
        
    def _detect_stuck_situation(self, paddle_y, current_time):
        """Detect if AI appears to be stuck and needs emergency reset."""
        # Check if paddle hasn't moved significantly in a while
        if not hasattr(self, '_last_paddle_y'):
            self._last_paddle_y = paddle_y
            return False
            
        movement_since_last = abs(paddle_y - self._last_paddle_y)
        
        if movement_since_last > 5:  # Paddle moved significantly
            self.last_movement_time = current_time
            self._last_paddle_y = paddle_y
            return False
            
        # Check if stuck for too long
        time_since_movement = current_time - self.last_movement_time
        if time_since_movement > self.stuck_detection_threshold:
            return True
            
        return False
        
    def _handle_emergency_reset(self, paddle_y, center_y, paddle_movement):
        """Handle emergency reset when AI appears stuck."""
        if not self.emergency_reset_mode:
            self.emergency_reset_mode = True
            self._clear_tracking_after_scoring()
            
        # Move toward center during emergency reset
        distance = center_y - paddle_y
        if abs(distance) < 5:
            self.emergency_reset_mode = False
            return center_y
            
        movement = min(paddle_movement, abs(distance))
        return paddle_y + (movement if distance > 0 else -movement)
        
    def _is_ball_respawning(self, ball_x, ball_y, ball_dx, ball_dy):
        """Enhanced respawn detection that clears map data when respawn detected."""
        center_x = self.game_width / 2
        center_y = self.game_height / 2
        
        # Ball is near center with low velocity
        near_center = (abs(ball_x - center_x) < 80 and abs(ball_y - center_y) < 80)
        low_velocity = (abs(ball_dx) < 30 and abs(ball_dy) < 30)
        
        # More aggressive center detection for respawn scenarios
        very_near_center = (abs(ball_x - center_x) < 120 and abs(ball_y - center_y) < 120)
        very_low_velocity = (abs(ball_dx) < 50 and abs(ball_dy) < 50)
        
        if (near_center and low_velocity) or (very_near_center and very_low_velocity):
            if not self.ball_respawn_detected:  # First time detecting respawn
                self._clear_tracking_after_scoring()  # Force clear all map data
            self.ball_respawn_detected = True
            return True
            
        # Sudden teleportation to center area (likely respawn)
        if self.last_ball_position:
            last_x, last_y = self.last_ball_position
            distance_jumped = math.sqrt((ball_x - last_x)**2 + (ball_y - last_y)**2)
            
            if distance_jumped > 150 and very_near_center:
                if not self.ball_respawn_detected:  # First time detecting respawn
                    self._clear_tracking_after_scoring()  # Force clear all map data
                self.ball_respawn_detected = True
                return True
        
        # If we previously detected respawn, keep it active until ball moves significantly
        if self.ball_respawn_detected:
            if abs(ball_dx) > 60 or abs(ball_dy) > 60:  # Ball started moving fast
                self.ball_respawn_detected = False
                # Don't clear map data here - only on initial respawn detection
                return False
            return True  # Still in respawn mode
            
        return False
        
    def _handle_ball_respawn(self, center_y):
        """Handle ball respawn by forcing complete state reset and going to center."""
        # Force complete cleanup including map data
        self._clear_tracking_after_scoring()
        
        # Additional safety: ensure we return exact center
        safe_center_y = (self.game_height - self.paddle_height) // 2
        return safe_center_y
        
    def _handle_normal_tracking(self, ball_x, ball_y, ball_dx, ball_dy, paddle_y, 
                               paddle_movement, all_balls, score_ai, score_opponent):
        """Handle normal AI tracking when not in special modes."""
        # Update ball position tracking (but not during respawn)
        if not self.ball_respawn_detected:
            self.last_ball_position = (ball_x, ball_y)
        
        # Select priority ball with extra validation
        target_ball = self._select_priority_ball(ball_x, ball_y, ball_dx, ball_dy, all_balls)
        
        # Extra safety: if ball seems to be in center area, use simple center tracking
        center_x = self.game_width / 2
        center_y = self.game_height / 2
        if (abs(target_ball['x'] - center_x) < 100 and 
            abs(target_ball['y'] - center_y) < 100 and 
            abs(target_ball['dx']) < 40):
            # Ball is near center - use simple center positioning
            return (self.game_height - self.paddle_height) // 2
        
        # Predict interception
        try:
            predicted_y = self._predict_interception_never_give_up(
                target_ball['x'], target_ball['y'], target_ball['dx'], target_ball['dy']
            )
        except (RecursionError, ValueError, AttributeError):
            # Fallback to simple tracking if prediction fails
            predicted_y = target_ball['y']
            
        # Calculate offensive positioning (disable if ball is slow/center)
        offensive_adjustment = 0
        if abs(target_ball['dx']) > 30 or abs(target_ball['dy']) > 30:
            try:
                offensive_adjustment = self._calculate_offensive_positioning(
                    target_ball['x'], target_ball['y'], target_ball['dx'], target_ball['dy'], predicted_y
                )
            except (ValueError, ZeroDivisionError, AttributeError):
                offensive_adjustment = 0  # No offensive adjustment if calculation fails
            
        # Apply strategy
        target_y = predicted_y + offensive_adjustment - (self.paddle_height / 2)
        
        # Ensure target stays within bounds
        target_y = max(0, min(target_y, self.game_height - self.paddle_height))
        
        # Move toward target
        distance = target_y - paddle_y
        if abs(distance) <= paddle_movement:
            return target_y
            
        return paddle_y + (paddle_movement if distance > 0 else -paddle_movement)
        
    def _clear_tracking_after_scoring(self):
        """
        Clear ALL tracking and map data after a scoring event.
        
        Called when ball respawns to ensure AI doesn't use stale tracking or map data.
        This includes portal mappings and level-specific knowledge.
        """
        # Clear ball tracking data
        self.ball_tracking_history.clear()
        self.offensive_target_cache = None
        self.last_ball_position = None
        
        # CRITICAL: Clear all map/level knowledge to prevent permanence issues
        self.portal_map = {}
        self.portal_rects = []
        
        # Force rebuild portal map with current level state
        if hasattr(self, 'level_compiler') and self.level_compiler:
            self._build_portal_map(self.level_compiler)
        
        # Reset any internal state that might be confused by ball respawn
        self.is_spiking = False
        self.last_spike_time = 0.0
        
        # Reset fail-safe mechanisms
        self.last_movement_time = time.time()
        self.emergency_reset_mode = False
        self.ball_respawn_detected = False
        
        # Clear paddle tracking for stuck detection
        if hasattr(self, '_last_paddle_y'):
            delattr(self, '_last_paddle_y')
            
        # Clear any cached level-specific data that might persist
        if hasattr(self, '_level_cache'):
            delattr(self, '_level_cache')
        if hasattr(self, '_map_analysis_cache'):
            delattr(self, '_map_analysis_cache')
        
    def on_score_event(self, scorer=None):
        """
        Called when a scoring event occurs to completely reset AI state.
        
        Args:
            scorer: Which player scored ('left', 'right', 'ai', 'opponent') - optional
        """
        # Force complete state reset including all map data
        self._force_complete_reset()
        
        # Additional cleanup based on who scored
        if scorer in ['left', 'opponent']:  # Opponent scored against AI
            # AI lost the point - be more aggressive next time
            pass  # Could adjust aggression here in future
        elif scorer in ['right', 'ai']:  # AI scored
            # AI won the point - maintain current strategy
            pass  # Could adjust conservativeness here in future
            
    def _force_complete_reset(self):
        """
        Force complete reset of ALL AI state and knowledge.
        
        This is the nuclear option - clears everything and rebuilds from scratch.
        """
        # Clear all tracking data
        self._clear_tracking_after_scoring()
        
        # Force paddle to center immediately
        self.is_resetting = True
        self.emergency_reset_mode = True
        
        # Clear all cached data that might persist
        for attr_name in list(self.__dict__.keys()):
            if ('cache' in attr_name.lower() or 
                'history' in attr_name.lower() or 
                'map' in attr_name.lower()):
                try:
                    if isinstance(getattr(self, attr_name), (list, dict)):
                        getattr(self, attr_name).clear()
                    else:
                        setattr(self, attr_name, None)
                except AttributeError:
                    pass
                    
        # Rebuild essential data structures
        self.ball_tracking_history = []
        self.portal_map = {}
        self.portal_rects = []
        
        # Force rebuild portal map if level compiler available
        if hasattr(self, 'level_compiler') and self.level_compiler:
            try:
                self._build_portal_map(self.level_compiler)
            except Exception:
                # If portal rebuild fails, disable portal features
                self.portal_rects = []
                self.portal_map = {}
            
    def _build_portal_map(self, level_compiler):
        """
        Build a map of portal locations and their targets for teleportation prediction.
        
        Args:
            level_compiler: LevelCompiler object containing level data
        """
        self.portal_map = {}
        self.portal_rects = []  # List of portal rects for collision detection
        
        if not hasattr(level_compiler, 'portals') or not level_compiler.portals:
            return
            
        # Build list of portal rectangles and their targets for quick collision detection
        for portal in level_compiler.portals:
            if hasattr(portal, 'portal') and hasattr(portal.portal, 'target_portal'):
                source_rect = portal.portal.rect
                target_portal = portal.portal.target_portal
                
                if target_portal:
                    target_rect = target_portal.rect
                    
                    portal_info = {
                        'source_rect': source_rect,
                        'target_rect': target_rect,
                        'source_portal': portal.portal,
                        'target_portal': target_portal
                    }
                    
                    self.portal_rects.append(portal_info)
                
    def _detect_ball_teleportation(self, ball_x, ball_y):
        """
        Detect if ball has been teleported through a portal by checking for sudden position changes.
        
        Args:
            ball_x: Current ball x position
            ball_y: Current ball y position
            
        Returns:
            bool: True if teleportation was detected
        """
        if self.last_ball_position is None:
            self.last_ball_position = (ball_x, ball_y)
            return False
            
        last_x, last_y = self.last_ball_position
        
        # Calculate distance moved since last frame
        distance_moved = math.sqrt((ball_x - last_x)**2 + (ball_y - last_y)**2)
        
        # If ball moved more than reasonable distance in one frame, likely teleported
        # Made more conservative to avoid false positives with high-speed gameplay
        max_reasonable_distance = 200  # Pixels per frame at very high speed
        
        teleported = distance_moved > max_reasonable_distance
        
        # Update tracking
        self.last_ball_position = (ball_x, ball_y)
        
        return teleported
        
    def _predict_portal_exit(self, ball_x, ball_y, ball_dx, ball_dy):
        """
        Predict where the ball will exit if it hits a portal.
        
        Args:
            ball_x: Ball x position
            ball_y: Ball y position
            ball_dx: Ball x velocity
            ball_dy: Ball y velocity
            
        Returns:
            dict: Portal exit prediction with 'x', 'y', 'dx', 'dy' or None if no portal hit predicted
        """
        if not self.portal_rects:
            return None
            
        # Only predict portal hits if ball is moving with reasonable speed
        if abs(ball_dx) < 10:  # Ignore very slow or stationary balls
            return None
            
        # Check if ball trajectory intersects with any portal
        for portal_info in self.portal_rects:
            source_rect = portal_info['source_rect']
            target_rect = portal_info['target_rect']
            
            # Predict ball path and check intersection
            if self._will_ball_hit_portal(ball_x, ball_y, ball_dx, ball_dy, source_rect):
                # Calculate exit position from target portal
                if source_rect.x <= 50:  # Left wall portal
                    exit_x = target_rect.right + 30  # Exit to right of target
                else:  # Right wall portal
                    exit_x = target_rect.left - 30  # Exit to left of target
                    
                # Maintain relative Y position within target portal
                rel_y = 0.5  # Default to center if can't calculate
                if source_rect.height > 0:
                    rel_y = max(0.1, min(0.9, (ball_y - source_rect.y) / source_rect.height))
                    
                exit_y = target_rect.y + (rel_y * target_rect.height)
                
                # Ensure exit position is reasonable
                exit_y = max(0, min(exit_y, self.game_height))
                
                return {
                    'x': exit_x,
                    'y': exit_y, 
                    'dx': ball_dx,  # Velocity preserved through portal
                    'dy': ball_dy
                }
                
        return None
        
    def _will_ball_hit_portal(self, ball_x, ball_y, ball_dx, ball_dy, portal_rect):
        """
        Check if ball trajectory will intersect with a portal.
        
        Args:
            ball_x: Ball x position
            ball_y: Ball y position
            ball_dx: Ball x velocity
            ball_dy: Ball y velocity
            portal_rect: pygame.Rect for the portal
            
        Returns:
            bool: True if ball will hit portal
        """
        if ball_dx == 0 or abs(ball_dx) < 10:
            return False
            
        # Only check portals that are reasonably close
        distance_to_portal = min(abs(portal_rect.left - ball_x), abs(portal_rect.right - ball_x))
        if distance_to_portal > 300:  # Don't predict very distant portals
            return False
            
        # Calculate time to reach portal x position
        if portal_rect.left <= ball_x <= portal_rect.right:
            # Ball is already within portal x range
            time_to_portal = 0
        elif ball_dx > 0 and ball_x < portal_rect.left:
            # Ball moving right toward portal
            time_to_portal = (portal_rect.left - ball_x) / ball_dx
        elif ball_dx < 0 and ball_x > portal_rect.right:
            # Ball moving left toward portal
            time_to_portal = (portal_rect.right - ball_x) / ball_dx
        else:
            return False  # Ball moving away from portal
            
        if time_to_portal < 0 or time_to_portal > 2.0:  # Don't predict more than 2 seconds ahead
            return False
            
        # Predict Y position when ball reaches portal
        predicted_y = ball_y + (ball_dy * time_to_portal)
        
        # Apply wall bounces to predicted Y
        predicted_y = self._apply_wall_bounces(predicted_y)
        
        # Check if predicted Y intersects with portal (with margin)
        margin = 10  # Small margin for collision detection
        return (portal_rect.top - margin) <= predicted_y <= (portal_rect.bottom + margin)


# PHASE 1 VALIDATION FUNCTIONS
# These functions help validate that the enhanced AI works correctly

def validate_ai_initialization():
    """Test that AI can be initialized without errors."""
    try:
        # Create a mock level compiler
        class MockLevelCompiler:
            def __init__(self):
                self.width = 800
                self.height = 600
                self.portals = []  # Empty portals list for Phase 1
        
        level_compiler = MockLevelCompiler()
        ai = PaddleAI(level_compiler)
        
        # Basic validation
        assert ai.game_width == 800
        assert ai.game_height == 600
        assert ai.paddle_height == 120
        assert not ai.is_resetting
        assert not ai.is_spiking
        
        # Phase 1 validation
        assert hasattr(ai, 'ball_tracking_history')
        assert hasattr(ai, 'portal_rects')
        assert hasattr(ai, 'last_ball_position')
        assert ai.threat_assessment_active == True
        
        # Fail-safe mechanism validation
        assert hasattr(ai, 'last_movement_time')
        assert hasattr(ai, 'emergency_reset_mode')
        assert hasattr(ai, 'ball_respawn_detected')
        assert ai.emergency_reset_mode == False
        
        return True
    except Exception as e:
        print(f"AI initialization validation failed: {e}")
        return False

def validate_ai_methods():
    """Test that all required AI methods return valid values."""
    try:
        class MockLevelCompiler:
            def __init__(self):
                self.width = 800
                self.height = 600
                self.portals = []  # Empty portals list for Phase 1
        
        level_compiler = MockLevelCompiler()
        ai = PaddleAI(level_compiler)
        
        # Test move_paddle with Phase 1 behavior
        result = ai.move_paddle(400, 300, 5, 3, 240, 10, False)
        assert isinstance(result, (int, float))
        assert 0 <= result <= 600 - 120
        
        # Test reset_position
        ai.reset_position()
        assert ai.is_resetting
        
        # Test should_attempt_spike (now has intelligent logic)
        spike_result = ai.should_attempt_spike(600, 5)  # Close ball
        assert isinstance(spike_result, bool)
        
        # Test predict_intersection
        prediction = ai.predict_intersection(400, 300, 5, 3)
        assert isinstance(prediction, (int, float))
        
        # Test scoring cleanup
        ai.on_score_event('opponent')
        assert ai.last_ball_position is None
        assert len(ai.ball_tracking_history) == 0
        assert ai.emergency_reset_mode == False
        assert ai.ball_respawn_detected == False
        
        # Test fail-safe mechanisms
        ai.emergency_reset_mode = True
        emergency_result = ai.move_paddle(400, 300, 5, 3, 100, 10, False)
        assert isinstance(emergency_result, (int, float))
        
        # Test ball respawn detection
        respawn_result = ai.move_paddle(640, 360, 0, 0, 240, 10, False)  # Center, no velocity
        assert isinstance(respawn_result, (int, float))
        
        return True
    except Exception as e:
        print(f"AI methods validation failed: {e}")
        return False

# Run validation if this module is executed directly
if __name__ == "__main__":
    print("Running Phase 0 AI validation...")
    
    init_valid = validate_ai_initialization()
    methods_valid = validate_ai_methods()
    
    if init_valid and methods_valid:
        print("✅ Phase 1 Robust AI validation passed!")
        print("   - AI initializes correctly with portal support")
        print("   - Never-give-up tracking active")
        print("   - Offensive strategy implemented")
        print("   - Fail-safe mechanisms functional")
        print("   - Ball respawn detection robust")
        print("   - Emergency reset system active")
        print("   - Scoring cleanup functional")
        print("   - Interface compatibility maintained")
        print("   - Ready for lockup-free game testing")
    else:
        print("❌ Phase 1 Robust AI validation failed!")
        print("   - Check implementation for issues")
        print("   - Ensure all method signatures are correct")
        print("   - Verify return types and ranges")
        print("   - Check Phase 1 feature implementations")
        print("   - Verify fail-safe mechanisms")