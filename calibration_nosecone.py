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
import asyncio
import pyuac
import ctypes

# to clean ports
from PortCleanUp import SocketCleaner

# MGListener.py must be in the same directory as mg_track.py
# By default, MGListener.py is located in program files x86 \ MetaGuide folder
from MGListener import MyListener, MGListener, MGMonitor

# PicomotorStandAlone.py must be in the same directory as this file
import PicomotorStandAlone
from pylablib.devices import Newport

# Check the command-line arguments to set the filename
if len(sys.argv) != 2:
    print("Usage: python calibration.py [nosecone|microlens]")
    sys.exit(1)

if sys.argv[1].lower() == 'nosecone':
    filename = 'calibration_data_nosecone.txt'
elif sys.argv[1].lower() == 'microlens':
    filename = 'calibration_data.txt'
else:
    print("Invalid argument. Use 'nosecone' or 'microlens'.")
    sys.exit(1)

# If popups appear: run CMD as admin OR use run_as_admin() OR use run_as_admin.bat
"""def run_as_admin(): # see below for main()
    if sys.platform == 'win32':
        try:
            # Elevate script's privileges using ShellExecuteW
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        except Exception as e:
            print(f"Failed to run as administrator: {e}")
            """

# Parameters: measure and modify for your magnification (distance in mm):
#distance_lens_lightsource = 118
#distance_lens_ccd = 83
#magnification = distance_lens_ccd / distance_lens_lightsource

#pixel size (micrometers) can be found on camera specs sheet
# for asi290mini pixel size is 2.9 microns, effective pixel size is ~ 4microns/pixel
#camera_pixel_size = 2.9
#effective_pixel_size = camera_pixel_size / magnification

# set scale factor for picomotor motion from camera feedback
#motion_scale = 0.01
#correction_scale = effective_pixel_size * motion_scale


def handle_client_connection(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print("Received data:", data.decode())
    client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9999))
    server.listen(5)
    print("Server started on port 9999")

    while True:
        client_sock, address = server.accept()
        print('Accepted connection from {}:{}'.format(address[0], address[1]))
        client_handler = threading.Thread(
            target=handle_client_connection,
            args=(client_sock,)
        )
        client_handler.start()

# Shut down MetaGuide and ASCOM using PIDs and signal
def kill_processes(pids, sig=signal.SIGTERM):
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
            print(f"Error {e} terminating process {pid}: "+get_program_name(pid))
    print("Processes killed")


def get_pid(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None


# Need to end threads to end program!
def end_threads():
    print("Stopping threads:")
    if listener.is_alive():
        listener.stop()
        listener.join()
        print("Listener stopped")
    else:
        print("Listener is not running")
    if monitor.is_alive():
        monitor.join()
        print("Monitor stopped")
    else:
        print("Monitor is not running")


def ending():
    # stop the motor
    motor_y.controller.stop(axis='all', immediate=True)

    # kill processes via PIDs
    mgpid = get_pid('MetaGuide.exe')
    apid = get_pid('ASCOM.TelescopeSimulator.exe')
    pids_to_kill = [mgpid, apid]
    kill_processes(pids_to_kill)

    # clean ports
    cleaner = SocketCleaner()
    cleaner.cleanup()

    # end Listener, Monitor threads
    end_threads()
    print("Done!")

    sys.exit(0)


async def main():
    global listener, monitor

    # Start picomotor controller 8742 communication
    n = Newport.get_usb_devices_number_picomotor()
    if n == 0:
        print("No Picomotor devices found.")
        return
    if n > 0:
        print('Controller found')
    try:
        controller = Newport.Picomotor8742()
        print(controller)
        global motor_y
        motor_y = PicomotorStandAlone.MotorOperations(controller, motor=1)
        # test to see if motors move:
        # motor_x = PicomotorStandAlone.MotorOperations(controller, motor=2)
        # motor_y.move_by_steps(1000, stop_event=None)
        # motor_x.move_by_steps(1000, stop_event=None)
    except Exception as e:
        print(f"Error connecting to the Picomotor controller: {e}")
        return

    # Options for starting MetaGuide:
    # can start via the plain.exe or win32api. plain.exe location shown below
    # app = Application().start(r"C:\Program Files (x86)\MetaGuide\MetaGuide.exe")
    # time.sleep(10)  # Wait for MetaGuide to open

    # We start with a saved MetaGuide setup file: test1.mg
    # remember to change to your own path!
    scope_setup_path = r'C:\Users\afham\Documents\MetaGuide\test1.mg'
    #scope_setup_path = r'C:\Users\linz\Documents\GitHub\Picomotor-Controls-1\test1.mg'
    os.startfile(scope_setup_path)
    time.sleep(3)

    # To see monitoring graphs:
    # monitor_path = r'C:\Program Files (x86)\MetaGuide\MetaMonitor.exe'
    # os.startfile(monitor_path)
    # time.sleep(5)

    # Start Listener and Monitor threads
    listener = MyListener()
    listener.start()
    # Wait for Listener to receive the first message
    while not listener.isAlive():
        if listener.isAlive():
            print('Listener Live!')
            # Print initial x and y coordinates
            # x, y, intens = listener.getXYI()
            # print(f"Initial coordinates: x={x}, y={y}, intensity={intens}")
            time.sleep(0.1)

    # Monitor:
    # in MetaGuide, setup button -> extra -> make sure Broadcast is checked
    # look at extra settings for port or IP settings
    # find your current connected router's ipv4 address and its subnet mask to calculate the broadcast mask
    # for the current router in Lab the broadcast is 10.206.255.255, it varies per router per device

    # Use windows test loopback adapter for local network to bypass need for router. Use CMD ipconfig/all
    # to find ipv4 and subnet mask for the test loopback adapter once you've installed it from Device Manager.
    # for example, the default test loopback for your Windows device may be 169.254.255.255

    monitor = MGMonitor(listener)
    monitor.start()
    while not monitor.is_alive():
        if monitor.is_alive():
            print('Monitor Live!')
        time.sleep(0.1)

    async def control_picomotors(delt_x, delt_y):
        # These deltas are in pixels
        print('Server output,' + str(delt_x) + ',' + str(delt_y))

    async def receive_data():
        # Set up UDP socket to listen
        XY_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('127.0.0.1', 5001)  # Use the same address and port as MGListener
        XY_sock.bind(server_address)

        # attempting to make second socket to send duplicate delta_x and delta_y values
        # Pico_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # server_address = ('127.0.0.1', 5002)

        while True:
            data, _ = XY_sock.recvfrom(4096)  # Buffer size
            delt_x, delt_y, x_init, y_init = map(float, data.decode().split(','))

            # Process received data to control picomotors
            #asyncio.create_task(control_picomotors(delt_x, delt_y))
            await asyncio.sleep(0.01)

    #asyncio.run(motor_y.start_sock_data())
    #asyncio.run(receive_data())

    # file name of the calibration data
    # filename = 'calibration_data_.txt'

    async def starting():
        await asyncio.gather(
            motor_y.calibration_process(filename),
            # receive_data()
        )

    await starting()

    #end the programs
    ending()


# If using run_as_admin:
"""if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        run_as_admin()
    else:
        main()"""

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Ending:")
        ending()