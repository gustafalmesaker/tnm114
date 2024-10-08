import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lunar Lander")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Spaceship properties
spaceship = {
    "x": WIDTH // 2,
    "y": HEIGHT // 4,
    "angle": 90,  # Start facing upwards (90 degrees)
    "velocity_x": 0,
    "velocity_y": 0,
    "thrust": 0.1,
    "gravity": 0.05,
}

# Landing zone properties
landing_zone = {
    "x": WIDTH // 3,
    "y": HEIGHT - 50,
    "width": 100,
    "height": 10,
}

# Game variables
running = True
score = 0

def draw_spaceship(x, y, angle):
    """Draws the spaceship as a rotated triangle based on its angle."""
    points = [
        (x, y),         # Tip of the spaceship (upward point)
        (x - 10, y + 20), # Bottom left
        (x + 10, y + 20)  # Bottom right
    ]
    rotated_points = []
    for px, py in points:
        # Rotate points around the spaceship's center based on angle
        translated_x = px - x
        translated_y = py - y
        rotated_x = translated_x * math.cos(math.radians(angle)) - translated_y * math.sin(math.radians(angle)) + x
        rotated_y = translated_x * math.sin(math.radians(angle)) + translated_y * math.cos(math.radians(angle)) + y
        rotated_points.append((rotated_x, rotated_y))
    pygame.draw.polygon(screen, WHITE, rotated_points)

def check_collision(spaceship, zone):
    """Check if the spaceship has collided with the landing zone."""
    ship_rect = pygame.Rect(spaceship["x"] - 10, spaceship["y"], 20, 20)
    zone_rect = pygame.Rect(zone["x"], zone["y"], zone["width"], zone["height"])

    return ship_rect.colliderect(zone_rect)

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
        spaceship["angle"] += 2  # Rotate counter-clockwise
    if keys[pygame.K_RIGHT]:
        spaceship["angle"] -= 2  # Rotate clockwise
    if keys[pygame.K_UP]:
        # Apply thrust in the direction the spaceship is pointing
        spaceship["velocity_x"] += spaceship["thrust"] * math.cos(math.radians(spaceship["angle"]))
        spaceship["velocity_y"] -= spaceship["thrust"] * math.sin(math.radians(spaceship["angle"]))

    # Apply gravity
    spaceship["velocity_y"] += spaceship["gravity"]

    # Update spaceship position
    spaceship["x"] += spaceship["velocity_x"]
    spaceship["y"] += spaceship["velocity_y"]

    # Check for boundaries (if out of bounds, end game)
    if spaceship["x"] < 0 or spaceship["x"] > WIDTH or spaceship["y"] < 0 or spaceship["y"] > HEIGHT:
        print("Spaceship out of bounds! Game Over!")
        print("You scored", score ," points!")
        running = False

    # Check if spaceship lands in the zone
    if check_collision(spaceship, landing_zone):
        print("Landed successfully!")
        score += 1
        # Reset spaceship position
        spaceship["x"] = WIDTH // 2
        spaceship["y"] = HEIGHT // 4
        spaceship["velocity_x"] = 0
        spaceship["velocity_y"] = 0

    # Draw spaceship
    draw_spaceship(spaceship["x"], spaceship["y"], spaceship["angle"])

    # Draw landing zone
    pygame.draw.rect(screen, GREEN, (landing_zone["x"], landing_zone["y"], landing_zone["width"], landing_zone["height"]))

    # Display score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Refresh screen
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
