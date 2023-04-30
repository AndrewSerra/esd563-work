import cv2
import time
import mmap
import json
import struct
import numpy as np
from frameGrabber import ImageProcessing, ImageFeedthrough
from enum import Enum

class CameraConstants(Enum):
    b              = 59.6192    # Baseline[mm]
    f              = 6.0969     # Focal length[mm] 1016.35/166.7
    ps             = .006       # Pixel size[mm]
    center_x_left  = 345.1903   # Left camera x center[px]
    center_y_left  = 228.0758   # Left camera y center[py]
    center_x_right = 379.8481   # Right camera x center[px]
    center_y_right = 283.3057   # Right camera y center[py]
    grad_thresh    = 240

class ProcessingParameters(Enum):
    dp             = 1
    min_dist       = 50
    param_1        = 200
    param_2        = 50
    min_radius     = 1
    max_radius     = 100

def get_circles_right(image):
    circles = cv2.HoughCircles(
        image, 
        cv2.HOUGH_GRADIENT, 
        ProcessingParameters.dp.value,
        ProcessingParameters.min_dist.value,
        param1=ProcessingParameters.param_1.value,
        param2=ProcessingParameters.param_2.value,
        minRadius=ProcessingParameters.min_radius.value,
        maxRadius=ProcessingParameters.max_radius.value)
    print("left, im: ", circles)
    if circles is not None:
        circles_int = np.round(circles[0, :]).astype("int")
        center_x = np.mean(circles_int[:, 0])
        center_y = np.mean(circles_int[:, 1])
        if len(circles_int) != 1:
            print("Too many damn circles: " + len(circles_int))

        return dict({"x": center_x, "y": center_y})
    return None

def get_circles_left(image):
    circles = cv2.HoughCircles(
        image, 
        cv2.HOUGH_GRADIENT, 
        ProcessingParameters.dp.value,
        ProcessingParameters.min_dist.value,
        param1=ProcessingParameters.param_1.value,
        param2=ProcessingParameters.param_2.value,
        minRadius=ProcessingParameters.min_radius.value,
        maxRadius=ProcessingParameters.max_radius.value)
    print("left, im: ", circles)
    if circles is not None:
        circles_int = np.round(circles[0, :]).astype("int")
        center_x = np.mean(circles_int[:, 0])
        center_y = np.mean(circles_int[:, 1])
        if len(circles_int) != 1:
            print("Too many damn circles: " + len(circles_int))

        return dict({"x": center_x, "y": center_y})
    return None

if __name__ == "__main__":
    camera_processor = ImageFeedthrough()

    world_positions = json.load("/etc/esd-bounce/april_tag.json")
    print(world_positions)

    with open("/dev/mem", "r+b") as f:
        simulink_mem = mmap.mmap(f.fileno(), 1000, offset=0x81200000)
        simulink_mem.seek(0) 
        simulink_mem.write(struct.pack('l', 1))        # reset IP core
        simulink_mem.seek(8)                         
        simulink_mem.write(struct.pack('l', 752))      # image width
        simulink_mem.seek(12)                        
        simulink_mem.write(struct.pack('l', 480))      # image height
        simulink_mem.seek(16)                        
        simulink_mem.write(struct.pack('l', 32))       # 32 horizontal porch
        simulink_mem.seek(20)                        
        simulink_mem.write(struct.pack('l', 32))       # 32 vertical porch
        simulink_mem.seek(256) 
        simulink_mem.write(struct.pack('l', CameraConstants.grad_thresh.value))   # 245 GradThresh (0-255)
        simulink_mem.write(struct.pack('l', 1))        # enable IP core
            

    while True:
        img_cam_left, img_cam_right = camera_processor.getStereoGray()
        print(img_cam_left, img_cam_right)
        left_circle = get_circles_left(img_cam_left)
        right_circle = get_circles_right(img_cam_right)

        if left_circle and right_circle:
            print(left_circle, right_circle)
            Z = (CameraConstants.b.value * CameraConstants.f.value) / \
                        (abs((left_circle.get("x") - CameraConstants.center_x_left.value) - ( right_circle.get("x") - CameraConstants.center_x_right.value)) * CameraConstants.ps.value)
                    
            X = (Z * (left_circle.get("x") - CameraConstants.center_x_left.value) * CameraConstants.ps.value) / CameraConstants.f.value
                
            Y = (Z * (left_circle.get("y") - CameraConstants.center_y_left.value) * CameraConstants.ps.value) / CameraConstants.f.value
            print(X, Y, Z)
        time.sleep(0.5)


