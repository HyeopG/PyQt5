import cv2
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import numpy as np
from PIL import Image
from PIL import ImageQt

form_class = uic.loadUiType("C:\\PYQT\\1. PYQT\\main_window.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.dataset = []

        self.pushOpen.clicked.connect(self.openFunction)
        self.ShowImg.clicked.connect(self.ShowImgFunction)
        self.RotationImg.clicked.connect(self.RotationImgFunction)
        self.horizontalScrollBar.actionTriggered.connect(self.scrollBarFunction)
        self.Zoom.clicked.connect(self.ZoomFunction)
        self.allSave.clicked.connect(self.allSaveFunction)

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
                data[i][j] = self.npData[num][i][j]
        return data


    def allSaveFunction(self):
        if self.dataset:
            degree = int(self.plainTextEdit_2.toPlainText())
            zoomNum = float(self.plainTextEdit_3.toPlainText())

            if degree % 360 == 0 and zoomNum <= 0:
                return
            
            self.dataset = []  # 데이터셋 초기화.
            for i in range(self.npData.shape-1):
                if zoomNum > 0:
                    dst = cv2.resize(self.MakeImg(i), None, fx = zoomNum, fy = zoomNum, interpolation=cv2.INTER_CUBIC)
                else:
                    dst = self.MakeImg(i)

                width = dst.shape[0]
                height = dst.shape[1]

                if degree % 360 != 0:
                    matrix = cv2.getRotationMatrix2D((width/2, height/2), degree, 1)
                    src = cv2.warpAffine(dst, matrix, (width, height))
                    self.dataset[i] = src
                else:
                    self.dataset[i] = dst

    def ZoomFunction(self):
        if self.dataset:
            zoomNum = float(self.plainTextEdit_3.toPlainText())

            if zoomNum <= 0:
                return

            width = int(self.npData[self.m_num].shape[0]) 
            height = int(self.npData[self.m_num].shape[1])

            dst = cv2.resize(self.MakeImg(self.m_num), None, fx = zoomNum, fy = zoomNum, interpolation=cv2.INTER_CUBIC)

            for x in range(width):
                for y in range(height):
                    self.npData[self.m_num][x][y] = dst[x][y][0]

            resultImg = Image.fromarray(dst)
            self.photo.setPixmap(ImageQt.toqpixmap(resultImg))


    def scrollBarFunction(self):
        sValue = self.horizontalScrollBar.value()
        self.plainTextEdit.setPlainText(str(sValue))

        if self.dataset:
            self.plainTextEdit_2.setPlainText("0")
            self.plainTextEdit_3.setPlainText("0")

            if sValue >= int(self.npData.shape[0]) or sValue < 0:
                return

            # 결과 출력하기
            resultImg = Image.fromarray(self.MakeImg(sValue))
            self.photo.setPixmap(ImageQt.toqpixmap(resultImg))


    def RotationImgFunction(self):
        if self.dataset:
            # 각도 받아오기.
            degree = int(self.plainTextEdit_2.toPlainText())
            if degree % 360 == 0:
                return
            
            width = int(self.npData[self.m_num].shape[0]) 
            height = int(self.npData[self.m_num].shape[1])

            # 회전 매트릭스 생성.
            matrix = cv2.getRotationMatrix2D((width/2, height/2), degree, 1)
            src = cv2.warpAffine(self.MakeImg(self.m_num), matrix, (width, height))
        
            for x in range(width):
                for y in range(height):
                    self.npData[self.m_num][x][y] = src[x][y][0]

            # 결과 출력하기.
            resultImg = Image.fromarray(src)
            self.photo.setPixmap(ImageQt.toqpixmap(resultImg))


    def ShowImgFunction(self):
        if self.dataset:
            self.m_num = int(self.plainTextEdit.toPlainText())
            self.plainTextEdit_2.setPlainText("0")
            self.plainTextEdit_3.setPlainText("0")
            self.horizontalScrollBar.setValue(self.m_num)

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

            self.horizontalScrollBar.setRange(0, self.npData.shape[0]-1)
            f.close()



app = QApplication(sys.argv)
mainWindow = WindowClass()
mainWindow.show()
app.exec_()