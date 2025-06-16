import sys
import os
import json
from pathlib import Path
from tqdm import tqdm
from PIL import Image
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage, QKeySequence
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QShortcut, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QPoint

INPUT_DIR = "images/original_jpeg"
OUTPUT_FILE = "image_data/6points.json"
WINDOW_HEIGHT = 840

class ImageLabel(QLabel):
    def __init__(self, pixmap, scale_factor) -> None:
        super().__init__()
        self.setPixmap(pixmap)
        self.points = []
        self.scale_factor = scale_factor

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            x = int(event.pos().x() / self.scale_factor)
            y = int(event.pos().y() / self.scale_factor)
            self.points.append((x, y))
            self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setBrush(Qt.red)
        painter.setPen(QPen(Qt.red, 4))
        for x, y in self.points:
            painter.drawEllipse(QPoint(int(x * self.scale_factor), int(y * self.scale_factor)), 2, 2)

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

    def load_image(self) -> None:
        if self.label:
            self.vbox.removeWidget(self.label)
            self.label.setParent(None)
            self.label = None
        if self.current_idx >= len(self.image_files):
            with Path.open(OUTPUT_FILE, "w") as f:
                json.dump(self.image_data, f, indent=4)
            print(f"All points saved to {OUTPUT_FILE}")
            QApplication.quit()
            return

        image_file = self.image_files[self.current_idx]
        img_path = Path(INPUT_DIR) / image_file
        img = Image.open(img_path)
        img = img.rotate(90, expand=True).convert("RGB")

        self.pbar.update()
        self.setWindowTitle(f"Click to select points ({image_file})")

        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        max_width, max_height = int(screen_rect.width()), int(WINDOW_HEIGHT)
        scale = min(max_width / img.width, max_height / img.height, 1.0)
        disp_width, disp_height = int(img.width * scale), int(img.height * scale)
        img_resized = img.resize((disp_width, disp_height)).convert("RGB")
        data = img_resized.tobytes()
        bytes_per_line = disp_width * 3
        img_qt = QImage(data, disp_width, disp_height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img_qt)

        self.label = ImageLabel(pixmap, scale)
        self.label.setFixedSize(disp_width, disp_height)
        self.label.move(0, 0)
        self.vbox.insertWidget(0, self.label, alignment=Qt.AlignTop | Qt.AlignLeft)

        self.resize(disp_width, disp_height)
        self.save_btn.raise_()

    def save_and_next(self) -> None:
        image_file = self.image_files[self.current_idx]
        self.image_data[image_file] = self.label.points
        with Path.open(OUTPUT_FILE, "w") as f:
            json.dump(self.image_data, f)
        self.current_idx += 1
        self.load_image()

    def undo_last_point(self) -> None:
        if self.label and self.label.points:
            self.label.points.pop()
            self.label.update()

if __name__ == "__main__":
    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".jpeg")]
    if not image_files:
        print(f"No JPEG images found in {INPUT_DIR}")
        sys.exit()

    app = QApplication(sys.argv)
    window = MainWindow(image_files)
    window.show()
    sys.exit(app.exec_())
