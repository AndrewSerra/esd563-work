import time
import json
import numpy as np
import cv2
import apriltag
from enum import Enum
from smbus2 import SMBus
from frameGrabber import ImageFeedthrough

ADDRESS     = 0x19
TAG_SIZE    = 0.1
OUTPUT_FILE = "./april_tag.json"

class AccelThresholds(Enum):
    X = 5.0
    Y = 5.0
    Z = 10.0

class CameraConstants(Enum):
    b              = 59.6192    # Baseline[mm]
    f              = 6.0969     # Focal length[mm] 1016.35/166.7
    ps             = .006       # Pixel size[mm]
    center_x_left  = 345.1903   # Left camera x center[px]
    center_y_left  = 228.0758   # Left camera y center[py]
    center_x_right = 379.8481   # Right camera x center[px]
    center_y_right = 283.3057   # Right camera y center[py]

# Convert reading to pos value
def convert_to_value(in_value_1, in_value_2):
    data = None
    if in_value_2 > 127:
        data = -1 * (65536 - (in_value_2 << 8) + in_value_1)
    else:
        data = (in_value_2 << 8) + in_value_1

    return round(data / 557.2, 2)

# Read a register value
def read(bus, reg):
    return bus.read_byte_date(ADDRESS, reg)

# Write a value to a register 
def write(bus, reg, value):
    bus.write_byte_data(ADDRESS, reg, value)
    return

def get_accel(bus, reg):
    data = bus.read_i2c_block_data(ADDRESS, reg, 6)

    x = convert_to_value(data[0], data[1])
    y = convert_to_value(data[2], data[3])
    z = convert_to_value(data[4], data[5])

    print(f"x: {x} y: {y} z: {z}")
    return (x, y, z)

def get_pos_obj(x, y, z):
    return dict({
        "x": x,
        "y": y,
        "z": z,
    })

# Rerun apriltag command to update rel position
def run_pos_update():
    feed_processing = ImageFeedthrough()
    detector = apriltag.Detector()

    left_gray_img, right_gray_img = feed_processing.getStereoGray()

    # Left camera matrix
    mtx_left = np.array([[1018.4, 0,      345.2],
                         [0,      1017.3, 228.1],
                         [0,      0,      1]])
    # Distortion coeffs - left
    dist_left = np.array([-0.3795, 0.1234, 0, 0])

    # Right camera matrix
    mtx_right = np.array([[1015.8, 0,        379.8],
                          [0,      1013.9,   283.3],
                          [0,      0,        1]])
    
    # Distortion coeffs - right
    dist_right = np.array([-0.3743, 0.0701, 0, 0])

    left_undistort_img = cv2.undistort(left_gray_img, mtx_left, dist_left)
    right_undistort_img = cv2.undistort(right_gray_img, mtx_right, dist_right)

    detection_left = detector.detect(left_undistort_img)
    detection_right = detector.detect(right_undistort_img)

    if len(detection_left) and len(detection_right):
         # fx,fy,cx,cy from the left calibration matrix
        pose = detector.detection_pose(detection_left[0], (984.7575, 983.0474, 310.7146, 261.7735), TAG_SIZE, 1)
        
        x1 = float(detection_left[0].corners[0][0])
        y1 = float(detection_left[0].corners[0][1])

        x2 = float(detection_right[0].corners[0][0])
        y2 = float(detection_right[0].corners[0][1])

        Z = (CameraConstants.b.value * CameraConstants.f.value) / \
            (abs((x1 - CameraConstants.center_x_left.value) -( x2 - CameraConstants.center_x_right.value)) * CameraConstants.ps.value)
                
        X = (Z * (x1 - CameraConstants.center_x_left.value) * CameraConstants.ps.value) / CameraConstants.f.value
        
        Y = (Z * (y1 - CameraConstants.center_y_left.value) * CameraConstants.ps.value) / CameraConstants.f.value
    
        # convert to m
        X = X / 1000.0
        Y = Y / 1000.0
        Z = Z / 1000.0

        camera_position = np.array([X, Y, Z, 1]).T
        position = np.dot(np.linalg.inv(pose[0]), camera_position)
    
        # convert to centimeters
        position_cm = position[0:3] * 100

        rotation_mat = pose[0][0:3,0:3]                # slice out the 3x3 rotation matrix from the 4x4 matrix
        rotation_vec, _ = cv2.Rodrigues(rotation_mat)  # convert 3x3 rotation matrix to rotation vector
        translation_vec = pose[0][0:3,3]               # slice out the 3x1 translation vector

        bottom_tag_points =  np.array([[-.29 , -.39,  0],  #closet to you bottom left, left side width
                                       [ .15 , -.389, 0],  # back left(up or down), back left (r to l)
                                       [ .13 ,  .27,  0],  #back right(up or down), back right(r to l)
                                       [-.29,   .29,  0]]) #closet to you bottom right, right side width

        cam_px_pts_bottom = cv2.projectPoints(bottom_tag_points, rotation_vec, translation_vec, mtx_left, None)

        top_tag_points = np.array([[-.29 , -.39 , -.1],
                                   [ .15 , -.389 , -.1],
                                   [ .13,   .27 ,  -.1],
                                   [-.29,   .29,   -.1]])
        
        cam_px_pts_top = cv2.projectPoints(top_tag_points, rotation_vec, translation_vec, mtx_left, None)

        with open(OUTPUT_FILE, "+a") as f:
            json.dump(dict(), f)
    else:
       print("No detection.")

if __name__ == "__main__":

    run_pos_update()
    # bus = SMBus(1)

    # prev_state = None

    # # Setup i2c settings
    # write(bus, 0x7c, 0) # Address 0x7c
    # write(bus, 0x7d, 4) # Address 0x7d

    # while True:
    #     # Read from device - 0x12 is starting address of
    #     # the x, y, z acceleration values
    #     x, y, z = get_accel(bus, 0x12)

    #     if prev_state is None:
    #         # assign continue
    #         prev_state = get_pos_obj(x, y, z)
    #     else:
    #         # Compare and react, reassign
    #         pass

    #     time.sleep(1)
