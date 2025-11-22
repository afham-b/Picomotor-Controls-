import sys
import os
import inspect
import time
import asyncio
import serial
import io
import datetime

# Import the .NET Common Language Runtime (CLR) to allow interaction with .NET
import clr
import numpy as np
from ctypes import byref, c_int

from pylablib.devices import Newport

class MotorOperations:
    def __init__(self, controller, motor):
        self.controller = controller
        self.motor = motor

    async def get_position(self):
        while True:
            try:
                if not self.controller.is_moving(self.motor):
                    break
            except Exception as e:
                print(f"Error checking if motor is moving: {e}")
            await asyncio.sleep(0.1)
        return self.controller.get_position(self.motor)

    async def jog_for_duration(self, direction, duration):
        address = self.controller.get_addr()
        self.controller.jog(self.motor, direction, address)
        await asyncio.sleep(duration)
        self.controller.stop(axis='all', immediate=True)  # Use 'all' for immediate stop

    async def move_to_position(self, position):
        self.controller.move_to(self.motor, position)
        return await self.get_position()

    async def move_by_steps(self, steps):
        self.controller.move_by(self.motor, steps)
        return await self.get_position()

    async def perform_operations(self, absolute_position, relative_steps, jog_direction, jog_duration):
        print(f'Motor {self.motor}')

        # Initial position
        position = await self.get_position()
        print("Initial Position: ", position)

        # Absolute movement
        position = await self.move_to_position(absolute_position)
        print("Absolute Position: ", position)

        # Relative movement
        position = await self.move_by_steps(relative_steps)
        print("Relative Position: ", position)

        # Jog movement
        await self.jog_for_duration(jog_direction, jog_duration)
        position = await self.get_position()
        print("Jog Position: ", position, "\n")


class LaserIO(object):

    def __init__(self, laser_port="COM5"):  # Update with the correct COM port
        self.laser_port = laser_port
        self.ser = serial.Serial(self.laser_port, 9600, timeout=0.25)
        self.ser_io = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 1),
                                       newline='\r',
                                       line_buffering=True)
        self.normal_mode()

    def normal_mode(self):
        print("normal mode")
        self.ser_io.write(u"R0\r")
        out = self.ser_io.readline()
        print(out)

    def measure(self, verbose=True):
        '''
        Get laser head measurement through serial
        '''
        self.ser_io.write(u'M0\r')
        out = self.ser_io.readline()
        if verbose:
            print(out)

        i = out.rfind("M0,") + 3
        if i == -1:
            print("M0 measurement not found")
            return None
        j = out[i:].find(",")
        head_val = out[i:i + j]
        print(head_val)

        if self.isfloat(head_val):
            distance = float(head_val)
            return distance
        else:
            print("Laser head out of range")
            return None

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def close(self):
        self.ser.close()
        return None


async def motor_operations_task(controller):
    motor1_operations = MotorOperations(controller, motor=1)
    await motor1_operations.perform_operations(absolute_position=50, relative_steps=1000, jog_direction="-", jog_duration=3)


async def laser_logging_task(laser, duration, logfile):
    start_time = time.time()
    while time.time() - start_time < duration:
        zlaser = laser.measure()
        line = str(time.time() - start_time) + "\t" + str(zlaser) + "\n"
        logfile.write(line)
        await asyncio.sleep(0.1)  # Adjust sleep duration as needed for logging frequency


async def run():
    print("measuring")
    if len(sys.argv) < 2:
        print("Usage: python laser_serial.py <duration>")
        return

    duration = int(sys.argv[1])
    laser = LaserIO()
    logfile = open("laser_log_" + str(datetime.date.today()) + '_' + str(time.time()) + ".txt", 'w')

    n = Newport.get_usb_devices_number_picomotor()
    if n == 0:
        print("No Picomotor devices found.")
        laser.close()
        return

    controller = Newport.Picomotor8742()

    motor_task = motor_operations_task(controller)
    laser_task = laser_logging_task(laser, duration, logfile)

    await asyncio.gather(motor_task, laser_task)

    logfile.close()
    laser.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
