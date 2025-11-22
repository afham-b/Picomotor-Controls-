import subprocess
import time


#import devcon_win


# hwid of port picomotors is currently in USB\VID_104D&PID_4000&REV_0100
#USB\VID_104D&PID_4000\12345678

# remove	Remove devices.	pnputil /remove-device
# rescan	Scan for new hardware.	pnputil /scan-devices
# resources	List hardware resources for devices.	pnputil /enum-devices /resources
# restart	Restart devices.	pnputil /restart-device
# stack	List expected driver stack for devices.	pnputil /enum-devices /stack
# status	List running status of devices.	pnputil /enum-devices


#pnputil /remove-device "USB\VID_104D&PID_4000\12345678"
#pnputil /restart-device "USB\VID_104D&PID_4000\12345678"
#print(devcon_win.Picomotor_Controller('status'))

def restart_usb_by_instance_id(instance_id):
    try:
        # Execute the devcon command to remove the device
        command = f'pnputil /restart-device "{instance_id}"'
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Output: {result.stdout}")
        print(f"USB device with instance ID {instance_id} restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to eject device: {e.stderr}")

# Replace with the actual instance ID found earlier
#instance_id = 'USB\\VID_XXXX&PID_XXXX\\PORT_#0002.HUB_#0002'
instance_id = 'USB\\VID_104D&PID_4000\\12345678'

restart_usb_by_instance_id(instance_id)