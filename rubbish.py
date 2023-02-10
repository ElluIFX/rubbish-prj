import os
import sys

sys.path.append(os.path.dirname(__file__))

"""Add parent directory to path"""

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QTimer,
    QUrl,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

"""
pyside imports
"""

import random
import time
import warnings

import cv2
import numpy as np
import qdarktheme
import skvideo.io

from rubbish_gui import Ui_MainWindow

colors = {
    "可回收垃圾": "#80EB57",
    "厨余垃圾": "#EB904B",
    "有害垃圾": "#EB4E3F",
    "其他垃圾": "#28D6EB",
}
text_color = "#FCFCFC"
warning_color = "#EB1900"
warning_percent = 90
font = "更纱黑体 UI SC"
emoji = {
    "1号电池": "🔋",
    "2号电池": "🔋",
    "5号电池": "🔋",
    "过期药物": "💊",
    "易拉罐": "🥤",
    "矿泉水瓶": "🥤",
    "小土豆": "🥔",
    "白萝卜": "🥕",
    "胡萝卜": "🥕",
    "瓷片": "🍽️",
    "鹅卵石": "🗿",
}
category = {
    "1号电池": "有害垃圾",
    "2号电池": "有害垃圾",
    "5号电池": "有害垃圾",
    "过期药物": "有害垃圾",
    "易拉罐": "可回收垃圾",
    "矿泉水瓶": "可回收垃圾",
    "小土豆": "厨余垃圾",
    "白萝卜": "厨余垃圾",
    "胡萝卜": "厨余垃圾",
    "瓷片": "其他垃圾",
    "鹅卵石": "其他垃圾",
}
item_list = list(category.keys())
video_file = "test.mp4"
videoCapture = cv2.VideoCapture(video_file)
video_fps = videoCapture.get(cv2.CAP_PROP_FPS)
video_frame_num = int(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
video_width = int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
videoCapture.release()


def set_color(widget, rgb):
    color = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})" if isinstance(rgb, tuple) else rgb
    widget.setStyleSheet(f"color: {color}")


class fps_counter:
    def __init__(self, max_sample=40) -> None:
        self.t = time.time()
        self.max_sample = max_sample
        self.t_list = []

    def tick(self) -> None:
        self.t_list.append(time.time() - self.t)
        self.t = time.time()
        if len(self.t_list) > self.max_sample:
            self.t_list.pop(0)

    @property
    def fps(self) -> float:
        length = len(self.t_list)
        sum_t = sum(self.t_list)
        if length == 0:
            return 0.0
        else:
            return length / sum_t


fpsc = fps_counter()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.init_timers()
        self.init_widgets()
        self.setGeometry(0, 0, 1024, 700)
        self.image_temp = None
        self.cap = cv2.VideoCapture()
        for i in range(10):
            self.cap.open(i)
            if self.cap.isOpened():
                print(f"Opened camera {i}")
                break
        if not self.cap.isOpened():
            warnings.warn("No camera found")
        self.test_temp = 0
        self.test_add = 1
        self.testtimer = QTimer()
        self.testtimer.timeout.connect(self.test)
        self.testtimer.start(100)

        # self.start_video()
        self.start_camera(60)

    def test(self):
        random_item = random.choice(item_list)
        rec_category = category[random_item]
        self.set_recognize_result(rec_category, random_item)
        self.add_recognized_item(rec_category, random_item)
        self.test_temp += self.test_add
        if self.test_temp == 100:
            self.test_add = -1
        elif self.test_temp == 0:
            self.test_add = 1
        self.update_bin_progress(*([self.test_temp] * 4))

    def init_widgets(self):
        self.progressBin1.progress_color = colors["可回收垃圾"]
        self.progressBin2.progress_color = colors["厨余垃圾"]
        self.progressBin3.progress_color = colors["有害垃圾"]
        self.progressBin4.progress_color = colors["其他垃圾"]
        set_color(self.labelBin1, colors["可回收垃圾"])
        set_color(self.labelBin2, colors["厨余垃圾"])
        set_color(self.labelBin3, colors["有害垃圾"])
        set_color(self.labelBin4, colors["其他垃圾"])
        self.labelSystem.setText("正在初始化...")
        self.labelResult.setText("等待识别")
        self.progressProcess.setMaximum(100)

    def init_timers(self):
        self.video_timer = QTimer()
        self.video_timer.setTimerType(Qt.PreciseTimer)
        self.video_timer.timeout.connect(self.read_video)
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.read_camera)
        self.processbar_timer = QTimer()
        self.processbar_timer.timeout.connect(self.update_processbar)

    def update_processbar(self):
        current = self.progressProcess.value()
        if current == 100:
            self.processbar_timer.stop()
            return
        self.progressProcess.setValue(current + 1)

    def start_processbar(self, estimate_time):
        self.progressProcess.setValue(0)
        self.processbar_timer.start(estimate_time * 1000 / 100)

    def finish_processbar(self):
        self.progressProcess.setValue(100)
        self.processbar_timer.stop()

    def start_video(self):
        self.videogen = skvideo.io.vreader(video_file)
        self.video_timer.start(1000 / video_fps)
        self.labelSystem.setText("播放公益视频")

    def stop_video(self):
        self.video_timer.stop()
        self.videogen.close()

    def start_camera(self, fps=30):
        self.camera_timer.start(1000 / fps)

    def stop_camera(self):
        self.camera_timer.stop()

    def read_video(self):
        try:
            self.frame = next(self.videogen)
            self.show_image(self.frame)
            fpsc.tick()
            print(f"fps: {fpsc.fps}")
        except StopIteration:
            self.stop_video()

    def read_camera(self):
        ret, self.frame = self.cap.read()
        if ret:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.show_image(self.frame)

    def update_bin_progress(self, percent1, percent2, percent3, percent4):
        for i, percent in enumerate([percent1, percent2, percent3, percent4]):
            percent = min(percent, 100)
            label = getattr(self, f"labelBin{i + 1}")
            progress = getattr(self, f"progressBin{i + 1}")
            progress.setValue(percent)
            if percent > warning_percent:
                set_color(label, warning_color)
                if "满" not in label.text():
                    label.setText(f"{label.text()}(满)")
                label.setFont(QFont(font, 12, QFont.Bold))
                progress.text_color = warning_color
            else:
                if "满" in label.text():
                    label.setText(label.text().replace("(满)", ""))
                set_color(getattr(self, f"labelBin{i + 1}"), colors[label.text()])
                label.setFont(QFont(font, 12))
                progress.text_color = text_color

    def set_recognize_result(self, category, name):
        self.labelResult.setText(f"{name} ({category})")
        set_color(self.labelResult, colors[category])

    def add_recognized_item(self, category, name):
        time_str = time.strftime("%H:%M:%S", time.localtime())
        item = QListWidgetItem(f"{time_str} {category}-{name}")
        item.setForeground(QColor(colors[category]))
        item.setFont(QFont(font, 12))
        self.listWidgetLog.addItem(item)
        self.listWidgetLog.scrollToBottom()

    def show_image(self, image: np.ndarray):
        self.pixmap = QPixmap.fromImage(
            QImage(image, image.shape[1], image.shape[0], QImage.Format.Format_RGB888)
        ).scaled(self.labelVideo.width(), self.labelVideo.height(), Qt.KeepAspectRatio)
        self.labelVideo.setPixmap(self.pixmap)

    def resizeEvent(self, event) -> None:
        if self.image_temp is not None:
            self.show_image(self.image_temp)
        if self.isMaximized():
            self.showFullScreen()
        return super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(qdarktheme.load_stylesheet(theme="dark"))
    window = MainWindow()
    window.show()
    app.exec()
