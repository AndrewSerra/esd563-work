import cv2
import threading
import time
import numpy as np
from frameGrabber import ImageProcessing
from enum import Enum

class CameraConstants(Enum):
    b              = 59.6192    # Baseline[mm]
    f              = 6.0969     # Focal length[mm] 1016.35/166.7
    ps             = .006       # Pixel size[mm]
    center_x_left  = 345.1903   # Left camera x center[px]
    center_y_left  = 228.0758   # Left camera y center[py]
    center_x_right = 379.8481   # Right camera x center[px]
    center_y_right = 283.3057   # Right camera y center[py]

class ProcessingParameters(Enum):
    dp             = 1
    min_dist       = 50
    param_1        = 200
    param_2        = 30
    min_radius     = 5
    max_radius     = 40

results = dict()

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
        if len(circles_int) != 1:
            print("Too many damn circles: " + len(circles_int))
            return

        global results
        results["right"] = dict({"x": center_x, "y": center_y})
        print(results)
    return

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
        if len(circles_int) != 1:
            print("Too many damn circles: " + len(circles_int))
            return

        global results
        results["left"] = dict({"x": circles_int[0], "y": circles_int[1]})
        print(results)
    return

if __name__ == "__main__":
    camera_processor = ImageProcessing()

    while True:
        results = dict()

        img_cam_left, img_cam_right = camera_processor.getStereoGray()

        get_circles_left(img_cam_left)
        get_circles_right(img_cam_right)

        if ("left" not in results) or ("right" not in results):
            continue

        left_circle = results.get("left")
        right_circle = results.get("right")

        if left_circle and right_circle:
            Z = (CameraConstants.b.value * CameraConstants.f.value) / \
                        (abs((left_circle.get("x") - CameraConstants.center_x_left.value) - ( right_circle.get("x") - CameraConstants.center_x_right.value)) * CameraConstants.ps.value)
                    
            X = (Z * (left_circle.get("x") - CameraConstants.center_x_left.value) * CameraConstants.ps.value) / CameraConstants.f.value
                
            Y = (Z * (left_circle.get("y") - CameraConstants.center_y_left.value) * CameraConstants.ps.value) / CameraConstants.f.value

        print(f"Results {results}")
        
        time.sleep(0.5)


