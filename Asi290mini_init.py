import asicamera
import numpy as np

def get_num_cameras():
    return asicamera.ASIGetNumOfConnectedCameras()

def get_camera_property(camera_id):
    camera_info = asicamera.ASI_CAMERA_INFO()
    result = asicamera.ASIGetCameraProperty(camera_info, camera_id)
    if result != asicamera.ASI_SUCCESS:
        raise Exception("Error getting camera property")
    return camera_info

if __name__ == "__main__":
    num_cameras = get_num_cameras()
    print(f"Number of connected cameras: {num_cameras}")
    if num_cameras > 0:
        camera_info = get_camera_property(0)
        print(f"Camera Name: {camera_info.Name}")
