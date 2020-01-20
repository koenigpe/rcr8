import numpy as np


class Memory(object):
    def __init__(self, input_shape, n_actions, mem_size=1000000, input_history = 5):
        self.mem_size = mem_size
        self.input_history = input_history
        self.cntr = 0
        self.mem_state = np.zeros((self.mem_size, input_shape))
        self.mem_next_state = np.zeros((self.mem_size, input_shape))
        self.mem_action = np.zeros((self.mem_size, n_actions), dtype=np.int8)
        self.mem_reward = np.zeros(self.mem_size)
        self.mem_done = np.zeros(self.mem_size, dtype=np.float32)

    def get_mem_history(self, idx, collection):
        most_recent_update = self.cntr % self.mem_size

        if idx - self.input_history < most_recent_update < idx:
            raise ValueError('the history at position idx was update with a new record.')

        h = [(x + self.mem_size) % self.mem_size for x in range(idx - self.input_history, idx, 1)]

        return np.concatenate(collection[h, :])

    def add(self, state, action, reward, next_state, done):
        index = self.cntr % self.mem_size
        self.mem_state[index] = state
        self.mem_next_state[index] = next_state
        actions = np.zeros(self.mem_action.shape[1])
        actions[action] = 1.0
        self.mem_action[index] = actions
        self.mem_reward[index] = reward
        self.mem_done[index] = 1 - done
        self.cntr += 1

    def add_state_history(self, state, idx):
        return np.concatenate((self.get_mem_history(idx, self.mem_state), state))

    def add_next_state_history(self, next_state, idx):
        return np.concatenate((self.get_mem_history(idx, self.mem_next_state), next_state))

    def get_current_idx(self):
        return self.cntr % self.mem_size -1

    def get_blacklist_range(self):
        current_idx = self.get_current_idx()
        return current_idx + 1 % self.mem_size, current_idx + self.input_history

    def get_sample_idx(self, batch_size):
        max_available = min(self.mem_size, self.cntr)
        sample_base = np.arange(0, max_available)
        blacklist_from, blacklist_to = self.get_blacklist_range()
        return np.random.choice(sample_base[(sample_base < blacklist_from) | (sample_base > blacklist_to)], batch_size)

    def get_sample(self, batch_size):
        batch = self.get_sample_idx(batch_size)

        states = np.stack([self.add_state_history(self.mem_state[b], b) for b in batch])

        actions = self.mem_action[batch]
        rewards = self.mem_reward[batch]
        next_state = np.stack([self.add_next_state_history(self.mem_next_state[b], b) for b in batch])

        done = self.mem_done[batch]
        return states, actions, rewards, next_state, done
