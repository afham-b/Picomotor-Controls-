import sys
import os
import inspect
import clr
import numpy as np

# ----- Locate this script and DLL folder -----
this_file = os.path.abspath(inspect.stack()[0][1])
dll_dir = os.path.dirname(this_file)

print("Executing file:", this_file)
print("DLL directory:", dll_dir)

# Make sure DLL dir is on sys.path so CLR can find them
sys.path.append(dll_dir)

# ----- Load the .NET assemblies -----
clr.AddReference("DeviceIOLib")
clr.AddReference("CmdLib8742")

from Newport.DeviceIOLib import DeviceIOLib
from NewFocus.PicomotorApp import CmdLib8742
from System.Text import StringBuilder

# ----- Create the DeviceIO + CmdLib objects -----
print("Waiting for device discovery...")
deviceIO = DeviceIOLib(True)       # True = enable logging
cmdLib = CmdLib8742(deviceIO)

# Restrict USB discovery to Picomotors (product ID 0x4000, from Newport sample)
deviceIO.SetUSBProductID(0x4000)

# Discover USB + Ethernet devices (arguments: maxDevices, timeout)
deviceIO.DiscoverDevices(5, 5000)

# Get all device keys and count
keys = deviceIO.GetDeviceKeys()
count = deviceIO.GetDeviceCount()
print("Device count:", count)

if count == 0:
    print("No 8742 controllers found.")
else:
    # Use the first discovered device key
    dev_key = str(keys[0])
    print("Using device key:", dev_key)

    if deviceIO.Open(dev_key):
        model = ""
        serial = ""
        fw_ver = ""
        fw_date = ""   # still pass something in, but we won't unpack it
        ret = -1

        # DLL currently returns 4 values: (ret, model, serial, fw_ver)
        ret, model, serial, fw_ver = cmdLib.IdentifyInstrument(
            dev_key, model, serial, fw_ver, fw_date
        )

        print("Return Value =", ret)
        print("Model =", model)
        print("Serial Num =", serial)
        print("Fw Version =", fw_ver)

        # You can also send raw commands if needed
        sb = StringBuilder(64)
        cmd = "*IDN?"
        sb.Remove(0, sb.Length)
        ret = deviceIO.Query(dev_key, cmd, sb)
        print("Query status:", ret)
        print("*IDN? response:", sb.ToString())

        # Close device when done
        deviceIO.Close(dev_key)
    else:
        print("Failed to open device key:", dev_key)

# Clean shutdown
cmdLib.Shutdown()
deviceIO.Shutdown()
