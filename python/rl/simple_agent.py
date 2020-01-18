import os

from keras.layers import Dense, Activation
from keras.models import Sequential, load_model
from keras.optimizers import Adam
import numpy as np


def get_net(lr, output_cnt, input_cnt , hidden1_cnt, hidden2_cnt, activation_fct='relu', loss='mse'):
    model = Sequential([
                Dense(hidden1_cnt, input_shape=(input_cnt,)),
                Activation(activation_fct),
                Dense(hidden2_cnt),
                Activation(activation_fct),
                Dense(output_cnt)])

    model.compile(optimizer=Adam(lr=lr), loss=loss)

    return model


class Memory(object):
    def __init__(self, input_shape, n_actions):
        self.mem_size = 1000000
        self.cntr = 0
        self.mem_state = np.zeros((self.mem_size, input_shape))
        self.mem_next_state = np.zeros((self.mem_size, input_shape))
        self.mem_action = np.zeros((self.mem_size, n_actions), dtype=np.int8)
        self.mem_reward = np.zeros(self.mem_size)
        self.mem_done = np.zeros(self.mem_size, dtype=np.float32)

    def get_mem_state_history(self, history, idx):
        h = [(x + self.mem_size) % self.mem_size for x in range(idx - history, idx, 1)]
        return np.concatenate(self.mem_state[h, :])

    def get_mem_next_state_history(self, history, idx):
        h = [(x + self.mem_size) % self.mem_size for x in range(idx - history, idx, 1)]
        return np.concatenate(self.mem_next_state[h, :])

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

    def get_sample(self, batch_size):
        max_available = self.cntr-batch_size if self.cntr > self.mem_size -batch_size else self.cntr
        batch = np.random.choice(np.arange(5, max_available), batch_size)
        states = np.array([self.get_mem_state_history(5, x+1) for x in batch])
        actions = self.mem_action[batch]
        rewards = self.mem_reward[batch]
        next_state = np.array([self.get_mem_next_state_history(5, x+1) for x in batch])
        done = self.mem_done[batch]
        return states, actions, rewards, next_state, done


class Agent(object):
    def __init__(self, lr, gamma, n_actions, epsilon, batch_size, epsilon_decay,  epsilon_min, file='_Agent.h5', restore=True):
        self.input_dims = 5
        self.action_space = [i for i in range(n_actions)]
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.file = file
        self.memory = Memory(self.input_dims, n_actions)
        self.net = get_net(lr, n_actions, self.input_dims*5, 25, 10)

        if restore:
            self.restore()

    def add_history(self, state):
        return np.concatenate((self.memory.get_mem_state_history(4, self.memory.cntr), state))

    def choose_action(self, state):
        input_layer = self.add_history(state)[np.newaxis, :]
        rand = np.random.random()
        if rand < self.epsilon:
            action = np.random.choice(self.action_space)
        else:
            actions = self.net.predict(input_layer)
            action = np.argmax(actions)
        return action

    def remember(self, state, action, reward, next_state, done):
        self.memory.add(state, action, reward, next_state, done)

    def learn(self):
        if self.memory.cntr > self.batch_size:
            state, action, reward, new_state, done = \
                                          self.memory.get_sample(self.batch_size)

            action_values = np.array(self.action_space, dtype=np.int8)
            action_indices = np.dot(action, action_values)
            q_eval = self.net.predict(state)
            q_next = self.net.predict(new_state)
            q_target = q_eval.copy()
            batch_index = np.arange(self.batch_size, dtype=np.int32)
            q_target[batch_index, action_indices] = reward + \
                                  self.gamma*np.max(q_next, axis=1)*done

            _ = self.net.fit(state, q_target, verbose=0)

            self.epsilon = self.epsilon*self.epsilon_decay if self.epsilon > \
                                                              self.epsilon_min else self.epsilon_min

    def save(self):
        self.net.save(self.file)

    def restore(self):
        if os.path.isfile(self.file):
            self.net = load_model(self.file)