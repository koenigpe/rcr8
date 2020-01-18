
from r8 import R8

MAX_SCORE = 1000


def distance_front_back(state):
    return min(state[0], state[2], state[4])

def derive_reward( sensor_values, steering, accel, steering_, accel_, score):

    i_dont_like = -0.07

    if score >= MAX_SCORE or score <= -200 or min(sensor_values) < 10:
        done = True
    else:
        done = False

    reward = 0

    # Border = bad
    border_start = 50
    border_max = 20
    border_max_reward = -20
    slope = border_max_reward / (border_start - border_max)
    reward += int(min(sensor_values) < border_start) * ( (border_start - min(sensor_values) )* slope)

    if accel == 1:
        reward += 1
    if accel == -1:
        reward += 0.1

    if accel == 0:
        reward += i_dont_like
    if steering != 0:
        reward += i_dont_like
    if steering != steering_:
        reward += i_dont_like
    if accel != accel_:
        reward += i_dont_like

    return done, reward

def action_to_movement(action):
    # action [0, 6]
    steering = R8.GO_AHEAD
    acceleration = R8.STOP

    if action == 0:
        steering = R8.TURN_LEFT
        acceleration = R8.BACKWARDS
    if action == 1:
        steering = R8.GO_AHEAD
        acceleration = R8.BACKWARDS
    if action == 2:
        steering = R8.TURN_RIGHT
        acceleration = R8.BACKWARDS

    if action == 3:
        steering = R8.TURN_LEFT
        acceleration = R8.FORWARDS
    if action == 4:
        steering = R8.GO_AHEAD
        acceleration = R8.FORWARDS
    if action == 5:
        steering = R8.TURN_RIGHT
        acceleration = R8.FORWARDS

    return steering, acceleration
