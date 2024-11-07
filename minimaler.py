import pygame
import math
import random
import pickle  # To save and load agent data

# Import your QLearningAgent class
from RLAgent import QLearningAgent
from DQN import DQNAgent, DQNNetwork



#load file
loadAgentFile = "models/3000_dqn.pkl"
saveAgentTo = "models/4000_dqn.pkl"

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Drift")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Globals
SIZEFACTOR = 0.4
SPEEDFACTOR = 3 #for testing
ANGLE = 10
GRAVITY = 0.01
FUEL_AREA_WIDTH = (100, WIDTH-100)
FUEL_AREA_HEIGHT = (100, HEIGHT-100)
NUM_OF_EPISODES = 1000
EPISODIAL_REWARD = 0
TOTAL_REWARD = 0


# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load images
spaceship_img = pygame.image.load("assets/spaceship3.png")
#rock_img = pygame.image.load("assets/rock2.png")
#fuel_img = pygame.image.load("assets/fuel2.png")

# Scale images
spaceship_img = pygame.transform.scale(spaceship_img, (int(spaceship_img.get_width() * SIZEFACTOR), int(spaceship_img.get_height() * SIZEFACTOR)))
#rock_img = pygame.transform.scale(rock_img, (int(rock_img.get_width() * SIZEFACTOR), int(rock_img.get_height() * SIZEFACTOR)))

# Adjust fuel image size manually to match the scale of the game
FUEL_SCALE = 0.08  # Adjust this scaling factor as needed
#fuel_img = pygame.transform.scale(fuel_img, (int(fuel_img.get_width() * FUEL_SCALE), int(fuel_img.get_height() * FUEL_SCALE)))

# Text
font = pygame.font.SysFont(None, 36)

# Spaceship properties
spaceship = {
    "x": 3 * WIDTH // 4,
    "y": 6 * HEIGHT // 8,
    "angle": 0,  
    "velocity_x": 0,
    "velocity_y": 0,
    "thrust": 0.2 * SPEEDFACTOR,
    "gravity": GRAVITY * SPEEDFACTOR,
    "width": spaceship_img.get_width(),
    "height": spaceship_img.get_height(),
    "fuel": 100,
    "episode": 1
}

# Define state and action size
state_size = 4  
action_size = 4

# Create a Q-learning agent
#agent = QLearningAgent(state_size, action_size)

# Instantiate the DQN agent
agent = DQNAgent(state_size, action_size)

# Load agent model if available
try:
    with open(loadAgentFile, "rb") as f:
        state_dict = pickle.load(f)
        if "fc1.weight" in state_dict:  # Check for correct model structure
            agent.q_network.load_state_dict(state_dict)
            print("Agent model loaded successfully!")
        else:
            print("Incompatible model format. Starting fresh.")
except FileNotFoundError:
    print("No previous model data found, starting fresh.")


# Function to reset the spaceship and landing zone properties
def reset_game():
    spaceship["x"] = 3 * WIDTH // 4
    spaceship["y"] = 7 * HEIGHT // 8
    spaceship["angle"] = 0
    spaceship["velocity_x"] = 0
    spaceship["velocity_y"] = 0
    spaceship["fuel"] = 100
    spaceship["episode"] += 1
    
    

# Draw spaceship function
def draw_spaceship(x, y, angle, image):
    """Draws the spaceship using the provided image, rotated by the angle."""
    rotated_image = pygame.transform.rotate(image, -angle)  # Rotate image based on angle
    rect = rotated_image.get_rect(center=(x, y))  # Center the rotated image
    screen.blit(rotated_image, rect.topleft)

def calculate_distance(x1, y1, x2, y2):
    """Calculate the Euclidean distance between two points (x1, y1) and (x2, y2)."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Initialize previous distance to a large value at the start of the game
#previous_distance = calculate_distance(spaceship["x"], spaceship["y"], fuel["x"], fuel["y"])

#succesful_landings = 0
out_of_fuel = 0

# Modify the game loop to include the new reward function
while spaceship["episode"] < NUM_OF_EPISODES:
    screen.fill(BLACK)
    state = [
        spaceship["x"],
        spaceship["y"],
        math.sqrt(spaceship["velocity_x"]*spaceship["velocity_x"] + spaceship["velocity_y"] * spaceship["velocity_y"]),
        spaceship["angle"] / 360
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

    # Check boundaries
    if spaceship["x"] < 0 or spaceship["x"] > WIDTH or spaceship["y"] < 0 or spaceship["y"] > HEIGHT:
        reward = reward - 10  # Out of bounds penalty
        print("Episode",spaceship["episode"],"is over! || Reward: ", EPISODIAL_REWARD)
        TOTAL_REWARD = EPISODIAL_REWARD + TOTAL_REWARD
        EPISODIAL_REWARD = 0
        reset_game()
        continue


    if spaceship["fuel"] < 0:
        reward -= 0.5
        print("Spaceship ran out of fuel! Episode ",spaceship["episode"]," is over!")
        out_of_fuel += 1
        EPISODIAL_REWARD = 0

        continue

    current_distance = calculate_distance(spaceship["x"], spaceship["y"], WIDTH // 2, HEIGHT // 2)

    if current_distance < 50:
        reward = reward + 100
    elif current_distance < 80:
        reward = reward + 75
    elif current_distance < 100:
        reward = reward + 40
    elif current_distance < 200:
        reward = reward + 20
    elif current_distance < 300:
        reward = reward + 10

    # Get next state
    next_state = [
        spaceship["x"],
        spaceship["y"],
        math.sqrt(spaceship["velocity_x"]*spaceship["velocity_x"] + spaceship["velocity_y"] * spaceship["velocity_y"]),
        spaceship["angle"] / 360
    ]

    EPISODIAL_REWARD = EPISODIAL_REWARD + reward
    # Store experience in replay memory
    agent.store_experience(state, action, reward, next_state, done=False)

    # Update the DQN model
    agent.update_q_network()


    # Draw fueltext
    fuel_text = font.render(f"Fuel: {spaceship['fuel']:.1f}%", True, WHITE)
    screen.blit(fuel_text, (WIDTH-200, 10))
    
    distance_text = font.render(f"Distance: {current_distance:.1f}", True, WHITE)
    screen.blit(distance_text, (WIDTH-200, 50))

    #Draw line between fuel and ship
    #pygame.draw.line(color=(255,255,0), surface=screen, width=10, start_pos=[fuel["x"], fuel["y"]], end_pos=[spaceship["x"], spaceship["y"]])

    #DRAW CIRCLES FOR REWARD VIZ
    pygame.draw.circle(color=(0,0,255), radius=300, center=(WIDTH // 2 , HEIGHT // 2), surface=screen)
    pygame.draw.circle(color=(0,200,200), radius=200, center=(WIDTH // 2 , HEIGHT // 2), surface=screen)
    pygame.draw.circle(color=(0,255,0), radius=100, center=(WIDTH // 2 , HEIGHT // 2), surface=screen)
    pygame.draw.circle(color=(200,200,0), radius=80, center=(WIDTH // 2 , HEIGHT // 2), surface=screen)
    pygame.draw.circle(color=(255,0,0), radius=50, center=(WIDTH // 2 , HEIGHT // 2), surface=screen)
    
    
    pygame.draw.line(color=(255,255,0), 
                     surface=screen, 
                     width=10, 
                     start_pos=[WIDTH // 2, HEIGHT // 2], 
                     end_pos=[spaceship["x"], spaceship["y"]])

    # Draw spaceship
    draw_spaceship(spaceship["x"], spaceship["y"], spaceship["angle"], spaceship_img)
    pygame.display.flip()
    clock.tick(60)

print("Total Reward: ", TOTAL_REWARD)
with open(saveAgentTo, "wb") as f:
    pickle.dump(agent.q_network.state_dict(), f)
print("Agent model saved.")
