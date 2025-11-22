import cv2
import numpy as np
import asicamera
import time
import ctypes

def get_camera_property(camera_index):
    camera_info = asicamera.ASI_CAMERA_INFO()
    result = asicamera.ASIGetCameraProperty(camera_info, camera_index)
    if result != asicamera.ASI_SUCCESS:
        raise Exception(f"Failed to get camera property: {result}")
    return camera_info

def open_camera(camera_id):
    result = asicamera.ASIOpenCamera(camera_id)
    if result != asicamera.ASI_SUCCESS:
        raise Exception(f"Failed to open camera: {result}")

def init_camera(camera_id):
    result = asicamera.ASIInitCamera(camera_id)
    if result != asicamera.ASI_SUCCESS:
        raise Exception(f"Failed to initialize camera: {result}")

def close_camera(camera_id):
    result = asicamera.ASICloseCamera(camera_id)
    if result != asicamera.ASI_SUCCESS:
        raise Exception(f"Failed to close camera: {result}")

def capture_frame(camera_id, width, height):
    img_type = asicamera.ASI_IMG_RAW8
    asicamera.ASISetROIFormat(camera_id, width, height, 1, img_type)
    asicamera.ASIStartVideoCapture(camera_id)
    buffer = np.zeros((height, width), dtype=np.uint8)
    buffer_ptr = buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    result = asicamera.ASIGetVideoData(camera_id, buffer_ptr, buffer.size, 2000)
    asicamera.ASIStopVideoCapture(camera_id)
    if result != asicamera.ASI_SUCCESS:
        raise Exception(f"Failed to capture image: {result}")
    return buffer

def find_brightest_object(image):
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
    return max_loc

def main():
    camera_index = 0
    camera_id = None

    try:
        # Attempt to get the camera property for the first camera
        camera_info = get_camera_property(camera_index)
        camera_id = camera_info.CameraID
        print(f"Camera Name: {camera_info.Name.decode('utf-8')}")

        open_camera(camera_id)
        init_camera(camera_id)

        width = camera_info.MaxWidth
        height = camera_info.MaxHeight

        # Set exposure and gain for better image
        asicamera.ASISetControlValue(camera_id, asicamera.ASI_EXPOSURE, 25000, asicamera.ASI_FALSE)  # Set exposure to 25ms
        asicamera.ASISetControlValue(camera_id, asicamera.ASI_GAIN, 100, asicamera.ASI_FALSE)  # Set gain to 100

        while True:
            frame = capture_frame(camera_id, width, height)
            object_position = find_brightest_object(frame)

            # Draw a circle around the detected object
            cv2.circle(frame, object_position, 10, (255, 0, 0), 2)

            # Display the frame with the detected object
            cv2.imshow("Frame", frame)

            # Print the object position
            print(f"Object Position: {object_position}")

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)  # Adjust the delay as needed

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if camera_id is not None:
            close_camera(camera_id)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
