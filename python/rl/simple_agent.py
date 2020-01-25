import os
import pickle

from keras.layers import Dense, Activation
from keras.models import Sequential, load_model
from keras.optimizers import Adam
import numpy as np

from rl.memory import Memory


def get_net(lr, output_cnt, input_cnt , hidden1_cnt, hidden2_cnt, activation_fct='relu', loss='mse'):
    model = Sequential([
                Dense(hidden1_cnt, input_shape=(input_cnt,)),
                Activation(activation_fct),
                Dense(hidden2_cnt),
                Activation(activation_fct),
                Dense(output_cnt)])

    model.compile(optimizer=Adam(lr=lr), loss=loss)

    return model


class SimpleAgent(object):
    def __init__(self, lr, gamma, n_actions, epsilon, batch_size, epsilon_decay, epsilon_min, restore=True):
        self.input_history = 0
        self.input_dims = 5
        self.action_space = [i for i in range(n_actions)]
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.agent_file = "_Agent.h5"
        self.memory_file = "memory.pkl"
        self.memory = Memory(self.input_dims, n_actions, input_history=self.input_history)
        self.net = get_net(lr, n_actions, self.input_dims* (self.input_history+1), 25, 10)

        if restore:
            self.restore()

    def add_history(self, state):
        return self.memory.add_state_history(state, self.memory.cntr)

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
        self.net.save(self.agent_file)
        with open(self.memory_file, 'wb') as output:
            pickle.dump(self.memory, output, pickle.HIGHEST_PROTOCOL)

    def restore(self):

        if os.path.isfile(self.agent_file):
            print("restored")
            self.net = load_model(self.agent_file)
        if os.path.isfile(self.memory_file):
            with open(self.memory_file, 'rb') as i:
                self.memory = pickle.load(i)
