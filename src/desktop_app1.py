
import pathlib
import sys
import os


from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QDialogButtonBox
from PySide6.QtGui import QIcon
import ui_desktop_app
import pzyp as pz
import lzss_io as lz
from utils import (
    compile_ui_if_needed, 
    connectev, 
    get_standard_location,
    msg_box,
    gen_unique_path_from,
    show_error, 
    show_info,
)

# Subclass QMainWindow to customize your application's main window

__all__ = [
    'PzypMainWindow',
]

LEVEL = {1: (10, 4), 2: (12, 4), 3: (14, 5), 4: (15, 5)}
DEFAULT_EXT = 'lzs'
FILE_NAME = ''


class PzypMainWindow(QMainWindow, ui_desktop_app.Ui_MainWindow):


    def __init__(self):
        super().__init__()
        self.setupUi(self)
        connectev(self.txtFile, 'mousePressEvent', self.browse_and_select)
        connectev(self.txtFile, 'keyPressEvent', self.check_file_path, call_base_before=True)
        self.txtFile.setEnabled(True)
        self.btnOk.clicked.connect(self.checkpasswords)
        self.btnStart.clicked.connect(self.start_compression)
        self.btnStart.setEnabled(False)
        self.comboBox.setEnabled(False)

    def browse_and_select(self, *_):
        
        """
        https://doc.qt.io/qt-6/qfiledialog.html#details
        """

        file_dialog = QFileDialog(self)
        file_dialog.setAcceptDrops(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setDirectory(get_standard_location('home'))
        file_path, *_ = file_dialog.getOpenFileName()
        if self.radioButtonC.isChecked():
                self.comboBox.setEnabled(True)
                if file_path.strip():
                    self.txtFile.setText(file_path)
                    self.btnStart.setEnabled(True)
        elif self.radioButtonD.isChecked():
                self.comboBox.setEnabled(False)
                if file_path.strip():
                    self.txtFile.setText(file_path)
                    self.btnStart.setEnabled(True)
        else:
            show_error(f"Please choose compress or decompress")                   

        

    def check_file_path(self, *_):
        txtfile, btnstart = self.txtFile, self.btnStart
        file_path = txtfile.text().strip()
        

        if btnstart.isEnabled() and not file_path:
            self.btnStart.setEnabled(False)
        elif not btnstart.isEnabled() and file_path:
            self.btnStart.setEnabled(True)
            

    def start_compression(self):

        in_file_path = self.txtFile.text().strip()
        out_file_path =  gen_unique_path_from(in_file_path)
        fils=pz.filePathFromUI(in_file_path, out_file_path)

        assert in_file_path, "File path is empty"

        if not os.path.exists(in_file_path):
            show_error(f"File '{in_file_path}' not found")
            return

        if not os.path.isfile(in_file_path):
            show_error(f"This program doesn't work on directories!")
            return

        if self.radioButtonC.isChecked():
            
            compressionLevel = int(self.comboBox.currentText()) if self.comboBox.currentIndex()!=0 else 2
            
            off_len = LEVEL[compressionLevel]
            off=off_len[0]
            leng=off_len[1]
            ctx=lz.PZYPContext(encoded_offset_size=off, encoded_len_size=leng)

            out_file_path =  gen_unique_path_from(in_file_path)
            fils=pz.filePathFromUI(in_file_path, out_file_path)

            pz.encode(fils[0], fils[1], None ,ctx)
            show_info(
                f"Compressed {in_file_path} into {fils[1]}")
            password = self.pwdtxt1.text().strip()
            if password:
                pz.genwrite_key(in_file_path, password)
            pass
        if self.radioButtonD.isChecked():
            assert DEFAULT_EXT in in_file_path, show_error("File is not compressed! Try again.")
            with open(in_file_path, 'rb') as f:
                head=f.readline().split()
                fileName = head[3].decode('utf8')
                off_len =[int(head[0]), int(head[1])]
                with open(fileName, 'w+') as out:
                    pz.decode(f, out, off_len)
            show_info(f"Decompressed {out_file_path} into {in_file_path}")
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