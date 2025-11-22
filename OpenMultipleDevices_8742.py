import sys
import os
import inspect

# Import the .NET Common Language Runtime (CLR) to allow interaction with .NET
import clr
import numpy as np
from ctypes import byref, c_int

print("Python %s\n\n" % (sys.version,))

strCurrFile = os.path.abspath(inspect.stack()[0][1])
print("Executing File = %s\n" % strCurrFile)

# Initialize the DLL folder path to where the DLLs are located
strPathDllFolder = os.path.dirname(strCurrFile)
print("Executing Dir  = %s\n" % strPathDllFolder)

# Add the DLL folder path to the system search path (before adding references)
sys.path.append(strPathDllFolder)

# Add a reference to each .NET assembly required
clr.AddReference("DeviceIOLib")
clr.AddReference("CmdLib8742")

clr.AddReference(os.path.join(strPathDllFolder, "DeviceIOLib"))
clr.AddReference(os.path.join(strPathDllFolder, "CmdLib8742"))


# Import a class from a namespace
from Newport.DeviceIOLib import DeviceIOLib
from NewFocus.PicomotorApp import CmdLib8742
from System.Text import StringBuilder

print("Waiting for device discovery...")
# Call the class constructor to create an object
deviceIO = DeviceIOLib(True)
cmdLib8742 = CmdLib8742(deviceIO)

# Set up USB to only discover picomotors
deviceIO.SetUSBProductID(0x4000)

# Discover USB and Ethernet devices - delay 5 seconds
deviceIO.DiscoverDevices(5, 5000)

# Get the list of discovered devices
strDeviceKeys = deviceIO.GetDeviceKeys()
nDeviceCount = deviceIO.GetDeviceCount()
print("Device Count = %d\n" % nDeviceCount)

# Print available methods in CmdLib8742
# for method in dir(CmdLib8742):
#    if callable(getattr(CmdLib8742, method)):
#        print(f"Method: {method}")


def get_motor_position(device_key, motor, current_position):
    _, new_position = cmdLib8742.GetPosition(device_key, motor, current_position)
    print(f"New position = {new_position}")
    return new_position


if nDeviceCount > 0:
    strBldr = StringBuilder(64)
    n = 0

    # For each device key in the list
    for oDeviceKey in strDeviceKeys:
        strDeviceKey = str(oDeviceKey)
        n = n + 1
        print("Device Key[%d] = %s" % (n, strDeviceKey))

        # If the device was opened
        if deviceIO.Open(strDeviceKey):

            strModel = ""
            strSerialNum = ""
            strFwVersion = ""
            strFwDate = ""
            nReturn = -1

            strModel, strSerialNum, strFwVersion, strFwDate = (
                cmdLib8742.IdentifyInstrument(
                    strDeviceKey,
                    strModel,
                    strSerialNum,
                    strFwVersion,
                    strFwDate,
                )
            )
            print("Return Value = %s" % nReturn)
            print("Model = %s" % strModel)
            print("Serial Num = %s" % strSerialNum)
            print("Fw Version = %s" % strFwVersion)
            print("Fw Date = %s\n" % strFwDate)

            strCmd = "*IDN?"
            strBldr.Remove(0, strBldr.Length)
            nReturn = deviceIO.Query(strDeviceKey, strCmd, strBldr)
            print("Return Status = %d" % nReturn)
            print("*IDN Response = %s\n\n" % strBldr.ToString())

            target_pos = 0
            motor = 1  # Example motor number

            if not cmdLib8742.AbsoluteMove(strDeviceKey, motor, target_pos):
                break

            print(f"Motor {motor} moved to position zero")
            position = get_motor_position(strDeviceKey, motor, target_pos)
            print(f"Current Position: {position}")

            # Attempting Relative Move
            relative_steps = 100  # Example number of steps to move
            if not cmdLib8742.RelativeMove(strDeviceKey, motor, relative_steps):
                break

            print(
                f"Motor {motor} moved {relative_steps} steps relative to its current position."
            )
            position = get_motor_position(strDeviceKey, motor, position)
            print(f"Current Position: {position}")

            # Attempting Absolute Move
            target_pos = 2000  # Example target position
            if not cmdLib8742.AbsoluteMove(strDeviceKey, motor, target_pos):
                break

            print(f"Motor {motor} moved to absolute position {target_pos}.")
            position = get_motor_position(strDeviceKey, motor, position)
            print(f"Current Position: {position}")

            # Attempting Jog Move
            if not cmdLib8742.JogPositive(strDeviceKey, motor):
                break

            print(f"Motor {motor} jogged positive.")
            position = get_motor_position(strDeviceKey, motor, position)
            print(f"Current Position: {position}")

            if not cmdLib8742.JogNegative(strDeviceKey, motor):
                break

            print(f"Motor {motor} jogged negative.")
            position = get_motor_position(strDeviceKey, motor, position)
            print(f"Current Position: {position}")

            # Close the device
            nReturn = deviceIO.Close(strDeviceKey)
else:
    print("No devices discovered.\n")

# Shut down all communication
cmdLib8742.Shutdown()
deviceIO.Shutdown()