import cv2
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtGui
import numpy as np
from PIL import Image
from PIL import ImageQt

# import tensorflow as tf
# from tensorflow.keras.datasets import mnist
#
# (x_train, y_train), (x_test, y_test) = mnist.load_data()
#
# x_train = x_train / 255.0
# x_test = x_test / 255.0
#
# x_train = x_train.reshape(60000, 28, 28, 1)
# x_test = x_test.reshape(10000, 28, 28, 1)
#
# input_shape = x_train[0]

form_class = uic.loadUiType("C:\\PYQT\\1. PYQT\\main_window.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushOpen.clicked.connect(self.openFunction)
        self.ShowImg.clicked.connect(self.ShowImgFunction)

    def ShowImgFunction(self):
        self.m_num = int(self.plainTextEdit.toPlainText())

        if self.m_num > 9999 | self.m_num < 0:
            return

        x = 28
        y = 28

        img = Image.new("RGB", (x,y))
        data = np.array(img)
        
        count = 0
        for i in range(x):
            for j in range(y):
                data[i][j] = self.dataset[self.m_num][count]
                count+=1

        resultImg = Image.fromarray(data)
        self.photo.setPixmap(ImageQt.toqpixmap(resultImg))



    def openFunction(self):
        fname = QFileDialog.getOpenFileName(self, 'Open File', '',
                                            'Mnist File(*.idx3-ubyte *.IDX3-UBYTE)')

        with open(fname[0], mode='rb') as f:
            data = f.read(16) # 헤더읽기
            
            #sizeData, Dsize = 이미지전체 개수!
            sizeData = (hex(data[4])+hex(data[5])+hex(data[6])+hex(data[7])).split("0x")
            sizeData.pop(0)
        
            Dsize = int("0x"+sizeData[0]+sizeData[1]+sizeData[2]+sizeData[3], 16)


            #dateset에 mnist이미지 삽입.
            self.dataset = []
            count = 0
            data = f.read()
            for size in range(Dsize):
                savedata = []
                for x in range(28):
                    for y in range(28):
                        savedata.append(data[count])
                        count+=1
                self.dataset.append(savedata)

            #self.plainTextEdit.setPlainText(data)
            #self.photo.setPixmap(QtGui.QPixmap(fname[0]))
            print("open!!")

        f.close()



app = QApplication(sys.argv)
mainWindow = WindowClass()
mainWindow.show()
app.exec_()