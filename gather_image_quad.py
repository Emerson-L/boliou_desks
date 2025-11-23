import sys
import os
import json
from pathlib import Path
from tqdm import tqdm
from PIL import Image
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage, QKeySequence
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QShortcut, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QPoint
from collections import Counter

INPUT_DIR = "assets/raw_jpeg_new"
OUTPUT_FILE = "assets/image_data_quads_new2.json"
WINDOW_HEIGHT = 840
DRAG_SELECT_DISTANCE = 40

class ImageLabel(QLabel):
    def __init__(self, pixmap, scale_factor, img_width, img_height) -> None:
        super().__init__()
        self.setPixmap(pixmap)
        self.points = []
        self.scale_factor = scale_factor
        self.img_width = img_width
        self.img_height = img_height
        self.dragging_idx = None

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            x_disp = int(event.pos().x() / self.scale_factor)
            y_disp = int(event.pos().y() / self.scale_factor)
            x = x_disp
            y = self.img_height - y_disp
            for idx, (px, py) in enumerate(self.points):
                if abs(px - x) < DRAG_SELECT_DISTANCE and abs(py - y) < DRAG_SELECT_DISTANCE:
                    self.dragging_idx = idx
                    return
            if len(self.points) < 4:
                self.points.append((x, y))
                self.update()

    def mouseMoveEvent(self, event) -> None:
        if self.dragging_idx is not None:
            x_disp = int(event.pos().x() / self.scale_factor)
            y_disp = int(event.pos().y() / self.scale_factor)
            x = x_disp
            y = self.img_height - y_disp
            self.points[self.dragging_idx] = (x, y)
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        self.dragging_idx = None

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setBrush(Qt.black)
        painter.setPen(QPen(Qt.black, 1))
        for x, y in self.points:
            painter.drawEllipse(QPoint(int(x * self.scale_factor), int((self.img_height - y) * self.scale_factor)), 6, 6)
        if len(self.points) > 1:
            painter.setPen(QPen(Qt.red, 3))
            for i in range(len(self.points) - 1):
                x1, y1 = self.points[i]
                x2, y2 = self.points[i + 1]
                painter.drawLine(
                    int(x1 * self.scale_factor), int((self.img_height - y1) * self.scale_factor),
                    int(x2 * self.scale_factor), int((self.img_height - y2) * self.scale_factor),
                )
        if len(self.points) == 4:
            painter.setPen(QPen(Qt.red, 3))
            x1, y1 = self.points[3]
            x2, y2 = self.points[0]
            painter.drawLine(
                int(x1 * self.scale_factor), int((self.img_height - y1) * self.scale_factor),
                int(x2 * self.scale_factor), int((self.img_height - y2) * self.scale_factor),
            )

class MainWindow(QMainWindow):
    def __init__(self, image_files) -> None:
        super().__init__()
        self.image_files = image_files
        self.pbar = tqdm(total=len(image_files), desc="Processing images")
        self.image_data = {}
        self.current_idx = 0
        self.setWindowTitle("Click to select points")
        self.label = None

        self.save_btn = QPushButton("Save and Next", self)
        self.save_btn.clicked.connect(self.save_and_next)
        self.save_btn.setFixedWidth(150)
        self.shortcut_open = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_open.activated.connect(self.save_and_next)
        self.shortcut_open = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.shortcut_open.activated.connect(self.undo_last_point)

        self.central_widget = QWidget(self)
        self.vbox = QVBoxLayout(self.central_widget)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        self.load_image()

    # Loads image, adjusting window to fit image size and aspect ratio.
    def load_image(self) -> None:
        if self.label:
            self.vbox.removeWidget(self.label)
            self.label.setParent(None)
            self.label = None
        if self.current_idx >= len(self.image_files):
            with Path.open(OUTPUT_FILE, "w") as f:
                json.dump(self.image_data, f, indent=4)
            QApplication.quit()
            return

        image_file = self.image_files[self.current_idx]
        img_path = Path(INPUT_DIR) / image_file
        img = Image.open(img_path)
        img = img.rotate(90, expand=True).convert("RGB")
        img_width, img_height = img.width, img.height

        self.pbar.update()
        self.setWindowTitle(f"Click to select points ({image_file})")

        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        max_width, max_height = int(screen_rect.width()), int(WINDOW_HEIGHT)
        scale = min(max_width / img_width, max_height / img_height, 1.0)
        disp_width, disp_height = int(img_width * scale), int(img_height * scale)
        img_resized = img.resize((disp_width, disp_height)).convert("RGB")
        data = img_resized.tobytes()
        bytes_per_line = disp_width * 3
        img_qt = QImage(data, disp_width, disp_height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img_qt)

        self.label = ImageLabel(pixmap, scale, img_width, img_height)
        self.label.setFixedSize(disp_width, disp_height)
        self.label.move(0, 0)
        self.vbox.insertWidget(0, self.label, alignment=Qt.AlignTop | Qt.AlignLeft)

        self.resize(disp_width, disp_height)
        self.save_btn.raise_()

    # Saves points in OUTPUT_FILE, loads next image
    def save_and_next(self) -> None:
        image_file = self.image_files[self.current_idx]
        points = self.rearrange_points(self.label.points)
        if points is None:
            return
        self.image_data[image_file] = points
        with Path.open(OUTPUT_FILE, "w") as f:
            json.dump(self.image_data, f)
        self.current_idx += 1
        self.load_image()

    # Rearranges points to the order needed for perspective correction using the centroid
    def rearrange_points(self, points:list) -> list:
        flipped_points = [(y, x) for (x, y) in points]
        x = [p[0] for p in flipped_points]
        y = [p[1] for p in flipped_points]
        centroid = (sum(x) / len(flipped_points), sum(y) / len(flipped_points))
        bottom_left, bottom_right, top_left, top_right = None, None, None, None
        for p in flipped_points:
            big_x = p[0] > centroid[0]
            big_y = p[1] > centroid[1]
            if big_x and big_y: # big big
                bottom_right = p
            elif big_x and not big_y: # big small
                top_right = p
            elif not big_x and big_y: # small big
                bottom_left = p
            else: # small small
                top_left = p
        if not bottom_left or not bottom_right or not top_left or not top_right:
            print("Invalid quadrangle. Try again with a more rectangular shape.")
            return None
        return ([bottom_left, bottom_right, top_left, top_right])

    # For ctrl-z
    def undo_last_point(self) -> None:
        if self.label and self.label.points:
            self.label.points.pop()
            self.label.update()

# For printing information on already collected data
def print_data_info() -> None:
    with Path.open(OUTPUT_FILE, "r") as f:
        point_data = json.load(f)
    nums_points = []
    for points in point_data.values():
        nums_points.append(len(points))
    for key, count in Counter(nums_points).items():
        print(f"{key} occurs {count} times")

if __name__ == "__main__":
    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.jpeg')]
    if not image_files:
        print(f"No images found in {INPUT_DIR}")
        sys.exit()

    app = QApplication(sys.argv)
    window = MainWindow(image_files)
    window.show()
    sys.exit(app.exec_())

    # print_data_info()
