import struct

import serial
import numpy as np


class R8():

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

    def __init__(self, serial_port, baudrate = 9600, timeout = 10):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = serial.Serial(serial_port, baudrate, timeout = timeout)

    def __del__(self):
        self.full_stop()

    def get_state(self):
        self.connection.write(bytes(":d\r\n", "UTF-8"))
        incomming = self.connection.read(5)
        return np.array([int(i) for i in incomming])

    def send_steering(self, direction):
        self.connection.write(bytes(":s", "UTF-8"))
        self.connection.write(struct.pack("B", direction + 1))
        self.connection.write(bytes("\r\n", "UTF-8"))

    def send_accelleration(self, direction):
        self.connection.write(bytes(":a", "UTF-8"))
        self.connection.write(struct.pack("B", direction + 1))
        self.connection.write(bytes("\r\n", "UTF-8"))

    def full_stop(self):
        self.send_steering(0)
        self.send_accelleration(0)





