# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rubbish_mainaAMghv.ui'
##
## Created by: Qt User Interface Compiler version 6.4.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
    QLabel, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QProgressBar, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget)

from gui import PyCircularProgress

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(971, 645)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frameInfo = QFrame(self.centralwidget)
        self.frameInfo.setObjectName(u"frameInfo")
        self.frameInfo.setMinimumSize(QSize(50, 50))
        self.frameInfo.setFrameShape(QFrame.Box)
        self.frameInfo.setFrameShadow(QFrame.Plain)
        self.frameInfo.setLineWidth(2)
        self.verticalLayout_4 = QVBoxLayout(self.frameInfo)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.frameInfo)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamilies([u"\u66f4\u7eb1\u9ed1\u4f53 UI SC"])
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.label)

        self.labelSystem = QLabel(self.frameInfo)
        self.labelSystem.setObjectName(u"labelSystem")
        self.labelSystem.setFont(font)
        self.labelSystem.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.labelSystem)

        self.horizontalLayout_4.setStretch(1, 1)

        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.frameInfo)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.labelResult = QLabel(self.frameInfo)
        self.labelResult.setObjectName(u"labelResult")
        self.labelResult.setFont(font)
        self.labelResult.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.labelResult)

        self.horizontalLayout_3.setStretch(1, 1)

        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.progressProcess = QProgressBar(self.frameInfo)
        self.progressProcess.setObjectName(u"progressProcess")
        self.progressProcess.setStyleSheet(u"QProgressBar::chunk {   background-color:#23A173;}")
        self.progressProcess.setValue(0)

        self.verticalLayout_4.addWidget(self.progressProcess)


        self.horizontalLayout_2.addWidget(self.frameInfo)

        self.frameState = QFrame(self.centralwidget)
        self.frameState.setObjectName(u"frameState")
        self.frameState.setMinimumSize(QSize(50, 50))
        self.frameState.setFrameShape(QFrame.Box)
        self.frameState.setFrameShadow(QFrame.Plain)
        self.frameState.setLineWidth(2)
        self.verticalLayout_10 = QVBoxLayout(self.frameState)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_5 = QLabel(self.frameState)
        self.label_5.setObjectName(u"label_5")
        font1 = QFont()
        font1.setFamilies([u"\u66f4\u7eb1\u9ed1\u4f53 UI SC"])
        font1.setPointSize(13)
        self.label_5.setFont(font1)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label_5)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.progressBin1 = PyCircularProgress(self.frameState)
        self.progressBin1.setObjectName(u"progressBin1")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBin1.sizePolicy().hasHeightForWidth())
        self.progressBin1.setSizePolicy(sizePolicy)
        self.progressBin1.setStyleSheet(u"QProgressBar::chunk {   background-color:#23A173;}")
        self.progressBin1.setValue(0)

        self.verticalLayout_6.addWidget(self.progressBin1)

        self.labelBin1 = QLabel(self.frameState)
        self.labelBin1.setObjectName(u"labelBin1")
        font2 = QFont()
        font2.setFamilies([u"\u66f4\u7eb1\u9ed1\u4f53 UI SC"])
        font2.setPointSize(12)
        self.labelBin1.setFont(font2)
        self.labelBin1.setAlignment(Qt.AlignCenter)

        self.verticalLayout_6.addWidget(self.labelBin1)

        self.verticalLayout_6.setStretch(0, 1)

        self.horizontalLayout_5.addLayout(self.verticalLayout_6)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.progressBin2 = PyCircularProgress(self.frameState)
        self.progressBin2.setObjectName(u"progressBin2")
        sizePolicy.setHeightForWidth(self.progressBin2.sizePolicy().hasHeightForWidth())
        self.progressBin2.setSizePolicy(sizePolicy)
        self.progressBin2.setStyleSheet(u"QProgressBar::chunk {   background-color:#23A173;}")
        self.progressBin2.setValue(0)

        self.verticalLayout_7.addWidget(self.progressBin2)

        self.labelBin2 = QLabel(self.frameState)
        self.labelBin2.setObjectName(u"labelBin2")
        self.labelBin2.setFont(font2)
        self.labelBin2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_7.addWidget(self.labelBin2)

        self.verticalLayout_7.setStretch(0, 1)

        self.horizontalLayout_5.addLayout(self.verticalLayout_7)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.progressBin3 = PyCircularProgress(self.frameState)
        self.progressBin3.setObjectName(u"progressBin3")
        sizePolicy.setHeightForWidth(self.progressBin3.sizePolicy().hasHeightForWidth())
        self.progressBin3.setSizePolicy(sizePolicy)
        self.progressBin3.setStyleSheet(u"QProgressBar::chunk {   background-color:#23A173;}")
        self.progressBin3.setValue(0)

        self.verticalLayout_8.addWidget(self.progressBin3)

        self.labelBin3 = QLabel(self.frameState)
        self.labelBin3.setObjectName(u"labelBin3")
        self.labelBin3.setFont(font2)
        self.labelBin3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_8.addWidget(self.labelBin3)

        self.verticalLayout_8.setStretch(0, 1)

        self.horizontalLayout_5.addLayout(self.verticalLayout_8)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.progressBin4 = PyCircularProgress(self.frameState)
        self.progressBin4.setObjectName(u"progressBin4")
        sizePolicy.setHeightForWidth(self.progressBin4.sizePolicy().hasHeightForWidth())
        self.progressBin4.setSizePolicy(sizePolicy)
        self.progressBin4.setStyleSheet(u"QProgressBar::chunk {   background-color:#23A173;}")
        self.progressBin4.setValue(0)
        self.progressBin4.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_9.addWidget(self.progressBin4)

        self.labelBin4 = QLabel(self.frameState)
        self.labelBin4.setObjectName(u"labelBin4")
        self.labelBin4.setFont(font2)
        self.labelBin4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_9.addWidget(self.labelBin4)

        self.verticalLayout_9.setStretch(0, 1)

        self.horizontalLayout_5.addLayout(self.verticalLayout_9)


        self.verticalLayout_10.addLayout(self.horizontalLayout_5)


        self.horizontalLayout_2.addWidget(self.frameState)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.scrollAreaLog = QScrollArea(self.centralwidget)
        self.scrollAreaLog.setObjectName(u"scrollAreaLog")
        self.scrollAreaLog.setMinimumSize(QSize(10, 0))
        self.scrollAreaLog.setMaximumSize(QSize(340, 16777215))
        self.scrollAreaLog.setFrameShape(QFrame.Box)
        self.scrollAreaLog.setFrameShadow(QFrame.Plain)
        self.scrollAreaLog.setLineWidth(2)
        self.scrollAreaLog.setMidLineWidth(0)
        self.scrollAreaLog.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 311, 460))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font2)
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_3)

        self.listWidgetLog = QListWidget(self.scrollAreaWidgetContents)
        self.listWidgetLog.setObjectName(u"listWidgetLog")
        self.listWidgetLog.setMinimumSize(QSize(50, 50))
        self.listWidgetLog.setFrameShadow(QFrame.Plain)
        self.listWidgetLog.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listWidgetLog.setSpacing(2)
        self.listWidgetLog.setViewMode(QListView.ListMode)
        self.listWidgetLog.setWordWrap(True)
        self.listWidgetLog.setItemAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.listWidgetLog)

        self.scrollAreaLog.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.scrollAreaLog)

        self.frameVideo = QFrame(self.centralwidget)
        self.frameVideo.setObjectName(u"frameVideo")
        self.frameVideo.setMinimumSize(QSize(50, 50))
        self.frameVideo.setFrameShape(QFrame.Box)
        self.frameVideo.setFrameShadow(QFrame.Plain)
        self.frameVideo.setLineWidth(2)
        self.verticalLayout_5 = QVBoxLayout(self.frameVideo)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_4 = QLabel(self.frameVideo)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font2)
        self.label_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.label_4)

        self.labelVideo = QLabel(self.frameVideo)
        self.labelVideo.setObjectName(u"labelVideo")
        self.labelVideo.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.labelVideo)

        self.verticalLayout_5.setStretch(1, 1)

        self.horizontalLayout.addWidget(self.frameVideo)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 3)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u7cfb\u7edf\u72b6\u6001\uff1a", None))
        self.labelSystem.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u8bc6\u522b\u7ed3\u679c\uff1a", None))
        self.labelResult.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.progressProcess.setFormat("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u5783\u573e\u6876\u72b6\u6001", None))
        self.progressBin1.setFormat("")
        self.labelBin1.setText(QCoreApplication.translate("MainWindow", u"\u53ef\u56de\u6536\u5783\u573e", None))
        self.progressBin2.setFormat("")
        self.labelBin2.setText(QCoreApplication.translate("MainWindow", u"\u53a8\u4f59\u5783\u573e", None))
        self.progressBin3.setFormat("")
        self.labelBin3.setText(QCoreApplication.translate("MainWindow", u"\u6709\u5bb3\u5783\u573e", None))
        self.progressBin4.setFormat("")
        self.labelBin4.setText(QCoreApplication.translate("MainWindow", u"\u5176\u4ed6\u5783\u573e", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u8bc6\u522b\u8bb0\u5f55", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"\u8bc6\u522b\u753b\u9762", None))
        self.labelVideo.setText("")
    # retranslateUi

