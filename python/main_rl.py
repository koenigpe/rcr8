import random
import time

from rl.env.r8_env import R8Env
from rl.env.r8_virtual_env import R8VirtualEnv
from rl.simple_agent import SimpleAgent

if __name__ == '__main__':

    def train(env, eposodes):

        agent = SimpleAgent(gamma=0.99, epsilon=0.1, lr=0.0005, epsilon_decay=0.9999,
                            n_actions=7, batch_size=128, epsilon_min=0.01, restore=False)
        score_history = []
        start = time.time()
        episode = 0

        while episode <= eposodes:
            episode += 1
            done = False
            score = 0
            moves = 0
            observation = env.reset()
            while not done:
                moves +=1
                action = agent.choose_action(observation)
                observation_, reward, done, info = env.step(action)
                score += reward
                agent.remember(observation, action, reward, observation_, int(done))
                observation = observation_
                agent.learn()

            score_history.append(score)
            duration = time.time()-start
            print(round(time.time()), "\t", episode,';%.2f' % score, "\t",
                  round(sum(score_history) / len(score_history), 2), "\t", agent.epsilon, "\t", round(duration, 0), "\t", round(moves / duration, 4))

            if episode % 5 == 0:
                agent.save()


    with R8VirtualEnv(enable_screen=False) as env:
       train(env, 2500)

    #with R8Env(serial_port="/dev/rfcomm0", baudrate=9600, timeout=10, reward_delay_msec=50) as env:
       #train(env, 5)

