import json
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
import cv2 as cv
from tqdm import tqdm
import calibrate_camera

NUM_CLUSTERS = 4
DATA_PATH = "image_data/quads.json"
RAW_DIR = "images/raw_jpeg"
UNDISTORTED_DIR = "images/undistorted"
WARPED_DIR = "images/warped"

WARP_IMG_WIDTH, WARP_IMG_HEIGHT = 2107, 2821

# Given an image array, return it undistorted
def undistort_image(img:np.uint8) -> cv.Mat:
    h,  w = img.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    return cv.undistort(img, mtx, dist, None, newcameramtx)

# Undistort images and write them to folder
def save_undistorteds(input_dir:str, output_dir:str) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for img_name in tqdm([img.name for img in Path(input_dir).glob("*.jpeg")]):
        img = cv.imread(Path(input_dir) / img_name)
        cv.imwrite(Path(output_dir) / img_name, undistort_image(img))

# Take in an image an the goal shape, do the perspective transformation and return the new image
def do_perspective_warp(img:cv.Mat, desk_corners:list, goal_corners:list) -> cv.Mat:
    t = cv.getPerspectiveTransform(desk_corners, goal_corners)
    return cv.warpPerspective(img, t, (WARP_IMG_WIDTH, WARP_IMG_HEIGHT))

# Save warped images
def save_warpeds(input_dir:str, output_dir:str) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for img_name in tqdm([img.name for img in Path(input_dir).glob("*.jpeg")]):
        img = cv.imread(Path(input_dir) / img_name)
        desk_corners = np.array(point_data[img_name], dtype = np.float32)
        img_warp = do_perspective_warp(img, desk_corners, goal_corners)
        cv.imwrite(Path(output_dir) / img_name, img_warp)

if __name__ == "__main__":
    with Path.open(DATA_PATH, "r") as f:
        point_data = json.load(f)
    all_points = []
    for points in point_data.values():
        all_points.extend(points)
    points_array = np.array(all_points)

    mtx, dist = calibrate_camera.calibrate(calibrate_camera.CALIBRATION_DIR)
    save_undistorteds(RAW_DIR, UNDISTORTED_DIR)

    goal_corners = np.array([[0, WARP_IMG_HEIGHT],
                             [WARP_IMG_WIDTH, WARP_IMG_HEIGHT],
                             [0, 0],
                             [WARP_IMG_WIDTH, 0]], dtype = np.float32)

    save_warpeds(UNDISTORTED_DIR, WARPED_DIR)


# rembg package to remove background
