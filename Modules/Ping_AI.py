class PaddleAI:
    def __init__(self, arena_height):
        self.arena_height = arena_height
        self.paddle_height = 120  # Standard paddle height

    def move_paddle(self, ball_center_y, paddle_y, paddle_movement):
        """
        Calculate the next paddle position based on ball position.
        
        Args:
            ball_center_y: Y coordinate of the ball's center
            paddle_y: Current Y coordinate of the AI paddle
            paddle_movement: Amount the paddle can move this frame
            
        Returns:
            float: New Y position for the paddle
        """
        # 70% chance to move - adds human-like hesitation
        if random.random() > 0.3:
            # Move paddle down if ball is below paddle center
            if ball_center_y > (paddle_y + self.paddle_height/2) and (paddle_y + self.paddle_height) < self.arena_height:
                new_y = paddle_y + paddle_movement
                return min(new_y, self.arena_height - self.paddle_height)
            # Move paddle up if ball is above paddle center
            elif ball_center_y < (paddle_y + self.paddle_height/2) and paddle_y > 50:  # 50px for scoreboard
                new_y = paddle_y - paddle_movement
                return max(50, new_y)
        
        return paddle_y  # Keep current position if not moving

import random