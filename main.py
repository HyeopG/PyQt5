import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic


form_class = uic.loadUiType("C:\\PYQT\\1. PYQT\\main_window.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushOpen.clicked.connect(self.openFunction)

    def openFunction(self):
        fname = QFileDialog.getOpenFileName(self)
        with open(fname[0]) as f:
            data = f.read()

        print("open!!")

app = QApplication(sys.argv)
mainWindow = WindowClass()
mainWindow.show()
app.exec_()