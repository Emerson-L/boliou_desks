import json
from pathlib import Path
import numpy as np
import cv2 as cv
from PIL import Image
from tqdm import tqdm
from rembg import remove
import calibrate_camera

DATA_PATH = "assets/image_data_quads.json"
RAW_DIR = "assets/raw_jpeg"
UNDISTORTED_DIR = "assets/undistorted"
WARPED_DIR = "assets/warped"
CROPPED_DIR = "assets/cropped"

MASKING_VALUE = 85 #0-255, higher making a tighter mask

# Given an image array, return it undistorted
def undistort_image(img:cv.Mat) -> cv.Mat:
    h,  w = img.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    return cv.undistort(img, mtx, dist, None, newcameramtx)

# Take in an image an the goal shape, do the perspective transformation and return the new image
def do_perspective_warp(img:cv.Mat, desk_corners:list, goal_corners:list) -> cv.Mat:
    t = cv.getPerspectiveTransform(desk_corners, goal_corners)
    return cv.warpPerspective(img, t, (goal_width, goal_height))

# Find the average dimensions of all desks to use as goal shape to warp images to.
# Takes in a list of lists of 4 tuples, returns one tuple
def find_average_dimensions(quads: list) -> tuple:
    widths, heights = [], []
    for quad_list in quads:
        quad = np.array(quad_list)
        bottom_width = np.linalg.norm(quad[0] - quad[1])  # bottom_left to bottom_right
        top_width = np.linalg.norm(quad[2] - quad[3])     # top_left to top_right
        avg_width = (bottom_width + top_width) / 2
        left_height = np.linalg.norm(quad[0] - quad[2])   # bottom_left to top_left
        right_height = np.linalg.norm(quad[1] - quad[3])  # bottom_right to top_right
        avg_height = (left_height + right_height) / 2
        widths.append(avg_width)
        heights.append(avg_height)
    return round(np.mean(widths)), round(np.mean(heights))

# Create a mask by blending all warped images, removing the background, converting to grayscale,
# and then thresholding.
def create_mask(folder:str, pattern:str="*.jpeg") -> cv.Mat:
    image_paths = sorted(Path(folder).glob(pattern))
    base_img = cv.imread(str(image_paths[0])).astype(np.float32)
    h, w, c = base_img.shape
    blend = np.zeros((h, w, c), dtype=np.float32)
    count = 0

    for img_path in image_paths:
        img = cv.imread(str(img_path)).astype(np.float32)
        if img.shape != (h, w, c):
            img = cv.resize(img, (w, h))
        blend += img
        count += 1

    blended = (blend / count).astype(np.uint8)
    no_bg = remove(blended)
    grayscale = cv.cvtColor(no_bg, cv.COLOR_BGR2GRAY)
    _, mask = cv.threshold(grayscale, MASKING_VALUE, 255, cv.THRESH_BINARY)
    return mask

# Apply the mask and make black pixels transparent using RGBA
def mask_to_rgba(img:cv.Mat, mask:cv.Mat) -> cv.Mat:
    png_masked = cv.bitwise_and(img, img, mask=mask)
    rgb = cv.cvtColor(png_masked, cv.COLOR_BGR2RGB)
    rgba = np.dstack([rgb, np.ones(rgb.shape[:2], dtype=np.uint8) * 255])
    black_pixels = np.all(rgb == [0, 0, 0], axis=-1)
    rgba[black_pixels, 3] = 0
    return rgba

if __name__ == "__main__":
    with Path.open(DATA_PATH, "r") as f:
        point_data = json.load(f)

    mtx, dist = calibrate_camera.calibrate(calibrate_camera.CALIBRATION_DIR)

    goal_width, goal_height = find_average_dimensions(point_data.values())
    goal_corners = np.array([[0, goal_height],
                             [goal_width, goal_height],
                             [0, 0],
                             [goal_width, 0]], dtype = np.float32)

    # Undistort, warp perspective, save warped images
    Path(WARPED_DIR).mkdir(parents=True, exist_ok=True)
    for img_name in tqdm([img.name for img in Path(RAW_DIR).glob("*.jpeg")]):
        img = cv.imread(Path(RAW_DIR) / img_name)
        img_undistorted = undistort_image(img)
        desk_corners = np.array(point_data[img_name], dtype = np.float32)
        img_warp = do_perspective_warp(img_undistorted, desk_corners, goal_corners) # Makes images 2539 x 3568
        cv.imwrite(Path(WARPED_DIR) / img_name, img_warp)

    # Create mask from warped images, then for all images: mask, convert to RGBA,
    # resize and optimize using PIL and save as png
    # Could also: Remove leftover background with rembg
    mask = create_mask(WARPED_DIR)
    Path(CROPPED_DIR).mkdir(parents=True, exist_ok=True)
    for img_name in tqdm([img.name for img in Path(WARPED_DIR).glob("*.jpeg")]):
        img = cv.imread(Path(WARPED_DIR) / img_name)
        img_masked = mask_to_rgba(img, mask)
        png_pil = Image.fromarray(img_masked, mode = "RGBA")
        png_resized = png_pil.resize((round(goal_width/2), round(goal_height/2)), Image.LANCZOS) # Makes images 1270 x 1784
        png_resized.save((Path(CROPPED_DIR) / img_name).with_suffix(".png"), optimize=True, quality=95)


