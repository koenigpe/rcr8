import gym
import numpy as np

class DebugEnv(gym.Env):

    def __init__(self):
        super(DebugEnv, self).__init__()  # Define action and observation space
        self.reward = 0
        self.state = np.random.rand(5, )

    def step(self, action):

        if (self.state[0]+1) % 5 == action:
            reward = 10
        else:
            reward = -1

        self.reward += reward
        done = self.reward > 50 or self.reward < 0

        self.state = np.array((action % 5, 0, 0, 0, 0))
        return self.state, reward, done, {}

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        pass

    def reset(self):
        print(self.state)
        self.reward = 0
        return self.state

