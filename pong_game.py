import turtle

# Set up the screen
win = turtle.Screen()
win.title("Ping")
win.bgcolor("black")
win.setup(width=800, height=600)
win.tracer(0)

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
ball.dx = 0.2
ball.dy = -0.2

# Paddle speed
paddle_speed = 0.2

# Movement flags
paddle_a_up_flag = False
paddle_a_down_flag = False
paddle_b_up_flag = False
paddle_b_down_flag = False

# Functions to set movement flags
def paddle_a_up():
    global paddle_a_up_flag
    paddle_a_up_flag = True

def paddle_a_down():
    global paddle_a_down_flag
    paddle_a_down_flag = True

def paddle_b_up():
    global paddle_b_up_flag
    paddle_b_up_flag = True

def paddle_b_down():
    global paddle_b_down_flag
    paddle_b_down_flag = True

def paddle_a_up_release():
    global paddle_a_up_flag
    paddle_a_up_flag = False

def paddle_a_down_release():
    global paddle_a_down_flag
    paddle_a_down_flag = False

def paddle_b_up_release():
    global paddle_b_up_flag
    paddle_b_up_flag = False

def paddle_b_down_release():
    global paddle_b_down_flag
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

# Main game loop
while True:
    win.update()

    # Move the ball
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # Move paddles based on flags
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
        ball.goto(0, 0)
        ball.dx *= -1

    if ball.xcor() < -390:
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