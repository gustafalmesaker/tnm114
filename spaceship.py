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
GREEN = (0, 255, 0)

# Globals
SIZEFACTOR = 0.4

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load spaceship image and rotate it to face upwards
#spaceship_img = pygame.image.load("assets/r_blue.png")
big_image = pygame.image.load("assets/spaceship2.png")
gas_image = pygame.image.load("assets/gas.png")

#spaceship_img = pygame.transform.rotate(spaceship_img, 90)  # Rotate 90 degrees counter-clockwise to face up

# Scale the spaceship image to 20% of its original size
original_width, original_height = big_image.get_size()

######
crop_rect_blue_spaceship = pygame.Rect(0, 0, original_width // 5, original_height)
crop_rect_rock = pygame.Rect(0, 0, 7*original_width // 10, original_height)
# Crop the image using subsurface
spaceship_img = big_image.subsurface(crop_rect_blue_spaceship)
rock_img = big_image.subsurface(crop_rect_rock)
#####
spaceship_width, spaceship_height = spaceship_img.get_size()
new_width = int(spaceship_width * SIZEFACTOR)
new_height = int(spaceship_height * SIZEFACTOR)
spaceship_img = pygame.transform.scale(spaceship_img, (new_width, new_height))

# Update spaceship dimensions after scaling
spaceship_width, spaceship_height = spaceship_img.get_size()

# Spaceship properties
spaceship = {
    "x": WIDTH // 2,
    "y": HEIGHT // 4,
    "angle": 0,  # 0 degrees represents facing upwards
    "velocity_x": 0,
    "velocity_y": 0,
    "thrust": 0.1,
    "gravity": 0.02,
    "width": spaceship_width,
    "height": spaceship_height,
    "fuel": 100

}

# Landing zone properties
landing_zone = {
    "x": WIDTH // 3,
    "y": HEIGHT - 50,
    "width": 50,
    "height": 10,
}

# Game variables
running = True
score = 0

def draw_spaceship(x, y, angle, image):
    """Draws the spaceship using the provided image, rotated by the angle."""
    rotated_image = pygame.transform.rotate(image, -angle)  # Rotate image based on angle
    rect = rotated_image.get_rect(center=(x, y))  # Center the rotated image
    screen.blit(rotated_image, rect.topleft)

def check_collision(spaceship, zone):
    """Check if the spaceship has collided with the landing zone."""
    ship_rect = pygame.Rect(spaceship["x"] - spaceship["width"] // 2,
                            spaceship["y"] - spaceship["height"] // 2,
                            spaceship["width"],
                            spaceship["height"])

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
        spaceship["angle"] -= 3  # Rotate counter-clockwise
    if keys[pygame.K_RIGHT]:
        spaceship["angle"] += 3  # Rotate clockwise
    if keys[pygame.K_UP]:
        # Apply thrust based on the direction the spaceship is facing
        if spaceship["fuel"] > 0:
            spaceship["velocity_x"] += spaceship["thrust"] * math.sin(math.radians(spaceship["angle"]))
            spaceship["velocity_y"] -= spaceship["thrust"] * math.cos(math.radians(spaceship["angle"]))
            spaceship["fuel"] -= 0.1

    # Apply gravity
    spaceship["velocity_y"] += spaceship["gravity"]

    # Update spaceship position
    spaceship["x"] += spaceship["velocity_x"]
    spaceship["y"] += spaceship["velocity_y"]

    # Check for boundaries (if out of bounds, end game)
    if spaceship["x"] < 0 or spaceship["x"] > WIDTH or spaceship["y"] < 0 or spaceship["y"] > HEIGHT:
        print("Spaceship out of bounds! Game Over!")
        running = False

    # Check if spaceship lands in the zone
    if check_collision(spaceship, landing_zone):
        print("Landed successfully!")
        score += 1
        spaceship["fuel"] += 20
        if spaceship["fuel"] > 100:
            spaceship["fuel"] = 100
        # Reset spaceship position
        #spaceship["x"] = WIDTH // 2
        #spaceship["y"] = HEIGHT // 4
        #spaceship["velocity_x"] = 0
        #spaceship["velocity_y"] = 0
        #spaceship["angle"] = 0
        landing_zone["x"] = random.randint(landing_zone["width"] // 2, WIDTH - landing_zone["width"] // 2)
        landing_zone["y"] = random.randint(HEIGHT // 2, HEIGHT - landing_zone["height"] - 20)

    # Draw spaceship with the provided image
    draw_spaceship(spaceship["x"], spaceship["y"], spaceship["angle"], spaceship_img)

    # Draw landing zone
    #pygame.draw.rect(screen, GREEN, (landing_zone["x"], landing_zone["y"], landing_zone["width"], landing_zone["height"]))

    # Display score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    fuel_text = font.render(f"Fuel: {spaceship['fuel']:.1f}%", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(fuel_text, (WIDTH-200, 10))
    screen.blit(gas_image, (landing_zone["x"], landing_zone["y"]))

    # Refresh screen
    pygame.display.flip()
    clock.tick(60)
print("You scored ", score , " points!")
pygame.quit()
