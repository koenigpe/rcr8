import random
import time

from rl.env.debug_env import DebugEnv
from rl.env.r8_env import R8Env
from rl.env.r8_virtual_env import R8VirtualEnv
from rl.simple_agent import SimpleAgent
import numpy as np

if __name__ == '__main__':

    def get_filename(reward, episode):
        e = str(episode).zfill(5)
        r = str(round(reward, 0)).zfill(5)
        return "screenshots/"+e+"_"+r+".jpg"

    def train(env, eposodes):

        agent = SimpleAgent(gamma=0.99, epsilon=0.1, lr=0.0005, epsilon_decay=0.99999,
                            n_actions=7, batch_size=512, epsilon_min=0.01, restore=False)

        score_history = np.array(())
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

                if moves % 10 == 0:
                    agent.learn()

            score_history = np.append(score_history, score)
            duration = time.time()-start

            mean_score = np.mean(score_history[-10:])
            
            if env.enable_screen and type(env).__name__ == "R8VirtualEnv":
                env.screen_shot(get_filename(score, episode))

            print(round(time.time()), "\t", episode,';%.2f' % score, "\t",
                  round(mean_score, 2), "\t", agent.epsilon, "\t", round(duration, 0), "\t", round(moves / duration, 4), "\t", agent.memory.cntr, "\t", env.state)

            if episode % 10 == 0:
                agent.save()




  #  with DebugEnv() as env:
   #     train(env, 100000)

    with R8VirtualEnv(enable_screen=True) as env:
       train(env, 250)

    #with R8Env(serial_port="/dev/rfcomm2", baudrate=9600, timeout=10, reward_delay_msec=0) as env:
       #train(env, 5)

