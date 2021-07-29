import cv2
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtGui
import numpy as np
from PIL import Image
from PIL import ImageQt

form_class = uic.loadUiType("C:\\PYQT\\1. PYQT\\main_window.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushOpen.clicked.connect(self.openFunction)
        self.ShowImg.clicked.connect(self.ShowImgFunction)
        self.RotationImg.clicked.connect(self.RotationImgFunction)
        

    def MakeImg(self, num):
        # x, y값 설정
        x = int(self.npData[num].shape[0])
        y = int(self.npData[num].shape[1])

        img = Image.new("RGB", (x,y))
        data = np.array(img)
        
        # 하나의 이미지 행렬을 만들어준다.
        count = 0
        for i in range(x):
            for j in range(y):
                data[i][j] = self.dataset[num][i][j]
        return data





    def RotationImgFunction(self):
        # 각도 받아오기.
        degree = int(self.plainTextEdit_2.toPlainText())
        if degree % 360 == 0:
            return
        
        width = int(self.npData[self.m_num].shape[0]) 
        height = int(self.npData[self.m_num].shape[1])

        # 회전 매트릭스 생성.
        matrix = cv2.getRotationMatrix2D((width/2, height/2), degree, 1)
        src = cv2.warpAffine(self.MakeImg(self.m_num), matrix, (width, height))
        
        # 결과 출력하기.
        resultImg = Image.fromarray(src)
        self.photo.setPixmap(ImageQt.toqpixmap(resultImg))


    def ShowImgFunction(self):
        self.m_num = int(self.plainTextEdit.toPlainText())
        self.plainTextEdit_2.setPlainText("0")

        if self.m_num >= int(self.npData.shape[0]) or self.m_num < 0:
            return

        # 결과 출력하기
        resultImg = Image.fromarray(self.MakeImg(self.m_num))
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

            #dataX, dataY = x와 y의 크기
            self.dataX = data[11]
            self.dataY = data[15]

            #dateset에 mnist이미지 삽입.
            self.dataset = []
            count = 0
            data = f.read()
            for size in range(Dsize):
                savedataX = []
                for x in range(self.dataX):
                    savedataY = []
                    for y in range(self.dataY):
                        savedataY.append(data[count])
                        count+=1
                    savedataX.append(savedataY)
                self.dataset.append(savedataX)

            self.npData = np.array(self.dataset)
            f.close()



app = QApplication(sys.argv)
mainWindow = WindowClass()
mainWindow.show()
app.exec_()