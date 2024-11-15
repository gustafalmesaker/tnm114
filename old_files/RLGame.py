import pygame
import math
import random
import pickle  # To save and load agent data

# Import your QLearningAgent class
from old_files.RLAgent import QLearningAgent

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lunar Lander")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Globals
SIZEFACTOR = 0.4
SPEEDFACTOR = 10 #for testing
ANGLE = 10

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load spaceship image
big_image = pygame.image.load("assets/spaceship2.png")
original_width, original_height = big_image.get_size()
crop_rect_blue_spaceship = pygame.Rect(0, 0, original_width // 5, original_height)
spaceship_img = big_image.subsurface(crop_rect_blue_spaceship)

# Scale the spaceship image to 20% of its original size
spaceship_width, spaceship_height = spaceship_img.get_size()
spaceship_img = pygame.transform.scale(spaceship_img, (int(spaceship_width * SIZEFACTOR), int(spaceship_height * SIZEFACTOR)))

# Text
font = pygame.font.SysFont(None, 36)

# Spaceship properties
spaceship = {
    "x": 3 * WIDTH // 4,
    "y": 7 * HEIGHT // 8,
    "angle": 0,  # 0 degrees represents facing upwards
    "velocity_x": 0,
    "velocity_y": 0,
    "thrust": 0.1 * SPEEDFACTOR,
    "gravity": 0.005 * SPEEDFACTOR,
    "width": spaceship_img.get_width(),
    "height": spaceship_img.get_height(),
    "fuel": 100
}

# Landing zone properties
landing_zone_length = 100
landing_zone_height = 10

landing_zone = {
    "length": landing_zone_length,
    "height": landing_zone_height,
    "angle": 0,  # Angle of the landing zone
    "x": landing_zone_length + 100,
    "y": 100
    #"x": random.randint(landing_zone_length // 2, WIDTH - landing_zone_length // 2),
    #"y": random.randint(landing_zone_height // 2, HEIGHT - landing_zone_height - 20),
}


# Define state and action size
state_size = 5  # e.g., [x, y, velocity_x, velocity_y, angle]
action_size = 6  # Actions: [rotate left, rotate right, thrust, thrust + rotate left, thrust + rotate right, do nothing]

# Create a Q-learning agent
agent = QLearningAgent(state_size, action_size)

# Load agent data if available
try:
    with open("agent_data.pkl", "rb") as f:
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
    #landing_zone["x"] = random.randint(landing_zone["length"] // 2, WIDTH - landing_zone["length"] // 2)
    #landing_zone["y"] = random.randint(landing_zone["height"] // 2, HEIGHT - landing_zone["height"] - 20)
    landing_zone["x"] =landing_zone_length + 100
    landing_zone["y"] = 100

def reset_after_win():
    spaceship["fuel"] = 100
    landing_zone["x"] = random.randint(landing_zone["length"] // 2, WIDTH - landing_zone["length"] // 2)
    landing_zone["y"] = random.randint(landing_zone["height"] // 2, HEIGHT - landing_zone["height"] - 20)
    

# Draw spaceship function
def draw_spaceship(x, y, angle, image):
    """Draws the spaceship using the provided image, rotated by the angle."""
    rotated_image = pygame.transform.rotate(image, -angle)  # Rotate image based on angle
    rect = rotated_image.get_rect(center=(x, y))  # Center the rotated image
    screen.blit(rotated_image, rect.topleft)

# Draw landing zone
def draw_landing_zone():
    pygame.draw.rect(screen, GREEN, (landing_zone["x"] - landing_zone["length"] // 2,
                                     landing_zone["y"] - landing_zone["height"] // 2,
                                     landing_zone["length"],
                                     landing_zone["height"]))

# Check collision with landing zone
def check_collision(spaceship, zone):
    ship_rect = pygame.Rect(spaceship["x"] - spaceship["width"] // 2,
                            spaceship["y"] - spaceship["height"] // 2,
                            spaceship["width"],
                            spaceship["height"])
    zone_rect = pygame.Rect(zone["x"] - zone["length"] // 2, zone["y"] - zone["height"] // 2, zone["length"], zone["height"])
    return ship_rect.colliderect(zone_rect)

def calculate_distance(x1, y1, x2, y2):
    """Calculate the Euclidean distance between two points (x1, y1) and (x2, y2)."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Initialize previous distance to a large value at the start of the game
previous_distance = calculate_distance(spaceship["x"], spaceship["y"], landing_zone["x"], landing_zone["y"])


episode = 1
num_episodes = 50
succesful_landings = 0
out_of_fuel = 0

# Modify the game loop to include the new reward function
while episode < num_episodes:
    screen.fill(BLACK)
    state = [
        spaceship["x"] / WIDTH,
        spaceship["y"] / HEIGHT,
        spaceship["velocity_x"],
        spaceship["velocity_y"],
        spaceship["angle"] / 360
    ]
    action = agent.choose_action(state)


    fuel_consumtion = 0.5
    # Map actions to spaceship controls
    if action == 0:
        nothing = True
    elif action == 1:  # Rotate left
        spaceship["angle"] -= ANGLE
    elif action == 2:  # Rotate right
        spaceship["angle"] += ANGLE
    elif action == 3:  # Thrust
        if spaceship["fuel"] > 0:
            spaceship["velocity_x"] += spaceship["thrust"] * math.sin(math.radians(spaceship["angle"]))
            spaceship["velocity_y"] -= spaceship["thrust"] * math.cos(math.radians(spaceship["angle"]))
            spaceship["fuel"] -= fuel_consumtion
    elif action == 4:  # Thrust and rotate left
        spaceship["angle"] -= ANGLE
        if spaceship["fuel"] > 0:
            spaceship["velocity_x"] += spaceship["thrust"] * math.sin(math.radians(spaceship["angle"]))
            spaceship["velocity_y"] -= spaceship["thrust"] * math.cos(math.radians(spaceship["angle"]))
            spaceship["fuel"] -= fuel_consumtion
    elif action == 5:  # Thrust and rotate right
        spaceship["angle"] += ANGLE
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

    # Check boundaries
    if spaceship["x"] < 0 or spaceship["x"] > WIDTH or spaceship["y"] < 0 or spaceship["y"] > HEIGHT:
        reward = -1000  # Out of bounds penalty
        print("Spaceship out of bounds! Episode ", episode ," is over!")
        episode += 1
        reset_game()
        continue

    if spaceship["fuel"] < 0:
        reward = -100
        print("Spaceship ran out of fuel! Episode ", episode ," is over!")
        episode += 1
        out_of_fuel += 1
        continue
    # Check collision with landing zone
    if check_collision(spaceship, landing_zone):
        reward = 1000  # Successful landing
        succesful_landings += 1
        print(f"Successfully landed in episode {episode}!")
        episode += 1
        reset_after_win()
        continue

    # Calculate new distance to the landing zone
    current_distance = calculate_distance(spaceship["x"], spaceship["y"], landing_zone["x"], landing_zone["y"])

    # Reward if spaceship is moving closer to the landing zone
    if current_distance < previous_distance:
        reward = 10  # Positive reward for moving closer
    else:
     reward = -1  # Negative reward for moving further away

    #reward += current_distance - previous_distance

    #previous_distance = current_distance
    

    # Get next state
    next_state = [
        spaceship["x"] / WIDTH,
        spaceship["y"] / HEIGHT,
        spaceship["velocity_x"],
        spaceship["velocity_y"],
        spaceship["angle"] / 360
    ]

    # Agent learning
    agent.learn(state, action, reward, next_state)

    # Draw spaceship and landing zone
    draw_spaceship(spaceship["x"], spaceship["y"], spaceship["angle"], spaceship_img)
    draw_landing_zone()

    
    fuel_text = font.render(f"Fuel: {spaceship['fuel']:.1f}%", True, WHITE)
    screen.blit(fuel_text, (WIDTH-200, 10))

    pygame.display.flip()
    clock.tick(60)
print("Succesful landings: ", succesful_landings, "out of ", num_episodes)
print("Ran out of fuel ", out_of_fuel, " times!")


#save model
with open("agent_data.pkl", "wb") as f:
    pickle.dump({"q_table": agent.q_table}, f)
print(f"Agent data saved at episode {episode}.")