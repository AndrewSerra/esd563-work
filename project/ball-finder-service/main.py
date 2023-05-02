import cv2
import time
import mmap
import json
import struct
import zmq
import numpy as np
from frameGrabber import ImageProcessing
from enum import Enum
from pathlib import Path

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
    min_dist       = 200
    param_1        = 30
    param_2        = 10
    min_radius     = 1
    max_radius     = 40

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

    if circles is not None:
        circles_int = np.round(circles[0, :]).astype("int")
        center_x = np.mean(circles_int[:, 0])
        center_y = np.mean(circles_int[:, 1])

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

    if circles is not None:
        circles_int = np.round(circles[0, :]).astype("int")
        center_x = np.mean(circles_int[:, 0])
        center_y = np.mean(circles_int[:, 1])

        return dict({"x": center_x, "y": center_y})
    return None

if __name__ == "__main__":
    curr_path = Path(__file__).parent.resolve()

    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.PUB)
    zmq_socket.bind("tcp://*:5555")

    camera_processor = ImageProcessing()

    world_positions = None

    with open("/etc/esd-bounce/april_tag.json", "r") as f:
        world_positions = json.load(f)
        # print(world_positions)

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

    # you only need 4 points in the rectangle in order to fully understand the bounds
    min_x = world_positions['world_pos']['top_top_left'][0]
    max_x = world_positions['world_pos']['top_bottom_right'][0]

    min_y = world_positions['world_pos']['top_top_left'][1]
    max_y = world_positions['world_pos']['top_bottom_right'][1]

    min_z = world_positions['world_pos']['bottom_bottom_right'][2]
    max_z = world_positions['world_pos']['top_bottom_right'][2]

    while True:
        img_cam_left, img_cam_right = camera_processor.getStereoRGB()

        img_left   = np.ascontiguousarray(img_cam_left[:,:,0:3], dtype=np.uint8)   # must make it contiguous for opencv processing to work
        img_right  = np.ascontiguousarray(img_cam_right[:,:,0:3], dtype=np.uint8)   # must make it contiguous for opencv processing to work
        
        cv2.imwrite(f"{curr_path}/left.jpg", img_left)
        cv2.imwrite(f"{curr_path}/right.jpg", img_right)

        gray_img_left = cv2.imread(f"{curr_path}/left.jpg", 0) # grayscale load
        gray_img_right = cv2.imread(f"{curr_path}/right.jpg", 0) # grayscale load

        left_circle = get_circles_left(gray_img_left)
        right_circle = get_circles_right(gray_img_right)

        if left_circle and right_circle:
            left_x_mm = left_circle.get("x") * 10
            right_x_mm = right_circle.get("x") * 10
            left_y_mm = left_circle.get("y") * 10

            Z = (CameraConstants.b.value * CameraConstants.f.value) / \
                        (abs((left_x_mm - CameraConstants.center_x_left.value) - (right_x_mm - CameraConstants.center_x_right.value)) * CameraConstants.ps.value)
                    
            X = (Z * (left_x_mm - CameraConstants.center_x_left.value) * CameraConstants.ps.value) / CameraConstants.f.value
                
            Y = (Z * (left_y_mm - CameraConstants.center_y_left.value) * CameraConstants.ps.value) / CameraConstants.f.value
            
            # convert to m
            X = X / 1000.0
            Y = Y / 1000.0
            Z = Z / 1000.0
            
            print(X, Y, Z)

            inside_bounds_x = (X >= min_x) and (X <= max_x)
            print(f'Inside X: {inside_bounds_x}')
            inside_bounds_y = (Y >= min_y) and (Y <= max_y)
            print(f'Inside Y: {inside_bounds_y}')
            inside_bounds_z = (Z >= (min_z - 0.5)) and (Z <= -(max_z + 0.5))
            print(f'Inside Z: {inside_bounds_z}')

            print(f'Min X: {min_x} Max X: {max_x}')
            print(f'Min Y: {min_y} Max Y: {max_y}')

            zmq_socket.send_string(json.dumps(dict({
                "position": (X, Y, Z),
                "in_field": 1 if (inside_bounds_x and inside_bounds_y) else 0,
            })))

        time.sleep(0.5)


