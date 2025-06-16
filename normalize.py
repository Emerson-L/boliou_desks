# NOTES

#Rotation on top-bottom of desk axis:
#Roll: Rotation on the top of desk/bottom of desk axis. So desk tilting left to right (from sitting in desk POV)
#Pitch: Rotation on the left-right of desk axis. So desk tilting front to back (from sitting in desk POV)
#Yaw: Rotation on the vertical axis. So desk flatspinning (from sitting in desk POV)

#Assumptions:
#   Each desk photo is taken from the average flatness, so the roll = avg(rool) and pitch = avg(pitch).
#   Each desk photo is taken from the front, so the yaw = avg(yaw).
#   Each desk photo is taken from the average height, so the distance from camera to desk = avg(height)
#Input to adjust assumptions:
#   Roll skew: A value to adjust the assumption of roll skew
#   Pitch skew: A value to adjust the assumption of pitch skew.
#   Yaw skew: A value to adjust the assumption of yaw skew.

# First idea:
# Average desk is the centroid of each cluster
# Pull every point from each image to the centroid of its cluster, adjusting the rest of image based on those 4 points.

# Take that average desk and see if it tesselates. must tesselate to be usable.

import json
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
import cv2
from tqdm import tqdm

NUM_CLUSTERS = 4
DATA_PATH = "image_data/4points.json"
IMAGE_DIR = "images/original_jpeg"
OUTPUT_DIR = "images/warped"

# Take in a numpy array of points and find clusters and cluster centers with k-means
def get_cluster_centers(array: np.array) -> list:
    kmeans = KMeans(n_clusters=NUM_CLUSTERS, init='k-means++', max_iter=300, n_init=10, random_state=0)
    kmeans.fit(array)
    labels = kmeans.labels_
    return kmeans.cluster_centers_, labels

# Take in an image and the goal shape, do the homography (perspective correction)
# and return the adjusted image
def do_homography(img_path: str, goal_corners: list) -> cv2.Mat:
    img = cv2.imread(Path(IMAGE_DIR) / img_path)
    img_corners = np.array(point_data[img_path])
    H, _ = cv2.findHomography(img_corners, goal_corners)  # noqa: N806
    return cv2.warpPerspective(img, H, (img.shape[1], img.shape[0]))

if __name__ == "__main__":
    with Path.open(DATA_PATH, "r") as f:
        point_data = json.load(f)
    all_points = []
    for points in point_data.values():
        all_points.extend(points)
    points_array = np.array(all_points)

    cluster_centers, _ = get_cluster_centers(points_array)

    # Warping to the average desk using kmeans
    #center_corners = list(zip(cluster_centers[:, 0], cluster_centers[:, 1]))
    #center_corners = np.array([[round(x), round(y)] for (x, y) in center_corners])

    # Warping to desk88
    center_corners = np.array(point_data["desk88.jpeg"])

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    for img_name in tqdm([img.name for img in Path(IMAGE_DIR).glob("*.jpeg")]):
        img_warp = do_homography(img_name, center_corners)
        cv2.imwrite(Path(OUTPUT_DIR) / img_name, img_warp)


# rembg package to remove background
