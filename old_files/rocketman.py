import random
import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpaceDrift")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Globals
SIZEFACTOR = 0.4

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load images
spaceship_img = pygame.image.load("assets/spaceship3.png")
rock_img = pygame.image.load("assets/rock2.png")
fuel_img = pygame.image.load("assets/fuel2.png")

# Scale images
spaceship_img = pygame.transform.scale(spaceship_img, (int(spaceship_img.get_width() * SIZEFACTOR), int(spaceship_img.get_height() * SIZEFACTOR)))
rock_img = pygame.transform.scale(rock_img, (int(rock_img.get_width() * SIZEFACTOR), int(rock_img.get_height() * SIZEFACTOR)))

# Adjust fuel image size manually to match the scale of the game
FUEL_SCALE = 0.05  # Adjust this scaling factor as needed
fuel_img = pygame.transform.scale(fuel_img, (int(fuel_img.get_width() * FUEL_SCALE), int(fuel_img.get_height() * FUEL_SCALE)))

# Spaceship properties
spaceship_width, spaceship_height = spaceship_img.get_size()
spaceship = {
    "x": WIDTH // 2,
    "y": HEIGHT // 4,
    "angle": 0,  # 0 degrees represents facing upwards
    "velocity_x": 0,
    "velocity_y": 0,
    "thrust": 0.1,
    "gravity": 0.02,
    "width": spaceship_width,
    "height": spaceship_height
}

# Rock properties
rock = {
    "x": random.randint(0, WIDTH - rock_img.get_width()),
    "y": random.randint(0, HEIGHT - rock_img.get_height()),
}

# Fuel properties
fuel = {
    "x": random.randint(0, WIDTH - fuel_img.get_width()),
    "y": random.randint(0, HEIGHT - fuel_img.get_height()),
    "collected": False
}

# Game variables
running = True
score = 0

def draw_spaceship(x, y, angle, image):
    """Draws the spaceship using the provided image, rotated by the angle."""
    rotated_image = pygame.transform.rotate(image, -angle)  # Rotate image based on angle
    rect = rotated_image.get_rect(center=(x, y))  # Center the rotated image
    screen.blit(rotated_image, rect.topleft)

def check_collision(rect1, rect2):
    """Check if two rectangles collide."""
    return rect1.colliderect(rect2)

# Game loop
while running:
    screen.fill(BLACK)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle key presses for control
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        spaceship["angle"] -= 3  # Rotate counter-clockwise
    if keys[pygame.K_RIGHT]:
        spaceship["angle"] += 3  # Rotate clockwise
    if keys[pygame.K_UP]:
        # Apply thrust based on the direction the spaceship is facing
        spaceship["velocity_x"] += spaceship["thrust"] * math.sin(math.radians(spaceship["angle"]))
        spaceship["velocity_y"] -= spaceship["thrust"] * math.cos(math.radians(spaceship["angle"]))

    # Apply gravity
    spaceship["velocity_y"] += spaceship["gravity"]

    # Update spaceship position
    spaceship["x"] += spaceship["velocity_x"]
    spaceship["y"] += spaceship["velocity_y"]

    # Check for boundaries (if out of bounds, end game)
    if spaceship["x"] < 0 or spaceship["x"] > WIDTH or spaceship["y"] < 0 or spaceship["y"] > HEIGHT:
        print("Spaceship out of bounds! Game Over!")
        running = False

    # Collision with rock - check if the spaceship's center is within the rock's bounds
    spaceship_rect = pygame.Rect(spaceship["x"] - spaceship["width"] // 2,
                                  spaceship["y"] - spaceship["height"] // 2,
                                  spaceship["width"],
                                  spaceship["height"])
    rock_rect = pygame.Rect(rock["x"], rock["y"], rock_img.get_width(), rock_img.get_height())

    # Check if spaceship's center collides with the center of the rock
    spaceship_center = (spaceship["x"], spaceship["y"])
    rock_center = (rock["x"] + rock_img.get_width() // 2, rock["y"] + rock_img.get_height() // 2)

    # Calculate the distance between centers
    distance = math.sqrt((spaceship_center[0] - rock_center[0]) ** 2 + (spaceship_center[1] - rock_center[1]) ** 2)
    
    # Check for collision only if the spaceship is close enough
    if distance < (spaceship_width / 2 + rock_img.get_width() / 2):
        print("Collision with rock! Game Over!")
        running = False

    # Collision with fuel
    fuel_rect = pygame.Rect(fuel["x"], fuel["y"], fuel_img.get_width(), fuel_img.get_height())
    if not fuel["collected"] and check_collision(spaceship_rect, fuel_rect):
        print("Fuel collected!")
        score += 1
        fuel["collected"] = True  # Mark fuel as collected
        # Respawn fuel in a new location within boundaries
        fuel["x"] = random.randint(0, WIDTH - fuel_img.get_width())
        fuel["y"] = random.randint(0, HEIGHT - fuel_img.get_height())
        fuel["collected"] = False  # Make it visible again

    # Draw spaceship
    draw_spaceship(spaceship["x"], spaceship["y"], spaceship["angle"], spaceship_img)

    # Draw rock
    screen.blit(rock_img, (rock["x"], rock["y"]))

    # Draw fuel
    if not fuel["collected"]:
        screen.blit(fuel_img, (fuel["x"], fuel["y"]))

    # Display score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Refresh screen
    pygame.display.flip()
    clock.tick(60)

print("You scored", score, "points!")
pygame.quit()
