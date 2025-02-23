import turtle
import random

# Screen setup
screen = turtle.Screen()
screen.title("2D Platformer")
screen.bgcolor("skyblue")
screen.setup(width=800, height=600)
screen.tracer(0)

# Main menu setup
menu = turtle.Turtle()
menu.hideturtle()
menu.penup()
menu.goto(0, 0)
menu.write("Press SPACE to Start", align="center", font=("Arial", 24, "normal"))

ground = turtle.Turtle()
ground.shape("square")
ground.color("brown")
ground.shapesize(stretch_wid=0.5, stretch_len=40)
ground.penup()
ground.goto(0, -270)

# Character setup
character = turtle.Turtle()
character.shape("square")
character.color("black")
character.penup()
character.goto(-350, -250)
game_started = False
character.dy = 0
game_paused = False
character.dx = 0

# Gravity
gravity = -0.5

# Obstacles and platforms setup
platforms = []
obstacles = []

def create_platform():
    if not game_started:
        return
    platform = turtle.Turtle()
    platform.shape("square")
    platform.color("green")
    platform.shapesize(stretch_wid=0.5, stretch_len=10)
    platform.penup()
    platform.goto(400, random.randint(-200, -50))
    platforms.append(platform)

def create_obstacle():
    if not game_started:
        return
    obstacle = turtle.Turtle()
    obstacle.shape("square")
    obstacle.color("red")
    obstacle.shapesize(stretch_wid=random.randint(3, 6), stretch_len=0.5)
    obstacle.penup()
    obstacle.goto(400, -250)
    obstacles.append(obstacle)

# Character movement
def jump():
    if character.ycor() == -250:
        character.dy = 15

def duck():
    character.shapesize(stretch_wid=0.5, stretch_len=1)

def stand():
    character.shapesize(stretch_wid=1, stretch_len=1)

# Character movement
def move_left():
    character.setx(character.xcor() - 20)

def move_right():
    character.setx(character.xcor() + 20)

# Keyboard bindings
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")
def toggle_pause():
    global game_paused
    game_paused = not game_paused

screen.onkeypress(toggle_pause, "p")
screen.listen()
def start_game():
    global game_started
    game_started = True
    menu.clear()

screen.onkeypress(lambda: (start_game(), jump()), "space")
screen.onkeypress(duck, "Down")
screen.onkeyrelease(stand, "Down")

# Main game loop
while True:
    screen.update()

    if game_started and not game_paused:
        # Apply gravity
        character.dy += gravity
        character.sety(character.ycor() + character.dy)

    # Check for ground collision
    if character.ycor() < -250:
        character.sety(-250)
        character.dy = 0

    # Move obstacles
    for obstacle in obstacles:
        obstacle.setx(obstacle.xcor() - 5)
        if obstacle.xcor() < -400:
            obstacle.hideturtle()
            obstacles.remove(obstacle)

    # Move platforms
    for platform in platforms:
        platform.setx(platform.xcor() - 5)
        if platform.xcor() < -400:
            platform.hideturtle()
            platforms.remove(platform)

    # Create new obstacles
    if random.randint(1, 150) == 1:
        create_obstacle()

    # Create new platforms
    if random.randint(1, 200) == 1:
        create_platform()

    # Platform collision detection
    for platform in platforms:
        if character.ycor() > platform.ycor() and character.ycor() < platform.ycor() + 20 and abs(character.xcor() - platform.xcor()) < 50:
            character.sety(platform.ycor() + 20)
            character.dy = 0

    # Collision detection
    for obstacle in obstacles:
        if character.distance(obstacle) < 20:
            print("Game Over")
            turtle.bye()

    # Delay
    import time
    time.sleep(0.01)