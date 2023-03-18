import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from depth_helpers import get_depth, get_position

def get_image_paths():
    current_path = Path(__file__).parent
    img_path = Path(f"{current_path}/img")
    left_images = sorted(img_path.glob("left*"))
    right_images = sorted(img_path.glob("right*"))
    return list(zip(left_images, right_images))

def get_output_path():
    current_path = Path(__file__).parent
    out_path = Path(f"{current_path}/output/{datetime.now().isoformat()}")
    # create directory if it does not exist
    out_path.mkdir(parents=True, exist_ok=True)
    return out_path

# imgset - tuple with two items that are images
def to_grayscale(imgset):
    left_img_gray = cv2.cvtColor(imgset[0], cv2.COLOR_RGB2GRAY)
    right_img_gray = cv2.cvtColor(imgset[1], cv2.COLOR_RGB2GRAY)

    return (left_img_gray, right_img_gray)

def get_coords(circle_set, img):
    if circle_set is not None:
        circles = np.round(circle_set[0, :]).astype("int")
        center_x = np.mean(circles[:, 0])
        center_y = np.mean(circles[:, 1])
        for (x, y, r) in circles:
            cv2.circle(img, (x, y), r, (0, 255, 0), 2)
            cv2.circle(img, (x, y), 2, (0, 0, 255), 4)
        return ((center_x, center_y), img)
    else:
        return (None, img)

if __name__ == "__main__":
    
    img_list = get_image_paths()

    for i, img_paths in enumerate(img_list):
        print(f"Working on image set {str(i+1)}. Identifier: {img_paths[0].name} and {img_paths[1].name}")
        left_img = cv2.imread(str(img_paths[0]))
        right_img = cv2.imread(str(img_paths[1]))

        grayscale_imgs = to_grayscale((left_img, right_img))
        # filtered_gray = [cv2.Canny(img, 100, 200) for img in grayscale_imgs]
        hough_circles = [cv2.HoughCircles(edge, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=200, param2=30, minRadius=50, maxRadius=190) for edge in grayscale_imgs]

        [hc_left, hc_right] = hough_circles

        [left_coords, left_img] = get_coords(hc_left, left_img)
        [right_coords, right_img] = get_coords(hc_right, right_img)

        if left_coords is None or right_coords is None:
            print("Cannot find circles.")
            continue

        [left_x, left_y], [right_x, right_y] = left_coords, right_coords
        print(f"Found coordinates for -> left image: {(left_x, left_y)}, right image: {(right_x, right_y)}")

        depth = get_depth(left_x, right_x)
        (x, y, z) = get_position(left_x, left_y, depth)

        print(f"X coordinate: {x}")
        print(f"Y coordinate: {y}")
        print(f"Z coordinate: {z}")

        cv2.imshow('left', left_img)
        cv2.imshow('right', right_img)
        cv2.waitKey(0)
