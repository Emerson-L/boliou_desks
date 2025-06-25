import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ExifTags
from tqdm import tqdm
from collections import Counter

CALIBRATION_DIR = "images/calibration"
CALIBRATION_BOARD = 7, 10

# Print image metadata of all images in specified directory
# For ensuring that images for calibration and perspective warp are all similar enough
def print_image_metadata(image_dir:str) -> None:
    keys_of_interest = ["Model", "ExifImageWidth", "ExifImageHeight", "FocalLength"]
    # Other possible paramaters to include to ensure full camera symmetry:
    # ApertureValue, ShutterSpeedValue, ISO, BrightnessValue, ExposureBiasValue, ExposureTime, FNumber, ISOSpeedRatings, LensSpecificaiton
    value_counters = {key: Counter() for key in keys_of_interest}

    for img_name in tqdm([img.name for img in Path(image_dir).glob("*.jpeg")]):
        img = Image.open(Path(image_dir) / img_name)
        exif_raw = img._getexif() # noqa: SLF001
        if not exif_raw:
            continue
        exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}
        for key in keys_of_interest:
            if key in exif:
                value_counters[key][exif[key]] += 1

    for key in keys_of_interest:
        print(f"{key}:")
        for value, count in value_counters[key].items():
            print(f"    {value}: {count} images")

# Calibrates camera given a directory with some calibration images of a black/white chessboard
# Mostly taken from docs.opencv.org
def calibrate(calibration_images_dir:str) -> None:
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((6*7,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane
    images = Path(calibration_images_dir).glob("*.jpeg")

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (7,6), None)
        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    return mtx, dist

