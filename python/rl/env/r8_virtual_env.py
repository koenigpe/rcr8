import random
import gym
import pygame
import numpy as np
from rl.env.r8_physics import action_to_movement, derive_reward, ACTION_SPACE, OBSERVATION_SPACE, MAX_SENSOR_DISTANCE_CM
from rl.env.r8_virtual_env_math_utils import np_cart_to_polar, np_rotate_polar


SCREEN_BORDER_PIXEl = 20
PIXEL_PER_METER = 500
R8_WIDTH_PIXEL = round(PIXEL_PER_METER * (8 / 100))
R8_LENGTH_PIXEL = round(PIXEL_PER_METER * (20 / 100))

BARRIERS = 2
BARRIER_SIZE_CM = 20

FPS = 60  # Frames per second.

FRONT_RIGHT = 335
RIGHT = 270
BACK = 180
LEFT = 90
FRONT_LEFT = 25

class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (125, 125, 125)
    RED = (255, 0, 0)
    AUDI_RED = (187, 10, 48)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    ORANGE = (255, 165, 0)

def to_pixel(cm, ppm = PIXEL_PER_METER):
    return int(cm * (ppm / 100))

def to_cm(pix, ppm = PIXEL_PER_METER):
    cm = int(pix /( ppm/100))
    if cm > MAX_SENSOR_DISTANCE_CM:
        return 100
    else:
        return cm

def to_cm_norm(pix):
    return to_cm(pix) / MAX_SENSOR_DISTANCE_CM

class R8VirtualEnv(gym.Env):


    def __init__(self, enable_screen=True, screen_size_cm = (200, 200)):
        super(R8VirtualEnv, self).__init__()  # Define action and observation space
        self.screen_size = (to_pixel(screen_size_cm[0]), to_pixel(screen_size_cm[1]))
        
        if enable_screen:
            pygame.font.init()
            self.screen = pygame.display.set_mode(self.screen_size)
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont('Tahoma', 20, True, False)
        self.size = R8_LENGTH_PIXEL
        self.position = (int(self.screen_size[0] / 2), int(self.screen_size[1] / 2))
        self.angle = random.randint(0, 360)
        self.reward = 0
        self.state = np.zeros(OBSERVATION_SPACE.shape[0])
        self.previous_action = (0, 0)
        self.enable_screen = enable_screen
        self.action_space = ACTION_SPACE
        self.observation_space = OBSERVATION_SPACE
        self.barrier_size = to_pixel(BARRIER_SIZE_CM)
        self.spawn_position = (int(self.screen_size[0] / 2), int(self.screen_size[1] / 2))


        self.generate_area()

    def distance_to_color(self, d):
            return Color.RED

    def generate_area(self):
        self.area = np.concatenate((self.generate_border(), self.generate_barrier(BARRIERS, self.barrier_size)))

    def generate_border(self):
        grid = [int(x) for x in np.linspace(SCREEN_BORDER_PIXEl, self.screen_size[0] - SCREEN_BORDER_PIXEl, 500)]

        border = np.array([(SCREEN_BORDER_PIXEl, x) for x in grid] + \
                          [(self.screen_size[0] - SCREEN_BORDER_PIXEl, x) for x in grid] + \
                          [(x, SCREEN_BORDER_PIXEl) for x in grid] + \
                          [(x, self.screen_size[0] - SCREEN_BORDER_PIXEl) for x in grid])
        return border


    def generate_barrier(self, cnt, size):
        blocks = (np.random.rand(cnt, 2) * self.screen_size[0]).astype(int)
        block_space = int(size / 50)

        blocks_x = blocks[:, 0]
        blocks_y = blocks[:, 1]
        blocks = np.concatenate(
            [np.concatenate([np.stack((blocks_x + dx, blocks_y + dy), axis=1) for dx in range(0, size, block_space)])
             for dy in range(0, size, block_space)], axis=0)

        # Remove blocks in car spawning area
        spawn_distance = np.sqrt(np.power(np.abs(blocks[:, 0] - self.spawn_position[0]), 2)+np.power(np.abs(blocks[:, 1] - self.spawn_position[1]), 2) )
        blocks = blocks[spawn_distance > 100]
        # Remove blocks outside of border
        blocks = blocks[(blocks[:, 0] > SCREEN_BORDER_PIXEl) &
                        (blocks[:, 1] > SCREEN_BORDER_PIXEl) &
                        (blocks[:, 0] < self.screen_size[0] - SCREEN_BORDER_PIXEl) &
                        (blocks[:, 1] < self.screen_size[1] - SCREEN_BORDER_PIXEl)]

        return blocks

    def drawBackground(self):


        if self.enable_screen:
            pygame.draw.rect(self.screen, Color.WHITE, (0, 0, self.screen_size[0], self.screen_size[0]))
            [pygame.draw.circle(self.screen, Color.BLACK, (x, y), 4, 4) for (x, y) in self.area]

    def draw_area(self):
        self.drawBackground()
        self.draw_me()
        text_surface = self.font.render(str(round(self.reward, 2)), True, Color.WHITE, Color.BLACK)
        self.screen.blit(text_surface, dest=(SCREEN_BORDER_PIXEl, SCREEN_BORDER_PIXEl))

    def draw_me(self):
        car_front = pygame.Vector2()
        car_front.from_polar((self.size / 2, self.angle))
        car_back = pygame.Vector2()
        car_back.from_polar((-self.size / 2, self.angle))
        pygame.draw.line(self.screen, Color.AUDI_RED, self.position + car_back, self.position + car_front, 2)

        #pygame.draw.circle(self.screen, Color.ORANGE, ( int(self.position[0]), int(self.position[1])), BORDER_START, 2)

        #pygame.draw.circle(self.screen, Color.RED, ( int(self.position[0]), int(self.position[1])), BORDER_END, 2)

    def step(self, action):

        steering, accel = action_to_movement(action)
        angle = steering * 7
        x = accel * 15

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

    def screen_shot(self, path):
         pygame.image.save(self.screen, path)

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        pygame.display.update()

    def reset(self):
        self.generate_area()
        self.position = self.spawn_position
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
            pygame.draw.line(self.screen, color, (p2x, p2y), self.position, 2)

        return closest_distance

    def get_distance(self, enable_noice=True):

        pol = np_rotate_polar(np_cart_to_polar(coords=self.area, zero_point=self.position, revert_y=True), self.angle)

        arc = pol[:, 0]
        distances = pol[:, 1]


        done_distance = self.get_sensor_reading(distances, arc, 0, Color.WHITE, False)

        s0 = self.get_sensor_reading(distances, arc, FRONT_RIGHT, Color.BLUE)
        s1 = self.get_sensor_reading(distances, arc, RIGHT, Color.GREY)
        s2 = self.get_sensor_reading(distances, arc, BACK, Color.GREY)
        s3 = self.get_sensor_reading(distances, arc, LEFT, Color.GREY)
        s4 = self.get_sensor_reading(distances, arc, FRONT_LEFT, Color.BLUE)

        if self.enable_screen:
            min_measured_dirstance = int(min(s0, s1, s2, s3, s4))
            pygame.draw.circle(self.screen, self.distance_to_color(min_measured_dirstance), ( int(self.position[0]), int(self.position[1])), int(min(s0, s1, s2, s3, s4)), 1)

        state = np.array((to_cm_norm(s0), to_cm_norm(s1), to_cm_norm(s2), to_cm_norm(s3), to_cm_norm(s4)))


        if enable_noice:
            error_rate = 0.1
            # 15% chance MAX_SENSOR_DISTANCE_CM
            state[np.random.rand(5)<error_rate] = 1
            # 10% chance [0, 5]
            error =np.random.rand(5)
            state[error<error_rate] = error[error<error_rate]/100


        return state, done_distance


if __name__ == '__main__':

   # env = R8VirtualEnv(True)
    #while True:
     #   env.step(random.randint(0, 5))
   print(to_cm(to_pixel(50)))
   print(to_cm(1000))
