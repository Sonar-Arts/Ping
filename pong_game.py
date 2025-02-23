import turtle
import time
import random
import winsound

# Set up the screen
win = turtle.Screen()
win.title("Pong")
win.bgcolor("black")
win.setup(width=800, height=600)
win.tracer(0)

# Game state
game_state = "main_menu"

def title_screen():
    """
    Displays the title screen with game options.
    - Creates and configures turtle objects to display the game title and options.
    - Listens for key presses to start the game.
    """
    global title_updating
    title_updating = True

    global game_state
    game_state = "main_menu"

    def random_color():
        return f"#{random.randint(0, 0xFFFFFF):06x}"

    letters = []
    positions = [-60, -20, 20, 60]
    for i, char in enumerate("Ping"):
        letter = turtle.Turtle()
        letter.speed(0)
        letter.color("white")
        letter.penup()
        letter.hideturtle()
        letter.goto(positions[i], 100)
        letter.write(char, align="center", font=("Courier", 36, "normal"))
        letter._char = char  # Store the character
        letters.append(letter)

    def update_title_colors():
        if not title_updating:
            clear_title()
            return
        for letter in letters:
            letter.clear()
            letter.color(random_color())
            letter.write(letter._char, align="center", font=("Courier", 36, "normal"))
        win.ontimer(update_title_colors, 3000)

    update_title_colors()

    option1 = turtle.Turtle()
    option1.speed(0)
    option1.color("white")
    option1.penup()
    option1.hideturtle()
    option1.goto(0, 0)
    option1.write("1. Player vs Player", align="center", font=("Courier", 24, "normal"))

    option2 = turtle.Turtle()
    option2.speed(0)
    option2.color("white")
    option2.penup()
    option2.hideturtle()
    option2.goto(0, -50)
    option2.write("2. Player vs AI", align="center", font=("Courier", 24, "normal"))

    win.listen()
    def clear_title():
        for letter in letters:
            letter.clear()
        option1.clear()
        option2.clear()

    win.onkeypress(lambda: clear_title() or start_game(False), "1")
    win.onkeypress(lambda: clear_title() or start_game(True), "2")

def start_game(ai_mode):
    """
    Clears the title screen and starts the main game.
    - Clears the screen and reinitializes the game window.
    - Calls main_game() to start the main game.
    """
    global title_updating
    title_updating = False
    
    win.clearscreen()
    win.title("Pong")
    win.bgcolor("black")
    win.setup(width=800, height=600)
    win.tracer(0)
    main_game(ai_mode)

# Main game function
def main_game(ai_mode):
    """
    Sets up and runs the main game loop.
    - Initializes paddles, ball, and score display.
    - Defines functions to handle paddle movements and score updates.
    - Sets up keyboard bindings for paddle controls.
    - Contains the main game loop that updates the game state, moves the ball and paddles, checks for collisions, and updates the score.
    """
    # Game constants
    FRAME_RATE = 60
    FRAME_TIME = 1.0 / FRAME_RATE
    BALL_SPEED = 400  # pixels per second
    PADDLE_SPEED = 400  # pixels per second

    # Paddle A
    paddle_a = turtle.Turtle()
    paddle_a.speed(0)
    paddle_a.shape("square")
    paddle_a.color("white")
    paddle_a.shapesize(stretch_wid=6, stretch_len=1)
    paddle_a.penup()
    paddle_a.goto(-350, 0)

    # Paddle B
    paddle_b = turtle.Turtle()
    paddle_b.speed(0)
    paddle_b.shape("square")
    paddle_b.color("white")
    paddle_b.shapesize(stretch_wid=6, stretch_len=1)
    paddle_b.penup()
    paddle_b.goto(350, 0)

    # Ball
    ball = turtle.Turtle()
    ball.speed(0)
    ball.shape("square")
    ball.color("white")
    ball.penup()
    ball.goto(0, 0)
    ball.dx = BALL_SPEED
    ball.dy = -BALL_SPEED

    # Movement flags
    paddle_a_up_flag = False
    paddle_a_down_flag = False
    paddle_b_up_flag = False
    paddle_b_down_flag = False

    # AI mode flag
    ai_mode = ai_mode

    def paddle_a_up():
        nonlocal paddle_a_up_flag
        paddle_a_up_flag = True

    def paddle_a_down():
        nonlocal paddle_a_down_flag
        paddle_a_down_flag = True

    def paddle_b_up():
        nonlocal paddle_b_up_flag
        paddle_b_up_flag = True

    def paddle_b_down():
        nonlocal paddle_b_down_flag
        paddle_b_down_flag = True

    def paddle_a_up_release():
        nonlocal paddle_a_up_flag
        paddle_a_up_flag = False

    def paddle_a_down_release():
        nonlocal paddle_a_down_flag
        paddle_a_down_flag = False

    def paddle_b_up_release():
        nonlocal paddle_b_up_flag
        paddle_b_up_flag = False

    def paddle_b_down_release():
        nonlocal paddle_b_down_flag
        paddle_b_down_flag = False

    # Keyboard bindings
    win.listen()
    win.onkeypress(paddle_a_up, "w")
    win.onkeyrelease(paddle_a_up_release, "w")
    win.onkeypress(paddle_a_down, "s")
    win.onkeyrelease(paddle_a_down_release, "s")
    if not ai_mode:
        win.onkeypress(paddle_b_up, "Up")
        win.onkeyrelease(paddle_b_up_release, "Up")
        win.onkeypress(paddle_b_down, "Down")
        win.onkeyrelease(paddle_b_down_release, "Down")

    # Score variables
    score_a = 0
    score_b = 0

    # Score display
    score_display = turtle.Turtle()
    score_display.speed(0)
    score_display.color("white")
    score_display.penup()
    score_display.hideturtle()
    score_display.goto(0, 260)
    score_display.write("Player A: 0  Player B: 0", align="center", font=("Courier", 24, "normal"))

    def update_score():
        """
        Updates the score display.
        - Clears the previous score and writes the updated score on the screen.
        """
        score_display.clear()
        score_display.write(f"Player A: {score_a}  Player B: {score_b}", align="center", font=("Courier", 24, "normal"))

    # Countdown before the game starts
    countdown_display = turtle.Turtle()
    countdown_display.speed(0)
    countdown_display.color("white")
    countdown_display.penup()
    countdown_display.hideturtle()
    countdown_display.goto(0, 0)

    for i in range(3, 0, -1):
        countdown_display.clear()
        countdown_display.write(i, align="center", font=("Courier", 48, "normal"))
        win.update()
        time.sleep(1)

    countdown_display.clear()

    # Initialize timing variables
    last_frame_time = time.time()
    accumulated_time = 0

    while True:
        """
        Continuously updates the game state.
        - Implements frame rate control using time-based movement
        - Moves the ball and paddles based on their respective flags.
        - Checks for collisions with the borders and paddles.
        - Updates the score when the ball crosses the left or right border.
        """
        current_time = time.time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time

        # Accumulate time and check if we should process the frame
        accumulated_time += delta_time
        if accumulated_time < FRAME_TIME:
            continue

        # Process as many frames as we've accumulated (usually just one)
        while accumulated_time >= FRAME_TIME:
            # Move the ball using delta time
            movement_x = (ball.dx * FRAME_TIME)
            movement_y = (ball.dy * FRAME_TIME)
            ball.setx(ball.xcor() + movement_x)
            ball.sety(ball.ycor() + movement_y)

            # Move paddles based on flags or AI
            paddle_movement = PADDLE_SPEED * FRAME_TIME

            # AI hesitation chance
            AI_HESITATION_CHANCE = 0.1  # 10% chance to hesitate

            if ai_mode:
                if random.random() > AI_HESITATION_CHANCE:
                    if ball.ycor() > paddle_b.ycor() and paddle_b.ycor() < 250:
                        paddle_b.sety(paddle_b.ycor() + paddle_movement)
                    elif ball.ycor() < paddle_b.ycor() and paddle_b.ycor() > -240:
                        paddle_b.sety(paddle_b.ycor() - paddle_movement)

            if paddle_a_up_flag and paddle_a.ycor() < 250:
                paddle_a.sety(paddle_a.ycor() + paddle_movement)
            if paddle_a_down_flag and paddle_a.ycor() > -240:
                paddle_a.sety(paddle_a.ycor() - paddle_movement)
            if not ai_mode:
                if paddle_b_up_flag and paddle_b.ycor() < 250:
                    paddle_b.sety(paddle_b.ycor() + paddle_movement)
                if paddle_b_down_flag and paddle_b.ycor() > -240:
                    paddle_b.sety(paddle_b.ycor() - paddle_movement)

            # Border checking
            if ball.ycor() > 290:
                ball.sety(290)
                ball.dy *= -1
                winsound.PlaySound("Ping_Sounds/Ping_FX/wall.wav", winsound.SND_ASYNC)

            if ball.ycor() < -290:
                ball.sety(-290)
                ball.dy *= -1
                winsound.PlaySound("Ping_Sounds/Ping_FX/wall.wav", winsound.SND_ASYNC)

            if ball.xcor() > 390:
                score_a += 1
                update_score()
                winsound.PlaySound("Ping_Sounds/Ping_FX/Score.wav", winsound.SND_FILENAME)
                ball.goto(0, 0)
                ball.dx *= -1

            if ball.xcor() < -390:
                score_b += 1
                update_score()
                winsound.PlaySound("Ping_Sounds/Ping_FX/Score.wav", winsound.SND_FILENAME)
                ball.goto(0, 0)
                ball.dx *= -1

            # Paddle and ball collisions
            if (ball.dx > 0 and ball.xcor() > 340 and ball.xcor() < 350 and
                    ball.ycor() < paddle_b.ycor() + 50 and ball.ycor() > paddle_b.ycor() - 50):
                ball.setx(340)
                ball.dx *= -1
                winsound.PlaySound("Ping_Sounds/Ping_FX/Paddle.wav", winsound.SND_ASYNC)

            if (ball.dx < 0 and ball.xcor() < -340 and ball.xcor() > -350 and
                    ball.ycor() < paddle_a.ycor() + 50 and ball.ycor() > paddle_a.ycor() - 50):
                ball.setx(-340)
                ball.dx *= -1
                winsound.PlaySound("Ping_Sounds/Ping_FX/Paddle.wav", winsound.SND_ASYNC)

            accumulated_time -= FRAME_TIME

        win.update()

# Start the title screen
title_screen()

# Keep the window open
turtle.mainloop()