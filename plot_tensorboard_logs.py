import os
import matplotlib.pyplot as plt
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

# Path to evaluation logs
log_dirs = {
    "125k": "evaluation_logs/125k",
    "500k": "evaluation_logs/500k",
    "1250k": "evaluation_logs/1250k",
}

# Function to extract rewards from TensorBoard logs
def extract_rewards(log_dir):
    event_acc = EventAccumulator(log_dir)
    event_acc.Reload()
    
    # Check if the scalar 'Evaluation/Reward' exists
    if 'Evaluation/Reward' not in event_acc.Tags()["scalars"]:
        print(f"No rewards found in {log_dir}")
        return []

    # Extract scalar values
    events = event_acc.Scalars('Evaluation/Reward')
    rewards = [event.value for event in events]
    return rewards

# Collect data for each model
model_rewards = {}
for model, log_dir in log_dirs.items():
    if os.path.exists(log_dir):
        model_rewards[model] = extract_rewards(log_dir)
    else:
        print(f"Log directory for {model} does not exist: {log_dir}")
        model_rewards[model] = []

# Plot the results
plt.figure(figsize=(10, 6))
for model, rewards in model_rewards.items():
    if rewards:
        plt.plot(range(1, len(rewards) + 1), rewards, label=model)

plt.xlabel("Evaluation Episode")
plt.ylabel("Reward")
plt.title("Comparison of Model Rewards")
plt.legend()
plt.grid(True)
plt.show()
