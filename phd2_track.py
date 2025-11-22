import requests
import time

# Define the PHD2 server address
PHD2_SERVER = 'http://localhost:4400'


# Helper function to send commands to PHD2
def send_phd2_command(method, params=None):
    payload = {
        'method': method,
        'id': 1,
        'jsonrpc': '2.0'
    }
    if params:
        payload['params'] = params

    response = requests.post(PHD2_SERVER, json=payload)
    return response.json()


# Connect to the camera
def connect_camera(camera_name):
    result = send_phd2_command('set_connected', params=['camera', True])
    if 'error' in result:
        raise Exception(f"Failed to connect to the camera: {result['error']}")
    print(f"Connected to the camera: {camera_name}")


# Set the exposure time
def set_exposure(exposure_time):
    result = send_phd2_command('set_exposure', params=[exposure_time])
    if 'error' in result:
        raise Exception(f"Failed to set exposure time: {result['error']}")
    print(f"Exposure time set to {exposure_time} seconds")


# Start looping exposures
def start_looping():
    result = send_phd2_command('loop')
    if 'error' in result:
        raise Exception(f"Failed to start looping: {result['error']}")
    print("Started looping exposures")


# Auto-select a star
def auto_select_star():
    result = send_phd2_command('find_star')
    if 'error' in result:
        raise Exception(f"Failed to auto-select star: {result['error']}")
    print("Auto-selected a star")


# Start guiding
def start_guiding():
    result = send_phd2_command('guide')
    if 'error' in result:
        raise Exception(f"Failed to start guiding: {result['error']}")
    print("Started guiding")


# Monitor guiding and restart if RA calibration fails
def monitor_guiding():
    while True:
        result = send_phd2_command('get_status')
        state = result['result']['state']

        if state == 'Stopped' and 'RA Calibration Failed' in result['result']['status']:
            print("RA calibration failed. Restarting guiding...")
            start_guiding()

        time.sleep(5)  # Adjust the delay as needed


def main():
    camera_name = "ZWO ASI290MM Mini"  # Replace with your camera name
    exposure_time = 0.1

    try:
        connect_camera(camera_name)
        set_exposure(exposure_time)
        start_looping()
        auto_select_star()
        start_guiding()
        monitor_guiding()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
