# import win32api
# import win32con
# from pywinauto import Application
import os
import time
import threading
import socket
import time
import sys
import select
import math
import psutil
import signal
import pyuac
import ctypes


# win32 import usually crashes the code, but it's useful
# import win32com.client

# this is from MGListener.py file, which must be in the same directory as mg_track
# MGListener.py is located in program files x86 \ MetaGuide folder by default
from MGListener import MyListener, MGListener, MGMonitor

# Run CMD as administrator to eliminate popups. If not running as admin, use run_as_admin()
# see below for main()
# however the popup still shows up...
"""def run_as_admin():
    if sys.platform == 'win32':
        try:
            # Elevate script's privileges using ShellExecuteW
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        except Exception as e:
            print(f"Failed to run as administrator: {e}")
            """
# alternative: use run_as_admin.bat

def main():

    # code to use PIDs to kill programs

    # can start MetaGuide via the plain.exe
    # app = Application().start(r"C:\Program Files (x86)\MetaGuide\MetaGuide.exe")
    # time.sleep(10)  # Wait for MetaGuide to open

    # can also start MetaGuide this way:
    # idguide = win32api.RegisterWindowMessage("MG_RemoteGuide")
    # win32api.PostMessage(win32con.HWND_BROADCAST, idguide, 0, 0)

    # We're starting with a saved MetaGuide setup file: test1
    # remember to change to your own path!
    scope_setup_path = r'C:\Users\afham\Documents\MetaGuide\test1.mg'
    os.startfile(scope_setup_path)
    time.sleep(3)


    # measure and modify the two parameters below for your magnification %
    # distance in mm
    distance_lens_lightsource = 118
    distance_lens_ccd = 83
    magnification = distance_lens_ccd / distance_lens_lightsource

    #pixel size (micrometer) can be found on camera specifications sheet
    # for asi290mini pixel size is 2.9 microns, effective pixel size is ~ 4microns/pixel
    camera_pixel_size = 2.9
    effective_pixel_size = camera_pixel_size / magnification

    # set scale factor for picomotor motion from camera feedback
    motion_scale = 1
    correction_scale = effective_pixel_size * motion_scale

    # if you want to see monitoring graphs, not necessary for code, just optional
    # monitor_path = r'C:\Program Files (x86)\MetaGuide\MetaMonitor.exe'
    # os.startfile(monitor_path)
    # time.sleep(5)

    # Start the listener and monitor threads

    listener = MyListener()
    listener.start()
    # Wait for the listener to receive the first message
    while not listener.isAlive():
        if listener.isAlive():
            print('Listener Live!')
            # Print the initial x and y coordinates
            # x, y, intens = listener.getXYI()
            # print(f"Initial coordinates: x={x}, y={y}, intensity={intens}")
        time.sleep(0.1)


    # Monitor stuff
    # in MetaGuide, open setup button (bottom bar)-> extra tab -> make sure Broadcast is checked
    # look at extra settings for port or ip settings, otherwise monitor may not work
    # you need to take your current connected router's ipv4 address and its subnet mask to calculate the broadcast mask
    # for the current router in Lab the broadcast is 10.206.255.255, it varies per router per device

    # you can use windows test loopback adapter for local network and bypasses need for router, use cmd ipconfig/all
    # to find ipv4 and subnet mask for the test loopback adapter once you've installed it from device manager.

    monitor = MGMonitor(listener)
    monitor.start()
    while not monitor.is_alive():
        if monitor.is_alive():
            print('Monitor Live!')
            # monitor.dumpState()
        time.sleep(0.1)

    x_init, y_init = listener.x_init, listener.y_init


    # Shut down MetaGuide using PIDs and signal
    def kill_processes(pids, sig=signal.SIGTERM):
        """
        Kill multiple processes given their PIDs using a signal (default: SIGTERM).
        """
        def get_program_name(pid):
            try:
                process = psutil.Process(pid)
                return process.name()
            except psutil.NoSuchProcess:
                print(f"No process found with PID {pid}.")
                return None

        for pid in pids:
            try:
                os.kill(pid, sig)
                print(f"Process with PID {pid} terminated: "+get_program_name(pid))
            except OSError as e:
                print(f"Error terminating process "+get_program_name(pid)+"with PID {pid}: {e} ")

    def get_pid(process_name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                return proc.info['pid']
        return None

    mgpid = get_pid('MetaGuide.exe')
    ascompid = get_pid('ASCOM.TelescopeSimulator.exe')

    input("Enter to close: ")
    pids_to_kill = [mgpid, ascompid]
    kill_processes(pids_to_kill)

    print("Now stopping threads")

    # need to end threads to end program!
    def end_threads():
        # Stop listener
        if listener.is_alive():
            listener.stop()
            listener.join()
        # Stop monitor
        if monitor.is_alive():
            monitor.join()

    end_threads()
    print("Done!")


# If you're using run_as_admin
"""if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        run_as_admin()
    else:
        main()"""

if __name__ == "__main__":
    main()

