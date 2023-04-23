import cv2
import threading
import time
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
    min_dist       = 200
    param_1        = 30
    param_2        = 10
    min_radius     = 1
    max_radius     = 400

def get_circles(image, camera_side = None, results = None):

    if image is None:
        return

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
        if results is not None and camera_side is not None:
            results[camera_side] = circles

    return

if __name__ == "__main__":
    camera_processor = ImageProcessing()

    while True:
        results = dict()

        img_cam_left, img_cam_right = camera_processor.getStereoGray()

        left_processing = threading.Thread(target=get_circles, args=(img_cam_left, "left", results,))
        right_processing = threading.Thread(target=get_circles, args=(img_cam_right, "right", results,))
        
        threads = [left_processing, right_processing]

        start_t = time.time()

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        elapsed_t = time.time() - start_t

        if ("left" in results) and ("right" in results):
            continue

        print(f"Successfully completed in {elapsed_t}s")
        print(f"Results {results}")
        time.sleep(2)


