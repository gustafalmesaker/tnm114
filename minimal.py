import pygame
import math
import random
import pickle  # To save and load agent data

# Import your QLearningAgent class
from RLAgent import QLearningAgent

#load file
loadAgentFile = "models/reduced_states.pkl"
saveAgentTo = "models/reduced_states.pkl"

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Drift")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Globals
SIZEFACTOR = 0.4
SPEEDFACTOR = 10 #for testing
ANGLE = 10
GRAVITY = 0.00
FUEL_AREA_WIDTH = (100, WIDTH-100)
FUEL_AREA_HEIGHT = (100, HEIGHT-100)
NUM_OF_EPISODES = 500

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
FUEL_SCALE = 0.08  # Adjust this scaling factor as needed
fuel_img = pygame.transform.scale(fuel_img, (int(fuel_img.get_width() * FUEL_SCALE), int(fuel_img.get_height() * FUEL_SCALE)))

# Text
font = pygame.font.SysFont(None, 36)

# Spaceship properties
spaceship = {
    "x": 3 * WIDTH // 4,
    "y": 6 * HEIGHT // 8,
    "angle": 0,  
    "velocity_x": 0,
    "velocity_y": 0,
    "thrust": 0.1 * SPEEDFACTOR,
    "gravity": GRAVITY * SPEEDFACTOR,
    "width": spaceship_img.get_width(),
    "height": spaceship_img.get_height(),
    "fuel": 100,
    "episode": 1
}

# Fuel properties
fuel = {
    "x": WIDTH // 2, 
    "y": HEIGHT // 2,
    #"x": random.randint(100, WIDTH-100),
    #"y": random.randint(100, HEIGHT-100)
    "index": 0
}

fuel_position = [[WIDTH // 2, HEIGHT // 2], [3 * WIDTH // 4, HEIGHT // 4], [3 * WIDTH // 4, 3 * HEIGHT // 4], [WIDTH // 4, HEIGHT // 4], [3 * WIDTH // 4, HEIGHT // 2]]

# Define state and action size
state_size = 6  
action_size = 4

# Create a Q-learning agent
agent = QLearningAgent(state_size, action_size)

# Load agent data if available
try:
    with open(loadAgentFile, "rb") as f:
        agent_data = pickle.load(f)
        agent.q_table = agent_data["q_table"]
        print("Agent data loaded successfully!")
except FileNotFoundError:
    print("No previous agent data found, starting fresh.")

# Function to reset the spaceship and landing zone properties
def reset_game():
    spaceship["x"] = 3 * WIDTH // 4
    spaceship["y"] = 7 * HEIGHT // 8
    spaceship["angle"] = 0
    spaceship["velocity_x"] = 0
    spaceship["velocity_y"] = 0
    spaceship["fuel"] = 100
    fuel["index"] = 0
    fuel["x"] , fuel["y"] = fuel_position[fuel["index"]]
    
    spaceship["episode"] += 1
    

def reset_after_win():
    spaceship["fuel"] += 25
    if spaceship["fuel"] > 100:
        spaceship["fuel"] = 100
    fuel["index"] += 1
    fuel["index"] = fuel["index"] % len(fuel_position)
    fuel["x"] , fuel["y"] = fuel_position[fuel["index"]]
    #fuel["x"] = random.randint(100, WIDTH-100)
    #fuel["y"] = random.randint(100, HEIGHT-100)
    
    

# Draw spaceship function
def draw_spaceship(x, y, angle, image):
    """Draws the spaceship using the provided image, rotated by the angle."""
    rotated_image = pygame.transform.rotate(image, -angle)  # Rotate image based on angle
    rect = rotated_image.get_rect(center=(x, y))  # Center the rotated image
    screen.blit(rotated_image, rect.topleft)

    
def draw_fuel():
    coord_x,coord_y = fuel["x"], fuel["y"]
    screen.blit(fuel_img,[coord_x, coord_y])

def check_collision(spaceship, fuel):
    fuel_width = fuel_img.get_width()
    fuel_height = fuel_img.get_height()
    ship_rect = pygame.Rect(spaceship["x"] - spaceship["width"] // 2,
                            spaceship["y"] - spaceship["height"] // 2,
                            spaceship["width"],
                            spaceship["height"])
    zone_rect = pygame.Rect(fuel["x"] - fuel_width // 2, fuel["y"] - fuel_height // 2, fuel_width, fuel_height)
    return ship_rect.colliderect(zone_rect)

def calculate_distance(x1, y1, x2, y2):
    """Calculate the Euclidean distance between two points (x1, y1) and (x2, y2)."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Initialize previous distance to a large value at the start of the game
previous_distance = calculate_distance(spaceship["x"], spaceship["y"], fuel["x"], fuel["y"])

succesful_landings = 0
out_of_fuel = 0

# Modify the game loop to include the new reward function
while spaceship["episode"] < NUM_OF_EPISODES:
    screen.fill(BLACK)
    state = [
        spaceship["x"] / WIDTH,
        spaceship["y"] / HEIGHT,
        math.sqrt(spaceship["velocity_x"]*spaceship["velocity_x"] + spaceship["velocity_y"] * spaceship["velocity_y"]),
        spaceship["angle"] / 360,
        (fuel["x"] - spaceship["x"]) / WIDTH,  # relative x-position of the fuel
        (fuel["y"] - spaceship["y"]) / HEIGHT,  # relative y-position of the fuel
    ]

    action = agent.choose_action(state)


    fuel_consumtion = 0.5
    # Map actions to spaceship controls
    if action == 0:
        doNothing = True
    elif action == 1:  # Rotate left
        spaceship["angle"] -= ANGLE
    elif action == 2:  # Rotate right
        spaceship["angle"] += ANGLE
    elif action == 3:  # Thrust
        if spaceship["fuel"] > 0:
            spaceship["velocity_x"] += spaceship["thrust"] * math.sin(math.radians(spaceship["angle"]))
            spaceship["velocity_y"] -= spaceship["thrust"] * math.cos(math.radians(spaceship["angle"]))
            spaceship["fuel"] -= fuel_consumtion
    
    
    #Display action
    action_text = font.render(f"Action: {action:.0f}", True, WHITE)
    screen.blit(action_text, (10, 10))
        

    # Apply gravity
    spaceship["velocity_y"] += spaceship["gravity"]

    # Update spaceship position
    spaceship["x"] += spaceship["velocity_x"]
    spaceship["y"] += spaceship["velocity_y"]

    #Reward for the RL agent
    reward = 0

    if abs(spaceship["velocity_x"] + spaceship["velocity_y"]) < 0.01:
        reward -= 0.01

    # Check boundaries
    if spaceship["x"] < 0 or spaceship["x"] > WIDTH or spaceship["y"] < 0 or spaceship["y"] > HEIGHT:
        reward -=1000  # Out of bounds penalty
        print("Episode",spaceship["episode"],"is over!")
        reset_game()
        continue

    if spaceship["fuel"] < 0:
        reward -= 0.5
        print("Spaceship ran out of fuel! Episode ",spaceship["episode"]," is over!")
        out_of_fuel += 1
        continue
    # Check collision with landing zone
    if check_collision(spaceship, fuel):
        reward += 100  # Successful landing
        succesful_landings += 1
        print(f"W")
        reset_after_win()
        continue

    # Calculate new distance to the landing zone
    current_distance = calculate_distance(spaceship["x"], spaceship["y"], fuel["x"] , fuel["y"])

    # Reward if spaceship is moving closer to the landing zone
    if current_distance < previous_distance:
        reward += 0.15  # Positive reward for moving closer
    else:
        reward -= 0.1  # Negative reward for moving further away

    # Get next state
    next_state = [
        spaceship["x"] / WIDTH,
        spaceship["y"] / HEIGHT,
        math.sqrt(spaceship["velocity_x"]*spaceship["velocity_x"] + spaceship["velocity_y"] * spaceship["velocity_y"]),
        spaceship["angle"] / 360,
        (fuel["x"] - spaceship["x"]) / WIDTH,  # relative x-position of the fuel
        (fuel["y"] - spaceship["y"]) / HEIGHT,  # relative y-position of the fuel
    ]


    # Agent learning
    agent.learn(state, action, reward, next_state)

    # Draw spaceship and landing zone
    draw_spaceship(spaceship["x"], spaceship["y"], spaceship["angle"], spaceship_img)
    draw_fuel()
    

    # Draw fuel
    screen.blit(fuel_img, (fuel["x"], fuel["y"]))
    fuel_text = font.render(f"Fuel: {spaceship['fuel']:.1f}%", True, WHITE)
    screen.blit(fuel_text, (WIDTH-200, 10))

    pygame.display.flip()
    clock.tick(60)
print("Succesful landings: ",succesful_landings," out of ",NUM_OF_EPISODES)
print("Ran out of fuel ",out_of_fuel," times!")


#save model
with open(saveAgentTo, "wb") as f:
    pickle.dump({"q_table": agent.q_table}, f)
print(f"Agent data saved.")