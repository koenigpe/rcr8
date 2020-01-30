import struct

import serial
import numpy as np

from rl.env.r8_physics import MAX_SENSOR_DISTANCE_CM, GO_AHEAD, STOP


class R8():

    def __init__(self, serial_port, baudrate = 9600, timeout = 10):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = serial.Serial(serial_port, baudrate, timeout = timeout)

    def __del__(self):
        self.full_stop()

    def get_state(self):
        self.connection.write(bytes(":d\r\n", "UTF-8"))
        incoming = self.connection.read(5)
        state = np.array([int(i) for i in incoming])
        state[state > MAX_SENSOR_DISTANCE_CM] = MAX_SENSOR_DISTANCE_CM
        state = state / MAX_SENSOR_DISTANCE_CM
        return state

    def send_steering(self, direction):
        self.connection.write(bytes(":s", "UTF-8"))
        self.connection.write(struct.pack("B", direction + 1))
        self.connection.write(bytes("\r\n", "UTF-8"))

    def send_accelleration(self, direction):
        self.connection.write(bytes(":a", "UTF-8"))
        self.connection.write(struct.pack("B", direction + 1))
        self.connection.write(bytes("\r\n", "UTF-8"))

    def full_stop(self):
        self.send_steering(GO_AHEAD)
        self.send_accelleration(STOP)





