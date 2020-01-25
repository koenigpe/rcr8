import time

import gym
import numpy as np
from r8 import R8
from rl.env.r8_physics import *


class R8Env(gym.Env):

    def __init__(self, serial_port, baudrate, timeout, reward_delay_msec):
        super(R8Env, self).__init__()    # Define action and observation space
        self.r8 = R8(serial_port, baudrate, timeout)
        self.reward_delay_msec = reward_delay_msec
        self.new_state = np.zeros(OBSERVATION_SPACE.shape[0])
        self.previous_action = (0, 0)
        self.reward = 0
        self.action_space = ACTION_SPACE
        self.observation_space = OBSERVATION_SPACE

    def step(self, action):

        steering, accel = action_to_movement(action)

        self.r8.send_accelleration(accel)
        self.r8.send_steering(steering)
        time.sleep(self.reward_delay_msec / 1000)
        self.new_state = self.r8.get_state()

        done_, reward = derive_reward(self.new_state, steering, accel, self.previous_action[0], self.previous_action[1], self.reward)

        self.previous_action = (steering, accel)
        self.reward += reward
        if done_:
            self.r8.full_stop()
        return self.new_state, reward, done_, {}

    def reset(self):
        self.free()
        self.reward = 0
        return self.new_state[0:5]   # ToDo Check actual size of state

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        raise NotImplementedError("Nothing to show")

    def free(self):
        self.new_state = self.r8.get_state()
        if np.array_equal(self.new_state ,  np.zeros(5)) or min(self.new_state) > 30:
            self.r8.full_stop()
            time.sleep(2)
            print("Reset done")
            return
        state_front = min(self.new_state[FRONT_RIGHT], self.new_state[FRONT_LEFT])

        if self.new_state[BACK] >= state_front:
            if self.new_state[RIGHT] >= self.new_state[LEFT]:
                self.new_state, _, _, _ = self.step(2)
            else:
                self.new_state, _, _, _ = self.step(0)
        else:
            if self.new_state[RIGHT] >= self.new_state[LEFT]:
                self.new_state, _, _, _ = self.step(5)
            else:
                self.new_state, _, _, _ = self.step(3)

        time.sleep(0.5)
        self.free()
