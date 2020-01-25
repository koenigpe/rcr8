import math
import time

import numpy as np
import pygame


def np_set_zero_point(coords, zero_point):
    x = coords[:, 0] - zero_point[0]
    y = coords[:, 1] - zero_point[1]
    return np.stack((x, y), axis=1)


def np_cart_to_polar(coords, zero_point, revert_y=True):

    if revert_y:
        y_relativ = coords[:, 1] *-1 - zero_point[1] *-1
    else:
        y_relativ = coords[:, 1] - zero_point[1]
    x_relativ = coords[:, 0] - zero_point[0] + (1 / 10 ** 10)
    deg = np.rad2deg(np.arctan(y_relativ / x_relativ))
    d = np.sqrt((y_relativ) ** 2 + (x_relativ) ** 2)
    deg[(x_relativ > 0) & (y_relativ < 0)] += 360
    deg[(x_relativ < 0) & (y_relativ > 0)] += 180
    deg[(x_relativ < 0) & (y_relativ < 0)] += 180
    return np.stack((deg, d), axis=1)


def np_rotate_polar(coords, deg_):
    deg = (coords[:, 0] + deg_) % 360
    d = coords[:, 1]
    return np.stack((deg, d), axis=1)


def np_polar_to_cart(coords, zero_point, revert_y=True):
    deg = np.deg2rad(coords[:, 0])
    d = coords[:, 1]

    x = d * np.cos(deg) + zero_point[0]
    if revert_y:
        y = ((d * np.sin(deg)) - zero_point[1]) *-1
    else:
        y = d * np.sin(deg) + zero_point[1]
    return np.stack((x, y), axis=1)


def cart_to_polar(coords, zero_point):
    x = coords[0]
    y = coords[1]
    d = math.sqrt((x - zero_point[0]) ** 2 + (y - zero_point[1]) ** 2)
    deg = math.degrees(math.atan((y - zero_point[1]) / (x - zero_point[0])))
    deg = deg + (180 if x - zero_point[0] < 0 and y - zero_point[1] > 0 else 0)
    deg = deg + (180 if x - zero_point[0] < 0 and y - zero_point[1] < 0 else 0)
    deg = deg + (360 if x - zero_point[0] > 0 and y - zero_point[1] < 0 else 0)

    return deg, d


def polar_to_cart(coords):
    deg = coords[0]
    d = coords[1]

    x = d * np.cos(deg)
    y = d * np.sin(deg)
    return (x, y)


if __name__ == '__main__':


    input = np.vstack([np.array((x, x)) for x in range(0, 3)])

    assert (np.array_equal(np_set_zero_point(input, (1, 1)), np.vstack([np.array((x, x)) for x in range(-1, 2, 1)])))

    assert (np.round(np_cart_to_polar(input, (0, 0), False)[2, 1], 3) == 2.828)
    assert (np.round(np_cart_to_polar(input, (0, 0), False)[1, 1],3 ) == 1.414)

    assert (np.array_equal(np.round(np_cart_to_polar(np.array((2, 2))[np.newaxis, :], (1, 1), False)[0]),
                           np.array([45.0, 1.0])))
    assert (np.array_equal(np.round(np_cart_to_polar(np.array((0, 2))[np.newaxis, :], (1, 1), False)[0]),
                           np.array([135.0, 1.0])))
    assert (np.array_equal(np.round(np_cart_to_polar(np.array((0, 0))[np.newaxis, :], (1, 1), False)[0]),
                           np.array([225.0, 1.0])))
    assert (np.array_equal(np.round(np_cart_to_polar(np.array((2, 0))[np.newaxis, :], (1, 1), False)[0]),
                           np.array([315.0, 1.0])))

    assert (np.array_equal(np.round(np_cart_to_polar(np.array((0, 2))[np.newaxis, :], (-1, 1), False)[0]),
                           np.array([45.0, 1.0])))
    assert (np.array_equal(np.round(np_cart_to_polar(np.array((-2, 2))[np.newaxis, :], (-1, 1), False)[0]),
                           np.array([135.0, 1.0])))
    assert (np.array_equal(np.round(np_cart_to_polar(np.array((-2, 0))[np.newaxis, :], (-1, 1), False)[0]),
                           np.array([225.0, 1.0])))
    assert (np.array_equal(np.round(np_cart_to_polar(np.array((0, 0))[np.newaxis, :], (-1, 1), False)[0]),
                           np.array([315.0, 1.0])))

    assert (np.array_equal(np.round(np_cart_to_polar(np.array((0, 0))[np.newaxis, :], (-1, -1), False)[0]),
                           np.array([45.0, 1.0])))
    assert (np.array_equal(np.round(np_cart_to_polar(np.array((-2, 0))[np.newaxis, :], (-1, -1), False)[0]),
                           np.array([135.0, 1.0])))
    assert (np.array_equal(np.round(np_cart_to_polar(np.array((-2, -2))[np.newaxis, :], (-1, -1), False)[0]),
                           np.array([225.0, 1.0])))
    assert (np.array_equal(np.round(np_cart_to_polar(np.array((0, -2))[np.newaxis, :], (-1, -1), False)[0]),
                           np.array([315.0, 1.0])))

    assert ((cart_to_polar((2, 2), (1, 1)))[0] == 45.0)
    assert ((cart_to_polar((0, 2), (1, 1)))[0] == 135.0)
    assert ((cart_to_polar((0, 0), (1, 1)))[0] == 225.0)
    assert ((cart_to_polar((2, 0), (1, 1)))[0] == 315.0)

    assert (np.array_equal(np.round(np_cart_to_polar(np.array((2, -2))[np.newaxis, :], (2, -2), False), 3)[0], np.array((0.0, 0.0))))

    assert (np.array_equal(np.round(np_cart_to_polar(np.array((-2, 2))[np.newaxis, :], (-2, 2), False), 3)[0], np.array((0.0, 0.0))))

    assert (np.array_equal(
        np.round(np_polar_to_cart(np_rotate_polar(np_cart_to_polar(np.array((1, 1))[np.newaxis, :], (0, 0), False), 90),(0, 0), False), 4),
        np.array((-1, 1))[np.newaxis, :]))

    assert (np.array_equal(
        np.round(np_polar_to_cart(np_rotate_polar(np_cart_to_polar(np.array((1, 1))[np.newaxis, :], (0, 0)), 90), (0, 0)), 4),
        np.array((1, -1))[np.newaxis, :]))

    assert (np.array_equal(
        np.round(np_polar_to_cart(np_rotate_polar(np_cart_to_polar(np.array((1, 1))[np.newaxis, :], (0, 0), False), 180), (0, 0),False), 4),
        np.array((-1, -1))[np.newaxis, :]))

    assert (np.array_equal(
        np.round(np_polar_to_cart(np_rotate_polar(np_cart_to_polar(np.array((1, 1))[np.newaxis, :], (0, 0)), 180), (0, 0), False), 4),
        np.array((-1, 1))[np.newaxis, :]))

    assert (np.array_equal(np.round(np_polar_to_cart(np_cart_to_polar(input, (0, 0), False), (0, 0),False), 4), input))


    assert(np.array_equal(np.array((1, -2))[np.newaxis, :], np_polar_to_cart(np_cart_to_polar(np.array((1, -2))[np.newaxis, :], (1, 1), False), (1, 1), False).astype('int')))
    assert(np.array_equal(np.array((1, -2))[np.newaxis, :], np_polar_to_cart(np_cart_to_polar(np.array((1, -2))[np.newaxis, :], (1, -1), False), (1, -1), False).astype('int')))
    assert(np.array_equal(np.array((1, -2))[np.newaxis, :], np_polar_to_cart(np_cart_to_polar(np.array((1, -2))[np.newaxis, :], (-1, 1), False), (-1, 1), False).astype('int')))
    assert(np.array_equal(np.array((1, -2))[np.newaxis, :], np_polar_to_cart(np_cart_to_polar(np.array((1, -2))[np.newaxis, :], (-1, -1), False), (-1, -1), False).astype('int')))

    assert(np.array_equal(np.array((1, -2))[np.newaxis, :], np_polar_to_cart(np_cart_to_polar(np.array((1, -2))[np.newaxis, :], (1, 1), True), (1, 1), True).astype('int')))
    assert(np.array_equal(np.array((1, -2))[np.newaxis, :], np_polar_to_cart(np_cart_to_polar(np.array((1, -2))[np.newaxis, :], (1, -1), True), (1, -1), True).astype('int')))
    assert(np.array_equal(np.array((1, -2))[np.newaxis, :], np_polar_to_cart(np_cart_to_polar(np.array((1, -2))[np.newaxis, :], (-1, 1), True), (-1, 1), True).astype('int')))
    assert(np.array_equal(np.array((1, -2))[np.newaxis, :], np_polar_to_cart(np_cart_to_polar(np.array((1, -2))[np.newaxis, :], (-1, -1), True), (-1, -1), True).astype('int')))



    # ToDo: Check this artifact
    pygame.font.init()
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    position = (500, 500)

    area = np.concatenate([[np.array((position[0] + x, position[1] + y)) for y in range(-100, 110, 100)] for x in range(-100, 110, 100)])

    angle = 90

    [pygame.draw.circle(screen, (0, 255, 0), a, 1) for a in area]

    pol = np_rotate_polar(np_cart_to_polar(coords=area, zero_point=(500, 500), revert_y=True), 45)
    [pygame.draw.circle(screen, (100,100,100), np.round(r, 0).astype('int'), 4, 4) for r in np_polar_to_cart(pol, (500, 500), True)]

    pygame.display.update()
    time.sleep(5)



