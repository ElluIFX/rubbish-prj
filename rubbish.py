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

import cv2
import numpy as np
import qdarktheme

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


def set_color(widget, rgb):
    color = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})" if isinstance(rgb, tuple) else rgb
    widget.setStyleSheet(f"color: {color}")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.progressBin1.progress_color = colors["可回收垃圾"]
        self.progressBin2.progress_color = colors["厨余垃圾"]
        self.progressBin3.progress_color = colors["有害垃圾"]
        self.progressBin4.progress_color = colors["其他垃圾"]
        self.labelSystem.setText("正在初始化...")
        self.labelResult.setText("等待识别")

        self.image_temp = None
        self.test_temp = 0
        self.testtimer = QTimer()
        self.testtimer.timeout.connect(self.test)
        self.testtimer.start(100)

    def test(self):
        self.image_temp = cv2.imread("test.png")
        random_item = random.choice(item_list)
        rec_category = category[random_item]
        self.set_recognize_result(rec_category, random_item)
        self.add_recognized_item(rec_category, random_item)
        self.labelSystem.setText("正在识别...")
        self.show_image(self.image_temp)
        self.test_temp += 1
        self.update_bin_progress(*([self.test_temp] * 4))
        self.progressProcess.setValue(self.test_temp)

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
                set_color(getattr(self, f"labelBin{i + 1}"), text_color)
                if "满" in label.text():
                    label.setText(label.text().replace("(满)", ""))
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
