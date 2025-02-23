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
projectile_gravity = gravity / 2

# Obstacles and platforms setup
platforms = []
obstacles = []
enemies = []
projectiles = []

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
    if random.randint(1, 3) <= 2:  # 2 in 3 chance to place an enemy on the platform
        create_enemy(platform)

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

def create_enemy(platform):
    enemy = turtle.Turtle()
    enemy.shape("square")
    enemy.color("red")
    enemy.shapesize(stretch_wid=1, stretch_len=1)
    enemy.penup()
    enemy.goto(platform.xcor(), platform.ycor() + 20)
    enemies.append(enemy)

def fire_projectile(enemy):
    projectile = turtle.Turtle()
    projectile.shape("square")
    projectile.color("black")
    projectile.shapesize(stretch_wid=0.5, stretch_len=0.5)
    projectile.penup()
    projectile.goto(enemy.xcor(), enemy.ycor())
    projectile.dy = 0
    projectiles.append(projectile)

def move_projectile_towards_player(projectile):
    if character.xcor() < projectile.xcor():
        projectile.setx(projectile.xcor() - 1)
    projectile.dy += projectile_gravity
    projectile.sety(projectile.ycor() + projectile.dy)

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

    if game_started and not game_paused:
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

        # Move enemies
        for enemy in enemies:
            enemy.setx(enemy.xcor() - 5)
            if enemy.xcor() < -400:
                enemy.hideturtle()
                enemies.remove(enemy)
            elif random.randint(1, 100) == 1:  # 1 in 100 chance to fire a projectile
                fire_projectile(enemy)

        # Move projectiles towards player
        for projectile in projectiles:
            move_projectile_towards_player(projectile)
            if projectile.xcor() < -400 or projectile.xcor() > 400 or projectile.ycor() < -300 or projectile.ycor() > 300 or projectile.ycor() < -250:
                projectile.hideturtle()
                projectiles.remove(projectile)

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

    for enemy in enemies:
        if character.distance(enemy) < 20:
            print("Game Over")
            turtle.bye()

    for projectile in projectiles:
        if character.distance(projectile) < 20:
            print("Game Over")
            turtle.bye()

    # Delay
    import time
    time.sleep(0.01)