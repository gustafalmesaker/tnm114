import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SPACESHIP_SPEED = 0.15   # Thrust force
ROTATE_SPEED = 2        # Rotation speed in degrees per frame
GRAVITY = 0.01         # Simulated gravity
TARGET_RADIUS = 20

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Spaceship Game")

# Spaceship settings
spaceship_img = pygame.Surface((50, 40), pygame.SRCALPHA)  # Transparent background
pygame.draw.polygon(spaceship_img, BLUE, [(0, 40), (25, 0), (50, 40)])  # Triangle spaceship
spaceship_rect = spaceship_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# Initial spaceship state
spaceship_x, spaceship_y = spaceship_rect.center
spaceship_vx, spaceship_vy = 0, 0  # Velocity in x and y directions
spaceship_angle = 0  # Initial rotation angle

# Random target position
target_x = SCREEN_WIDTH // 4
target_y = SCREEN_HEIGHT // 3

# Function to rotate spaceship
def rotate(surface, angle):
    return pygame.transform.rotate(surface, angle)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get key inputs for rotation and thrust
    keys = pygame.key.get_pressed()

    # Rotate spaceship
    if keys[pygame.K_LEFT]:
        spaceship_angle += ROTATE_SPEED
    if keys[pygame.K_RIGHT]:
        spaceship_angle -= ROTATE_SPEED

    # Apply thrust
    if keys[pygame.K_UP]:
        angle_radians = math.radians(spaceship_angle)
        spaceship_vx += math.sin(angle_radians) * SPACESHIP_SPEED
        spaceship_vy -= math.cos(angle_radians) * SPACESHIP_SPEED

    # Apply gravity
    spaceship_vy += GRAVITY

    # Update spaceship position based on velocity
    spaceship_x += spaceship_vx
    spaceship_y += spaceship_vy

    # Keep spaceship within screen bounds
    if spaceship_x < 0: spaceship_x = SCREEN_WIDTH
    if spaceship_x > SCREEN_WIDTH: spaceship_x = 0
    if spaceship_y < 0: spaceship_y = SCREEN_HEIGHT
    if spaceship_y > SCREEN_HEIGHT: spaceship_y = 0

    # Clear the screen
    screen.fill(WHITE)

    # Draw target
    pygame.draw.circle(screen, RED, (target_x, target_y), TARGET_RADIUS)

    # Draw spaceship (rotated)
    rotated_spaceship = rotate(spaceship_img, spaceship_angle)
    new_rect = rotated_spaceship.get_rect(center=(spaceship_x, spaceship_y))
    screen.blit(rotated_spaceship, new_rect.topleft)

    # Check for collision with target (simple distance check)
    distance_to_target = math.hypot(spaceship_x - target_x, spaceship_y - target_y)
    if distance_to_target < TARGET_RADIUS:
        print("Target collected!")
        running = False  # End the game

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
