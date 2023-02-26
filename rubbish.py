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
    QThread,
    QTime,
    QTimer,
    QUrl,
    Signal,
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
    QProgressBar,
    QProgressDialog,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

"""
pyside imports
"""

import os
import random
import shutil
import sys
import time
import warnings

import cv2
import numpy as np
import qdarktheme
import skvideo.io

from H750_STEP.python_sdk.FlightController import FC_Controller, logger
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
video_file = r"test_h264.mp4"
videoCapture = cv2.VideoCapture(video_file)
video_fps = videoCapture.get(cv2.CAP_PROP_FPS)
video_frame_num = int(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
video_width = int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
videoCapture.release()
cam = cv2.VideoCapture()
api = FC_Controller()
# api.start_listen_serial("COM11", 115200)


def set_color(widget, rgb):
    color = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})" if isinstance(rgb, tuple) else rgb
    widget.setStyleSheet(f"color: {color}")


class fps_counter:
    def __init__(self, max_sample=40) -> None:
        self.t = time.perf_counter()
        self.max_sample = max_sample
        self.t_list = []

    def tick(self) -> None:
        now = time.perf_counter()
        self.t_list.append(now - self.t)
        self.t = now
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


class MySignal(QObject):
    image_signal = Signal(np.ndarray)
    start_processbar_signal = Signal(int)
    finish_processbar_signal = Signal()
    update_bin_progress_signal = Signal(int, int, int, int)
    set_system_status_signal = Signal(str)
    set_recognize_result_signal = Signal(str, str)
    add_recognized_item_signal = Signal(str, str)
    start_video_signal = Signal()
    stop_video_signal = Signal()


sig = MySignal()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.init_widgets()
        self.init_timers()
        self.init_threads()
        self.init_signals()
        self.setGeometry(0, 0, 1024, 700)
        self.misThread.start()
        self.image_temp = None

    def init_timers(self):
        self.processbar_timer = QTimer()
        self.processbar_timer.timeout.connect(self.update_processbar)
        self.video_timer = QTimer()
        self.video_timer.setTimerType(Qt.PreciseTimer)
        self.video_timer.timeout.connect(self.read_video)

    def init_threads(self):
        self.misThread = QThread()
        self.worker = MissionThread()
        self.worker.moveToThread(self.misThread)
        self.misThread.started.connect(self.worker.run)

    def init_signals(self):
        sig.image_signal.connect(self.show_image)
        sig.start_processbar_signal.connect(self.start_processbar)
        sig.finish_processbar_signal.connect(self.finish_processbar)
        sig.set_recognize_result_signal.connect(self.set_recognize_result)
        sig.add_recognized_item_signal.connect(self.add_recognized_item)
        sig.update_bin_progress_signal.connect(self.update_bin_progress)
        sig.set_system_status_signal.connect(self.set_system_status)
        sig.start_video_signal.connect(self.start_video)
        sig.stop_video_signal.connect(self.stop_video)

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

    def update_bin_progress(self, percent1, percent2, percent3, percent4):
        for i, percent in enumerate([percent1, percent2, percent3, percent4]):
            percent = min(percent, 100)
            label: QLabel = getattr(self, f"labelBin{i + 1}")
            progress: QProgressBar = getattr(self, f"progressBin{i + 1}")
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

    def set_system_status(self, status):
        self.labelSystem.setText(status)

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

    def start_video(self):
        time.sleep(1)
        self.videogen = skvideo.io.vreader(video_file)
        self.video_timer.start(1000 / video_fps)

    def stop_video(self):
        self.video_timer.stop()
        self.videogen.close()

    def read_video(self):
        try:
            frame = next(self.videogen)
            self.show_image(frame)
        except StopIteration:
            self.stop_video()

    def show_image(self, image: np.ndarray):
        fpsc.tick()
        self._image = image.copy()
        cv2.putText(
            self._image,
            f"{fpsc.fps:.2f}FPS",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2,
        )
        self.pixmap = QPixmap.fromImage(
            QImage(
                self._image,
                self._image.shape[1],
                self._image.shape[0],
                QImage.Format.Format_RGB888,
            )
        ).scaled(self.labelVideo.width(), self.labelVideo.height(), Qt.KeepAspectRatio)
        self.labelVideo.setPixmap(self.pixmap)
        self.image_temp = self._image

    def resizeEvent(self, event) -> None:
        if self.image_temp is not None:
            self.pixmap = QPixmap.fromImage(
                QImage(
                    self.image_temp,
                    self.image_temp.shape[1],
                    self.image_temp.shape[0],
                    QImage.Format.Format_RGB888,
                )
            ).scaled(
                self.labelVideo.width(), self.labelVideo.height(), Qt.KeepAspectRatio
            )
            self.labelVideo.setPixmap(self.pixmap)
        return super().resizeEvent(event)

    # F11 全屏
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        return super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        self.misThread.quit()
        return super().closeEvent(event)


class MissionThread(QObject):
    ### 设置
    rotation_speed = 45

    ### 变量
    sight_pos = 1  # 当前视角位置 一共六格
    down_pos = 0  # 下盘位置 一共六格

    def __init__(self, parent=None):
        super().__init__(parent)

    def show_image(self, image: np.ndarray):
        self._image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        sig.image_signal.emit(self._image)

    def run(self):
        while True:
            for i in range(0,10):
                cam.open(i)
                if cam.isOpened():
                    logger.info(f"Opened camera {i}")
                    break
            if not cam.isOpened():
                logger.warn("No camera found")
                sig.set_system_status_signal.emit(f"错误: 未找到摄像头")
            else:
                sig.set_system_status_signal.emit(f"摄像头已连接")
                break
        while True:
            try:
                self.work()
            except Exception as e:
                sig.set_system_status_signal.emit(f"任务线程异常, 正在重启...")
                logger.exception(e)
                time.sleep(1)
            else:
                sig.set_system_status_signal.emit("任务线程正常退出")
                break

    def calibration(self):
        sig.set_system_status_signal.emit("正在校准储物盘")
        time.sleep(1)
        sig.set_system_status_signal.emit("校准完成")
        time.sleep(1)

    def left(self):
        self.sight_pos = (self.sight_pos + 1) % 6
        api.step_rotate_abs(api.STEP1, self.sight_pos * 60)
        api.step_rotate_abs(api.STEP2, (self.sight_pos - self.down_pos) * 60)
        api.wait_for_step_idle(api.STEP1 | api.STEP2)

    def right(self):
        self.sight_pos = (self.sight_pos - 1) % 6
        api.step_rotate_abs(api.STEP1, self.sight_pos * 60)
        api.step_rotate_abs(api.STEP2, (self.sight_pos - self.down_pos) * 60)
        api.wait_for_step_idle(api.STEP1 | api.STEP2)

    def goto(self, pos):
        self.sight_pos = pos
        api.step_rotate_abs(api.STEP1, self.sight_pos * 60)
        api.step_rotate_abs(api.STEP2, (self.sight_pos - self.down_pos) * 60)
        api.wait_for_step_idle(api.STEP1 | api.STEP2)

    def release_next(self):
        self.down_pos = self.down_pos + 1
        api.step_rotate_abs(api.STEP2, (self.sight_pos - self.down_pos) * 60)
        api.wait_for_step_idle(api.STEP2)

    def work(self):
        while True:
            ret, frame = cam.read()
            if not ret:
                continue
            self.show_image(frame)
        
        time.sleep(1)
        sig.set_system_status_signal.emit("等待控制器连接中...")
        api.wait_for_connection(-1)
        sig.set_system_status_signal.emit("控制器连接成功")
        api.step_set_speed(api.STEP1 | api.STEP2, self.rotation_speed)
        time.sleep(1)
        self.calibration()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(qdarktheme.load_stylesheet(theme="dark"))
    window = MainWindow()
    window.show()
    app.exec()
