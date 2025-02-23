import turtle

# Set up the screen
win = turtle.Screen()
win.title("Pong")
win.bgcolor("black")
win.setup(width=800, height=600)
win.tracer(0)

# Title screen
def title_screen():
    """
    Displays the title screen with game options.
    - Creates and configures turtle objects to display the game title and options.
    - Listens for key presses to start the game.
    """
    title = turtle.Turtle()
    title.speed(0)
    title.color("white")
    title.penup()
    title.hideturtle()
    title.goto(0, 100)
    title.write("Ping", align="center", font=("Courier", 36, "normal"))

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
    win.onkeypress(lambda: start_game(False), "1")
    win.onkeypress(lambda: start_game(True), "2")

def start_game(ai_mode):
    """
    Clears the title screen and starts the main game.
    - Clears the screen and reinitializes the game window.
    - Calls main_game() to start the main game.
    """
    win.clearscreen()
    win.title("Pong")
    win.bgcolor("black")
    win.setup(width=800, height=600)
    win.tracer(0)
    main_game()

# Main game function
def main_game(ai_mode):
    """
    Sets up and runs the main game loop.
    - Initializes paddles, ball, and score display.
    - Defines functions to handle paddle movements and score updates.
    - Sets up keyboard bindings for paddle controls.
    - Contains the main game loop that updates the game state, moves the ball and paddles, checks for collisions, and updates the score.
    """
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
    ball.speed(40)
    ball.shape("square")
    ball.color("white")
    ball.penup()
    ball.goto(0, 0)
    ball.dx = 0.1
    ball.dy = -0.1

    # Paddle speed
    paddle_speed = 0.1

    # Movement flags
    paddle_a_up_flag = False
    paddle_a_down_flag = False
    paddle_b_up_flag = False
    paddle_b_down_flag = False

    # AI mode flag
    ai_mode = ai_mode

    # AI paddle speed
    ai_paddle_speed = 0.1

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
        turtle.time.sleep(1)

    countdown_display.clear()

    while True:
        """
        Continuously updates the game state.
        - Moves the ball and paddles based on their respective flags.
        - Checks for collisions with the borders and paddles.
        - Updates the score when the ball crosses the left or right border.
        - Adds a delay to control the frame rate.
        """
        win.update()

        # Move the ball
        ball.setx(ball.xcor() + ball.dx)
        ball.sety(ball.ycor() + ball.dy)

        # Move paddles based on flags or AI
        if ai_mode:
            if ball.ycor() > paddle_b.ycor() and paddle_b.ycor() < 250:
                paddle_b.sety(paddle_b.ycor() + ai_paddle_speed)
            elif ball.ycor() < paddle_b.ycor() and paddle_b.ycor() > -240:
                paddle_b.sety(paddle_b.ycor() - ai_paddle_speed)
        else:
            if paddle_b_up_flag and paddle_b.ycor() < 250:
                paddle_b.sety(paddle_b.ycor() + paddle_speed)
            if paddle_b_down_flag and paddle_b.ycor() > -240:
                paddle_b.sety(paddle_b.ycor() - paddle_speed)

        if paddle_a_up_flag and paddle_a.ycor() < 250:
            paddle_a.sety(paddle_a.ycor() + paddle_speed)
        if paddle_a_down_flag and paddle_a.ycor() > -240:
            paddle_a.sety(paddle_a.ycor() - paddle_speed)
        if paddle_b_up_flag and paddle_b.ycor() < 250:
            paddle_b.sety(paddle_b.ycor() + paddle_speed)
        if paddle_b_down_flag and paddle_b.ycor() > -240:
            paddle_b.sety(paddle_b.ycor() - paddle_speed)

        # Border checking
        if ball.ycor() > 290:
            ball.sety(290)
            ball.dy *= -1

        if ball.ycor() < -290:
            ball.sety(-290)
            ball.dy *= -1

        if ball.xcor() > 390:
            score_b += 1
            update_score()
            ball.goto(0, 0)
            ball.dx *= -1

        if ball.xcor() < -390:
            score_a += 1
            update_score()
            ball.goto(0, 0)
            ball.dx *= -1

        # Paddle and ball collisions
        if (ball.dx > 0 and ball.xcor() > 340 and ball.xcor() < 350 and
                ball.ycor() < paddle_b.ycor() + 50 and ball.ycor() > paddle_b.ycor() - 50):
            ball.setx(340)
            ball.dx *= -1

        if (ball.dx < 0 and ball.xcor() < -340 and ball.xcor() > -350 and
                ball.ycor() < paddle_a.ycor() + 50 and ball.ycor() > paddle_a.ycor() - 50):
            ball.setx(-340)
            ball.dx *= -1

        # Add a delay to control the frame rate
        turtle.delay(10)

# Start the title screen
title_screen()

# Keep the window open
turtle.mainloop()