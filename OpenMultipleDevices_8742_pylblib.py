import sys
import os
import inspect
import time
import asyncio

# Import the .NET Common Language Runtime (CLR) to allow interaction with .NET
import clr
import numpy as np
from ctypes import byref, c_int

from pylablib.devices import Newport


async def get_controller_position(controller, motor):
    while controller.is_moving(motor):
        await asyncio.sleep(0.1)
    return controller.get_position(motor)


async def jog_for_duration(controller, axis, direction, duration):
    address = controller.get_addr()
    controller.jog(axis, direction, address)
    await asyncio.sleep(duration)
    controller.stop("all", immediate=True)  # Use 'all' when stopping immediately


async def run():
    n = Newport.get_usb_devices_number_picomotor()

    if n == 0:
        return

    controller = Newport.Picomotor8742()
    # print(controller.get_all_axes())

    # Below is for motor 1 (axis 1)
    print('Motor 1')
    motor = 1

    # Initial position
    position = await get_controller_position(controller, motor)
    print("Initial Position: ", position)

    # Absolute movement
    controller.move_to(motor, 50)
    position = await get_controller_position(controller, motor)
    print("Absolute Position: ", position)

    # Relative movement
    controller.move_by(motor, 1000)
    position = await get_controller_position(controller, motor)
    print("Relative Position: ", position)

    # Jog movement (for 3 seconds in negative direction)
    await jog_for_duration(controller, motor, "-", 3)
    position = await get_controller_position(controller, motor)
    print("Jog Position: ", position, "\n")

    # Below is for motor 2 (axis 2)
    print('Motor 2')
    motor = 2

    # Initial position
    position = await get_controller_position(controller, motor)
    print("Initial Position: ", position)

    # Absolute movement
    controller.move_to(motor, 75)
    position = await get_controller_position(controller, motor)
    print("Absolute Position: ", position)

    # Relative movement
    controller.move_by(motor, 600)
    position = await get_controller_position(controller, motor)
    print("Relative Position: ", position)

    # Jog movement (for 2 seconds in positive direction)
    await jog_for_duration(controller, motor, "+", 2)
    position = await get_controller_position(controller, motor)
    print("Jog Position: ", position, "\n")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
