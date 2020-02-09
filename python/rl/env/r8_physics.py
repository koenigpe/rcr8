import gym

import numpy as np

# sr04 constants
FRONT_RIGHT = 0
RIGHT = 1
BACK = 2
LEFT = 3
FRONT_LEFT = 4

# Steering constants
TURN_LEFT = -1
TURN_RIGHT = 1
GO_AHEAD = 0

# Acceleration constants
FORWARDS = 1
BACKWARDS = -1
STOP = 0

#Actions
BACKWARD_TURN_LEFT = 0
BACKWARDS_GO_AHEAD = 1
BACKWARDS_TURN_RIGHT = 2
FORWARDS_TURN_LEFT = 3
FORWARDS_GO_AHEAD = 4
FORWARDS_TURN_RIGHT = 5

# Virtual env rules
R8_WIDTH = 8
R8_LENGTH = 20
MAX_SENSOR_DISTANCE_CM = 150

# Reward / done variables
DONE_MAX_SCORE = 100
DONE_MIN_SCORE = -100
I_DO_NOT_LIKE = -0.25
BORDER_END = R8_LENGTH
BORDER_MAX_NEGATIVE_REWARD = -10
#BORDER_REWARD_SLOPE = BORDER_MAX_NEGATIVE_REWARD / (BORDER_START - BORDER_END)
#assert(BORDER_REWARD_SLOPE <= 0.0)



ACTION_SPACE = gym.spaces.Discrete(7)
OBSERVATION_SPACE = gym.spaces.Box(low=-MAX_SENSOR_DISTANCE_CM, high=MAX_SENSOR_DISTANCE_CM, dtype=np.int16, shape=(5,))


def check_done(score, sensor_values, min_score=DONE_MIN_SCORE, max_score=DONE_MAX_SCORE, border_end=BORDER_END):
    if score >= max_score or score <= min_score or min(sensor_values) < border_end:
        return True
    else:
        return False


def get_border_distance_reward(closest_distance):
    #is_to_close = closest_distance < border_start
    #return int(is_to_close) * ((border_start - closest_distance) * border_reward_slope)
    if closest_distance <BORDER_END:
        return BORDER_MAX_NEGATIVE_REWARD
    else:
        return 0


def get_acceleration_reward(acceleration, reward_go_ahead = 1,reward_backwards = -0.75, reward_stop=I_DO_NOT_LIKE):
    if acceleration == 1:
        return reward_go_ahead
    if acceleration == -1:
        return reward_backwards
    if acceleration == 0:
        return reward_stop


def get_steering_reward(steering, i_do_not_like=I_DO_NOT_LIKE):
    if steering != 0:
        return i_do_not_like
    else:
        return 0


def get_new_action_reward(steering, accel, steering_, accel_, i_do_not_like=I_DO_NOT_LIKE):
    #if steering != steering_ or accel != accel_:
    if accel != accel_:
        return i_do_not_like * 5
    else:
        return 0


def derive_reward(sensor_values, steering, accel, steering_, accel_, score):
    reward = get_border_distance_reward(min(sensor_values))

    reward += get_acceleration_reward(accel)
    reward += get_steering_reward(steering)
    reward += get_new_action_reward(steering, accel, steering_, accel_)

    done = check_done(score + reward, sensor_values)

    return done, reward





def action_to_movement(action):
    # action [0, 6]
    steering = GO_AHEAD
    acceleration = STOP

    if action == BACKWARD_TURN_LEFT:
        steering = TURN_LEFT
        acceleration = BACKWARDS
    if action == BACKWARDS_GO_AHEAD:
        steering = GO_AHEAD
        acceleration = BACKWARDS
    if action == BACKWARDS_TURN_RIGHT:
        steering = TURN_RIGHT
        acceleration = BACKWARDS

    if action == FORWARDS_TURN_LEFT:
        steering = TURN_LEFT
        acceleration = FORWARDS
    if action == FORWARDS_GO_AHEAD:
        steering = GO_AHEAD
        acceleration = FORWARDS
    if action == FORWARDS_TURN_RIGHT:
        steering = TURN_RIGHT
        acceleration = FORWARDS

    return steering, acceleration


if __name__ == '__main__':

    assert(check_done(score = 100, sensor_values=[90], min_score=-100, max_score= 150, border_end=10) == False)
    assert(check_done(score = -100, sensor_values=[90], min_score=-100, max_score= 150, border_end=10) == True)
    assert(check_done(score = 150, sensor_values=[90], min_score=-100, max_score= 150, border_end=10) == True)
    assert(check_done(score = 100, sensor_values=[5], min_score=-100, max_score= 150, border_end=10) == True)


