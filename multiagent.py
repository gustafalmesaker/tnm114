import pygame
import math
import random
import pickle
from RLAgent import QLearningAgent
from main import check_collision, calculate_distance, draw_spaceship, draw_fuel

# Load file
loadAgentFile = "models/reduced_states"
saveAgentTo = "models/minimal_action"

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Drift")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Globals
SIZEFACTOR = 0.4
SPEEDFACTOR = 10
ANGLE = 10
GRAVITY = 0.00
NUM_OF_EPISODES = 50
NUM_AGENTS = 3

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load images
spaceship_img = pygame.image.load("assets/spaceship3.png")
fuel_img = pygame.image.load("assets/fuel2.png")
spaceship_img = pygame.transform.scale(spaceship_img, (int(spaceship_img.get_width() * SIZEFACTOR), int(spaceship_img.get_height() * SIZEFACTOR)))
FUEL_SCALE = 0.08
fuel_img = pygame.transform.scale(fuel_img, (int(fuel_img.get_width() * FUEL_SCALE), int(fuel_img.get_height() * FUEL_SCALE)))

# Text
font = pygame.font.SysFont(None, 36)

# Fuel positions
fuel_position = [[WIDTH // 2, HEIGHT // 2], [3 * WIDTH // 4, HEIGHT // 4], [3 * WIDTH // 4, 3 * HEIGHT // 4], [WIDTH // 4, HEIGHT // 4], [3 * WIDTH // 4, HEIGHT // 2]]

# Define state and action size
state_size = 6
action_size = 4

# Create multiple Q-learning agents
agents = [QLearningAgent(state_size, action_size) for _ in range(NUM_AGENTS)]

# Initialize agents' states and individual episode counters
agents_states = [
    {"spaceship": {
        "x": 3 * WIDTH // 4, "y": 6 * HEIGHT // 8, "angle": 0, "velocity_x": 0, "velocity_y": 0, "thrust": 0.1 * SPEEDFACTOR,
        "gravity": GRAVITY * SPEEDFACTOR, "width": spaceship_img.get_width(), "height": spaceship_img.get_height(),
        "fuel": 100, "episode": 1
    },
    "fuel": {"x": fuel_position[0][0], "y": fuel_position[0][1], "index": 0}} for _ in range(NUM_AGENTS)
]

# Load agents' data if available
for i, agent in enumerate(agents):
    try:
        with open(f"{loadAgentFile}_{i}.pkl", "rb") as f:
            agent_data = pickle.load(f)
            agent.q_table = agent_data["q_table"]
            print(f"Agent {i} data loaded successfully!")
    except FileNotFoundError:
        print(f"No previous data for agent {i}, starting fresh.")

# Function to reset the spaceship and landing zone properties for an agent
def reset_game(agent_state):
    agent_state["spaceship"].update({
        "x": 3 * WIDTH // 4, "y": 7 * HEIGHT // 8, "angle": 0,
        "velocity_x": 0, "velocity_y": 0, "fuel": 100
    })
    agent_state["fuel"]["index"] = 0
    agent_state["fuel"]["x"], agent_state["fuel"]["y"] = fuel_position[agent_state["fuel"]["index"]]
    agent_state["spaceship"]["episode"] += 1

def reset_after_win(agent_state):
    agent_state["spaceship"]["fuel"] += 25
    if agent_state["spaceship"]["fuel"] > 100:
        agent_state["spaceship"]["fuel"] = 100
    agent_state["fuel"]["index"] = (agent_state["fuel"]["index"] + 1) % len(fuel_position)
    agent_state["fuel"]["x"], agent_state["fuel"]["y"] = fuel_position[agent_state["fuel"]["index"]]

# Main game loop
while all(agent_state["spaceship"]["episode"] < NUM_OF_EPISODES for agent_state in agents_states):
    screen.fill(BLACK)

    for i, agent in enumerate(agents):
        agent_state = agents_states[i]
        spaceship = agent_state["spaceship"]
        fuel = agent_state["fuel"]

        # Define the state
        state = [
            spaceship["x"] / WIDTH,
            spaceship["y"] / HEIGHT,
            math.sqrt(spaceship["velocity_x"]**2 + spaceship["velocity_y"]**2),
            spaceship["angle"] / 360,
            (fuel["x"] - spaceship["x"]) / WIDTH,
            (fuel["y"] - spaceship["y"]) / HEIGHT
        ]

        # Agent chooses an action
        action = agent.choose_action(state)
        
        # Map actions to spaceship controls
        fuel_consumption = 0.5
        if action == 1:  # Rotate left
            spaceship["angle"] -= ANGLE
        elif action == 2:  # Rotate right
            spaceship["angle"] += ANGLE
        elif action == 3 and spaceship["fuel"] > 0:  # Thrust
            spaceship["velocity_x"] += spaceship["thrust"] * math.sin(math.radians(spaceship["angle"]))
            spaceship["velocity_y"] -= spaceship["thrust"] * math.cos(math.radians(spaceship["angle"]))
            spaceship["fuel"] -= fuel_consumption

        # Apply gravity
        spaceship["velocity_y"] += spaceship["gravity"]

        # Update spaceship position
        spaceship["x"] += spaceship["velocity_x"]
        spaceship["y"] += spaceship["velocity_y"]

        # Calculate reward and check conditions
        reward = -0.01  # Small penalty to encourage efficiency
        if spaceship["fuel"] <= 0:
            reward -= 0.5  # Penalty for running out of fuel
            reset_game(agent_state)
            continue

        if spaceship["x"] < 0 or spaceship["x"] > WIDTH or spaceship["y"] < 0 or spaceship["y"] > HEIGHT:
            reward -= 1000  # Out of bounds penalty
            reset_game(agent_state)
            continue

        # Check collision with fuel
        if check_collision(spaceship, fuel):
            reward += 100  # Reward for successful landing
            reset_after_win(agent_state)
            continue

        # Calculate distance to the fuel
        distance = calculate_distance(spaceship["x"], spaceship["y"], fuel["x"], fuel["y"])
        reward += 0.15 if distance < previous_distance else -0.1
        previous_distance = distance

        # Define next state
        next_state = [
            spaceship["x"] / WIDTH,
            spaceship["y"] / HEIGHT,
            math.sqrt(spaceship["velocity_x"]**2 + spaceship["velocity_y"]**2),
            spaceship["angle"] / 360,
            (fuel["x"] - spaceship["x"]) / WIDTH,
            (fuel["y"] - spaceship["y"]) / HEIGHT
        ]

        # Agent learning
        agent.learn(state, action, reward, next_state)

        # Draw spaceship and fuel
        draw_spaceship(spaceship["x"], spaceship["y"], spaceship["angle"], spaceship_img)
        draw_fuel()

        # Display action and fuel info
        action_text = font.render(f"Agent {i} Action: {action}", True, WHITE)
        screen.blit(action_text, (10, 10 + i * 30))
        fuel_text = font.render(f"Fuel: {spaceship['fuel']:.1f}%", True, WHITE)
        screen.blit(fuel_text, (WIDTH - 200, 10 + i * 30))

    pygame.display.flip()
    clock.tick(60)

print("Training complete.")

# Save agent models
for i, agent in enumerate(agents):
    with open(f"{saveAgentTo}_{i}.pkl", "wb") as f:
        pickle.dump({"q_table": agent.q_table}, f)
    print(f"Agent {i} data saved.")
