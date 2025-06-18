import json
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
import cv2
from tqdm import tqdm
import calibrate_camera

NUM_CLUSTERS = 4
DATA_PATH = "image_data/16points_1.json"
RAW_DIR = "images/raw_jpeg"
UNDISTORTED_DIR = "images/undistorted"
WARPED_DIR = "images/warped"

# Given an image array, return it undistorted
def undistort_image(img:np.uint8) -> cv2.Mat:
    h,  w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    return cv2.undistort(img, mtx, dist, None, newcameramtx)

# Undistort images and write them to folder
def save_undistorteds(input_dir:str, output_dir:str) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for img_name in tqdm([img.name for img in Path(input_dir).glob("*.jpeg")]):
        img = cv2.imread(Path(input_dir) / img_name)
        cv2.imwrite(Path(output_dir) / img_name, undistort_image(img))

# Take in a numpy array of points and find clusters and cluster centers with k-means
def get_cluster_centers(array: np.array) -> list:
    kmeans = KMeans(n_clusters=NUM_CLUSTERS, init='k-means++', max_iter=300, n_init=10, random_state=0)
    kmeans.fit(array)
    labels = kmeans.labels_
    return kmeans.cluster_centers_, labels

# Take in an image and the goal shape, do the homography (perspective correction)
# and return the adjusted image
def do_homography(img:cv2.Mat, img_corners:list, goal_corners:list) -> cv2.Mat:
    H, _ = cv2.findHomography(img_corners, goal_corners)  # noqa: N806
    return cv2.warpPerspective(img, H, (img.shape[1], img.shape[0]))

# Save homographies/warped images
def save_warpeds(input_dir:str, output_dir:str) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for img_name in tqdm([img.name for img in Path(input_dir).glob("*.jpeg")]):
        img = cv2.imread(Path(input_dir) / img_name)
        img_corners = np.array(point_data[img_name])
        img_warp = do_homography(img, img_corners, center_corners)
        cv2.imwrite(Path(output_dir) / img_name, img_warp)

# Take in a list of 4 (x, y) pairs and reorder them, returning the new list
# Necessary for homography if point data collection order is inconsistent
def reorder_points(points: list) -> list:
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    avg_x, avg_y = sum(xs) / 4, sum(ys) / 4

    big_x = [p for p in points if p[0] > avg_x]
    small_x = [p for p in points if p[0] <= avg_x]
    big_y = [p for p in points if p[1] > avg_y]
    small_y = [p for p in points if p[1] <= avg_y]

    def find_corner(x_area:list, y_area:list) -> tuple:
        return next(p for p in points if p in x_area and p in y_area)

    return [
        find_corner(small_x, small_y), find_corner(big_x, small_y),
        find_corner(big_x, big_y), find_corner(small_x, big_y),
    ]


if __name__ == "__main__":
    with Path.open(DATA_PATH, "r") as f:
        point_data = json.load(f)
    all_points = []
    for points in point_data.values():
        all_points.extend(points) #reorder_points here if 4point
    points_array = np.array(all_points)

    # mtx, dist = calibrate_camera.calibrate(calibrate_camera.CALIBRATION_DIR)
    # save_undistorteds(RAW_DIR, UNDISTORTED_DIR)

    #4point version

    #cluster_centers, _ = get_cluster_centers(points_array)

    # center_corners = list(zip(cluster_centers[:, 0], cluster_centers[:, 1])) #warping to average desk
    # center_corners = [[round(x), round(y)] for (x, y) in center_corners]
    # center_corners = np.array(reorder_points(center_corners))

    # center_corners = np.array(reorder_points(point_data["desk88.jpeg"])) #warping to desk88

    #16point version
    center_corners = np.array(point_data["desk88.jpeg"])

    save_warpeds(UNDISTORTED_DIR, WARPED_DIR)


# rembg package to remove background
