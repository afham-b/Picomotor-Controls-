import sys
import time
import asyncio
import threading
import math
from datetime import datetime
import matplotlib.pyplot as plt
from pylablib.devices import Newport
from lighttest import ArduinoController

import socket

pico_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 5002)  # Use the same address and port as MGListener
pico_sock.bind(server_address)

# file name of the calibration data
filename = 'calibration_data.txt'  # microlens lenslets
#filename = 'calibration_data_nosecone.txt' #nosecone relay

log = open('pico_log.txt', 'a')


class MotorOperations:
    def __init__(self, controller, arduino, motor, default_speed=1750, close_speed=1000, very_close_speed=40):
        self.controller = controller
        self.address = self.controller.get_addr()
        self.motor = motor
        self.arduino = arduino
        self.default_speed = default_speed
        self.close_speed = close_speed
        self.very_close_speed = very_close_speed
        self.set_velocity(self.default_speed, acceleration=10000)

        # steps for motor 1, 2, 3, 4
        self.motor_steps = [0, 0, 0, 0]
        self.calibrated = 0
        self.x = -1
        self.y = 0
        self.x_init = 0
        self.y_init = 0
        self.delt_x_previous = -1
        self.delt_y_previous = -1
        self.delt_x = 0
        self.delt_y = 0
        self.theta = 0

        self.controller.setup_velocity(1, speed=default_speed, accel=200000)
        self.controller.setup_velocity(2, speed=default_speed, accel=200000)

        #used to keep track of rejection of false guide coordinates from metaguide
        self.pixel_threshold = 100
        self.rejected = False
        self.rejection_count = 0
        self.rejection_threshold = 200

        #used to check to see if the motor is stuck, or arms are maxed out
        self.stall_count = 0
        self.stall_threshold = 0.2
        self.max_stall_count = 100

        # Initialize variables to keep track of the previous range
        self.prev_delt_x_range = None
        self.prev_delt_y_range = None
        # Determine the current range for delt_x and delt_y
        self.current_delt_x_range = None
        self.current_delt_y_range = None
        self.range_breakpoint1 = 4.5
        self.range_breakpoint2 = 15
        self.range_breakpoint3 = 50

        self.calibration_files = ['calibration_data.txt', 'calibration_data_nosecone.txt']
        self.calibration_data = {file: {'theta': None, 'timestamp': None} for file in self.calibration_files}
        self.read_calibration_data()

        # when instance is initialized, retrieve the theta value from calibration_data.txt
        with open(filename, 'r') as file:
            lines = file.readlines()
            # Ensure there is at least one line in the file
            if not lines:
                self.theta = 0
                raise ValueError("The Calibration Data File is empty. Check File or Calibrate")

            # Get the latest theta value (last line)
            latest_theta = float(lines[-1].strip())

            self.theta = latest_theta

        # measure and modify the two parameters below for your magnification
        # distance in mm
        self.distance_lens_lightsource = 106
        self.distance_lens_ccd = 116

        #if there is a lens on the camera use magnification calculation
        self.magnification = self.distance_lens_ccd / self.distance_lens_lightsource
        #self.magnification = 1

        # pixel size (micrometer) can be found on camera specifications sheet
        # for asi290mini pixel size is 2.9 microns/px
        # for asi1600 pro pixel size is 3.8 microns/px

        #self.camera_pixel_size = 3.8
        self.camera_pixel_size = 2.9

        #effective pixel size is ~ 4microns/pixel with a lens or 2.9 micron/pixel with no lens
        self.effective_pixel_size = self.camera_pixel_size / self.magnification

        # set scale factor for picomotor motion from camera feedback
        #self.motion_scale = 0.75

        #lenslet
        # self.motion_scale_y = 0.8
        # self.motion_scale_x = 0.8

        #relay
        self.motion_scale_y = 0.75
        self.motion_scale_x = 0.75

        # the pico motor moves 20 nm per step, adjust this value based on the mas the motor moves
        #self.step_size = 0.02

        #is actuation forces for the motors are not eqivalent in both axis, you can set axis specific stepsizes

        #lenslet
        # self.step_size_y = 0.015
        # self.step_size_x = 0.015

        #relay
        self.step_size_y = 0.015
        self.step_size_x = 0.015

        # how close we want the picomotor to try to get to the home position
        self.margin_of_error = 2

    def get_range(self, delta):
        if abs(delta) < self.range_breakpoint1:
            return 1  # Range 1: 0 <= |delta| < 4.5
        elif self.range_breakpoint1 <= abs(delta) <= self.range_breakpoint2:
            return 2  # Range 2: 4.5 <= |delta| <= 10
        elif self.range_breakpoint2 <= abs(delta) <= self.range_breakpoint3:
            return 3  # Range 3: 10 <= |delta| < 50
        else:
            return 4  # Range 4:  |delta| > 50

    async def control_picomotors(self):

        #vars used to keep track for previous deltas, which are assigned at the end of the control picomotors function
        x_pre = self.delt_x
        y_pre = self.delt_y

        # since the real flexure we are compensating for is smooth and grows slowly
        # attempt to reject sudden jumps in offset, likely due to camera metaguide error or mechanical issue

        if self.delt_x_previous != -1 and self.rejection_count < self.rejection_threshold:
            if (abs(self.delt_x - self.delt_x_previous) >= self.pixel_threshold
                    or abs(self.delt_y - self.delt_y_previous) >= self.pixel_threshold):
                self.delt_x = self.delt_x_previous
                self.delt_y = self.delt_y_previous
                self.rejected = True
                self.rejection_count = self.rejection_count + 1
                print("REJECTED")
                return

        if self.rejection_count > self.rejection_threshold:
            print("significant shift above normal threshold measured, Correcting")

        print('control_picomotors output (x,y): ' + str(round(self.delt_x, 4)) + ', ' + str(round(self.delt_y, 4)))

        log.write('\n' + str(datetime.now()) + '    ' + 'control_picomotors output (x,y): ' + str(
            round(self.delt_x, 4)) + ', ' + str(round(self.delt_y, 4)))

        # using theta correction
        if self.theta != 0:
            corrected_delta_x = self.delt_x * math.cos(self.theta) - self.delt_y * math.sin(self.theta)
            corrected_delta_y = self.delt_x * math.sin(self.theta) + self.delt_y * math.cos(self.theta)
            #print("Corrected with theta (x,y)" + str(corrected_delta_x) + ' ' + str(corrected_delta_y))
        else:
            corrected_delta_x = self.delt_x
            corrected_delta_y = self.delt_y

        # not using theta correction
        #corrected_delta_x = self.delt_x
        #corrected_delta_y = self.delt_y

        # Determine the current range for delt_x and delt_y
        current_delt_x_range = self.get_range(self.delt_x)
        current_delt_y_range = self.get_range(self.delt_y)

        # Check if the range for delt_x has changed
        if current_delt_x_range != self.prev_delt_x_range:
            if current_delt_x_range == 1:
                await self.change_velocity(2, 500)  # Set velocity for range 1
            elif current_delt_x_range == 2:
                await self.change_velocity(2, 800)  # Set velocity for range 2
            elif current_delt_x_range == 3:
                await self.change_velocity(2, 1200)  # Example: Set velocity for range 3
            elif current_delt_x_range == 4:
                await self.change_velocity(2, 1700)
            self.prev_delt_x_range = current_delt_x_range  # Update previous range

        if current_delt_y_range != self.prev_delt_y_range:
            if current_delt_y_range == 1:
                await self.change_velocity(1, 500)  # Set velocity for range 1
            elif current_delt_y_range == 2:
                await self.change_velocity(1, 800)  # Set velocity for range 2
            elif current_delt_y_range == 3:
                await self.change_velocity(1, 1200)  # Example: Set velocity for range 3
            elif current_delt_y_range == 4:
                await self.change_velocity(1, 1700)
            self.prev_delt_y_range = current_delt_y_range  # Update previous range

        correction_scale_x = self.effective_pixel_size * self.motion_scale_x
        correction_scale_y = self.effective_pixel_size * self.motion_scale_y

        move_x = corrected_delta_x * correction_scale_x
        move_y = corrected_delta_y * correction_scale_y

        steps_x = move_x / self.step_size_x
        steps_y = move_y / self.step_size_y

        #avoid attempting to move the picomotors by a non integer number of steps
        #steps_x = math.floor(steps_x)
        #steps_y = math.floor(steps_y)

        steps_x = steps_x / 1
        steps_y = steps_y / 1

        # direction: invert steps for x-axis correction on microlens/lenslet array plate
        # direction: invert steps for x-axis correction on relay mirror
        invert = -1
        steps_x = steps_x * invert
        steps_y = steps_y * invert
        #print(f"Steps_x and y: {steps_x}, {steps_y}")

        #y-axis motor
        self.motor = 1

        # for testing
        #print("Correction Beginning, @Line nnn")
        #print('Delta Y: ' + str(self.delt_y))
        #print('Delta X: ' + str(self.delt_x))

        if abs(self.delt_y) > self.margin_of_error:
            # print('delta y moving')
            # print('motor number is ' + str(self.motor))
            #print('about to await move by steps y')
            await self.move_by_steps(steps_y)
            #print('move by steps y awaited')
            await asyncio.sleep(0.001)
        else:
            # self.controller.stop(axis='all', immediate=True, addr=self.address)
            #self.controller.stop(axis='all', immediate=True)
            #print('stopped motion y')
            await asyncio.sleep(0.001)

        #await asyncio.sleep(0.001)
        moving = True
        while moving:
            try:
                moving = self.controller.is_moving(self.motor)
                if not moving:
                    break
            except Exception as e:
                print(f"Error checking if motor is moving: {e}")
                await asyncio.sleep(0.001)
            await asyncio.sleep(0.001)

        self.motor = 2
        # x axis motor
        if abs(self.delt_x) > self.margin_of_error:
            #print('delta x moving')
            # switch to motor 2 to move the x-axis since self by default is y
            #print('motor number is ' + str(self.motor))
            #print("steps x: " + str(steps_x))
            await self.move_by_steps(steps_x)
            await asyncio.sleep(0.001)
        else:
            #self.controller.stop(axis='all', immediate=True)
            await asyncio.sleep(0.001)

        # moving = True
        # while moving:
        #     try:
        #         moving = self.controller.is_moving(self.motor)
        #         if not moving:
        #             break
        #     except Exception as e:
        #         print(f"Error checking if motor is moving: {e}")
        #         await asyncio.sleep(0.001)
        #     await asyncio.sleep(0.001)

        #if abs(self.delt_x) > self.margin_of_error and abs(self.delt_y) > self.margin_of_error:
        #    self.controller.stop(axis='all', immediate=True)

        if abs(self.delt_x) > self.margin_of_error or abs(self.delt_y) > self.margin_of_error:
            if abs(self.delt_x - self.delt_x_previous) > self.stall_threshold or abs(
                    self.delt_y - self.delt_y_previous) > self.stall_threshold:
                self.stall_count += 1
            else:
                self.stall_count = 0
            if self.stall_count > self.max_stall_count:
                print("Motor is stalling. Resetting...")
                try:
                    # put in stalling code here, i.e return motor to home after and relay restart
                    # return motor arms to intial positions
                    self.motor = 1
                    await self.move_to_position(0)
                    self.motor = 2
                    await self.move_to_position(0)
                except ValueError as e:
                    if "invalid literal for int() with base 10" in str(e):
                        print("Error connecting to the Picomotor controller: invalid response detected")
                        print("Attempting to restart controller via Arduino relay")
                        await self.arduino.relay_restart()
                        try:
                            self.controller = Newport.Picomotor8742()
                            self.motor = 1
                            await self.move_to_position(0)
                            self.motor = 2
                            await self.move_to_position(0)
                        except Exception as e:
                            print(f"Failed to reconnect to the Picomotor controller after restart: {e}")
                            #return  # Exit if the reconnection fails

        if not self.rejected:
            self.rejection_count = 0
            self.delt_x_previous = x_pre
            self.delt_y_previous = y_pre

    async def change_velocity(self, motor, speed):
        try:
            self.controller.setup_velocity(motor, speed=speed)
        except ValueError as e:
            # Check if the error message matches the expected invalid literal error
            if "invalid literal for int() with base 10" in str(e):
                print("Error connecting to the Picomotor controller: invalid response detected")
                try:
                    self.controller.setup_velocity(motor, speed=speed)
                except Exception as e:
                    print("Error Setting velocity, passed")
                    pass
        await asyncio.sleep(0.001)
        return

    async def calibration_data_stream(self):
        while True:
            data, _ = pico_sock.recvfrom(4096)  # Buffer size
            self.delt_x, self.delt_y, self.x, self.y = map(float, data.decode().split(','))
            if self.calibrated == 1:
                break
            await asyncio.sleep(0.01)

    async def calibrate(self, filename):

        print("Beginning Calibration")
        #print('Past Stored Theta Values:' + str(self.theta))
        await asyncio.sleep(5)
        print(f"Calibrate Picomotors: {self.delt_x}, {self.delt_y}")
        # print('Motor Number: ' + str(self.motor))

        try:
            await asyncio.sleep(2)
            # use for finding slope
            first_x = self.delt_x
            first_y = self.delt_y
            print(f"First x and y: {self.delt_x}, {self.delt_y}")

            await asyncio.sleep(3)

            print("Setting Reference Points, Standby")

            # position 1 is the motors at zenith, position 0 is motors at t=0 of exposure
            self.motor = 1
            await self.set_position_reference(position=1)
            await asyncio.sleep(2)
            self.motor = 2
            await self.set_position_reference(position=1)

            await asyncio.sleep(3)

            # for the microlens array plate & mirror nosecone plate
            # move y motor in negative motor direction to get positive y shift to find slope
            invert = -1
            calibration_steps = 5000

            self.motor = 1
            await self.move_by_steps(calibration_steps)
            await asyncio.sleep(3)

            print(f"Second x and y: {self.delt_x}, {self.delt_y}")
            second_y = self.delt_y
            second_x = self.delt_x

            if second_y != first_y and second_x != first_x:
                ratio = (second_x - first_x) / (second_y - first_y)
                print(ratio)
                theta = math.asin(ratio)
                self.theta = theta
                print(f'Theta = {self.theta}')
                f = open(filename, 'a')
                f.write('\n' + str(datetime.now()) + '\n' + str(self.theta))
                f.close()
            elif second_x == first_x:
                self.theta = 0
                print("Calibration: No rotational offset detected (x)")
            elif second_y == first_y:
                print("Error In Calibration: No offset detected (y)")

        except Exception as e:
            print(f"Error during calibration: {e}")

        print("Moving y motor back to the original position")
        await self.move_by_steps(5000)
        await asyncio.sleep(1)
        print(f"Calibrated! Theta is {self.theta}")
        self.calibrated = 1
        await asyncio.sleep(0.001)

    async def calibration_process(self, filename):
        await asyncio.gather(self.calibration_data_stream(), self.calibrate(filename))

    def read_calibration_data(self):
        for file in self.calibration_files:
            try:
                with open(file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        latest_entry = lines[-2:]
                        timestamp = latest_entry[0].strip()
                        theta = float(latest_entry[1].strip())
                        self.calibration_data[file] = {'theta': theta, 'timestamp': timestamp}
            except FileNotFoundError:
                print(f"file {file} not found.")
            except Exception as e:
                print(f"Error reading file {file}: {e}")

    #async def start_sock_data(self, arduino):
    async def start_sock_data(self):
        loop_tracker = 0

        print("Last calibrated:")
        for file, data in self.calibration_data.items():
            print(f"    {file}: \n          Theta: {data['theta']}    \n          Time: {data['timestamp']}")

        first_input = True

        while True:
            data, _ = pico_sock.recvfrom(4096)  # Buffer size
            self.delt_x, self.delt_y, self.x, self.y = map(float, data.decode().split(','))
            #print('Socket data received: ' + str(self.delt_x) + str(self.delt_y))

            if first_input and self.x and self.y:
                print("Setting Reference Position, Please Wait")
                #position_y = self.controller.get_position(1)
                #position_x = self.controller.get_position(2)
                #await self.set_position_reference(position_y)
                #self.motor = 2
                #await self.set_position_reference(position_x)

                #this sets the current position as position '0' for both motors
                self.motor = 1
                await self.set_position_reference(position=0)
                self.motor = 2
                await self.set_position_reference(position=0)
                first_input = False

                break

            await asyncio.sleep(0.001)

        while True:
            data, _ = pico_sock.recvfrom(4096)  # Buffer size
            self.delt_x, self.delt_y, self.x, self.y = map(float, data.decode().split(','))
            # print('Socket data received: ' + str(self.delt_x) + str(self.delt_y))

            #await asyncio.sleep(0.01)
            #print('X is : ' + str(self.delt_x+self.x_init))
            # print ('X is : ' + str(self.x))

            #if self.x != -1.00 and self.arduino.light:

            if self.x != -1.00 and self.controller.is_moving(1) != True and self.controller.is_moving(2) != True:
                await self.control_picomotors()

            # if self.x != -1.00:
            #     await self.control_picomotors()

            #await self.control_picomotors()
            await asyncio.sleep(0.001)

    def set_velocity(self, speed, acceleration=10000):
        self.controller.setup_velocity(self.motor, speed=speed, accel=acceleration)

    # move the motors counter to the total integrated amount of steps at the end of the correction
    async def counter_steps(self):
        # Loop through the motor numbers (1 to 4) and their respective step counts

        n = Newport.get_usb_devices_number_picomotor()
        if n == 0:
            return

        #print(self.motor_steps)

        #set to max speed
        await self.change_velocity(1,1700)
        await self.change_velocity(2,1700)

        #self.motor =1
        #total_steps_y = int(self.controller.get_position())
        #print(total_steps_y)
        #self.motor =2
        #total_steps_x = int(self.controller.get_position())
        #print(total_steps_x)

        homing_time_y = 0
        #homing_time_y_max = (total_steps_y / 1700) + 5
        #print(homing_time_y_max)

        homing_time_x = 0
        #homing_time_x_max = (total_steps_x / 1700) + 5
        #print(homing_time_x_max)

        # if unsure of steps give each motor 1 min to reset
        default_homing_time = 60 #seconds

        self.motor = 1
        #await self.move_to_position(1, self.controller)
        await self.move_to_position(1)
        while self.controller.is_moving():
            homing_time_y += 1
            if homing_time_y > default_homing_time:
                break
            await asyncio.sleep(1)
        print('Motor 1 Homed')

        self.motor = 2
        await self.move_to_position(1)
        while self.controller.is_moving():
            homing_time_x += 1
            if homing_time_x > default_homing_time:
                break
            await asyncio.sleep(0.5)
        print('Motor 2 Homed')

        if not self.controller.is_moving(1) and not self.controller.is_moving(2):
            return True

        # for i in range(4):
        #     self.motor = i + 1  # Set motor to the current motor number
        #     motor_counter_steps = -1 * self.motor_steps[i]  # Calculate counter steps
        #     await self.move_by_steps(motor_counter_steps)  # Move the motor by the counter steps

    async def get_position(self):
        while True:
            try:
                if not self.controller.is_moving(self.motor):
                    break
            except Exception as e:
                print(f"Error checking if motor is moving: {e}")
            await asyncio.sleep(0.005)
        return self.controller.get_position(self.motor)

    async def move_to_position(self, position, stop_event=None):
        """
        Move to an absolute position.
        """
        self.controller.move_to(self.motor, position)
        while not (stop_event and stop_event.is_set()) and self.controller.is_moving(self.motor):
            await asyncio.sleep(0.001)
        await asyncio.sleep(2)  # Pause for 2 seconds

    # async def move_by_steps(self, steps, stop_event=None):
    async def move_by_steps(self, steps, stop_event=None):
        """
        Move by a number of steps.
        """
        self.controller.move_by(self.motor, steps)

        self.motor_steps[self.motor - 1] = self.motor_steps[self.motor - 1] + steps

        start_time = time.time()
        timeout = 10  # Timeout in n seconds

        moving = True

        while not (stop_event and stop_event.is_set()) and moving:
            await asyncio.sleep(0.001)
            elapsed_time = time.time() - start_time
            moving = self.controller.is_moving(self.motor)
            if elapsed_time > timeout:
                print("Move_by_Steps Timeout reached")
                # self.controller.stop(axis='all', immediate=True, addr=self.address)
                self.controller.stop(axis='all', immediate=True)
                moving = False
                # self.controller = controller # is this breaking the code?
                await self.start_sock_data()
                break
            try:
                if not self.controller.is_moving(self.motor):
                    break
            except Exception as e:
                print(f"Error checking if motor is moving: {e}")
                await asyncio.sleep(0.001)

            # time.sleep(0.001)
            await asyncio.sleep(0.001)

        await asyncio.sleep(0.001)  # Pause for n seconds
        # time.sleep(0.001)

    async def set_position_reference(self, position=0):
        # Set the current position as the reference position
        self.controller.set_position_reference(self.motor, position)
        await asyncio.sleep(0.5)  # Small delay to ensure the command is processed

    async def perform_operations(self, stop_event=None, distance=0.02):
        print(f'Motor {self.motor}')

        # for most masses below 1lb, the picomotor moves 20 nm per step
        steps = int((distance * 1e6) / 20)

        # Set the current position as the reference position
        await self.set_position_reference(position=0)

        # Move to initial home position (0.00)
        await self.move_to_position(0, stop_event=stop_event)
        print("Position: Home (0.00mm)")

        # Move to -0.02mm (1000 steps)
        await self.move_by_steps(steps, stop_event=stop_event)
        print("Position: -0.02mm")

        # Move to initial home position (0.00)
        await self.move_to_position(0, stop_event=stop_event)
        print("Position: Home (0.00mm)")

        # Move to +0.02mm (1000 steps from -0.02mm)
        await self.move_by_steps((-1 * steps), stop_event=stop_event)
        print("Position: +0.02mm")

        # Move back home (0.00)
        await self.move_to_position(0, stop_event=stop_event)
        print("Position: Home (0.00mm)")

    async def jog_until(self, laser, target_distance, margin=0.1, stop_event=None):
        address = self.address
        current_distance = laser.measure(verbose=True)
        if current_distance is None:
            print("Initial laser measurement failed. Aborting.")
            return

        direction = "+" if current_distance > target_distance else "-"
        self.controller.jog(self.motor, direction, address)

        while not (stop_event and stop_event.is_set()):
            distance = laser.measure(verbose=True)
            distance_to_target = distance - target_distance

            # Determine direction based on the current position and target distance
            new_direction = "+" if distance_to_target > 0 else "-"
            if new_direction != direction:
                print(f"Switching direction from {direction} to {new_direction}")
                self.controller.stop(axis='all', immediate=True)
                self.controller.jog(self.motor, new_direction, address)
                direction = new_direction

            # Adjust speed based on distance to target
            if abs(distance_to_target) < 0.001:
                self.set_velocity(1)
            elif abs(distance_to_target) < 0.005:
                self.set_velocity(3)
            elif abs(distance_to_target) < 0.01:
                self.set_velocity(self.very_close_speed)
            elif abs(distance_to_target) < 0.05:
                self.set_velocity(self.close_speed)
            elif abs(distance_to_target) < 0.1:
                self.set_velocity(1000)
            else:
                self.set_velocity(self.default_speed)

            if target_distance - margin <= distance <= target_distance + margin:
                self.controller.stop(axis='all', immediate=True)
                await asyncio.sleep(5)  # Pause for 5 seconds (this is for testing)
                break
            await asyncio.sleep(0.001)

        self.controller.stop(axis='all', immediate=True)

    async def joggin(self, target_distance=0, margin=0.1, stop_event=None):
        address = self.address

        if self.delt_y is None:
            print("Initial laser measurement failed. Aborting.")
            return

        direction = "+" if self.delt_y > target_distance else "-"
        self.controller.jog(self.motor, direction, address)

        while not (stop_event and stop_event.is_set()):
            distance_to_target = self.delt_y - target_distance

            # Determine direction based on the current position and target distance
            new_direction = "+" if distance_to_target > 0 else "-"
            if new_direction != direction:
                print(f"Switching direction from {direction} to {new_direction}")
                self.controller.stop(axis='all', immediate=True)
                self.controller.jog(self.motor, new_direction, address)
                direction = new_direction

            # Adjust speed based on distance to target
            if abs(distance_to_target) < 0.001:
                self.set_velocity(1)
            elif abs(distance_to_target) < 0.005:
                self.set_velocity(3)
            elif abs(distance_to_target) < 0.01:
                self.set_velocity(self.very_close_speed)
            elif abs(distance_to_target) < 0.05:
                self.set_velocity(self.close_speed)
            elif abs(distance_to_target) < 0.1:
                self.set_velocity(1000)
            else:
                self.set_velocity(self.default_speed)

            if target_distance - margin <= self.delt_y <= target_distance + margin:
                self.controller.stop(axis='all', immediate=True)
                await asyncio.sleep(5)  # Pause for 5 seconds (this is for testing)
                break
            await asyncio.sleep(0.001)

        self.controller.stop(axis='all', immediate=True)


async def motor_operations_task(controller, stop_event):
    motor1_operations = MotorOperations(controller, motor=1)
    await motor1_operations.perform_operations(stop_event=stop_event, distance=0.02)


def plot_measurements(measurements):
    times, distances = zip(*measurements)
    plt.figure()
    plt.plot(times, distances, label="Distance from Motor")
    plt.axhline(y=0.02, color='r', linestyle='--', label="Target Distance +0.02mm")
    plt.axhline(y=-0.02, color='b', linestyle='--', label="Target Distance -0.02mm")
    plt.xlabel("Time (s)")
    plt.ylabel("Distance (mm)")
    plt.legend()
    plt.title("Motor Position Data")
    plt.show()


async def run(controller):
    print("measuring")
    stop_event = asyncio.Event()
    duration = None
    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
        asyncio.get_event_loop().call_later(duration, stop_event.set)

    motor_task = asyncio.create_task(motor_operations_task(controller, stop_event))
    await motor_task


def stop_motors(controller):
    controller.stop(axis='all', immediate=True)
    print("Motors stopped.")


def monitor_keyboard(controller, loop, stop_event):
    while True:
        key = input()
        if key.lower() == 'x':
            stop_motors(controller)
            stop_event.set()
            loop.stop()
            break


if __name__ == "__main__":
    n = Newport.get_usb_devices_number_picomotor()
    if n == 0:
        print("No Picomotor devices found.")
    else:
        controller = Newport.Picomotor8742()
        loop = asyncio.get_event_loop()
        stop_event = asyncio.Event()

        threading.Thread(target=monitor_keyboard, args=(controller, loop, stop_event)).start()

        try:
            loop.run_until_complete(run(controller))
        except asyncio.CancelledError or KeyboardInterrupt:
            pass
        finally:
            def end():
                stop_motors(controller)
                loop.close()
                controller.close()


            end()
            print("done")
