import pygame
import random
import numpy as np
import math
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
import matplotlib.pyplot as plt

# Constants
WIDTH, HEIGHT = 600, 600
BLOCK_SIZE = 20
WHITE = (255, 255, 255)
RED = (255, 0, 0)

#FPS = 15 #Normal Speed
FPS = 120 #Learning Speed

class SnakeEnv:
    def __init__(self):
        self.action_space = 4  # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        self.reset()

    def reset(self):
        # Reset game variables
        self.snake_pos = [[WIDTH // 2, HEIGHT // 2]]
        self.snake_speed = [0, BLOCK_SIZE]
        self.food_pos = self._generate_food()
        self.score = 0
        self.done = False
        return self._get_state()

    def step(self, action):
        # Calculate the current distance to the food
        prev_distance = self._get_distance(self.snake_pos[0], self.food_pos)

        # Change direction based on action
        if action == 0 and self.snake_speed[1] != BLOCK_SIZE:  # UP
            self.snake_speed = [0, -BLOCK_SIZE]
        elif action == 1 and self.snake_speed[1] != -BLOCK_SIZE:  # DOWN
            self.snake_speed = [0, BLOCK_SIZE]
        elif action == 2 and self.snake_speed[0] != BLOCK_SIZE:  # LEFT
            self.snake_speed = [-BLOCK_SIZE, 0]
        elif action == 3 and self.snake_speed[0] != -BLOCK_SIZE:  # RIGHT
            self.snake_speed = [BLOCK_SIZE, 0]

        self._update_snake()

        # Calculate the new distance to the food
        new_distance = self._get_distance(self.snake_pos[0], self.food_pos)

        # Check if the snake eats the food
        if self.snake_pos[0] == self.food_pos:
            reward = 10  # Reward for eating the food
            self.food_pos = self._generate_food()
            self.score += 10
        else:
            # Reward for getting closer or penalty for getting farther
            reward = 1 if new_distance < prev_distance else -0.5
            self.snake_pos.pop()  # Remove the snake's tail if no food is eaten

        if self._game_over():
            self.done = True
            reward = -50  # Big penalty for hitting the wall or itself

        return self._get_state(), reward, self.done

    def _get_distance(self, pos1, pos2):
        # Calculate Euclidean distance between two positions
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


    def render(self):
        # Ensure the window and clock are initialized only once
        if not hasattr(self, 'win'):
            self.win = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
            pygame.font.init()
            self.font = pygame.font.SysFont("consolas", 20)  # Create the font object once

        # Clear the screen
        self.win.fill((0, 0, 0))

        # Draw the snake and the food
        for pos in self.snake_pos:
            pygame.draw.rect(self.win, WHITE, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.win, RED, pygame.Rect(self.food_pos[0], self.food_pos[1], BLOCK_SIZE, BLOCK_SIZE))

        # Render the score using the font object created earlier
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.win.blit(score_text, (10, 10))

        # Update the display and control the frame rate
        pygame.display.update()
        self.clock.tick(FPS)  # Set FPS to 15, or use a variable `FPS`


    def _generate_food(self):
        while True:
            x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            food_pos = [x, y]
            if food_pos not in self.snake_pos:
                return food_pos

    
    def _is_collision(self):
        # Check if snake hits the boundary
        head_x, head_y = self.snake_pos[0]
        if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
            return True
        # Check if snake hits itself
        if self.snake_pos[0] in self.snake_pos[1:]:
            return True
        return False

    def _update_snake(self):
        new_head = [self.snake_pos[0][0] + self.snake_speed[0], self.snake_pos[0][1] + self.snake_speed[1]]
      
        if self._is_collision():
            self._game_over
        self.snake_pos.insert(0, new_head)

    def _game_over(self):
        return self._is_collision()

    def _get_state(self):
        head_x, head_y = self.snake_pos[0]
        food_x, food_y = self.food_pos
        state = [
            head_x, head_y,  # Snake head position
            food_x, food_y,  # Food position
            self.snake_speed[0], self.snake_speed[1]  # Snake speed
        ]
        return np.array(state, dtype=np.float32)

# Define the DQN Model
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 256)
        self.fc3 = nn.Linear(256, output_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

# Define the DQN Agent
class DQNAgent:
    def __init__(self, input_dim, action_space, gamma=0.99, lr=0.001, batch_size=64, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.input_dim = input_dim
        self.action_space = action_space
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.memory = deque(maxlen=2000)  # Experience replay buffer

        # Create the Q-network and target network
        self.q_network = DQN(input_dim, action_space).float()
        self.target_network = DQN(input_dim, action_space).float()
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)

        # Synchronize the weights of the target network with the Q-network
        self.update_target_network()

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return random.randrange(self.action_space)  # Random action
        state = torch.FloatTensor(state).unsqueeze(0)  # Convert to tensor
        with torch.no_grad():
            q_values = self.q_network(state)
        return torch.argmax(q_values).item()  # Choose the action with highest Q-value

    def train(self):
        if len(self.memory) < self.batch_size:
            return

        # Sample a random mini-batch from memory
        batch = random.sample(self.memory, self.batch_size)
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*batch)

        # First, convert the list of numpy arrays to a single numpy array
        state_batch = torch.FloatTensor(np.array([s.flatten() for s in state_batch]))
        next_state_batch = torch.FloatTensor(np.array([s.flatten() for s in next_state_batch]))
        
        #no need to flatten
        action_batch = torch.LongTensor(action_batch)
        reward_batch = torch.FloatTensor(reward_batch)
        done_batch = torch.FloatTensor(done_batch)


        # Compute the target Q-value using the target network
        q_values_next = self.target_network(next_state_batch).max(1)[0].detach()
        target_q_values = reward_batch + (self.gamma * q_values_next * (1 - done_batch))

        # Compute current Q-values
        q_values = self.q_network(state_batch).gather(1, action_batch.unsqueeze(1)).squeeze(1)

        # Compute loss and optimize the Q-network
        loss = F.mse_loss(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon for exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# Training the DQN Agent
if __name__ == "__main__":
    env = SnakeEnv()
    agent = DQNAgent(input_dim=6, action_space=4)  # state: [head_x, head_y, food_x, food_y, speed_x, speed_y]
    episodes = 500
    scores = []

    # Define a threshold for early stopping based on poor performance

# Initialize variables to track consecutive bad scores
bad_score_count = 0

# Training Loop
for e in range(episodes):
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)
        total_reward += reward

        # Store experience in replay memory
        agent.remember(state, action, reward, next_state, done)
        state = next_state

        # Train the agent with the experience from memory
        agent.train()

        # Uncomment the following line to see the game in action (slows down training)
        #env.render()

    # Update target network weights every few episodes
    if e % 10 == 0:
        agent.update_target_network()

    # Track scores and print progress
    scores.append(total_reward)
    print(f"Episode: {e}/{episodes}, Score: {total_reward}, Epsilon: {agent.epsilon:.2f}")

   
    # Save the trained model to a file
    #torch.save(agent.model.state_dict(), "dqn_snake_model_", episodes, "_episodes_.pth")  # Save only the model's weights

    # Plot the scores
plt.plot(scores)
plt.xlabel("Episodes")
plt.ylabel("Score")
plt.show()
