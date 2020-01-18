from r8 import R8

DONE_MAX_SCORE = 1000
DONE_MIN_SCORE = -200

I_DO_NOT_LIKE = -0.07

BORDER_START = 50
BORDER_END = 20
BORDER_MAX_NEGATIVE_REWARD = -100
BORDER_REWARD_SLOPE = BORDER_MAX_NEGATIVE_REWARD / (BORDER_START - BORDER_END)
assert(BORDER_REWARD_SLOPE <= 0.0)


def check_done(score, sensor_values, min_score=DONE_MIN_SCORE, max_score=DONE_MAX_SCORE, border_end=BORDER_END):
    if score >= max_score or score <= min_score or min(sensor_values) < border_end:
        return True
    else:
        return False


def get_border_distance_reward(closest_distance, border_reward_slope=BORDER_REWARD_SLOPE, border_start=BORDER_START):
    is_to_close = closest_distance < border_start
    return int(is_to_close) * ((border_start - closest_distance) * border_reward_slope)


def get_acceleration_reward(acceleration, reward_go_ahead = 1,reward_backwards = 0.1, reward_stop=I_DO_NOT_LIKE):
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
    if steering != steering_ or accel != accel_:
        return i_do_not_like
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


if __name__ == '__main__':

    assert(get_border_distance_reward(1100, -0.1, 10) == 0)
    assert(get_border_distance_reward(11, -0.1, 10) == 0)
    assert(get_border_distance_reward(9, -0.1, 10) == -0.1 )
    assert(get_border_distance_reward(1, -0.1, 10) == -0.9)
    assert(get_border_distance_reward(0, -0.1, 10) == -1.0)

    assert(check_done(score = 100, sensor_values=[90], min_score=-100, max_score= 150, border_end=10) == False)
    assert(check_done(score = -100, sensor_values=[90], min_score=-100, max_score= 150, border_end=10) == True)
    assert(check_done(score = 150, sensor_values=[90], min_score=-100, max_score= 150, border_end=10) == True)
    assert(check_done(score = 100, sensor_values=[5], min_score=-100, max_score= 150, border_end=10) == True)

    assert(get_acceleration_reward(1, 1, 0.1, -0.5) == 1)
    assert(get_acceleration_reward(0, 1, 0.1, -0.5) == -0.5)
    assert(get_acceleration_reward(-1, 1, 0.1, -0.5)== 0.1)


