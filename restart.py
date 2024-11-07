import pygame
import numpy as np

# Define constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

class SpaceshipGame:
    def __init__(self, render=True):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) if render else None
        self.clock = pygame.time.Clock()
        self.render = render
        self.reset()

    def reset(self):
        # Initialize game state, e.g., spaceship and fuel can positions
        self.spaceship_pos = np.array([SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2])
        self.fuel_can_pos = np.random.randint(0, SCREEN_WIDTH), np.random.randint(0, SCREEN_HEIGHT)
        self.done = False
        return self.get_state()

    def get_state(self):
        # Return the current state, e.g., positions of spaceship and fuel can
        return {
            "spaceship": self.spaceship_pos,
            "fuel_can": self.fuel_can_pos
        }

    def step(self, action):
        # Update the spaceship position based on the action
        if action == 0:  # Move up
            self.spaceship_pos[1] -= 5
        elif action == 1:  # Move down
            self.spaceship_pos[1] += 5
        elif action == 2:  # Move left
            self.spaceship_pos[0] -= 5
        elif action == 3:  # Move right
            self.spaceship_pos[0] += 5

        # Check for collision with fuel can
        reward = -1
        if np.linalg.norm(self.spaceship_pos - self.fuel_can_pos) < 20:
            reward = 10  # Reward for catching fuel
            self.fuel_can_pos = np.random.randint(0, SCREEN_WIDTH), np.random.randint(0, SCREEN_HEIGHT)

        # Render if in game mode
        if self.render:
            self.render_game()

        return self.get_state(), reward, self.done

    def render_game(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        pygame.draw.circle(self.screen, (0, 255, 0), self.spaceship_pos, 10)  # Draw spaceship
        pygame.draw.circle(self.screen, (255, 0, 0), self.fuel_can_pos, 10)  # Draw fuel can
        pygame.display.flip()
        self.clock.tick(30)

    def close(self):
        pygame.quit()

class RLAgent:
    def __init__(self, num_agents=1):
        self.num_agents = num_agents

    def select_action(self, state):
        # Dummy action selection: random movement
        return np.random.choice([0, 1, 2, 3])

    def train(self, envs, num_episodes=100):
        for episode in range(num_episodes):
            for env in envs:
                state = env.reset()
                done = False
                while not done:
                    action = self.select_action(state)
                    state, reward, done = env.step(action)
                    
                # Training logic here (update agent based on reward)

def main(mode='train', num_agents=1):
    envs = [SpaceshipGame(render=(mode == 'game')) for _ in range(num_agents)]
    agent = RLAgent(num_agents=num_agents)

    if mode == 'train':
        agent.train(envs)
    elif mode == 'game':
        done = False
        while not done:
            step = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            state = envs[0].reset()
            done = False
            while not done:
                step += 1
                if step > 1000: done = True
                action = agent.select_action(state)
                state, _, done = envs[0].step(action)
                

        envs[0].close()

if __name__ == "__main__":
    main(mode='game', num_agents=10)
    # Use mode='train' and adjust num_agents for training without rendering
