import pygame
import sys
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the display
window_size = (800, 800)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Game of Life")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)

# Define grid properties
cols, rows = 50, 50  # Number of columns and rows in the grid
cell_size = window_size[0] // cols  # Size of each cell

# Create the grid, initially all cells are dead (0)
grid = np.zeros((rows, cols), dtype=int)

# Function to draw the grid and cells
def draw_grid(screen, grid, cell_size):
    for row in range(rows):
        for col in range(cols):
            # Determine color based on cell state
            color = WHITE if grid[row][col] == 1 else BLACK
            # Draw the cell as a rectangle
            pygame.draw.rect(screen, color, 
                             (col * cell_size, row * cell_size, cell_size, cell_size))
            # Draw the grid lines
            pygame.draw.rect(screen, GRAY, 
                             (col * cell_size, row * cell_size, cell_size, cell_size), 1)

# Function to count the number of live neighbors for a given cell
def count_live_neighbors(grid, row, col):
    neighbors = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),         (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]
    count = 0
    for dr, dc in neighbors:
        r, c = row + dr, col + dc
        # Ensure neighbor is within bounds
        if 0 <= r < rows and 0 <= c < cols:
            count += grid[r][c]
    return count

# Function to update the grid according to the Game of Life rules
def update_grid(grid):
    # Create a copy of the grid to apply changes
    new_grid = np.copy(grid)
    for row in range(rows):
        for col in range(cols):
            live_neighbors = count_live_neighbors(grid, row, col)

            # Apply the rules of the Game of Life
            if grid[row][col] == 1:  # If the cell is alive
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[row][col] = 0  # Cell dies
            else:  # If the cell is dead
                if live_neighbors == 3:
                    new_grid[row][col] = 1  # Cell becomes alive
    return new_grid

# Main loop
running = True
paused = True  # Start in paused state to allow user to set initial configuration
clock = pygame.time.Clock()
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  # Toggle pause/play with spacebar
            elif event.key == pygame.K_r:
                # Reset the grid when 'r' is pressed
                grid = np.zeros((rows, cols), dtype=int)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle cell state on mouse click
            x, y = pygame.mouse.get_pos()
            col, row = x // cell_size, y // cell_size
            grid[row][col] = 1 - grid[row][col]  # Toggle between 1 and 0

    # Fill the screen with a black background
    screen.fill(BLACK)

    # Draw the grid
    draw_grid(screen, grid, cell_size)

    # Update the grid if the game is not paused
    if not paused:
        grid = update_grid(grid)

    # Update the display
    pygame.display.flip()

    # Limit the frame rate to 10 frames per second for better visualization
    clock.tick(10)

# Quit Pygame
pygame.quit()
sys.exit()
