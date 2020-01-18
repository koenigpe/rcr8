import random
import gym
import pygame
import numpy as np
from rl.env.r8_utils import action_to_movement, derive_reward
from rl.env.r8_virtual_env_utils import np_cart_to_polar, np_rotate_polar, R8_LENGTH


class R8VirtualEnv(gym.Env):
    SCREEN_SIZE = (1000, 1000)
    SCREEN_BORDER = 20

    FPS = 60  # Frames per second.

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (125, 125, 125)

    RED = (255, 0, 0)
    AUDI_RED = (187, 10, 48)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    FRONT_RIGHT = 335
    RIGHT = 270
    BACK = 180
    LEFT = 90
    FRONT_LEFT = 25

    def __init__(self,  enable_screen=True):
        super(R8VirtualEnv, self).__init__()  # Define action and observation space
        if enable_screen:
            pygame.font.init()
            self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
            self.clock = pygame.time.Clock()
        self.size = R8_LENGTH
        self.position = (int(self.SCREEN_SIZE[0] / 2), int(self.SCREEN_SIZE[1] / 2))
        self.angle = random.randint(0, 360)
        self.reward = 0
        self.state = np.zeros(5)
        self.previous_action = (0, 0)
        self.enable_screen = enable_screen

        self.generate_area()

    def generate_area(self):
        cnt_barriers = 4
        self.area = np.concatenate((self.generate_border(), self.generate_barrier(cnt_barriers, 50)))

    def generate_border(self):
        grid = [int(x) for x in np.linspace(self.SCREEN_BORDER, self.SCREEN_SIZE[0] - self.SCREEN_BORDER, 100)]

        border = np.array([(self.SCREEN_BORDER, x) for x in grid] + \
                          [(self.SCREEN_SIZE[0] - self.SCREEN_BORDER, x) for x in grid] + \
                          [(x, self.SCREEN_BORDER) for x in grid] + \
                          [(x, self.SCREEN_SIZE[0] - self.SCREEN_BORDER) for x in grid])
        return border

    def generate_barrier(self, cnt, size):
        blocks = (np.random.rand(cnt, 2) * 1000).astype(int)
        block_space = int(size / 7)

        blocks_x = blocks[:, 0]
        blocks_y = blocks[:, 1]
        blocks = np.concatenate(
            [np.concatenate([np.stack((blocks_x + dx, blocks_y + dy), axis=1) for dx in range(0, size, block_space)])
             for dy in range(0, size, block_space)], axis=0)

        # Remove blocks in car spawning area
        blocks = blocks[((blocks[:, 0] / 100).astype(int) != 5) | ((blocks[:, 1] / 100).astype(int) != 5)]
        # Filter
        blocks = blocks[(blocks[:, 0] > self.SCREEN_BORDER) &
                        (blocks[:, 1] > self.SCREEN_BORDER) &
                        (blocks[:, 0] < self.SCREEN_SIZE[0] - self.SCREEN_BORDER) &
                        (blocks[:, 1] < self.SCREEN_SIZE[1] - self.SCREEN_BORDER)]

        return blocks

    def drawBackground(self):


        if self.enable_screen:
            pygame.draw.rect(self.screen, self.WHITE, (0, 0, self.SCREEN_SIZE[0], self.SCREEN_SIZE[0]))
            [pygame.draw.circle(self.screen, self.BLACK, (x, y), 4, 4) for (x, y) in self.area]

    def draw_area(self):
        self.drawBackground()
        self.draw_me()
        font = pygame.font.SysFont('Tahoma', 20, True, False)
        text_surface = font.render(str(round(self.reward, 2)), True, self.WHITE, self.BLACK)
        #self.state = self.get_distance()
        self.screen.blit(text_surface, dest=(25, 950))

    def draw_me(self):
        car_front = pygame.Vector2()
        car_front.from_polar((self.size / 2, self.angle))
        car_back = pygame.Vector2()
        car_back.from_polar((-self.size / 2, self.angle))
        pygame.draw.line(self.screen, self.AUDI_RED, self.position + car_back, self.position + car_front, 2)

        front = self.position + car_front
        pygame.draw.circle(self.screen, self.GREEN, (round(front[0]), round(front[1])), 1)

    def step(self, action):

        steering, accel = action_to_movement(action)
        angle = steering * 5
        x = accel * 10

        self.angle = (self.angle + angle) % 360

        vec = pygame.Vector2()
        vec.from_polar((x, self.angle))

        self.position = self.position + vec

        if self.enable_screen:
            self.draw_area()
            self.state, done_distance = self.get_distance()
        else:
            self.state, done_distance = self.get_distance()

        done, reward = derive_reward(np.array((done_distance, done_distance)), steering, accel, self.previous_action[0], self.previous_action[1],
                               self.reward)


        self.previous_action = (steering, accel)
        self.reward += reward
        if self.enable_screen:
            pygame.display.update()

        return self.state, reward, done, {}

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        pygame.display.update()

    def reset(self):
        self.generate_area()
        self.position = (int(self.SCREEN_SIZE[0] / 2), int(self.SCREEN_SIZE[1] / 2))
        self.angle = 0# random.randint(0,360)
        self.reward = 0
        return self.get_distance()[0]

    def get_sensor_reading(self, distances, arc, angle, color, sensor_arc_enable = True):
        if sensor_arc_enable:
            _from = (angle - 7 )
            _to = (angle + 7 )
            relevant = ((arc >= _from) & (arc <= _to))
        else:
            relevant = arc<400

        d = np.copy(distances)

        d[np.invert(relevant)] = 99999

        idx = np.argmin(d)
        closest_distance = distances[idx]

        if self.enable_screen and sensor_arc_enable:
            a1 = pygame.Vector2()
            a1.from_polar((100, self.angle + angle + 7))
            a2 = pygame.Vector2()
            a2.from_polar((100, self.angle + angle - 7))

            p1x, p1y = self.position + a1
            p2x, p2y = self.position + a2
            pygame.draw.line(self.screen, color, self.position, (p1x, p1y), 2)
           # pygame.draw.line(self.screen, color, (p1x, p1y), (p2x, p2y), 2)
            pygame.draw.line(self.screen, color, (p2x, p2y), self.position, 2)

        return closest_distance

    def get_distance(self):

        pol = np_rotate_polar(np_cart_to_polar(coords=self.area, zero_point=self.position, revert_y=True), self.angle)

        arc = pol[:, 0]
        distances = pol[:, 1]


        done_distance = self.get_sensor_reading(distances, arc, 0, self.WHITE, False)

        s0 = self.get_sensor_reading(distances, arc, self.FRONT_RIGHT, self.BLUE)
        s1 = self.get_sensor_reading(distances, arc, self.RIGHT, self.GREY)
        s2 = self.get_sensor_reading(distances, arc, self.BACK, self.GREY)
        s3 = self.get_sensor_reading(distances, arc, self.LEFT, self.GREY)
        s4 = self.get_sensor_reading(distances, arc, self.FRONT_LEFT, self.BLUE)

        #print((round(s0), round(s1), round(s2), round(s3), round(s4)), round(done_distance))
        return np.array((s0, s1, s2, s3, s4)), done_distance


if __name__ == '__main__':
    env = R8VirtualEnv(20)

    while True:
        env.step(random.randint(0, 5))

