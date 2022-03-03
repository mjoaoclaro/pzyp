# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'desktop_appmhsqLb.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QLabel,
    QLineEdit, QMainWindow, QPushButton, QRadioButton,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(390, 436)
        icon = QIcon()
        icon.addFile(u"logo.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"")
        MainWindow.setAnimated(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.radioButtonC = QRadioButton(self.centralwidget)
        self.radioButtonC.setObjectName(u"radioButtonC")
        self.radioButtonC.setGeometry(QRect(80, 210, 99, 20))
        self.radioButtonD = QRadioButton(self.centralwidget)
        self.radioButtonD.setObjectName(u"radioButtonD")
        self.radioButtonD.setGeometry(QRect(190, 210, 99, 20))
        self.txtFile = QLineEdit(self.centralwidget)
        self.txtFile.setObjectName(u"txtFile")
        self.txtFile.setGeometry(QRect(40, 270, 291, 21))
        self.btnStart = QPushButton(self.centralwidget)
        self.btnStart.setObjectName(u"btnStart")
        self.btnStart.setGeometry(QRect(240, 330, 100, 41))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(80, 120, 71, 16))
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(60, 40, 261, 141))
        self.pwdtxt1 = QLineEdit(self.groupBox)
        self.pwdtxt1.setObjectName(u"pwdtxt1")
        self.pwdtxt1.setGeometry(QRect(30, 40, 181, 21))
        self.pwdtxt1.setEchoMode(QLineEdit.Password)
        self.pwdtxt1.setClearButtonEnabled(False)
        self.pwdtxt2 = QLineEdit(self.groupBox)
        self.pwdtxt2.setObjectName(u"pwdtxt2")
        self.pwdtxt2.setGeometry(QRect(30, 80, 181, 21))
        self.pwdtxt2.setEchoMode(QLineEdit.Password)
        self.btnOk = QPushButton(self.groupBox)
        self.btnOk.setObjectName(u"btnOk")
        self.btnOk.setGeometry(QRect(220, 100, 31, 32))
        self.comboBox = QComboBox(self.centralwidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(30, 330, 161, 32))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(30, 370, 131, 16))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"LZSS", None))
        self.radioButtonC.setText(QCoreApplication.translate("MainWindow", u"Compress", None))
        self.radioButtonD.setText(QCoreApplication.translate("MainWindow", u"Decompress", None))
        self.btnStart.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.label.setText("")
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Password:", None))
        self.btnOk.setText(QCoreApplication.translate("MainWindow", u"Ok", None))
        self.comboBox.setItemText(0, "")
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"1", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"2", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"3", None))
        self.comboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"4", None))

        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Compress Level", None))
    # retranslateUi