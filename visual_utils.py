import matplotlib.pyplot as plt
import numpy as np
import cv2
from pathlib import Path
import json
import sys
import normalize as n

def options() -> None:
    print(
        "graph_points, graph_points_clusters, desk_shape, original_vs_warped1 <desk_num>, "
        "original_vs_warped2 <desk_num>, compare_overlays")

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

# Show points and k-means cluster centers
# should probably get y_kmeans categories
def graph_points_clusters() -> None:
    cluster_centers, _ = n.get_cluster_centers(points_array)
    plt.scatter(points_array[:, 0], points_array[:, 1], c=labels, s=50, cmap='viridis')
    plt.scatter(cluster_centers[:, 0], cluster_centers[:, 1], c='black', s=200, alpha=0.75)
    plt.show()

# Show shape of k-means clustered desk
def desk_shape() -> None:
    closed_centers = np.vstack([cluster_centers, cluster_centers[0]])
    plt.plot(closed_centers[:, 0], closed_centers[:, 1])
    plt.xlabel("Long side (px)")
    plt.ylabel("Short side (px)")
    plt.xlim(0, 4032)
    plt.ylim(0, 3024)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

# Visualize original image next to warped image next to warped image crossed with goal image, desk88
def original_vs_warped1(desk_num: int) -> None:
    original = cv2.cvtColor(cv2.imread(Path(n.UNDISTORTED_DIR) / f"desk{desk_num}.jpeg"), cv2.COLOR_BGR2RGB)
    warped = cv2.cvtColor(cv2.imread(Path(n.WARPED_DIR) / f"desk{desk_num}.jpeg"), cv2.COLOR_BGR2RGB)
    goal = cv2.cvtColor(cv2.imread(Path(n.UNDISTORTED_DIR) / "desk88.jpeg"), cv2.COLOR_BGR2RGB)
    overlaid = cv2.addWeighted(warped, 0.5, goal, 0.5, 0.0)
    fig, axes = plt.subplots(1, 3, figsize=(18, 8), dpi=100)
    for ax, img in zip(axes, [original, warped, overlaid]):
        ax.imshow(img)
        ax.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
    plt.show()

# Visualize original image next to warped image overlayed with goal points
def original_vs_warped2(desk_num: int) -> None:
    original = cv2.cvtColor(cv2.imread(Path(n.UNDISTORTED_DIR) / f"desk{desk_num}.jpeg"), cv2.COLOR_BGR2RGB)
    warped = cv2.cvtColor(cv2.imread(Path(n.WARPED_DIR) / f"desk{desk_num}.jpeg"), cv2.COLOR_BGR2RGB)
    fig, axes = plt.subplots(1, 2, figsize=(18, 8), dpi=100)
    for ax, img in zip(axes, [original, warped]):
        ax.imshow(img)
        ax.axis("off")
    goal_points = n.reorder_points(list(zip(cluster_centers[:, 0], cluster_centers[:, 1])))
    closed_points = np.vstack([goal_points, goal_points[0]])
    plt.plot(-closed_points[:, 1] + 3024, closed_points[:, 0])
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
    plt.show()

# Visualize warped images overlayed and original images overlayed to evaluate homographies
def compare_overlays(alpha:int = 0.04) -> None:
    original_paths = sorted(Path(n.UNDISTORTED_DIR).glob("*.jpeg"))
    warped_paths = sorted(Path(n.WARPED_DIR).glob("*.jpeg"))
    plt.figure(figsize=(12, 8))
    plt.subplot(1, 2, 1)
    for img_path in original_paths:
        img = cv2.cvtColor(cv2.imread(str(img_path)), cv2.COLOR_BGR2RGB)
        plt.imshow(img, alpha=alpha)
    plt.axis("off")

    plt.subplot(1, 2, 2)
    for img_path in warped_paths:
        img = cv2.cvtColor(cv2.imread(str(img_path)), cv2.COLOR_BGR2RGB)
        plt.imshow(img, alpha=alpha)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    with Path.open(n.DATA_PATH, "r") as f:
        point_data = json.load(f)
    all_points = []
    for points in point_data.values():
        all_points.extend(points)
    points_array = np.array(all_points)
    cluster_centers, labels = n.get_cluster_centers(points_array)

    func = globals()[sys.argv[1]]
    if len(sys.argv) == 3:  # noqa: PLR2004
        func(sys.argv[2])
    else:
        func()

