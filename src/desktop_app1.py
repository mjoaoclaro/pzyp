
from mailbox import mbox
import sys
import os
from tarfile import CompressionError
from tkinter import messagebox

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDialogButtonBox
from PySide6.QtGui import QIcon
import ui_desktop_app
import compress_decompress as cd
from utils import (
    compile_ui_if_needed, 
    connectev, 
    get_standard_location,
    msg_box,
    show_error, 
    show_info,
    gen_unique_path_from,
)

# Subclass QMainWindow to customize your application's main window

__all__ = [
    'PzypMainWindow',
]

DEFAULT_EXT = 'lzs'


class PzypMainWindow(QMainWindow, ui_desktop_app.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        connectev(self.txtFile, 'mousePressEvent', self.browse_and_select)
        connectev(self.txtFile, 'keyPressEvent', self.check_file_path, call_base_before=True)
        self.txtFile.setEnabled(True)
        self.btnOk.clicked.connect(self.checkpasswords)
        self.btnStart.clicked.connect(self.start_compression)

        
    def browse_and_select(self, *_):
        
        """
        https://doc.qt.io/qt-6/qfiledialog.html#details
        """
    
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptDrops(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setDirectory(get_standard_location('home'))
        file_path, *_ = file_dialog.getOpenFileName()
        if file_path.strip():
            self.txtFile.setText(file_path)
            self.btnStart.setEnabled(True)

    def check_file_path(self, *_):
        txtfile, btnstart = self.txtFile, self.btnStart
        file_path = txtfile.text().strip()

        if btnstart.isEnabled() and not file_path:
            self.btnStart.setEnabled(False)
        elif not btnstart.isEnabled() and file_path:
            self.btnStart.setEnabled(True)
        

    def start_compression(self):
        
        in_file_path = self.txtFile.text().strip()
        assert in_file_path, "File path is empty"

        if not os.path.exists(in_file_path):
            show_error(f"File '{in_file_path}' not found")
            return

        if not os.path.isfile(in_file_path):
            show_error(f"This program doesn't work on directories!")
            return
        

        if not self.radioButtonC.isChecked() and not self.radioButtonD.isChecked():
            show_info(f"Please choose compress or decompress")

        if self.radioButtonC.isChecked():
            compressionLevel = self.comboBox.currentText()
            # cd.encode()
            #codifo para mandar para o decode e o encode 
            #show_info(f"Compressed {in_file_path} into {out_file_path}")
            password = self.pwdtxt1.text().strip()
            if password:
                cd.genwrite_key(in_file_path, password)
            pass
        if self.radioButtonD.isChecked():
            #cd.decode()
            #show_info(f"Decompressed {in_file_path} into {out_file_path}")
            pass


    def checkpasswords(self, *_):

            if self.passwords_match():
                show_info(f"Password defined")
                if self.pwdtxt1.text().strip():
                    self.btnStart.setEnabled(True)
            else:
                self.btnStart.setEnabled(False)
                show_error(f"Passwords don't match.")
                #por aqui

    def passwords_match(self) -> bool:
        return self.pwdtxt1.text().strip() == self.pwdtxt2.text().strip()

    @staticmethod
    def run_app(argv=sys.argv):
        app = QApplication(argv)
        app.setWindowIcon(QIcon('icon.png')) #nao funciona, tentar perceber pq
        QIcon.Active
        window = PzypMainWindow()
        window.show()
        app.exec()

if __name__ == '__main__':
    PzypMainWindow.run_app()