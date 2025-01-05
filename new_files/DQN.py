import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

class DQNNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQNNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    def __init__(self, state_size, action_size, alpha=0.001, gamma=0.99, epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.995, memory_size=50000, batch_size=64, target_update=1000):
        self.state_size = state_size
        self.action_size = action_size
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_min = epsilon_min  # Minimum epsilon
        self.epsilon_decay = epsilon_decay  # Decay rate
        self.memory = deque(maxlen=memory_size)
        self.batch_size = batch_size
        self.target_update = target_update
        self.step_count = 0
        
        # Q-network and target network
        self.q_network = DQNNetwork(state_size, action_size)
        self.target_network = DQNNetwork(state_size, action_size)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.alpha)

        # Copy the weights from q_network to target_network initially
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

    def choose_action(self, state):
        # Epsilon-greedy action selection
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, self.action_size - 1)
        else:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
            return torch.argmax(q_values).item()

    def store_experience(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def update_q_network(self):
        # Check if there is enough experience to sample a batch
        if len(self.memory) < self.batch_size:
            return

        # Sample a batch from memory
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # Compute target Q-values
        with torch.no_grad():
            max_next_q_values = self.target_network(next_states).max(1)[0]
            targets = rewards + (self.gamma * max_next_q_values * (1 - dones))

        # Compute current Q-values
        q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        # Compute the loss
        loss = nn.MSELoss()(q_values, targets)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update target network periodically
        if self.step_count % self.target_update == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())

        # Increment step count and decay epsilon
        self.step_count += 1
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
