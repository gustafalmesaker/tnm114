import pygame
import sys
from env import droneEnv  # Ensure this matches your environment class file name

def play_game():
    pygame.init()

    # Initialize the environment
    env = droneEnv()
    observation = env.reset()

    print("Game Controls:\nW: Thrust Up\nS: Thrust Down\nA: Rotate Left\nD: Rotate Right\nQ: Quit")

    # Mapping of keys to actions
    key_action_map = {
        pygame.K_w: 1,  # Thrust Up
        pygame.K_s: 2,  # Thrust Down
        pygame.K_a: 3,  # Rotate Left
        pygame.K_d: 4,  # Rotate Right
    }

    action = 0  # No action by default

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        # Determine action based on pressed key
        action = 0  # Default action: No action
        for key, mapped_action in key_action_map.items():
            if keys[key]:
                action = mapped_action
                break

        # Quit if Q is pressed
        if keys[pygame.K_q]:
            print("Exiting game.")
            pygame.quit()
            sys.exit()

        # Take a step in the environment
        observation, reward, done, info = env.step(action)

        # Check if the game has ended
        if done:
            print("Game Over! Resetting...")
            observation = env.reset()

        # Render the environment
        env.render()

if __name__ == "__main__":
    play_game()
