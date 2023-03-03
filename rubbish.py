import os
import sys

sys.path.append(os.path.dirname(__file__))

"""Add parent directory to path"""

from PyQt5.QtCore import (
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
)
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtGui import (
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
from PyQt5.QtWidgets import (
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
from threading import Event

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
warning_percent = 80
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
translate = {
    "battery_1": "1号电池",
    "battery_2": "2号电池",
    "battery_5": "5号电池",
    "medicine": "过期药物",
    "can": "易拉罐",
    "bottle": "矿泉水瓶",
    "potato": "小土豆",
    "white_carrot": "白萝卜",
    "carrot": "胡萝卜",
    "tile": "瓷片",
    "rock": "鹅卵石",
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
cam_img = None
cam_width = 1920
cam_height = 1080
cam_event = Event()
api = FC_Controller()
api.start_listen_serial("COM3", 115200)
api.settings.strict_ack_check = False


def set_color(widget, rgb):
    color = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})" if isinstance(rgb, tuple) else rgb
    widget.setStyleSheet(f"color: {color}")


def set_bar_color(widget, rgb):
    color = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})" if isinstance(rgb, tuple) else rgb
    widget.setStyleSheet(
        "QProgressBar::chunk " + "{" + f"background-color: {color};" + "}"
    )


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
    def __init__(self, parent=None):
        super(MySignal, self).__init__(parent)

    image_signal = Signal(np.ndarray)
    start_processbar_signal = Signal(int)
    finish_processbar_signal = Signal()
    update_bin_progress_signal = Signal(int, int, int, int)
    set_system_status_signal = Signal(str)
    set_recognize_result_signal = Signal(str, str)
    add_recognized_item_signal = Signal(str, str)
    start_video_signal = Signal()
    stop_video_signal = Signal()
    cam_thread_start_signal = Signal()
    key_event_signal = Signal(int)


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
        self.update_bin_progress(20, 20, 20, 20)

    def init_timers(self):
        self.processbar_timer = QTimer()
        self.processbar_timer.timeout.connect(self.update_processbar)
        self.video_timer = QTimer()
        self.video_timer.setTimerType(Qt.PreciseTimer)
        self.video_timer.timeout.connect(self.read_video)

    def init_threads(self):
        self.misThread = QThread()
        self.misWorker = MissionThread()
        self.misWorker.moveToThread(self.misThread)
        self.misThread.started.connect(self.misWorker.run)
        self.camThread = QThread()
        self.camWorker = CameraThread()
        self.camWorker.moveToThread(self.camThread)
        self.camThread.started.connect(self.camWorker.run)

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
        sig.cam_thread_start_signal.connect(self.camThread.start)

    def init_widgets(self):
        set_bar_color(self.progressBin1, colors["可回收垃圾"])
        set_bar_color(self.progressBin2, colors["厨余垃圾"])
        set_bar_color(self.progressBin3, colors["有害垃圾"])
        set_bar_color(self.progressBin4, colors["其他垃圾"])
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
                if "未满" in label.text():
                    label.setText(f"{label.text().replace('未满','即将装满')}")
                label.setFont(QFont(font, 12, QFont.Bold))
                progress.text_color = warning_color
            else:
                if "即将装满" in label.text():
                    label.setText(label.text().replace("即将装满", "未满"))
                set_color(
                    getattr(self, f"labelBin{i + 1}"),
                    colors[label.text().replace("\n未满", "")],
                )
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
        logger.info("start video")
        self.videogen = skvideo.io.vreader(video_file)
        self.video_timer.start(int(1000 / video_fps))

    def stop_video(self):
        logger.info("stop video")
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
        sig.key_event_signal.emit(int(event.key()))
        return super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        self.misThread.quit()
        return super().closeEvent(event)


class CameraThread(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        global cam_img, cam
        logger.info("Camera thread started")
        while True:
            if not cam.isOpened():
                time.sleep(0.1)
                continue
            ret, frame = cam.read()
            if ret:
                cam_img = frame.copy()
                cam_event.set()
            else:
                time.sleep(0.1)
                logger.warn("Camera read failed")


class MissionThread(QObject):
    ### 设置
    rotation_speed = 60
    push_speed = 200
    rec_offset = 105
    max_push = 7000
    idle_delay = 30  # 空闲视频等待时间

    ### 变量
    sight_pos = 1  # 当前视角位置 一共六格
    down_pos = 0  # 下盘位置 一共六格
    idle = True  # 是否空闲

    def __init__(self, parent=None):
        super().__init__(parent)
        self.calibrating = False
        self.cali_target = 0
        self.cali_list = [api.STEP1, api.STEP2, api.STEP3]
        sig.key_event_signal.connect(self.key_event)

    def show_image(self, image: np.ndarray):
        self._image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        sig.image_signal.emit(self._image)

    def open_camera(self):
        while True:
            for i in range(1, 10):
                cam.open(i)
                if cam.isOpened():
                    logger.info(f"Opened camera {i}")
                    break
            if not cam.isOpened():
                logger.warn("No camera found")
                self.system_info(f"等待摄像头连接中...")
            else:
                cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
                cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)
                self.system_info(f"摄像头已连接(ID:{i})")
                time.sleep(1)
                break

    def run(self):
        self.system_info("等待控制器连接中...")
        # api.wait_for_connection(-1)
        self.system_info("控制器连接成功")
        time.sleep(1)
        api.step_set_speed(api.STEP1 | api.STEP2, self.rotation_speed)
        api.step_set_speed(api.STEP3, self.push_speed)
        self.open_camera()
        sig.cam_thread_start_signal.emit()
        self.calibrate()
        while True:
            try:
                self.work()
            except Exception as e:
                self.system_info(f"任务线程异常, 正在重启...")
                logger.exception(e)
                time.sleep(1)
            else:
                self.system_info("任务线程正常退出")
                break

    def calibrate(self):
        global cam_img
        self.calibrating = True
        api.settings.check_idle = False
        self.system_info(f"正在校准电机-{self.cali_target}")
        while self.calibrating:
            cam_event.wait()
            cam_event.clear()
            frame = cam_img
            self.show_image(frame)
        self.show_image(np.zeros((cam_height, cam_width, 3), dtype=np.uint8))
        time.sleep(1)

    def key_event(self, key: int):
        if self.calibrating:
            if key == int(Qt.Key_X):
                self.calibrating = False
                self.system_info("校准完成")
                api.settings.check_idle = True
                api.step_set_angle(api.STEP1 | api.STEP2 | api.STEP3, 0)
            elif key == int(Qt.Key_W):
                self.cali_target = (self.cali_target + 1) % len(self.cali_list)
                self.system_info(f"正在校准电机-{self.cali_target}")
            elif key == int(Qt.Key_S):
                self.cali_target = (self.cali_target - 1) % len(self.cali_list)
                self.system_info(f"正在校准电机-{self.cali_target}")
            elif key == int(Qt.Key_A):
                api.step_rotate(self.cali_list[self.cali_target], -1)
            elif key == int(Qt.Key_D):
                api.step_rotate(self.cali_list[self.cali_target], 1)
            elif key == int(Qt.Key_Q):
                api.step_rotate(self.cali_list[self.cali_target], -60)
            elif key == int(Qt.Key_E):
                api.step_rotate(self.cali_list[self.cali_target], 60)
            elif key == int(Qt.Key_Z):
                api.step_rotate(self.cali_list[self.cali_target], -200)
            elif key == int(Qt.Key_C):
                api.step_rotate(self.cali_list[self.cali_target], 200)
        else:
            if key == int(Qt.Key_X):
                self.calibrating = True
                self.system_info(f"进入临时校准模式")
                api.settings.check_idle = False
        if key == int(Qt.Key_O):
            self.idle = not self.idle
            logger.debug(f"Idle: {self.idle}")

    def system_info(self, text):
        sig.set_system_status_signal.emit(text)

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
        global cam_img
        last_recognize_time = time.time()
        playing_video = False
        while True:
            time.sleep(0.01)
            if (
                self.idle
                and time.time() - last_recognize_time > self.idle_delay
                and not playing_video
            ):
                playing_video = True
                sig.start_video_signal.emit()
                self.system_info("播放公益视频")
            elif playing_video and not self.idle:
                playing_video = False
                sig.stop_video_signal.emit()
                self.system_info("空闲")
            cam_event.wait()
            cam_event.clear()
            img = cam_img
            if not playing_video:
                self.show_image(img)


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(qdarktheme.load_stylesheet(theme="dark"))
    window = MainWindow()
    window.show()
    app.exec()
