
# from msilib.schema import RadioButton
from mailbox import mbox
import sys
import os
from tkinter import messagebox

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
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

# UI_FILE_PATH = 'desktop_app.ui'

# try:
#     compile_ui_if_needed(UI_FILE_PATH)
# except ValueError as ex:
#     print(ex, file=sys.stderr)
#     sys.exit(7)

class PzypMainWindow(QMainWindow, ui_desktop_app.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        connectev(self.txtFile, 'mousePressEvent', self.browse_and_select)
        connectev(self.txtFile, 'keyPressEvent', self.check_file_path, call_base_before=True)
        self.txtFile.setEnabled(True)
        self.btnStart.clicked.connect(self.start_compression)
        connectev(self.pwdtxt1, 'keyPressEvent', self.checkpasswords, call_base_before=True)
        connectev(self.pwdtxt2, 'keyPressEvent', self.checkpasswords, call_base_before=True)
        
    
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

        if not self.passwords_match():
            show_error(f"Passwords don't match.")
            return
    
        if self.radioButtonC.isChecked:
            out_file_path =  gen_unique_path_from(f'{in_file_path}.{DEFAULT_EXT}') 
            # encode() #acrecentar
            password = self.pwdtxt1.text().strip()
            if password:
                cd.genwrite_key(password, out_file_path) #confirmar
            show_info(f"Compressed {in_file_path} into {out_file_path}")
        if self.radioButtonD.isChecked:
            mbox.setText("funciona")
            #decode()
    #:

    def checkpasswords(self, *_):
        if self.passwords_match():
            if self.pwdtxt1.text().strip():
                self.btnStart.setEnabled(True)
        else:
            self.btnStart.setEnabled(False)

    def passwords_match(self) -> bool:
        return self.pwdtxt1.text().strip() == self.pwdtxt2.text().strip()

        
    def run_app(argv=sys.argv):
        app = QApplication(argv)
        app.setWindowIcon((QIcon('logo.png')))
        window = PzypMainWindow()
        window.show()
        app.exec()

if __name__ == '__main__':
    PzypMainWindow.run_app()