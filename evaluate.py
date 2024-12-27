import argparse
from env import droneEnv
import logging
from stable_baselines3 import A2C
#from stable_baselines3 import DQN

#Initialize the argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='models/125k.zip', help='Path to the model zip file')
parser.add_argument('--log_dir', type=str, default='evaluation_logs', help='Directory to save evaluation logs')
args = parser.parse_args()

try:
    env = droneEnv()
    # Load the model using the provided argument or the default value
    model = A2C.load(args.model, env=env)
    # model = DQN.load(args.model, env=env)
except Exception as e:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.error(e)
    quit()

# Initialize TensorBoard writer
writer = SummaryWriter(log_dir=args.log_dir)

# Evaluate the model
mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10, return_episode_rewards=True)

# Log evaluation results to TensorBoard
for i, reward in enumerate(mean_reward):
    writer.add_scalar('Evaluation/Reward', reward, i)

writer.close()

#import os
#from stable_baselines3.common.evaluation import evaluate_policy

#evaluate_policy(model, env, n_eval_episodes=10)
#quit()