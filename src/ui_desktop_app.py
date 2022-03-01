# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desktop_appXYCxRl.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialogButtonBox, QGroupBox,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QRadioButton, QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(403, 431)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.radioButtonC = QRadioButton(self.centralwidget)
        self.radioButtonC.setObjectName(u"radioButtonC")
        self.radioButtonC.setGeometry(QRect(80, 50, 99, 20))
        self.radioButtonD = QRadioButton(self.centralwidget)
        self.radioButtonD.setObjectName(u"radioButtonD")
        self.radioButtonD.setGeometry(QRect(190, 50, 99, 20))
        self.txtFile = QLineEdit(self.centralwidget)
        self.txtFile.setObjectName(u"txtFile")
        self.txtFile.setGeometry(QRect(30, 280, 211, 21))
        self.btnStart = QPushButton(self.centralwidget)
        self.btnStart.setObjectName(u"btnStart")
        self.btnStart.setGeometry(QRect(270, 270, 100, 41))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(80, 120, 71, 16))
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(60, 100, 261, 131))
        self.pwdtxt1 = QLineEdit(self.groupBox)
        self.pwdtxt1.setObjectName(u"pwdtxt1")
        self.pwdtxt1.setGeometry(QRect(30, 40, 181, 21))
        self.pwdtxt1.setClearButtonEnabled(False)
        self.pwdtxt2 = QLineEdit(self.groupBox)
        self.pwdtxt2.setObjectName(u"pwdtxt2")
        self.pwdtxt2.setGeometry(QRect(30, 80, 181, 21))
        self.buttonOkC = QDialogButtonBox(self.centralwidget)
        self.buttonOkC.setObjectName(u"buttonOkC")
        self.buttonOkC.setGeometry(QRect(80, 340, 201, 32))
        self.buttonOkC.setStyleSheet(u"")
        self.buttonOkC.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.radioButtonC.setText(QCoreApplication.translate("MainWindow", u"Compress", None))
        self.radioButtonD.setText(QCoreApplication.translate("MainWindow", u"Decompress", None))
        self.btnStart.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.label.setText("")
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Password:", None))
    # retranslateUi

