import numpy as np
from dqn_agent import DQNAgent
from env import droneEnv  # Replace with your custom environment

# Initialize environment
env = droneEnv()
state_size = env.observation_space.shape[0]
action_size = env.action_space.n

# Initialize DQN agent
agent = DQNAgent(state_size=state_size, action_size=action_size)

# Training parameters
episodes = 5
target_update_frequency = 10

for e in range(episodes):
    state = env.reset()
    state = np.reshape(state, [1, state_size])
    total_reward = 0
    
    for time in range(500):  # Max time steps per episode
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        next_state = np.reshape(next_state, [1, state_size])
        agent.remember(state, action, reward, next_state, done)
        state = next_state
        total_reward += reward
        if done: print(done)

        if done:
            print(f"Episode: {e+1}/{episodes}, Score: {total_reward}, Epsilon: {agent.epsilon:.2}")
            break
    
    # Replay and train
    agent.replay()
    
    # Update target network
    if e % target_update_frequency == 0:
        agent.update_target_model()
        
# Save the trained DQN model
agent.model.save("models/dqn_models")
env.close()
