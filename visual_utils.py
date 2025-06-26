import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
from pathlib import Path
import json
import sys
import normalize as n

def options() -> None:
    print("graph_points, original_vs_warped <desk_num>, compare_overlays")

# Visualize points gathered using gather_image_data.py
def graph_points() -> None:
    plt.figure(figsize=(8, 8))
    for _, points in point_data.items():
        if not points:
            continue
        xs, ys = zip(*points)
        plt.scatter(xs, ys, alpha=0.4)
    plt.xlabel("Long side (px)")
    plt.ylabel("Short side (px)")
    plt.xlim(0, 4032)
    plt.ylim(0, 3024)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

# Visualize original image next to warped image next to warped image
def original_vs_warped(desk_num: int) -> None:
    original = cv.cvtColor(cv.imread(Path(n.UNDISTORTED_DIR) / f"desk{desk_num}.jpeg"), cv.COLOR_BGR2RGB)
    warped = cv.cvtColor(cv.imread(Path(n.WARPED_DIR) / f"desk{desk_num}.jpeg"), cv.COLOR_BGR2RGB)
    fig, axes = plt.subplots(1, 3, figsize=(18, 8), dpi=100)
    for ax, img in zip(axes, [original, warped]):
        ax.imshow(img)
        ax.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
    plt.show()

# Visualize warped images overlayed and original images overlayed to evaluate homographies
def compare_overlays(alpha:int = 0.04) -> None:
    original_paths = sorted(Path(n.UNDISTORTED_DIR).glob("*.jpeg"))
    warped_paths = sorted(Path(n.WARPED_DIR).glob("*.jpeg"))
    fig = plt.figure(figsize=(12, 8))
    ax1 = fig.add_subplot(1, 2, 1)
    for img_path in original_paths:
        img = cv.cvtColor(cv.imread(str(img_path)), cv.COLOR_BGR2RGB)
        ax1.imshow(img, alpha=alpha)
    ax1.axis("off")

    ax2 = fig.add_subplot(1, 2, 2)
    for img_path in warped_paths:
        img = cv.cvtColor(cv.imread(str(img_path)), cv.COLOR_BGR2RGB)
        ax2.imshow(img, alpha=alpha)
    ax2.axis("off")
    fig.tight_layout()
    plt.show()

# Show cropped image
def cropped(desk_num:int) -> None:
    img = cv.cvtColor(cv.imread(str(Path(n.CROPPED_DIR) / f"desk{desk_num}.png")), cv.COLOR_BGR2RGB)
    plt.imshow(img)
    plt.show()

if __name__ == "__main__":
    with Path.open(n.DATA_PATH, "r") as f:
        point_data = json.load(f)
    all_points = []
    for points in point_data.values():
        all_points.extend(points)
    points_array = np.array(all_points)

    func = globals()[sys.argv[1]]
    if len(sys.argv) == 3:  # noqa: PLR2004
        func(sys.argv[2])
    else:
        func()

